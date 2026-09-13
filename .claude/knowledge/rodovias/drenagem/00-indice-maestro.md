# Drenagem em Rodovias — Índice Maestro

**Versão**: 1.0  
**Data**: 2026-08-04  
**Agente responsável**: Manta 03-S1 (Agente Infraestrutura — Rodovias)  
**Status**: Publicado para produção

---

## Propósito

Este índice organiza os tópicos técnicos de **drenagem em projetos rodoviários** segundo a estrutura de fases do ciclo de vida de infraestrutura. Cada tópico fornece conceitos fundamentais, fórmulas, exemplos com valores reais (padrão Vd=100 federal brasileiro), tabelas normativas DNIT e casos de estudo.

---

## Estrutura da Série

### Fundação Teórica

| Tópico | Arquivo | Escopo | Status |
|--------|---------|--------|--------|
| **Tópico 1** | `01-fundamentos-hidrologicos.md` | Ciclo hidrológico, bacias, escoamento, precipitação, evapotranspiração, infiltração, vazão racional | ✅ Completo |
| **Tópico 2** | `02-drenagem-superficial.md` | Sarjetas, valetas, canaletas, cálculo de capacidade, velocidade, proteção contra erosão | 🔄 Planejado |
| **Tópico 3** | `03-drenagem-subsuperficial.md` | Camadas drenantes, drenos perimetrais, geotêxtil, material filtrante, infiltração em profundidade | 🔄 Planejado |

### Projetos Específicos

| Tópico | Arquivo | Escopo | Status |
|--------|---------|--------|--------|
| **Tópico 4** | `04-taludes-trincheiras.md` | Proteção de cortes, drenagem de encostas, trincheiras drenantes, estabilização | 🔄 Planejado |
| **Tópico 5** | `05-bueiros-galerias.md` | Dimensionamento, tipologia (circular, celular), revestimento, fundação, assentamento | 🔄 Planejado |
| **Tópico 6** | `06-intersecoes-dispositivos.md` | Interseções, rotatórias, dispositivos especiais, drenagem em áreas urbanas | 🔄 Planejado |

### Operação e Manutenção

| Tópico | Arquivo | Escopo | Status |
|--------|---------|--------|--------|
| **Tópico 7** | `07-manutencao-inspecao.md` | Inspeção de sistemas, limpeza, desobstrução, reparação, gestão de ciclo de vida | 🔄 Planejado |

---

## Relacionamento com Outros Tópicos Rodoviários

Este índice **drenagem** integra-se aos tópicos irmãos:

```
├── GEOMETRIA
│   ├── Elementos Geométricos
│   ├── Cálculos Práticos
│   └── Interseções & Dispositivos
│
├── PAVIMENTAÇÃO
│   ├── Estrutura do pavimento (suporte)
│   ├── Camadas drenantes (proteção)
│   └── Terraplenagem (interface)
│
├── DRENAGEM (este índice)
│   ├── Fundamentos Hidrológicos
│   ├── Superficial & Subsuperficial
│   ├── Proteção de Taludes
│   ├── Bueiros & Galerias
│   └── Manutenção
│
├── TERRAPLENAGEM & MOVIMENTO DE TERRA
│   ├── Seções transversais
│   ├── Balanço de massas
│   └── Estabilidade (vinculado a drenagem)
│
└── OAE (Obras de Arte Especial)
    ├── Pontes (drenagem crítica)
    ├── Viadutos
    └── Túneis
```

---

## Normas Técnicas Aplicáveis

### Normativas DNIT

- **ES 131/86** — Drenagem Superficial de Rodovias
- **ES 132/86** — Drenagem Subsuperficial de Rodovias
- **ES 133/86** — Drenagem de Cortes e Aterros em Rodovias
- **M 145** — Materiais para Drenagem
- **M 149** — Geotêxteis

### NBR — Associação Brasileira de Normas Técnicas

- **NBR 10844:2020** — Instalações Prediais de Águas Pluviais
- **NBR 6459:2016** — Limite de Liquidez
- **NBR 7180:2016** — Limite de Plasticidade

### Internacionais (compatibilidade)

- **ASCE Manual 28** — Principles and Practices of Water Resources Engineering
- **USDA TR-55** — Urban Hydrology for Small Watersheds
- **FAA AC 150/5320-5H** — Drainage Design (padrão de aeroportos)

---

## Casos de Aplicação por Fase do Ciclo de Vida

### Fase 1: Estudo Prévio / EVTE

