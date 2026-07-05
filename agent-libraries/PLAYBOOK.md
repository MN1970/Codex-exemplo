# Fan-out Playbook — Manta Maestro

Situações canônicas de cliente → **quais agentes despachar em paralelo** →
**como o Maestro sintetiza**. Complementa a cláusula 1 do
[SKILL.md do Maestro](../sharepoint/01-agentes-fundamentais/agente-maestro/SKILL.md)
e os 21 [agent-libraries](./README.md).

**Regra dourada:** tarefas independentes = **fan-out obrigatório**.
Serialização = exceção documentável no `manta_trace.reason_serial`.

**Notação:** `[N × agentes]` = fan-out simultâneo; `→` = serial obrigatório.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## Cenário 1 — Cliente notifica atraso em obra (pleito)

**Sinal:** "cliente disse que a obra vai atrasar 90 dias", "recebi notificação
de disruption", "reunião com contratada sobre delay".

**Fan-out** (mesmo turno):
- **01 Claims** — TIA retrospectiva (CRN-M-005) + Measured Mile (CLM-M-003) via KEs 016-020
- **07 Cronograma** — recompõe as-built + Monte Carlo de recuperação (CRN-M-002/006)
- **02 Contratual** — cláusulas de force majeure / suspensão + fundamentação
- **05 Orçamento** — impacto de custo indireto do atraso (curva S revista)

**Serialização inevitável:** Maestro só sintetiza *depois* que 07 devolve o
recompute (Claims consome baseline vs as-built). Se 07 não devolver em 60s,
Maestro emite parecer preliminar e reabre com hard data quando 07 chegar.

**Saída ao usuário:** parecer único do Maestro com anexos (TIA + MM + cláusulas
+ impacto financeiro).

---

## Cenário 2 — Estudo prévio de rodovia com pontes e drenagem

**Sinal:** "novo trecho BR-XXX", "vamos participar de edital de projeto
rodoviário", "cliente quer viabilidade".

**Fan-out** (multi-vertical + multi-horizontal):
- **S1 Rodovias** — RDV-M-001..005 (memoriais preliminares)
- **S2 OAE** — OAE-M-001 (pré-dim de pontes/viadutos do trecho)
- **S8 Saneamento** — se drenagem urbana relevante (SAN-M-001 modelo hidráulico)
- **05 Orçamento** — SICRO composição preliminar (ORC-M-001) via KE-027
- **07 Cronograma** — cronograma-mestre + Monte Carlo preliminar
- **04 Imobiliário** — pré-cadastro de faixa de domínio

**Sem serialização** — cada agente responde independente sobre seu escopo. O
Maestro consolida no formato de proposta ou EVTE.

**Saída ao usuário:** dossiê consolidado com uma seção por agente + memória
comum de premissas.

---

## Cenário 3 — Due Diligence de concessão rodoviária

**Sinal:** "cliente vai comprar concessão", "análise pré-M&A", "DD para banco".

**Fan-out** (7 agentes em paralelo):
- **S1 Rodovias** — auditoria técnica do trecho
- **S2 OAE** — auditoria do portfólio de OAEs usando KE-041 (custos recuperação Ecovias) + KE-042 (comparativo inspeção)
- **15 Advisory** — parecer normativo (KEs 034-038: ANTT, TCE-MG, Procrofe)
- **06 Modelagem** — FCM histórico + projetado (MOD-M-001, KE-037/039)
- **02 Contratual** — matriz de riscos + histórico de aditivos
- **04 Imobiliário** — faixa de domínio, servidões, gravames
- **01 Claims** — histórico de pleitos e passivo contingente

**Sem serialização inicial** — cada agente tem escopo isolado. Depois de 7
respostas, **rodada 2 obrigatória** com Opus escalado: resolve conflitos
(ex.: S1 diz "pavimento OK", 01 diz "pleito recente por defeito de pavimento").

**Saída ao usuário:** parecer consolidado + red flags + racional financeiro.

---

## Cenário 4 — AySA (estudo prévio saneamento Argentina) — prioridade

**Sinal:** "AySA", "Buenos Aires saneamento", "concessão água/esgoto Argentina".

**Fan-out** (bloco B7 completo):
- **S8 Saneamento** — SAN-M-001 (modelo EPANET) + SAN-M-004 (business case), consome KEs 015, 043-047
- **15 Advisory** — análise regulatória comparativa BR × AR (usa KE-024, 044)
- **06 Modelagem** — FCM da concessão + sensibilidade tarifária (KE-046)
- **02 Contratual** — desenho contratual comparado (KE-043 evidencia que isso
  determina universalização)
- **13 BD** — mapeamento de stakeholders e oportunidades adjacentes

**Sem serialização.** É o cenário-flagship do WF-AKP-001 — 4 dos 7 KEs de B7
foram ingeridos exatamente para alimentar isso.

**Saída ao usuário:** business case AySA + análise regulatória + modelagem
financeira.

