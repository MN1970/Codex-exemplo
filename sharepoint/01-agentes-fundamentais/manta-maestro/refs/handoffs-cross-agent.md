# refs/handoffs-cross-agent.md — manta-maestro

Playbook de 8 cenários canônicos de handoff cross-agent, herdado da
v4.5. Serve como teste E2E manual de coordenação: cada cenário lista
o input do usuário, o fluxo esperado pelo Maestro, e a fronteira
sensível que precisa ser testada.

Convenções:
- `→` = handoff explícito emitido pelo agente primário (transfere contexto).
- `⇢` = consulta cruzada (agente primário chama outro como tool, sem transferir).
- **negrito** = agente que RESPONDE ao usuário no fim.

Fonte canônica: `/docs/HANDOFFS-CROSS-AGENT.md` (v4.5). Este documento
é o espelho na pasta do Maestro para consumo direto.

---

## Cenário 1 — DD de porto graneleiro com acesso rodoviário e LT

**Input**: "Preciso de DD técnica para o Porto Aratu-Salvador, incluindo
terminal de grãos, canal de acesso, e infra de energia. Cliente CIA
fictícia comprando ativo."

**Fluxo**:
1. Maestro → **agente-portos** (S7)
2. agente-portos ⇢ **agente-barragens** (S11) — se houver TSF de minério no berço
3. agente-portos → **agente-infraestrutura-s1** (S1) — rodovia de acesso
4. agente-portos → **agente-energia** (S10) — LT + SE dedicada
5. agente-portos ⇢ **agente-advisory** (Manta 15) — modelagem financeira de arrendamento
6. agente-portos ⇢ **agente-contratual** (Manta 02) — cláusulas ANTAQ

**Critério**: nada "cai no vazio"; KEs acadêmicos citados (PIANC 158, SNIS).

---

## Cenário 2 — Refinaria brownfield com integração ferroviária

**Input**: "Expansão da Rnest — nova unidade de coqueamento retardado
50 kbpd, com carregamento ferroviário e nova SE 138 kV."

**Fluxo**:
1. Maestro → **agente-oleo-gas** (S14) — "Rnest", "coqueamento", "UCR"
2. agente-oleo-gas → **agente-infraestrutura-s3** (S3) — ferrovia
3. agente-oleo-gas → **agente-energia** (S10) — SE 138 kV
4. agente-oleo-gas ⇢ **agente-saneamento** (S9) — água industrial + ETE oleosa

**Fronteira testada**: S14 NÃO dimensiona a ETE — encaminha para S9.

---

## Cenário 3 — Mina de ferro com dry stack e mine-to-port

**Input**: "Planejar mina de ferro nova em MG com produção 15 Mtpa,
dry stack para rejeitos, correia até terminal em Vitória."

**Fluxo**:
1. Maestro → **agente-mineracao** (S13) — "mina", "Mtpa"
2. agente-mineracao **Q0**: "TSF? Não (dry stack)" → segue
3. agente-mineracao ⇢ **agente-barragens** (S11) — revisão do dry stack
4. agente-mineracao → **agente-infraestrutura-s3** (S3) — correia longa > 50 km
5. agente-mineracao → **agente-portos** (S7) — terminal em Vitória
6. agente-mineracao → **agente-energia** (S10) — LT + SE

**Fronteira testada**: dry stack está no limite S11/S13. Q0 do intake
de S13 deve explicitar o encaminhamento a S11.

---

## Cenário 4 — Data center 5 MW greenfield

**Input**: "Data center TIER III 5 MW em Barueri — 30k m², LEED Silver,
SLA 99,982%."

**Fluxo**:
1. Maestro → **agente-edificacoes** (S6) — "data center", "LEED"
2. agente-edificacoes → **agente-energia** (S10) — SE 34,5 kV + no-break
3. agente-edificacoes → **agente-saneamento** (S9) — drenagem + reúso
4. agente-edificacoes ⇢ **agente-advisory** (Manta 15) — OpEx TIER III

**Fronteira testada**: data center NÃO cai em S14 (não é refinaria).

---

## Cenário 5 — Túnel urbano de metrô em terreno mole

**Input**: "Extensão da Linha 4-Amarela SP, novo trecho com túnel NATM
em solo mole + estação com poço de acesso VCA."

**Fluxo**:
1. Maestro → **agente-tuneis** (S12) — "NATM", "poço de acesso"
2. agente-tuneis ⇢ **agente-infraestrutura-s4** (S4) — sistemas do metrô
3. agente-tuneis ⇢ **agente-infraestrutura-s2** (S2) — OAE do portal
4. agente-tuneis alerta sobre necessidade de método observacional Peck

**Fronteira testada**: pós-v4.4, S12 tem agente próprio — deve DOMINAR
a resposta, não apenas repassar para S2+S4.

---

## Cenário 6 — Barragem de rejeitos existente (descaracterização)

**Input**: "Alteamento a montante em Nova Lima, PoV do dono da mina —
plano de descaracterização até 2027 conforme Lei 14.066."

