# Agent Library — Manta 15 Advisory (manta-15, advisory)

Referência canônica de trabalho do agente **Advisory** (Sonnet/Opus híbrido).
Se o `.claude/agents/agente-advisory.md` é o **como o agente pensa**, este
arquivo é o **com o que o agente trabalha**.

**Escopo:** pareceres para stakeholders externos (bancos, TCU/TCE, agências
reguladoras), *systematic reviews*, análises comparativas de política
pública, notas técnicas de risco. Segundo maior consumidor de KEs (12 de 52).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/12_Advisory/`                        | Pareceres e notas técnicas — leitura+escrita   |
| `03_Projetos/{segmento}/{obra}/12_Advisory/Externos/`               | Documentos a bancos/TCU/agências — leitura+escrita |
| `04_IA/Manta-Maestro/Modelos/Advisory/`                             | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B4/`, `B5/`, `B7/`                       | PDFs originais dos KEs — só leitura            |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| ADV-M-001   | Parecer técnico — reequilíbrio econômico-financeiro       | FGV EEF-Rodovias + KE-037       |
| ADV-M-002   | Nota técnica — Lei 14.026/2020 (novo marco saneamento)   | ANPEC 2025 + KE-043             |
| ADV-M-003   | Systematic review — template estruturado                  | KE-002, KE-021                  |
| ADV-M-004   | Parecer TCE — 11 parâmetros de reequilíbrio               | TCE-MG 2023 + KE-038            |
| ADV-M-005   | Análise de renegociação de concessão (FCM + risco)        | FGV EPGE + KE-039               |

## 3. Knowledge Elements (12 KEs no pgvector)

Do `INDICE-KEs.md`, seção Advisory (12 KEs · B4 + B5 + B7):

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-014 | metodo       | Teoria TFV — base para arg. teórica em pareceres             |
| KE-024 | benchmark    | Diff-in-diff privatização 3.536 municípios (evidência)       |
| KE-034 | case_study   | ANTT — pedidos de revisão extraordinária (jurisprudência)    |
| KE-035 | norma        | Resolução ANTT 5.850/2019 — FCM                              |
| KE-036 | metodo       | Framework EEF Lei 8.987/95 — matriz + Fator D                 |
| KE-037 | metodo       | Procrofe fases I-III — racional econômico                     |
| KE-039 | metodo       | Renegociação vs reequilíbrio — teoria econômica FGV/BNDES     |
| KE-043 | benchmark    | Pós-NMLSB — desenho contratual determina universalização      |
| KE-044 | case_study   | SNIS público × privado — evidência empírica                   |
| KE-045 | case_study   | 4 casos saneamento BR (Limeira, Prolagos, Petrópolis…)        |
| KE-046 | parametro    | Evolução tarifária pré/pós privatização — benchmark AySA      |
| KE-047 | case_study   | Iguá/CEDAE RJ — contraponto (riscos de gestão privada)        |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '15' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `advisory.parecer_reequilibrio` — monta ADV-M-001 com FCM anexo (KE-035/037)
- `advisory.systematic_review` — organiza literatura por tipo/ano/método (KE-002/021)
- `advisory.tarifa_benchmark` — extrai série tarifária dos KEs 045/046
- `advisory.risk_matrix_externa` — matriz de riscos para bancos/agências

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Banco pede parecer sobre reequilíbrio                | 12_Advisory/Externos              | ADV-M-001 + FCM + ADV-M-004 anexo                 |
| Cliente decide entrar em concessão de saneamento     | 12_Advisory                        | ADV-M-002 + ADV-M-005 (racional econômico)        |
| Agência (ANTT/TCU) faz questionamento técnico        | 12_Advisory/Externos              | Nota técnica com KE-034/038 como fundamentação    |
| Pesquisa acadêmica sobre política pública            | 12_Advisory                        | ADV-M-003 preenchida (systematic review)          |
| Handoff de 01 Claims (pleito precisa endosso)        | 09_Pleitos + 12_Advisory          | Parecer independente com base normativa           |

Handoff frequente: **01 Claims** (pareceres para pleitos), **02 Contratual**
(fundamentação de aditivos), **06 Modelagem** (análise financeira em conjunto),
**03-S8 Saneamento** (contexto AySA).
