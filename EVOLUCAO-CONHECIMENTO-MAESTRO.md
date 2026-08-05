# Evolução de Conhecimento do Manta Maestro — Learning Loop v5.0

**Data**: 2026-08-02  
**Tema**: Como o Maestro aprende, melhora e evolui com o tempo  
**Status**: ✅ Confirmado (Feedback Loop Contínuo)

---

## Visão Geral — O Maestro Nunca Para de Aprender

```
Dia 1 (v5.0 Go-Live):
  Conhecimento inicial: 500 documentos RAG + 20 SKILL.md

Semana 4:
  + 50 projetos executados
  + 5.000 queries processadas
  + Feedback de 80% dos consultores
  → Heurísticas MSE refinadas 1x
  → RAG atualizado com 20 novos docs

Mês 3:
  + 500 projetos executados
  + 50.000 queries processadas
  + Taxa de sucesso detectada (qual agent/metal funciona melhor)
  → MSE v1.2 (heurísticas melhoradas)
  → Novos padrões identificados (adicionados a SKILL.md)
  → RAG expandido para 600+ docs

Ano 1:
  + 5.000 projetos executados
  + 500.000 queries processadas
  + 100% cobertura de casos (ambíguos resolvidos)
  → MSE v2.0 (aprendizado de máquina integrado)
  → Conhecimento consolidado em 25 SKILL.md (evolução natural)
  → RAG cresceu para 1.000+ docs (knowledge base muito maior)
```

---

## 1. Feedback Loop — Como Aprende

### A. Feedback Explícito (Do Usuário)

```
Usuário recebe resultado do Maestro
    │
    ├─ ⭐⭐⭐⭐⭐ "Perfeito! Orçamento impecável"
    ├─ ⭐⭐⭐ "Bom, mas precisaria de mais detalhes na justificativa"
    ├─ ⭐⭐ "Resultado tem inconsistência X. Maestro errou em Y"
    └─ ⭐ "Completamente errado. Começar do zero."
         │
         ↓
    MAESTRO REGISTRA:
    ├─ Qual agente foi usado? (Manta 05 — orçamento)
    ├─ Qual modelo foi usado? (Sonnet)
    ├─ Qual a complexidade detectada? (0.45)
    ├─ Qual foi o resultado? (texto X)
    ├─ Qual o feedback? (⭐⭐⭐ = 3/5)
    ├─ Qual foi o erro específico? (sem detalhes em fundações)
    └─ Timestamp: 2026-08-15 14:23:00
         │
         ↓
    ARMAZENA NA TABELA:
    ├─ maestro_execution_log (linha com quality_score = 60)
    ├─ maestro_feedback (novo! feedback explícito)
    │   ├─ session_id
    │   ├─ rating (1-5)
    │   ├─ comment (texto do usuário)
    │   └─ error_category (se rating < 3: "missing_detail", "wrong_calc", etc)
    └─ maestro_learning_queue (fila para processar feedback)
         │
         ↓
    ANÁLISE SEMANAL:
    ├─ Manta 05 + Sonnet teve 60% de feedback satisfatório
    ├─ Erro recorrente: "falta detalhes em fundações"
    ├─ Ação: Adicionar seção "Detalhamento de Fundações" ao SKILL.md
    ├─ Reexaminar: Prompts que causaram erro (para ajustar)
    └─ Atualizar MSE: Se complexidade > 0.45 + "fundação" → escalar para Opus
```

### B. Feedback Implícito (Do Comportamento)

