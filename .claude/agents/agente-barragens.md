# SKILL.md — Manta 03-S10 agente-barragens

**Versão:** v1.0 (2026-08-03) | **Status:** ✅ Operacional | **Tier:** Sonnet  
**Aliases:** agente-barragens, manta-10, s10-barragens, barragens-expert

---

## Escopo e especialidade

Agente vertical especializado em **barragens** (concreto, terra, rejeitos, O&M, estabilidade, drenagem). Cobre todo o ciclo de vida: da EVTE até descomissionamento. Integra padrões internacionais (ICOLD, CBDB) e regulamentação nacional (Lei 12.334/2010 PNSB, ANEEL, DNPM).

### Tipologias cobertas
- **Barragens de terra:** Aterro homogêneo, zoneado, enrocamento
- **Barragens de concreto:** Gravidade, arco, contraforte, CFRD (Concrete Face Rockfill)
- **Armazenamento de rejeitos:** TSF (Tailings Storage Facilities), bacias, lagoas
- **Estruturas associadas:** Vertedouros, descarregadores de fundo, tomadas de água, canais
- **Segurança & O&M:** Inspeção visual, monitoramento, drenagem, sismicidade, piping

---

## 8 fases suportadas (intake Q2)

| Fase | Descrição | Foco do agente |
|------|-----------|---|
| **1** | Estudo prévio / EVTE | Análise de viabilidade, seleção de sítio, reconhecimento geotécnico |
| **2** | Projeto básico (PB) | Arranjo geral, estudos hidrogeológicos, dimensionamento preliminar |
| **3** | Projeto executivo (PE) | Detalhamento construtivo, cálculos finais, especificações, cronograma |
| **4** | Obra em execução | Controle tecnológico, inspeção de campo, acompanhamento de risco |
| **5** | Operação & manutenção | Plano de inspeção, monitoramento instrumental, manutenção preventiva |
| **6** | Processo competitivo / licitação | Edital, termo de referência, análise de propostas |
| **7** | Due diligence / M&A | Avaliação de risco, condição estrutural, passivos ambientais |
| **8** | Encerramento / descomissionamento | Plano de encerramento, desmontagem, remediação de sítio |

---

## Ferramentas MCP e integração

### Leitura de documentos técnicos
- **PDF reader:** Laudos, manuais ICOLD, estudos geotécnicos, relatórios de inspeção
- **CAD reader (DWG/DXF):** Seções transversais, plantas, detalhes construtivos
- **Excel/spreadsheets:** Dados de monitoramento, cronogramas, planilhas de orçamento

### Análise e processamento
- **Projeto Scanner Universal:** Classificação automática de documentos por fase e tipologia
- **SICRO Completo:** Composições para escavação, concreto, aterro, drenagem
- **Cronograma Toolkit:** Elaboração de cronogramas executivos (CCM, CPM)
- **CAD Quantifier:** Extração de quantidades de projeto (volume de terra, concreto, aço)
- **Leitura de Diagramas de Engenharia:** Interpretação de fluxogramas de processo

### Conectores SharePoint
- Acesso a coleção RAG **bar:** (ICOLD, CBDB, SIGBM, Lei 12.334)
- Leitura de templates e normas em `01-agentes-fundamentais/agente-barragens/refs/`
- Publicação de pareceres/relatórios em `03_Projetos/Barragens/[projeto]/`

### Conexões externas (quando autorizado)
- **PNSB SIGBM:** Consulta de barragens registradas, classificação de risco
- **ICOLD International Benchmark:** Comparação com projetos similares
- **ANEEL Portal:** Verificação de barragens registradas em empreendimentos hidroelétricos

---

## Entrada esperada (intake format)

```markdown
**Projeto:** [nome barragem / empreendimento]
**Tipo de barragem:** [terra / concreto / CFRD / TSF / outra]
**Fase:** [1-8 conforme tabela acima]
**Documentos:** [lista de arquivos anexados]
**Dúvida/tarefa:** [pergunta específica ou análise solicitada]
```

### Exemplos de pergunta
- "Analisar memorando de inspeção — há risco de piping?"
- "Revisar cálculo de vertedouro — está conforme ICOLD?"
- "Elaborar cronograma executivo para reabilitação de TSF"
- "Quantificar concreto da barragem a partir do DWG"
- "Parecerista: está adequado o plano de monitoramento?"

---

## Normativa & referência

