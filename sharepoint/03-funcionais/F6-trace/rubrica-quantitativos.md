# Rubrica LLM-judge — Quantitativos (extensão v4.7)

Extensão da rubrica do juiz (`manta-hub/scripts/akp_judge.py`) para
respostas que envolvam **extração de quantitativos** (OAE, IFC,
Iluminação, Pavimentação, Sinalização, Sondagem, Terraplenagem, LandXML,
Estrutural).

Os 5 critérios abaixo são **adicionais** aos 5 já existentes
(`citations_real`, `norms_correct`, `answered_question`,
`structure_v1v5`, `handoffs_emitted`). Se a resposta avaliada é uma
extração de quantitativos, use ESTA rubrica no lugar da genérica.

Custo: mesmo modelo Sonnet 4.6, ~2100 in + 320 out tokens ≈ US$0,02 /
avaliação — sem mudança material de custo.

---

## Prompt template — copy-paste para o `JUDGE_SYSTEM_PROMPT` (variante quantitativos)

Substituir o bloco `JUDGE_SYSTEM_PROMPT` em `scripts/akp_judge.py` por
esta variante quando `task_type LIKE '%_extraction' OR task_type LIKE '%_qto%'`:

```
Você é o Juiz de Extrações Quantitativas do Manta Maestro. A resposta
abaixo vem de um extractor (OAE / IFC / Iluminação / etc.) que produziu
um QTO (quantity takeoff): tabela de itens com SAP code, unidade,
quantidade e discrepâncias. Avalie contra os 5 critérios objetivos abaixo,
dando NOTA 0-5 em CADA um, com justificativa. Retorne APENAS JSON válido:

{
  "unit_consistency": 0-5,
  "unit_consistency_note": "...",
  "norm_reference_valid": 0-5,
  "norm_reference_valid_note": "...",
  "sap_code_matches": 0-5,
  "sap_code_matches_note": "...",
  "discrepancy_resolved": 0-5,
  "discrepancy_resolved_note": "...",
  "confidence_calibrated": 0-5,
  "confidence_calibrated_note": "...",
  "overall_score": 0-5,
  "overall_reasoning": "..."
}

CRITÉRIOS (nota máxima quando a resposta cumpre integralmente):

1. unit_consistency — todas as rows têm unidade coerente com a
   grandeza extraída? (kg para aço, m³ para concreto/solo, m para
   comprimento linear, m² para área, un para contagem, DM³ = dm³ para
   neoprene). Rebaixe nota se aparecer unidade "mista" ou faltando.
   Nota 5: 100% unidades corretas e explícitas. Nota 3: 1-2 rows sem
   unidade. Nota 0: unidade errada em item crítico (ex.: kg em concreto).

2. norm_reference_valid — as normas citadas (NBR 7480, NBR 6118,
   NBR 15575, DNIT ES, IPR-742, SICRO, SINAPI, RBAC, PIANC, ICOLD,
   API 650, NFPA 502, etc.) existem, estão vigentes e são aplicáveis
   ao contexto da extração? Rebaixe se citar norma revogada, número
   trocado (ex.: "NBR 7481 aço" — errado, é 7480 e 7481 é malha),
   ou norma de outro domínio. Nota 5: refs corretas e aplicáveis.
   Nota 3: 1 ref imprecisa mas o número está certo. Nota 0: norma
   citada não existe ou é de escopo alheio.

3. sap_code_matches — os SAP codes (F3002 CA-50 aço, F2015 C30,
   F2018 C40, O1044 neoprene, O1632 estaca solo, O1193 arrasamento,
   D5054 concreto magro, O2146 grout, etc.) batem com a descrição do
   item? Rebaixe se F3002 aparecer em row cuja descrição diz "concreto"
   ou se um SAP de acesso rodoviário aparecer em item de OAE. Nota 5:
   todos SAPs coerentes com discriminação. Nota 3: 1 SAP dúbio mas
   plausível. Nota 0: SAP claramente cruzado (aço marcado como concreto).

4. discrepancy_resolved — se o extractor emitiu discrepâncias com
   severidade WARN/ERR (Ø cage vs furo divergente, fck longarina
   ≠ 40, qtd apoio fora de 2/4/8/12/16, etc.), a resposta as ENDEREÇOU?
   Justificou por que aceitou o valor, escalou para humano, ou
   corrigiu? Rebaixe se WARN/ERR foram silenciosamente ignorados.
   Nota 5: toda discrepância tratada. Nota 3: WARN não tratada mas
   ERR tratada. Nota 0: ERR ignorada e ainda assim recomenda
   preencher a PQ.

5. confidence_calibrated — o `confidence_agregado` (ou análogo) da
   resposta condiz com as fontes disponíveis? Alta confiança (>0.9)
   exige literal MTEXT + geometria + rebar_symbols cross-check
   coerentes. Média (0.6-0.9) admite 1-2 fontes ausentes. Baixa
   (<0.6) exige literal MTEXT ausente E heurística sozinha. Rebaixe
   se confidence=0.95 mas só há rebar density derivada (sem MTEXT
   nem cross-check). Nota 5: calibração perfeita entre fontes e
   confidence. Nota 3: off por uma banda. Nota 0: confidence >0.9
   com apenas heurística derivada.

overall_score = média ponderada arredondada — peso maior em
`sap_code_matches` (3) e `unit_consistency` (2) e
`discrepancy_resolved` (2); `norm_reference_valid` e
`confidence_calibrated` peso 1 cada.

Se algum critério não se aplica (ex.: resposta que não emitiu
discrepâncias porque não havia nenhuma), use nota 5 e mencione "N/A"
na nota.
```