```
Maestro monitora IMPLICITAMENTE:
    │
    ├─ Escalação automática ocorreu?
    │   └─ Sonnet retornou "I'm not confident" → escalou para Opus
    │   └─ Mas Opus também não conseguiu?
    │       → FLAG: "Esse tipo de problema não é adequado para Opus"
    │       → Ação: Adicionar "humano review obrigatório" para esse tipo
    │
    ├─ Handoff ocorreu?
    │   └─ Saneamento → Energia (subestação em ETA)
    │   └─ Energia → Saneamento (bomba de recirculação)
    │   → Padrão: esses dois agentes trabalham bem juntos
    │   → Ação: Adicionar "handoff bidirecional" ao SKILL.md
    │
    ├─ Tempo de execução?
    │   └─ Orçamento complexo levou 45 min (vs baseline 15 min)
    │   └─ Porque? Consultas múltiplas ao SICRO
    │   → Ação: Cache de SICRO queries para speedup
    │
    ├─ Taxa de retrabalho?
    │   └─ 20% dos orçamentos retornaram com "refazer"
    │   └─ Padrão: quando projeto > 5 componentes, taxa sobe para 30%
    │   → Ação: Oferecer "orçamento simplificado" vs "detalhado"
    │
    └─ Custos de modelo?
        └─ Opus era escalado 40% das vezes, mas sucesso só 60%
        └─ Haiku escalado 10% das vezes, sucesso 85%
        → Ação: Rebalancear thresholds MSE (ser mais agressivo em Haiku)
```

---

## 2. Evolução de Componentes — O Que Muda

### Componente 1: SKILL.md (Conhecimento Codificado)

```
INICIAL (v5.0):
┌────────────────────────────────────┐
│ agente-orcamento SKILL.md          │
├────────────────────────────────────┤
│ # Agente Orçamento (Manta 05)      │
│                                    │
│ ## Intake (Q1-Q4)                  │
│ - Que? Orçamento                   │
│ - Qual? Executivo/pré-projecto     │
│ - Onde? Localidade                 │
│ - Como? XLSX/memo                  │
│                                    │
│ ## Execução                        │
│ 1. Desagrega projeto em itens      │
│ 2. Consulta SICRO vigente          │
│ 3. Aplica fatores regionais        │
│ 4. Produz planilha                 │
│                                    │
│ ## Handoffs                        │
│ - Para Modelagem: se financeiro    │
│ - Para Cronograma: se timeline     │
│                                    │
│ ## Referências                     │
│ - SICRO (sinapi.org.br)            │
│ - NBR 12721 (índices)              │
│ - Padrão BDI Manta (25%)           │
└────────────────────────────────────┘

APÓS 3 MESES DE FEEDBACK:
┌────────────────────────────────────┐
│ agente-orcamento SKILL.md v1.1     │
├────────────────────────────────────┤
│ # Agente Orçamento (Manta 05)      │
│                                    │
│ ## NOVO: Tipos de Orçamento        │
│ 1. Simplificado (1 página)         │
│    - Apenas valores por item       │
│    - Sem justificativa             │
│    - Uso: Pré-viabilidade rápida   │
│                                    │
│ 2. Executivo (5 páginas)           │
│    - Resumo + desagregação         │
│    - Justificativas de fatores     │
│    - Uso: Aprovação geral          │
│                                    │
│ 3. Detalhado (20+ páginas) ← NOVO  │
│    - Composições SICRO completas   │
│    - Detalhamento por subsistema   │
│    - Análise de fundações          │ ← NOVO (foi feedback)
│    - Cronograma integrado          │ ← NOVO (melhoria sugerida)
│    - Uso: Projeto executivo        │
│                                    │
│ ## NOVO: Padrão de Fundações       │
│ Se projeto tem estrutura:          │
│   • Investigação geotécnica → X%   │
│   • Sondagem SPT → Y%              │
│   • Escavação → Z% do custo total  │
│   • Referência: casos AySA/Rodovias│
│                                    │
│ ## NOVO: Checklist de Escalação    │
│ Escalar para Opus se:              │
│   ✓ Projeto > 5 componentes        │
│   ✓ Fundações complexas            │
│   ✓ Valor total > R$ 10M           │
│   ✓ Localidade remota (fatores+)   │
│                                    │
│ ## Handoffs (ATUALIZADO)           │
│ - Para Modelagem: SEMPRE (novo!)   │
│ - Para Saneamento: se ETA/ETE inline│
│ - Para Energia: se subestação      │
│ - Para Cronograma: se > 12 meses   │
│                                    │
│ ## Referências (EXPANDIDO)         │
│ - SICRO (sinapi.org.br)            │
│ - NBR 12721 (índices)              │
│ - ABNT NBR 6122 (fundações) ← NOVO │
│ - Padrão BDI Manta (25%)           │
│ - Casos AySA 2024-2026 (novo RAG)  │
└────────────────────────────────────┘

PADRÃO: A cada trimestre, SKILL.md evolui com:
  • Novos tipos de problema detectados
  • Novos padrões identificados
  • Novos handoffs adicionados
  • Novas referências integradas
```

