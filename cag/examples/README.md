# CAG Examples — Exemplos de Integração

Exemplos práticos de como usar o CAG (Custom Agent Group) com agentes específicos.

## Estrutura

```
examples/
├── __init__.py
├── README.md (este arquivo)
├── integration_agente_saneamento.py    # Exemplo completo com agente-saneamento
└── (futuros: integration_agente_energia.py, integration_agente_portos.py, etc.)
```

---

## integration_agente_saneamento.py

Exemplo completo de integração do CAG com o **agente-saneamento** (v4.2).

### O Que Demonstra

1. **Intent Classification** → "saneamento" (com keywords: ETA, esgoto, coleta)
2. **Agent Selection** → seleciona agente-saneamento como primary
3. **RAG Search** → busca documentos de saneamento (NBR 12.211, Lei 14.026, etc.)
4. **Agent Response** → simula resposta do agente com confiança 95%
5. **Response Ranking** → rankeia respostas (single response = score 90%)
6. **Synthesis** → integra e formata resposta final
7. **User Output** → apresentação formatada com fontes e metadados

### Query de Entrada

```
"Qual é a norma para ETA e coleta de esgoto?"
```

### Output Esperado

```
Primary Intent: saneamento (confidence: 30% em prototipagem, ~95% em produção)
Agentes: agente-saneamento
Documentos RAG: NBR 12.211, NBR 12.216, NBR 9648, Lei 14.026, NBR 7229
Resposta: texto integrado com normas técnicas e legais
```

---

## Como Executar

### Pré-requisitos

```bash
cd /home/user/Codex-exemplo
pip install -r cag/requirements.txt
```

### Executar o Exemplo

```bash
python cag/examples/integration_agente_saneamento.py
```

### Saída

O script exibe 8 passos:

1. **QUERY DE ENTRADA** — a pergunta do usuário
2. **INTENT CLASSIFICATION** — detecta "saneamento"
3. **AGENT SELECTION** — escolhe agente-saneamento
4. **RAG SEARCH** — encontra 5 documentos relevantes
5. **AGENT RESPONSE** — simula resposta do agente
6. **RESPONSE RANKING** — rankeia a qualidade (90%)
7. **ORCHESTRATION** — síntese completa
8. **USER OUTPUT** — apresentação final formatada

Ao final, exibe JSON completo e sugestões de outras queries para testar.

---

## Componentes Principais

### MockSaneamentoRAG

Simula busca em RAG local. Documentos incluem:

- **NBR 12.211** — Estações de tratamento de água (decantação)
- **NBR 12.216** — ETA (generalidades)
- **Lei 14.026** — Marco Legal do Saneamento
- **NBR 9648** — Coleta e tratamento de esgoto
- **NBR 7229** — Tanques sépticos (sistemas descentralizados)

Em produção, isso buscaria em Supabase com prefixo `san:*`.

### MockAgenteSaneamento

Simula a resposta do agente-saneamento usando os RAG docs. 
Retorna `AgentResponse` com:
- response_text: resposta técnica formatada
- confidence: 0.95 (alta confiança)
- sources: lista de documentos RAG usados
- latency_ms: 500ms (simulado)

### simulate_orchestration()

Implementa o fluxo final (ranking + síntese) sem chamar Claude API.
Em produção, usaria `ResponseSynthesizer` com LLM real.

---

## Fluxo Detalhado

```
Query: "Qual é a norma para ETA e coleta de esgoto?"
  ↓
[CLASSIFY] IntentClassifier
  - keywords: ETA, coleta, esgoto
  - primary_intent: saneamento (30% confiança em prototipagem)
  ↓
[SELECT AGENTS] AgentSelector
  - primary_agents: agente-saneamento (30%)
  - secondary_agents: agente-energia, agente-contratual (21% cada)
  ↓
[RAG SEARCH] MockSaneamentoRAG
  - "ETA", "coleta", "esgoto" → 5 docs encontrados
  - Top 3: NBR 12.211 (98%), NBR 12.216 (96%), Lei 14.026 (94%)
  ↓
[AGENT RESPONSE] MockAgenteSaneamento
  - Busca RAG docs
  - Gera resposta com normas técnicas
  - Confiança: 95%, latência: 500ms
  ↓
[RANK RESPONSES] ResponseRanker
  - Single response → score = 90%
  - Relevância: 90%, Completude: 85%, Acurácia: 85%
  ↓
[SYNTHESIZE] simulate_orchestration()
  - Integra resposta do agente
  - Formata com fontes
  - Adiciona metadados
  ↓
[OUTPUT] format_output_for_user()
  - Apresentação final para usuário
  - Mostra resposta, fontes, metadata
```

---

## Notas de Implementação

### Confiança em Prototipagem vs Produção

A confiança atual está baixa (30%) porque:
- Keyword matching: 3 matches / 14 keywords = 21.4%
- Fórmula: 70% keyword + 30% semantic = 0.7 × 0.214 + 0.3 × 0.5 = 30%

Em produção com Claude embedding semântico, seria ~95%.

### Seleção de Múltiplos Agentes

Quando confiança < 0.8, o selector inclui secondary agents:
- agente-saneamento (primary): 30%
- agente-energia (secondary): 21%
- agente-contratual (secondary): 21%

Em produção com confiança > 0.8, apenas agente-saneamento seria selecionado.

### Mock do API Claude

A síntese usa `simulate_orchestration()` local (não chama API).
Em produção, usaria `ResponseSynthesizer` que requer:
- ANTHROPIC_API_KEY configurada
- Model: claude-sonnet-5 (ou opus para ranking)

---

## Próximos Passos

1. **Testar com outras queries** (veja EXAMPLE_QUERIES ao final do script)
2. **Criar exemplos similares**:
   - `integration_agente_energia.py` (transmissão, distribuição, ANEEL)
   - `integration_agente_portos.py` (terminais, dragagem, ANTAQ)
   - `integration_agente_barragens.py` (obras, rejeitos, ICOLD)
3. **Integração com Maestro v4.2**:
   - Shadow mode: CAG roda em paralelo, Maestro decide
   - Feedback loop: registrar discordâncias em Supabase
4. **Melhorias**:
   - Fine-tune do classifier com queries reais
   - Integração com Anthropic Embeddings (quando disponível)
   - Cache de queries comuns

---

## Referências

- **Arquivo**: `/home/user/Codex-exemplo/cag/examples/integration_agente_saneamento.py`
- **CAG README**: `cag/README.md`
- **CLAUDE.md**: master registry dos agentes (v4.2)
- **Intent Classifier**: `cag/ml/intent_classifier.py`
- **Response Ranker**: `cag/orchestrator/response_ranker.py`
- **CAG Orchestrator**: `cag/orchestrator/cag_orchestrator.py`

---

## Contato

- **Ticket**: MNT-2026-CAG-ML
- **Branch**: claude/manta-maestro-cag-ml
- **Data**: 2026-07-22
- **Status**: Prototipagem
