# Handoffs cross-agent — cenários canônicos de teste (v4.5)

Backlog item #5. Cada fluxo abaixo é um teste E2E de coordenação
entre múltiplos agentes verticais + horizontais. Estes cenários NÃO
rodam automatizados hoje — servem como playbook de validação manual
pelo MN e pela equipe, e como base para o futuro teste automatizado.

Convenções:
- `→` = handoff explícito emitido pelo agente primário
- `⇢` = consulta cruzada (agente primário chama outro agente como tool sem transferir contexto)
- **negrito** = agente que RESPONDE ao usuário no fim

---

## Cenário 1 — DD de porto graneleiro com acesso rodoviário e LT

**Input do usuário**: "Preciso de DD técnica para o Porto Aratu-Salvador,
incluindo terminal de grãos, canal de acesso, e infra de energia. Cliente
CIA fictícia comprando ativo."

**Fluxo esperado**:
1. Maestro roteia para **agente-portos** (S6) — palavra-chave "porto", "terminal", "canal"
2. agente-portos ⇢ **agente-barragens** (S10) — se houver TSF de minério no berço
3. agente-portos → **agente-infraestrutura-s1** (S1) — rodovia de acesso ao porto
4. agente-portos → **agente-energia** (S9) — LT + SE dedicada
5. agente-portos ⇢ **agente-advisory** (Manta 15) — modelagem financeira de arrendamento
6. agente-portos ⇢ **agente-contratual** (Manta 02) — cláusulas ANTAQ
7. agente-portos consolida em resposta única com seções por disciplina

**Critérios de sucesso**:
- Cada agente secundário citado explicitamente no memorial.
- Nenhum tópico "cair no vazio" (ex.: energia mencionada mas sem S9 ativado).
- KEs acadêmicos citados quando aplicável (PIANC 158, SNIS 2024, etc.).

---

## Cenário 2 — Refinaria brownfield com integração ferroviária

**Input**: "Expansão da Rnest — nova unidade de coqueamento retardado
50 kbpd, com carregamento ferroviário e nova SE 138 kV."

**Fluxo esperado**:
1. Maestro → **agente-oleo-gas** (S12) — palavras "Rnest", "coqueamento", "UCR"
2. agente-oleo-gas → **agente-infraestrutura-s3** (S3) — ferrovia de derivados
3. agente-oleo-gas → **agente-energia** (S9) — SE 138 kV
4. agente-oleo-gas ⇢ **agente-saneamento** (S8) — água industrial + ETE de água oleosa
5. agente-oleo-gas consolida ordenando por criticidade (SCI/HAZOP → equipamento → utilidades)

**Fronteira testada**: S12 NÃO deve tentar dimensionar a ETE — encaminha para S8.

---

## Cenário 3 — Mina de ferro com dry stack e mine-to-port

**Input**: "Planejar mina de ferro nova em MG com produção 15 Mtpa,
dry stack para rejeitos, correia até terminal em Vitória."

**Fluxo esperado**:
1. Maestro → **agente-mineracao** (S11) — "mina", "ferro", "Mtpa"
2. agente-mineracao **Q0 do intake**: "TSF? Não (dry stack)" → segue
3. agente-mineracao ⇢ **agente-barragens** (S10) para revisão do dry stack (fronteira sensível)
4. agente-mineracao → **agente-infraestrutura-s3** (S3) — correia longa (>50 km) como "ferrovia funcional"
5. agente-mineracao → **agente-portos** (S6) — terminal em Vitória
6. agente-mineracao → **agente-energia** (S9) — LT dedicada e SE
7. agente-mineracao consolida com LOM (Life of Mine)

**Fronteira testada**: dry stack está no limite S10/S11. O Q0 do
intake de S11 deve explicitar o encaminhamento a S10 para revisão.

---

## Cenário 4 — Data center 5MW greenfield com edificação industrial

**Input**: "Projetar data center TIER III de 5 MW em Barueri — terreno
30k m², cliente exige LEED Silver e SLA 99,982%."

**Fluxo esperado**:
1. Maestro → **agente-edificacoes** (S13) — "data center", "LEED"
2. agente-edificacoes → **agente-energia** (S9) — SE 34,5 kV + LT + no-break
3. agente-edificacoes → **agente-saneamento** (S8) — drenagem urbana + reúso de água de resfriamento
4. agente-edificacoes ⇢ **agente-advisory** (Manta 15) — modelagem de OpEx do TIER III
5. agente-edificacoes consolida com foco em desempenho + SLA

**Fronteira testada**: data center NÃO cai em S12 (não é refinaria).

---

## Cenário 5 — Túnel urbano de metrô com portal em terreno mole

**Input**: "Extensão da Linha 4-Amarela SP, novo trecho com túnel NATM
em solo mole + estação com poço de acesso VCA."

