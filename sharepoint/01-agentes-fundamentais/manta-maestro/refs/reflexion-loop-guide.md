# refs/reflexion-loop-guide.md — manta-maestro

Referência canônica do **Reflexion Loop pré-entrega** — Upgrade A do
roadmap v4.7 (MNT-IA-20260712-001, §2). Introduz autocrítica estruturada
antes de o Maestro entregar ao usuário: o output é avaliado contra os
`success_criteria` do P2, e se não passa, o Maestro re-executa (com
limite de iterações e escalação humana).

Fonte: Shinn et al. 2023 "Reflexion: language agents with verbal
reinforcement learning" (NeurIPS) + Madaan et al. 2023 "Self-Refine:
iterative refinement with self-feedback" (NeurIPS).

Aplicar SOMENTE em tarefas classificadas como **star2** ou **star3**
(intake §Q3 do SKILL.md). Star1 (perguntas triviais) NÃO passa por
Reflexion — custo/latência não compensa.

---

## 1. Fluxo em ASCII art

```
                   ┌──────────────────────────────┐
                   │  P2 Contract emitido por      │
                   │  Maestro → subagente X        │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │  Subagente X executa a tarefa │
                   │  e produz OUTPUT_i (i=1..3)   │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │  Maestro roda AUTOCRÍTICA     │
                   │  (Sonnet 4.6, prompt §2.4)    │
                   │  Compara OUTPUT_i vs          │
                   │  P2.success_criteria          │
                   └──────────────┬───────────────┘
                                  │
                        ┌─────────┴─────────┐
                        │                   │
                        ▼                   ▼
                ┌───────────────┐   ┌──────────────────┐
                │ TODOS         │   │ ≥1 critério       │
                │ critérios     │   │ falhou            │
                │ passaram      │   └────────┬─────────┘
                └───────┬───────┘            │
                        │                    ▼
                        │           ┌──────────────────┐
                        │           │ i < max_iter (3)?│
                        │           └────────┬─────────┘
                        │                    │
                        │           ┌────────┴────────┐
                        │           │                 │
                        │           ▼                 ▼
                        │    ┌────────────┐  ┌──────────────┐
                        │    │ SIM: emitir │  │ NÃO: ESCALAR │
                        │    │ feedback +  │  │ para humano  │
                        │    │ re-executar │  │ (MN)         │
                        │    └──────┬─────┘  └──────────────┘
                        │           │
                        │           │  (i := i+1, loop)
                        │           └────────────┐
                        │                        │
                        ▼                        │
                ┌───────────────┐                │
                │ ENTREGAR ao   │◄───────────────┘
                │ usuário +      │
                │ log em         │
                │ agent_episodes │
                └───────────────┘
```

---

## 2. Prompt template de autocrítica

Executado com Sonnet 4.6, temperatura 0.2, max_tokens 800. Injetado
como user message num call novo (não continua a conversa do subagente).

```
Você é o crítico técnico do Manta Maestro. Sua tarefa é avaliar se o
output abaixo cumpre os critérios de sucesso do contrato P2. Seja
severo mas justo — falso positivo (aprovar ruim) é 10x pior que falso
negativo (rejeitar bom).

## Contrato P2 (extrato)

Objetivo:
{p2.objective}

Critérios de sucesso (binários):
{p2.success_criteria}

## Output do subagente {p2.target_agent}

{output_i}

## Sua tarefa

Para cada critério, responda em JSON estrito:

{
  "critical_review": "<2-3 frases apontando o que falhou ou brilhou>",
  "criteria_check": [
    {"criterion": "<texto do critério 1>", "passed": true|false, "evidence": "<citação do output>"},
    {"criterion": "<texto do critério 2>", "passed": true|false, "evidence": "<citação do output>"},
    ...
  ],
  "all_passed": true|false,
  "recommendation": "deliver" | "retry_with_feedback" | "escalate_human",
  "feedback_for_retry": "<se retry_with_feedback: instrução curta ao subagente>"
}

Regras:
- `passed=true` SÓ se você conseguir citar evidência textual literal.
- `all_passed` = AND lógico dos passed.
- `retry_with_feedback` apenas se o erro é *corrigível* (falta uma
  seção, número fora da faixa, referência ausente). Se o erro é
  *estrutural* (escopo errado, alucinação de fatos), use `escalate_human`.
- `feedback_for_retry` fala EM 2ª PESSOA com o subagente
  ("adicione X", "recalcule Y usando Z").
```

---

## 3. Critérios de parada

Ordem de precedência (avaliada a cada iteração):

1. **Convergência**: `all_passed == true` → entrega direta.
2. **Max iterações**: `i >= 3` → escalar humano (MN). Não roda uma 4ª.
3. **Guard**: `budget_usd_used >= P2.budget_usd` → escalar humano.
4. **Recomendação escalação**: `recommendation == "escalate_human"` →
   escalar imediatamente, sem re-executar.
5. **Reversão de score**: se `output_i` ficou PIOR que `output_{i-1}`
   em ≥1 critério que antes passava, escalar (evita degradação).

Escalação humana emite notificação no Slack + cria issue GH com o
histórico completo (P2 + outputs_1..i + feedbacks + judge scores).

---

## 4. Custos e trade-offs

- **Custo por iteração**: ~US$0.03-0.10 (Sonnet 4.6, ~1500 tokens de
  contexto + 500 de output para o crítico).
- **Custo típico por tarefa**: 1.4 iterações média (v4.7 baseline)
  ⇒ +50-70% do custo do subagente. Aceito para star2/star3.
