# Gaps, decisões e checklists do Manta Maestro

> Extraído do `CLAUDE.md` na v5.5.0 (2026-09-26), sem alteração de
> conteúdo. Leitura sob demanda — só quando a tarefa envolve uma
> pendência, decisão MN ou o checklist de deploy.

## MODELO MESTRE DE PROPOSTA

> 🔴 **Atualização 2026-09-10**: a seção "Variante Tipo A / Concessão de
> Infraestrutura de Grande Porte", hoje viva na skill real
> (`02-atividades/A1-proposta/SKILL.md`, v3.3.5), foi confirmada como
> **recorrência da fabricação** corrigida abaixo — reproduz quase
> palavra-por-palavra o addendum fabricado deste repositório e cita a
> mesma revisão inexistente `MNT-2026-COM-1183_D`. Nenhuma escrita foi
> feita na skill; ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`
> ("Recorrência confirmada — Variante Tipo A") para a evidência
> completa e a recomendação ao MN.

> ⚠️ **Correção 2026-09-07**: a versão anterior desta seção (histórico
> abaixo) descrevia a skill `proposta-comercial` como tendo 18 seções,
> um "agente A7-bd" e um modo "M6" validado contra
> "MNT-2026-COM-1183_D" — nada disso bate com a skill real de
> produção. Com acesso real ao SharePoint (`SharePoint_Manta` MCP)
> nesta sessão, confirmamos que a skill real
> (`04_IA/Manta-Maestro/05-sub-skills/skill-proposta-comercial-SKILL.md`)
> tem **14 seções**, **5 modos (M1–M5)**, tabela de **12 níveis** e
> referência real **Hope PPP MNT-2025-COM-1104**; a revisão mais
> recente de MNT-2026-COM-1183 encontrada é **"_C"**, não "_D". Detalhe
> completo em `docs/MODELO-MESTRE-PROPOSTA.md`.

A ideia central (segregar **Tarifa** × **Success Fee** na seção de
Preço, definir a **exigibilidade do success fee** pela **formalização**
do evento-gatilho — economia de custo → aprovação de orçamento;
conquista → formalização da conquista; cronograma → marco formalmente
aprovado — nunca pela implementação física, e acrescentar cláusula de
**multa, juros de mora e correção monetária** por atraso de pagamento)
**já foi aplicada na skill real** em 2026-09-07, a pedido do usuário —
reescrita no formato verdadeiro dela.

> ⚠️ **A skill mudou de lugar de novo, no mesmo dia (2026-09-07/08)**:
> horas depois da correção acima, uma confusão de caminho reportada por
> outra sessão Claude disparou um saneamento estrutural real do
> SharePoint. A skill foi fundida em
> `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (v3.3.0),
> puxando um pacote de conteúdo anterior à correção — **sem** as
> cláusulas acima. Reaplicadas nesta sessão como **v3.3.1** no novo
> caminho real (16.191 bytes, verificado por leitura pós-upload).
> `05-sub-skills/skill-proposta-comercial-SKILL.md` **não é mais a
> fonte** — virou um ponteiro de descontinuação. Detalhe completo em
> `docs/MODELO-MESTRE-PROPOSTA.md` §3. **O SharePoint real está sendo
> editado por múltiplas sessões em paralelo** — antes de editar essa
> skill de novo, sempre reler o arquivo primeiro.

Detalhe e checklist real em `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`
(o addendum original de "18 seções/M6" está lá marcado como
histórico/não aplicável).

Pendências: (1) revisão jurídica dos percentuais padrão de multa/juros/
correção monetária antes do próximo uso real em proposta de cliente;
(2) confirmar se existe cópia local da skill sincronizada por
`Sync-MantaMaestro.ps1` que precise do mesmo texto, para não ser
sobrescrita no próximo sync a partir da máquina local do usuário; (3)
reconciliação arquitetural mais ampla entre este repositório e o
SharePoint real — ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.

---

## GAPS ABERTOS / PENDÊNCIAS

