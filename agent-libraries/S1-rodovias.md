# Agent Library — Manta 03-S1 Rodovias (agente-infraestrutura S1)

Agente vertical **Rodovias** (Sonnet). Cobre estudo prévio → obra → O&M em
rodovias federais/estaduais/vicinais. Consumidor natural do bloco B1
(terraplenagem/mass-haul) + B3 (SICRO composição) do MASTER-CATALOG.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Rodovias/{obra}/`                                      | Raiz do projeto — L+E                          |
| `03_Projetos/Rodovias/{obra}/02_Projeto/{Geometrico,Terraplenagem,Pavimentacao,Drenagem}/` | Disciplinas técnicas |
| `04_IA/Manta-Maestro/Modelos/Rodovias/`                             | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B1/`                                     | KEs terraplenagem/mass-haul                    |
| `04_IA/Bases/SICRO/`, `DNIT/`                                       | Bases oficiais — só leitura                    |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| RDV-M-001   | Projeto geométrico — memorial (classe I-D DNIT)           | Manual DNIT 706/2010            |
| RDV-M-002   | Terraplenagem — quadro de distribuição de terra (Brückner) | KE-007 + KE-052                |
| RDV-M-003   | Pavimentação — dimensionamento MePDG / DNIT               | DNIT PRO 269/94                 |
| RDV-M-004   | Drenagem — dimensionamento OAC/OGC                        | DNIT IPR 724/2006               |
| RDV-M-005   | Sinalização vertical + horizontal — cadastro              | CONTRAN R 236                   |

## 3. Knowledge Elements (9 KEs no pgvector)

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-001 | metodo       | MILP terraplenagem+pavimentação+haul (121 cortes/257 aterros) |
| KE-002 | benchmark    | Mapping 72 papers earthwork optimization                      |
| KE-007 | metodo       | Extensão Brückner com condicionantes geotécnicas              |
| KE-008 | parametro    | Custos equipamentos transporte por tipologia                  |
| KE-021 | benchmark    | Mapping 5785→71 papers — LP/MILP/GA dominantes                |
| KE-022 | metodo       | GIS-based allocation com múltiplos haul roads                 |
| KE-027 | metodo       | Pipeline SICRO composição + BDI diferenciado                  |
| KE-028 | parametro    | Fator conversão + IS 44/2021                                  |
| KE-052 | metodo       | Algoritmo balanceamento mass-haul (Nassar 2011)               |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '03-S1' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `rodovias.geometrico_check` — verifica classe DNIT vs raios/rampas
- `rodovias.terraplenagem_mh` — Brückner + MILP (KE-001, KE-052)
- `rodovias.pavimentacao_dim` — MePDG a partir de N + CBR
- `rodovias.drenagem_ogc` — dimensiona OGC/OAC por bacia
- `rodovias.orcamento_sicro` — handoff com 05 usando KE-027

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Estudo prévio (Q2=A)                                 | 02_Projeto/*                      | Memoriais preliminares + orçamento (fan-out 05)    |
| Projeto básico/executivo (Q2=B/C)                    | 02_Projeto/*                      | RDV-M-001..005 preenchidos                        |
| Obra em execução (Q2=D)                              | 03-04 acompanhamento              | Handoff 07 (cronograma) + 05 (medição) paralelo   |
| Concessão rodoviária (DD)                            | 12_Advisory                       | Fan-out S1 + 15 + 06 + 02                         |

Handoff frequente: **05 Orçamento** (SICRO), **07 Cronograma**, **04
Imobiliário** (faixa de domínio), **S2 OAE** (pontes na rodovia).
