# TRAINING-QUANTITATIVOS — Framework de treino contínuo dos extractors de quantitativos

Este framework define **como os extractors de quantitativos (OAE, IFC,
Iluminação, Pavimentação, Sinalização, Sondagem, Terraplenagem, LandXML,
Estrutural) aprendem com o próprio uso**, migrando de uma arquitetura
"regex + heurística congelada" para uma arquitetura **auto-melhorável
via memória episódica + feedback humano + medições de campo**.

Depende de:

- Supabase project `manta-maestro` (`ogxxgvgtulrbbppshjie`) — v4.7 já em
  prod com `agent_episodes`, `maestro_cost_log`, `get_relevant_episodes`,
  `consolidate_old_episodes`, `v_episodes_health`, `v_cost_by_agent`.
- `manta_shared.training_hooks` — `EpisodeRecorder` + `LessonInjector`
  (importável por todos os backends).
- Nova migração `2026_07_13_quantitativo_overrides_and_field.sql` —
  captura overrides de UI e medições de campo.
- Rubrica extendida do LLM-judge — 5 critérios de quantitativos em
  `sharepoint/03-funcionais/F6-trace/rubrica-quantitativos.md`.

---

## 1. As 6 camadas de treino

Cada extração passa (em regime esperado) por até 6 sinais de melhoria.
Nem toda extração passa pelos 6 — 1, 2 e 4 são **sempre** obrigatórios;
3, 5 e 6 aparecem quando há material para eles.

| # | Camada | Frequência | Sinal | Propaga como |
|---|--------|-----------|-------|--------------|
| 1 | **Golden tests** (E2E OAE 622, Balanço, LandXML EPR, IFC/Sondagem fixtures) | A cada commit | pass/fail determinístico | Bloqueio de CI |
| 2 | **agent_episodes** (self_critique + lessons_learned) | Toda extração | quality_score + iterações | `LessonInjector` no próximo prompt |
| 3 | **Human-in-the-loop** (Mapping Page + `quantitativo_overrides`) | Sempre que o operador corrige a UI | delta_pct entre extractor e humano | Training data supervisionado + issue no backlog |
| 4 | **LLM-judge quantitativos** (5 novos critérios) | 10% amostragem estratificada | judge_score 0-25 | Auto-flag < 15/25 → `manta_rag_errors` + backlog |
| 5 | **Cross-source** (LandXML SurfVolume × Civil3DResult; OAE rebar_symbols × RebarRow parsed) | Quando há 2 fontes redundantes | divergence % | Discrepância + confidence recalibrada |
| 6 | **Field measurement** (`field_measurements` pós-obra) | Uma vez por (project, sap_code) | delta predito vs medido | View `v_predicted_vs_actual` + banda de acurácia |

---

## 2. Fluxo canônico em um backend (exemplo OAE)

```
1. USER upload → POST /api/upload-batch
2. USER extract → POST /api/extract
   → dentro do handler:
     with EpisodeRecorder(agent_id='oae-extractor',
                          task_type='rebar_extraction',
                          project_id=session_id) as ep:
         lessons = LessonInjector.get_relevant(
             'oae-extractor', 'rebar_extraction', limit=5)
         result = run_pipeline(..., extra_prompt=lessons.format_for_prompt())
         ep.set_quality_score(result.confidence_agregado)
         ep.set_guards(aluci_pass=..., consist_pass=result.discrepancies_are_all_info)
         ep.set_self_critique(auto_gerar_critique(result))
         ep.set_lessons(extract_lessons_from_run(result))
3. USER edita QUANT na Mapping Page → POST /api/aggregates/{sid}/override
   → grava em `public.quantitativo_overrides`
4. Cron 03:00 UTC → akp_judge.py roda em 10% das extrações do dia
5. Obra em execução → field team roda `SELECT backfill_field_measurement(...)`
```

---

## 3. MOP semanal — MN — 2h todo domingo

**Objetivo:** detectar deterioração cedo, curar `agent_episodes` de baixa
qualidade, promover lessons_learned recorrentes a regra no extractor.

