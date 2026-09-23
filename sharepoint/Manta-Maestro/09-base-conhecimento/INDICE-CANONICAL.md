# INDICE-CANONICAL — Manta Maestro

> Ponto único de consulta. Todos os agentes/skills leem isto ANTES de qualquer busca.
> Versão: 1.2 · Gerado: 2026-09-22 (v1.1: 2026-09-07) · Cobertura: 12 pastas root, 151+ diretórios, 275+ arquivos (excl. `99-backup/`) -- contagem herdada da v1.0 (2026-07-11), pendente de recontagem completa; ver §13 e §14 para o que foi verificado em cada revisão.
> Sanitizado sob R1 — zero nome de empresa ou profissional; só termos técnicos/regulatórios/geográficos/paths.
> [v1.2] Fonte de edição: repositório GitHub (`sharepoint/Manta-Maestro/09-base-conhecimento/INDICE-CANONICAL.md`), publicado aqui por espelho. Editar lá, não aqui — ver §14.

Consulte §10 (Vocabulário de roteamento) para ir direto ao destino. Se o pedido não estiver mapeado, ler §2–§6 (donos por eixo) antes de disparar busca ampla.

---

## 1. Camadas (eixos)

| Eixo | Camada | Path | Contagem | Papel |
|---|---|---|---|---|
| Segmentos (S) | L1.5 | `01-segmentos/` | **14 (S1–S14)** [v1.1: +S12-túneis, S13-mineração, S14-óleo&gás] | Dono do domínio setorial — quem opera aquele tipo de projeto |
| Atividades (A) | L1.7 | `02-atividades/` | **11 (A1–A11)** [v1.1: +A11-fiscalização] | Formato do deliverable — quem sabe emitir aquele produto |
| Funcionais (F) | L1.6 | `03-funcionais/` | **10 (F1–F10)** [v1.1: +F9-meta, F10-pesquisa-evolutiva] | Serviços transversais — infra que qualquer S/A consome |
| Disciplinas (D) | L1.8 | `04-disciplinas/` | **22 (D01–D22)** [v1.1: +D21-topografia-geodesia, D22-túneis] | Biblioteca técnica — normas, métodos, memórias |
| Sub-skills | L1.9 | `05-sub-skills/` | 4 builders operacionais (1 aposentado em 2026-09-07, ver §6) | Executores concretos herdados/em migração |
| Exemplares L3 | L3 | `06-exemplares/` | 30 células S.A escaneadas, 3 documentadas (S1.A1) | Casos-referência por célula S.A.D |
| Execuções | L2 | `07-execucoes/` | pipeline Python + edge functions | RAG-indexer, chunker, sync delta |
| Rubricas | L2 | `08-rubricas/` | **41** (A1–A10 completo [v1.1: A9 já ativa], S1–S11 completo, D01–D20) [v1.1: falta rubrica para D21/D22, S12–S14, A11] | Auto-juízes por atividade/segmento/disciplina |
| Base conhecimento | L0.5 | `09-base-conhecimento/` | assets + este índice | Fonte única — normas, referências |
| Arquitetura | L0 | `00-arquitetura/` | **37 arquivos** [v1.1: +6, ver §13] | Especificações, planos, mapas mestres |
| Infra | L2 | `06-infraestrutura/` | MCP servers + scripts sync | Runtime dependencies |
| Meta | L0 | `99-meta/` | agente-projeto-claude | Skills auxiliares do próprio Maestro |

Legado: `99-backup/` (v2.2 agentes-fundamentais + snapshots + saneamento 2026-09-07) — **ignorar em consulta corrente**. [v1.2] `03-exemplares/` também é legado — esvaziado em 2026-09-22, ver §7.

Pendência aberta [v1.1]: a biblioteca de documentos solta `04_IA` (fora de `Documentos Compartilhados`) ainda tem ~15 arquivos/pastas antigos não migrados nem arquivados (versões anteriores de `02-atividades/*` soltas, `04-routing-migration-v4.2/`, `09-base-conhecimento/` reduzido, `99-backup/` próprio, `99-meta/`, arquivos raiz `GUIA_INGESTAO_PROPOSTAS.md` e `RAG_COMANDOS_EQUIPE.md`). O que era exclusivo de lá (5 arquivos de arquitetura v6 + reconciliação de `MAESTRO-OBJECTS-METALS/`) já foi migrado para a árvore canônica em 2026-09-07 (ver §13). A aposentadoria completa da biblioteca `04_IA` solta requer revisão humana antes de mover/apagar o restante — não foi automatizada.

---

## 2. Segmentos S1–S14 — quem é dono do quê [v1.1: expandido]

Denso = tem sub-agentes especializados por eixo do segmento. Leve = SKILL.md único no root.