- **Latência**: +8-12s por iteração de crítica. Aceito.
- **Star1** (respostas < 30s): NÃO aplicar Reflexion. Perde propósito.

Métrica de eficácia: v4.7 target = **taxa de aprovação na 1ª iteração
≥ 65%**. Se < 40%, o P2 está mal calibrado (critérios impossíveis)
ou o subagente está sub-treinado.

---

## 5. Três exemplos reais de self_critique

### 5.1 Exemplo BOM — aprovação na 1ª iteração

**P2 objetivo**: `"Listar 5 riscos técnicos do TUP Porto Central"`

**Critérios**:
- `"Cita PIANC 158 no risco geotécnico"`
- `"Cada risco tem probabilidade × impacto"`
- `"Ordenado do maior para o menor risco"`

**Output i=1**: [lista com 5 riscos, PIANC 158 citada no risco #2,
matriz P×I preenchida, ordenação correta]

**Judge output**:
```json
{
  "critical_review": "Output cumpriu todos os critérios. Boa citação da PIANC 158 no risco geotécnico. P×I coerente com baseline histórica.",
  "criteria_check": [
    {"criterion": "Cita PIANC 158 no risco geotécnico", "passed": true, "evidence": "Risco 2 (assentamento diferencial): ... conforme PIANC 158 §4.2.1 ..."},
    {"criterion": "Cada risco tem probabilidade × impacto", "passed": true, "evidence": "Todos os 5 têm P=n/5 e I=n/5"},
    {"criterion": "Ordenado do maior para o menor risco", "passed": true, "evidence": "Risco 1 P×I=20, Risco 5 P×I=4"}
  ],
  "all_passed": true,
  "recommendation": "deliver"
}
```

### 5.2 Exemplo AMBÍGUO — retry na 2ª

**P2 objetivo**: `"Estimar TIR real da concessão rodoviária Fase 5"`

**Critérios**:
- `"TIR real em 3 cenários (base/pessimista/otimista)"`
- `"Comparar com 2 benchmarks nomeados"`
- `"Discutir risco cambial explicitamente"`

**Output i=1**: TIR em 3 cenários OK. Comparou com "CCR Nova Dutra"
mas o 2º benchmark é `"outros ativos similares"` (não nomeado). Sem
menção a risco cambial.

**Judge output**:
```json
{
  "critical_review": "TIR bem calculada, mas 2 dos 3 critérios falharam. Benchmark 2 genérico não conta. Risco cambial ausente e é RELEVANTE (fundo BR investindo em ativo com IPCA).",
  "criteria_check": [
    {"criterion": "TIR real em 3 cenários", "passed": true, "evidence": "Base 9.2%, Pess 6.8%, Ot 11.4%"},
    {"criterion": "Comparar com 2 benchmarks nomeados", "passed": false, "evidence": "Só CCR Nova Dutra nomeado; 2º é 'outros ativos'"},
    {"criterion": "Discutir risco cambial explicitamente", "passed": false, "evidence": "N/A — ausente"}
  ],
  "all_passed": false,
  "recommendation": "retry_with_feedback",
  "feedback_for_retry": "Nomeie o 2º benchmark (sugestão: Motiva EcoRodovias 2023 ou CCR AutoBAn 2022) com TIR real reportada. Adicione parágrafo curto sobre risco cambial: o ativo é IPCA-indexado mas o fundo mede em USD."
}
```

Output i=2 corrigiu ambos ⇒ delivered.

### 5.3 Exemplo ESCALAÇÃO — humano assumiu

**P2 objetivo**: `"Análise de viabilidade de descaracterização de barragem X"`

**Output i=1**: agente sugeriu ADIAR descaracterização para 2032 (Lei
14.066 exige 2027). Judge detectou alucinação de fato legal.

**Judge output**:
```json
{
  "critical_review": "ALUCINAÇÃO GRAVE. Lei 14.066 art. 6º é INEQUÍVOCA quanto ao prazo 2027 para alteamentos a montante. Recomendar adiar é ilegal. Erro estrutural — não é corrigível por retry porque o agente pode não ter na base a versão atualizada da lei.",
  "criteria_check": [
    {"criterion": "Cita Lei 14.066 explicitamente", "passed": true, "evidence": "Lei 14.066 mencionada 4x"},
    {"criterion": "Recomendação é acionável e legal", "passed": false, "evidence": "Sugere adiar para 2032, ilegal"}
  ],
  "all_passed": false,
  "recommendation": "escalate_human",
  "feedback_for_retry": ""
}
```

MN foi notificado, criou issue GH com histórico, e refez o P2
explicitando `skills_preloaded: ["barragens-lei-14066-vigente-2027"]`
+ critério novo `"prazo recomendado ≤ 2027"`. Nova tarefa passou.

---

## 6. Instrumentação

- **Log**: cada iteração grava em `agent_episodes` com `iteration=i`,
  `judge_output JSONB`, `all_passed`, `feedback`, `cost_usd`.
- **View**: `v_reflexion_stats` — taxa 1-iter, média de iterações,
  taxa de escalação humana por agente.
- **Alerta**: taxa de escalação > 10% em janela 7d ⇒ ping para MN
  investigar (o P2 está mal calibrado ou o agente precisa retrain).

---

## Ver também

- `SKILL.md` §14.A — política operacional do Reflexion Loop
- `p2-contract-template.md` — como os `success_criteria` são
  estruturados
- `episodic-memory-schema.md` — como iterações são persistidas
- Roadmap MNT-IA-20260712-001 §2 — motivação e prior art
