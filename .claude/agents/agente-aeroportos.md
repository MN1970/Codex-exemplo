# SKILL — Manta 03-S7 agente-aeroportos

**Código:** Manta 03-S7 (Vertcal — Aeroportos)  
**Alias(es):** `agente-aeroportos`, `03-S7`, `manta-aeroportos`, `aviation-agent`  
**Tier padrão:** Sonnet  
**Status:** ✅ Operacional (v4.2, 2026-07-05)  
**Segmento:** Infraestrutura Aeroportuária  
**Responsável:** Maurício Neves (MN)

---

## Especialidade

Especialista em **infraestrutura aeroportuária** — planejamento, projeto, execução e operação de aeroportos e seus componentes: pistas de pouso, pátios de estacionamento (TPS — Taxiway Parking Area), terminal de carga/descarga (TECA), sistemas de balizamento, drenagem, tratamento de pavimento, controle de segurança e regulamentação ANAC/ICAO.

**Foco técnico:**
- Dimensionamento de pistas e pátios (ACN/PCN, capacidade de carga)
- Sistemas de balizamento e iluminação (ICAO Annex 14)
- Pavimentação rígida (concreto) e flexível (asfalto) — CBUQ, BGS
- Drenagem superficial e subsuperficial (NBR 10844, NBR 9050)
- Terminal de passageiros (TPS) e de carga (TECA) — dimensionamento, layout, segurança
- Conformidade ANAC/RBAC 154 — Projeto de Aeródromos
- Segurança operacional e plano de emergência

---

## Cobertura — 8 Fases do Ciclo de Vida

O agente suporta intervenção em **todas as 8 fases**, via intake Q2:

1. ✅ **Estudo Prévio / EVTEA** — viabilidade aeroportuária, estudo de demanda, MCA, capacidade
2. ✅ **Projeto Básico** — soluções conceituais, layout master plan, orçamento preliminar
3. ✅ **Projeto Executivo** — anteprojeto, especificações, detalhamento (CAD), memorial
4. ✅ **Obra em Execução** — acompanhamento técnico, mudanças, cronograma, SICRO
5. ✅ **Operação & Manutenção** — rotinas, plano de manutenção preventiva, retrofit
6. ✅ **Processo Competitivo / Licitação** — edital, RTEP, análise de propostas, diálogo competitivo
7. ✅ **Due Diligence / M&A** — valorização, análise técnica, passivos ambientais, conformidade regulatória
8. ✅ **Encerramento / Descomissionamento** — plano de encerramento, reciclagem, remediação

---

## Ferramentas MCP

O agente acessa os seguintes conjuntos de ferramentas:

### Ferramentas principais
- **RAG — Coleção `aer:`** (base de conhecimento em Supabase)
  - ANAC/RBAC documentação completa
  - ICAO Annex 14 (aerodrome design standards)
  - FAA Advisory Circulars (AC) relacionadas
  - Editais BNDES/ANTAQ sobre aeroportos
  - NBR 12207 (aeronavegabilidade), NBR 15575 (desempenho de edifícios)
  - Estudos de caso de aeroportos brasileiros