```sql
-- (a) Quais agents estão degradando?
SELECT * FROM v_episodes_health
 WHERE avg_quality_score < 7
 ORDER BY total_episodes DESC;

-- (b) Últimos 20 self_critique do agent problemático
SELECT id, task_type, quality_score, self_critique, lessons_learned, created_at
  FROM agent_episodes
 WHERE agent_id = '<oae-extractor|ifc-extractor|...>'
   AND created_at > NOW() - INTERVAL '7 days'
 ORDER BY created_at DESC LIMIT 20;

-- (c) Overrides humanos frequentes (indicam bugs recorrentes)
SELECT source_backend, sap_code,
       COUNT(*) AS n_overrides,
       AVG(delta_pct) AS avg_delta_pct
  FROM quantitativo_overrides
 WHERE created_at > NOW() - INTERVAL '7 days'
 GROUP BY 1, 2
HAVING COUNT(*) >= 3
 ORDER BY n_overrides DESC;

-- (d) Judge health quantitativo
SELECT agent_slug, AVG(judge_score) AS avg_judge, COUNT(*)
  FROM manta_rag_queries
 WHERE judge_scored_at > NOW() - INTERVAL '7 days'
   AND judge_score IS NOT NULL
 GROUP BY 1 HAVING AVG(judge_score) < 3 ORDER BY 2;
```

**Ação:** para cada agent com `avg_quality_score < 7`, abrir issue em
`akp_curation_backlog` e aplicar o playbook §6 abaixo.

---

## 4. MOP mensal — 1º domingo de cada mês

```sql
-- Roda decay policy (30-90d → destilled_*; >90d → apaga)
SELECT consolidate_old_episodes();

-- Revisa lessons_learned recorrentes que viraram destilados
SELECT agent_id, task_type,
       array_agg(DISTINCT unnest_lesson) FILTER (WHERE unnest_lesson IS NOT NULL) AS top_lessons
  FROM agent_episodes, unnest(lessons_learned) AS unnest_lesson
 WHERE task_type LIKE 'destilled_%'
   AND created_at > NOW() - INTERVAL '30 days'
 GROUP BY 1, 2;
```

**Ação:** cada `destilled_*.top_lessons` que aparece em ≥3 destilações
consecutivas vira **regra hard-coded** no extractor (Playbook §6 passo 4)
ou vira KE oficial em `academic_knowledge_elements` se for norma.

---

## 5. MOP per-project — pós-obra

Para cada obra concluída, o gestor do projeto executa o backfill de
medições de campo (comparação predito × real):

```sql
-- Uma linha por (project_id, sap_code) que foi medido em obra
SELECT public.backfill_field_measurement(
  p_project_id  := 'OAE-622',
  p_sap_code    := 'F3002',
  p_qty_measured:= 3980.5,       -- kg medido em obra
  p_measured_by := 'joao@mantaassociados.com',
  p_unit        := 'kg',
  p_notes       := 'Pesagem CA-50 chapa de obra 12/07'
);
```

A função INSERE em `field_measurements` E anexa a `lessons_learned` do
episódio original `predicted_vs_actual = ±X.Y%`, alimentando o LessonInjector
das próximas extrações do mesmo `agent_id`.

**KPI de sucesso pós-obra:** view `v_predicted_vs_actual` mostra:
- `acurado` (<5% delta) — meta ≥ 70% dos itens
- `moderado` (5-10%) — meta ≤ 25%
- `divergente` (>10%) — meta ≤ 5%; toda linha divergente vira issue.

---

## 6. Playbook — corrigir um extractor que erra cronicamente (5 passos)

Aplicar quando `avg_quality_score < 7 por 3 semanas consecutivas` OU
quando um `sap_code` acumula ≥5 overrides humanos em 7 dias.

1. **Isolar o modo de falha.** Query em `agent_episodes` filtrando o
   agent + task_type; ler os 20 mais recentes `self_critique`. Se ≥40%
   das críticas mencionam o mesmo termo (ex.: "MTEXT vertical não lido",
   "Ø 32 confundido com 3.2"), o modo de falha está isolado.