### Componente 2: RAG (Knowledge Base)

```
MÊS 0 (Go-live):
  Documentos: 500
  ├─ Normas (NBR): 50
  ├─ SICRO: 50 (composições amostrais)
  ├─ Padrões Manta: 20
  ├─ Casos anteriores: 100
  ├─ Legislação: 30
  ├─ Benchmarks: 50
  └─ Outros: 200

MÊS 1 (Feedback levanta gaps):
  Usuário: "Maestro não sabe que em SP profundidade mínima de adução é 0.8m"
  Ação:
    • Pesquisar legislação SP (código sanitário)
    • Inserir 5 novos documentos (legislação regional)
    • Tagger em RAG: "san:br:sp:legislacao"
    • MSE atualiza: detecta "SP" → consulta "san:br:sp:*"
  
  Documentos agora: 505 (+5)

MÊS 2 (Padrão novo emerge):
  Maestro detecta: "30% dos orçamentos mencionam 'pré-moldado' "
  Ação:
    • Criação de coleção especial "san:br:pre-moldado:*"
    • 20 documentos (fabricantes, códigos SICRO, padrões)
    • SKILL.md: nova seção "Componentes pré-moldados"
  
  Documentos agora: 525 (+20)

MÊS 3 (Internacionalização):
  Consultor Argentina: "Legislação AySA é diferente de Brasil"
  Ação:
    • Pesquisar normas Argentina (ERAS, CAA)
    • 50 novos documentos em sub-coleção "san:ar:*"
    • MSE detecta: "Argentina" → consulta "san:ar:*" primeiro
    • SKILL.md: "Legislação Brasil vs Argentina" seção
  
  Documentos agora: 575 (+50)

ANO 1 (Consolidação):
  Documentos: ~1.000+ (mais que 2x inicial)
  Sub-coleções criadas por:
    • Segmento (saneamento, energia, portos, etc)
    • País (Brasil, Argentina)
    • Tipologia (ETA, ETE, adução, etc)
    • Recência (2026, 2025, arquivos históricos)
  
  Crescimento é ORGÂNICO: cada consulta/feedback adiciona novo doc
```

### Componente 3: MSE (Metal Selection Engine) — Heurísticas Melhoram