| Código | Nome | Path | Densidade | Sub-agentes | Palavras-chave de roteamento |
|---|---|---|---|---|---|
| S1 | Rodovias | `01-segmentos/S1-rodovias/` | leve | — | rodovia, asfalto, duplicação, restauração, EVTEA rodoviário, concessão rodoviária, DNIT, DER, ARTESP, faixas adicionais, SP-330, IPR |
| S2 | OAE | `01-segmentos/S2-oae/` | leve | — | ponte, viaduto, passagem inferior/superior, túnel rodoviário, mesoestrutura, superestrutura, protensão, aparelho de apoio, NBR 7187, NBR 6118 |
| S3 | Ferrovia | `01-segmentos/S3-ferrovia/` | denso | edital, geometrico, patio-oficina, portal-ferrovia-builder, row, sinalizacao, tracao-energia, via-permanente | ferrovia, via permanente, AMV, ROW ferroviário, subestação de tração, catenária, AREMA, UIC, ANTT |
| S4 | Metro | `01-segmentos/S4-metro/` | leve | — | metrô, estação subterrânea/elevada, PSD, NATM metroviário, TBM, poço de ventilação, VEA, catenária, CBTC, terceiro trilho, Linha 5 Lilás |
| S5 | Imobiliário | `01-segmentos/S5-imobiliario/` | leve | — | incorporação, empreendimento residencial/comercial/misto, VGV, SCP, landbank, permuta, RICS, USPAP, NBR 14653 |
| S6 | Edificações | `01-segmentos/S6-edificacoes/` | leve | — | hospital, industrial, corporativo, shopping, escola, hoteleiro, arena/estádio, retrofit, LEED, WELL, NBR 15575, RTQ-C |
| S7 | Portos | `01-segmentos/S7-portos/` | denso | abrigo, arrendamento, cais-pier, dragagem, retroarea | porto, terminal marítimo/fluvial/lacustre, dragagem, cais, píer, quebra-mar, retroárea, arrendamento portuário, ANTAQ, PIANC, ROM 0.2/2.0, ISPS, MARPOL, NORMAM |
| S8 | Aeroportos | `01-segmentos/S8-aeroportos/` | denso | concessao-aeroportuaria, patio-tps, pavimento, pista-taxiway, sistemas-navegacao | aeroporto, pista, taxiway, pátio TPS, PAPI, PCN, ICAO Annex 14, FAA AC 150/5300, ANAC RBAC 154/139, DECEA ICA 100-12 |
| S9 | Saneamento | `01-segmentos/S9-saneamento/` | denso | captacao-eta, concessao, drenagem-urbana, ete-esgoto, rede-adutora | ETE, ETA, esgoto, água, adutora, drenagem urbana, concessão saneamento, SNIS, Lei 14.026, ANA NR-001, PMSB, IWA, NBR 15645 |
| S10 | Energia | `01-segmentos/S10-energia/` | denso | estudo-eletrico, geracao, leilao-rap, lt-torre, subestacao | linha de transmissão, LT, torre, subestação, geração, RAP, leilão A-N, ANEEL, ONS, EPE PDE, IEEE 738/80, IEC 60826 |
| S11 | Barragens | `01-segmentos/S11-barragens/` | denso | concreto-cvc-ccr, rejeitos-mineracao, seguranca-pae, terra-enrocamento, vertedouro-descarregador | barragem, hidrelétrica, contenção de rejeitos, PAE, vertedouro, terra-enrocamento, CCR, ICOLD 164/194, DAMBRK, CBDB, Lei 12.334 PNSB, ANM Res 95, ANA SNISB |
| S12 | Túneis | `01-segmentos/S12-tuneis/` | **a confirmar** | — | **[v1.1: pasta existe na árvore, conteúdo/keywords não auditados nesta revisão — consultar SKILL.md diretamente]** [v1.2: `agente-tuneis` v1.0.0 confirmado existente em 2026-09-11; ver nota `manta_code` abaixo] |
| S13 | Mineração | `01-segmentos/S13-mineracao/` | **a confirmar** | — | **[v1.1: idem S12 — pasta existe, keywords a confirmar]** [v1.2: `agente-mineracao` v1.0.0 confirmado existente em 2026-09-11] |
| S14 | Óleo e Gás | `01-segmentos/S14-oleogas/` | **a confirmar** | — | **[v1.1: idem S12 — pasta existe, keywords a confirmar]** [v1.2: `agente-oleo-gas` v1.0.0 confirmado existente em 2026-09-11] |

Cada segmento denso mantém `_agent-types/` (perfis de subagente) e `_referencias/INDICE-NORMAS-<seg>.md` (bibliografia setorial). Segmento leve mantém tudo no SKILL.md do root. S12–S14 ainda não têm rubrica em `08-rubricas/` (ver §9).

**[v1.2] Numeração S é esta tabela — decisão D2 de 2026-09-22.** A tabela de capacidades do banco (`manta_agent_capabilities`, projeto Supabase do Maestro) usava uma numeração antiga (túneis=03-S5, portos=03-S6 … edificações=03-S13) e foi renumerada para esta em 2026-09-22 (ver §14). **Atenção**: os SKILL.md de S12–S14 ainda carregam um campo legado `manta_code` herdado do template de infraestrutura que colide com o código de outro segmento (S12 diz "03-S5", S13 diz "03-S11", S14 diz "03-S12"). O campo que vale para roteamento é o código desta tabela (`sp_operational_segment`), não `manta_code`.

---

