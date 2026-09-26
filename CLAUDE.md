# CLAUDE.md — Manta Maestro (núcleo)

Registro mestre dos agentes IA da Manta Associados, referenciado pelos
SKILL.md e pelos runbooks operacionais no SharePoint.

Versão: **v5.5.0** (2026-09-26) — **planejador + núcleo enxuto**. Este
arquivo entra em toda sessão e em todo subagente, então guarda só o
essencial: regras de economia, planejador, hierarquia, catálogo
compacto e RAG. O detalhe completo (antes 1.143 linhas) foi movido sem
alteração para `docs/maestro/` e é lido **só quando a tarefa exige**.
Linha de base de arquitetura: v5.0 / v5.0.1 (modelo de 4 eixos S×A×F×D).

| Precisa de… | Leia |
| --- | --- |
| Como planejar e conter agentes | `docs/maestro/PLANEJADOR.md` |
| Eixos S/A/F/D, composição S.A.D, routing completo, SharePoint, padrões de output, árvore de arquivos | `docs/maestro/REGISTRO-AGENTES.md` |
| Gaps abertos, decisões MN, proposta mestre, deploy checklist | `docs/maestro/GAPS-E-DECISOES.md` |
| Histórico de versões (v4.1 → v5.4.7) | `docs/maestro/HISTORICO.md` |

---

## Regras de economia (valem para todo agente)

1. **Planejar antes de executar.** Nenhum agente é carregado antes do
   plano do N0 (ver abaixo). Padrão: **1 agente**; até 3 sem perguntar;
   acima disso, mostrar o plano e pedir aprovação.
2. **Catálogo, não definições.** Para escolher, use o catálogo compacto
   desta página. A definição completa (`.claude/agents/<slug>.md` ou
   `SKILL.md` no SharePoint) só é lida para agentes que estão no plano.
3. **Referência sob demanda.** Não ler `docs/maestro/*` "por garantia" —
   só a seção que a tarefa precisa.
4. **Subagente devolve resumo.** Conclusão + números + fontes, nunca o
   conteúdo bruto de arquivos lidos.
5. **Guardiões no fim.** `aluci-guard` / `consist-guard` / `dedup-guard`
   rodam uma vez, no final, e só quando o entregável vai para fora
   (laudo, claim, parecer, proposta, orçamento).
6. **Opus é exceção justificada**, sempre com aprovação.
7. **Estado fora da conversa.** Decisões, números-chave e versões de
   artefato vão para arquivo de estado da sessão a cada marco. Números
   de laudo/claim/orçamento são sempre **relidos do arquivo**, nunca
   lembrados da conversa — é o erro mais perigoso após compactação.
   Uso da janela: avisar em 60%, salvar estado em 75%, nova sessão em 85%.

---

## Planejador (N0)

Antes de qualquer agente, o Maestro gera um plano:

```text
python -m src.maestro.planner "<pedido>" [--externo] [--json]
```

1. **Palavras-chave primeiro** (custo LLM zero) — `src/maestro/planner.py`,
   espelho de `maestro_routing_keywords`.
2. Nada casou → **planejador Haiku** decide com o catálogo compacto
   (`prompt_planejador_llm`).
3. Plano define: agentes, ordem, papel (primário / handoff / co-agente),
   modelo, teto de tokens e se requer aprovação.
4. Execução carrega **só** os agentes do plano.
5. Registro plano × executado em `maestro_plans` (migração candidata
   `supabase/migrations/2026_09_26_maestro_plans.sql`, pendente gate MN).

Regra de composição: **S** decide o primário (vertical dono da sessão);
**A** decide o handoff horizontal; **D** decide normas/RAG carregados;
**F** é acionado por qualquer agente sem mudar o dono da sessão.

## Hierarquia

| Nível | Quem | Modelo | Pode chamar | Teto/passo |
| --- | --- | --- | --- | --- |
| N0 | Maestro / planejador | Haiku 4.5 | N1 | 20 mil tokens |
| N1 | Orquestradores de segmento (S) e atividade (A) | Sonnet 5 | N2, N3 | 120 mil |
| N2 | Especialistas e subagentes | Sonnet 5 / Haiku 4.5 | N3 | 60 mil |
| N3 | Guardiões e ferramentas determinísticas | script / Haiku 4.5 | — | 10 mil |

No máximo 2 níveis de delegação; ninguém chama o próprio nível ou
acima. Opus 5.5 só para claims complexos, arquitetura e second opinion
crítico. Tetos são estimativas iniciais — recalibrar com `maestro_plans`.

---

## Catálogo compacto de agentes

21 operacionais (12 horizontais + 9 verticais); a v5.0.1 registrava
20 agentes. Detalhe, aliases e status em `docs/maestro/REGISTRO-AGENTES.md`.

**Verticais (S)** — primário da sessão