**Fluxo esperado**:
1. Maestro → **agente-tuneis** (S5) — "NATM", "poço de acesso"
2. agente-tuneis ⇢ **agente-infraestrutura-s4** (S4) — sistemas do metrô + estação
3. agente-tuneis ⇢ **agente-infraestrutura-s2** (S2) — OAE do portal (se aplicável)
4. agente-tuneis alerta sobre necessidade de método observacional Peck (solo mole)
5. agente-tuneis consolida com convergência-confinamento

**Fronteira testada**: hoje S5 era "coberto por S2+S4". Após v4.4 tem
agente próprio — deve dominar a resposta, não apenas repassar.

---

## Cenário 6 — Barragem de rejeitos existente com descaracterização

**Input**: "Alteamento a montante em Nova Lima, PoV do dono da mina —
plano de descaracterização até 2027 conforme Lei 14.066."

**Fluxo esperado**:
1. Maestro → **agente-barragens** (S10) — "alteamento montante", "Lei 14.066"
2. agente-barragens ⇢ **agente-mineracao** (S11) — para conflitos com plano de lavra
3. agente-barragens → **agente-contratual** (Manta 02) — compliance ANM Res 95
4. agente-barragens consolida com cronograma físico + PAE/PAEBM
5. agente-barragens cita **KEs acadêmicos** (Mendes 2022 alteamento crítica, Fernandes 2020 dry stack)

**Fronteira testada**: quem lidera é S10 (rejeitos = disposto). S11
entra como consultor. NÃO invertido.

---

## Cenário 7 — Aeroporto regional amazônico

**Input**: "Novo aeródromo regional em Coari-AM, aeronave crítica ATR
72-600. Concessão federal fase 3."

**Fluxo esperado**:
1. Maestro → **agente-aeroportos** (S7)
2. agente-aeroportos ⇢ **agente-saneamento** (S8) — abastecimento remoto + esgoto do TPS
3. agente-aeroportos ⇢ **agente-energia** (S9) — subestação isolada + gerador de emergência
4. agente-aeroportos cita **KE acadêmico** Pereira 2021 (crítica ao superdimensionamento em regionais amazônicos)
5. agente-aeroportos consolida com FCL corrigido pela ATRA

---

## Cenário 8 — Adutora AySA em obra + estação de bombeamento

**Input**: "AySA — adutora dn 1200 mm de 15 km com EEAB intermediária.
Zona norte de Buenos Aires."

**Fluxo esperado**:
1. Maestro → **agente-saneamento** (S8) — "AySA", "adutora", "EEAB"
2. agente-saneamento → **agente-energia** (S9) — alimentação da EEAB
3. agente-saneamento ⇢ **agente-tuneis** (S5) SE travessia por HDD (perfuração direcional) em rio
4. agente-saneamento ⇢ **agente-orcamento** (Manta 05) — SICRO/TPU para custos BR ≠ pesos argentinos
5. agente-saneamento consolida com PIRHA como framework regulatório

**Fronteira testada**: PRIORIDADE AySA é do S8 (metadata no SKILL).
Não é jogado para S1 (rodovia) ou S12 (adução de óleo).

---

## Como usar este playbook

### Manual (hoje)

Para cada cenário, um operador MN:
1. Envia o **input do usuário** ao Maestro em uma sessão limpa (sem contexto anterior).
2. Observa qual agente PRIMEIRO responde (deveria bater com o esperado).
3. Verifica handoffs emitidos (deveriam cobrir a lista `→` e `⇢`).
4. Checa que a resposta final consolida e cita corretamente.
5. Marca ✓ ou ✗ em uma tabela de resultados.

### Automatizado (futuro)

Backlog: um GitHub Action que roda a cada release do CLAUDE.md master,
executando os 8 cenários contra o Maestro em staging, validando as
regras acima via LLM-as-a-judge (Claude Sonnet 4.6 avaliando se a
resposta cumpre os critérios). Falha o build se ≥1 cenário quebrar.

Referência de estado da arte: Chen et al. (2024) "AgentBench: Evaluating
LLMs as Agents" — método análogo aplicado ao AgentVerse. Adaptar
critérios ao domínio brasileiro de engenharia civil consultiva.

---

## Ver também

- `CLAUDE.md` v4.5 (mapa de agentes + routing do Maestro)
- `sharepoint/01-agentes-fundamentais/<agente>/README.md` — cada agente
  lista seus handoffs frequentes
- `supabase/migrations/2026_07_12_akp_telemetry.sql` — a view
  `v_akp_similarity_health` deve mostrar todos os segmentos verdes após
  8/8 cenários passarem
- `supabase/migrations/2026_07_12_akp_governance_v4_5.sql` — table
  `agent_fallback_events` (v4.3 telemetry) grava fallbacks em produção
  para comparar com o playbook aqui
