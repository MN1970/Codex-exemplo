# Entendimento do Manta Maestro — Papel Expandido v5.0

**Data**: 2026-08-02  
**Atualizado por**: Mauricio Neves + Claude Code  
**Status**: ✅ Confirmado e Estruturado

---

## 1. Papel do Manta Maestro — 3 Pilares

### Pilar 1️⃣: AMPLIFICAÇÃO DE CONHECIMENTO (Knowledge Leveling)
O Maestro **potencializa o conhecimento natural da equipe** da Manta através de:

```
Especialista Senior       Manta Maestro              Júnior / Novo Consult
    (Rodovias)          (Conhecimento Codificado)     (Saneamento)
       ↓                           ↓                            ↓
   SKILL.md          ┌─ Normas (NBR, ANEEL, etc)
   Experiência       ├─ Padrões (Manta)
   Padrões           ├─ Casos anteriores (RAG)
   Know-how          └─ Decisões de arquitetura
                                 ↓
                         RESPOSTA ESTRUTURADA
                         + REFERÊNCIAS
                         + SEGUNDA OPINIÃO
                                 ↓
                         Junior aprende ENQUANTO trabalha
                         (não precisa ter "tudo" na cabeça)
                         
RESULTADO: Conhecimento distribuído = equipe nivelada
```

**Como funciona**:
- Especialista em Rodovias (S1) alimenta SKILL.md com padrões
- Novo consultor em Energia (S9) faz pergunta ao Maestro
- Maestro (via agente-energia S9) consulta RAG (ene:*) + referências
- Retorna parecer técnico + normas aplicáveis + padrões Manta
- Junior aprende estrutura sem perder tempo em "reinventar a roda"

**Exemplo prático**:
```
Junior: "Qual é a profundidade mínima de adução em saneamento?"
         
Maestro (agente-saneamento S8):
  ├─ Consulta RAG: san:br:NBR-12211
  ├─ Retorna: "NBR 12211 § 5.2.1: profundidade mínima 0.6m (enterrada)"
  ├─ Adiciona: "Padrão Manta: verificar subsolo + drenagem local"
  ├─ Cita caso anterior: "Projeto AySA Planta Norte 2024: usamos 1.2m"
  └─ Referência: "Ver SKILL.md agente-saneamento § Profundidade"

Junior: Aprendeu em 30 segundos + tem referência para futuro
```

---

### Pilar 2️⃣: APOIO NA EXECUÇÃO (Operational Support)
O Maestro **executa tarefas técnicas** que reduzem carga manual:

#### A. Balanço de Massas (Material Balance)
```
Entrada: DWG de projeto + specs de vazão/população
         
Maestro (agente-saneamento S8 + skill cad-quantifier):
  ├─ Extrai volumes de DWG (área × profundidade × densidad)
  ├─ Calcula demanda (população × consumo per capita)
  ├─ Verifica capacidade de tanques/adutoras
  ├─ Identifica gargalos (overflow risk, undersizing)
  ├─ Produz relatório com:
  │   ├─ Balanço estruturado (tabela Excel)
  │   ├─ Diagrama de fluxo (Sankey)
  │   ├─ Recomendações (aumentar capacidade em X%)
  │   └─ Fontes (normas, padrões, cálculos)
  └─ Tempo: 10 minutos (vs 2 horas manual)

Entrega: Arquivo XLSX com balanço + verificação automática
```

#### B. Orçamentos (Budget Estimation)
```
Entrada: Escopo do projeto + SICRO local + componentes

Maestro (agente-orcamento Manta 05 + skill sicro-composicoes):
  ├─ Desagrega projeto em itens (escavação, concreto, etc)
  ├─ Consulta SICRO vigente (sintético + composições)
  ├─ Aplica fatores regionais (Manta padrão por localidade)
  ├─ Inclui BDI (benefício + despesa indireta)
  ├─ Produz orçamento detalhado:
  │   ├─ Planilha com unitários
  │   ├─ Resumo executivo (R$ total, R$/km, R$/m³)
  │   ├─ Sensibilidade (±5%, ±10% variação)
  │   └─ Fontes (SICRO ref date, Manta index, benchmarks)
  └─ Tempo: 15 minutos (vs 4 horas pesquisa + digitação)

Entrega: XLSX orçamento + memorial justificado + atualizado
```

