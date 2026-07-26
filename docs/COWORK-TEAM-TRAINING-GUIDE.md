# Manta Maestro — Guia de Treinamento do Time Cowork

```
Cliente:        Interno (Manta Associados)
Projeto:        Manta Maestro v4.2 / v5.0 — Agent Registry & Routing
Documento:      Guia de Treinamento — Time Cowork
Objeto:         Onboarding técnico: Router, UI de Feedback, Testes, Troubleshooting
Versão:         v1.0 (2026-07-26)
Gerado por:     Claude AI — Manta Associados
Classificação:  Interno
ID:             MANTA-TRAINING-GUIDE-COWORK-20260726-01
```

> **Como usar este guia**: cada seção tem status explícito — **✅ Implementado**
> (existe no repo, com caminho de arquivo), **🔨 Pendente** (especificado, mas
> aguardando integração do time Cowork/manta-hub) ou **📝 Padrão recomendado**
> (boa prática sugerida, ainda não codificada). Não trate pseudocódigo de guia
> como contrato de API — a Seção 4 e o FAQ documentam pontos onde a
> documentação de fases anteriores diverge do schema real do banco.

---

## Sumário

1. [Maestro Router — Fundamentos](#1-maestro-router--fundamentos)
2. [Componentes de UI (Feedback, Notificações)](#2-componentes-de-ui-feedback-notificações)
3. [Testes & Validação](#3-testes--validação)
4. [Troubleshooting](#4-troubleshooting)
5. [Script de Vídeo (Outline)](#5-script-de-vídeo-outline)
6. [FAQ](#6-faq)
7. [Fontes & Ficha Técnica](#7-fontes--ficha-técnica)

---

## 1. Maestro Router — Fundamentos

### 1.1 Visão geral do fluxo

O Maestro (Manta 00) é o orquestrador central. Ele recebe a consulta do
usuário, calcula um score por agente candidato (20 agentes hoje: 11
horizontais + 9 segmentos verticais S1-S10, com S5/Túneis coberto por
S2+S4), decide se o roteamento é claro ou ambíguo, e despacha.

```
User Query
  ↓
1. Scoring por keyword (todos os agentes candidatos)
  ↓
2. primary_agent = maior score · secondary_agent = runner-up
  ↓
3. score_gap = primary_score - secondary_score
  ↓
4. Dois tipos de ambiguidade tratados de formas DIFERENTES:
  │
  ├─ Ambiguidade "multi-domínio real" (gap < 0.10)
  │    → Manta 16 (Orchestrator) despacha AMBOS os agentes em paralelo
  │      e funde as respostas (ver Seção 1.5 e docs/ORCHESTRATOR-
  │      IMPLEMENTATION-GUIDE.md)
  │
  └─ Ambiguidade "keyword insuficiente" (gap < 0.15 OU primary < 0.70)
       → Advanced Router (LLM tie-breaker, Sonnet) escolhe UM agente
         entre os top-2 (ver Seção 1.4 e docs/ADVANCED-ROUTING-
         IMPLEMENTATION-GUIDE.md — Phase 3.5)
  ↓
5. Dispatch ao(s) agente(s) final(is) + log em maestro_routing_trace
```

**Ponto importante para o time**: existem *dois* limiares de ambiguidade
documentados no repositório e eles **não são a mesma coisa** — é um erro
comum confundi-los:

| Limiar | Onde vive | O que acontece | Fonte |
|---|---|---|---|
| `score_gap < 0.10` | `maestro_routing_trace.is_ambiguous` | Dispatch **duplo** + merge (Manta 16) | `.claude/agents/maestro-orchestrator.md`, `supabase/migrations/2026_07_25_add_maestro_monitoring.sql` |
| `score_gap < 0.15` **OU** `primary_score < 0.70` | `AdvancedRouter.should_use_tie_breaker()` | LLM escolhe **um** agente entre os 2 (tie-break, não funde respostas) | `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md` |

Use o gap de 0.10 para decidir "isso é um projeto que toca dois
domínios de verdade?" (ex.: UHE com barragem + linha de transmissão).
Use o gap de 0.15/0.70 para decidir "o keyword-matching não teve
confiança suficiente para saber qual É o domínio único certo?" (ex.:
"Estação" — pode ser estação de metrô ou estação de tratamento).

### 1.2 Keyword scoring — como o score é calculado

O motor de roteamento (Fase 1, `backends/mcp/app/maestro.py` no
`manta-hub`) é **keyword match ponderado**, determinístico — não chama
LLM na rota "clara". Cada keyword casada soma um peso ao score do
agente candidato.

Exemplo real de composição de score (`docs/COWORK-INTEGRATION.md`):

```
Query: "AySA reabilitação da Planta Norte"

agente-saneamento:
  "saneamento" (contexto implícito do domínio)  → +100
  "AySA" (keyword de prioridade, ver CLAUDE.md)  → +120
  ────────────────────────────────────────────
  Score total ≥ 220
```

Note que essa escala (score bruto, ex. 220) é diferente da escala
normalizada 0–1 usada no `AdvancedRouter` (`primary_score: 0.95`) e no
`maestro_routing_trace.primary_score`. **Confirme qual escala o
componente que você está integrando espera** antes de hard-codar um
limiar — é uma fonte comum de bug silencioso (ver Seção 4.2).

### 1.3 Tabela de keywords → agente (Q1 do intake do Maestro)

Copiada e mantida em sincronia com `CLAUDE.md` (routing rules, seção
"ROUTING — Maestro (Manta 00)"). Sempre que este arquivo mudar, o
`scripts/test_routing.py` e `tests/routing/prompts.md` precisam ser
revisados juntos.

| Keywords (qualquer uma dispara) | Agente destino |
|---|---|
| saneamento, ETA, ETE, adutora, esgoto, AySA, drenagem urbana, SNIS | `agente-saneamento` (S8) |
| transmissão, LT, subestação, ANEEL, RAP, leilão transmissão, ONS, EPE | `agente-energia` (S9) |
| porto, terminal, ANTAQ, dragagem, molhe, berço, calado, contêiner, granel | `agente-portos` (S6) |
| aeroporto, pista pouso, ANAC, ICAO, TPS, TECA, balizamento | `agente-aeroportos` (S7) |
| barragem, vertedouro, CFRD, CCR, rejeitos, PNSB, ICOLD, CBDB, TSF | `agente-barragens` (S10) |
| rodovia, pavimento, CBUQ, BGS, terraplenagem, SICRO, DNIT | `agente-infraestrutura` S1 |
| ponte, viaduto, OAE, NBR 7187, túnel rodoviário | `agente-infraestrutura` S2 |
| ferrovia, trilho, AMV, dormente, via permanente | `agente-infraestrutura` S3 |
| metrô, estação, NATM, PSD, linha 4, linha 5, VLT | `agente-infraestrutura` S4 |

**Regra de desambiguação por especificidade**: quando duas linhas
casam (ex.: "estação" aparece em S4 e potencialmente em saneamento),
o Maestro deve preferir o agente **mais específico**, não o primeiro
match da tabela — é por isso que existe o tie-breaker (Seção 1.4) em
vez de resolver por ordem de declaração.

### 1.4 Tie-breaker — quando e como o LLM decide

Implementado em `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md`
(`AdvancedRouter`, Phase 3.5, modelo Sonnet, alvo: Fev/2027).

**Gatilho** (`should_use_tie_breaker`):
```python
score_gap = primary_score - secondary_score
return score_gap < 0.15 or primary_score < 0.70
```

**O que o LLM recebe**: a query original + os top-2 agentes candidatos
com score e descrição de especialidade de cada um. **O que ele
devolve**: um JSON `{"primary_agent", "confidence", "reasoning"}` —
sempre restrito aos dois candidatos originais (o parser rejeita
qualquer terceiro agente e cai de volta no score de keyword se o JSON
não parsear).

```json
{
  "primary_agent": "agente-saneamento",
  "confidence": 0.85,
  "reasoning": "Query menciona adutora + AySA explicitamente; agente-barragens não tem match direto"
}
```

Toda decisão de tie-break é logada em `maestro_tiebreaker_events`
(timestamp, prompt, primary_from_keywords, primary_from_llm,
confidence, reasoning) — isso é o que permite calcular a métrica de
efetividade abaixo.

**Métricas de sucesso do tie-breaker** (`docs/ADVANCED-ROUTING-
IMPLEMENTATION-GUIDE.md`):

| Métrica | Alvo |
|---|---|
| Taxa de uso do tie-breaker | 5–10% das queries |
| Taxa de aprovação (feedback do usuário) | > 85% |
| Taxa de mudança de decisão (LLM discorda do keyword) | 30–50% |
| Latência adicional | < 500ms |

### 1.5 Q2 intake — esclarecendo consultas ambíguas dentro do agente

**Atenção**: "Q2" não é uma pergunta que o *Maestro* faz antes de
rotear — é a segunda pergunta do intake obrigatório que **cada agente
vertical** faz *depois* de receber o dispatch. Está documentado no
`SKILL.md` de cada agente (ex.:
`sharepoint/01-agentes-fundamentais/agente-saneamento/SKILL.md`,
seção "PERGUNTA OBRIGATÓRIA INICIAL"):

```
Q1: Que eixo do domínio? (ex.: água / esgoto / drenagem / resíduos)
Q2: Qual fase do projeto?
    (A) Estudo prévio / EVTE          (E) O&M
    (B) Projeto básico                (F) Concessão / licitação
    (C) Projeto executivo             (G) Due diligence / M&A
    (D) Obra em execução              (H) Encerramento
Q3: País / marco regulatório?
Q4: Como os dados chegam? (DWG/DXF, PMSB, analíticos, etc.)
```

As 8 opções de Q2 mapeiam 1:1 com o **Eixo 3 — Ciclo de vida** do
`CLAUDE.md` master ("Todos os agentes verticais suportam as 8 fases
via intake Q2"). Isso é o que torna Q2 padronizado entre os 20
agentes: a fase de vida do projeto determina qual tier de RAG é
consultado (normas vs. projetos vs. estudos vs. templates) e qual
formato de entregável é gerado.

**Por que isso importa para o time Cowork**: se um usuário reclamar
que o agente certo respondeu "genérico demais" ou "sem contexto de
fase", o problema normalmente não é roteamento — é que o Q2 intake
não foi respondido/capturado antes do agente gerar a resposta.
Verifique o transcript antes de abrir um ticket de "routing incorreto".

---

## 2. Componentes de UI (Feedback, Notificações)

### 2.1 Status desta seção

🔨 **Pendente de integração** (Phase 2.1, dono: Cowork Team + MN).
Banco de dados e funções SQL já existem (✅); o botão em si na UI do
Cowork ainda não foi implementado. Fonte:
`docs/DEPLOYMENT-PHASE-2.md` § Part 4, `docs/PHASE-2-COMPLETION-
SUMMARY.md` § Phase 2.1.

### 2.2 Botão de Feedback — componente React

Mock-up de UI (`docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md`):

```
┌─────────────────────────────────────────┐
│ Agent Response                          │
│ "A profundidade ideal para a ETA..."   │
├─────────────────────────────────────────┤
│ Was this agent correct?                 │
│                                         │
│  👍 Helpful    👎 Incorrect            │
│                                         │
│  Confidence: [●●●●○] 4/5               │
│                                         │
│  [What agent should have answered?  ▼] │
│  └─ Selectable: same agent, other...   │
│                                         │
│  [Submit Feedback]                      │
└─────────────────────────────────────────┘
```

Componente (adaptado do pseudocódigo TypeScript oficial em
`docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md` § Task 1):

```tsx
interface FeedbackPanelProps {
  routingTraceId: string;   // id retornado por maestro_routing_trace
  agentSlug: string;
  agentResponse: string;
  sessionId: string;
}

function FeedbackPanel({ routingTraceId, agentSlug, agentResponse, sessionId }: FeedbackPanelProps) {
  const [confidence, setConfidence] = useState(3);
  const [status, setStatus] = useState<'idle' | 'submitting' | 'sent' | 'error'>('idle');

  async function handleFeedback(approved: boolean) {
    setStatus('submitting');
    try {
      await submitFeedback({ routingTraceId, approved, confidence });
      setStatus('sent');
    } catch (err) {
      setStatus('error'); // ver Seção 2.5 — tratamento de erro
    }
  }

  return (
    <div className="feedback-panel" role="group" aria-label="Feedback de roteamento">
      <p>Este agente ({agentSlug}) respondeu corretamente?</p>
      <button onClick={() => handleFeedback(true)} disabled={status === 'submitting'}>
        👍 Correto
      </button>
      <button onClick={() => handleFeedback(false)} disabled={status === 'submitting'}>
        👎 Incorreto
      </button>
      <input
        type="range" min={1} max={5} value={confidence}
        onChange={(e) => setConfidence(Number(e.target.value))}
        aria-label="Nível de confiança (1-5)"
      />
      {status === 'error' && <span className="feedback-error">Falha ao enviar. Tentar novamente.</span>}
      {status === 'sent' && <span className="feedback-ok">Feedback registrado. Obrigado!</span>}
    </div>
  );
}
```

**⚠️ Ponto crítico de integração — schema real vs. pseudocódigo dos
guias**: vários trechos em `docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md`
e `docs/DEPLOYMENT-PHASE-2.md` mostram um `insert` direto assim:

```javascript
// ⚠️ NÃO REFLETE O SCHEMA REAL — não copiar isto literalmente
supabase.table('maestro_user_feedback').insert({
  prompt: original_query,
  routed_agent: 'agente-saneamento',
  correct_agent: 'agente-saneamento',
  confidence: 5,
  approved: true,
  timestamp: datetime.utcnow(),
  session_id: session_id,
})
```

Mas a migração real (`supabase/migrations/2026_07_26_add_feedback_
tables.sql`) define `maestro_user_feedback` com estas colunas:

```sql
CREATE TABLE maestro_user_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamp DEFAULT now(),
  routing_trace_id uuid UNIQUE REFERENCES maestro_routing_trace(id) ON DELETE CASCADE,
  approved boolean NOT NULL,
  confidence int DEFAULT NULL,     -- escala 1-5
  notes text DEFAULT NULL,
  session_id text NULL,
  user_id text NULL,
  user_agent text DEFAULT NULL,
  was_actioned boolean DEFAULT false,
  action_type text DEFAULT NULL,
  action_description text DEFAULT NULL,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
```

**Não existem** colunas `prompt`, `routed_agent`, `correct_agent` ou
`feedback_type` nessa tabela — essa informação já mora em
`maestro_routing_trace` (que tem `prompt`, `primary_agent`,
`alternate_agents`), e o feedback só **referencia** essa trace via
`routing_trace_id`. **A forma correta e suportada de gravar feedback é
chamar a function SQL já pronta**, nunca inserir na tabela direto:

```javascript
const { data, error } = await supabase.rpc('process_routing_feedback', {
  p_routing_trace_id: routingTraceId,
  p_approved: approved,
  p_confidence: confidence, // 1-5
});
if (error) throw error;
```

`process_routing_feedback()` já cuida de: (1) gravar o feedback, (2)
atualizar `maestro_routing_trace.user_approved`, e (3) ajustar
`maestro_routing_keywords.confidence` (+0.05 se aprovado, -0.10 se
rejeitado) — é o "learning loop" mencionado no `CLAUDE.md`/roadmap.
Se o time Cowork inserir direto na tabela pulando a function, o passo
(3) — o efeito prático de "o roteamento aprende" — **não acontece**.

Pré-requisito: **o `routingTraceId` precisa existir antes do feedback
ser enviado** — ele é criado no momento do dispatch (ver
`MaestroMetricsClient.insert_routing_trace()` em
`docs/MONITORING-MAESTRO.md` § 2). Se a UI do Cowork não recebe/repassa
esse id junto com a resposta do agente, o botão de feedback não tem
como funcionar — é o item nº 1 do checklist de integração (Seção 4.3).

### 2.3 Ações de aprovação / rejeição / escalonamento

Além do par aprovar/rejeitar do feedback de roteamento, a
Classificação Automática de Documentos (Phase 2.3,
`docs/DOCUMENT-AUTO-CLASSIFICATION.md`) usa um conjunto maior de
ações em notificações:

```python
actions=[
    {"label": "Concordar e mover", "action": "approve"},
    {"label": "Discordar", "action": "reject"},
    {"label": "Revisar manualmente", "action": "escalate"},
]
```

Fluxo de decisão:

| Ação do usuário | O que acontece |
|---|---|
| **Concordar (approve)** | Move o arquivo para `03_Projetos/<Segmento>/`, grava `approved=true` |
| **Discordar (reject)** | Não move o arquivo; grava `approved=false` + `correct_agent` sugerido pelo usuário |
| **Revisar manualmente (escalate)** | Arquiva em `_Review`, não grava aprovação/rejeição (fica pendente de triagem humana) |

Para o feedback de roteamento (Seção 2.2), pense em "escalonamento"
como: se `approved=false` repetido, o item deve virar candidato a
GitHub Issue automático (Seção 3.2/3.3) em vez de só decrementar
confiança de keyword silenciosamente.

### 2.4 Notificações — payload e dados que trafegam

Estrutura de notificação enviada ao Cowork
(`docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md` § Phase 2.3, Task 3):

```python
notification = await cowork_client.create_notification(
    user_id=user_id,
    title=title,                 # ex.: "📄 design.pdf"
    message=message,             # ex.: "Classified as agente-saneamento"
    type="document_classification",
    actions=actions,             # lista approve/reject/escalate acima
    metadata={
        "source": "maestro_document_classifier",
        "timestamp": datetime.utcnow().isoformat(),
    }
)
```

Campos que **o time Cowork precisa garantir que persistem** no
round-trip da UI (senão a ação do usuário não pode ser processada
corretamente no backend):

| Campo | Por quê é necessário |
|---|---|
| `routing_trace_id` (feedback) / `file_url` (classificação) | Chave para religar a ação à decisão original |
| `suggested_agent` + `confidence` | Exibido na notificação e necessário se o usuário aprovar sem editar |
| `actions[].action` | Usado no `switch`/`if` do handler (`approve`/`reject`/`escalate`) |
| `user_id`, `session_id` | Necessários para auditoria e para A/B testing (Seção 3.3) |
| `timestamp` | Usado no cálculo de SLA de resposta (timeout de 3600s no listener, `docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md` § Task 1) |

### 2.5 Tratamento de erro — 📝 Padrão recomendado

Os guias de fase não especificam tratamento de erro para o botão de
feedback; o padrão abaixo estende o que já existe de forma consistente
com o resto do sistema (mesmo padrão de retry usado nos scripts de
ingestão RAG e sync SharePoint, que têm "error handling + retry
logic" documentado em `docs/PHASE-2-COMPLETION-SUMMARY.md`).

```typescript
async function submitFeedback(
  payload: { routingTraceId: string; approved: boolean; confidence: number },
  attempt = 1,
): Promise<void> {
  try {
    const { error } = await supabase.rpc('process_routing_feedback', {
      p_routing_trace_id: payload.routingTraceId,
      p_approved: payload.approved,
      p_confidence: payload.confidence,
    });
    if (error) throw error;
  } catch (err) {
    // Rede instável / timeout: até 2 retries com backoff curto
    if (attempt < 3 && isRetryable(err)) {
      await sleep(300 * attempt);
      return submitFeedback(payload, attempt + 1);
    }
    // Falha definitiva: nunca perder o sinal de feedback silenciosamente.
    // Guarda em fila local (IndexedDB/localStorage) para reenvio posterior
    // e mostra toast de erro não-bloqueante ao usuário.
    queueFeedbackForRetry(payload);
    throw err;
  }
}

function isRetryable(err: unknown): boolean {
  // Timeout, 5xx, erro de rede => retryable.
  // Erro de validação (4xx do Supabase, ex. routing_trace_id inexistente) => não retryable.
  return isNetworkOrTimeoutError(err) || isServerError(err);
}
```

Checklist mínimo de UX de erro:
- Nunca travar a tela do agente esperando o feedback ser confirmado
  (enviar de forma otimista, reconciliar depois).
- Diferenciar erro de rede (retry automático) de erro de validação
  (ex.: `routing_trace_id` não encontrado — não adianta reenviar, tem
  que reportar bug).
- Persistir feedback pendente localmente se a rede cair, para não
  perder o sinal — perda silenciosa de feedback é o problema descrito
  na Seção 4.3 ("feedback loop não atualiza").

---

## 3. Testes & Validação

### 3.1 Cenários de teste manual — as 30 rotas de roteamento

A suíte oficial (`tests/COMPREHENSIVE-TEST-SUITE.md`, gerada por 30
agentes Sonnet em paralelo) define **30 cenários de roteamento** em 6
categorias de 5 casos cada:

| Categoria | O que valida | Exemplo |
|---|---|---|
| Single-Segment (5) | Roteamento claro, alta confiança (>90%) | "ETE do AySA com SNIS indicators" → `agente-saneamento` (96%) |
| Multi-Segment Orchestration (5) | Ativação do Manta 16 e merge de resposta | "BR-364 rodovia + OAE ponte" → S1 + S2 |
| Ambiguous Routing (5) | Gatilho do tie-breaker / Q2 do intake | "Estação" (metrô vs. estação de tratamento) |
| Edge Cases (5) | Typos, keywords parciais, jargão sobreposto | "PNSB + TSF" com erro de digitação em "barragen" |
| High-Confidence Clear Routing (5) | Vocabulário regulatório específico | "ANEEL R6 transmission line design" → `agente-energia` (95%) |
| Cross-Concern Queries (5) | Coordenação multi-domínio sem ambiguidade real | "ETE + subestação no canteiro" → saneamento + energia |

**Casos manuais adicionais** (36 prompts extras, separados por
segmento) vivem em `tests/routing/prompts.md` — úteis para QA humano
quando o script automatizado ainda não roda no ambiente do Cowork.

Execução:

```bash
# Suíte completa (30 casos, todas as categorias)
python tests/test_routing_scenarios.py --all

# Por categoria específica
python tests/test_routing_scenarios.py --category single-segment
python tests/test_routing_scenarios.py --category orchestration
python tests/test_routing_scenarios.py --category ambiguous

# Runner do repositório atual (lê tests/routing/prompts.md, chama a API real)
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/test_routing.py tests/routing/prompts.md --verbose
```

`scripts/test_routing.py` já existe no repo: ele faz parsing do
padrão `` `prompt` → **agente-x** `` em `tests/routing/prompts.md`,
chama o modelo com um system prompt simplificado de roteamento, mede
latência (p50/p95) e falha o processo (`exit 1`) se a acurácia cair
abaixo de 90%.

Critérios de sucesso (`tests/COMPREHENSIVE-TEST-SUITE.md`):

| Métrica | Alvo |
|---|---|
| Acurácia geral | ≥ 90% |
| Acurácia single-segment | ≥ 95% |
| Detecção de orquestração multi-agente | ≥ 85% |
| Detecção de ambiguidade | ≥ 80% |
| Tolerância a edge case (typos/informal) | ≥ 70% |

### 3.2 Simulação de feedback — gerar dado fake e observar a análise

Passo a passo para treinar sem esperar tráfego real de usuário:

```sql
-- 1. Criar uma routing trace fake (simula um dispatch já ocorrido)
INSERT INTO maestro_routing_trace (
  prompt, prompt_hash, primary_agent, primary_score,
  alternate_agents, score_gap, is_ambiguous
) VALUES (
  'Preciso projetar uma ETA de ciclo completo para 200 mil hab.',
  md5('Preciso projetar uma ETA de ciclo completo para 200 mil hab.'),
  'agente-saneamento', 0.94,
  '[{"agent":"agente-infraestrutura-s1","score":0.12}]'::jsonb,
  0.82, false
) RETURNING id;
-- guarde o id retornado como :trace_id

-- 2. Simular feedback do usuário via a function oficial (não insert direto!)
SELECT process_routing_feedback(
  p_routing_trace_id := ':trace_id',
  p_approved := true,
  p_confidence := 5
);

-- 3. Repetir passos 1-2 ~15-20x para o mesmo agente para passar o limiar
--    de "boost" (analyze_feedback_and_recommend exige count >= 15 para
--    recomendar 'Boost keywords')

-- 4. Rodar a análise semanal manualmente e observar a recomendação
SELECT * FROM analyze_feedback_and_recommend(CURRENT_DATE);
```

Saída esperada depois de simular reprovações (`approved := false`)
repetidas (≥ 3x no mesmo dia) para um agente:

```
 agent_slug        | recommendation                                         | priority | affected_feedback_count
--------------------+---------------------------------------------------------+----------+--------------------------
 agente-saneamento | Review and demote keywords for agente-saneamento         | HIGH     | 4
                    | (rejected 4x today)
```

Isso é o mecanismo real por trás do "GitHub issue automático" citado
no roadmap (`docs/DEPLOYMENT-PHASE-2.md` § 4.2) — a criação do issue
em si ainda é um passo manual/script separado, a function só gera a
recomendação estruturada.

### 3.3 A/B testing — control vs. experimental routing

Tabela real (`supabase/migrations/2026_07_26_add_feedback_tables.sql`),
**não** a mesma forma mostrada em alguns guias de fase anterior — use
esta como fonte da verdade:

```sql
CREATE TABLE maestro_routing_ab_tests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  test_name text NOT NULL,
  test_slug text UNIQUE NOT NULL,
  description text,
  variant_a_prompt text NOT NULL,   -- keywords/config atual (control)
  variant_b_prompt text NOT NULL,   -- keywords/config nova (experimental)
  control_rate float DEFAULT 0.9,   -- % de tráfego em A
  treatment_rate float DEFAULT 0.1, -- % de tráfego em B
  status text DEFAULT 'draft',      -- draft, active, paused, completed
  started_at timestamp, ended_at timestamp,
  variant_a_samples int DEFAULT 0, variant_a_approval_rate float DEFAULT 0.0,
  variant_b_samples int DEFAULT 0, variant_b_approval_rate float DEFAULT 0.0
);
```

Criando e ativando um teste:

```sql
-- 1. Criar o teste em modo draft
INSERT INTO maestro_routing_ab_tests (
  test_name, test_slug, description,
  variant_a_prompt, variant_b_prompt,
  control_rate, treatment_rate, status
) VALUES (
  'Saneamento — keywords AySA reforçadas',
  'saneamento-aysa-boost-2026-08',
  'Testa se reforçar peso de AySA/PIRHA reduz falsos negativos vs energia',
  'keywords atuais (peso AySA=120)',
  'keywords propostas (peso AySA=160, + PIRHA, ERAS)',
  0.90, 0.10, 'draft'
);

-- 2. Ativar (marca started_at)
UPDATE maestro_routing_ab_tests
SET status = 'active', started_at = now()
WHERE test_slug = 'saneamento-aysa-boost-2026-08';

-- 3. Ao fim do período de coleta, atualizar taxas de aprovação
--    (calculadas a partir de maestro_user_feedback + tag de variante
--    aplicada no runtime, não incluída neste schema — precisa de uma
--    coluna própria ou de uma tabela de join se o time for medir isso
--    em produção; hoje o schema grava só o agregado final)
UPDATE maestro_routing_ab_tests
SET status = 'completed', ended_at = now(),
    variant_a_approval_rate = 0.86, variant_a_samples = 140,
    variant_b_approval_rate = 0.93, variant_b_samples = 15
WHERE test_slug = 'saneamento-aysa-boost-2026-08';
```

**Gotcha para o time**: o schema real acima usa `variant_a_prompt` /
`variant_b_prompt` / `control_rate` / `treatment_rate`. Um exemplo em
`docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md` § Task 4 mostra colunas
diferentes (`control_agent`, `experimental_agent`, `test_start`,
`test_end`, `sample_size`) que **não existem** na migração aplicada —
mais um caso de "pseudocódigo do guia divergiu do schema real"
(mesmo padrão do alerta na Seção 2.2). Ao escrever SQL de verdade,
confira sempre a migração, não o guia narrativo.

---

## 4. Troubleshooting

### 4.1 Agente não responde (timeout / erro)

**Onde olhar primeiro**: `maestro_runtime_metrics` (latência) e os
alertas configurados em `docs/MONITORING-MAESTRO.md`.

```sql
-- Latência recente do agente com problema
SELECT agent_slug, latency_p50, latency_p95, latency_p99,
       CASE WHEN latency_p95 < 300 THEN '✅ OK'
            WHEN latency_p95 < 500 THEN '⚠️ WARNING'
            ELSE '❌ SLA_BREACH' END as slo_status
FROM maestro_metrics_daily
WHERE agent_slug = 'agente-energia'
  AND date = CURRENT_DATE - interval '1 day';

-- Fallback rate (indica que o agente está caindo para tier/modelo alternativo)
SELECT agent_slug, fallback_rate, COUNT(*) as fallback_cases
FROM maestro_metrics_daily
WHERE date = CURRENT_DATE - interval '1 day'
  AND fallback_rate > 0.05
GROUP BY agent_slug, fallback_rate;
```

Passo a passo:
1. **P95 > 500ms** → provável problema de tier (Opus sendo chamado
   quando Sonnet bastaria) ou RAG vetorial lento. Ver
   `maestro_metrics_current_hour` para tier distribution na última
   hora.
2. **Fallback rate > 5%** → alerta configurado deveria já ter disparado
   (Slack). Verifique `fallback_reason` (`latency`, `cost`, `error`)
   em `maestro_runtime_metrics` para o request específico.
3. Se não há métrica nenhuma sendo gravada → o problema não é o
   agente, é a instrumentação (`insert_maestro_metric` não está sendo
   chamado no dispatch) — verifique se o deploy mais recente do
   `manta-hub` ainda chama `MaestroMetricsClient.insert_metric()`.
4. Escalonar para o time Maestro (`manta-hub`) se o SLA de latência
   estiver estourado de forma consistente (não um pico isolado).

### 4.2 Roteamento para o agente errado

**Debug**: sempre comece pela `maestro_routing_trace`, não pela
resposta do agente.

```sql
SELECT prompt, primary_agent, primary_score, alternate_agents,
       score_gap, is_ambiguous, executed_agent, user_approved
FROM maestro_routing_trace
WHERE prompt_hash = md5('<cole o prompt exato do usuário aqui>')
ORDER BY timestamp DESC
LIMIT 1;
```

Checklist de diagnóstico:
1. **`is_ambiguous = false` mas o agente errado ganhou** → problema de
   peso de keyword. Confira `maestro_routing_keywords` para o agente
   esperado — se `confidence` estiver baixo (feedback negativo passado
   já penalizou essa keyword, ver função `process_routing_feedback`),
   isso explica o score baixo.
2. **`is_ambiguous = true` mas não foi orquestrado nem tie-break** →
   verifique se o deploy do `manta-hub` já tem o Advanced Router
   (Phase 3.5) e o Orchestrator (Phase 2.2) integrados — ambos ainda
   são 🔨 pendentes de implementação em produção conforme
   `docs/PHASE-2-COMPLETION-SUMMARY.md`.
3. **Confirme contra a suíte de testes**: o prompt (ou um muito
   parecido) está em `tests/routing/prompts.md`? Se sim, qual era o
   agente esperado ali? Isso separa "bug de roteamento" de "prompt do
   usuário genuinamente ambíguo e não coberto ainda".
4. **Registre o feedback correto imediatamente** — mesmo investigando
   manualmente, sempre chame `process_routing_feedback(trace_id,
   approved=false, confidence=...)` para o caso real, para que o
   keyword correspondente seja penalizado automaticamente.
5. **Se o padrão se repetir (≥ 3x/dia para o mesmo agente)** → vira
   candidato a issue automático via `analyze_feedback_and_recommend()`
   (Seção 3.2). Não espere a rotina semanal se for urgente — rode a
   função manualmente com `CURRENT_DATE`.

### 4.3 Loop de feedback não atualiza (dado obsoleto / dessincronizado)

Esta é a categoria de bug mais fácil de introduzir por engano — a
Seção 2.2 já descreve a causa mais comum (inserir direto na tabela em
vez de chamar a function). Checklist completo:

1. **O feedback foi de fato persistido?**
   ```sql
   SELECT * FROM maestro_user_feedback
   WHERE routing_trace_id = ':trace_id';
   ```
   Se vazio: o botão do Cowork não está chamando
   `process_routing_feedback` (ou o `routing_trace_id` nunca chegou
   até a UI — ver pré-requisito na Seção 2.2).

2. **`timestamp` vs. `created_at`** — a tabela tem *ambas* as colunas,
   ambas com `DEFAULT now()`. A function `analyze_feedback_and_
   recommend()` filtra por `DATE(uf.timestamp)`; outras queries de
   dashboard (`docs/DEPLOYMENT-PHASE-2.md`) filtram por `created_at`.
   Se algum código de integração customizado sobrescrever só uma das
   duas colunas manualmente (em vez de deixar o `DEFAULT now()`
   agir), os dois caminhos de leitura passam a divergir — um
   dashboard mostra o feedback, o job semanal "não vê". Prefira nunca
   setar `timestamp`/`created_at` manualmente na chamada.

3. **`maestro_routing_keywords.confidence` não mudou mesmo após
   feedback aprovado** — releia a lógica de `process_routing_
   feedback()`: o boost de +0.05 só é aplicado às keywords do
   `primary_agent` da trace que **não** aparecem literalmente no
   texto do prompt (`keyword <> ANY(string_to_array(lower(prompt),
   ' '))`) — isso é proposital (evita reforçar o óbvio), mas costuma
   parecer "bug" para quem não leu a function. Confirme se a keyword
   que você espera ver subir de confiança realmente não está contida
   no prompt literal antes de abrir um chamado.

4. **Job semanal não rodou** — confirme o agendamento via `pg_cron`:
   ```sql
   SELECT * FROM cron.job WHERE jobname = 'maestro_weekly_feedback_analysis';
   SELECT * FROM cron.job_run_details
   WHERE jobid = (SELECT jobid FROM cron.job WHERE jobname = 'maestro_weekly_feedback_analysis')
   ORDER BY start_time DESC LIMIT 5;
   ```
   Se não existir nenhum job cadastrado, o cron ainda não foi
   configurado no ambiente (item pendente do checklist de deploy,
   `docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md` § Task 2) — rode a
   function manualmente enquanto isso não é resolvido.

5. **RLS (Row Level Security)** — se as tabelas de feedback tiverem
   policies restritivas configuradas depois da migração inicial, o
   `insert`/`rpc` pode falhar silenciosamente do lado do client (sem
   exception visível) dependendo de como o erro é engolido no
   `try/catch` do componente. Sempre logue `error` do retorno do
   Supabase client, nunca apenas o `data`.

---

## 5. Script de Vídeo (Outline)

**Título sugerido**: "Manta Maestro para o Time Cowork: Roteamento,
Feedback e Troubleshooting" · **Duração alvo**: 11–13 min

| # | Tempo | Cena / tela | Narração (pontos-chave) |
|---|---|---|---|
| 1 | 0:00–0:45 | Slide de título + logo Manta | Objetivo do vídeo, quem deve assistir (time Cowork), pré-requisitos (acesso Supabase, repo `Codex-exemplo` clonado) |
| 2 | 0:45–2:30 | Diagrama do fluxo (Seção 1.1) animado | Passo a passo: query → score → gap → 2 caminhos de ambiguidade (orquestração vs. tie-breaker). Enfatizar que são gatilhos DIFERENTES (0.10 vs 0.15/0.70) |
| 3 | 2:30–4:00 | Tela dividida: `CLAUDE.md` routing rules + `tests/routing/prompts.md` | Mostrar a tabela de keywords ao vivo, rodar 2-3 prompts de exemplo mentalmente ("qual agente ganharia aqui?") |
| 4 | 4:00–5:30 | `SKILL.md` do agente-saneamento, seção de intake | Explicar Q1-Q4, com foco em Q2 (8 fases do ciclo de vida) e por que isso não é "roteamento", é refinamento pós-dispatch |
| 5 | 5:30–8:00 | Editor de código: componente `FeedbackPanel` + Supabase dashboard | Demo ao vivo: clicar 👍/👎 no protótipo, mostrar o INSERT acontecendo em `maestro_user_feedback` via `process_routing_feedback`. Destacar o alerta do pseudocódigo desatualizado (Seção 2.2) |
| 6 | 8:00–9:30 | Terminal: `python scripts/test_routing.py tests/routing/prompts.md -v` | Rodar a suíte, mostrar acurácia/latência no output, explicar os 6 categorias das 30 rotas |
| 7 | 9:30–11:00 | SQL editor: simulação de feedback + `analyze_feedback_and_recommend()` | Rodar o passo a passo da Seção 3.2 ao vivo, mostrar a recomendação aparecendo |
| 8 | 11:00–12:30 | Dashboard de troubleshooting (queries da Seção 4) | Mostrar como diagnosticar os 3 problemas mais comuns em produção |
| 9 | 12:30–13:00 | Slide de encerramento | Onde encontrar este guia, quem é dono de cada workstream (Cowork/Maestro/DevOps), como abrir um ticket |

**Notas de produção**:
- Gravar telas em resolução consistente com o resto do material de
  onboarding Manta (evitar zoom excessivo em terminal).
- Incluir legendas em PT-BR (público interno da Manta).
- Publicar em `04_IA/Manta-Maestro/01-agentes-fundamentais/` no
  SharePoint junto com o link deste guia.

---

## 6. FAQ

**P: O Maestro sempre chama um LLM para rotear?**
R: Não. A rota "clara" (gap ≥ 0.15 e primary_score ≥ 0.70) é puro
keyword-match determinístico, sem chamada de modelo — é rápida e
gratuita. Só as rotas ambíguas acionam Sonnet (tie-breaker) ou
duplo-dispatch + merge (Orchestrator/Manta 16, que aí sim usa Opus).

**P: score_gap < 0.10 e score_gap < 0.15 parecem a mesma coisa. Por
que dois limiares?**
R: Não são a mesma decisão. O de 0.10 (Manta 16) responde "este
projeto genuinamente precisa de dois especialistas trabalhando
juntos?" (ex.: barragem + LT). O de 0.15/0.70 (Advanced Router)
responde "o keyword matching não teve confiança de qual É o único
agente certo?" (ex.: "estação", sem mais contexto). Um resulta em
resposta fundida de 2 agentes; o outro resulta em 1 agente escolhido
por LLM. Ver tabela comparativa na Seção 1.1.

**P: Por que meu `insert` direto em `maestro_user_feedback` com
`prompt`/`routed_agent` deu erro de coluna inexistente?**
R: Porque esses campos não existem nessa tabela — eles vivem em
`maestro_routing_trace`. `maestro_user_feedback` só referencia a trace
via `routing_trace_id`. Use sempre `process_routing_feedback()` (RPC),
nunca insert direto — ver Seção 2.2 para o porquê (o RPC também
atualiza `maestro_routing_keywords`, algo que um insert cru não faz).

**P: Onde vejo os 20 agentes e seus aliases sem abrir 20 arquivos?**
R: Via MCP do `manta-hub` (`list_maestro_agents`), documentado em
`docs/COWORK-INTEGRATION.md`. Não requer credencial extra além do
custom connector já configurado no workspace Cowork.

**P: O botão de feedback já está em produção no Cowork?**
R: Não, ainda é 🔨 pendente (dono: Cowork Team + MN). O banco de dados,
as functions SQL e o design da UI já existem — falta só a integração
front-end + o job semanal agendado. Ver checklist em
`docs/DEPLOYMENT-PHASE-2.md` § Part 4.

**P: Como sei se um "caso ambíguo" deveria ter sido tie-break ou
orquestração, numa investigação real?**
R: Olhe `maestro_routing_trace.score_gap` e `is_ambiguous`. Se
`is_ambiguous=true`, o gap estava abaixo de 0.10 → deveria ter sido
orquestração dupla. Se o gap estava entre 0.10 e 0.15 (ou
primary_score < 0.70 mesmo com gap maior), deveria ter passado pelo
tie-breaker do Advanced Router. Combine com os testes de
`tests/routing/test_multiagent_dispatch.md` para casos de referência.

**P: A/B testing de roteamento já roda em produção?**
R: A tabela `maestro_routing_ab_tests` existe e é funcional para
tracking manual (Seção 3.3), mas a atribuição automática de tráfego
control/experimental e o cálculo automatizado das taxas de aprovação
por variante ainda não têm implementação de referência no repo — hoje
é um processo majoritariamente manual/SQL.

**P: Quem eu acionamos para cada tipo de problema?**
R: Roteamento/keywords → Time Maestro (`manta-hub`). Botão de
feedback/UI/notificações → Time Cowork + MN. RAG/ingestão e sync
SharePoint → Time Claude Code. Ver tabela de donos completa na Seção
7.

---

## 7. Fontes & Ficha Técnica

### 7.1 Arquivos-fonte consultados neste guia

| Arquivo | Conteúdo usado |
|---|---|
| `CLAUDE.md` | Mapa de 20 agentes, tabela de routing rules (Q1), ciclo de vida de 8 fases |
| `.claude/agents/maestro-orchestrator.md` | Manta 16, gatilho de 0.10, dataclasses I/O, exemplos de merge |
| `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md` | Advanced Router / tie-breaker, gatilho 0.15/0.70, schema `maestro_tiebreaker_events` |
| `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md` | Algoritmo de dispatch duplo + merge |
| `docs/MONITORING-MAESTRO.md` | Métricas de runtime, SLOs de latência, alertas |
| `docs/DEPLOYMENT-PHASE-2.md` | Checklist de deploy Phase 2, status de cada workstream |
| `docs/PHASE-2-COMPLETION-SUMMARY.md` | Status ✅/🔨 de cada entregável de Phase 2 |
| `docs/INTEGRATION-GUIDES-PHASE-2.1-2.3.md` | Pseudocódigo de UI de feedback, notificações, A/B test (com divergências sinalizadas) |
| `docs/DOCUMENT-AUTO-CLASSIFICATION.md` | Ações approve/reject/escalate, fluxo de notificação |
| `docs/COWORK-INTEGRATION.md` | Exemplo real de score composto (AySA), MCP tools disponíveis |
| `tests/COMPREHENSIVE-TEST-SUITE.md` | 30 cenários de roteamento, critérios de sucesso |
| `tests/routing/prompts.md` | 36 prompts manuais de QA por segmento |
| `tests/routing/test_multiagent_dispatch.md` | Casos de orquestração multi-agente |
| `scripts/test_routing.py` | Runner de teste real do repositório |
| `supabase/migrations/2026_07_25_add_maestro_monitoring.sql` | Schema real de `maestro_runtime_metrics`, `maestro_routing_trace` |
| `supabase/migrations/2026_07_26_add_feedback_tables.sql` | Schema real de `maestro_user_feedback`, `maestro_routing_keywords`, `maestro_feedback_analysis`, `maestro_routing_ab_tests`, functions SQL |

### 7.2 Ficha técnica

```
Cliente:        Interno (Manta Associados)
Projeto:        Manta Maestro v4.2 / v5.0
Documento:      Guia de Treinamento — Time Cowork
Objeto:         Onboarding: Router, UI de Feedback, Testes, Troubleshooting
Versão:         v1.0 — criação inicial
Data Criação:   26/07/2026
Gerado por:     Claude AI — Manta Associados
Ferramenta:     Claude Code (subagent de documentação)
Classificação:  Interno
ID:             MANTA-TRAINING-GUIDE-COWORK-20260726-01
```
