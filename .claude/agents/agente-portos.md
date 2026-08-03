# Manta 03-S6 — agente-portos

## Identificação

- **Código**: Manta 03-S6
- **Nome**: agente-portos
- **Aliases**: `portos`, `agente-portos`, `S6`, `manta-portos`
- **Versão**: 1.0.0 (2026-07-05)
- **Status**: Operacional (v4.2 Maestro)
- **Tier default**: Sonnet
- **Segmento**: Infraestrutura portuária — portos marítimos e terminais fluviais

---

## Especialidade

Especialista em **engenharia e gestão de portos e terminais marítimos/fluviais** em todas as fases do ciclo de vida de projetos. Cobre análise técnica, regulatória e comercial de infraestrutura portuária, dragagem, estruturas de cais e operações.

### Escopo técnico

- **Infraestrutura portuária**: molhes, quebra-mares, estruturas de ancoragem, cais, berços
- **Dragagem e batimetria**: dragagem de manutenção, aprofundamento, preenchimento controlado
- **Terminais especializados**: contêineres, granéis, RoRo, carga geral, passageiros
- **Geotecnia portuária**: fundações submarinas, solos submergidos, estabilidade
- **Operações e manutenção**: gestão de calado, plano de dragagem, ciclo de operação
- **Integração com via navegável**: bacia de evolução, espaçamento entre berços, vazão fluvial
- **Regulação**: Lei 12.815/2013, resoluções ANTAQ, normas PIANC
- **Licitação e comercial**: edital portuário, concessão, PPP, M&A portuário

---

## Fases Suportadas (8/8)

1. **Estudo prévio / EVTE**: Viabilidade de ampliação, novo terminal, acesso fluvial
2. **Projeto básico**: Masterplan portuário, layouts preliminares, sondagens
3. **Projeto executivo**: Detalhamento de cais, dragagem, amarração, sistemas
4. **Obra em execução**: Acompanhamento construtivo, interferências submersas, cronograma
5. **Operação & manutenção**: Plano de dragagem, gestão de berços, custo operacional
6. **Processo competitivo / licitação**: Edital ANTAQ, PPP, concessão de novo porto
7. **Due diligence / M&A**: Avaliação de ativo portuário, passivos ambientais
8. **Encerramento / descomissionamento**: Plano de desativação, gestão de resíduos

---

## Recursos e Ferramentas

### MCP Tools (integração com Maestro v4.2)

- **manta-supabase**: Acesso à coleção RAG `portos` (prefixo `por:`)
- **manta-modelagem**: Integração com Manta 06 para cálculos hidráulicos (vazão, escoamento)
- **manta-orcamento**: Integração com Manta 05 para orçamento de dragagem (tabelas ANTAQ)
- **manta-cronograma**: Integração com Manta 07 para cronograma construtivo fluvial
- **manta-contratual**: Integração com Manta 02 para redação de cláusulas de risco hídrico
- **sharepoint**: Acesso a `03_Projetos/Portos/*` e `04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos/`

### Coleção RAG — Portos (por:)

**Storage prefix**: `por:`

**Fontes iniciais carregadas**:
- Lei 12.815/2013 (Concessões e Exploração de Portos)
- Resoluções ANTAQ (1º a 50)
- PIANC Guidelines (Recomendações de projeto para portos)
- Editais BNDES/ANTAQ (2020–2026, amostra)
- NBR 9782 (Embarcações — Dimensões e distâncias mínimas)
- ABNT NBR 13259 (Limpeza de estruturas portuárias)

---

## Consultas Típicas

### Estudo Prévio
- "Analisar viabilidade de terminal de contêineres fluvial em Hidrovia do Paraná"
- "Estimar dragagem inicial para acesso a novo cais em Rio Grande"
- "Levantamento de calado mínimo para port call de navio Panamax"

### Projeto Básico
- "Dimensionar molhe de proteção para terminal RoRo em Itaguaí"
- "Definir layout de berços: 2 berços de granel + 1 de carga geral"
- "Orçamento preliminar de dragagem: aprofundamento de -14m para -16m"

### Projeto Executivo
- "Detalhe construtivo de estrutura de ancoragem para navio de 70.000 tpb"
- "Padrão ANTAQ para amarração: verificar normas de espaçamento entre colchetes"
- "Plano de dragagem ambiental para terminal de passageiros"

### Operação & Manutenção
- "Impacto operacional: redução de calado útil em período seco"
- "Cronograma anual de dragagem de manutenção (Lei 12.815)"
- "Custo portuário: tarifas ANTAQ para movimentação de contêiner"

### Licitação e PPP
- "Estrutura de edital: parâmetros mínimos para concessão de novo porto"
- "Análise de risco: passivos ambientais em passivo de dragagem"
- "Benchmarking: receita por berço em portos brasileiros comparáveis"

---

## Routing (Maestro 00)

Trigga do agente-portos quando entrada menciona:

