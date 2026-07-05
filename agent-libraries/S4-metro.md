# Agent Library — Manta 03-S4 Metrô (agente-infraestrutura S4)

Agente vertical **Metrô / VLT** (Sonnet). Cobre TBM/EPB, NATM, estações,
PSDs, sistemas metroferroviários. Consumidor natural do bloco B6 do
MASTER-CATALOG.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Metro/{obra}/02_Projeto/{Tunel,Estacao,Sistemas}/`     | Projeto executivo — L+E                        |
| `03_Projetos/Metro/{obra}/06_Instrumentacao/`                       | Marcos superficiais, tassômetros — L+E         |
| `04_IA/Manta-Maestro/Modelos/Metro/`                                | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B6/`                                     | KEs metrô/túneis                               |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| MTR-M-001   | Memorial FEM Plaxis 2D — TBM/EPB                          | KE-003 + KE-004                 |
| MTR-M-002   | Retroanálise NATM Plaxis + Hoek-Brown                     | KE-009 + KE-010                 |
| MTR-M-003   | Programa de instrumentação — marcos + tassômetros         | KE-023 (L2-Verde SP)            |
| MTR-M-004   | Estação com PSD — projeto arquitetônico+estrutural         | Modelo Manta                    |

## 3. Knowledge Elements (5 KEs no pgvector)

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-003 | metodo       | Diretrizes FEM Plaxis 2D — TBM/EPB, MC vs HS, revestimento    |
| KE-004 | parametro    | Hardening Soil para solos SP — E50/Eur/m                      |
| KE-009 | metodo       | Retroanálise NATM Plaxis + Hoek-Brown + RMR                   |
| KE-010 | case_study   | Túnel A4 Porto/Amarante — monitorização real                  |
| KE-023 | case_study   | Recalques TBM L2-Verde Metrô SP 2024 — benchmark direto       |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '03-S4' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `metro.fem_plaxis_tbm` — setup Plaxis 2D com KE-003/004
- `metro.natm_retroanalise` — retroanálise NATM (KE-009)
- `metro.instrumentacao_plan` — plano de monitorização (KE-023)
- `metro.recalque_predict` — previsão de recalques via HS + benchmark L2-V

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Projeto executivo túnel TBM (Q2=C)                   | 02_Projeto/Tunel                  | MTR-M-001 + parâmetros HS calibrados              |
| NATM em maciço rochoso                               | 02_Projeto/Tunel                  | MTR-M-002 + programa de faseamento                |
| Obra em execução — recalques observados vs previstos | 06_Instrumentacao                 | MTR-M-003 + análise de conformidade               |
| DD/M&A de concessão metroviária                      | 12_Advisory                       | Fan-out S4 + 15 + 06                              |

Handoff frequente: **05 Orçamento**, **07 Cronograma**, **S2 OAE** (túnel
rodoviário com abordagem similar), **15 Advisory**.