```
VERSÃO 1.0 (Go-live):
┌──────────────────────────────────────────────────────────┐
│ MSE Heurísticas Simples                                 │
├──────────────────────────────────────────────────────────┤
│ def select_metal(prompt, agent):                         │
│     score = 0                                            │
│     if "claim" in prompt:      score += 0.3              │
│     if "complex" in prompt:    score += 0.2              │
│     if "multi_domain" in prompt: score += 0.3            │
│     if "value > R$500M" in prompt: score += 0.2          │
│                                                          │
│     if score > 0.75: return "Opus"                       │
│     elif score > 0.50: return "Sonnet"                   │
│     else: return "Haiku"                                 │
│                                                          │
│ Acuracy: 75% (vs 90% almejado)                          │
└──────────────────────────────────────────────────────────┘

MÊS 1 FEEDBACK:
  • 25% das queries Opus retornaram "uncertain"
  • 15% das queries Haiku falharam (deveriam ser Sonnet)
  • Padrão: Keywords simples são insuficientes
  
  Ação: Adicionar feature extraction
  ┌──────────────────────────────────────────────────────────┐
  │ MSE Heurísticas v1.1 (Melhorada)                         │
  ├──────────────────────────────────────────────────────────┤
  │ def select_metal(prompt, agent):                         │
  │     # Feature extraction (novo!)                         │
  │     has_numbers = len(re.findall(r'\d+', prompt)) > 3   │
  │     has_ambiguity = ("ou" or "talvez") in prompt        │
  │     has_risk_words = any(w in prompt for w in          │
  │                          ["claim", "arbitragem", "risco"])
  │     input_tokens = estimate_tokens(prompt)              │
  │                                                          │
  │     score = 0                                            │
  │     if has_risk_words: score += 0.5                      │
  │     if has_ambiguity: score += 0.2                       │
  │     if input_tokens > 5000: score += 0.1                │
  │     if has_numbers and not agent.is_vertical: score += 0.2 │
  │     # ... (mais lógica)                                  │
  │                                                          │
  │ Accuracy: 82% → 88% (melhora de +6%)                     │
  └──────────────────────────────────────────────────────────┘

MÊS 3 FEEDBACK (Padrões Detectados):
  • Quando agente-orcamento + "ETA > 100L/s" → 60% escalação para Opus
  • Mas sucesso em Sonnet foi 85%! (não precisava Opus)
  • Padrão: "grande capacidade ≠ automaticamente complexo"
  
  • Quando agente-saneamento + "Argentina" → 70% escalação
  • Mas 90% sucesso já em Sonnet (AySA tem SKILL.md rico)
  
  Ação: Refatorar heurísticas por (agent, domain) pair
  ┌──────────────────────────────────────────────────────────┐
  │ MSE Heurísticas v1.2 (Contextualizada)                  │
  ├──────────────────────────────────────────────────────────┤
  │ ESCALATION_RULES = {                                     │
  │     ("agente-orcamento", "capacity > 100L/s"): 0.30,    │
  │     ("agente-orcamento", "claim"): 0.70,                │
  │     ("agente-saneamento", "Argentina"): 0.10,           │
  │     ("agente-saneamento", "ambiguous_location"): 0.50,  │
  │     # ... (100+ rules criadas a partir de histórico)    │
  │ }                                                        │
  │                                                          │
  │ Accuracy: 88% → 92% (melhora de +4%)                     │
  └──────────────────────────────────────────────────────────┘

ANO 1 (Machine Learning):
  • 500.000 queries processadas
  • 50.000 pares (prompt, agent, model, success) coletados
  • Treinamento: pequeno modelo de scoring (NN leve)
  
  MSE v2.0 (com ML):
  ├─ Embedding do prompt (768D via Claude)
  ├─ Consulta histórico similar (cosine similarity)
  ├─ Retorna: "88% desses prompts usaram Sonnet com sucesso"
  ├─ Predição: "Para este prompt, probabilidade Sonnet = 0.85"
  ├─ Accuracy: 92% → 96%
  └─ Tempo MSE: 100ms (vs 50ms antes, tradeoff aceitável)
```

### Componente 4: Agent Success Rates (Aprendizado Individual)

```
TABELA: agents table — new columns

┌─────────────────────────────────────────────────────────────┐
│ Manta Code │ Agent            │ Success │ Avg Cost │ Quality │
├─────────────────────────────────────────────────────────────┤
│ 03-S8      │ agente-saneamento│ 87.2%   │ $2.15    │ 88/100  │
│ Manta 05   │ orcamento        │ 91.5%   │ $1.80    │ 92/100  │
│ Manta 07   │ cronograma       │ 79.3%   │ $2.50    │ 81/100  │
│ Manta 01   │ claims           │ 95.2%   │ $4.20    │ 97/100  │
│ ...        │ ...              │ ...     │ ...      │ ...     │
└─────────────────────────────────────────────────────────────┘

MÊS 1:
  agente-cronograma success rate: 79.3%
  Root cause analysis:
    • 12% falhas: "prazo insuficiente (usuário não informou)"
    • 5% falhas: "dependências não-lineares (projeto complexo)"
    • 2% falhas: "mudanças mid-project (não coberto por prompts)"
  
  Ação: Adicionar perguntas ao intake
    • "Qual é o prazo MÁXIMO aceitável?"
    • "Há dependências paralelas? Quantas?"
    • "Este é um projeto com mudanças esperadas?"
  
  Ação: Atualizar SKILL.md com seção "Mitigação de Riscos"

MÊS 3:
  agente-cronograma success rate: 79.3% → 85.1% (+5.8%)
  
  Benchmark: Qual é o "bom"?
    • Opus-only agents: 95%+ (claims: 95.2%)
    • Sonnet-primary: 85-92% (saneamento: 87.2%)
    • Haiku-primary: 70-80% (maestro routing: ~75%)
  
  Cronograma está no padrão esperado ✓

ANO 1:
  Ranking de agentes por success:
    1. Manta 01 (claims): 95.2% ← Sempre Opus, problema bem-definido
    2. Manta 05 (orçamento): 91.5% ← Dados públicos (SICRO)
    3. Manta 06 (modelagem): 89.7% ← Estruturado
    4. Agente-saneamento: 87.2% ← Normas bem-documentadas
    5. ... ↓
    10. Manta 07 (cronograma): 85.1% ← Mais ambiguidade
    11. Agente-energia: 82.4% ← Mercado volátil
    12. Agente-portos: 79.8% ← Menos histórico
  
  Insight: Sucesso correlaciona com:
    • Dados estruturados? (SICRO > volátil)
    • Ambiguidade baixa? (claims > cronograma)
    • RAG-rich? (saneamento bem-documentado)
    • Caso uso claro? (orçamento < modelagem)
```

