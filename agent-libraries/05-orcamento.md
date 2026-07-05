# Agent Library — Manta 05 Orçamento (manta-05)

Referência canônica de trabalho do agente **Orçamento** (Sonnet, tier default).
Se o `.claude/agents/agente-orcamento.md` é o **como o agente pensa**, este
arquivo é o **com o que o agente trabalha**.

**Escopo:** composição de custos (SICRO/SINAPI/TPU), CHP/CHI de equipamentos,
BDI diferenciado, EVM para acompanhamento. Atende principalmente **03-S1
Rodovias**, mas é chamado por todos os segmentos.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/05_Orcamento/`                       | Planilha orçamentária ativa — leitura+escrita  |
| `03_Projetos/{segmento}/{obra}/05_Orcamento/BDI/`                   | Memórias de BDI por faixa — leitura+escrita    |
| `03_Projetos/{segmento}/{obra}/05_Orcamento/Composicoes/`           | Composições customizadas — leitura+escrita     |
| `04_IA/Manta-Maestro/Modelos/Orcamento/`                            | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B1/`, `B3/`, `B4/`                       | PDFs dos KEs — só leitura                      |
| `04_IA/Bases/SICRO/`, `SINAPI/`, `TPU/`                             | Bases de referência mensais — só leitura       |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                              | Origem                          |
|-------------|--------------------------------------------------------|---------------------------------|
| ORC-M-001   | Planilha orçamentária — obra rodoviária SICRO           | Modelo Manta + KE-027           |
| ORC-M-002   | Memória de BDI diferenciado (5 faixas)                 | Decreto 7.983/2013 + KE-028     |
| ORC-M-003   | Composição CHP/CHI — equipamento pesado                 | SINAPI + KE-025/026             |
| ORC-M-004   | Comparativo SINAPI × SICRO — mesmo insumo               | Barreiros + KE-029              |
| ORC-M-005   | Curva S baseline + EVM (PV/EV/AC/CPI/SPI)               | Nature 2025 + KE-048/049        |

## 3. Knowledge Elements (12 KEs no pgvector)

Do `INDICE-KEs.md`, seção Orçamento (12 KEs · B1 + B3 + B4):

| KE     | Tipo         | Uso operacional                                         |
|--------|--------------|---------------------------------------------------------|
| KE-001 | metodo       | MILP terraplenagem+pavimentação+haul (com 05 aplicado)  |
| KE-002 | benchmark    | Mapping 72 papers earthwork optimization                 |
| KE-021 | benchmark    | Mapping 5785→71 papers — LP/MILP/GA                     |
| KE-025 | norma        | Manual SINAPI — CHP/CHI, encargos, aferição             |
| KE-026 | parametro    | Fórmulas CHP/CHI — depreciação, disponibilidade 1.25    |
| KE-027 | metodo       | Pipeline SICRO — composição + BDI + IS 44/2021           |
| KE-028 | parametro    | Fator conversão corte→solto + BDI faixas                 |
| KE-029 | benchmark    | SINAPI × SICRO — comparativo CHP                         |
| KE-048 | benchmark    | 3 técnicas EVM em 30 projetos (Egito) — benchmark        |
| KE-049 | metodo       | Framework seleção EVM por estágio                        |
| KE-050 | case_study   | EVM em obras reais Equador — VAC%=-3.24%                 |
| KE-051 | metodo       | ML + 19 métodos EAC — integrável com 16 pesquisador      |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '05' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `orcamento.compose_sicro` — busca item SICRO + monta composição no ORC-M-001
- `orcamento.bdi_calc` — calcula BDI diferenciado a partir do Decreto 7.983
- `orcamento.chp_chi` — gera CHP/CHI de equipamento (SINAPI ou SICRO)
- `orcamento.evm_snapshot` — calcula PV/EV/AC/CPI/SPI/EAC a partir do medido
- `orcamento.compare_bases` — SINAPI vs SICRO para mesmo insumo (ORC-M-004)

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Estudo prévio de obra (Q2=1) — precisa de estimativa | 05_Orcamento                      | ORC-M-001 preenchida com base + BDI justificado   |
| Preço novo em obra em execução (Q2=4)                | 05_Orcamento/Composicoes          | Composição customizada + parecer IS/DG 44/2021    |
| Medição mensal + acompanhamento de custo             | 05_Orcamento + 08_Cronograma      | ORC-M-005 (EVM) + curva S atualizada              |
| Diferença SINAPI × SICRO detectada                   | 05_Orcamento                      | ORC-M-004 preenchida + recomendação de escolha    |
| Handoff de 07 Cronograma (EVM cruzado)               | 08_Cronograma                     | Snapshot EVM + interpretação CPI/SPI              |

Handoff frequente: **03-S1 Rodovias** (base natural), **07 Cronograma** (EVM
integra as duas dimensões), **01 Claims** (composição para pleito de preço
novo), **16 Arquiteto-IA** (ML+EVM via KE-051).
