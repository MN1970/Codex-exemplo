# Agent Library — Manta 03-S8 Saneamento (agente-saneamento) — PRIORIDADE AySA

Agente vertical **Saneamento** (Sonnet). Cobre água (ETA, adutora,
distribuição), esgoto (coleta, ETE, disposição), drenagem urbana, resíduos.
**Prioridade AySA** (projeto Argentina). Consumidor natural do bloco B7 do
MASTER-CATALOG (7 KEs sobre privatização, EPANET, marco NMLSB).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Saneamento/{obra}/`                                    | Raiz — L+E                                     |
| `03_Projetos/Saneamento/AySA/`                                      | Projeto AySA — pasta dedicada, prioridade      |
| `03_Projetos/Saneamento/{obra}/02_Projeto/{ETA,ETE,Rede}/`          | Disciplinas — L+E                              |
| `04_IA/Manta-Maestro/Modelos/Saneamento/`                           | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B7/`                                     | KEs saneamento                                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| SAN-M-001   | Modelo hidráulico EPANET — rede de distribuição            | KE-015 (UFAL Piaçabuçu)         |
| SAN-M-002   | Análise regulatória Lei 14.026/2020 (NMLSB)                | KE-043 + KE-024                 |
| SAN-M-003   | Estudo tarifário pré/pós privatização                     | KE-045 + KE-046                 |
| SAN-M-004   | Business case AySA — comparativo com casos BR             | KE-024 + KE-044 + KE-047        |
| SAN-M-005   | Projeto executivo ETE — MBR / UASB / lodo ativado          | NBR 12211-12218                 |

## 3. Knowledge Elements (7 KEs no pgvector)

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-015 | metodo       | Pipeline GIS + EPANET 2.0 — replicável para AySA              |
| KE-024 | benchmark    | Diff-in-diff 3.536 municípios (privatização impacto)          |
| KE-043 | benchmark    | Pós-NMLSB — desenho contratual determina universalização      |
| KE-044 | case_study   | SNIS público × privado (perdas, eficiência, cobertura)        |
| KE-045 | case_study   | 4 casos BR (Limeira, Prolagos, Juturnaíba, Petrópolis)        |
| KE-046 | parametro    | Evolução tarifária pré/pós — benchmark direto p/ AySA         |
| KE-047 | case_study   | Iguá/CEDAE RJ — contraponto (riscos sem regulação)            |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '03-S8' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `saneamento.epanet_build` — monta modelo EPANET a partir de GIS (KE-015)
- `saneamento.tarifa_scenario` — cenários tarifários usando KE-046
- `saneamento.privatization_analysis` — usa KE-024/043/044/045/047 como panorama
- `saneamento.mbr_uasb_dim` — dimensionamento ETE (SAN-M-005)

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Estudo AySA — nova fase                              | Saneamento/AySA                   | SAN-M-004 + fan-out 15 + 06                       |
| Projeto de rede de distribuição                      | 02_Projeto/Rede                   | SAN-M-001 + calibração hidráulica                 |
| Estudo de outorga/concessão saneamento               | 12_Advisory + Saneamento          | SAN-M-002 + SAN-M-003 + parecer 15                |
| Projeto ETE                                          | 02_Projeto/ETE                    | SAN-M-005 + orçamento (handoff 05)                |

Handoff frequente: **15 Advisory** (contexto regulatório NMLSB), **06 Modelagem**
(FCM de concessão), **05 Orçamento**, **07 Cronograma**.