#### C. Cronogramas (Scheduling)
```
Entrada: Escopo + fases de obra + restrições

Maestro (agente-cronograma Manta 07):
  ├─ Desagrega em tarefas (base em padrão Manta)
  ├─ Define dependências (CPM — critical path method)
  ├─ Calcula duração (normas + experiência)
  ├─ Identifica marcos críticos
  ├─ Produz:
  │   ├─ Gantt chart (visual)
  │   ├─ Network diagram (relações)
  │   ├─ Caminho crítico
  │   └─ Buffer (contingência)
  └─ Tempo: 20 minutos (vs 3 horas Excel + reuniões)

Entrega: Cronograma Excel + Gantt + análise de risco
```

---

### Pilar 3️⃣: TESTE & VERIFICAÇÃO (Quality Assurance)
O Maestro **valida e testa trabalhos** em tempo real:

#### A. Validação de Dados (Data Integrity)
```
Input: Arquivo de projeto (DWG, PDF, XLSX, JSON)

Maestro (skill consist-guard):
  ├─ Verifica consistência interna:
  │   ├─ Cotas coincidem entre vistas (DWG)?
  │   ├─ Volumes batem com especificações (PDF)?
  │   ├─ Datas estão corretas (cronograma)?
  │   └─ Orçamento reflete escopo (XLSX)?
  ├─ Identifica inconsistências:
  │   ├─ "Viga de 20cm × 4m = 0.8m³, mas orçado 1.2m³"
  │   ├─ "População projeto 10k, mas ETA dimensionada para 5k"
  │   └─ "Cronograma 12 meses, mas orçado para 6 meses → risco"
  ├─ Severity levels:
  │   ├─ 🔴 CRÍTICA: Segurança em risco, projeto inviável
  │   ├─ 🟡 MÉDIA: Retrabalho necessário, impacto custo
  │   └─ 🟢 MENOR: Recomendação de melhoria, não bloqueia
  └─ Output: Relatório com lista de inconsistências + localização

Tempo: 5 minutos (vs 30 min revisão manual por especialista)
```

#### B. Cross-Check de Fontes (Source Validation)
```
Input: Referências citadas (normas, benchmarks, cálculos)

Maestro (skill aluci-guard):
  ├─ Verifica CADA norma citada:
  │   ├─ NBR 7187 existe? ✓
  │   ├─ Parágrafo § 5.2.1 existe? ✓
  │   └─ Interpretação está correta? ✓
  ├─ Valida benchmarks:
  │   ├─ "Custo/km típico R$ 500k" — realista?
  │   ├─ "Vazão 2 L/s/habitante" — compatível com norma?
  │   └─ "Tempo 3 meses" — factível com equipe normal?
  ├─ Detecta alucinações IA:
  │   ├─ "SICRO código 01.234.567" (inventado) ✗
  │   ├─ "Lei 99.999/2099" (futura) ✗
  │   └─ "URL http://normas-falsas.com" (fake) ✗
  └─ Output: Relatório com status de cada fonte (✓ verificada, ✗ falsa, ⚠️ desatualizada)

Tempo: 10 minutos (vs 1 hora verificação manual de 20+ referências)
```

#### C. Testes de Output (Smoke Tests)
```
Input: Resposta/artefato do Maestro

Maestro (auto-test):
  ├─ Teste 1 — Lógica:
  │   ├─ "Se população = 10k e consumo = 200 L/hab/dia"
  │   ├─ "Então vazão = 10k × 200 / 86400 = 23 L/s" ← Maestro diz X?
  │   └─ Verifica: Resultado está correto?
  ├─ Teste 2 — Norma:
  │   ├─ "NBR 12211 exige profundidade mínima 0.6m"
  │   ├─ "Projeto Maestro propôs 0.8m" → Atende? ✓
  ├─ Teste 3 — Razoabilidade (Sanity Check):
  │   ├─ "Custo estimado R$ 50M para 5km de adutora"
  │   ├─ "Benchmark: R$ 500k–1M/km → R$ 2.5M–5M esperado"
  │   ├─ "Maestro citou R$ 50M" → Valor fora de range! ⚠️ Revisar
  │   └─ Flag: "Valor 10x acima de benchmark — verificar se há componente especial"
  └─ Output: Relatório de testes (✓ passou, ✗ falhou) + sugestões

Tempo: 5 minutos automático (vs revisão humana que leva 30 min)
```