## 3. Atividades A1–A11 — formatos de deliverable [v1.1: +A11]

Todos em `02-atividades/A<n>-<nome>/SKILL.md` (camada L1.7, versão 3.0.0+; A1 está em 3.3.10 desde 2026-09-22, ver §13 e §14).

| Código | Nome | Quando invocar |
|---|---|---|
| A1 | Proposta | Proposta técnica, comercial (Tipo A/PTC, Tipo B/PRT, PRC), T1–T10, TR obrigatório, índice canônico, longa/curta. **v3.3.0**: agora inclui convenção de numeração MNT-YYYY-COM-NNNN, tabela tarifária (13 perfis), dados fixos da proponente, cláusulas padrão e a variante de concessão de infraestrutura de grande porte |
| A2 | Quantidades | Levantamento quantitativo, m/m²/m³, memória de cálculo, cross-check |
| A3 | Orçamento | Orçamento executivo, SICRO/SINAPI, CCU, BDI, benchmarking multi-banco, equalização |
| A4 | Modelagem | DCF, LBO, 3-statement, WACC, TIR, VPL, sensibilidade, comps, Damodaran |
| A5 | Cronograma | XER, MPP, CPM, DCMA-14, curva-S, Monte Carlo, forense TIA/Window |
| A6 | Contratual | Cláusula, aditivo, TAC, matriz de risco contratual, garantia, penalidade |
| A7 | Claims | Reequilíbrio econômico-financeiro, nexo causal (NC), cascata cronológica, AACE 29R-03, SCL D&D2 |
| A8 | Advisory | Parecer técnico, laudo, perícia judicial/arbitral, second opinion, due diligence técnica |
| A9 | Regulatório | Comentários a consulta pública, gap analysis, redação de norma, reg-diff |
| A10 | Risco | Matriz de risco, análise probabilística, mitigação, plano de contingência |
| A11 | Fiscalização | **[v1.1: pasta existe na árvore, keywords/escopo não auditados nesta revisão — consultar SKILL.md diretamente]** |

---

## 4. Disciplinas D01–D22 — bibliotecas técnicas [v1.1: +D21, D22]

Todos em `04-disciplinas/D<nn>-<nome>/SKILL.md` (camada L1.8).

| Código | Nome | Segmentos-cliente típicos |
|---|---|---|
| D01 | Tráfego | S1, S4, S8 |
| D02 | Geométrico | S1, S3, S8 |
| D03 | Geotecnia | S1, S2, S3, S4, S7, S11 |
| D04 | Fundações | S2, S4, S6, S10, S11 |
| D05 | Terraplenagem | S1, S3, S7, S8, S11 |
| D06 | Pavimentação | S1, S8 |
| D07 | Hidrologia | S1, S7, S9, S11 |
| D08 | Estrutural OAE | S2, S3, S4 |
| D09 | Contenção | S1, S2, S4 |
| D10 | Sinalização | S1, S3, S8 |
| D11 | Iluminação | S1, S8 |
| D12 | Interferências | S1, S3, S4, S9, S10 |
| D13 | Meio ambiente | todos |
| D14 | Desapropriação | S1, S3, S10 |
| D15 | MEP | S4, S6, S8 |
| D16 | HVAC | S4, S6, S8 |
| D17 | Elétrica | S4, S6, S8, S10 |
| D18 | Acústica | S4, S6 |
| D19 | Acessibilidade | S4, S6, S8 |
| D20 | BIM | todos |
| D21 | Topografia e Geodésia | **[v1.1: pasta existe, segmentos-cliente a confirmar]** |
| D22 | Túneis | **[v1.1: pasta existe — provável cliente S12-túneis, S1, S2, S4; a confirmar]** |

---

## 5. Funcionais F1–F10 — serviços transversais [v1.1: +F9, F10]

Todos em `03-funcionais/F<n>-<nome>/SKILL.md` (camada L1.6).

| Código | Papel na arquitetura |
|---|---|
| F1 IA | Model tiering, roteamento por complexidade, uso de LLM |
| F2 SharePoint | Wrap ms365-extrator + Graph write via adapter L2.5 |
| F3 Portal | Padrão portal Manta, tabs verticais, GED por último |
| F4 Extração | PDF/DOCX/XLSX/DWG → JSON schema canônico |
| F5 Notificação | Alertas por email/Teams, agendamento Cowork |
| F6 Trace | Log estruturado — evento, params, resultado, fonte, base, status |
| F7 Guardrails | aluci-guard, consist-guard, context-guardian, R1–R5 |
| F8 Padronização | padrão-manta visual, marca d'água, rastreabilidade |
| F9 Meta | **[v1.1: pasta existe (`03-funcionais/F9-meta/`) — possivelmente sobreposta a `99-meta/agente-projeto-claude/`, escopo exato a confirmar]** |
| F10 Pesquisa Evolutiva | **[v1.1: pasta existe (`03-funcionais/F10-pesquisa-evolutiva/`) — provável dono do "Daily Evolution Engine" citado em outras skills; escopo exato a confirmar]** |

---

## 6. Sub-skills builders (`05-sub-skills/`)