2. **Correlacionar com overrides.** Cruze com `quantitativo_overrides`
   por `sap_code` — se o mesmo SAP tem alto `avg_delta_pct` sistemático,
   o extractor está enviesado (não é ruído).

3. **Reproduzir localmente** com o fixture do projeto que gerou os
   episódios de baixa qualidade. Rodar o extractor sob debugger. Se
   o teste E2E do golden ainda passa mas o real falha → o golden não
   cobre esse modo → **adicionar novo golden fixture** ANTES de tocar
   o código.

4. **Corrigir o extractor** (regex, heurística, cascata de fallback).
   Se for algo que o LessonInjector consegue mitigar (ex.: "para OAE
   PRL/RioSP com sufixo B, Ø 32 aparece como '3.2 mm' em MTEXT vertical
   — trate como 32 mm"), promover a lição para uma **regra fixa** no
   código E remover do backlog de lessons dinâmicas (evita drift).

5. **Fechar o loop:** rodar o novo golden, mergear, e monitorar
   `v_episodes_health` do agente pelas 2 semanas seguintes. Se
   `avg_quality_score` subir ≥ 1.5 pontos, marcar issue como resolvida
   em `akp_curation_backlog`. Se não subir, reabrir o passo 1 com
   modo de falha ampliado.

---

## 7. Métricas de sucesso trackáveis

Painel `/admin/training-quantitativos` (a construir) mostra:

| Métrica | Fonte | Alvo v1 |
|---------|-------|---------|
| `avg_quality_score` por agent_id (30d) | `v_episodes_health` | ≥ 8.0 |
| Taxa de `escalated_to_human` (30d) | `v_episodes_health.pct_escalated` | < 5% |
| Overrides humanos por semana (por backend) | `quantitativo_overrides` | trend ↓ mensal |
| Judge quantitativo médio (10% amostra) | `manta_rag_queries.judge_score` | ≥ 20/25 |
| Delta predito vs actual em obra | `v_predicted_vs_actual` | 70% acurado (<5%) |
| Ciclo lição→regra (dias) | timestamps `agent_episodes` → commit | < 14d |
| Custo médio por extração (USD) | `v_cost_by_agent` | < US$0.15 / rodada |

Toda métrica é queryable via SQL — o painel só chama `select_json_agg`.
As metas são gates para promoção de tier: um agent só é promovido de
star para star2 quando bate 3/5 dessas metas por 4 semanas.

---

## 8. Como um novo backend adota o framework

Passo mínimo (~2h de trabalho) para adicionar um backend novo ao loop:

1. Import de `EpisodeRecorder` + `LessonInjector` no endpoint principal
   (`main.py` do backend).
2. Escolher um `agent_id` estável (ex.: `sondagem-extractor`) e um
   `task_type` por tipo de operação (`spt_table_parse`,
   `coordenadas_utm_parse`, `na_extract`).
3. Adicionar `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` ao `.env` (se
   ausentes, os hooks fazem no-op — não quebra o backend).
4. Se o backend expõe UI de correção manual, POST em
   `/api/training/override` (a implementar como router shared) para
   gravar em `quantitativo_overrides`.
5. Adicionar um golden test em `tests/<backend>/test_golden.py` que
   trave o comportamento mínimo aceitável.

Isso é o piso. A camada 4 (judge) já é transversal — quando o backend
grava em `agent_episodes`, entra automaticamente na amostragem.

---

## 9. Não-objetivos (v1)

- **Não** fazemos fine-tune de modelo em v1. As lessons_learned vão
  no prompt via `LessonInjector`; se em 6 meses a base tiver ≥ 5k
  episódios de alta qualidade, aí sim considera-se fine-tune.
- **Não** substituímos os testes E2E. Camada 1 continua sendo gate
  duro de CI — as camadas 2-6 são complemento, não substituto.
- **Não** compartilhamos episódios entre tenants. `agent_id` embute a
  identidade do agent global (não do cliente); `project_id` isola por
  obra e é o único cruzamento entre camadas 3 e 6.

---

Autor: Manta Maestro v4.7 · Agente C · 2026-07-13.