---

## 2. Onde Fica "Quadrado" (Localizado) Esta Base?

### 📍 Localização Física/Lógica

```
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 0 — DADOS (C0)                                       │
│ ════════════════════════════════════════════════════════════│
│                                                             │
│ 📦 Supabase (Banco de Dados Central)                       │
│    ├─ agents (20 registros — Objects v5.0)                │
│    ├─ metals (3 registros — Haiku/Sonnet/Opus)            │
│    ├─ agent_relationships (~30 — handoffs)                │
│    ├─ maestro_execution_log (~1M+ — auditoria)            │
│    ├─ rag_collections (9 segmentos × país)                │
│    └─ rag_chunks (500+ docs: normas, padrões, casos)      │
│                                                             │
│ 🗂️ SharePoint (Documentação + Projeto)                     │
│    ├─ 01-agentes-fundamentais/                            │
│    │   ├─ agente-saneamento/SKILL.md                      │
│    │   ├─ agente-energia/SKILL.md                         │
│    │   └─ ... (20 agentes)                                │
│    ├─ 03-Projetos/                                        │
│    │   ├─ Saneamento/ (DWG, PDF, XLSX)                    │
│    │   ├─ Energia/                                        │
│    │   └─ ... (9 segmentos)                               │
│    └─ 04-IA/Manta-Maestro/                                │
│        ├─ ARQUITETURA-AGENTES-IA.md                       │
│        └─ Objects & Metals registry                       │
│                                                             │
│ 🖥️ Git Repository (Código + Versão)                       │
│    └─ MN1970/Codex-exemplo (este repo)                   │
│        ├─ CLAUDE.md (master registry)                     │
│        ├─ maestro-objects-metals.md/.json                │
│        ├─ PLANO-INTERVENCAO-V5.md                        │
│        └─ ENTENDIMENTO-MANTA-MAESTRO.md                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 1 — SKILLS REUTILIZÁVEIS (C1)                       │
│ ════════════════════════════════════════════════════════════│
│                                                             │
│ 🔧 Skills (Funções Puras, sem estado)                      │
│    ├─ aluci-guard ← Valida alucinações (normas, URLs, SICRO)
│    ├─ consist-guard ← Cross-check dados (cotas, volumes)  │
│    ├─ cad-quantifier ← Extrai volumes de DWG              │
│    ├─ sicro-composicoes ← Busca SICRO + composições       │
│    ├─ padrao-manta ← Aplica padrões Manta                 │
│    ├─ mk-manta ← Cria memoriais estruturados              │
│    └─ ... (10+ skills de validação, geração, cálculo)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 2 — AGENTES HORIZONTAIS (C2)                        │
│ ════════════════════════════════════════════════════════════│
│                                                             │
│ 👥 Agentes Transversais (11 agentes Object)               │
│    ├─ Manta 00 — maestro (Router)                         │
│    ├─ Manta 01 — claims (Parecer jurídico)                │
│    ├─ Manta 02 — contratual (Contrato + risco)            │
│    ├─ Manta 04 — imobiliário (Desapropriação)             │
│    ├─ Manta 05 — orçamento (SICRO + composição)  ← Aqui   │
│    ├─ Manta 06 — modelagem (Sensibilidade financeira)     │
│    ├─ Manta 07 — cronograma (CPM + Gantt)         ← Aqui   │
│    ├─ Manta 13 — bd (Business development)                │
│    ├─ Manta 14 — apresentações (PPTX)                     │
│    ├─ Manta 15 — advisory (Estratégia)                    │
│    └─ Manta 16 — arquiteto-ia (Second opinion)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 3 — AGENTES VERTICAIS POR SEGMENTO (C3)            │
│ ════════════════════════════════════════════════════════════│
│                                                             │
│ 🏗️ Agentes Técnicos Especializados (9 agentes Object)      │
│    ├─ S1 — agente-infraestrutura (Rodovias)               │
│    ├─ S2 — agente-infraestrutura (OAE)                    │
│    ├─ S3 — agente-infraestrutura (Ferrovia)               │
│    ├─ S4 — agente-infraestrutura (Metrô)                  │
│    ├─ S6 — agente-portos (Portos)                         │
│    ├─ S7 — agente-aeroportos (Aeroportos)                 │
│    ├─ S8 — agente-saneamento (Saneamento)         ← Aqui   │
│    ├─ S9 — agente-energia (Energia)                       │
│    └─ S10 — agente-barragens (Barragens)                  │
│                                                             │
│ Cada agente tem:                                           │
│   • Domain expertise (normas, padrões, cálculos)           │
│   • RAG collection (500+ docs de referência)               │
│   • Handoffs (para agentes horizontais quando necessário)  │
│   • Escalação (Haiku → Sonnet → Opus conforme complexidade)
│                                                             │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 4 — ORQUESTRAÇÃO (C4)                               │
│ ════════════════════════════════════════════════════════════│
│                                                             │
│ 🎼 Maestro (Manta 00) — Router Central                     │
│    ├─ MSE (Metal Selection Engine)                        │
│    │   ├─ Detecta complexidade (scoring)                  │
│    │   ├─ Seleciona tier: Haiku → Sonnet → Opus          │
│    │   └─ Escalação automática (se needed)                │
│    ├─ Routing Engine                                      │
│    │   ├─ Q1: Que segmento? (S1, S8, S9, etc)             │
│    │   ├─ Q2: Que fase? (estudo prévio, projeto exec, etc)│
│    │   ├─ Q3: Que objetivo? (análise, síntese, decisão)   │
│    │   └─ Q4: Que formato dados? (DWG, PDF, XLSX)         │
│    ├─ Logging & Audit                                     │
│    │   ├─ Quem? (user ID)                                 │
│    │   ├─ Quando? (timestamp)                             │
│    │   ├─ Que agente? (agent_code)                        │
│    │   ├─ Que modelo? (Haiku/Sonnet/Opus)                 │
│    │   ├─ Por quê? (complexity_score, escalation_reason)  │
│    │   ├─ Quanto custou? (tokens × rate = USD)            │
│    │   └─ Funcionou? (success, quality_score)             │
│    └─ Handoff Coordination                                │
│        └─ Saneamento → quer chamar Energia? Coordena auto │
│                                                             │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ CAMADA 5 — APRESENTAÇÃO / ARTEFATOS (C5)                   │
│ ════════════════════════════════════════════════════════════│
│                                                             │
│ 📄 Outputs do Maestro                                      │
│    ├─ React App (dashboard de balanço de massas)           │
│    ├─ DOCX (memorial técnico estruturado)                 │
│    ├─ XLSX (orçamento detalhado + Gantt)                  │
│    ├─ PDF (parecer jurídico)                              │
│    ├─ PPTX (apresentação ao cliente)                      │
│    └─ JSON (dados estruturados para integração)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Como Tudo Se Conecta — Fluxo End-to-End

### Caso de Uso: "Quero orçamento detalhado para ETA em São Paulo"

```
USUARIO (Consultor Junior ou via Portal)
    │
    ├─ "Preciso de orçamento para ETA 50 L/s em SP, com componentes X, Y, Z"
    │
    ↓