---

## 3. Ciclo de Aprendizado (Automation)

```
AUTOMÁTICO (Semanal):
┌────────────────────────────────────────────────────────┐
│ 1. Coletar feedback (execution_log + user feedback)   │
│ 2. Agrupar por (agent, metal, problem_type)           │
│ 3. Calcular estatísticas (success rate, avg quality)  │
│ 4. Identificar padrões (outliers, trends)             │
│ 5. Gerar recomendações (update heuristics, RAG, etc)  │
│ 6. Notificar MN (weekly digest de melhoras)           │
└────────────────────────────────────────────────────────┘

SEMANAL (Dashboard Maestro):
  Week 1:
    ├─ agente-orcamento: 91.5% success (✓ stable)
    ├─ agente-cronograma: 85.1% success (↑ +5.8% this month)
    ├─ agente-energia: 82.4% success (↓ -2.3% — investigate)
    ├─ Top error category: "missing detail" (40% de falhas)
    ├─ Recommended action: "Add 'complexity scoring' to intake"
    └─ New docs added: 8 (AySA case study, ERAS update, etc)

TRIMESTRAL (Strategy Review):
  Q3 2026:
    ├─ Documentos RAG: 500 → 575 (+15%)
    ├─ SKILL.md versões: v5.0 → v1.2 em média (+0.2/mês)
    ├─ MSE accuracy: 75% → 92% (+17%)
    ├─ Agent success rate (média): 82% → 87% (+5%)
    ├─ Custo de IA: Reduzido 35% (downgrading inteligente)
    ├─ Produtividade: +2.3x consultor (vs baseline)
    └─ Próximo foco: "Expandir RAG para 1.000 docs, ML no MSE"

ANUAL (Board Review):
  2026 vs 2025 (baseline manual):
    ├─ Conhecimento: 500 docs → 1.000 docs (2x)
    ├─ Velocidade: 60 análises/ano → 200/ano (+3.3x)
    ├─ Qualidade: 82% baseline → 87% atual (+5%)
    ├─ Custos: $21.6K/ano → $13.8K/ano (-36%)
    ├─ Compliance: 0% auditoria → 100% rastreabilidade
    └─ Team: 5 consultores → 15 efetivos (3x menos headcount/análise)
```

---

## 4. Evolução de Conhecimento — Exemplo Concreto

### Case: Agente-Saneamento (S8) Evolução 6 Meses

