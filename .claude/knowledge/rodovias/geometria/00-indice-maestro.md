# 📚 Índice Maestro — Geometria de Rodovias

**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:*`  
**Status**: 🔄 Consolidação em andamento (20 agentes Sonnet em paralelo)  
**Data**: 2026-08-03  
**Branch**: `claude/agente-rodovias-conhecimento-6jhqhc`

---

## 🎯 Objetivo

Aprofundar e expandir o conhecimento do agente-infraestrutura S1 em **geometria de rodovias**, cobrindo:
- ✅ Normas fundamentais (DNIT, NBR, ABNT)
- ✅ Elementos geométricos (H, V, transversal)
- ✅ Cálculos práticos e exemplos reais
- ✅ Softwares padrão (MX Road, Civil 3D)
- ✅ Orçamentação SICRO
- ✅ Testes de validação e checklist

---

## 📋 Estrutura de Conhecimento

### 1️⃣ Documentos Criados (Estáticos)

| Arquivo | Tópicos | Status |
|---------|---------|--------|
| `01-elementos-geometricos.md` | Alinhamento H, Alinhamento V, Seção Transversal, Visibilidade | ✅ Completo |
| `02-calculos-praticos.md` | Casos reais BR, Raios, Superelevação, SICRO | ✅ Completo |
| `03-softwares-referencias.md` | MX Road, Civil 3D, SICRO, Normas | ✅ Completo |
| `00-indice-maestro.md` | Este documento | 🔄 Sendo atualizado |

### 2️⃣ Conteúdo em Paralelo (20 Agentes)

| Agente # | Tópico | Foco Principal |
|----------|--------|----------------|
| 1 | Normas DNIT ES 101/97 | Fundamentação normativa completa |
| 2 | Curvas Horizontais Avançadas | Clotóides, radii variáveis, espirais duplas |
| 3 | Superelevação — Métodos | Rotação de eixo, bordo, transição suave |
| 4 | Visibilidade em Curva 3D | Flecha, banquetas, análise risco |
| 5 | Alinhamento Vertical | Parábolas côncavas/convexas, frenagem |
| 6 | Seção Transversal Avançada | Taludes, estabilidade, drenagem |
| 7 | Pavimentação | CBUQ/BGS, espessuras, vida útil |
| 8 | Casos Reais | BR-116, BR-101, BR-163 (histórico Manta) |
| 9 | MX Road | Automação, macros, saída DNIT nativa |
| 10 | Civil 3D | Corridors, assemblies, volumes dinâmicos |
| 11 | SICRO | Composições, índices, automação custo |
| 12 | Drone Mapping | Captura, densidade, processamento |
| 13 | Interseções | Rotatórias, triângulo visibilidade |
| 14 | Drenagem Superficial | Banquetas, declividades, proteção |
| 15 | Segurança & Risco | Curvas perigosas, acidentes, mitigação |
| 16 | Testes Unitários | Python scripts, validação geométrica |
| 17 | Projeto vs Reabilitação | Novo traçado vs ajustes, custos |
| 18 | Integração Agente-infraestrutura | Prompts, intake, outputs |
| 19 | Templates & Checklists | Estruturas, validação final |
| 20 | Roadmap Futuro | ML, otimização, big data |

---

## 📊 Matriz de Cobertura

### Por Fase de Projeto

```
Estudo Prévio
  ├─ Reconhecimento topográfico (Drone Mapping) ✅ #12
  ├─ Análise de classe/velocidade (Normas DNIT) ✅ #1
  └─ Levantamento preliminar ✅

Projeto Básico
  ├─ Alinhamento horizontal (Curvas H) ✅ #2, #9
  ├─ Alinhamento vertical (Curvas V) ✅ #5, #9
  ├─ Seção transversal tipo ✅ #6
  └─ Volumetria preliminar ✅ #10

Projeto Executivo
  ├─ Detalhamento (Superelevação) ✅ #3
  ├─ Visibilidade verificada ✅ #4
  ├─ Drenagem superficial ✅ #14
  ├─ Taludes/banquetas ✅ #6
  └─ Memoriais DNIT ✅ #1