- **🟡 Este repositório diverge do Manta Maestro real no SharePoint
  (encontrado em 2026-09-07 — numeração e embedder já corrigidos,
  resto aberto)**: com acesso real de leitura/escrita ao
  `SharePoint_Manta` MCP nesta sessão, confirmamos que a arquitetura
  real em produção (`09-base-conhecimento/INDICE-CANONICAL.md` +
  `00-arquitetura/manta-maestro-arquitetura-v3.0.md`/`v3.2.md` +
  `09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md`) é **diferente**
  da descrita neste `CLAUDE.md` em vários pontos — já corrigidos: skill
  `proposta-comercial` (ver "Modelo Mestre de Proposta"), numeração de
  segmentos (ver "Eixo S — Segmentos"), embedder G010 (ver Gaps
  abertos). **Investigação mais funda revelou que o núcleo
  Supabase/RAG é real** (projeto `ogxxgvgtulrbbppshjie`, confirmado por
  chamadas reais de API), só com especificações diferentes das
  assumidas aqui (agendamento real é `cron` Linux, não APScheduler;
  nomes de tabela diferem em partes) — mas **sem evidência real
  encontrada** para ML routing/XGBoost, consensus voting, disaster
  recovery, Docker/K8s, "Maestro OS v6.0" e a numeração "20+ agentes
  Manta NN". Análise completa e o que falta investigar em
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`. Ação: decisão MN sobre
  as próximas fases (numeração — concluída; embedder — concluído;
  renumerar frontmatter dos agentes, corrigir specs de Supabase/RAG, e
  decidir o destino do que não tem lastro real — ainda não escopadas).
- ~~**S5 (Imobiliário) sem vertical dedicado**~~ — **corrigido em
  2026-09-11, decisão fechada em 2026-09-13**: leitura ao vivo confirma
  que `agente-S5-imobiliario` já existe no SharePoint real, maduro
  (v3.0.0, 5 sub-agentes: viabilidade, incorporação/patrimônio de
  afetação, avaliação, gestão de empreendimento, exit/securitização).
  A pergunta "criar vertical ou não" está respondida — já existe. A
  sobreposição de escopo com Manta 04 (horizontal de negócio
  imobiliário) foi levada ao MN, que decidiu **manter os dois
  coexistindo como estão hoje, sem reconciliação de escopo por
  enquanto** — não é uma pendência ativa. Ver
  `docs/PLANEJAMENTO-MANTA-MAESTRO.md` §2.
- **`agente-oleo-gas` (S14) e `agente-mineracao` (S13) — confirmados
  reais e maduros em 2026-09-11, mas com um bug de metadado sério**:
  releitura direta de `INDICE-CANONICAL.md` v1.1 e dos próprios
  `SKILL.md` mostrou que o índice real vai até S14 (não S11) e que os
  três segmentos mais novos (S12-Túneis, S13-Mineração, S14-Óleo e Gás)
  já têm agentes de produção completos (`agente-tuneis`,
  `agente-mineracao`, `agente-oleo-gas`, todos v1.0.0). **Achado mais
  sério**: cada um carrega um campo `manta_code` legado que colide com
  o código real de OUTRO segmento — S13 diz internamente "Manta
  03-S11" (código real de Barragens), S14 diz "Manta 03-S12" (código
  real de Túneis), S12 diz "Manta 03-S5" (código antigo de si mesmo).
  Segmentos mais antigos (S9, S11) não têm esse campo legado — é
  isolado aos 3 mais novos, herdado do template `agente-infraestrutura
  v1.0.0` nunca migrado. **Se o routing de produção real ainda ler
  `manta_code` em vez de `sp_operational_segment`, isso é um bug de
  misroteamento ativo** (pergunta sobre óleo e gás → agente de túneis).
  Ação: MN confirmar com quem opera o Maestro real qual campo o
  routing efetivamente consome — prioridade alta. Detalhe completo em
  `docs/PLANEJAMENTO-MANTA-MAESTRO.md` §3.
  `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md` e
  `docs/SEGMENTOS-S12-S13-DECISION.md` mantidos como histórico do
  raciocínio anterior (usavam códigos que não correspondem aos reais).
- **D03-Geotecnia — confirmado maduro em produção, proposta de agente
  "Manta 17/geotecnia" descartada (2026-09-11)**: uma sessão anterior
  chegou a rascunhar um agente horizontal dedicado a geotecnia partindo
  da premissa "nenhum agente cobre isso hoje". Leitura ao vivo do
  `SKILL.md` real de `D03-Geotecnia` (v2.0.0) mostrou que essa premissa
  era falsa — a disciplina já existe, madura, com normas, fórmulas,
  red flags e handoffs formalizados para S1/S2/S3/S4/S8/S11. A
  proposta de agente foi descartada sem merge. Uma segunda correção
  (também 2026-09-11): S12-Túneis **não** depende de D03 como se
  pensou inicialmente — já tem geotecnia própria internalizada; o gap
  real é um possível drift de método entre D03 e essa geotecnia
  interna, não uma lacuna de listagem. Guia completo em
  `docs/D03-GEOTECNIA-APLICACAO-PROJETOS-MANTA.md`.
- ~~**Embedder (G010)**~~ — **✅ resolvido em 2026-09-07** com decisão
  real: `09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md` (SharePoint
  real, lido via `SharePoint_Manta` MCP) confirma que `bge-m3` foi
  avaliado em 24/07/2026 e **explicitamente rejeitado**, e
  `bge-small-en-v1.5` (384-d) foi **confirmado canônico em 26/07/2026**.
  O comentário de coluna que `docs/SUPABASE-PROJECT-AUDIT.md` citou
  como evidência de "schema já é bge-m3" é de 03/07/2026 — **anterior**
  à decisão real e ficou desatualizado, não reflete o estado atual.
  `docs/EMBEDDER-DECISION.md` (que recomendava migrar para bge-m3) e
  `docs/SUPABASE-PROJECT-AUDIT.md` foram corrigidos com essa
  informação. Achado relevante: **o projeto Supabase
  `ogxxgvgtulrbbppshjie` é real** (mesma conta `mneves@
  mantaassociados.com`, confirmado por chamadas reais de API na
  auditoria G012) — a infraestrutura RAG básica existe de verdade,
  ainda que com specs diferentes das assumidas em partes deste
  repositório. Ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.
- **Supabase — projeto `xgluoaaymbdzbbudnwrh` (G012)**: auditoria real
  (`docs/SUPABASE-PROJECT-AUDIT.md`) concluiu, com evidência de API,
  que é provavelmente referência morta (projeto não pertence à
  organização Supabase ativa da conta corporativa). **Confirmação
  humana (dashboard) ainda pendente** antes de remover a referência —
  ver action items AI-1 a AI-10 nesse documento.
- **RLS desabilitado em 3 tabelas públicas** (`rag_collections`,
  `sp_agent_routing`, `maestro_routing_keywords`) — achado de segurança
  correlato da auditoria G012, com SQL de remediação já redigido mas
  **não aplicado** (requer policies de leitura corretas antes de
  habilitar RLS, para não quebrar o acesso do próprio Maestro em
  runtime). Ver AI-6 em `docs/SUPABASE-PROJECT-AUDIT.md`.
- **3 projetos Supabase `INACTIVE`** (`manta-tocantins`,
  `manta-rodovias`, `manta-portal-piloto`) — decisão de consolidar,
  arquivar ou manter pendente MN (ver AI-7/AI-8 no mesmo documento).
- **A9 (Regulatório) e A10 (Risco)**: sem Manta-code horizontal
  dedicado — ver Eixo A.
- **Edificações (S6) e Óleo & Gás sem RAG, sem rota SharePoint, sem
  keyword de routing** — agentes existem como arquivo, mas não são
  despacháveis pelo Maestro hoje.
- **Templates Motiva sem upload real para o SharePoint da equipe**:
  `docs/templates/EAP-PADRAO-MOTIVA.xlsx` e
  `PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx` existem versionados
  neste repositório e já estão referenciados no routing e nos agentes
  de output (v5.4), mas ainda não foram copiados para
  `sites/Engenharia/.../04_IA/Manta-Maestro/` onde a equipe de fato
  trabalha. **Atualização 2026-09-07**: esta sessão passou a ter
  acesso real de escrita ao SharePoint (`SharePoint_Manta` MCP) — a
  limitação de "MCP somente leitura" registrada em `docs/DEPLOY-v4.2.md`
  não se aplica mais a partir de agora; o upload em si não foi feito
  nesta sessão (fora do escopo combinado, que era só a correção de
  numeração de segmento) mas deixou de depender de acesso externo.
- **Cor institucional da Motiva não confirmada** — ver seção 5 de
  `docs/PADRAO-OUTPUT-MOTIVA.md`; templates usam paleta neutra Manta
  até confirmação do cliente.

---

## QUESTIONÁRIO DE DECISÃO PARA MN

1. ~~**Numeração de segmento**~~ — **decidido em 2026-09-07**: adota-se
   a numeração real do SharePoint (`INDICE-CANONICAL.md`), a mesma que
   este arquivo chamava de "Convenção B". Aplicado nesta versão (ver
   "Eixo S — Segmentos"). Renumeração dos 5 agentes operacionais
   (frontmatter interno de cada `.md`) e da migração/RAG/rotas SP
   segue como próxima fase, ainda não feita.
2. ~~**Óleo & Gás e Mineração sem segmento real confirmado**~~ — **em
   grande parte respondido em 2026-09-11**: leitura ao vivo confirma
   `agente-oleo-gas` (S14) e `agente-mineracao` (S13) já existem,
   maduros, em produção — não precisam ser formalizados, só espelhados
   neste repositório. **Nova questão aberta, mais séria**: os três
   segmentos mais novos (S12/S13/S14) carregam um campo `manta_code`
   legado que colide com o código real de OUTRO segmento (S13 diz
   internamente "Manta 03-S11", que é Barragens; S14 diz "Manta
   03-S12", que é Túneis). Se o routing de produção real ainda ler
   `manta_code` em vez de `sp_operational_segment`, isso é um bug de
   misroteamento ativo, não só uma inconsistência documental — MN
   confirmar com quem opera o Maestro real qual campo o routing
   efetivamente consome. Ver `docs/PLANEJAMENTO-MANTA-MAESTRO.md` §3.
3. ~~**S5 Imobiliário**~~ — **respondido em 2026-09-11, fechado em
   2026-09-13**: o vertical S5 já existe, maduro (v3.0.0, 5
   sub-agentes), no SharePoint real. MN decidiu manter S5 (vertical) e
   Manta 04 (horizontal) coexistindo como estão hoje, sem reconciliação
   de escopo por enquanto.
4. ~~**D21 — taxonomia**~~ — **decidido em 2026-09-13**: prevalece a
   numeração D01–D22 já usada neste repositório. O candidato real do
   SharePoint (rotulado internamente "D21/Manta 51") precisa ser
   renumerado ou descontinuado para bater com essa decisão — ação
   ainda não executada na fonte real, pendente de quem mantém aquele
   candidato. Ver `docs/PLANEJAMENTO-MANTA-MAESTRO.md` §2.
5. **Embedder**: antes de decidir bge-small vs. bge-m3, confirmar a
   dimensão real da coluna de vetor em produção — a decisão atual
   (`docs/EMBEDDER-DECISION.md`) parte de uma premissa não verificada
   contra o achado da auditoria Supabase.
6. **Projeto Supabase `xgluoaa...`**: autorizar confirmação manual via
   dashboard (AI-1) antes de remover a referência do SKILL.md?
7. **Timeline de merge**: em qual sprint este v5.0 vai para `main`?

---

## DEPLOY CHECKLIST v5.0

Checklist completo e detalhado em `docs/DEPLOY-CHECKLIST-v5.0.md`
(herda o checklist v4.2, ainda com 8/10 itens pendentes fora do git, e
adiciona a sequência de consolidação/validação da v5.0). Resumo:

- [x] Consolidar modelo de 4 eixos (S×A×F×D) no CLAUDE.md master
- [x] ~~Reconciliar divergência de numeração de segmento (Convenção A)~~
      — **revertido em 2026-09-07**: a "Convenção A" era a numeração
      errada; a real (SharePoint) é a que este item chamava de
      "Convenção B". Ver checklist de correção logo abaixo.
- [x] Corrigir tabela de coleções RAG com dados de auditoria real (9 confirmadas — nota: fonte dessa "auditoria" é parte da infraestrutura Supabase ainda não confirmada como real, ver `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`)
- [x] ~~Registrar S12 (Óleo & Gás) e S13 (Edificações) como propostos~~ — Edificações renumerado para S6 (real); Óleo & Gás segue sem S confirmado
- [x] ~~Identificar S11 (Mineração) a partir de `manta_agent_capabilities`~~ — fonte não confirmada como real; S11 real é Barragens
- [x] Linkar Eixo A/F/D aos documentos dedicados já produzidos
- [x] ~~Corrigir numeração de segmento em `docs/DISCIPLINAS-D01-D20.md`, `docs/ATIVIDADES-A1-A10.md` e `agente-aeroportos.v5.0.md` (Convenção B → A)~~ — **não era necessário**: esses arquivos já usavam a numeração correta (real)
- [x] Abrir gap G015 — documentação de formalização S11 (Mineração) em `docs/SEGMENTO-S11-MINERACAO-GAP-G015.md` (mantido como histórico)
- [ ] Reconciliar `docs/EMBEDDER-DECISION.md` com achado de
      `docs/SUPABASE-PROJECT-AUDIT.md` antes de decidir embedder
- [ ] Confirmar manualmente o destino do projeto `xgluoaa...` (AI-1)
- [ ] Aplicar RLS nas 3 tabelas expostas (AI-6)
- [ ] Criar RAG + rota SP + routing keywords para Edificações (S6) e Óleo & Gás (se aprovado)
- [ ] Rodar aluci-guard sobre este documento antes de merge
- [ ] Rodar consist-guard sobre este documento antes de merge
- [ ] Gate humano: aprovação MN antes de merge

### Correção de numeração de segmento (2026-09-07, fase 1 da reconciliação com o SharePoint real)

- [x] Ler `INDICE-CANONICAL.md` real via `SharePoint_Manta` MCP e
      confirmar a numeração real (S1–S11, Edificações=S6…Barragens=S11)
- [x] Reescrever tabela "Eixo S — Segmentos" com a numeração real
- [x] Atualizar "Mapa completo de agentes" (verticais), "Modelo de
      composição S.A.D", "ROUTING", "RAG", "SharePoint routing rules"
      com os novos códigos
- [x] Remover a nota de "inconsistência" em Eixo D (os arquivos já
      estavam certos)
- [x] Atualizar Gaps abertos e Questionário MN
- [ ] Renumerar o frontmatter interno dos 5 agentes verticais afetados
      (`agente-portos.md` S6→S7, `agente-aeroportos.md` S7→S8,
      `agente-saneamento.md` S8→S9, `agente-energia.md` S9→S10,
      `agente-barragens.md` S10→S11, `agente-edificacoes.md` S13→S6) —
      **fora do escopo desta fase**, próxima fase da reconciliação
- [ ] Renomear/atualizar migrações SQL e nomes de arquivo que citam a
      numeração antiga (`2026_07_05_v4_2_agents_s6_s10.sql`,
      `2026_07_31_v4_3_agents_s12_s13.sql`) — fora do escopo desta fase
- [ ] Reconciliação mais ampla (infraestrutura Supabase/APScheduler/ML
      fictícia vs. estrutura real de `SKILL.md`) — ver
      `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`, fases seguintes ainda
      não escopadas

---