---

## Cenário 5 — Pleito de reequilíbrio econômico-financeiro em concessão

**Sinal:** "vamos entrar com pedido de reequilíbrio", "ANTT solicitou
manifestação", "TCE questionou nossos números".

**Fan-out** (bloco B5 completo — 10 KEs):
- **01 Claims** — CLM-M-004 (Resolução ANTT 5.850/2019 via KE-035)
- **02 Contratual** — CTR-M-001 (aditivo) + fundamentação (KE-036: Fator D)
- **15 Advisory** — parecer independente (ADV-M-001, KE-037: Procrofe fases)
- **06 Modelagem** — FCM antes/depois (MOD-M-001)

**Serialização parcial:** 06 precisa do valor do desequilíbrio calculado por
01 antes de rodar FCM. Solução: **01 emite valor preliminar rapidinho**, 06
começa com esse valor, refina quando 01 emite valor final.

**Rodada 2:** se 15 diverge de 01 sobre nexo causal, Opus resolve.

**Saída ao usuário:** requerimento + FCM + parecer + minuta de aditivo.

---

## Cenário 6 — Leilão de transmissão (ANEEL)

**Sinal:** "próximo leilão ANEEL LT", "vamos ao leilão de dezembro", "R1-R5
publicado".

**Fan-out** (bloco não coberto ainda — usa stub S9):
- **S9 Energia** — ENR-M-001 (LT) + ENR-M-003 (RAP para leilão)
- **13 BD** — BDV-M-001 (fit score) + BDV-M-004 (pricing)
- **05 Orçamento** — CAPEX + OPEX
- **06 Modelagem** — TIR × RAP com sensibilidade
- **07 Cronograma** — prazo do leilão + prazo pós-outorga

**Sem serialização inicial.** Depois de todos responderem, decisão **go/no-go**
pelo humano — Maestro NÃO emite recomendação binária (regra política).

**Saída ao usuário:** dossiê go/no-go com números claros por dimensão.

---

## Cenário 7 — Consulta conceitual (sem projeto específico)

**Sinal:** "como funciona TIA?", "qual a diferença entre reequilíbrio e
renegociação?", "o que é PPC no Last Planner?".

**Fan-out** (retrieval-only):
- **16 Arquiteto-IA** — retrieval irrestrito no MASTER-CATALOG
- (Opcional) **agente-alvo** — se a pergunta é claramente de um domínio (ex.:
  "TIA" → 01/07 respondem em paralelo)

**Não é fan-out amplo** — cenário raro em que o Maestro **responde direto**
usando o retrieval do 16. Objetivo é velocidade + citações precisas.

**Saída ao usuário:** resposta curta + 2-3 KEs citados com `ke_codigo`.

---

## Cenário 8 — Inspeção rotineira revela OAE danificada

**Sinal:** "inspeção mostrou infiltração 88%", "ponte tem risco urgente",
"cliente pede plano de recuperação".

**Fan-out:**
- **S2 OAE** — OAE-M-004 (GDE/UnB) + OAE-M-005 (plano) via KE-040/041/042
- **05 Orçamento** — custo baseado em benchmark Ecovias (KE-041)
- **07 Cronograma** — sequenciamento das intervenções (obra em serviço vs
  desvio de tráfego)
- **15 Advisory** — se concessionária, parecer sobre gatilho de reequilíbrio
  (recuperação não prevista)

**Serialização:** 05 depende de S2 identificar a intervenção. Fan-out
retomado depois.

**Saída ao usuário:** laudo + plano + orçamento + cronograma + eventual
gatilho contratual.

---

## Padrão anti-fan-out (quando NÃO paralelizar)

Cenários em que serial é obrigatório:

1. **Escalada de tier**: Haiku falhou → não faz sentido rodar 3 Haikus em
   paralelo do mesmo prompt. Escalar único agente para Sonnet.
2. **Dependência de dado crítica**: 06 Modelagem NÃO pode rodar antes de 05
   Orçamento emitir CAPEX. Serial obrigatório.
3. **Conflito de escrita**: se 3 agentes precisam editar a mesma célula do
   mesmo XLSX no SP, serializar por lock ou rota alternativa.
4. **Gate humano intermediário**: Maurício exige revisar output de S1 antes de
   acionar 05. Serial explícito por instrução política.

Toda serialização precisa aparecer no `manta_trace.reason_serial` para
auditoria posterior.

---

## Métricas de qualidade do fan-out (v2 roadmap)

- **latência média** por cenário (fan-out vs serial equivalente)
- **taxa de conflito** entre sub-agentes (quantas rodadas 2 precisaram)
- **cobertura KEs** por resposta (quantos KEs foram citados)
- **satisfação do humano** (feedback pós-entrega)

Serão coletadas via `manta_trace` e alimentarão o **16 Arquiteto-IA** para
propor evoluções do playbook (A/B tests de fan-out shape).
