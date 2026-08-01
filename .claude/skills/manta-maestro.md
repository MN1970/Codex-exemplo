# Manta Maestro Skill — Integração Claude AI + Cowork

**Versão**: v5.0.1  
**Data**: 31 de julho de 2026  
**Compatibilidade**: Claude AI web, Claude Code, Cowork  
**Status**: 🚀 Operacional

---

## O que é Manta Maestro?

Manta Maestro é um **multi-agent architecture** especializado em infraestrutura de engenharia civil. Fornece acesso a:

- **23 agentes especializados** (11 horizontais + 12 verticais)
- **4 eixos ortogonais** (Segmentos, Atividades, Funcionais, Disciplinas)
- **9 coleções RAG** com 204 chunks de conhecimento específico
- **Roteamento inteligente** baseado em keywords e contexto

---

## Quando Usar

### ✅ USE quando:
- Perguntar sobre infraestrutura: rodovias, portos, ferrovias, metrô, saneamento, energia, barragens, aeroportos
- Precisar de análise de orçamento, cronograma, contratual, claims
- Consultar normas técnicas (ABNT, NBR, ANEEL, ANAC, ANTAQ)
- Solicitar quantidades, cronogramas, modelagem financeira
- Questões de regulatório, riscos, advisory

### ❌ NÃO USE quando:
- Tarefas genéricas (use Claude direto)
- Conteúdo não relacionado a infraestrutura
- Solicitar criação de código (use outros agents)

---

## Como Usar

### No Claude AI Web

```
Mencione qualquer palavra-chave relevante:
"Quero analisar o orçamento de uma rodovia no Mato Grosso"
"Projeto de refinaria: HAZOP e custos"
"ETA e ETE para AySA Argentina"
"Linha de transmissão ANEEL: estudos prévios"
"Barragem de rejeitos: estrutural e risco"
```

O Maestro roteia automaticamente para o agente especializado.

### No Claude Code

```bash
# Ver status do Maestro
claude manta status

# Listar agentes disponíveis
claude manta agents list

# Consultar agente específico
claude manta query "pergunta aqui" --segment portos
```

### No Cowork (Microsoft 365)

```
Teams/Slack mention:
@manta-maestro "análise de S8-saneamento para projeto AySA"

SharePoint integration:
- Agentes em /Skills/
- Documentação em /Arquitetura/
- Referências técnicas em /RAG-Collections/
```

---

## Roteamento de Segmentos

| Menção | Agente | Exemplos |
|--------|--------|----------|
| rodovia, pavimento, DNIT, SICRO | agente-infraestrutura S1 | "Projeto de rodovia" |
| ponte, viaduto, OAE, NBR 7187 | agente-infraestrutura S2 | "Viaduto urbano" |
| ferrovia, trilho, via permanente | agente-infraestrutura S3 | "Projeto ferroviário" |
| metrô, estação, NATM, VLT | agente-infraestrutura S4 | "Linha 4 do metrô" |
| porto, terminal, ANTAQ, dragagem | agente-portos | "Terminal de contêineres" |
| aeroporto, pista, ANAC, TPS | agente-aeroportos | "Ampliação de aeroporto" |
| saneamento, ETA, ETE, AySA | agente-saneamento | "Projeto AySA Argentina" |
| energia, transmissão, ANEEL | agente-energia | "Leilão de LT" |
| barragem, vertedouro, rejeitos | agente-barragens | "TSF de ouro" |
| petróleo, gasoduto, refinaria | agente-oleo-gas | "Oleoduto costeiro" |
| edificação, galpão, BIM, LEED | agente-edificacoes | "Data center em SP" |
| mineração, lavra, NRM | agente-mineracao | "Projeto de ferro" |

---

## Atividades Disponíveis

| Atividade | Agente | Use quando |
|-----------|--------|-----------|
| Proposta (A1) | Manta 13-14 | Estruturar proposta comercial |
| Quantidades (A2) | Vertical + skills | Calcular takeoff |
| Orçamento (A3) | Manta 05 | Estimativa de custos |
| Modelagem (A4) | Manta 06 | Análise financeira |
| Cronograma (A5) | Manta 07 | Planejamento temporal |
| Contratual (A6) | Manta 02 | Termos e condições |
| Claims (A7) | Manta 01 | Disputas e reclamações |
| Advisory (A8) | Manta 15 | Consultoria estratégica |
| Regulatório (A9) | Manta-09 | Compliance e licenças |
| Risco (A10) | Manta-10 | Análise de riscos |

---

## Disciplinas de Engenharia

| Disciplina | Normas | Use quando |
|------------|--------|-----------|
| Hidráulica (D01) | NBR 10844, ABNT | Drenagem, vazões |
| Estrutural (D02) | NBR 6118, 6120 | Verificação estrutural |
| Geotecnia (D03) | NBR 7175, 8682 | Fundações, estabilidade |
| Pavimentação (D04) | DNIT, SICRO | Camadas asfálticas |
| Elétrica (D05) | NBR 5422, IEC | Subestações, cabos |
| Ambiental (D06) | Lei 6938, CONAMA | Licenças, impactos |
| Econômica (D07) | SICRO, INPC | Custos, indexadores |
| Planejamento (D08) | PMI, MS Project | Cronograma, marcos |
| Jurídico (D09) | Lei 8.666, 13.303 | Contratos, licitação |
| Comercial (D10) | INCOTERMS | Negociação, preços |

