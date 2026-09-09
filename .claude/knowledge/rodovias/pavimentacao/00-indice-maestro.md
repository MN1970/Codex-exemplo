# 📚 Índice Maestro — Pavimentação de Rodovias

**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:pavimento:*`  
**Status**: 🔄 Consolidação em andamento  
**Data**: 2026-08-04  
**Branch**: `claude/agente-pavimentacao-topicos`

---

## 🎯 Objetivo

Aprofundar e expandir o conhecimento do agente-infraestrutura S1 em **pavimentação rodoviária**, cobrindo:
- ✅ Agregados (seleção, composição, origem regional, DNIT/ABNT)
- ✅ Ligantes asfálticos (CAP, modificados, viscoelasticidade)
- ✅ Misturas asfálticas (CBUQ, SMA, BINDER, bases, dosagem Marshall/Superpave)
- ✅ Dimensionamento de estrutura de pavimento (método AASHTO, método de custo de ciclo de vida)
- ✅ Patologias e reabilitação (trincamento, afundamento, remendos, fresagem)
- ✅ Pavimentos rígidos (concreto Portland, juntas, drenagem)
- ✅ Controle de qualidade em obra (ensaios de campo)
- ✅ Orçamentação SICRO 2026 (composições, quantitativos, custos)
- ✅ Casos reais (BR federal, SP estadual, projetos Manta)

---

## 📋 Estrutura de Conhecimento

### 1️⃣ Tópicos Planejados (Série Pavimentação)

| Tópico # | Título | Foco Principal | Status | Data |
|----------|--------|----------------|--------|------|
| **T1** | Fundamentos de Pavimentação | Conceitos, histórico, classificação | 📋 Planejado | — |
| **T2** | Agregados (ESTE ARQUIVO) | Seleção, composição, origem regional | ✅ **Concluído** | 2026-08-04 |
| **T3** | Ligantes Asfálticos | CAP, polímeros, ensaios PG, SUPERPAVE | 📋 Planejado | — |
| **T4** | Misturas Asfálticas | Dosagem Marshall/Superpave, CBUQ, SMA | 📋 Planejado | — |
| **T5** | Dimensionamento de Pavimento | AASHTO, método CBR, análise estrutural | 📋 Planejado | — |
| **T6** | Patologias e Reabilitação | Trincas, afundamentos, fresagem, recapeamento | 📋 Planejado | — |
| **T7** | Pavimentos Rígidos | Concreto Portland, fibras, juntas, drenagem | 📋 Planejado | — |
| **T8** | Controle de Qualidade em Obra | Ensaios densidade, umidade, Marshall de campo | 📋 Planejado | — |

---

## 📊 Cobertura por Tópico T2 (Agregados)

### Seções Principais

| Seção | Subtópicos | Cobertura |
|-------|-----------|-----------|
| **1. Conceitos Fundamentais** | Tipos, origem, classificação, mineralógica | 100% |
| **2. Propriedades Técnicas** | Granulometria, resistência (IRC, CPA), absorção | 100% |
| **3. Seleção Normativa** | DNIT ES 032, faixas granulométricas, tabelas | 100% |
| **4. Cálculos Práticos** | Dosagem de agregado, curva Fuller, SICRO | 100% |
| **5. Integração SICRO 2026** | Composições, custo agregados 1 km pavimento | 100% |
| **6. Tabelas Normativas** | DNIT ES 032, NBR 7809, NBR 11798 | 100% |
| **7. Casos Reais** | BR-116 (RJ), BR-163 (GO), BR-101 (SP) | 100% |
| **8. Referências** | Normativa, interna Manta, internacional | 100% |

---

## 📁 Arquivos deste Tópico

```
pavimentacao/
├── 00-indice-maestro.md        (este arquivo)
├── 01-fundamentos.md           (planejado)
├── 02-agregados.md             (✅ CRIADO 2026-08-04)
├── 03-ligantes-asfalticos.md   (planejado)
├── 04-misturas-asfalticas.md   (planejado)
├── 05-dimensionamento.md       (planejado)
├── 06-patologias-reabilitacao.md (planejado)
├── 07-pavimentos-rigidos.md    (planejado)
├── 08-controle-qualidade.md    (planejado)
└── README.md                   (planejado)
```

---

## 🔧 Integração com RAG (Supabase)

Estrutura planejada após consolidação:

```
Coleção: rodovias (prefixo: rod:)

Subprefixos Rod:pavimento:
├─ rod:pavimento:agregados     # Tópico 2 ✅
│  ├─ rod:pav:agg:tipos        # Classificação
│  ├─ rod:pav:agg:propriedades # IRC, CPA, absorção
│  ├─ rod:pav:agg:seleção      # DNIT, faixas
│  ├─ rod:pav:agg:origem       # Jazidas, regiões BR
│  ├─ rod:pav:agg:granulometria # Fuller, faixa A-F
│  ├─ rod:pav:agg:sicro        # Composições, custos
│  └─ rod:pav:agg:casos        # BR real

├─ rod:pavimento:ligantes      # Tópico 3
│  ├─ rod:pav:lig:cap          # CAP 50/70, 85/100, etc.
│  ├─ rod:pav:lig:modificados  # CAP + polímero
│  └─ rod:pav:lig:propriedades # Viscosidade, PG

├─ rod:pavimento:misturas      # Tópico 4
│  ├─ rod:pav:mix:cbuq         # Concreto betuminoso
│  ├─ rod:pav:mix:sma          # Stone mastic asphalt
│  ├─ rod:pav:mix:binder       # Camada intermediária
│  └─ rod:pav:mix:dosagem      # Marshall, Superpave