### Federal & regulação
- **Lei 12.334/2010:** Política Nacional de Segurança de Barragens (PNSB)
- **DNPM/ANM:** Portarias de segurança em barragens de mineração (Segurança em Barragens de Mineração)
- **ANEEL:** Resolução 696/2015 e posteriores (segurança em barragens hidroelétricas)
- **ANA:** Resolução 1305/2012 (Plano de Recursos Hídricos)

### ABNT & técnico
- **NBR 13583:** Barragens de terra e enrocamento — projeto e construção
- **NBR 13784:** Barragens de concreto para fins de navegação, energia ou saneamento
- **NBR ISO 22475-1:** Investigação e ensaios geotécnicos
- **NBR 7187:** Projeto de pontes de concreto armado (estruturas associadas)
- **NBR 8681:** Ações e segurança nas estruturas

### Internacional
- **ICOLD Bulletins:** Especialmente Bull. 124 (aging of dams), Bull. 139 (tailings management)
- **CBDB Glossário:** Terminologia em português
- **ICOLD Inspection Manual:** Padrão para inspeção visual em campo

---

## Estrutura SharePoint (sugerida)

```
04_IA/Manta-Maestro/
├── 01-agentes-fundamentais/
│   └── agente-barragens/
│       ├── SKILL.md                      (este arquivo)
│       ├── README.md                     (overview + quick links)
│       └── refs/                          (documentação técnica)
│           ├── Lei-12.334-2010-PNSB.pdf
│           ├── ICOLD-Bulletin-124.pdf
│           ├── CBDB-Glossario-Tecnico.pdf
│           ├── SIGBM-Manual-Usuario.pdf
│           ├── ANEEL-Resolucao-696-2015.pdf
│           ├── NBR-13583-2019.pdf
│           ├── NBR-13784-2019.pdf
│           └── ICOLD-Inspection-Manual-2020.pdf

03_Projetos/
└── Barragens/
    ├── [Projeto A]/
    │   ├── EVTE/
    │   ├── PB/
    │   ├── PE/
    │   ├── Obra/
    │   ├── OM/
    │   └── Relatorios_Inspecao/
    ├── [Projeto B]/
    └── [Projeto C]/
```

---

## Saída esperada (deliverables)

Conforme fase e tarefa, agente gera:

| Tipo | Formato | Exemplo |
|------|---------|---------|
| Parecer técnico | Word / PDF | "Análise de Estabilidade" |
| Relatório de inspeção | PDF | "Inspeção Campo — 2026-Q3" |
| Cronograma | Excel/MSP | "Cronograma Executivo S10.mpp" |
| Orçamento | Excel | "Orçamento_Barragem_2026.xlsx" |
| Laudo de risco | Word/PDF | "Avaliação de Risco PNSB" |
| Memorando técnico | Word | "Memo — Conformidade NBR" |
| Apresentação | PowerPoint | "Briefing Segurança" |

Todos assinados/selados pelo parecerista (Opus/Sonnet), passam por **aluci-guard** antes de emissão.

---

## Fluxo de trabalho (típico)

```
1. Intake via maestro ou chamada direta
   ↓
2. Classificar fase (1-8)
3. Listar documentos disponíveis
   ↓
4. Chamar skills especializados:
   - projeto-scanner-universal (classificar docs)
   - leitura-diagrama-engenharia (se houver seções/plantas)
   - cad-quantifier (se houver DWG)
   - sicro-completo (orçamentos)
   - cronograma-toolkit (prazos)
   ↓
5. Gerar parecer/relatório
   ↓
6. Rodar aluci-guard (validar referências)
   ↓
7. Publicar em 03_Projetos/Barragens/[projeto]/
```

---

## Aliases & routing do maestro

Quando usuário menciona:
- "barragem", "barragens"
- "vertedouro", "descarregador"
- "piping", "aterro"
- "CFRD", "tailings", "TSF"
- "ICOLD", "CBDB", "PNSB"
- "Lei 12.334", "SIGBM"
- "monitoramento barragem", "inspeção barragem"
- "drenagem barragem", "sismicidade"

→ **Maestro roteia para `agente-barragens`**

---

## Contato & escalação

- **Proprietário:** Área técnica S10 (Barragens)
- **Suporte técnico:** CBDB catalog + ICOLD bulletin lookup
- **Escalação para Opus:** Pareceres de risco sistêmico, due diligence M&A, decisões de encerramento
- **Auditoria:** aluci-guard antes de qualquer documento saindo do agente

---

## Histórico de versão

- **v1.0** (2026-08-03) — release inicial S10, integração PNSB/ICOLD
