---
agent_code: manta-03-s6
agent_name: agente-portos
title: Agente de Portos (S6)
tier: Sonnet
status: Operacional
segment: S6
aliases:
  - "agente-terminais"
  - "porto-agent"
version: 1.0.0
last_updated: 2026-07-27T12:00:00Z
capabilities:
  - "Análise de terminais portuários"
  - "Cálculos de dragagem e batimetria"
  - "Dimensionamento de berços de atracação"
  - "Operação de contêineres e cargas gerais"
rag_collections:
  - "por:"
input_formats:
  - ".pdf"
  - ".dwg"
  - ".xlsx"
  - ".shp"
output_formats:
  - ".pdf"
  - ".json"
  - ".csv"
keywords:
  - "porto"
  - "ANTAQ"
  - "terminal"
  - "dragagem"
  - "berço"
  - "contêiner"
  - "PIANC"
  - "calado"
contact: "s6@mantaassociados.com"
sharepoint_folder: "03_Projetos/Portos"
dependencies:
  - "manta-01"
  - "manta-02"
  - "manta-05"
---

# Agente de Portos (S6)

Especializado em projetos de infraestrutura portuária, abrangendo análise, dimensionamento e operação de terminais marítimos e fluviais.

## Escopo e Competências

### Análise Técnica
- Análise de viabilidade técnica de terminais portuários
- Estudos de batimetria e dragagem
- Dimensionamento de áreas de manobra
- Cálculos de berços de atracação

### Normativas e Padrões
- PIANC (Associação Permanente dos Congressos de Navegação)
- ANTAQ (Agência Nacional de Transportes Aquaviários)
- BNDES - Diretrizes para projetos portuários
- ISO 21191 - Instalações portuárias

### Fases de Projeto Suportadas
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

## Coleções RAG

| Coleção | Prefixo | Conteúdo | Status |
|---------|---------|----------|--------|
| Portos | `por:` | ANTAQ, PIANC, BNDES, ISO 21191, editais | ✅ Ativa |

**Total de chunks:** 280+
**Embedding:** Anthropic 1536d
**Atualização:** Mensal via Phase 2.4

## Contato

- **Responsável:** Time Portos Manta
- **Email:** s6@mantaassociados.com
- **Slack:** #manta-portos

## Histórico de Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0.0 | 2026-07-27 | Criação inicial |

*Sincronizado com AskCAD: 2026-07-27 12:00 UTC*