Obra
  ├─ Orçamento SICRO ✅ #11, #7
  ├─ Pavimentação sequência ✅ #7
  └─ Segurança e risco ✅ #15

O&M
  ├─ Manutenção de geometria ✅ #14
  ├─ Análise de falhas ✅ #15
  └─ Reabilitação ✅ #17
```

### Por Especialidade Técnica

```
Cálculo & Fórmulas
  • R_mín, superelevação, clotóide ✅ #2, #3
  • Visibilidade, frenagem ✅ #4, #5
  • Volume terraplenagem ✅ #10

Desenho & CAD
  • Alinhamento H/V ✅ #9
  • Seções transversais ✅ #10
  • Detalhes de construção ✅ #6

Normativo
  • DNIT ES 101/97 ✅ #1
  • Tabelas oficiais ✅ #1
  • Critérios de segurança ✅ #15

Orçamento
  • Composições SICRO ✅ #11
  • Quantitativos ✅ #7, #10
  • Sequência obra ✅ #17

Casos de Uso
  • Projeto novo ✅ #8, #17
  • Reabilitação ✅ #17
  • Análise de risco ✅ #15

Integração Agente-infraestrutura
  • Prompts de intake ✅ #18
  • Q&A do agente ✅ #18
  • Outputs estruturados ✅ #18, #19
```

---

## 🔧 Integração com RAG (Supabase)

Após consolidação, migrar para Supabase com estrutura:

```
Coleção: rodovias (prefixo: rod:)

Sub-prefixos:
├─ rod:geom:                     # Geometria (tudo)
│  ├─ rod:geom:h                # Alinhamento horizontal
│  ├─ rod:geom:v                # Alinhamento vertical
│  ├─ rod:geom:seção            # Seção transversal
│  ├─ rod:geom:visibilidade     # Visibilidade e risco
│  ├─ rod:geom:cálculos         # Fórmulas e exemplos
│  ├─ rod:geom:normas           # Referências DNIT/NBR
│  ├─ rod:geom:softwares        # MX Road, Civil 3D
│  ├─ rod:geom:sicro            # Orçamento
│  ├─ rod:geom:casos            # Casos reais
│  └─ rod:geom:testes           # Scripts validação
│
├─ rod:pavimento:               # Pavimentação
│  ├─ rod:pavimento:cbuq        # Concreto betuminoso
│  ├─ rod:pavimento:bgs         # Bases granulares
│  └─ rod:pavimento:vida_util   # Dimensionamento
│
├─ rod:terraplenagem:           # Movimento de terra
├─ rod:drenagem:                # Hidrologia/drenagem
├─ rod:segurança:               # Análise de risco
└─ rod:casos_reais:             # BR-116, BR-101, etc
```

---

## 📝 Prompts de Teste (Validação)

Após consolidação, testar agente com:

### Teste 1: Geometria Básica
```
"Preciso projetar uma curva horizontal em uma BR federal (Vd=100 km/h). 
O raio disponível é 400m. Qual deve ser a superelevação? 
Qual o comprimento da clotóide? Preciso de recuo de banqueta?"
```

**Saída esperada**:
- e ≈ 4.7%
- L_c ≈ 110m
- Flecha ≈ 4.7m

### Teste 2: Visibilidade
```
"Tenho uma curva de 500m de raio. A distância de parada é 137m. 
Qual flecha de recuo preciso abrir na banqueta de corte?"
```

**Saída esperada**:
- f ≈ 4.7m (conforme cálculo 02-calculos-praticos.md)

### Teste 3: Orçamento
```
"Preciso orçar 1km de rodovia federal, pista dupla, Vd=100 km/h, 
pavimento CBUQ 5cm. Qual quantitativo e custo SICRO estimado?"
```

**Saída esperada**:
- Pavimento: 7,200 m²
- SICRO: ~R$ 5.2M (conforme 02-calculos-praticos.md)

### Teste 4: Integração Agente
```
"Tenho uma rodovia estadual, topografia montanhosa, volume 400k veículos/ano. 
Qual deve ser minha velocidade de projeto e padrões geométricos?"
```

**Saída esperada**:
- Vd = 80 km/h
- R_mín = 220m
- e = 7.0%
- Faixa = 3.30m

### Teste 5: Análise de Risco
```
"Identifiquei um trecho da BR com 4 acidentes em 2 anos. 
As curvas têm R=250m (Vd=100km/h). 
Qual é o risco geométrico e como mitigá-lo?"
```

**Saída esperada**:
- Risco alto (R < R_mín)
- Mitigação: reduzir Vd ou reconstruir curva

---

## 🚀 Próximos Passos (Roadmap)

### Semana 1 (Consolidação)
- [ ] Consolidar output dos 20 agentes
- [ ] Revisar consistência técnica
- [ ] Integrar em documentos mestres
- [ ] Criar migração SQL para Supabase

### Semana 2 (Implementação RAG)
- [ ] Aplicar migração Supabase
- [ ] Indexar 20 coleções de conhecimento
- [ ] Testar retrieval (busca de chunks)
- [ ] Validar respostas agente

### Semana 3 (Testes & Validação)
- [ ] Rodar 5 prompts de teste
- [ ] Comparar com respostas esperadas
- [ ] Ajustar prompts do agente se necessário
- [ ] Documentar lições aprendidas

### Semana 4 (Deploy)
- [ ] Merge na branch main
- [ ] Deploy em produção
- [ ] Monitoramento de uso
- [ ] Feedback loop

---

## 📞 Contacts & Escalations

| Papel | Responsável | Escalação |
|-------|-------------|-----------|
| PM (Agente-infraestrutura) | Maurício Neves | MN@manta.br |
| Arquiteto IA (Manta 16) | [Manta 15-ARQ] | escalate:manta-arq |
| Revisor Técnico | DNIT/NBR specialist | technical-review |
| Testes QA | [QA Team] | qa-rodovias |

---

## 📚 Referências Cruzadas

- **CLAUDE.md**: Registro mestre dos 20 agentes Manta
- **ARQUITETURA-AGENTES-IA.md**: Estrutura de 5 camadas (C0-C5)
- **docs/DEPLOY-v4.2.md**: Checklist de deploy
- **tests/routing/prompts.md**: Testes de roteamento

---

## 📊 Status Workflow Paralelo

```
Iniciado: 2026-08-03
Agentes: 20 × Claude Sonnet 5
Execução: Paralela (max concorrência ~10)
Timeout: 600s per agente
Status: 🔄 EM ANDAMENTO