```
MÊS 0 (Maio 2026 — Go-live):
├─ SKILL.md: Versão 5.0 (inicial)
│  ├─ 10 seções (intake, execução, handoffs, refs)
│  ├─ Padrões: genéricos (NBR 12211, ETA/ETE básico)
│  └─ RAG: san:br: (100 docs), san:ar: (50 docs)
├─ Success rate: 82%
├─ Avg cost: $2.15
└─ Avg quality: 83/100

MÊS 1 (Junho 2026):
├─ Feedback recebido:
│  ├─ 50 queries processadas
│  ├─ Usuários mencionam: "Profundidade adução em SP é diferente"
│  ├─ Usuários mencionam: "Pré-moldados não estão no orçamento"
│  └─ Rating médio: 3.2/5
├─ Ações executadas:
│  ├─ Insert: Legislação São Paulo (5 novos docs em RAG)
│  ├─ Insert: Componentes pré-moldados (10 novos docs)
│  ├─ Update: SKILL.md § Profundidade Mínima (novo padrão SP)
│  └─ Update: SKILL.md § Orçamento (nova seção Pré-moldados)
├─ Resultado:
│  ├─ RAG: 150 docs → 165 docs
│  ├─ SKILL.md: v5.0 → v1.1 (5 mudanças)
│  ├─ Success rate: 82% → 84% (+2%)
│  └─ Avg quality: 83/100 → 85/100 (+2)

MÊS 2 (Julho 2026):
├─ Feedback recebido:
│  ├─ 100 queries processadas (crescimento 2x)
│  ├─ Padrão detectado: "Argentina vs Brasil legalmente diferentes"
│  ├─ Padrão detectado: "ETA pequenas (<10 L/s) são muito diferentes"
│  └─ Rating médio: 3.4/5 (melhorando!)
├─ Ações executadas:
│  ├─ Insert: Legislação Argentina ERAS (30 novos docs em san:ar:)
│  ├─ Insert: Especificações ETA pequenas (8 novos docs)
│  ├─ Update: MSE heurística (detectar "Argentina" → consultar san:ar: primeiro)
│  ├─ Update: SKILL.md § Brasil vs Argentina (nova tabela comparativa)
│  └─ Update: SKILL.md § ETA Pequenas (novo subtipo)
├─ Resultado:
│  ├─ RAG: 165 docs → 203 docs (+23%)
│  ├─ SKILL.md: v1.1 → v1.2 (8 mudanças)
│  ├─ Success rate: 84% → 87% (+3%)
│  └─ Avg quality: 85/100 → 88/100 (+3)

MÊS 3 (Agosto 2026):
├─ Feedback recebido:
│  ├─ 150 queries processadas (crescimento 1.5x)
│  ├─ Padrão detectado: "Reúso de água começou a aparecer (novo)"
│  ├─ Padrão detectado: "Drenagem urbana tem complexidade própria"
│  └─ Rating médio: 3.6/5 (continuando melhorar)
├─ Ações executadas:
│  ├─ Insert: Normas de reúso de água (12 novos docs)
│  ├─ Insert: Drenagem urbana especial (15 novos docs)
│  ├─ Update: SKILL.md § Reúso (nova seção completa)
│  ├─ Update: SKILL.md § Drenagem Urbana (nova seção)
│  ├─ Update: MSE (detectar "reúso" ou "drenagem" → avaliar escalação)
│  └─ Handoff: Novo → Se "drenagem urbana" + "mudança de zoneamento" → Energia
├─ Resultado:
│  ├─ RAG: 203 docs → 240 docs (+18%)
│  ├─ SKILL.md: v1.2 → v1.3 (12 mudanças)
│  ├─ Success rate: 87% → 88.5% (+1.5%)
│  └─ Avg quality: 88/100 → 89/100 (+1)

MÊS 4-6 (Setembro-Outubro 2026):
├─ Feedback contínuo:
│  ├─ Convergência: padrões estão se repetindo (menos novos)
│  ├─ Taxa de melhora diminui (plateau esperado)
│  └─ Rating médio: 3.7/5 (estável)
├─ Manutenção/Refinamento:
│  ├─ Adicionar detalhes nos padrões já existentes
│  ├─ Otimizar handoffs (que funcionam bem, qual frequência)
│  ├─ Refinar prompts do agent (output mais estruturado)
│  └─ Expandir RAG com variações (casos similares)
├─ Resultado:
│  ├─ RAG: 240 docs → 300 docs (consolidação)
│  ├─ SKILL.md: v1.3 → v1.5 (refinamentos)
│  ├─ Success rate: 88.5% → 89.5% (+1%)
│  └─ Avg quality: 89/100 → 90/100 (+1)

6 MESES SUMMARY:
├─ Documentos RAG: 150 → 300 (+100%, 2x)
├─ SKILL.md versão: v5.0 → v1.5 (+evolução contínua)
├─ Success rate: 82% → 89.5% (+7.5%)
├─ Avg quality: 83 → 90 (+7 points)
├─ Handoffs adicionados: 0 → 3 novas conexões
├─ Padrões identificados: 4 novos (SP, pré-moldados, Argentina, reúso, drenagem)
└─ Pronto para: "Expandir para 3 novos segmentos (mesmos padrões aplicam)"
```