| Item | Path | Papel |
|---|---|---|
| manta-maestro | `05-sub-skills/manta-maestro/SKILL.md` | Orquestrador raiz (M12 canônico) |
| SS01-superposicao-disciplinar | `05-sub-skills/SS01-superposicao-disciplinar/SKILL.md` | Merge multi-disciplinar |
| skill-analise-capex | `05-sub-skills/skill-analise-capex-SKILL.md` | Análise CAPEX standalone |
| ~~skill-proposta-comercial~~ | `05-sub-skills/skill-proposta-comercial-SKILL.md` | **[v1.1: ABSORVIDO por A1-proposta em 2026-09-07.** Este arquivo agora é só um stub de 667 bytes apontando para `02-atividades/A1-proposta/SKILL.md`. Não usar como fonte -- mantido apenas para quem tiver o caminho antigo salvo.] |

Fila local de sincronização: `05-sub-skills/manta-maestro/_sync_pending.json`.

Nota [v1.1]: `02-sub-skills/`, `04-rubricas/` e `05-execucoes/` (paths de v4.x) já estavam corretamente aposentados antes desta revisão -- cada um contém só um `_DEPRECATED.md` apontando para o path atual (`05-sub-skills/`, `08-rubricas/`, `07-execucoes/` respectivamente). Bom padrão, seguido agora também para `skill-proposta-comercial` e, desde a v1.2, para `03-exemplares/`.

---

## 7. Exemplares L3 (`06-exemplares/`)

Casos-referência ancorados em célula S.A.D (segmento × atividade × disciplina). Consultar antes de gerar novo entregável da mesma célula.

| Célula | Exemplares | Status |
|---|---|---|
| S1.A1 (Rodovias × Proposta) | EX-001 obra-duplicacao-rodovia, EX-002 estudo-capex-concessao, EX-003 adequacao-oae-estrutura-edital | 3 documentados |
| S1.A2, S1.A3, S1.A5, S1.A7, S10.A1, S10.A4, S11.A2, S11.A8, S2.A2, S2.A3, S2.A8, S3.A1, S3.A2, S3.A3, S3.A5, S3.A7, S4.A1, S4.A3, S4.A6, S5.A1, S5.A4, S6.A1, S6.A3, S7.A1, S7.A3, S8.A1, S8.A4, S9.A1, S9.A4 | [v1.1: 29 células adicionais confirmadas existentes na árvore -- pastas escaneadas, conteúdo não auditado nesta revisão] | pasta criada, aguarda casos (a confirmar individualmente) |
| S5.A4 (Imobiliário × Modelagem) | [v1.2] snippet visual `pedra-da-panela/` + `re-dashboard-v1.jsx` (movidos de `03-exemplares/imobiliario/` em 2026-09-22) | snippet visual, não é exemplar documentado |
| `_indices/` | [v1.2] `manta_propostas_index.json` (movido de `03-exemplares/bd/` em 2026-09-22) | índice de propostas em uso corrente pelo BD |

Índice de propostas (uso corrente do BD): `06-exemplares/_indices/manta_propostas_index.json`. Snippet visual imobiliário: `06-exemplares/S5.A4/pedra-da-panela/`, `06-exemplares/S5.A4/re-dashboard-v1.jsx`. [v1.2: até 2026-09-22 ambos viviam em `03-exemplares/bd/` e `03-exemplares/imobiliario/`; referências em `02-atividades/A1-proposta/SKILL.md` (v3.3.10) e `template-prt-rodovias-v1.md` (v1.0.1) já atualizadas.]

Nota [v1.2]: a árvore paralela antiga `03-exemplares/<dominio>/` (advisory, bd, claims, contratual, ferrovia, imobiliario, metro, oae, rodovias) foi **descontinuada em 2026-09-22**: o conteúdo em uso foi movido para `06-exemplares/` (acima), as 9 subpastas vazias restantes foram para a lixeira do SharePoint (recuperáveis) e `03-exemplares/_DEPRECATED.md` aponta para `06-exemplares/`. Não criar conteúdo novo em `03-exemplares/`.

---

## 8. Base de conhecimento (`09-base-conhecimento/`)

Assets fonte única (R5):

| Arquivo | Papel |
|---|---|
| `referencias-engenharia.json` | 14 disciplinas + CQP consolidado (asset rodovias-knowledge v1) |
| `INDICE-NORMAS-MESTRE.md` | Bibliografia normativa mestre |
| `INDICE-CANONICAL.md` | **Este arquivo** — ponto único de consulta |
| `RAG_ARQUITETURA_CANONICA.md` | Arquitetura do pipeline RAG |
| `TRAINING-QUANTITATIVOS.md` | Material de treino para quantitativos |

Subpastas: `eval/`, `notas-sprint/`.

Referências específicas por segmento vivem em `01-segmentos/S<n>-<nome>/_referencias/INDICE-NORMAS-<seg>.md` (S3, S7, S8, S9, S10, S11).

Mapas complementares em `00-arquitetura/`:

- `MAPA-CONHECIMENTO.md` — fontes por segmento em 3 camadas (I)nternacional / (N)acional / (L)ocal
- `MATRIZ-SEGMENTO-DISCIPLINA.md` — quais D<nn> cada S<n> consome
- `INDICE-MANTA.md` + `indice-manta.json` — índice mestre v2/v3
- `manta-maestro-arquitetura-v3.1.md`, `v3.2.md`, `v5.0.md` — specs históricas e vigente
- `PLANO-EVOLUTIVO.md`, `PENDENTE-SHAREPOINT.md`, `DESENVOLVIMENTO-AGENTES.md`, `MANTA_MAESTRO_RELATORIO_reconciliacao-v5.0-vs-producao_v1_20260724.md`
- [v1.1, novos] `ARQUITETURA-AGENTES-IA-v6.1.0.md`, `CLAUDE.md-v6.1.0-CONSOLIDATED.md`, `SKILL-MANTA-MAESTRO-v6.1.0.md`, `MANTA-v5.0.1-DEPLOYMENT-STATUS.md`, `ROUTING-DECISION-TREE-v5.0.1.md`, `CONSOLIDACAO-SHAREPOINT-v5.0.1.md` (este último recuperado com gap documentado, ver §13) — arquitetura "v6" ainda não reconciliada com a v5.0.1 vigente; tratar como trabalho em andamento, não como substituição.

---

## 9. Rubricas L2 (`08-rubricas/`)

Auto-juízes que classificam saídas de cada atividade/segmento/disciplina. **41 rubricas ativas** [v1.1: A1–A10 completo, incluindo A9-regulatorio que estava pendente na v1.0 e já foi preenchida; S1–S11 completo; D01–D20 completo].

| Cobertura | Status |
|---|---|
| rubrica-A1 a A10 | ativas (10/10) |
| rubrica-S1 a S11 | ativas (11/11) |
| rubrica-D01 a D20 | ativas (20/20) |
| rubrica-A11-fiscalizacao | **faltando** [v1.1] |
| rubrica-D21, D22 | **faltando** [v1.1] |
| rubrica-S12, S13, S14 | **faltando** [v1.1] |

Rubrica alimenta gate pré-entrega (manta-qa) e o cross-check do M18 (arquiteto-ia).

---

## 10. Vocabulário de roteamento

Tabela de intenção → destino. Ler PRIMEIRO. Cobre 90% dos pedidos recorrentes.