├─ rod:pavimento:dimensionamento # Tópico 5
│  ├─ rod:pav:dim:aashto       # Método AASHTO
│  ├─ rod:pav:dim:cbr          # Método CBR
│  └─ rod:pav:dim:estrutura    # Análise estrutural

├─ rod:pavimento:patologias    # Tópico 6
│  ├─ rod:pav:pat:trincas      # Mapa trincas, causas
│  ├─ rod:pav:pat:afundamentos # Deformação permanente
│  └─ rod:pav:pat:reabilitação # Fresagem, recapeamento

├─ rod:pavimento:rigidos       # Tópico 7
│  ├─ rod:pav:rig:concreto     # Concreto Portland
│  ├─ rod:pav:rig:juntas       # Junta, espaçamento
│  └─ rod:pav:rig:drenagem     # Drenagem base

├─ rod:pavimento:qualidade     # Tópico 8
│  ├─ rod:pav:qc:densidade     # Ensaios densidade
│  ├─ rod:pav:qc:granulometria # Curva granulométrica
│  └─ rod:pav:qc:marshall      # Teste de resistência

└─ rod:pavimento:sicro         # Orçamentação
   ├─ rod:pav:sicro:agregados  # Item 73600-73800
   ├─ rod:pav:sicro:ligantes   # Item 77000-77100
   ├─ rod:pav:sicro:composições # Cálculo custo 1 km
   └─ rod:pav:sicro:casos      # Estimativas reais
```

---

## 📝 Prompts de Teste (Validação)

Após consolidação de cada tópico, testar agente com:

### Série Agregados (Tópico 2)

#### Teste 1: Seleção de Agregado
```
"Estou projetando uma rodovia federal (Vd=100 km/h) em SP e tenho duas 
opções de jazida: Basalto (R$ 42/t, 5 km) e Granito (R$ 35/t, 50 km). 
Qual devo usar para CBUQ? Qual é o diferencial de custo?"
```

**Saída esperada**:
- Basalto recomendado (IRC 98%, CPA 62)
- Granito marginal (IRC 87%, CPA 48)
- Diferencial: +R$ 7/t mas reduz custo transporte por proximidade
- Resultado: Basalto economicamente melhor

#### Teste 2: Granulometria
```
"Tenho uma areia natural com 28% passando 0.59 mm. Preciso atingir 
faixa A do DNIT (17-20% em 0.59 mm). Como ajustar?"
```

**Saída esperada**:
- Reduzir 8% areia fina
- Compensar com pedrisco (9.5-4.75 mm)
- Calcular proporções da mistura

#### Teste 3: Orçamento
```
"Preciso de agregados para 15 km de pavimento (CBUQ 5 cm + Binder 10 cm + 
BGS 15 cm). Usando basalto a R$ 42/t, qual será o custo total?"
```

**Saída esperada**:
- Volume total: ~40 kt
- Custo: 40 × 42 = R$ 1.68 M (aprox.)

---

## 🚀 Próximos Passos (Roadmap)

### Fase 1: Tópico 2 (Agregados) — ATUAL
- [x] Estrutura de conhecimento definida
- [x] Arquivo 02-agregados.md criado e consolidado
- [ ] Revisão técnica interna (DNIT specialist)
- [ ] Testes de validação (3 testes acima)
- [ ] Feedback de campo (obra real)
- [ ] Integração RAG Supabase

### Fase 2: Tópicos 3-4 (Ligantes & Misturas)
- [ ] Planejamento conteúdo T3 (Ligantes)
- [ ] Planejamento conteúdo T4 (Misturas)
- [ ] Criação arquivos T3, T4
- [ ] Testes validação

### Fase 3: Tópicos 5-8 (Dimensionamento, Patologias, Rígidos, QC)
- [ ] Planejamento T5-T8
- [ ] Criação arquivos
- [ ] Testes integrados

### Fase 4: Consolidação & Deploy
- [ ] Integração RAG Supabase (todos os tópicos)
- [ ] Testes integrados agente-infraestrutura
- [ ] Review DNIT/NBR specialist
- [ ] Merge na branch main
- [ ] Deploy em produção

---

## 📞 Escalação & Responsabilidades

| Papel | Responsável | Escalação | Contato |
|-------|-------------|-----------|---------|
| PM Agente-infraestrutura | Maurício Neves | MN@manta.br | +55-11-xxxx |
| Especialista DNIT (Pavimentação) | [TBD] | technical-review | — |
| Tester (QA Rodovias) | [TBD] | qa-rodovias | — |
| Arquiteto IA (Manta 16) | [Manta 15-ARQ] | escalate:manta-arq | — |

---

## 📚 Referências Cruzadas

- **CLAUDE.md master**: Registro de todos os 20 agentes Manta
- **Índice Maestro Geometria** (irmão): `.claude/knowledge/rodovias/geometria/00-indice-maestro.md`
- **SICRO 2026**: Tabela oficial (seção agregados 73600-73800)
- **DNIT ES 032/2005**: Especificação CBUQ
- **NBR 7809, NBR 11798**: Ensaios de agregados

---

## 📊 Status Workflow

```
Iniciado: 2026-08-04
Tópico 2 (Agregados): ✅ CRIADO
Próximo: Tópico 3 (Ligantes) — início 2026-08-15

Timeline:
├─ T2 (Agregados): 2026-08-04 ✅
├─ T3 (Ligantes): 2026-08-15 (planejado)
├─ T4 (Misturas): 2026-08-29 (planejado)
├─ T5 (Dimensionamento): 2026-09-12 (planejado)
└─ Consolidação RAG: 2026-09-30 (planejado)
```

---

**Última atualização**: 2026-08-04  
**Próxima revisão**: 2026-08-11  
**Mantido por**: Agente-infraestrutura S1 + Manta 16 (Arquiteto IA)
