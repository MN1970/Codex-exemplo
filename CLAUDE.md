# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
Saneamento, Energia, Barragens). Histórico completo em `CHANGELOG.md`.

Arquitetura detalhada (5 camadas, model tiering, diagramas de fluxo):
`sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`. Este arquivo
mantém apenas o registro operacional que o Maestro consulta em runtime
(mapa de agentes + regras de routing) — mantenha-o enxuto.

---

## MAPA COMPLETO DE AGENTES — 20 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional |

### Eixo 2 — Verticais por segmento (C3)

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| Manta 03-S6 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | 🆕 Criado 2026-07-05 |
| Manta 03-S8 | Saneamento | agente-saneamento | 🆕 Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | 🆕 Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | 🆕 Criado 2026-07-05 |

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais suportam as 8 fases via intake Q2:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento atualizada para Q1 do intake. **Fonte única** —
não duplicar este bloco em outro arquivo; referenciar por link.

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS|PMSB
   → agente-saneamento (S8)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE|condutor|ampacidade|ACSR
   → agente-energia (S9)

IF menção a porto|terminal|ANTAQ|dragagem|molhe|quebra-mar|berço|calado|contêiner|granel|PIANC
   → agente-portos (S6)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento|RBAC|PCN|pátio de aeronaves|carga aérea
   → agente-aeroportos (S7)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF|dam breach|SIGBM|ANM|rompimento
   → agente-barragens (S10)

# Regras existentes S1-S4 mantidas sem alteração
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4
```

Keywords adicionadas em 2026-08-12 após smoke test (`tests/routing/prompts.md`)
revelar ~20% de falha de match literal nos prompts de exemplo. Mesma
lista replicada em `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`
(`maestro_routing_keywords`) — atualizar os dois juntos até o Maestro
carregar keywords de uma fonte única.

### Regra de desempate — múltiplos matches

O bloco acima é uma lista plana de `IF`s independentes: mais de uma
regra pode bater no mesmo prompt (ex.: "barragem CFRD + LT 500kV").
Quando isso acontecer:

1. O agente cujo match representa a **estrutura principal** do pedido
   (o ativo sendo projetado/operado/analisado) é o despacho
   **primário**.
2. Qualquer outro agente cujo match represente uma interligação ou
   insumo de suporte (alimentação elétrica, adução de água, travessia)
   recebe **handoff automático** — nunca fica sem resposta.
3. Em caso de empate real (nenhum dos dois é claramente "principal"),
   usar a ordem de prioridade: barragens (S10) > energia (S9) >
   saneamento (S8) > aeroportos (S7) > portos (S6) > metrô (S4) >
   ferrovia (S3) > OAE (S2) > rodovias (S1) — infraestrutura crítica
   de maior risco regulatório primeiro.
4. Casos de referência já resolvidos por esta regra — ver
   `tests/routing/prompts.md` §Casos ambíguos:
   - UHE (barragem + LT) → **agente-barragens** primário + handoff
     **agente-energia**.
   - ETE + subestação → **agente-saneamento** primário + handoff
     **agente-energia**.
   - Porto + pista de carga aérea → **agente-portos** primário +
     handoff **agente-aeroportos**.
   - Adutora + barragem de rejeitos → **agente-saneamento** primário +
     consulta técnica ao **agente-barragens**.

---

## RAG e SharePoint — coleções por vertical

5 coleções novas (v4.2): `saneamento` (`san:`), `energia` (`ene:`),
`portos` (`por:`), `aeroportos` (`aer:`), `barragens` (`bar:`) — cada
uma mapeada para `03_Projetos/<Segmento>/*` no SharePoint.

Detalhe completo (fontes, sub-prefixos, patterns de arquivo):
`ARQUITETURA-AGENTES-IA.md` §7-8. Migração: `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`.

---

## Deploy e histórico

- Checklist de deploy (Supabase, SharePoint, testes de routing):
  `docs/DEPLOY-v4.2.md`.
- Histórico completo de versões: `CHANGELOG.md`.
- Definições canônicas dos 5 agentes verticais v4.2:
  `.claude/agents/agente-{portos,aeroportos,saneamento,energia,barragens}.md`
  (SKILL.md completo em `sharepoint/01-agentes-fundamentais/agente-<slug>/`).

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.