**Tópicos relevantes**: 1 (Fundamentos)

- Análise de bacias de drenagem natural
- Estimativa de vazões de chuva máxima (Tr = 25 anos)
- Identificação de riscos de inundação
- Mapeamento preliminar do lençol freático

**Entrega**: Memorando de drenagem com áreas críticas identificadas.

---

### Fase 2: Projeto Básico

**Tópicos relevantes**: 1, 2, 3, 5

- Refinamento de dados hidrológicos (equação IDF regional)
- Dimensionamento preliminar de sistemas (Método Racional)
- Definição de períodos de retorno por tipo de drenagem
- Anteprojeto de sarjetas, valetas, bueiros
- Especificação de materiais drenantes

**Entrega**: Projeto Básico com plantas de drenagem e memorando de cálculos.

---

### Fase 3: Projeto Executivo

**Tópicos relevantes**: 1, 2, 3, 4, 5, 6

- Cálculos detalhados de vazão (seção por seção)
- Definição final de tipologia e dimensões de bueiros
- Detalhamento de camadas drenantes (espessura, permeabilidade)
- Especificações de geotêxtil e material filtrante
- Proteção de taludes e trincheiras drenantes
- Drenagem de intersecções e dispositivos especiais

**Entrega**: Projeto Executivo completo com plantas, perfis, seções, especificações e orçamento.

---

### Fase 4: Obra em Execução

**Tópicos relevantes**: 3, 4, 5, 7

- Recebimento de materiais (permeabilidade certificada)
- Inspeção de assentamento de bueiros
- Teste de infiltração em camadas drenantes (DNIT ES 132/86)
- Relatório de execução (as-built)

**Entrega**: Documentação de execução com testes de conformidade.

---

### Fase 5: Operação & Manutenção

**Tópicos relevantes**: 7

- Inspeção periódica de sistemas de drenagem
- Limpeza e desobstrução de bueiros e valetas
- Reparação de erosão ou colapsos
- Monitoramento de lençol freático

**Entrega**: Relatórios de manutenção preventiva e corretiva.

---

## Fluxo de Consulta — Roteiro por Problema

### Problema: "Qual é a vazão que deve ser drenada?"

1. **Consulte Tópico 1** — Cálculo de vazão pelo Método Racional
   - Delimitação de bacia (área, comprimento)
   - Coeficiente de escoamento
   - Intensidade de chuva (equação IDF)
   - Resultado: **Q em m³/s**

---

### Problema: "Como dreno água que cai na sarjeta?"

1. **Consulte Tópico 2** — Dimensionamento de sarjetas
   - Formato e profundidade
   - Cálculo de capacidade (Manning)
   - Velocidade máxima (proteção contra erosão)
   - Resultado: **Seção de sarjeta adequada**

---

### Problema: "O solo próximo ao pavimento é muito úmido; como posso drenar?"

1. **Consulte Tópico 3** — Drenagem subsuperficial
   - Especificação de camada drenante (material e espessura)
   - Teste de infiltração (DNIT ES 132/86)
   - Drenos perimetrais
   - Resultado: **Detalhes de camada drenante + especificação**

---

### Problema: "Há risco de erosão de talude em corte; como proteger?"

1. **Consulte Tópico 4** — Proteção de taludes
   - Cálculo de fluxo subterrâneo
   - Trincheiras drenantes
   - Proteção superficial
   - Resultado: **Projeto de estabilização**

---

### Problema: "Preciso dimensionar um bueiro para cruzamento de drenagem."

1. **Consulte Tópico 5** — Bueiros e galerias
   - Vazão de projeto (Tópico 1)
   - Tipo de bueiro (circular, celular, retangular)
   - Cálculo de capacidade e verificação de altura de remanso
   - Especificação de fundação e revestimento
   - Resultado: **Dimensões e especificação técnica de bueiro**

---

### Problema: "Como dreno uma interseção ou rotatória?"

1. **Consulte Tópico 6** — Intersecções e dispositivos especiais
   - Áreas de convergência de fluxos
   - Cálculo de bacia local
   - Sistemas combinados (sarjeta + bueiro)
   - Resultado: **Projeto de drenagem em interseção**

---

### Problema: "Qual é a vida útil de um sistema de drenagem? Como manter?"

1. **Consulte Tópico 7** — Manutenção e inspeção
   - Cronograma de inspeção
   - Limpeza preventiva (frequência)
   - Reparação de falhas
   - Resultado: **Plano de manutenção e responsabilidades**