| S | Segmento | Agente | Palavras-chave principais |
| --- | --- | --- | --- |
| S1 | Rodovias | agente-infraestrutura (S1) | rodovia, pavimento, CBUQ, SICRO, DNIT |
| S2 | OAE | agente-infraestrutura (S2) | ponte, viaduto, OAE, NBR 7187 |
| S3 | Ferrovia | agente-infraestrutura (S3) | ferrovia, trilho, AMV, dormente |
| S4 | Metrô | agente-infraestrutura (S4) | metrô, NATM, PSD, VLT |
| S5 | Imobiliário | agente-S5-imobiliario (SharePoint) | — (coexiste com Manta 04) |
| S6 | Edificações | agente-edificacoes | ⚠ sem keyword de routing ainda |
| S7 | Portos | agente-portos | porto, ANTAQ, dragagem, berço, calado |
| S8 | Aeroportos | agente-aeroportos | aeroporto, pista de pouso, ANAC, TPS |
| S9 | Saneamento | agente-saneamento | ETA, ETE, adutora, esgoto, AySA |
| S10 | Energia | agente-energia | LT, subestação, ANEEL, RAP, ONS |
| S11 | Barragens | agente-barragens | barragem, vertedouro, CFRD, rejeitos |
| S14 | Óleo & Gás | agente-oleo-gas | ⚠ sem keyword de routing ainda |

**Horizontais (A)** — handoff

| Código | Agente | Atividade | Tier |
| --- | --- | --- | --- |
| Manta 00 | maestro (router) | planejamento/roteamento | Haiku→Sonnet |
| Manta 01 | agente-claims | A7 claims, pleito, reequilíbrio | Opus |
| Manta 02 | agente-contratual | A6 contratual | Sonnet |
| Manta 04 | agente-imobiliario | negócio imobiliário | Sonnet |
| Manta 05 | agente-orcamento | A3 orçamento | Sonnet |
| Manta 06 | agente-modelagem | A4 modelagem financeira | Sonnet/Opus |
| Manta 07 | agente-cronograma | A5 cronograma | Sonnet |
| Manta 13 | agente-bd | A1 proposta | Sonnet |
| Manta 14 | agente-apresentacoes | A1 apresentações | Sonnet |
| Manta 15 | agente-advisory | A8 advisory, A10 risco | Sonnet/Opus |
| Manta 16 | agente-arquiteto-ia | arquitetura IA | Opus |
| Manta 20 | agente-esg (manta-20-esg) | ESG — co-agente | Sonnet |

**Co-agentes de padrão**: menção a Motiva / CCR Rodovias / SP-258 /
SP-330 / Contorno Apucarana aplica `docs/PADRAO-OUTPUT-MOTIVA.md` sem
trocar o primário.

**Casos ambíguos** (primário → handoff): UHE → barragens → energia;
ETE + subestação → saneamento → energia; porto + pista de carga →
portos → aeroportos; adutora em barragem de rejeitos → saneamento →
barragens.

---

## RAG — Coleções em Supabase

Projeto `manta-maestro` (`ogxxgvgtulrbbppshjie`). Notas de embedder e
sub-prefixos em `docs/maestro/REGISTRO-AGENTES.md`.

| Coleção | Prefixo storage | Fontes iniciais | Status |
| --- | --- | --- | --- |
| rodovias | rod: | DNIT, SICRO, NBR-DNIT | ✅ Operacional (pré-existente) |
| oae | oae: | NBR 7187, 6118, 6122, PRL/RioSP | ✅ Operacional (pré-existente) |
| ferrovia | fer: | AREMA, DNIT ferroviário, concessionárias | ✅ Operacional (pré-existente) |
| metro | mtr: | ABNT NBR-NM, ARTESP, manual STM | ✅ Operacional (pré-existente) |
| portos | por: | ANTAQ, PIANC, ROM, editais BNDES | ✅ v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | ✅ v4.2 |
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, ERAS/AySA | ✅ v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE, IEC, NBR 5422 | ✅ v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, SNISB, Lei 12.334/14.066, NBR 13028/8681 | ✅ v4.2 |
| óleo-gás | og: *(sugerido)* | ANP, API 650/653, ASME B31.3/4/8, NFPA 30, HAZOP | 🔲 Não criada — segmento sem numeração real confirmada (ver "Eixo S") |
| edificações | edi: *(sugerido)* | NBR 15575, LEED, BIM | 🔲 Não criada — segmento renumerado para S6, depende do gate MN |

---

## Alertas que valem para toda sessão

- **Citações de "proposta real X" como fonte de validação**: já houve
  duas fabricações (MNT-2026-COM-1183_D, MNT-2026-COM-1301). Confirmar
  contra o SharePoint antes de aceitar.
- **SharePoint editado por várias sessões em paralelo**: sempre reler o
  arquivo antes de editar.
- **`manta_code` legado em S12–S14** colide com códigos de outros
  segmentos — risco de misroteamento. Detalhe em
  `docs/maestro/GAPS-E-DECISOES.md`.
- **Gate humano MN** antes de merge e antes de qualquer escrita em
  produção (SharePoint, Supabase).

---

## Versão atual

- **v5.5.0** (2026-09-26) — planejador N0 (`src/maestro/planner.py` +
  `docs/maestro/PLANEJADOR.md`), hierarquia N0–N3 com tetos de tokens,
  regras de economia e núcleo enxuto: `CLAUDE.md` de 1.143 para ~200
  linhas, conteúdo detalhado movido sem alteração para `docs/maestro/`.
  Migração candidata `maestro_plans` (não aplicada). Histórico completo
  em `docs/maestro/HISTORICO.md`.