---

## 5. Métricas de Evolução — Dashboard de Aprendizado

```
DASHBOARD — Real-time Learning Metrics
═══════════════════════════════════════════════════════════

📊 CONHECIMENTO (RAG)
  ├─ Documentos no RAG: 575 / 1.000 (57%)
  │   └─ Crescimento: +15 docs/mês (trend ↑)
  ├─ Cobertura por segmento:
  │   ├─ Saneamento (san:): 240 docs ✓ (objetivo 300)
  │   ├─ Energia (ene:): 180 docs ✓ (objetivo 300)
  │   ├─ Rodovias (rod:): 155 docs (objetivo 300)
  │   ├─ Portos (por:): 100 docs ↓ (objetivo 200) — IMPROVE
  │   └─ ... (9 segmentos)
  └─ "Hotspots" (docs com mais acesso):
      ├─ SICRO composições: 45x/semana
      ├─ NBR 12211: 38x/semana
      ├─ Padrão Manta: 32x/semana
      └─ Legislação regional: 28x/semana

🧠 HEURÍSTICAS (MSE)
  ├─ MSE Accuracy: 92% (objetivo 95%)
  │   └─ Trend: +1%/mês (a caminho)
  ├─ Escalação Automática:
  │   ├─ Haiku → Sonnet: 5% das queries (economia!)
  │   ├─ Sonnet → Opus: 10% das queries
  │   └─ Apex: Sonnet solução final: 85% (no escalation needed)
  └─ Feature importance (o que mais impacta decisão):
      ├─ Input tokens: 30%
      ├─ Domain keywords: 25%
      ├─ Agent success history: 20%
      ├─ Complexity score: 15%
      └─ User feedback rating: 10%

📈 AGENTES (Success Rates)
  ├─ Todos agentes (média): 87% (objetivo 90%)
  │   └─ Best: Manta 01 (claims): 95.2% ✓
  │   └─ Worst: agente-portos: 79.8% (IMPROVE)
  ├─ Variação por tier:
  │   ├─ Haiku queries: 80% success
  │   ├─ Sonnet queries: 88% success
  │   └─ Opus queries: 94% success
  └─ Trend (6 meses):
      └─ Baseline: 82% → Atual: 87% (+5%)

💰 CUSTO (Efficiency)
  ├─ Custo médio por query: $0.48 (target: $0.40)
  │   └─ Trend: -$0.01/mês (downgrading inteligente!)
  ├─ Distribuição por tier:
  │   ├─ Haiku: 20% das queries, 3% do custo
  │   ├─ Sonnet: 70% das queries, 60% do custo
  │   └─ Opus: 10% das queries, 37% do custo
  └─ Economia vs "sempre Sonnet":
      └─ Baseline (always Sonnet): $0.73/query
      └─ Atual (smart tiering): $0.48/query
      └─ Economia: $0.25/query (34% cheaper)

⚡ EXECUÇÃO (Performance)
  ├─ Latência p99: 45 segundos (objetivo < 60s) ✓
  │   └─ Trend: +500ms/mês (OK — mais dados no RAG)
  ├─ Taxa de escalação auto: 15% (objetivo < 20%) ✓
  │   └─ Quando escalação ocorre, sucesso em 96% ✓
  └─ Retrabalho: 8% (objetivo < 5%)
      └─ Padrão: quando "missing detail" — melhorar intake

🎯 FEEDBACK
  ├─ Rating médio: 3.6/5 (objetivo 4.0/5)
  │   └─ Trend: +0.3/5 por mês (perto do objetivo!)
  ├─ Engagement: 73% de users deixam feedback
  │   └─ Trend: +3%/mês (mais engajamento)
  └─ NPS (Net Promoter Score): 52 (objetivo 70)
      └─ Trend: +5 pontos/mês (melhorando)
```