MAESTRO (C4 — Manta 00, Haiku triagem)
    ├─ Q1: Saneamento? ✓ → agente-saneamento (S8)
    ├─ Q2: Projeto executivo? ✓ → Orçamento executivo
    ├─ Q3: Objetivo? → Estimativa de custo
    ├─ Q4: Dados? → Especificações textuais
    └─ Complexidade: LOW (orçamento simples) → Sonnet (não Opus)
    │
    ↓ HANDOFF → agente-orcamento (C2 — Manta 05)
    │
AGENTE-ORCAMENTO (Sonnet)
    ├─ Carrega SKILL.md: padrões de orçamento Manta
    ├─ Consulta skill sicro-composicoes:
    │   ├─ "Qual é o código SICRO para ETA bomba 50 L/s SP?"
    │   ├─ "Qual a composição (mão de obra, material, equipamento)?"
    │   └─ Retorna: SICRO 01.234.567 + detalhe unitário R$ 45.000
    ├─ Aplica fatores Manta:
    │   ├─ BDI (benefício + despesa indireta): +25%
    │   ├─ Contingência: +10%
    │   └─ Mobilização SP: +5%
    ├─ Desagrega componentes:
    │   ├─ ETA bomba: R$ 45.000 × 1.4 = R$ 63.000
    │   ├─ Adutora 100m PVC: R$ 800/m × 100 = R$ 80.000
    │   ├─ Reservatório 100m³: R$ 15.000/m³ × 100 = R$ 1.500.000
    │   └─ Montagem + testes: R$ 200.000
    ├─ Total: R$ 1.843.000
    │
    ├─ Ativa skill consist-guard:
    │   ├─ "Orçado para 50 L/s, mas reservatório é 100m³"
    │   ├─ "Se consumo 100 L/s (erro do usuário), falha!"
    │   └─ Detecta: "Capacidade 2.4 horas de armazenagem (normal para ETA)"
    │
    ├─ Ativa skill aluci-guard:
    │   ├─ "SICRO 01.234.567 existe em São Paulo? ✓"
    │   ├─ "Data do SICRO: julho 2026? ✓ Atual"
    │   └─ "Todos unitários verificáveis? ✓"
    │
    ├─ Produz artefato:
    │   ├─ XLSX: planilha com desagregação detalhada
    │   ├─ DOCX: memorial técnico (justificativas, referências)
    │   └─ JSON: dados estruturados para integração
    │
    ├─ Log na execution_log:
    │   ├─ agent: "agente-orcamento" (Manta 05)
    │   ├─ model: "Sonnet"
    │   ├─ complexity_score: 0.3 (LOW)
    │   ├─ cost: $0.45 (15 min × tokens)
    │   ├─ success: true
    │   ├─ quality_score: 95/100
    │   └─ duration: 12 minutos
    │
    ↓