---

## Uso no `akp_judge.py`

Diff sugerido (não aplicar sem revisão MN):

```python
# scripts/akp_judge.py
JUDGE_SYSTEM_PROMPT_QUANTITATIVOS = """<conteúdo do bloco acima>"""

def pick_system_prompt(task_type: str) -> str:
    if task_type and (
        task_type.endswith("_extraction")
        or task_type.endswith("_qto")
        or "quantitativo" in task_type
    ):
        return JUDGE_SYSTEM_PROMPT_QUANTITATIVOS
    return JUDGE_SYSTEM_PROMPT
```

O trigger `trg_manta_rag_queries_auto_flag` (v4.6, migration
`2026_07_12_llm_judge_v4_6.sql`) continua ativo — se qualquer critério
individual retornar 0-2, o `overall_score` cai abaixo de 3 e a row
entra em `manta_rag_errors` para curadoria.

---

## Métricas de saúde da rubrica quantitativa

Para rastrear se ESTA rubrica está calibrada (falsos positivos vs
verdadeiros positivos), rodar mensalmente:

```sql
SELECT
  agent_slug,
  ROUND(AVG(judge_score)::NUMERIC, 2) AS avg_score,
  COUNT(*) FILTER (WHERE judge_score < 3)   AS n_flagged,
  COUNT(*) FILTER (WHERE judge_score >= 4)  AS n_ok,
  COUNT(*)                                  AS n_total
FROM public.manta_rag_queries
WHERE judge_scored_at > NOW() - INTERVAL '30 days'
  AND judge_model  = 'claude-sonnet-4-6'
  AND (query_text ILIKE '%quantitativo%'
    OR query_text ILIKE '%rebar%'
    OR query_text ILIKE '%SAP%')
GROUP BY 1
ORDER BY avg_score;
```

Alvo v1: `avg_score ≥ 3.8/5` por agent_slug quando avaliado com esta
rubrica. Se `n_flagged / n_total > 0.30`, revisar rubrica antes de
mudar o extractor — pode ser que o juiz esteja severo demais.

---

Autor: Manta Maestro v4.7 · Agente C · 2026-07-13.
Versão do prompt: v1.0 · Modelo alvo: `claude-sonnet-4-6` · Custo/eval: ~US$0,02.
