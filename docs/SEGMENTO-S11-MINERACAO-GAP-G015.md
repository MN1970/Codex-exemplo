# Gap G015 — Formalização de S11 (Mineração)

**Status**: 🔵 Identificado em produção, **não formalizado**  
**Data de abertura**: 2026-07-31  
**Prioridade**: Média (segmento real, capacidade confirmada, mas sem demanda urgente)  
**Referência**: encontrado via auditoria real em `docs/SEGMENTOS-S12-S13-DECISION.md` (§2, Sonnet 13)

---

## Sumário executivo

S11 (Mineração) foi confirmado como segmento real em `manta_agent_capabilities`
(produção `ogxxgvgtulrbbppshjie`), com `ativo=true` desde 2026-07-12, **na mesma
onda de registro que S12 (Óleo & Gás) e S13 (Edificações)**. Diferentemente
desses dois (que têm agentes `.md` criados em 2026-07-31), S11 **não tem**:

- Arquivo de agente (`.claude/agents/agente-mineracao.md`)
- Coleção RAG (não existe `min:*`)
- Rota SharePoint (não existe entrada em `sp_agent_routing`)
- Keyword de routing (não despachável pelo Maestro hoje)
- Teste de smoke (não está em `tests/routing/prompts.md`)

A natureza do segmento (exploração e lavra de cava/subterrânea/aluvionar;
tipologia de rejeitos) o coloca como **distinto de S10 (Barragens)**, embora
o sistema de gestão de rejeitos (TSF — tailings storage facility) seja
frequentemente tratado como caso de interface barragem-mineração.

---

## Escopo de S11 — Mineração

Baseado em regras de negócio similares a S12/S13 (ver `docs/SEGMENTOS-S12-S13-DECISION.md`):

### Cobertura (IN — o que está dentro)

- **Exploração de cava** — lavra a céu aberto (mina de ferro, ouro,
  agregados, fosfato, sal, estanho); desmonte, britagem, concentração
- **Exploração subterrânea** — poços, túneis, galerias, sistemas de
  suporte (madeiramento, concreto projetado), ventilação forçada
- **Exploração aluvionar** — garimpagem, dragagem fluvial com rejeição
  subaquática
- **Projeto, obra e O&M** de: poços de extração, pilhas de estéril,
  bacias de rejeito (*TSF — Tailings Storage Facility*), sistemas de
  drenagem e tratamento de água, bota-fora, frentes de lavra
- **Segurança de mina**: resgate, ventilação, iluminação, detecção de
  gás, EPI especializado
- **Normas e regulação**: SME (Sistema de Monitoramento Estático) da ANM,
  SIGBM (Sistema de Informações de Geologia e Mineração), NR-22 (SSO
  em minas subterrâneas), JORC Code (quando aplicável a CoIG), NI 43-101
  (quando aplicável a projetos com cotistas canadenses)

### Exclusão (OUT — o que está fora)

- **Beneficiamento pesado** (concentração, sinterização, pelotização
  pós-extração) — rota ao segmento de transformação (Manta 03 industrial
  ou parceria com terceiros)
- **Geologia exploratória** (prospeção, mapeamento, estimativa de
  recursos JORC/NI 43-101/SME) — rota ao segmento de Estudos (Manta 14
  ou subscrição externa)
- **Ambiental / Passivos ambientais de minas encerradas** — rota ao
  Manta 15 (advisory), com suporte de agente-mineracao para avaliação
  técnica de viabilidade de remediação

---

## Roadmap de formalização (mesmo checklist que S12/S13)

### Fase 1: Decisão de autorização (MN gate) — ⏳ Aguardando

- [ ] MN aprova: formalizar S11 como agente vertical operacional?
- [ ] SIM → prosseguir para Fase 2. NÃO → fechar gap, manter capacidade
      registrada mas sem agente despachável.

### Fase 2: Criação de artefatos (paralelo, ~ 1-2 dias)