| Pedido contém | Rota primária | Alternativa/co-consulta |
|---|---|---|
| dragagem, cais, píer, quebra-mar, ANTAQ, arrendamento portuário | `S7-portos/` (subskill correspondente) | D03 geotecnia, D07 hidrologia |
| ETE, ETA, esgoto, adutora, saneamento, SNIS, Lei 14.026 | `S9-saneamento/` | D07 hidrologia, A9 regulatório |
| barragem, PAE, rejeitos, vertedouro, ICOLD, PNSB | `S11-barragens/` | D03 geotecnia, D07 hidrologia, A10 risco |
| linha de transmissão, LT, subestação, RAP, ANEEL, leilão A-N | `S10-energia/` | D14 desapropriação, D17 elétrica |
| aeroporto, pista, taxiway, PCN, ICAO, RBAC 154/139 | `S8-aeroportos/` | D01 tráfego, D06 pavimentação |
| ferrovia, via permanente, AMV, catenária, AREMA, ANTT | `S3-ferrovia/` | D03 geotecnia, D08 estrutural |
| metrô, estação, PSD, NATM, TBM, Linha 5 Lilás | `S4-metro/` | D03 geotecnia, D15 MEP, D17 elétrica |
| rodovia, duplicação, EVTEA, DNIT, DER, ARTESP, SP-330 | `S1-rodovias/` | D02 geométrico, D06 pavimentação |
| ponte, viaduto, túnel rodoviário, NBR 7187 | `S2-oae/` | D03 geotecnia, D04 fundações, D08 estrutural |
| incorporação, VGV, SCP, landbank, RICS, NBR 14653 | `S5-imobiliario/` | A4 modelagem |
| hospital, corporativo, shopping, escola, LEED, NBR 15575 | `S6-edificacoes/` | D15 MEP, D16 HVAC, D18 acústica |
| túnel (não rodoviário isolado), TBM de grande diâmetro, escavação subterrânea dedicada | `S12-tuneis/` [v1.1, a confirmar] | D22 túneis, D03 geotecnia |
| mineração, lavra, beneficiamento mineral, barragem de rejeitos ligada a mina | `S13-mineracao/` [v1.1, a confirmar] | S11 barragens, D03 geotecnia |
| óleo e gás, dutos, terminal petrolífero, upstream/downstream | `S14-oleogas/` [v1.1, a confirmar] | D07 hidrologia |
| proposta técnica, T1–T10, TR, apresentação de proposta, proposta comercial, PTC, PRC, MNT-COM | `A1-proposta/` | F8 padronização |
| quantitativo, m/m²/m³, memória cálculo, cross-check | `A2-quantidades/` | F4 extração |
| orçamento, SICRO, SINAPI, CCU, BDI, benchmarking | `A3-orcamento/` | referências em `09-base-conhecimento/` |
| DCF, LBO, WACC, TIR, VPL, Damodaran, 3-statement | `A4-modelagem/` | S5 (imob), S10 (energia) |
| cronograma, XER, MPP, CPM, DCMA, curva-S, Monte Carlo | `A5-cronograma/` | plugin-p6-analytics (L3) |
| cláusula, aditivo, TAC, matriz de risco contratual | `A6-contratual/` | A10 risco |
| claim, reequilíbrio, nexo causal, cascata, AACE 29R-03, SCL | `A7-claims/` | A5 cronograma (forense) |
| parecer técnico, laudo, perícia, second opinion, due diligence | `A8-advisory/` | rubrica-A8 |
| consulta pública, reg-diff, comentários a norma | `A9-regulatorio/` | rubrica-A9 (ativa) |
| matriz de risco, análise probabilística, mitigação | `A10-risco/` | A6 contratual |
| fiscalização de obra/contrato (a confirmar escopo exato) | `A11-fiscalizacao/` [v1.1, a confirmar] | A6 contratual |
| padrão visual, marca d'água, tabs verticais, GED último | `F3-portal/` + `F8-padronizacao/` | asset padrão-manta |
| SharePoint (ler/mapear/escrever), Graph, ms365 | `F2-sharepoint/` | adapter L2.5 sharepoint-adapter |
| extrair PDF/DOCX/XLSX/DWG para JSON | `F4-extracao/` | manta-core cross-check-tripla |
| trace, log estruturado, rastreabilidade | `F6-trace/` | R5 kernel |
| aluci-guard, consist-guard, R1 sanitização | `F7-guardrails/` | kernel L1 |
| model tiering, Haiku vs Sonnet vs Opus | `F1-ia/` | manta-arquiteto-ia (M18) |
| sondagem SPT, NBR 6484, NSPT, perfil geológico | `D03-geotecnia/` | extrator-sondagem (Manta 22) |
| ponte protendida, pilar, aparelho apoio, NBR 6118 | `D08-estrutural-oae/` | S2 OAE |
| pavimento CBR, camada, dimensionamento, PMSP | `D06-pavimentacao/` | S1 rodovias, S8 aeroportos |
| tráfego, VMD, HCM, PDT, capacidade | `D01-trafego/` | S1, S4, S8 |
| interferências, cadastro, remanejamento, utilidades | `D12-interferencias/` | S1, S3, S4 |
| meio ambiente, EIA/RIMA, licença, RAP ambiental | `D13-meio-ambiente/` | todos os segmentos |
| desapropriação, DUP, indenização, imissão | `D14-desapropriacao/` | S1, S3, S10 |
| BIM, LOD, IFC, compatibilização | `D20-bim/` | S4, S6 |
| levantamento topográfico, geodésia, georreferenciamento | `D21-topografia-geodesia/` [v1.1, a confirmar] | S1, S3 |
| túnel — disciplina técnica (revestimento, ventilação, NATM) | `D22-tuneis/` [v1.1, a confirmar] | S12-tuneis, S2-oae, S4-metro |
| CAPEX standalone, análise investimento | `05-sub-skills/skill-analise-capex-SKILL.md` | A4 modelagem |
| exemplar de célula S.A.D (caso referência) | `06-exemplares/S<n>.A<m>/` | 3 documentados em S1.A1, 29 pastas adicionais existentes (conteúdo a confirmar) |
| índice de propostas, catálogo de propostas entregues | `06-exemplares/_indices/manta_propostas_index.json` [v1.2] | A1 proposta |
| pipeline RAG, chunker, embedder, sync delta | `07-execucoes/pipeline/` | edge functions em `07-execucoes/edge-functions/` |
| MCP server sharepoint-write | `06-infraestrutura/mcp-servers/sharepoint-write/` | script `Sync-MantaMaestro.ps1` |

---

## 11. Como consumir este índice

Regra do agente/skill que herda o kernel:

1. **Antes de buscar**, ler §10 (vocabulário) e §2.–§6 (donos por eixo). 80% dos pedidos resolvem aqui.
2. **Só se não achar aqui**, disparar busca ampla pelo canonical com Glob/Grep — nunca antes.
3. **Delta-aware**: se a data no topo estiver > 7 dias defasada versus `git log` do canonical, alertar (regenerar índice). [v1.1: esta regra existia na v1.0 e foi ignorada por 58 dias -- há agora uma Rotina mensal automatizada (criada em 2026-09-07) que verifica isso.]
4. **Nunca duplicar** — se o pedido cai em célula S.A.D já em §7 (Exemplares), citar exemplar e reusar.
5. **R1 estrito** — este índice não referencia nome de empresa/profissional. Se precisar apontar contrato específico, ir ao `CLAUDE.md` do projeto (não a este arquivo).
6. **Roteamento composto** é comum — ex.: "orçamento de ETE" = A3 + S9 + D07. §10 já sinaliza o co-consulta.
7. **[v1.1] Itens marcados "a confirmar"** (S12–S14, A11, D21–D22, F9–F10, as 29 células de exemplares não auditadas) existem fisicamente na árvore mas não tiveram seu conteúdo/keywords verificados nesta revisão -- ao rotear para eles, ler o SKILL.md/conteúdo real da pasta antes de confiar cegamente nesta tabela.
8. **[v1.2] Editar na fonte.** Este arquivo é publicado a partir do repositório GitHub. Correção feita direto no SharePoint é sobrescrita no próximo espelhamento — abrir a mudança no repositório.