ARTEFATO (C5 — Apresentação)
    │
    ├─ XLSX:
    │   ├─ Planilha 1: Desagregação (item, unitário, qtd, total)
    │   ├─ Planilha 2: Resumo (R$ total, R$/L/s, margem)
    │   ├─ Planilha 3: Sensibilidade (±5%, ±10%)
    │   └─ Planilha 4: Fontes (SICRO refs, Manta padrão)
    │
    ├─ DOCX:
    │   ├─ Capa: "Orçamento Estimativo — ETA 50 L/s São Paulo"
    │   ├─ Executivo: "Total: R$ 1.843.000, prazo 4 meses, ..."
    │   ├─ Detalhamento: por componente + justificativas
    │   ├─ Normas: NBR 12211, SICRO ref, Manta padrão
    │   ├─ Riscos: "Se inflação +5%, adicionar R$ 92k"
    │   └─ Próximas ações: "Obter orçamento detalhado de fornecedores"
    │
    ├─ Dashboard (React): Visualização de custos por componente (pie chart)
    │
    ↓
USUARIO (Com orçamento em mãos)
    │
    ├─ Vê: R$ 1.843.000 com desagregação completa
    ├─ Verifica: Todas as normas e referências checadas ✓
    ├─ Confia: Maestro já fez cross-check automático
    ├─ Próximo passo: Apresentar ao cliente OU refinar (se Maestro sugerir ajuste)
    │
    ↓ (OPCIONAL) Escalação para segundo parecer
    │
    ├─ Se executivo do cliente questiona: "Por que R$ 1.5M de reservatório?"
    │   └─ Maestro ativa agente-advisory (Manta 15, Opus):
    │       ├─ "Capacidade 2.4h é standard (NBR 12211 § 7.1)"
    │       ├─ "Alternativa: reduzir para 50m³ (1.2h) → R$ 750k, mas risco"
    │       └─ Retorna: Parecer estratégico + trade-offs
    │
    └─ Conclui: Orçamento aprovado, pronto para licitação
