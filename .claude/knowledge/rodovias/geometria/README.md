# 📚 Geometria de Rodovias — Índice de Documentação

**Versão**: v4.3 (Fase I Consolidada)  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Data Atualização**: 2026-08-04  
**Branch**: `claude/agente-rodovias-conhecimento-6jhqhc`

---

## 🎯 Comece Aqui

### Novo no Tema?
👉 Leia em ordem:
1. **01-elementos-geometricos.md** (30 min) — Conceitos fundamentais
2. **02-calculos-praticos.md** (45 min) — Exemplos reais passo-a-passo
3. **00-indice-maestro.md** (15 min) — Visão geral da estrutura

### Precisa de Referência Rápida?
👉 Vá diretamente para:
- **Raio mínimo?** → Doc 01, Seção "Alinhamento Horizontal"
- **Superelevação?** → Doc 04, Seção "Superelevação"
- **Orçamento?** → Doc 02, Seção "Cálculos SICRO"
- **Interseções (PARCLO, Diamante)?** → Doc 06
- **Brückner?** → Doc 07

### Implementando em Projeto?
👉 Siga o fluxo:
1. **Doc 05** (Normas DNIT) — Valide contra ES 101/97
2. **Doc 01-03** (Elementos & Cálculos) — Dimensione geometria
3. **Doc 03** (Softwares) — Use MX Road ou Civil 3D
4. **Doc 08** (Especializações) — Aprofunde conforme necessário

---

## 📋 Documentos por Foco

### 🔹 Nível 1 — Fundação (30 min)

**[01-elementos-geometricos.md](./01-elementos-geometricos.md)**
- Alinhamento horizontal: conceitos, fórmulas, tabelas
- Alinhamento vertical: rampas, curvas parabólicas
- Seção transversal: componentes, dimensões
- Visibilidade: distância de parada, critérios

**Quando usar**: Começar projeto, entender conceitos básicos

---

### 🔹 Nível 2 — Aplicação (60 min)

**[02-calculos-praticos.md](./02-calculos-praticos.md)**
- Caso 1: BR Federal (Vd=100)
- Caso 2: Rodovia Estadual (Vd=80, montanhosa)
- Orçamento SICRO integrado
- Cronograma de execução

**Quando usar**: Dimensionar projeto novo, orçar, planejar execução

**[03-softwares-referencias.md](./03-softwares-referencias.md)**
- MX Road: workflow prático
- Civil 3D: corridors e assemblies
- SICRO: integração de custos
- Drone mapping: captura topográfica

**Quando usar**: Escolher ferramenta, aprender automação

---

### 🔹 Nível 3 — Especialização (2-4 horas)

**[04-integracao-sharepoint-maestro.md](./04-integracao-sharepoint-maestro.md)**
- Mapeamento com SharePoint Manta Maestro
- SKILL.md integration
- RAG prefixes: `rod:geom:*`
- Fluxo de consolidação

**Quando usar**: Integrar com Manta, fazer upload em SharePoint

**[04-curvas-horizontais-avancado.md](./04-curvas-horizontais-avancado.md)**
- Clotóides simples e duplas
- Espirais logarítmicas
- Radii variáveis
- Validação de visibilidade 3D

**Quando usar**: Curvas complexas, terreno desafiador

**[05-normas-dnit-brasileiras.md](./05-normas-dnit-brasileiras.md)**
- ES 101/97 completa
- ES 131/86 (drenagem)
- NBR standards
- Checklist de conformidade
- Composições SICRO normalizadas

**Quando usar**: Validar conformidade, citar normas, auditoria

**[06-intersecoes-dispositivos-seguranca.md](./06-intersecoes-dispositivos-seguranca.md)**
- Rotatórias: fórmulas, dimensionamento
- Cloverleaf completa: custos R$80-120M
- PARCLO (A, B, D): custos R$45-60M
- Diamond intersection: custos R$15-25M
- Dispositivos de segurança (defensas, tachosl)
- Análise de risco geométrico
- Casos reais: BR-116, BR-101

**Quando usar**: Projeto de interseção, análise de risco, orçamento

