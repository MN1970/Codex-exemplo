# FUNCIONAIS-F1-F8.md

**Sistema Manta Maestro — Eixo F (Funcionais transversais)**

- **Versão**: 1.0.0
- **Data**: 2026-07-31
- **Autor**: Manta Associados
- **Relacionado a**: `CLAUDE.md` v4.2 (registro mestre, Eixos 1-3),
  `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` v2.0.0

---

## Sumário

- [0. Visão geral do Eixo F](#0-visão-geral-do-eixo-f)
- [F1 — IA](#f1--ia-routing-model-tiering-scaling-prompting)
- [F2 — SharePoint](#f2--sharepoint-indexação-sync-storage-por-agente-permissões-versioning)
- [F3 — Portal](#f3--portal-interface-web-sso-autenticação-rbac)
- [F4 — Extração](#f4--extração-parser-pdfdwg-ocr-nlp-entity-extraction-validation)
- [F5 — Notificação](#f5--notificação-email-slack-webhook-subscriptions-templates)
- [F6 — Trace](#f6--trace-audit-log-approval-gates-workflow-versioning-history)
- [F7 — Guardrails](#f7--guardrails-aluci-guard-consist-guard-context-guardian)
- [F8 — Padronização](#f8--padronização-style-guide-templates-nomenclatura-conventions-checkpoints)
- [Matriz de status consolidada](#matriz-de-status-consolidada)
- [Interdependências entre Funcionais](#interdependências-entre-funcionais)
- [Histórico de versões](#histórico-de-versões)

---

## 0. Visão geral do Eixo F

O `CLAUDE.md` mestre descreve o sistema em **3 eixos**: horizontais
(agentes transversais), verticais (segmentos S1-S10) e ciclo de vida
(8 fases). Esses eixos respondem **quem** atua e **sobre o quê**.

O **Eixo F (Funcionais)** é ortogonal — descreve **como** o sistema
funciona por baixo de qualquer agente ou segmento. Um agente vertical
(`agente-saneamento`) e um horizontal (`manta-05 orcamento`) consomem
os mesmos 8 Funcionais: ambos roteados por F1, ambos lêem/gravam em
F2, ambos acessíveis via F3, ambos extraem dados via F4, ambos
notificam via F5, ambos deixam rastro em F6, ambos são auditados por
F7 antes de virar entregável, e ambos seguem o style guide de F8.

```
   Eixo 1 (Horizontais) × Eixo 2 (Verticais) × Eixo 3 (Fases de vida)
                             │
                             ▼
   F1 IA │ F2 SharePoint │ F3 Portal │ F4 Extração │ F5 Notificação
   F6 Trace │ F7 Guardrails │ F8 Padronização
```

Cada Funcional segue o mesmo template: descrição, componentes,
integrações, exemplo de uso, API/interface, status.

---

## F1 — IA (routing, model tiering, scaling, prompting)

**Descrição.** Motor de decisão do Maestro (Manta 00): classifica a
consulta (Q1 segmento, Q2 fase de ciclo de vida, Q3 objetivo, Q4
formato de dados), escolhe agente(s) de destino e tier de modelo, e
mantém o roteamento estável na sessão, incluindo handoffs
declarativos entre agentes.

**Componentes**
- Router por keyword/regex sobre Q1 (bloco `IF menção a... → agente-X`
  no `CLAUDE.md`), com fallback semântico.
- Model tiering:

| Tier | Modelo | Uso | % chamadas |
|---|---|---|---|
| Triagem | Haiku | routing, intake, metadados | ~20% |
| Execução | Sonnet | análise técnica, redação, orçamento | ~70% |
| Complexo | Opus | claims complexos, arquitetura, 2ª opinião | ~10% |

- Scaling dinâmico: sessão começa em Haiku, escala para Sonnet ao
  entrar no agente, escala para Opus se detectar complexidade composta
  (claim + jurídico + técnico + financeiro).
- Biblioteca de prompts de teste: `tests/routing/prompts.md` (inclui
  casos ambíguos, ex. UHE = barragem + energia).

**Integrações** — lê o mapa/regras do `CLAUDE.md`; consulta RAG (F2)
por prefixo após decidir o segmento; aciona F7 antes de fechar output;
dispara handoffs para outros agentes sem retornar ao cliente.

**Exemplo de uso**
```
"ETE do sistema Riachuelo com problema de subestação"
→ Q1 = saneamento + energia → dispatch primário agente-saneamento (S8),
  handoff declarado agente-energia (S9)
```

**API/interface** — entrada: string livre + contexto de sessão. Saída:
`{ agente_primario, agentes_handoff[], tier, fase_ciclo_vida, confidence }`.
Critério de aprovação de routing: ≥90% dos prompts de teste caindo no
agente esperado (`docs/DEPLOY-v4.2.md`, seção 5).

**Status**: ✅ Operacional — routing ativo para os 20 agentes; model
tiering documentado no frontmatter de cada agente `.md`; scaling
dinâmico depende do orquestrador de runtime (fora deste repositório).

---

## F2 — SharePoint (indexação, sync, storage por agente, permissões, versioning)

**Descrição.** Camada de armazenamento documental — cada agente
vertical tem pasta canônica de projetos e pasta de definição
(`SKILL.md`, `README.md`, `refs/`, `prompts/`) em SharePoint Online,
acessadas via MCP.

**Componentes**
- Tabela `sp_agent_routing`: `agent_slug → sp_folder → file_patterns[]
  → priority` (ver `CLAUDE.md`, seção SharePoint routing).
- Árvore canônica: `03_Projetos/<Segmento>/*` (projetos) e
  `04_IA/Manta-Maestro/01-agentes-fundamentais/agente-<slug>/`
  (definição do agente).
- MCP (`mcp__SharePoint_Manta__*`): `list_libraries`, `list_folders`,
  `list_files`, `search_files`, `find_item`, `get_folder_tree`,
  `read_document`, `download_file`, `upload_file`, `create_folder`,
  `move_item`, `copy_item`, `rename_item`, `delete_item`,
  `update_metadata`, `get_file_metadata`, `get_library_columns`,
  `get_site_info`.
- Versioning nativo: todo `upload_file` gera nova versão; exclusão vai
  para lixeira recuperável.
- Permissões: modo delegado — escritas ocorrem como o usuário
  autenticado, respeitando ACLs do site.

**Integrações** — F1 consulta `sp_agent_routing` para saber onde
ler/escrever; F4 lê documentos via `read_document`/`download_file`;
F6 registra cada upload/update como evento de auditoria; F8 define
nomenclatura antes do `upload_file`.

**Exemplo de uso**
```
find_item("edital Suape ANTAQ") → read_document(item_id)
→ get_file_metadata(item_id)  # confirma versão vigente
→ upload_file(folder="03_Projetos/Portos/Suape/", name="Memorial-v2.docx")
```

**API/interface** — site `sites/Engenharia`, library `Documentos
Compartilhados`. Todo acesso passa pelo MCP `SharePoint_Manta` (sem
Graph API direta pelos agentes). Colunas custom checadas via
`get_library_columns` antes de `update_metadata`.

**Status**: ⚡ Parcial — leitura/busca operacional em produção;
escrita disponível via MCP, mas as 10 pastas da expansão v4.2 (5
agente + 5 projeto) ainda não foram criadas e `sp_agent_routing` ainda
não recebeu as 5 linhas novas (`docs/DEPLOY-v4.2.md`, seções 2-3).

---

## F3 — Portal (interface web, SSO, autenticação, RBAC, permissões granulares)

**Descrição.** Camada de apresentação web — portais de gestão de
projeto/contrato que consomem os agentes (F1) e os dados (F2/F4) por
trás de autenticação corporativa, com controle por papel e por objeto.

**Componentes**
- Portais de referência (skills que materializam F3):
  `portal-gestao-manta`, `portal-megaprojeto-builder`,
  `portal-metro-l4` — cada um cobre um recorte (gestão geral,
  megaprojeto FIDIC multi-módulo, portal de cliente/linha específico).
- SSO via identidade Microsoft 365 / Entra ID (mesma base do
  `get_me` do MCP `Microsoft_365`, compartilhada com F2).
- RBAC previsto: `viewer` (leitura), `analista` (edita, não publica),
  `gestor` (aprova gates de F6), `admin` (gerencia permissões
  granulares por projeto/cliente).
- Permissões granulares: por projeto (alocação no contrato), por
  segmento (S8 ≠ S10), por fase de ciclo de vida (claims/DD restritos
  a sócios).

**Integrações** — mesma requisição do usuário aciona o router de F1;
dashboards lêem/gravam via F2 (nunca storage paralelo); ações que
alteram estado geram evento em F6; aplica o design system de F8.

**Exemplo de uso**
```
gestor autentica via SSO (Entra ID) → RBAC libera contrato "Nova Ponte
Tocantins" → dashboard do GR-04 → aprovação registra timestamp e
identidade do aprovador em F6
```

**API/interface** — entry point de referência:
`hub.mantaassociados.com/askcad`. Autorização: matriz
`{papel} × {projeto/cliente} × {segmento} × {fase}` resolvida antes de
renderizar módulo.

**Status**: 🆕 Planejado/parcial — skills de portal existem como
geradores de artefato/dashboard, mas o portal único com SSO e RBAC
centralizados ainda não está consolidado; cada portal hoje é um
app/artefato independente por projeto.

---

## F4 — Extração (parser PDF/DWG, OCR, NLP, entity extraction, validation)

**Descrição.** Transforma documento não estruturado (PDF de edital,
DWG de projeto, planilha) em JSON canônico consumível pelos agentes
verticais — quantitativos, entidades técnicas (normas, SICRO,
parâmetros), texto pesquisável.

**Componentes**
- Parsers de documento: skill `pdf` (texto/tabelas, OCR, merge/split,
  formulários).
- Parsers CAD/BIM: `autodesk-toolkit` (DXF/DWG/IFC/RVT sem software
  Autodesk instalado), `cqp-cad-bridge` (disciplinas/layers/
  quantitativos → schema `cqp-artesp/1`).
- Extratores de domínio: `evtea-extractor` (EVTEA → JSON conforme
  DNIT EB-101), `ler-edital`, `ler-edital-aneel` (RAP, lotes, sublotes).
- Quantificadores: `cad-quantifier`, `evtea-quantifier`.
- Leitura visual: `leitura-diagrama-engenharia` (plantas, perfis,
  seções, diagramas Tempo×Caminho).
- Validation: schema versionado por extrator; campo incerto/ausente é
  sinalizado, nunca inferido silenciosamente.

**Integrações** — lê o documento via F2; entrega JSON ao agente de F1;
aciona `aluci-guard` (F7) quando preenche norma/código citado; publica
resultado de volta em F2 como nova versão.

**Exemplo de uso**
```
Edital ANEEL (PDF + anexos) → ler-edital-aneel extrai RAP/lotes/prazos
→ campos sem match no texto ficam "a_confirmar" → JSON segue para
agente-energia (S9) via F1
```

**API/interface** — saída: JSON versionado por domínio (ex.
`params.json`, `cqp-artesp/1`). Contrato de erro: campo ilegível →
`null` + `"status": "a_confirmar"`.

**Status**: ✅ Operacional — extratores existentes e usáveis hoje.
Cobertura desigual por segmento: forte em Rodovias/OAE (S1/S2) e
Energia (S9); Portos/Aeroportos/Barragens (S6/S7/S10) ainda dependem
de extração genérica (`pdf` + `autodesk-toolkit`), sem extrator de
domínio dedicado.

---

## F5 — Notificação (email, Slack, webhook, subscriptions, templates)

**Descrição.** Informa humanos e sistemas quando algo relevante
acontece: documento aprovado, PR aberto, gate humano pendente, routine
agendado disparando.

**Componentes**
- Agendamento: `create_trigger`/`update_trigger`/`delete_trigger`/
  `fire_trigger`/`list_triggers` (cron ou one-shot); `send_later` para
  lembrete pontual na mesma sessão.
- Webhooks de PR/issue: `subscribe_pr_activity`/
  `unsubscribe_pr_activity` — eventos entregues como mensagem na sessão
  que monitora o PR (usado no fluxo de merge S6-S10 do `CLAUDE.md`).
- Templates: `morning` (briefing diário), `internal-comms` (status
  reports, updates de liderança, incident reports).
- Canais sem tool de envio direto neste ambiente: e-mail (só busca via
  `Microsoft_365`, não envio); Slack (`slack-gif-creator` gera
  conteúdo, não envia notificação).

**Integrações** — F6 é a fonte primária de eventos que podem disparar
notificação; F1 pode registrar routine de acompanhamento pós-handoff;
upload em F2 é candidato a gatilho (não implementado — depende de
webhook nativo do SharePoint, fora do MCP atual).

**Exemplo de uso**
```
subscribe_pr_activity(owner="MN1970", repo="Codex-exemplo", pullNumber=1)
→ comentários/CI chegam como evento na sessão do gate humano MN
→ unsubscribe_pr_activity após merge
```

**API/interface** — `create_trigger(name, prompt, cron_expression |
run_once_at)`; `subscribe_pr_activity(owner, repo, pullNumber)`
(idempotente, um steward por PR); `send_later(message, at |
delay_minutes)`.

**Status**: ⚡ Parcial — agendamento e webhook de PR operacionais.
Envio ativo de e-mail/Slack não disponível como tool neste ambiente —
hoje é fluxo manual. Templates existem mas não conectados a disparo
automático de canal.

---

## F6 — Trace (audit log, approval gates, workflow, versioning, history)

**Descrição.** Garante que toda decisão relevante — merge de PR,
migração aplicada, documento publicado, claim aprovado — seja
rastreável: quem, quando, com base em quê, qual gate validou.

**Componentes**
- Gate humano MN: nenhuma mudança de agente/routing/RAG vai a produção
  sem aprovação do sócio responsável (item explícito no checklist de
  deploy v4.2).
- Versionamento Git: PR + revisão formal
  (`pull_request_review_write`, `add_comment_to_pending_review`,
  `submit_pending`).
- Versioning documental: nativo do SharePoint (F2) — nova versão a
  cada upload, exclusão recuperável.
- Rollback documentado: bloco `ROLLBACK` comentado em cada migração
  crítica (`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) +
  runbook de reversão (`docs/DEPLOY-v4.2.md`, seção 6).
- Estado consolidado: checklists vivos (`- [ ]`/`- [x]`) como single
  source of truth do que foi aprovado/aplicado vs. pendente.

**Integrações** — F5 pode notificar sobre evento de F6; F7 é
pré-requisito (nenhum documento entra em fila de aprovação sem
guardrails); F2 é o repositório físico, F6 é a camada de significado
sobre esse histórico.

**Exemplo de uso**
```
PR aberto em Codex-exemplo + manta-hub → gate humano MN (approve+merge)
→ só após merge de ambos: aplicar migração Supabase → checklist
versionado marca cada etapa
```

**API/interface** — `pull_request_review_write(method="create"|
"submit_pending")`; checklist Markdown como formato padrão de estado
auditável; `BEGIN…COMMIT` + `ROLLBACK` comentado como padrão de
migração reversível.

**Status**: ✅ Operacional para fluxo Git/PR (gate humano, revisão,
rollback, checklists) — em uso ativo nesta expansão v4.2. ⚡ Parcial
para audit log transacional único: hoje o rastro está distribuído
entre Git, versioning do SharePoint e checklists Markdown, sem log
agregado central.

---

## F7 — Guardrails (validação de referências, consistência, coesão semântica)

**Descrição.** Camada de controle de qualidade que roda antes de
qualquer saída virar laudo, claim, parecer, orçamento ou documento
oficial. Três guardrails complementares.

**Componentes**
- **`aluci-guard`** (referência factual): detecta normas ABNT/leis
  fabricadas, URLs/DOIs inventados, códigos SICRO inexistentes via
  regex + lookup em registry local. Gatilho: "rodar aluci-guard",
  "auditar alucinação", "checar referências do laudo", ou
  automaticamente antes de fechar laudo/claim/parecer/orçamento.
- **`consist-guard`** (consistência interna): tags balanceadas,
  consistência numérica (quantum, subtotais, impostos), lógica/ordem
  de datas, numeração sequencial de capítulos, pendências marcadas
  ("a cargar", "a confirmar"), rastreabilidade de fontes citadas.
  Gatilho: "rodar consist-guard", "revisar consistência", ao
  fechar/enviar documento técnico.
- **`context-guardian`** (coesão semântica): preserva contexto em
  sessões longas, evita perda por compactação/truncamento/esquecimento
  de artefatos anteriores. Gatilho: "não compacte", "mantenha o
  contexto", sessões com múltiplos artefatos/versões, ou
  proativamente acima de ~10 trocas densas.

**Integrações** — F4 aciona `aluci-guard` ao preencher campo com
norma/código citado; F6 exige F7 completo antes do gate humano; F8 e
F7 rodam juntos ao fechar documento (forma + conteúdo confiável);
agentes verticais delegam validação final a F7 em vez de auto-validar.

**Exemplo de uso**
```
Laudo cita NBR 7187, SICRO 2S07 100 00, 3 URLs
→ aluci-guard confirma normas/SICRO no registry, sinaliza 1 URL
  não verificável ("a confirmar")
→ consist-guard checa subtotais, ordem de datas, numeração de capítulos
→ só após os dois PASS: documento segue para F6 (gate humano)
```

**API/interface** — cada guardrail é skill invocável por nome ou
gatilho de linguagem natural; saída padrão: achados classificados por
severidade (bloqueante/atenção/informativo), nunca "PASS/FAIL" opaco;
não sobrescrevem o documento — apontam o problema para correção.

**Status**: ✅ Operacional — as três skills existem e são ativáveis
hoje. Uso é por convenção/gatilho, não hook obrigatório de pipeline:
um agente pode, em tese, fechar documento sem acionar F7. Formalizar
F7 como hook obrigatório antes de `upload_file` de documento técnico é
melhoria pendente.

---

## F8 — Padronização (style guide, templates, nomenclatura, conventions, checkpoints)

**Descrição.** Garante que qualquer material — relatório,
apresentação, dashboard, aplicativo, documento — seja reconhecível
como Manta: identidade visual, estrutura, nomenclatura, independente
do agente/skill que o gerou.

**Componentes**
- **`padrao-manta`**: aplica logo, cores, marca d'água e
  rastreabilidade completa em apresentações, relatórios, dashboards,
  aplicativos e documentos.
- Regras obrigatórias para artefatos HTML: abas verticais em coluna à
  esquerda (nunca horizontais); indicador do objeto do artefato
  sempre visível; numeração de seções; prioridade para
  quadros/tabelas — nunca cards como formato primário.
- Nomenclatura: `03_Projetos/<Segmento>/` (projetos),
  `agente-<slug>/` (definição de agente), `MNT-<ano>-<TAG>` (tickets,
  ex. `MNT-2026-UPGRADE-AGENTS-S6S10`).
- Templates complementares: `proposta-comercial`,
  `proposta-tecnica-rod`, `docx` (memorial com capa/sumário/
  numeração), `pptx`/`SlidesGPT`, `xlsx` (planilha analítica por
  disciplina).
- Checkpoints de fechamento: F8 roda com F7 antes de publicar — forma
  (F8) + conteúdo confiável (F7) são os dois portões de saída.

**Integrações** — F3 consome o design system diretamente na
renderização; F6 usa a nomenclatura de F8 para localizar versões/
tickets; F2 organiza pastas segundo a árvore que F8 define; agentes
de F1 outsourcing a materialização visual para `padrao-manta`.

**Exemplo de uso**
```
Dashboard React pronto → padrao-manta aplica logo/paleta/marca d'água,
abas verticais, tabelas > cards, numeração, rodapé com fonte/data/
versão/ticket → nome de arquivo segue convenção
<Segmento>-<Objeto>-v<N>.html → publicação via F2, evento em F6
```

**API/interface** — skill `padrao-manta` invocada sempre que o output
for HTML/React/PPTX/DOCX/XLSX destinado à Manta ou a clientes;
convenção de nomenclatura documentada aqui e em `manta-context`; regra
de layout é obrigatória, não opcional por preferência de agente.

**Status**: ✅ Operacional — `padrao-manta` madura e de uso obrigatório
por convenção em material client-facing; templates complementares
operacionais em produção. Em aberto: não há linter automático que
rejeite artefato fora do padrão antes da publicação — cumprimento
depende do agente autor aplicar a skill corretamente.

---

## Matriz de status consolidada

| Funcional | Descrição curta | Status |
|---|---|---|
| F1 — IA | routing, model tiering, scaling, prompting | ✅ Operacional |
| F2 — SharePoint | indexação, sync, storage, permissões, versioning | ⚡ Parcial (leitura completa; escrita/pastas v4.2 pendentes) |
| F3 — Portal | interface web, SSO, RBAC | 🆕 Planejado/parcial (portais existem, RBAC central não) |
| F4 — Extração | parser PDF/DWG, OCR, NLP, validation | ✅ Operacional (cobertura desigual por segmento) |
| F5 — Notificação | email, Slack, webhook, subscriptions | ⚡ Parcial (routines/webhook de PR sim; envio ativo de e-mail/Slack não) |
| F6 — Trace | audit log, gates, workflow, versioning | ✅ Operacional (Git/PR); ⚡ parcial (audit log agregado) |
| F7 — Guardrails | aluci-guard, consist-guard, context-guardian | ✅ Operacional (uso por convenção, não hook obrigatório) |
| F8 — Padronização | style guide, templates, nomenclatura | ✅ Operacional (sem linter automático de conformidade) |

## Interdependências entre Funcionais

```
F1 (IA) ──decide agente──► F2 (SharePoint) ──doc fonte──► F4 (Extração)
   │                                                            │
   │                                                     JSON canônico
   ▼                                                            ▼
F5 (Notificação) ◄──evento── F6 (Trace) ◄──aprova/rejeita── F7 (Guardrails)
                                  ▲                               ▲
                                  │                               │
                            gate humano MN                  F8 (Padronização)
                                                          (forma do documento)
```

Um pedido entra por F1, que busca a fonte em F2 e aciona F4 para
estruturar o dado. O resultado passa por F7 (confiabilidade de
conteúdo) e F8 (forma/identidade visual) antes de seguir para F6 (gate
humano, versionamento). Eventos de F6 podem disparar F5. Nenhum
Funcional opera isolado — pular F7 antes de publicar é desvio de
processo.

## Histórico de versões

- **v1.0.0** (2026-07-31) — primeira versão formal do Eixo F
  (Funcionais), documentando F1-F8 com descrição, componentes,
  integrações, exemplo de uso, API/interface e status de implementação
  para cada um. Complementa o `CLAUDE.md` v4.2 (Eixos 1-3) e o
  `ARQUITETURA-AGENTES-IA.md` v2.0.0 (5 camadas C0-C5), sem alterá-los.

---

_Documento vivo. Alterações via pull request neste repositório,
aprovação MN (gate humano — ver F6), e propagação para SharePoint como
nova versão, seguindo o processo de `docs/DEPLOY-v4.2.md`._
