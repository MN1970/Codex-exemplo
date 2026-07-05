# Agent Library — Manta 01 Claims (02-C, manta-claims)

Referência canônica de trabalho do agente **Claims** (Opus, tier default).
Se o `.claude/agents/agente-claims.md` é o **como o agente pensa** (system
prompt), este arquivo é o **com o que o agente trabalha**: pastas SP canônicas,
documentos-modelo, KEs indexadas no pgvector, skills registradas, e os padrões
de acionamento.

- **Formato:** 5 seções fixas — replicáveis para os outros 10 horizontais.
- **Fonte da verdade dos KEs:** [`academic-ingestor/MASTER-CATALOG.json`](../academic-ingestor/MASTER-CATALOG.json) via `knowledge_extractions` no Supabase `manta-maestro`.
- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

Rotas do `sp_agent_routing` que o agente lê/escreve por padrão:

| Rota SP                                                         | Uso                                                                  |
|-----------------------------------------------------------------|----------------------------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/09_Pleitos/`                     | Pleitos ativos por obra — leitura+escrita                            |
| `03_Projetos/{segmento}/{obra}/03_Contratos/`                   | Contrato-mãe e aditivos — só leitura                                 |
| `03_Projetos/{segmento}/{obra}/08_Cronograma/`                  | Baseline + as-built para TIA / Measured Mile — só leitura            |
| `04_IA/Manta-Maestro/Modelos/Claims/`                           | Documentos-modelo (item 2) — só leitura                              |
| `04_IA/Manta-Maestro/Teses/{B2,B5}/`                            | PDFs originais dos KEs (item 3) — só leitura                         |

## 2. Documentos-modelo (starter kit)

Templates curados. Pilotar sempre a partir daqui — nunca de projeto anterior.

| ID          | Documento                                       | Origem                          |
|-------------|--------------------------------------------------|---------------------------------|
| CLM-M-001   | Carta de notificação de pleito (5 dias / EPC)   | Modelo Manta 2024               |
| CLM-M-002   | Memória de cálculo TIA — retrospectiva          | AACE RP 29R-03 + KE-016         |
| CLM-M-003   | Memória de cálculo Measured Mile                 | Spire 2021 + KE-018             |
| CLM-M-004   | Requerimento de reequilíbrio (ANTT 5.850/2019)  | UNB 2021 + KE-035               |
| CLM-M-005   | Parecer TCU / TCE-MG — matriz de riscos          | TCE-MG 2023 + KE-038            |

> **Curadoria:** Maurício revisa a cada 6 meses. Item marcado como *deprecated* na coluna origem sai do índice.

## 3. Knowledge Elements (10 KEs no pgvector)

Do `INDICE-KEs.md`, seção Claims (10 KEs · B2 + B5):

| KE     | Tipo         | Uso operacional                                         |
|--------|--------------|---------------------------------------------------------|
| KE-016 | metodo       | TIA prospectiva vs retrospectiva (MIP 3.3-3.7)          |
| KE-017 | benchmark    | Tabela comparativa 5 técnicas delay (quando usar cada)  |
| KE-018 | metodo       | Measured Mile — pipeline 5 etapas + fórmulas            |
| KE-019 | case_study   | MM em power plant (piping) — referência de laudo        |
| KE-020 | benchmark    | AACE 25R-03 — 25 causas de perda de produtividade       |
| KE-034 | case_study   | Pedidos de revisão extraordinária ANTT — gatilhos       |
| KE-035 | norma        | Resolução ANTT 5.850/2019 — FCM                         |
| KE-036 | metodo       | EEF Lei 8.987/95 — matriz de riscos + Fator D           |
| KE-037 | metodo       | Procrofe fases I-III — desconto de reequilíbrio         |
| KE-038 | norma        | TCE-MG — 11 parâmetros para conceder reequilíbrio       |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '01' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

Registradas no skill catalog (a preencher quando o registro estiver publicado):

- `claims.notify_delay` — gera CLM-M-001 preenchida a partir do baseline vs as-built
- `claims.tia_retrospective` — executa TIA a partir de dois cronogramas
- `claims.measured_mile` — pipeline MM a partir de curva de produtividade
- `claims.reequilibrio_pack` — monta requerimento ANTT com KE-035/037/038 como anexos

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                              | Rota                                        | Saída esperada                                    |
|------------------------------------------------------|---------------------------------------------|---------------------------------------------------|
| Cliente notifica atraso ≥5 dias                      | 09_Pleitos/{obra}                           | CLM-M-001 preenchida + parecer sobre nexo         |
| Solicitação de análise de disruption                 | 09_Pleitos/{obra}                           | CLM-M-003 + gráfico de produtividade + laudo      |
| Pedido de revisão extraordinária em concessão        | 03_Contratos + 09_Pleitos                   | CLM-M-004 + FCM anexo + parecer TCU/TCE-MG        |
| Auditoria retrospectiva de cronograma                 | 08_Cronograma + 09_Pleitos                  | CLM-M-002 + relatório MIP 3.3-3.7                 |

Handoff frequente: **02-C Contratual** (para revisão de cláusulas) e **15 Advisory** (para pareceres para stakeholders externos).