**[07-balanço-massa-movimento-terra.md](./07-balanço-massa-movimento-terra.md)**
- Diagrama de Brückner: construção passo-a-passo
- Free Haul Distance (FHD)
- Custos de escavação, transporte, compactação
- Borrow areas e rejeitos
- Compensação lateral vs longitudinal
- Python script para automatizar

**Quando usar**: Otimizar movimento terra, reduzir custo transporte

**[08-especializacoes-paralelas.md](./08-especializacoes-paralelas.md)**
- 20 especializações (20 agentes Sonnet)
- Tópicos: DNIT, clotóides, superelevação, visibilidade, V, taludes, pavimentação, casos reais, softwares, SICRO, drone, interseções, drenagem, segurança, testes, reabilitação, integração, templates, roadmap

**Quando usar**: Aprofundar em tópico específico, ML/otimização

---

## 🗂️ Índice Maestro

**[00-indice-maestro.md](./00-indice-maestro.md)** — Visão geral da estrutura completa
- Status do workflow paralelo (20 agentes)
- Matriz de cobertura por fase de projeto
- Integração com RAG Supabase
- Próximos passos (Fase II)

---

## 🧪 Testes & Validação

**[../tests/geometria-rodovias-validation.md](../tests/geometria-rodovias-validation.md)** — 5 smoke tests
- Teste 1: Raio mínimo & superelevação
- Teste 2: Visibilidade em curva
- Teste 3: Orçamento SICRO
- Teste 4: Recomendação de parâmetros
- Teste 5: Análise de risco

---

## 🚀 Fluxos de Uso

### Fluxo 1: Projetar Rodovia Nova
```
1. Doc 01 → Entender conceitos
2. Doc 05 → Validar contra normas
3. Doc 02 → Calcular dimensões
4. Doc 03 → Usar software (MX Road/Civil 3D)
5. Doc 08 → Aprofundar tópico específico
6. Doc 06 → Se houver interseção
7. Doc 07 → Otimizar terraplenagem
```

### Fluxo 2: Analisar Rodovia Existente
```
1. Doc 06 → Verificar interseções
2. Doc 01 → Comparar contra parâmetros
3. Doc 08 (Teste 5) → Análise de risco
4. Doc 07 → Brückner se reabilitação
5. Doc 02 → Orçamento de intervenção
```

### Fluxo 3: Resolver Problema Específico
```
"Qual raio mínimo para Vd=100?"
→ Doc 01, Seção "Alinhamento Horizontal"

"Como calcular superelevação?"
→ Doc 04, Seção "Superelevação"

"Qual custo SICRO para CBUQ 5cm?"
→ Doc 02, Seção "Orçamento SICRO"

"Curva perigosa, como mitigar?"
→ Doc 08, Teste 5 + Doc 06

"Quantificar movimento terra?"
→ Doc 07, "Diagrama de Brückner"
```

---

## 📊 Cobertura Total

| Aspecto | Cobertura | Documento |
|---------|-----------|-----------|
| **Normativo** | ES 101/97, ES 131/86, NBR 6123, 11682, 14644 | Doc 05 |
| **Horizontal** | Retas, arcos, clotóides simples/duplas, espirais | Doc 01, 04 |
| **Vertical** | Rampas, curvas parabólicas, frenagem | Doc 01, 05 |
| **Transversal** | Largura, taludes, banquetas, drenagem | Doc 01, 06 |
| **Visibilidade** | Distância parada, flecha, risco | Doc 01, 04, 06 |
| **Cálculos** | Raio, superelevação, volume, custo | Doc 02, 07, 08 |
| **Softwares** | MX Road, Civil 3D, SICRO, Drone | Doc 03, 08 |
| **Casos Reais** | BR-116, BR-101, BR-163, histórico | Doc 02, 06, 08 |
| **Interseções** | Rotatória, Cloverleaf, PARCLO, Diamond | Doc 06 |
| **Brückner** | Diagrama, FHD, otimização | Doc 07 |
| **Testes** | 5 smoke tests críticos | tests/ |

---

## 🔗 Integração com Manta