---

## Dados e Valores de Referência (Padrão Vd=100)

### Precipitação Máxima para Períodos de Retorno Comuns

Baseado em série histórica de 40+ anos, rodovia federal média (Centro-Oeste/Sudeste):

| Período de Retorno | Precipitação (mm) | Duração crítica | Intensidade (mm/h) |
|-------------------|------------------|-----------------|-------------------|
| Tr = 2 anos | 70 | 30 min | 110 |
| Tr = 5 anos | 100 | 30 min | 155 |
| Tr = 10 anos | 125 | 30 min | 185 |
| **Tr = 25 anos** | **160** | **30 min** | **245** |
| Tr = 50 anos | 185 | 30 min | 270 |
| Tr = 100 anos | 210 | 30 min | 305 |

*Nota*: Usar valores locais quando série regional disponível em INMET/ANA.

---

### Coeficientes de Escoamento (C) por Tipo de Cobertura

| Tipo | C mín | C máx | Notas |
|------|-------|-------|-------|
| Pavimento asfáltico | 0,95 | 1,00 | Praticamente impermeável |
| Concreto | 0,95 | 1,00 | Impermeável |
| Grama/pasto | 0,15 | 0,30 | Depende declive e tipo de solo |
| Bosque | 0,05 | 0,15 | Boa infiltração |
| Solo nu | 0,20 | 0,40 | Infiltração moderada a baixa |
| Rocha aflorante | 0,40 | 0,70 | Declive influencia muito |

---

### Capacidade de Infiltração por Tipo de Solo

| Solo (SUCS) | f_c (mm/h) | Aplicação |
|-------------|-----------|-----------|
| GW — Cascalho bem graduado | 50–100 | Material para camada drenante (preferido) |
| GP — Cascalho pobremente graduado | 20–50 | Dreno |
| SW — Areia bem graduada | 10–20 | Filtro |
| SP — Areia pobremente graduada | 5–15 | Filtro |
| SM — Areia siltosa | 2–5 | Evitar drenagem |
| SC — Areia argilosa | 0,5–2 | Evitar |
| ML — Silte | 0,2–1 | Não recomendado |
| CL — Argila | 0,05–0,2 | Praticamente impermeável |

---

## Equipes e Responsabilidades

### Fases de Projeto

| Fase | Disciplina primária | Disciplinas de suporte |
|------|-------------------|----------------------|
| Estudo prévio | Hidrologia / Geotecnia | Topografia, Ambiente |
| Projeto básico | Drenagem (Engenheiro) | Geotecnia, Pavimentação |
| Projeto executivo | Drenagem | Geotecnia, Estrutura (OAE) |
| Execução | Drenagem / Fiscalização | Geotecnia, Qualidade |
| Operação | Operador / Concedente | Drenagem (consultoria) |

---

## Integração com SkillBook Manta

Esta série de documentos **drenagem** alimenta os seguintes **skills** Manta:

- **skill:rodovias** — Menção a "drenagem", "escoamento", "vazão", "precipitação"
- **skill:rodovias-geotecnia** — Menção a "infiltração", "lençol freático", "permeabilidade"
- **skill:manta-maestro** — Roteamento de queries de drenagem para Agente S1

**Modelo de integração**:
```
Usuário: "Qual é a vazão que deve ser drenada em uma bacia de 12 ha?"
         ↓
Maestro: "Roteando para agente-infraestrutura S1 (rodovias)..."
         ↓
S1 (Claude Code): Carrega Tópico 1 (Fundamentos Hidrológicos)
         ↓
Resposta: Método Racional com exemplo prático
```

---

## Histórico de Versões

| Versão | Data | Alterações |
|--------|------|-----------|
| **1.0** | 2026-08-04 | Criação inicial; Tópico 1 completo; estrutura planejada para Tópicos 2–7 |

---

## Próximas Ações

- [ ] Completar **Tópico 2** (Drenagem Superficial) — Estimativa: 1 semana
- [ ] Completar **Tópico 3** (Drenagem Subsuperficial) — Estimativa: 1 semana
- [ ] Validar exemplos de cálculo com casos reais de projetos Manta em execução
- [ ] Criar **README.md** nesta pasta com resumo executivo
- [ ] Registrar esta série no catálogo de skills Manta

---

**Responsável**: Agente Infraestrutura S1 (Manta Associados)  
**Status**: Ativo — Produção  
**Próxima revisão**: 2026-12-31