---

## 12. Estatísticas do canonical [v1.1]

- Pastas root ativas: 12 (exclui `99-backup/`)
- Segmentos: 14 (S1–S14) -- 11 com keywords confirmadas, 3 (S12–S14) a confirmar
- Atividades: 11 (A1–A11) -- 10 com escopo confirmado, 1 (A11) a confirmar
- Funcionais: 10 (F1–F10) -- 8 com escopo confirmado, 2 (F9–F10) a confirmar
- Disciplinas: 22 (D01–D22) -- 20 com escopo confirmado, 2 (D21–D22) a confirmar
- Sub-skills 05: 4 builders (1 aposentado em 2026-09-07: skill-proposta-comercial, absorvido por A1-proposta)
- Rubricas ativas: 41/47 possíveis (faltam A11, D21, D22, S12, S13, S14)
- Exemplares L3: 1 célula com 3 casos documentados (S1.A1); 29 células adicionais existem como pasta, conteúdo não auditado
- Arquivos em `00-arquitetura/`: 37 (31 da v1.0 + 6 recuperados/mesclados da biblioteca `04_IA` solta em 2026-09-07)
- MCP servers dedicados: 1 (`sharepoint-write` em `06-infraestrutura/mcp-servers/`)
- Última verificação de estrutura: 2026-09-22 (v1.2, parcial — só `03-exemplares/` e `06-exemplares/`); 2026-09-07 (v1.1) — ver §13 e §14 para o que foi de fato auditado vs. herdado da v1.0

---

## 13. Changelog de saneamento — 2026-09-07 [novo em v1.1]

Consolidação estrutural realizada nesta data, motivada por confusão de caminhos
reportada por duas sessões distintas ao tentar localizar a skill de proposta
comercial. Trabalho realizado:

1. **Arquitetura v6 resgatada.** A biblioteca de documentos solta `04_IA`
   (fora de `Documentos Compartilhados`) continha 6 arquivos de arquitetura
   "v6" inexistentes na árvore canônica: `ARQUITETURA-AGENTES-IA-v6.1.0.md`,
   `CLAUDE.md-v6.1.0-CONSOLIDATED.md`, `SKILL-MANTA-MAESTRO-v6.1.0.md`,
   `MANTA-v5.0.1-DEPLOYMENT-STATUS.md`, `ROUTING-DECISION-TREE-v5.0.1.md` e
   `CONSOLIDACAO-SHAREPOINT-v5.0.1.md`. Todos copiados para
   `00-arquitetura/` na árvore canônica. Os 5 primeiros foram confirmados
   byte-exatos; o último (`CONSOLIDACAO-SHAREPOINT-v5.0.1.md`) tem um
   problema de encoding na ferramenta de leitura (UTF-8 lido como latin-1,
   truncando a extração nos últimos ~16 bytes de forma consistente) — foi
   recuperado com os acentos corrigidos manualmente, mas a última linha da
   tabela B está incompleta e alguns glifos de status foram substituídos por
   marcadores genéricos `[ok]`. Nota embutida no próprio arquivo.
   **A arquitetura v6 em si ainda não foi reconciliada/adotada como
   substituta da v5.0.1 vigente — isso é uma decisão de arquitetura em
   aberto, fora do escopo deste saneamento estrutural.**
2. **`MAESTRO-OBJECTS-METALS/` reconciliado.** A cópia canônica tinha só 1
   arquivo placeholder (201 bytes); a cópia em `04_IA` tinha 8 arquivos
   completos. Todos os 8 migrados para a canônica (7 confirmados
   byte-exatos; `maestro-objects-metals.md` recuperado com 3066 dos 3078
   bytes originais, mesmo problema de encoding do item acima, faltando a
   última linha).
3. **Pasta `agente-bd` órfã removida.** Uma pasta vazia em
   `04_IA/02-agentes-horizontais/agente-bd` (fora da árvore `Manta-Maestro/`)
   foi confirmada vazia e movida para a lixeira do SharePoint (reversível).
   O conteúdo real desse agente já estava corretamente arquivado desde
   2026-06-21 em `99-backup/agentes-fundamentais-v2.2-legado/agente-bd/`
   (SKILL.md de 7359 bytes + subpastas) — esse backup não foi tocado.