### RAG (Supabase)
```
Coleção: rodovias
Prefixo: rod:geom:*

Sub-prefixos:
├─ rod:geom:h              # Alinhamento horizontal
├─ rod:geom:v              # Alinhamento vertical
├─ rod:geom:seção          # Seção transversal
├─ rod:geom:visibilidade   # Visibilidade e risco
├─ rod:geom:cálculos       # Fórmulas e exemplos
├─ rod:geom:normas         # Referências DNIT/NBR
├─ rod:geom:softwares      # MX Road, Civil 3D
├─ rod:geom:sicro          # Orçamento
├─ rod:geom:casos          # Casos reais
└─ rod:geom:testes         # Scripts validação
```

### SharePoint Manta
```
01-agentes-fundamentais/agente-infraestrutura-s1/
├── refs/
│   ├── 01-elementos-geometricos.md
│   ├── 05-normas-dnit-brasileiras.md
│   └── DNIT-ES-101-97.pdf
│
└── exemplos/
    ├── br-116-sp-mg-real.md
    ├── br-101-rj-sp.md
    └── casos-reais.md
```

### SKILL.md (Agente-infraestrutura S1)
```yaml
disciplinas: [Geometria, Pavimentação, Terraplenagem, Drenagem]
normas: [ES 101/97, ES 131/86, IPR 702, IPR 726, NBR 6123, 11682, 14644]
softwares: [MX Road, Civil 3D, SICRO, Drone Mapping]
rag_collection: rodovias
rag_prefix: rod:geom:*
```

---

## 📈 Estatísticas

- **Total de documentos**: 9 (01-08 + README)
- **Total de linhas**: ~12,000
- **Total de tópicos**: 100+
- **Casos reais**: 3 (BR-116, BR-101, BR-163)
- **Fórmulas integradas**: 15+
- **Tabelas normativas**: 20+
- **Scripts Python**: 3 (validação)
- **Tempo de leitura total**: ~3 horas (Nível 1-2), +4 horas (Nível 3)

---

## ✅ Checklist de Uso

### Antes de Usar
- [ ] Entendeu nível de detalhe necessário
- [ ] Identificou documento apropriado
- [ ] Validou fonte normativa (ES 101/97)

### Ao Usar
- [ ] Consultou exemplos práticos
- [ ] Comparou com casos reais
- [ ] Confirmou valores contra tabelas
- [ ] Citou fonte em projeto/parecer

### Após Usar
- [ ] Documentou decisões tomadas
- [ ] Validou contra norma
- [ ] Agregou novo caso/lição aprendida (feedback)

---

## 🔄 Atualizações & Evolução

### Próximas Fases (Roadmap)

**Fase II — Disciplinas Transversais** (após aprovação MN)
- Pavimentação (20 agentes)
- Terraplenagem (15 agentes)
- Drenagem (15 agentes)
- O&M (10 agentes)
- Timeline: 15-20 dias

**Fase III — Inteligência Avançada**
- Machine Learning: previsão de falhas
- Otimizador de traçado: minimizar custo
- Big Data: análise integrada clima+tráfego+accidents

---

## 📞 Suporte & Feedback

### Dúvidas Frequentes
- "Qual raio mínimo?" → Doc 01, tabela
- "Como orçar?" → Doc 02, seção SICRO
- "Qual Vd?" → Doc 04 (teste 4)
- "Curva perigosa?" → Doc 06 + Doc 08 (teste 5)

### Reportar Problema
- Erro técnico: abre issue no GitHub
- Falta de conteúdo: request em backlog
- Atualização SICRO: sincroniza com DNIT mensal

### Contribuir
- Adicionar caso real: cria PR com novo exemplo
- Melhorar fórmula: valida contra norma + submete review
- Expandir tópico: coordena com PM (Maurício Neves)

---

## 📖 Histórico de Versões

| Versão | Data | Mudança |
|--------|------|---------|
| v4.3 | 2026-08-04 | Consolidação Fase I: 9 docs, 20 agentes, RAG ready |
| v4.2 | 2026-08-03 | Base: 6 docs + integração Manta Maestro |
| v4.1 | Anterior | Fundação: elementos geométricos + cálculos |

---

**Última atualização**: 2026-08-04  
**Próxima review**: Após aprovação MN (Fase II)  
**Mantido por**: Agente-infraestrutura S1 + Manta 16 (Arquiteto IA)