**Fluxo**:
1. Maestro → **agente-barragens** (S11) — "alteamento montante", "Lei 14.066"
2. agente-barragens ⇢ **agente-mineracao** (S13) — conflitos com plano de lavra
3. agente-barragens → **agente-contratual** (Manta 02) — compliance ANM Res 95
4. agente-barragens cita **KEs acadêmicos** (Mendes 2022, Fernandes 2020)

**Fronteira testada**: quem lidera é S11 (rejeitos = disposto). S13
entra como consultor. NÃO invertido.

---

## Cenário 7 — Aeroporto regional amazônico

**Input**: "Novo aeródromo regional em Coari-AM, aeronave crítica ATR
72-600. Concessão federal fase 3."

**Fluxo**:
1. Maestro → **agente-aeroportos** (S8)
2. agente-aeroportos ⇢ **agente-saneamento** (S9) — abastecimento + esgoto do TPS
3. agente-aeroportos ⇢ **agente-energia** (S10) — subestação isolada + gerador
4. agente-aeroportos cita **KE acadêmico** Pereira 2021 (crítica ao
   superdimensionamento em regionais amazônicos)

---

## Cenário 8 — Adutora AySA + estação de bombeamento

**Input**: "AySA — adutora DN 1200 mm de 15 km com EEAB intermediária.
Zona norte de Buenos Aires."

**Fluxo**:
1. Maestro → **agente-saneamento** (S9) — "AySA", "adutora", "EEAB"
2. agente-saneamento → **agente-energia** (S10) — alimentação da EEAB
3. agente-saneamento ⇢ **agente-tuneis** (S12) — travessia por HDD em rio
4. agente-saneamento ⇢ **agente-orcamento** (Manta 05) — SICRO/TPU BR ≠ ARS

**Fronteira testada**: PRIORIDADE AySA é do S9 (metadata no SKILL).
Não é jogado para S1 (rodovia) ou S14 (adução de óleo).

---

## Cenário 9 — A2 Quantitativos SEMPRE precede briefing confirmado

**Input**: "Roda o levantamento de quantidades do projeto OAE 622 pra mim."
(ou variantes: "extrai tudo agora", "faz o quantitativo", "gera a
PQ_SUPRIMENTOS", "cria a planilha de suprimentos SAP", "levanta os aços
do viaduto").

**Fluxo esperado (NAO invertivel):**

1. Maestro → **manta-maestro** (roteador) reconhece A2 no verbo/objeto.
2. Maestro instancia `BriefingGenerator(mode=auto_select_mode(...),
   project_files=[...])` do modulo
   `manta-hub/backends/shared/briefing_generator.py`.
3. Maestro chama `build_briefing(backend_hint=<oae|balanco|drenagem|...>)`
   → gera `ProjectBriefing` com os 10 blocos (ver §14.2.1 do SKILL.md).
4. Maestro renderiza `briefing.to_markdown()` no chat e AGUARDA CONFIRM
   do MN. Correcao MN → `briefing.diff_after_patch(patch)`.
5. So depois do CONFIRM (ou modo `DIRETO` acionado por >=3 episodios
   similares em `agent_episodes`), Maestro dispara os backends de
   extracao (`backends/oae`, `backends/balanco`, `backends/sondagem`,
   `backends/drenagem`, `backends/ifc`, `backends/landxml`,
   `backends/pavimentacao`, `backends/terraplenagem`,
   `backends/iluminacao`).
6. Backend de extracao consome o `discrepancy_rules_active` do briefing
   → gera Auditoria/Discrepancias/Rastreabilidade nas abas do XLSX.
7. Ao terminar, Maestro grava `agent_episodes` com o P2 emitido + o
   briefing confirmado (`context_json.briefing`) — alimenta o modo
   Direto de futuras execucoes.

**Fronteira testada:** o Maestro **NUNCA** delega A2 antes de MN
aprovar briefing. Se o usuario forcar ("nao precisa preambulo, roda"),
o Maestro **insiste** no minimo dos blocos 1/2/3 (base SICRO/TPU/SINAPI
+ estado + data-base) — porque um quantitativo errado por base
desatualizada e retrabalho garantido. Modo Direto NAO e atalho de
preguica: e atalho de aprendizado (o Maestro ja aprendeu o padrao).

**Regressao testavel:** input "levanta o aço da OAE 622" ⇒ Maestro
emite briefing OAE com 22 itens SAP esperados (F3002, F2015, F2018,
F1001, F1002, O1044, O1632, O1193, D5054, C5001, T3017, O2141, O2146,
O1174, O2021, O1443, O1401, O1522, O1541, O2701, F2020 + item variavel)
+ regras de consist-guard (taxa_armadura, diametro_cage_vs_furo,
qtd_neoprene) + base SICRO/DNIT + SP + 2024-10. Se qualquer bloco
sair vazio ou o Maestro pular pro EXECUTE sem CONFIRM: cenario
falha.

---

## Automação futura (v5)

GH Action rodando os 8 cenários a cada release do CLAUDE.md master
contra Maestro em staging, validando com LLM-as-a-judge (Sonnet 4.6)
os 5 critérios de §9. Falha o build se ≥1 cenário quebrar.

Referência: Chen et al. (2024) "AgentBench" — método análogo aplicado
ao AgentVerse.