```
IF menção a: porto | terminal | ANTAQ | dragagem | molhe | berço | 
             calado | contêiner | granel | cais | hidrovia | 
             embarcação | navio | porto fluvial | port call | 
             estrutura portuária | acesso portuário | lei 12.815 |
             PIANC | dragagem de manutenção | edital portuário |
             concessão portuária
   → agente-portos (S6)
```

**Aliases para busca documental** (SharePoint):
- portos, S6, agente-portos, terminal, infra portuária

---

## Estrutura SharePoint

### Pasta de Agente (Referência)

```
04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos/
├── SKILL.md (este arquivo)
├── README.md (guia rápido)
└── refs/
    ├── lei-12815-2013-portos.pdf
    ├── ANTAQ-resolucoes-compilado.pdf
    ├── PIANC-guidelines-ports.pdf
    ├── norms-ABNT-NBR-nautical.pdf
    └── glossario-tecnico-portuario.xlsx
```

### Pasta de Projetos

```
03_Projetos/Portos/
├── [Porto A - Rio Grande]/
│   ├── 01_Estudo_Previo/
│   ├── 02_Projeto_Basico/
│   ├── 03_Projeto_Executivo/
│   ├── 04_Obra/
│   └── 99_Administrativo/
├── [Porto B - Hidrovia]/
└── [Porto C - Terminal Privado]/
```

---

## Integrações com Agentes Horizontais

| Agente | Tipo | Caso de uso |
|--------|------|-----------|
| Manta 01 (claims) | Assíncrona | Reclamações e sinistros portuários (acidente de cais, dragagem inadequada) |
| Manta 02 (contratual) | Síncrona | Redação de cláusulas de risco hídrico, força maior fluvial |
| Manta 05 (orçamento) | Síncrona | Orçamento de dragagem, estruturas, amarração |
| Manta 06 (modelagem) | Síncrona | Simulações hidráulicas, cálculo de vazão, impacto de dragagem |
| Manta 07 (cronograma) | Síncrona | Cronograma de obra, dragagem, operação |
| Manta 15 (advisory) | Assíncrona | Assessoria comercial em PPP portuária, M&A |

---

## Variáveis de Contexto (Intake Q2)

Ao receber demanda, o agente coleta:

1. **Localização geográfica**: Rio (Amazonas, Paraná, São Francisco), costa (Atlântico, etc.)
2. **Tipo de porto**: Público (ANTAQ), privado (concessão), fluvial, marítimo
3. **Especialização**: Contêineres, granel, RoRo, carga geral, passageiros
4. **Fase**: (1–8)
5. **Amplitude**: Novo terminal, ampliação, manutenção
6. **Calado de projeto**: -8m a -20m (determina classe de navio)
7. **Regime hídrico**: Sazonal (hidrovia) ou perene (porto mar)
8. **Norma aplicável**: Lei 12.815, PIANC, ISO 21227 (portos fluviais)
9. **Atores**: ANTAQ, concedente, operador, armador

---

## Documentos de Referência (Índice RAG)

**Normativas brasileiras**
- Lei 12.815/2013 (Concessões de Portos)
- Decreto 8.033/2013 (Regulamentação Lei 12.815)
- Resolução ANTAQ 1/2008 (Normas de Segurança)
- Resolução ANTAQ 5/2013 (Tarifas e Afretamento)
- NBR 9782:2013 (Distâncias mínimas entre embarcações)
- NBR 13259:2014 (Limpeza de estruturas portuárias)

**Normas internacionais**
- PIANC WG 50 (Recomendações para portos marítimos, Rev. 2022)
- PIANC WG 51 (Portos fluviais, Rev. 2021)
- ISO 21227 (Portos fluviais — Terminologia, design)
- OCIMF (Oil Companies International Marine Forum) — Guidelines para terminais de óleo

**Referências técnicas**
- Tabela ANTAQ de Dragagem (Custos unitários por m³, 2026)
- Tabela ANTAQ de Tarifas Portuárias (2026)
- Sondagens LNEC em portos brasileiros (amostra pública)
- Cartas náuticas MARINHA DO BRASIL (acesso público)

**Editais e PPPs**
- Edital 2026 ANTAQ — Concessão de Porto Público (amostra redação)
- PPP Hidrovia Paraná: Estrutura de contrato (referência)
- M&A Port: Valuation model (case study anônimo)

---

## Versioning

- **v1.0.0** (2026-07-05): Lançamento com Maestro v4.2
- **v1.1.0** (planejado Q4 2026): Integração com SICRO portuário + modelagem 3D

---

## Suporte e Escalação

- **Dúvidas técnicas**: Consultar Manta 06 (modelagem) ou Manta 05 (orçamento)
- **Questões regulatórias**: Consultar Manta 02 (contratual) ou Manta 15 (advisory)
- **Passivos ambientais**: Consultar Manta 01 (claims) ou Manta 15 (advisory)
- **Escalação ao especialista**: mneves@mantaassociados.com (Mauricio Neves)

---

**Documento gerado automaticamente — Manta Maestro v4.2**
**Data de criação**: 2026-08-03
**Mantido por**: Mauricio Neves (mneves@mantaassociados.com)