---

## 6. Ciclos de Melhoria — Roadmap de Aprendizado

```
Q3 2026 (Ago-Out): Consolidação
  ├─ Objetivo: Atingir 87% success rate, 92% MSE accuracy
  ├─ Foco: Refinamento de padrões iniciais
  └─ Deliverable: SKILL.md v1.5 (consolidado), RAG 300 docs

Q4 2026 (Nov-Dez): Expansão
  ├─ Objetivo: Adicionar 2-3 novos segmentos menores
  ├─ Foco: Replicação de padrões (reúso de conhecimento)
  └─ Deliverable: agente-xxx v5.0 (novos segmentos)

Q1 2027 (Jan-Mar): ML Integration
  ├─ Objetivo: MSE com small ML model (NN leve)
  ├─ Foco: Predição com base em histórico
  └─ Deliverable: MSE v2.0 (accuracy 94%+)

Q2 2027 (Abr-Jun): Autonomy
  ├─ Objetivo: Maestro "auto-updates" de feedback
  ├─ Foco: Sem intervenção manual (apenas review MN)
  └─ Deliverable: Fully autonomous learning loop

ANO 2 (2027+): Mastery
  ├─ Objetivo: 95%+ success, 1.000+ doc RAG
  ├─ Foco: Cobertura completa (todos segmentos, fases)
  └─ Deliverable: "Manta Maestro é tão especialista quanto senior consultant"
```

---

## 7. Como Usuários Veem a Evolução

```
USUÁRIO 1 (Junior, Mês 1):
"Maestro me ajudou a fazer orçamento em 15 min. Tinha dúvida
sobre profundidade de adução em SP, mas Maestro citou a norma."
Rating: ⭐⭐⭐ (3/5 — faltou mais contexto)

USUÁRIO 1 (Junior, Mês 3):
"Maestro agora oferece 'orçamento simplificado vs detalhado'.
Escolho o tipo baseado no cliente. E a seção de 'Pré-moldados'
é bem útil — não estava antes!"
Rating: ⭐⭐⭐⭐ (4/5 — muito melhor)

USUÁRIO 1 (Junior, Mês 6):
"Trabalho sozinho em projetos que antes precisava de senior.
Maestro me ensina padrões, valida meu trabalho antes de entregar.
Crescimento profissional garantido!"
Rating: ⭐⭐⭐⭐⭐ (5/5 — transformou meu trabalho)

───────────────────────────────────

USUÁRIO 2 (Senior, Mês 1):
"Maestro é bom, mas faltam nuances. Algumas decisões precisam
de expert humano. Vejo como ferramenta de 'first-pass', não solução."
Rating: ⭐⭐⭐⭐ (4/5 — útil para triagem)

USUÁRIO 2 (Senior, Mês 3):
"Maestro começou a capturar algumas nuances que eu fazia
intuitivamente. Vejo que está aprendendo com meu feedback.
Confiança aumentou."
Rating: ⭐⭐⭐⭐ (4/5 — parceiro, não apenas ferramenta)

USUÁRIO 2 (Senior, Mês 6):
"Maestro agora traz segunda opinião que eu respeito. Em 80%
dos casos concordo. Quando discordo, explico e ele aprende.
É como ter 2 experts ao invés de 1."
Rating: ⭐⭐⭐⭐⭐ (5/5 — amplificação de capacidade)
```

---

## Conclusão: O Maestro Nunca Para de Aprender

```
DIA 1 (Go-live):
  "Maestro tem o conhecimento básico de Manta Associados"

MÊS 3:
  "Maestro refinou padrões, adicionou nuances, melhorou heurísticas"

MÊS 6:
  "Maestro é 2x melhor: mais rápido, mais preciso, mais confiável"

ANO 1:
  "Maestro é agora parceiro estratégico, não ferramenta"

ANO 2+:
  "Maestro é senior consultant (conhecimento consolidado)"
```

**Modelo**: Feedback → Melhoria → Novo padrão → RAG expande → SKILL.md evolui → MSE aprende → próximo feedback (ciclo contínuo)

**Resultado**: Sistema que melhora semana a semana, nunca fica obsoleto, aprende com cada consulta.