---

## SharePoint Integration

Arquivos do Maestro estão em:

```
/Manta Associados
├── /Skills/
│   ├── /Óleo & Gás/ → agente-oleo-gas.md
│   ├── /Edificações/ → agente-edificacoes.md
│   ├── /Saneamento/ → agente-saneamento.md
│   ├── /Energia/ → agente-energia.md
│   ├── /Portos/ → agente-portos.md
│   ├── /Aeroportos/ → agente-aeroportos.md
│   └── /Barragens/ → agente-barragens.md
├── /Arquitetura/
│   ├── ARQUITETURA-AGENTES-IA.md (v3.0.0)
│   ├── ATIVIDADES-A1-A10.md
│   ├── FUNCIONAIS-F1-F8.md
│   └── DISCIPLINAS-D01-D20.md
├── /RAG-Collections/
│   ├── Rodovias/ (20 chunks)
│   ├── Portos/ (18 chunks)
│   ├── Saneamento/ (24 chunks)
│   ├── Energia/ (30 chunks)
│   └── [9 coleções total, 204 chunks]
└── /Documentação/
    ├── CLAUDE.md (master registry)
    ├── Planejamento-Evolucao-v5.0.1.md
    └── Deploy-Checklist.md
```

---

## RAG (Retrieval-Augmented Generation)

Ao consultar, o Maestro acessa automaticamente:

- **Normativas**: ABNT NBR, ANEEL R1-R5, ANAC RBAC, ANP Edital
- **Documentação técnica**: Cálculos, exemplos, estudos de caso
- **Custos**: SICRO, DNIT preços, tabelas de referência
- **Jurídico**: Lei 8.666, Lei 13.303, leis específicas por setor

Latência de recuperação: < 500ms

---

## Modelo de Operação

```
Pergunta do usuário
    ↓
Maestro Router (Manta 00) — triagem com Haiku
    ↓
Match keywords → Agente vertical (Sonnet)
    ↓
Consulta RAG por segmento
    ↓
Resposta especializada
    ↓
Se complexo → escala para Opus
```

---

## Exemplo de Uso Prático

### Pergunta
```
"Estou estruturando a proposta para uma ETA de 50 ML/dia 
para o projeto AySA em Buenos Aires. Preciso de orçamento, 
cronograma, normas aplicáveis e matriz de riscos."
```

### Roteamento
```
Keywords detectadas: AySA, ETA, saneamento, orçamento, cronograma, risco
Agente primário: agente-saneamento (S8)
Handoffs: Manta 05 (orçamento), Manta 07 (cronograma), Manta-10 (risco)
RAG ativado: san:ar:* (saneamento Argentina), normas IWA + ERAS
```

### Resposta Integrada
```
[agente-saneamento faz contexto]
"Para uma ETA de 50 ML/dia em Buenos Aires, seguindo ERAS/AySA..."

[Manta 05 fornece orçamento]
"Estimativa de custos por componente (SICRO + Argentina pricing)..."

[Manta 07 fornece cronograma]
"Fases: Projeto básico (3m), Executivo (2m), Obra (12m)..."

[Manta-10 fornece riscos]
"Matriz: Política (alta), Técnica (média), Ambiental (média)..."
```

---

## Cowork Integration

### Teams/Slack Mentions

```
@manta-maestro "análise de barragem"
→ Ativa agente-barragens
→ Publica resultado em thread

@manta-maestro S1 "orçamento rodovia PR"
→ Força roteamento para agente-infraestrutura S1
→ Integra com Manta 05
```

### SharePoint Sync

```
Arquivo novo em /Manta/RAG-Collections/Portos/ + *.pdf
    ↓
MCP detecta via indexação automática
    ↓
Ingestão em 24h para agente-portos
    ↓
Disponível em próximas consultas
```

### OneNote Integration

```
Criar caderno "Projeto [Nome]" com:
- Segmento, Atividades, Disciplinas associadas
- Link para agente Maestro relevante
- Histórico de consultas (rastreável)
```

---

## Limitações & Fallbacks

### Quando Maestro não consegue responder:

1. **Fora do escopo**: Ativa busca web ou escalação para Manta 15
2. **Dado incompleto**: Solicita clarificação com opções S.A.D
3. **Norma não em RAG**: Busca em base oficial (ABNT, ANEEL) com disclaimer
4. **Emergência**: Escala para Opus para segunda opinião

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| "Não entendi o segmento" | Use keyword: "rodovia", "porto", "energia" etc. |
| Resposta genérica | Seja mais específico: setor, norma, fase do projeto |
| RAG fora de data | Atualizar docs no SharePoint; re-sync em 24h |
| Preciso de código | Use agente diferente; Maestro foca análise técnica |
| Urgência máxima | Mencione "CRÍTICO" para escalação automática Opus |

---

## Suporte

- **Documentação**: `/Manta/Arquitetura/`
- **Issues técnicas**: #manta-architect (Slack/Teams)
- **Feature requests**: JIRA/Azure DevOps ticket
- **Escalação**: Manta 15 (Advisory)

---

**Skill Status**: ✅ ATIVO  
**Última atualização**: 2026-08-01  
**Próxima versão**: v5.1 (Fase 2 — Manta-09 + S11)

