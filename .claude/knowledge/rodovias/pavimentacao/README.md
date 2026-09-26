# Pavimentação de Rodovias — Base de Conhecimento

**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:pavimento:*`  
**Última atualização**: 2026-08-04

---

## 📖 Bem-vindo

Esta pasta contém a base de conhecimento técnico consolidado sobre **pavimentação rodoviária**, organizada em **8 tópicos principais** que cobrem desde fundamentos até reabilitação de rodovias, sempre com foco em:

- ✅ **Normas brasileiras** (DNIT ES 032, NBR, ABNT)
- ✅ **Casos reais de projeto** (BR federais, rodovias SP, projetos Manta)
- ✅ **Integração SICRO 2026** (orçamentação, composições, custos)
- ✅ **Exemplos numéricos** com valores reais de obra
- ✅ **Propriedades e dimensionamento** com fórmulas e tabelas

---

## 📂 Estrutura de Tópicos

| # | Tópico | Arquivo | Status | Data |
|---|--------|---------|--------|------|
| **T1** | Fundamentos de Pavimentação | `01-fundamentos.md` | 📋 Planejado | — |
| **T2** | Agregados | `02-agregados.md` | ✅ Criado | 2026-08-04 |
| **T3** | Ligantes Asfálticos (CAP, Modificados) | `03-ligantes-asfalticos.md` | 📋 Planejado | — |
| **T4** | Misturas Asfálticas (CBUQ, SMA, Dosagem) | `04-misturas-asfalticas.md` | 📋 Planejado | — |
| **T5** | Dimensionamento de Estrutura de Pavimento | `05-dimensionamento.md` | 📋 Planejado | — |
| **T6** | Patologias e Reabilitação de Pavimentos | `06-patologias-reabilitacao.md` | 📋 Planejado | — |
| **T7** | Pavimentos Rígidos (Concreto Portland) | `07-pavimentos-rigidos.md` | 📋 Planejado | — |
| **T8** | Controle de Qualidade em Obra | `08-controle-qualidade.md` | 📋 Planejado | — |

---

## 🚀 Começando — Tópico 2: Agregados (T2)

**Arquivo Principal**: `02-agregados.md`

O tópico 2 cobre **seleção e especificação de agregados** para pavimentação rodoviária. Ideal para engenheiros que precisam:

- ✅ Selecionar agregados para projetos de pavimento
- ✅ Entender granulometria e conformidade com DNIT
- ✅ Calcular custos de agregados com SICRO 2026
- ✅ Analisar origem regional e disponibilidade de jazidas

### Sumário Rápido (T2)

1. **Conceitos Fundamentais** — Tipos de agregados, origem geológica, composição mineral
2. **Propriedades Técnicas** — Granulometria (Fuller), resistência (IRC/CPA), absorção de água
3. **Seleção Normativa** — DNIT ES 032/2005, faixas granulométricas A-F
4. **Cálculos Práticos** — Dosagem agregado, curva granulométrica, compatibilidade com betume
5. **SICRO 2026** — Composições, custo agregados por fração, cálculo 1 km pavimento completo
6. **Tabelas Normativas** — DNIT, NBR, limites técnicos
7. **Casos Reais** — BR-116 (RJ), BR-163 (GO), BR-101 (SP)

### Exemplo Rápido

**Pergunta**: "Qual agregado usar em uma BR com tráfego alto?"

**Resposta esperada** (baseada em T2):
- Basalto britado (IRC ≥ 98%, CPA ≥ 62, absorção < 1%)
- Aplicar faixa granulométrica DNIT Faixa A para CBUQ
- Custo aprox. R$ 42-50/t (tabela SICRO 2026)
- Para 22 km × 2 pistas: ~5,000 t agregados = R$ 210-250 k

---

## 🎯 Uso Prático

### Para Engenheiros de Projeto

1. Leia **T2 — seção 3** (Seleção e Especificação Normativa)
2. Consulte **seção 7** (Casos Reais) para situações similares
3. Use checklist (seção 9) para validar agregados em obra

### Para Gerentes de Obra

1. Leia **T2 — seção 5** (Integração SICRO)
2. Use tabelas de custo (seção 5.2) para orçamentação
3. Realize controle de qualidade com protocolo de campo

### Para Especialistas Técnicos

1. Estude **T2 — seção 2** (Propriedades Técnicas) em detalhes
2. Consulte **seção 6** (Tabelas Normativas) para decisões críticas
3. Analise **seção 4** (Cálculos Práticos) para dimensionamento

---

## 📚 Tabelas Principales do T2

- **Tab. 2.1** — Classificação de agregados por origem (pág. 2)
- **Tab. 2.4** — Granulometria (curva de Fuller) para D=19 mm (pág. 3)
- **Tab. 3.1** — Critérios DNIT para CBUQ (pág. 4)
- **Tab. 5.2** — Valores SICRO 2026 para agregados (pág. 6)
- **Tab. 7.1** — Caso BR-116 RJ (quantitativo, custo) (pág. 8)

---

## 🔧 Como Usar Este Conhecimento no Agente

O arquivo `02-agregados.md` está integrado ao Supabase via:

```
Prefixo RAG: rod:pavimento:agregados
Sub-prefixos:
  - rod:pav:agg:tipos          (classificação)
  - rod:pav:agg:propriedades   (IRC, CPA, absorção)
  - rod:pav:agg:seleção        (DNIT, faixas)
  - rod:pav:agg:origem         (jazidas, regiões BR)
  - rod:pav:agg:granulometria  (Fuller, faixas A-F)
  - rod:pav:agg:sicro          (composições, custos)
  - rod:pav:agg:casos          (BR real)
```

Ao fazer uma query, o agente-infraestrutura recuperará chunks relevantes de `02-agregados.md`.

---

## 📞 Suporte & Escalação

| Dúvida | Contatar | Escalação |
|--------|----------|-----------|
| Conteúdo técnico T2 | [DNIT Specialist] | technical-review@manta |
| Integração RAG | [Manta 16 Arquiteto IA] | escalate:manta-arq |
| Casos reais de obra | Maurício Neves (PM) | MN@manta.br |

---

## ✅ Checklist: Tópico 2 Completo

- [x] Conceitos fundamentais documentados
- [x] Propriedades técnicas com fórmulas e valores reais
- [x] Seleção normativa (DNIT ES 032/2005)
- [x] Cálculos práticos com exemplos numerados
- [x] Integração SICRO 2026 (composições, custos)
- [x] Tabelas normativas DNIT/ABNT
- [x] 3 casos reais de BR federais
- [x] Checklist de validação de agregados
- [x] Índice maestro criado
- [x] README criado

---

## 📅 Próximas Etapas

- **2026-08-04**: Tópico 2 (Agregados) — ✅ Criado
- **2026-08-15**: Tópico 3 (Ligantes Asfálticos) — Planejado
- **2026-08-29**: Tópico 4 (Misturas Asfálticas) — Planejado
- **2026-09-30**: Integração RAG completa — Planejado

---

**Versão**: 1.0  
**Mantido por**: Agente-infraestrutura S1 + Manta 16 (Arquiteto IA)  
**Última atualização**: 2026-08-04