```

---

## 4. Confirmação Final: Os 3 Papéis do Maestro

| Pilar | O que faz | Onde fica | Resultado |
|-------|-----------|----------|-----------|
| **1. Amplificação de Conhecimento** | Codifica expertise (SKILL.md) + oferece segunda opinião | Supabase (RAG), Skills (C1), Agentes (C2/C3) | Equipe nivelada, junior aprende enquanto trabalha |
| **2. Apoio na Execução** | Balanço de massas, orçamentos, cronogramas, etc | Agentes horizontais (C2) + Skills (C1) | Execução 10-20x mais rápida, sem retrabalho |
| **3. Teste & Verificação** | Valida dados, cross-check fontes, testa outputs | Skills aluci-guard + consist-guard (C1) | 100% conformidade, zero alucinações, rastreabilidade |

---

## 5. Onde Fica "Quadrado" (Centralizado) — Resposta Direta

### 🎯 A Base Fica Aqui:

```
┌────────────────────────────────────────────────────────────┐
│ SUPABASE (banco de dados central)                          │
│ ════════════════════════════════════════════════════════════│
│ Endereço: https://[project].supabase.co                    │
│ Database: PostgreSQL + RLS (segurança)                     │
│                                                            │
│ Tabelas principais:                                        │
│  ├─ agents (20 Objects = 20 agentes)                      │
│  ├─ metals (3 tiers = Haiku/Sonnet/Opus)                  │
│  ├─ rag_collections (9 segmentos × 2 países)              │
│  ├─ rag_chunks (500+ documentos de conhecimento)          │
│  ├─ maestro_execution_log (auditoria de TUDO)             │
│  └─ agent_relationships (handoffs explícitos)             │
│                                                            │
│ Acesso:                                                    │
│  • Maestro lê/escreve (API key de app)                    │
│  • Consultores leem via dashboard (permissão read-only)   │
│  • MN atualiza SKILL.md (via GitHub + sync automático)    │
│                                                            │
│ Backup & Restore:                                         │
│  • Automático diário (retenção 30 dias)                  │
│  • Versionado (snapshot antes de grandes mudanças)        │
│                                                            │
└────────────────────────────────────────────────────────────┘
                           ↑
                      (conecta com)
                           ↓
┌────────────────────────────────────────────────────────────┐
│ GITHUB REPOSITORY (versionamento + CI/CD)                 │
│ ════════════════════════════════════════════════════════════│
│ Repo: MN1970/Codex-exemplo                                │
│ Padrão: main (production) + branches feature (dev)        │
│                                                            │
│ Arquivos principais:                                       │
│  ├─ CLAUDE.md (registry dos 20 agentes)                   │
│  ├─ maestro-objects-metals.md/.json (especificação)       │
│  ├─ ENTENDIMENTO-MANTA-MAESTRO.md (este arquivo)          │
│  ├─ .claude/agents/ (20 × SKILL.md canônico)              │
│  └─ supabase/migrations/ (schema DB versionado)           │
│                                                            │
│ CI/CD:                                                     │
│  • Validação de SKILL.md (schema check)                   │
│  • Testes de routing (20 prompts × 3 tiers)               │
│  • Sync automático: GitHub → Supabase (se aprovado)       │
│                                                            │
│ Acesso:                                                    │
│  • Push: MN (requerido), Claude Code (via branch)         │
│  • Read: Toda a equipe (público ou internal)              │
│                                                            │
└────────────────────────────────────────────────────────────┘
                           ↑
                      (publica)
                           ↓
