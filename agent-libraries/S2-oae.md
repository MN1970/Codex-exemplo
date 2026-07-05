# Agent Library — Manta 03-S2 OAE (agente-infraestrutura S2)

Agente vertical **OAE (Obras de Arte Especiais)** — pontes, viadutos, túneis
rodoviários. Cobre estudo prévio → obra → O&M + inspeção NBR 9452 / DNIT 010-PRO
/ GDE-UnB. Consumidor natural do bloco B8 do MASTER-CATALOG.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/OAE/{obra}/02_Projeto/{Estrutura,Fundacoes,Superestrutura}/` | Projeto estrutural — L+E                 |
| `03_Projetos/OAE/{obra}/05_Inspecao/`                               | Laudos de inspeção — L+E                       |
| `04_IA/Manta-Maestro/Modelos/OAE/`                                  | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B8/`                                     | KEs de OAE                                     |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| OAE-M-001   | Memorial de cálculo estrutural — viaduto viga contínua    | NBR 7187 + KE-005/006           |
| OAE-M-002   | Laudo de inspeção rotineira — NBR 9452                    | ABNT NBR 9452                   |
| OAE-M-003   | Laudo de inspeção — DNIT 010-PRO                          | DNIT 010-PRO/2004               |
| OAE-M-004   | Laudo de inspeção — GDE/UnB (ponderações)                 | KE-042                          |
| OAE-M-005   | Plano de recuperação — orçamento com custos Ecovias        | KE-041                          |

## 3. Knowledge Elements (5 KEs no pgvector)

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-005 | metodo       | Monte Carlo contra flecha em balanço sucessivo                |
| KE-006 | formula      | Fluência estocástica CEB-FIP/NBR 6118                         |
| KE-040 | metodo       | Metodologia inspeção OAE (gravidade/extensão/intensidade)     |
| KE-041 | benchmark    | Custos reais recuperação 332 OAEs (Ecovias/Autopistas)        |
| KE-042 | benchmark    | Comparativo NBR 9452 × DNIT 010-PRO × GDE/UnB                 |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '03-S2' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `oae.contraflecha_mc` — Monte Carlo para contra flecha (KE-005)
- `oae.fluencia_ceb` — estimativa de fluência com incerteza (KE-006)
- `oae.inspecao_score` — classifica dano NBR 9452 ou GDE/UnB
- `oae.custo_recuperacao` — estimativa a partir da base Ecovias (KE-041)

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Projeto de OAE nova (Q2=B/C)                         | 02_Projeto                        | OAE-M-001 + fan-out 05 + 07                       |
| Inspeção rotineira (Q2=E)                            | 05_Inspecao                       | OAE-M-002/003/004                                 |
| OAE danificada — plano de recuperação                | 05_Inspecao + 02_Projeto          | OAE-M-005 + orçamento (handoff 05)                |
| DD de concessão com portfólio de OAEs                | 12_Advisory                       | Fan-out S2 + 15 + 06 usando KE-041 como benchmark |

Handoff frequente: **07 Cronograma** (Monte Carlo compartilhado), **S1
Rodovias** (OAE numa rodovia), **05 Orçamento**, **15 Advisory** (DD de portfólio).