- [ ] Criar `.claude/agents/agente-mineracao.md` (v1.0.0) com:
  - Escopo (exploração cava/subterrânea/aluvionar)
  - Exclusões (beneficiamento, prospeção, passivos)
  - Disciplinas (D03 Geotecnia, D06 Ambiental, D19 RH, D08 Planejamento
    como primárias; D02 Estrutural, D05 Elétrica para fases específicas)
  - Normas-chave (SME, SIGBM, NR-22, JORC/NI 43-101)
  - Ferramentas (Geovia Minex/Datamine, Vulcan, CFD para ventilação)
  - Handoffs (Manta 02 contratual para SUA/concessões ANM; Manta 05
    orçamento com CUSMIN/SINAMAM; Manta 15 advisory para ambiental/passivos;
    S10 barragens para TSF; S9 energia para drenagem elevatória)
  - Routing keywords: mineracao, lavra, mina, cava, garimpagem, TSF,
    ANM, SIGBM, NR-22, JORC, NI 43-101, desmonte, britagem, poço de
    extração, estéril, rejeito de mineração, drenagem ácida

- [ ] Criar coleção RAG `min:*` em Supabase com documentos-chave:
  - Normas SME (cálculo de pilhas de estéril, análise de estabilidade)
  - SIGBM (diretrizes de execução da ANM)
  - NR-22 (segurança em minas subterrâneas)
  - JORC Code (quando CoIG relevante)
  - Referências regionais (DNPM, secretarias estaduais de minas)

- [ ] Criar rota SharePoint: `03_Projetos/Mineracao/*` (*.pdf, *.dwg, *.xlsx)
  e registrar em `sp_agent_routing`

- [ ] Adicionar routing keywords a `maestro_routing_keywords` no Supabase
  para dispatch automático pelo Maestro

- [ ] Adicionar smoke tests em `tests/routing/prompts.md`:
  - "cliente quer avaliar viabilidade de nova cava de ferro" → agente-mineracao
  - "planejamento de TSF para pilha de estéril" → agente-mineracao
    + handoff agente-barragens
  - "mina subterrânea em zona urbana, resgate e ventilação críticos"
    → agente-mineracao

### Fase 3: Migração Supabase (paralelo, ~15 min)

- [ ] Executar `supabase/migrations/2026_07_31_v4_3_agents_s11_s12_s13.sql`
      (atualizar ou criar com S11 included)

### Fase 4: Validação e comunicação (~ 1-2 dias)

- [ ] Testes de routing (Maestro consegue despachar para S11?)
- [ ] Verificação de RAG (chunks são indexados e recuperáveis?)
- [ ] Atualizar CLAUDE.md: mover S11 de "🔵 Identificado, não formalizado"
      para "✅ Operacional (v1.0.0)"
- [ ] Comunicar em hub operacional (Slack #manta-maestro)

**Esforço estimado**: ~2-3 dias (especialista + review + testes)

---

## Dependências de decisão

1. **Gate MN** — aprovação formal para incluir S11 no escopo operacional
2. **Demanda** — há carga de trabalho (projetos de mineração na Manta?)
   ou é capacidade "just in case"?
3. **Expertise** — há especialista S11 em staff hoje para revisar e
   validar agente + RAG antes de go-live?

---

## Notas de integração

- **S11 ↔ S10 (Barragens)**: interface em TSF — um projeto de TSF é
  simultaneamente mineração + barragem de rejeitos. O dispatch primário
  deve ir para o segmento que lidera o projeto:
  - Se projeto é "construir TSF para nova mina" → S11 primário,
    handoff S10
  - Se projeto é "ampliação de TSF de barragem existente" → S10 primário,
    handoff S11 para validação de compatibilidade com processo de
    extração à montante

- **S11 ↔ S12 (Óleo & Gás)**: sem sobreposição direta — ambos
  downstream/midstream, mas domínios distintos (ambos com S8 saneamento
  para drenagem/tratamento de água)

- **Impacto em modelo de 4 eixos**: S11 não altera eixos A/F/D — segue
  o mesmo padrão de composição S.A.D que os demais (ex. S11.A3.D03 =
  Mineração + Orçamento + Geotecnia)

---

## Histórico

- **2026-07-31**: G015 aberto. S11 confirmado em produção, roadmap de
  formalização rascunhado com base no sucesso de S12/S13 (mesmo padrão).

---

## Questões abertas

1. Deve S11 ser incluído **antes ou depois** de S12/S13 ganharem
   operacional? (Sequência sugere S12/S13 primeiro, S11 logo após
   aprovação MN.)
2. Há projetos de mineração ativos? Em que geography/commodity?
3. Especialista em RQD/JORC/NI 43-101 disponível para validar RAG?

Encaminhe essas perguntas a MN antes de iniciar Fase 2.