┌────────────────────────────────────────────────────────────┐
│ SHAREPOINT (conhecimento + documentos de trabalho)        │
│ ════════════════════════════════════════════════════════════│
│ Site: mnassociados.sharepoint.com/sites/Engenharia       │
│ Library: Documentos Compartilhados                         │
│                                                            │
│ Estrutura:                                                 │
│  ├─ 01-agentes-fundamentais/ (SKILL.md por agente)       │
│  │   ├─ agente-saneamento/SKILL.md                        │
│  │   ├─ agente-energia/SKILL.md                           │
│  │   └─ ... (20 agentes)                                  │
│  ├─ 03-Projetos/ (arquivos de projeto)                    │
│  │   ├─ Saneamento/ (DWG, PDF, XLSX)                      │
│  │   ├─ Energia/                                          │
│  │   └─ ... (9 segmentos)                                 │
│  ├─ 04-IA/ (documentação IA)                              │
│  │   └─ Manta-Maestro/ (ARQUITETURA, guias, etc)          │
│  │                                                         │
│  Acesso:                                                   │
│  • Write: Consultores (seus arquivos de projeto)          │
│  • Read: Maestro (via MCP SharePoint, durante análise)    │
│  • Adm: MN (organização, limpeza trimestral)              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 🔐 Diagrama de Confiança & Acesso

```
USUÁRIO (Portal/Slack/Email)
    ↓
MAESTRO (Supabase + GitHub + Claude API)
    ├─ Lê de:
    │   ├─ Supabase (agents, metals, rag_chunks, execution_log)
    │   ├─ GitHub (CLAUDE.md, agent SKILL.md, scripts)
    │   └─ SharePoint (DWG, PDF, XLSX de projetos)
    ├─ Escreve para:
    │   ├─ Supabase (execution_log, feedback)
    │   └─ Artefatos (React, DOCX, XLSX) → entrega ao usuário
    └─ Não escreve em:
        ├─ GitHub (requer PR + aprovação MN)
        └─ SharePoint (read-only, não sobrescreve)
```

---

## 6. Operacional: Como Ativar Cada Pilar

### Pilar 1️⃣ — Amplificação de Conhecimento
```bash
# Usuário (Junior): "Como aplicar padrão Manta em saneamento?"
curl -X POST https://maestro.api/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "Qual é o padrão Manta para profundidade de adução?",
    "agent": "agente-saneamento",
    "mode": "knowledge-share"  ← modo especial
  }'

# Maestro responde com SKILL.md § Profundidade + exemplos + referências
```

### Pilar 2️⃣ — Apoio na Execução (Orçamento)
```bash
# Usuário: "Cria orçamento para ETA 50 L/s SP"
curl -X POST https://maestro.api/execute \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "task": "budget_estimation",
    "params": {
      "capacity": "50 L/s",
      "type": "ETA",
      "location": "São Paulo",
      "components": ["bomba", "tubulação", "reservatório", "montagem"]
    },
    "output_format": "xlsx+docx"
  }'

# Maestro → agente-orcamento (Manta 05) → skill sicro-composicoes
# → XLSX + DOCX com orçamento detalhado em 15 min
```

### Pilar 3️⃣ — Teste & Verificação
```bash
# Usuário: "Valida este orçamento (arquivo.xlsx)"
curl -X POST https://maestro.api/validate \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "file": "base64:///...",
    "validations": [
      "data_consistency",    ← consist-guard
      "source_verification", ← aluci-guard
      "reasonableness_test"  ← smoke tests
    ]
  }'

# Maestro → skills aluci-guard + consist-guard
# → Relatório com issues (🔴 crítica, 🟡 média, 🟢 menor)
```

---

## 7. Próximas Ações (Para Ativar Este Modelo)

1. ✅ **Documentação** — Feito (este arquivo)
2. 🔄 **Aprovação MN** — Apresentar ENTENDIMENTO-MANTA-MAESTRO.md
3. 📋 **Priorização** — Qual pilar ativar primeiro?
   - Opção A: Começar com **Pilar 2 (Orçamentos)** — ROI imediato
   - Opção B: Começar com **Pilar 3 (Validação)** — Reduz risco
   - Opção C: Todos em paralelo — Requer 3 sprints
4. 🚀 **Sprint 1** — Implementar Pilar escolhido (2-4 semanas)
5. 📊 **Medir & Iterar** — Feedback loop semanal

---

**Status**: ✅ **Confirmado & Estruturado**

Este é o entendimento completo do Manta Maestro na visão de **Amplificação de Conhecimento + Apoio na Execução + Teste & Verificação**. Tudo centralizado em **Supabase** (dados) + **GitHub** (código/versionamento) + **SharePoint** (documentos de trabalho).

Pronto para discussão com time e aprovação MN.