4. **Skill de proposta fundida.** `02-atividades/A1-proposta/SKILL.md`
   passou de v3.2.0 (5498 bytes, só metodologia) para **v3.3.0** (13342
   bytes): incorporou a convenção de numeração MNT-YYYY-COM-NNNN, a tabela
   tarifária de 13 perfis, os dados fixos da proponente, as cláusulas
   padrão (Seção IA, deslocamentos, medição, não aliciamento) e uma nova
   variante "Tipo A / Concessão de Infraestrutura de Grande Porte" (5
   blocos adicionais: dados oficiais rastreáveis, cenários com success fee,
   método do paramétrico em etapas, infraestrutura incluída, controle de
   revisão + ficha técnica) — validada contra a proposta real
   MNT-2026-COM-1183_D (Concessão Rota 2 de Julho). Esse conteúdo antes só
   existia num pacote de skill fora do SharePoint, nunca escrito na árvore.
   `05-sub-skills/skill-proposta-comercial-SKILL.md` (o stub de 809 bytes
   que existia antes) foi substituído por um ponteiro de descontinuação de
   667 bytes, no mesmo padrão de `_DEPRECATED.md` já usado em
   `02-sub-skills/`, `04-rubricas/` e `05-execucoes/`.
   **[v1.2 — correção de fonte]** A afirmação "validada contra a proposta
   real MNT-2026-COM-1183_D" **não se sustenta**: a revisão `_D` não foi
   encontrada no SharePoint (a mais recente localizada é `_C`), e o texto
   da variante reproduz quase literalmente um addendum de repositório cuja
   premissa já havia sido marcada como não verificada. A fonte foi
   corrigida na própria skill A1-proposta em v3.3.7; mantido aqui o texto
   original da v1.1 como registro histórico. Não citar `_D` como fonte.
5. **Rotina de manutenção mensal criada.** Verifica no dia 1 de cada mês se
   este índice está com mais de 7 dias de defasagem (regra do §11, item 3,
   que ficou 58 dias sem ser seguida antes deste saneamento) ou se a
   contagem real diverge da registrada aqui, e regenera/avisa se necessário.

**Não feito nesta revisão (fora de escopo, requer decisão humana):**

- Aposentadoria completa da biblioteca `04_IA` solta (restam ~15
  arquivos/pastas antigos ali, mais pobres que a canônica, mas não
  auditados individualmente).
- Remoção do backup `99-backup/importado-de-04_IA-2026-07-30/` (fica
  redundante só depois da aposentadoria completa acima).
- Confirmação de escopo/keywords para S12–S14, A11, D21–D22, F9–F10 e as 29
  células de exemplares não documentadas (marcados "a confirmar" em todo
  este índice).
- Reconciliação da arquitetura "v6" recém-resgatada com a v5.0.1 vigente.

---

## 14. Changelog da auditoria — 2026-09-22 [novo em v1.2]

Auditoria do sistema Manta Maestro (repositório + SharePoint + banco),
com decisões de MN registradas no plano de auditoria do repositório
(`docs/PLANO-AUDITORIA-v1.md`, §7). O que mudou aqui:

1. **Fonte de edição = repositório (decisão D1), com exceção.** Este índice
   e o template PRT rodovias passam a ter a cópia de edição no repositório
   GitHub (`sharepoint/Manta-Maestro/…`) e são publicados aqui por espelho
   (ver §11 item 8). **Exceção:** `02-atividades/A1-proposta/SKILL.md`
   continua com edição **aqui no SharePoint** — contém dados comerciais
   (tabela tarifária, dados bancários, contato) e o repositório é público.
   Até decisão de MN, nenhum arquivo com dado comercial ou nome de
   cliente/pessoa vai para o repositório.
2. **Numeração de segmentos confirmada (decisão D2).** A numeração deste
   índice (§2, S1–S14) é a oficial. A tabela `manta_agent_capabilities` do
   banco foi renumerada para ela (túneis 03-S5→03-S12, portos 03-S6→03-S7,
   aeroportos 03-S7→03-S8, saneamento 03-S8→03-S9, energia 03-S9→03-S10,
   barragens 03-S10→03-S11, mineração 03-S11→03-S13, óleo e gás
   03-S12→03-S14, edificações 03-S13→03-S6), com tabela de auditoria e
   bloco de reversão na migração
   `supabase/migrations/2026_09_22_auditoria_w8_seguranca_renumeracao.sql`
   do repositório. Logs históricos não foram reescritos.
3. **`03-exemplares/` descontinuado.** `bd/manta_propostas_index.json` →
   `06-exemplares/_indices/`; `imobiliario/pedra-da-panela/` e
   `imobiliario/re-dashboard-v1.jsx` → `06-exemplares/S5.A4/`. As 9
   subpastas de domínio que ficaram vazias foram para a lixeira
   (recuperáveis) e `03-exemplares/_DEPRECATED.md` foi criado. Referências
   atualizadas em `02-atividades/A1-proposta/SKILL.md` (v3.3.10) e
   `02-atividades/A1-proposta/template-prt-rodovias-v1.md` (v1.0.1).
4. **Fonte fabricada sinalizada** em §13 item 4 (MNT-2026-COM-1183_D).
5. **Campo `manta_code` legado** de S12–S14 sinalizado em §2 (colide com
   o código de outro segmento; o código válido é o de §2).

**Não feito nesta revisão:** confirmação de escopo/keywords dos itens "a
confirmar" (S12–S14, A11, D21–D22, F9–F10); correção do campo
`manta_code` dentro dos SKILL.md de S12–S14; recontagem completa da
árvore; aposentadoria da biblioteca `04_IA` solta.