- **MCP — SharePoint Agent** (acesso à pasta 03_Projetos/Aeroportos/*)
  - Leitura e upload de projetos, laudos, planilhas
  - Versionamento de arquivos

- **MCP — Supabase Vectorizer** (busca semântica sobre normas aeroportuárias)

### Ferramentas secundárias (conforme contexto)
- **SICRO Skill** — composições de preço para pavimentação aeroportuária
- **Cronograma Skill** — planejamento de execução de projetos aeroportuários
- **Modelagem Skill** — BIM/CAD para layouts de pista e pátio
- **Orçamento Skill** — elaboração de orçamentos base e detalhados
- **Contratual Skill** — análise de contratos, RTEP, cláusulas de operação

---

## Entrada e Roteamento

**Regra Maestro:**
```
IF menção a aeroporto | pista pouso | ANAC | ICAO | TPS | TECA | balizamento
   → agente-aeroportos (S7)
```

**Exemplos de prompt que ativam o agente:**
- "Preciso de projeto executivo para ampliação de pista em [Aeroporto X]"
- "Analisar conformidade com ANAC/RBAC 154"
- "Elaborar EVTEA para novo terminal de carga"
- "Descrever sistema de balizamento e iluminação conforme ICAO Annex 14"
- "Orçamento para pavimentação de TPS — aeroporto Congonhas"
- "Plano de manutenção para pavimento rígido de pista"
- "Due diligence técnica — M&A de concessão aeroportuária"

---

## Arquitetura RAG

**Coleção:** `aer:` (em Supabase `rag_chunks`)

**Documentos de referência (gerenciados em `refs/`):**

| ID Documento | Tipo | Cobertura | Observação |
|--------------|------|-----------|-----------|
| ANAC-RBAC-154-v2 | Norma | Projeto de aeródromos | Padrão regulador Brasil |
| ICAO-Annex-14-8ed | Padrão | Design e operação de aeródromos | Referência técnica internacional |
| FAA-AC-150-5300-13C | Advisory | Design de pistas e taxiways | Prática americana |
| NBR-12207-2016 | Norma | Aeronavegabilidade | Sinalização, comunicação |
| NBR-15575-2021 | Norma | Desempenho de edifícios | Terminal de passageiros |
| NBR-10844-2021 | Norma | Drenagem de água de chuva | Pistas e pátios |
| NBR-9050-2020 | Norma | Acessibilidade | Terminal (público geral) |
| Lei-13-182-2015 | Lei | Concessões de aeroportos | Marco regulador |
| BNDES-EDITAL-2025-AER | Edital | Financiamento de expansões | Requisitos econômicos |
| ANTAQ-NORMATIVA-S7 | Regulamento | Operação de aeroportos | Conformidade operacional |

**Fontes externas para sincronização:**
- Site ANAC (anac.gov.br/regulacoes)
- ICAO Document Store
- FAA Advisory Circulars
- Repositório ABNT (NBR vigentes)
- Editais BNDES/FINEP
- Portal de transparência de concessões aeroportuárias

---

## Estrutura SharePoint

**Pasta principal:**
```
04_IA/Manta-Maestro/01-agentes-fundamentais/agente-aeroportos/
├── SKILL.md                              (este arquivo)
├── README.md                             (onboarding de uso)
├── CHANGELOG.md                          (histórico de versões)
├── refs/
│   ├── ANAC-RBAC-154-v2.pdf             (norma ANAC)
│   ├── ICAO-Annex-14-8ed.pdf            (padrão ICAO)
│   ├── FAA-AC-150-5300-13C.pdf          (advisory FAA)
│   ├── NBR-12207-2016.pdf               (aeronavegabilidade)
│   ├── NBR-15575-2021.pdf               (desempenho edifícios)
│   ├── NBR-10844-2021.pdf               (drenagem)
│   ├── NBR-9050-2020.pdf                (acessibilidade)
│   ├── Lei-13-182-2015.pdf              (concessões aeroportos)
│   ├── BNDES-EDITAL-2025-AER.pdf        (financiamento)
│   └── ANTAQ-NORMATIVA-S7.pdf           (operação)
└── exemplos/
    ├── exemplo-evtea-aeroporto.pdf      (case EVTEA)
    ├── exemplo-projeto-executivo.pdf    (case Projeto Executivo)
    └── exemplo-contrato-concessao.docx  (template contrato)

03_Projetos/Aeroportos/
├── [Aeroporto Regional A]/
│   ├── EVTEA/
│   ├── Projetos/
│   ├── Orçamentos/
│   ├── Cronogramas/
│   └── Licitações/
├── [Aeroporto Regional B]/
│   └── (idem)
├── [Ampliações TPS-TECA]/
│   ├── CAD/
│   ├── Calculo/
│   └── Laudos/
└── Modelos-templates/
    ├── Template-EVTEA-Aeroportos.xlsx
    ├── Template-Orçamento-TPS.xlsx
    └── Template-Cronograma-Aeroportuário.mpp
```

---

## Histórico de versão

| Versão | Data | Alteração | Autor |
|--------|------|-----------|-------|
| 1.0 | 2026-07-05 | Criação inicial (v4.2 Codex) | Manta Maestro |

---

## Contato

**Responsável técnico:** Maurício Neves (mneves@mantaassociados.com)  
**Suporte Maestro:** routing@mantaassociados.com  
**Ticket de criação:** MNT-2026-UPGRADE-AGENTS-S6S10