Progresso esperado:
  ├─ Planejamento: ✅ Completo
  ├─ Execução Paralela: 🔄 EM ANDAMENTO
  └─ Consolidação: ⏳ Aguardando resultado

Resultado será consolidado aqui quando completo.
```

---

## 🎓 Estrutura de Aprendizado

Este material é organizado em **3 níveis de profundidade**:

### Nível 1 — Fundação (Iniciante)
📄 Documentos: `01-elementos-geometricos.md`  
🎯 Objetivo: Entender conceitos básicos (raio, superelevação, visibilidade)  
⏱️ Tempo: 30 min

### Nível 2 — Aplicação (Intermediário)
📄 Documentos: `02-calculos-praticos.md`, `03-softwares-referencias.md`  
🎯 Objetivo: Resolver problemas reais, dimensionar projetos  
⏱️ Tempo: 2h

### Nível 3 — Especialização (Avançado)
📄 Documentos: Output dos 20 agentes Sonnet  
🎯 Objetivo: Profundidade em cada subdisciplina  
⏱️ Tempo: 4h+

---

## ✅ Checklist Final

- [ ] Documentação estática criada (3 arquivos)
- [ ] Workflow paralelo lançado (20 agentes)
- [ ] Índice maestro consolidado
- [ ] Testes de validação definidos
- [ ] Integração RAG planejada
- [ ] Migração Supabase criada
- [ ] Deploy checklist atualizado
- [ ] Aprovação MN antes de merge
- [ ] Commit na branch designada
- [ ] PR aberto com documentação

---

**Última atualização**: 2026-08-03  
**Próxima review**: 2026-08-10  
**Mantido por**: Agente-infraestrutura S1 + Manta 16 (Arquiteto IA)
