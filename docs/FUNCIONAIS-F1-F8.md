# FUNCIONAIS-F1-F8.md

**Sistema Manta Maestro — Eixo F (Funcionais transversais)**

- **Versão**: 1.0.0
- **Data**: 2026-07-31
- **Autor**: Manta Associados
- **Relacionado a**: `CLAUDE.md` v4.2 (registro mestre, Eixos 1-3),
  `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` v2.0.0
- **Status geral**: documento de arquitetura — parte operacional, parte
  planejada (ver coluna "Status" em cada seção)

---

## Sumário

- [0. Visão geral do Eixo F](#0-visão-geral-do-eixo-f)
- [F1 — IA (routing, tiering, scaling, prompting)](#f1--ia-routing-model-tiering-scaling-prompting)
- [F2 — SharePoint (indexação, sync, storage, permissões)](#f2--sharepoint-indexação-sync-storage-por-agente-permissões-versioning)
- [F3 — Portal (interface web, SSO, RBAC)](#f3--portal-interface-web-sso-autenticação-rbac)
- [F4 — Extração (parser PDF/DWG, OCR, NLP)](#f4--extração-parser-pdfdwg-ocr-nlp-entity-extraction-validation)
- [F5 — Notificação (email, Slack, webhook)](#f5--notificação-email-slack-webhook-subscriptions-templates)
- [F6 — Trace (audit log, gates, versioning)](#f6--trace-audit-log-approval-gates-workflow-versioning-history)
- [F7 — Guardrails (aluci-guard, consist-guard, context-guardian)](#f7--guardrails-aluci-guard-consist-guard-context-guardian)
- [F8 — Padronização (style guide, templates, nomenclatura)](#f8--padronização-style-guide-templates-nomenclatura-conventions-checkpoints)
- [Matriz de status consolidada](#matriz-de-status-consolidada)
- [Interdependências entre Funcionais](#interdependências-entre-funcionais)
- [Histórico de versões](#histórico-de-versões)

---

## 0. Visão geral do Eixo F

O `CLAUDE.md` mestre descreve o sistema Manta Maestro em **3 eixos**:
horizontais (agentes transversais), verticais (segmentos S1-S10) e
ciclo de vida (8 fases). Esses três eixos respondem **quem** atua e
**sobre o quê**.

O **Eixo F (Funcionais)** é ortogonal aos três — descreve **como** o
sistema funciona por baixo de qualquer agente ou segmento. Um agente
vertical (ex.: `agente-saneamento`) e um agente horizontal (ex.:
`manta-05 orcamento`) consomem os mesmos 8 Funcionais: ambos são
roteados por F1, ambos leem/escrevem em F2, ambos podem ser acessados
via F3, ambos extraem dados de PDF/DWG via F4, ambos notificam via F5,
ambos deixam rastro em F6, ambos são auditados por F7 antes de virar
entregável, e ambos seguem o style guide de F8.

```
                    Eixo 1 (Horizontais)  ×  Eixo 2 (Verticais)  ×  Eixo 3 (Fases)
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────────────┐
        │                    EIXO F — FUNCIONAIS                    │
        │  F1 IA │ F2 SharePoint │ F3 Portal │ F4 Extração │        │
        │  F5 Notificação │ F6 Trace │ F7 Guardrails │ F8 Padrão    │
        └───────────────────────────────────────────────────────────┘
```

Cada Funcional abaixo segue o mesmo template: **descrição**,
**componentes**, **integrações**, **exemplo de uso**, **API/interface**
e **status de implementação**.

---

## F1 — IA (routing, model tiering, scaling, prompting)

### Descrição

F1 é o motor de decisão do Maestro (Manta 00): recebe a consulta bruta
do usuário, classifica-a segundo o intake padrão (Q1 segmento, Q2 fase
de ciclo de vida, Q3 objetivo, Q4 formato de dados), escolhe o(s)
agente(s) de destino e o tier de modelo, e mantém esse roteamento
estável durante a sessão — inclusive fazendo handoffs declarativos
entre agentes quando o escopo muda no meio da conversa.

### Componentes

- **Router (Manta 00)** — regex/keyword matching sobre Q1 (ver bloco
  de routing no `CLAUDE.md`), com fallback para classificação
  semântica quando nenhuma keyword bate.
- **Model tiering** — 3 níveis:

| Tier | Modelo | Uso típico | % de chamadas |
|---|---|---|---|
| Triagem | Haiku | routing, intake, extração de metadados | ~20% |
| Execução | Sonnet | análise técnica, redação, orçamento, cronograma | ~70% |
| Complexo | Opus | claims complexos, arquitetura, second opinion crítico | ~10% |

- **Scaling dinâmico** — sessão começa em Haiku (triagem), escala para
  Sonnet ao entrar no agente vertical/horizontal, escala novamente
  para Opus se detectar complexidade composta (ex.: claim + jurídico +
  técnico + financeiro no mesmo pleito).
- **Biblioteca de prompts** — prompts canônicos por agente (Q1-Q4 do
  intake), casos ambíguos documentados em `tests/routing/prompts.md`.

### Integrações

- Lê o mapa de agentes e regras de routing do `CLAUDE.md` mestre
  (seção "MAPA COMPLETO DE AGENTES" e "ROUTING — Maestro").
- Consulta as coleções RAG (F2/Supabase) por prefixo de storage
  (`san:`, `ene:`, `por:`, `aer:`, `bar:`, etc.) depois de decidir o
  agente vertical.
- Invoca skills de F7 (guardrails) antes de fechar qualquer output
  técnico.
- Dispara handoffs para outros agentes (F1 → F1) sem retornar ao
  cliente — ex.: `agente-saneamento` → `manta-05` para orçamento.

### Exemplo de uso

```
Usuário: "preciso analisar o ETE do sistema Riachuelo, tem problema
          de subestação de energia também"

F1 (Haiku, triagem):
  Q1 = saneamento (menção "ETE") + energia (menção "subestação")
  Q2 = operação & manutenção (contexto: "problema")
  → dispatch primário: agente-saneamento (S8)
  → handoff declarado: agente-energia (S9)

F1 (Sonnet, execução):
  agente-saneamento assume, consulta RAG "san:ar:*" (AySA/Argentina),
  detecta necessidade de handoff real → aciona agente-energia
```

### API/interface

- **Entrada**: string livre do usuário + contexto de sessão (histórico,
  artefatos abertos).
- **Saída**: `{ agente_primario, agentes_handoff[], tier, fase_ciclo_vida, confidence }`.
- **Regras de routing**: bloco `IF menção a ... → agente-X` documentado
  em `CLAUDE.md`, testável via `tests/routing/prompts.md`.
- **Critério de aprovação de routing**: ≥ 90% dos prompts do arquivo de
  teste caindo no agente esperado (ver `docs/DEPLOY-v4.2.md`, seção 5).

### Status de implementação

✅ **Operacional** — routing keyword-based ativo para os 20 agentes
(11 horizontais + 9 verticais completos + 1 parcial). Model tiering
documentado e aplicado por convenção nos agentes `.md`
(`model: sonnet` no frontmatter). Scaling dinâmico dentro de uma
mesma sessão depende do orquestrador de runtime do Maestro (fora
deste repositório, que é somente o registro versionado).

---

## F2 — SharePoint (indexação, sync, storage por agente, permissões, versioning)

### Descrição

F2 é a camada de armazenamento documental do ecossistema — cada agente
vertical possui uma pasta canônica de projetos e uma pasta de
definição (`SKILL.md`, `README.md`, `refs/`, `prompts/`), ambas em
SharePoint Online, com sincronização assistida por agente via MCP.

### Componentes

- **`sp_agent_routing`** (tabela) — mapeia `agent_slug → sp_folder →
  file_patterns[] → priority`. Ver `CLAUDE.md`, seção "SHAREPOINT —
  Routing rules".
- **Árvore canônica**:
  - `03_Projetos/<Segmento>/*` — arquivos de projeto (`*.pdf`, `*.dwg`,
    `*.xlsx`).
  - `04_IA/Manta-Maestro/01-agentes-fundamentais/agente-<slug>/` —
    `SKILL.md`, `README.md`, `refs/`, `prompts/`.
- **MCP SharePoint (`mcp__SharePoint_Manta__*`)** — camada de acesso
  usada pelos agentes em runtime: `list_libraries`, `list_folders`,
  `list_files`, `search_files`, `find_item`, `get_folder_tree`,
  `read_document`, `download_file`, `upload_file`, `create_folder`,
  `move_item`, `copy_item`, `rename_item`, `delete_item`,
  `update_metadata`, `get_file_metadata`, `get_library_columns`,
  `get_site_info`.
- **Versioning nativo do SharePoint** — cada upload gera nova versão;
  exclusões vão para lixeira (recuperáveis), nunca hard-delete direto.
- **Permissões** — modo delegado: escritas ocorrem como o usuário
  autenticado, respeitando os grupos/ACLs já configurados no site
  (`sites/Engenharia`).

### Integrações

- F1 decide o agente → F1 consulta `sp_agent_routing` (F2) para saber
  onde ler/escrever.
- F4 (Extração) lê documentos via `read_document`/`download_file` e
  devolve dados estruturados.
- F6 (Trace) registra cada `upload_file`/`update_metadata` como evento
  de auditoria (quem, quando, versão anterior).
- F8 (Padronização) define convenção de nomenclatura de arquivo antes
  do `upload_file`.

### Exemplo de uso

```
Agente: agente-portos precisa consultar o edital ANTAQ do Porto de
Suape antes de responder.

1. find_item(query="edital Suape ANTAQ")
2. read_document(item_id=...)          # extrai texto/tabelas
3. get_file_metadata(item_id=...)      # confirma versão vigente
4. (se produzir memorial novo) upload_file(folder="03_Projetos/Portos/Suape/",
   name="Memorial-Suape-v2.docx")      # gera nova versão, mantém histórico
```

### API/interface

- Site canônico: `https://mnassociados.sharepoint.com/sites/Engenharia`.
- Library: `Documentos Compartilhados`.
- Todas as chamadas passam pelo servidor MCP `SharePoint_Manta`
  (leitura e escrita); não há acesso direto a Graph API pelos agentes.
- Colunas de metadata customizadas consultáveis via
  `get_library_columns` antes de `update_metadata` (evita erro de
  schema).

### Status de implementação

⚡ **Parcial** — leitura/busca (`list_*`, `search_files`,
`read_document`, `get_*`) operacional em produção. Escrita
(`upload_file`, `create_folder`, `move_item` etc.) disponível via MCP,
mas as 10 pastas da expansão v4.2 (5 de agente + 5 de projeto) ainda
**não foram criadas** — item em aberto no `docs/DEPLOY-v4.2.md`,
seção 3. `sp_agent_routing` aguarda insert das 5 linhas novas
(seção 2 do mesmo runbook).

---

## F3 — Portal (interface web, SSO, autenticação, RBAC, permissões granulares)

### Descrição

F3 é a camada de apresentação web do ecossistema Manta — portais de
gestão de projeto/contrato que consomem os agentes (F1) e os dados
(F2/F4) por trás de autenticação corporativa, com controle de acesso
por papel e por objeto (projeto, contrato, cliente).

### Componentes

- **Portais de referência** (skills do catálogo que materializam F3):
  `portal-gestao-manta`, `portal-megaprojeto-builder`,
  `portal-metro-l4` — cada um cobre um recorte (gestão geral,
  megaprojetos FIDIC multi-módulo, portal específico de cliente/linha).
- **SSO** — autenticação corporativa via identidade Microsoft 365 /
  Entra ID, a mesma usada pelo MCP `Microsoft_365` (`get_me` resolve
  identidade do usuário autenticado; mesmo diretório usado por
  SharePoint em F2).
- **RBAC** — papéis mínimos previstos: `viewer` (leitura de
  dashboards), `analista` (edição de projeto, sem publicar), `gestor`
  (aprova gates de F6), `admin` (gerencia usuários e permissões
  granulares por projeto/cliente).
- **Permissões granulares** — por projeto (ex.: só quem está alocado
  no contrato CT5500097701 vê os GRs daquele contrato), por segmento
  (ex.: acesso a S8-Saneamento não implica acesso a S10-Barragens) e
  por fase de ciclo de vida (ex.: claims/due diligence com visibilidade
  restrita a sócios).

### Integrações

- F1 — o portal é um front-end alternativo ao chat: a mesma
  requisição do usuário no portal aciona o mesmo router de F1.
- F2 — dashboards do portal leem e gravam nos mesmos repositórios
  SharePoint via F2, nunca em storage paralelo.
- F6 — toda ação do portal que altera estado de um documento (aprovar,
  publicar, arquivar) gera evento de trace.
- F8 — o portal aplica o padrão visual Manta (abas verticais à
  esquerda, tabelas priorizadas sobre cards, logo/marca d'água) via o
  design system descrito em F8.

### Exemplo de uso

```
Usuário (papel: gestor) acessa hub.mantaassociados.com/askcad
  → SSO valida identidade corporativa (Entra ID)
  → RBAC resolve: gestor tem acesso ao contrato "Nova Ponte Tocantins"
  → Portal renderiza dashboard do GR-04 (Infraestrutura das Pontes)
  → Usuário aprova o relatório → F6 registra aprovação com timestamp
    e identidade do aprovador
```

### API/interface

- Entry point de referência citado no runbook operacional:
  `https://hub.mantaassociados.com/askcad` (ambiente do Maestro).
- Autenticação: token OIDC/SAML da conta corporativa Manta, mesma
  origem usada pelo `Microsoft_365` MCP.
- Autorização: matriz `{papel} × {projeto/cliente} × {segmento} × {fase}`
  resolvida antes de renderizar qualquer módulo do portal.

### Status de implementação

🆕 **Planejado / parcial** — skills de portal (`portal-gestao-manta`,
`portal-megaprojeto-builder`, `portal-metro-l4`) existem no catálogo
como geradores de artefato/dashboard, mas o **portal único com SSO e
RBAC centralizados** ainda não está consolidado neste repositório;
cada portal hoje é um artefato/app independente por projeto. Formalizar
RBAC granular multi-projeto é item de arquitetura em aberto (ver
`manta-arquiteto-ia` para decisões de plataforma).

---

## F4 — Extração (parser PDF/DWG, OCR, NLP, entity extraction, validation)

### Descrição

F4 transforma documento não estruturado (PDF de edital, DWG de
projeto, planilha) em dado estruturado (JSON canônico) que os agentes
verticais conseguem processar — quantitativos, entidades técnicas
(normas, códigos SICRO, parâmetros de engenharia), texto pesquisável.

### Componentes

- **Parsers de documento**: skill `pdf` (extração de texto/tabelas,
  OCR de PDF escaneado, merge/split, formulários).
- **Parsers CAD/BIM**: skill `autodesk-toolkit` (DXF, DWG, IFC, RVT
  sem precisar de AutoCAD/Civil 3D/Revit instalado) e
  `cqp-cad-bridge` (extração de disciplinas, layers e quantitativos
  de DWG/DXF/PDF para o schema `cqp-artesp/1`).
- **Extratores de domínio**: `evtea-extractor` (EVTEA rodoviário →
  JSON canônico conforme DNIT EB-101), `ler-edital` (editais de
  licitação → dados administrativos + técnicos), `ler-edital-aneel`
  (editais ANEEL de transmissão → JSON com RAP, lotes, sublotes).
- **Quantificadores** (NLP + heurística de domínio sobre o JSON já
  extraído): `cad-quantifier`, `evtea-quantifier`.
- **Leitura visual de diagrama de engenharia**:
  `leitura-diagrama-engenharia` (interpreta plantas de situação,
  perfis longitudinais, seções transversais, diagramas Tempo×Caminho).
- **Validation** — cada extrator produz um schema JSON versionado
  (ex.: `cqp-artesp/1`) e sinaliza campos incertos/ausentes em vez de
  inferir silenciosamente.

### Integrações

- Lê o documento fonte via F2 (`read_document`/`download_file`).
- Entrega JSON canônico para os agentes verticais de F1 (ex.:
  `evtea-extractor` → `agente-infraestrutura S1`).
- Aciona F7 (`aluci-guard`) quando o extrator preenche campos com
  normas/códigos citados no documento fonte, para validar que a
  referência realmente existe no texto.
- Alimenta F2 de volta quando o resultado (planilha, memória de
  cálculo) é publicado como novo artefato/versão.

### Exemplo de uso

```
Usuário envia edital ANEEL (PDF, 340 páginas) + 4 anexos técnicos

1. ler-edital-aneel: parse do PDF principal + anexos + minuta de
   contrato → JSON com RAP teto, lotes, sublotes, prazos
2. cad-quantifier (se houver DWG anexo): quantitativos de LT/SE
3. Validation: campos sem match no texto fonte ficam marcados
   "a confirmar" em vez de inferidos
4. JSON canônico segue para agente-energia (S9) via F1
```

### API/interface

- Schema de saída típico: JSON versionado por domínio (ex.:
  `params.json` do EVTEA, `cqp-artesp/1` do CQP-bridge).
- Entrada: arquivo binário (PDF/DWG/DXF/XLSX) localizado via F2 ou
  anexado diretamente na conversa.
- Contrato de erro: campo ausente/ilegível → `null` + flag
  `"status": "a_confirmar"`, nunca valor inventado.

### Status de implementação

✅ **Operacional** — todos os extratores citados são skills existentes
e utilizáveis hoje (`pdf`, `autodesk-toolkit`, `cqp-cad-bridge`,
`evtea-extractor`, `evtea-quantifier`, `ler-edital`,
`ler-edital-aneel`, `cad-quantifier`, `leitura-diagrama-engenharia`).
Cobertura por segmento ainda é desigual: forte em Rodovias/OAE
(S1/S2) e Energia (S9); Portos/Aeroportos/Barragens (S6/S7/S10) ainda
dependem de extração genérica (`pdf` + `autodesk-toolkit`) sem
extrator de domínio dedicado.

---

## F5 — Notificação (email, Slack, webhook, subscriptions, templates)

### Descrição

F5 informa humanos e outros sistemas quando algo relevante acontece no
ecossistema: um documento foi aprovado, um PR de agente foi aberto,
uma migração precisa de gate humano, um routine agendado disparou.

### Componentes

- **Agendamento/routines** — `create_trigger` / `update_trigger` /
  `delete_trigger` / `fire_trigger` / `list_triggers`: mensagens
  recorrentes (cron) ou one-shot (`send_later`) entregues de volta a
  uma sessão — base de qualquer notificação programada (ex.: lembrete
  de gate humano pendente).
- **Webhooks de PR/issue** — `subscribe_pr_activity` /
  `unsubscribe_pr_activity`: eventos de comentário e falha de CI em
  pull requests entregues como mensagem `<github-webhook-activity>`
  na sessão que monitora o PR (usado no fluxo de deploy do `CLAUDE.md`
  — merges dos PRs de expansão S6-S10).
- **Templates de mensagem** — briefing diário (`morning` skill),
  comunicação interna estruturada (`internal-comms` skill: status
  reports, updates de liderança, incident reports).
- **Canais previstos, ainda sem tool de envio direto neste
  repositório**: e-mail (busca via `Microsoft_365` MCP existe;
  *envio* não); Slack (`slack-gif-creator` cobre geração de conteúdo,
  não envio de notificação).

### Integrações

- F6 (Trace) é a fonte primária de eventos: toda aprovação/rejeição de
  gate gera um evento que **pode** disparar uma notificação via F5.
- F1 pode registrar um routine de acompanhamento após um handoff
  crítico (ex.: "avisar se claim não avançar em 48h").
- F2 — upload de novo documento em pasta monitorada é candidato a
  gatilho de notificação (não implementado neste repo; depende de
  webhook nativo do SharePoint, fora do escopo do MCP atual).

### Exemplo de uso

```
Ticket MNT-2026-UPGRADE-AGENTS-S6S10 aberto como PR:

1. subscribe_pr_activity(owner="MN1970", repo="Codex-exemplo", pullNumber=1)
2. Comentários e falhas de CI chegam como eventos na sessão que
   acompanha o merge (gate humano MN)
3. Após merge: unsubscribe_pr_activity (fim do monitoramento)
```

### API/interface

- `create_trigger(name, prompt, cron_expression | run_once_at, ...)` —
  cron mínimo de 1h; `run_once_at` para disparo único.
- `subscribe_pr_activity(owner, repo, pullNumber)` /
  `unsubscribe_pr_activity(...)` — idempotente, um "steward" por PR.
- `send_later(message, at | delay_minutes)` — lembrete pontual na
  mesma sessão.

### Status de implementação

⚡ **Parcial** — agendamento (routines) e webhook de PR/issue são
capacidades reais e utilizáveis hoje. Envio ativo de e-mail e
mensagens Slack **não** está disponível como tool neste ambiente —
hoje é fluxo manual (humano lê o output do agente e replica no canal
apropriado). Templates de comunicação existem (`internal-comms`,
`morning`) mas não estão conectados a um disparo automático de canal.

---

## F6 — Trace (audit log, approval gates, workflow, versioning, history)

### Descrição

F6 garante que toda decisão relevante do ecossistema — merge de PR,
aplicação de migração, publicação de documento técnico, aprovação de
claim — seja rastreável: quem, quando, com base em quê, e qual gate
humano validou.

### Componentes

- **Gate humano MN** — padrão explícito no `CLAUDE.md`: nenhuma
  mudança de agente/routing/RAG vai para produção sem aprovação do
  sócio responsável (linha "Gate humano: aprovação MN antes de merge"
  no checklist de deploy v4.2).
- **Versionamento Git** — todo artefato canônico (`CLAUDE.md`, agentes
  `.md`, migrações `.sql`) versionado via PR, com histórico completo
  de commits e revisão (`pull_request_review_write`,
  `add_comment_to_pending_review`, `submit_pending`).
- **Versioning documental** — versionamento nativo do SharePoint (F2):
  cada `upload_file` gera nova versão, nada é sobrescrito
  silenciosamente; exclusões vão para lixeira recuperável.
- **Rollback documentado** — cada migração crítica inclui bloco de
  `ROLLBACK` comentado (ver
  `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) e runbook
  de reversão (`docs/DEPLOY-v4.2.md`, seção 6: revert de merge, rollback
  SQL, rename de pastas SP para `*_DEPRECATED`).
- **Estado consolidado** — checklists vivos (`docs/DEPLOY-v4.2.md`,
  seção "Estado atual") como single source of truth de o que já foi
  aprovado/aplicado vs. o que ainda está pendente.

### Integrações

- F5 pode notificar quando um evento de F6 ocorre (merge, aprovação,
  rollback).
- F7 é pré-requisito de F6: nenhum documento entra em fila de
  aprovação sem antes passar por guardrails.
- F2 é o repositório físico de versões; F6 é a camada de significado
  sobre esse histórico (quem aprovou, por quê, com que gate).

### Exemplo de uso

```
Fluxo de aprovação da expansão v4.2 (Portos/Aeroportos/Saneamento/
Energia/Barragens):

1. PR aberto em MN1970/Codex-exemplo (registro mestre) e em
   viniciusmagnos/manta-hub (mirror dos agentes)
2. Gate humano MN: revisão + approve + merge (draft → ready → merged)
3. Só após merge de AMBOS os PRs: aplicar migração Supabase
4. Cada etapa registrada em checklist versionado
   (docs/DEPLOY-v4.2.md) — nenhuma etapa é considerada concluída sem
   marcação explícita [x]
```

### API/interface

- `pull_request_review_write(method="create"|"submit_pending")` +
  `add_comment_to_pending_review` — fluxo de revisão formal de PR.
- Checklist Markdown (`- [ ]` / `- [x]`) como formato padrão de estado
  auditável em runbooks (`docs/DEPLOY-v4.2.md`).
- Bloco `BEGIN…COMMIT` + `ROLLBACK` comentado como padrão de migração
  reversível em `supabase/migrations/*.sql`.

### Status de implementação

✅ **Operacional** para o fluxo de Git/PR (gate humano, revisão,
rollback documentado, checklists versionados) — em uso ativo na
expansão v4.2 deste próprio repositório. ⚡ **Parcial** para audit log
transacional centralizado (quem aprovou o quê, com timestamp, em uma
única tabela consultável) — hoje o rastro está distribuído entre Git,
SharePoint (versioning nativo) e checklists Markdown, sem um log
único agregado.

---

## F7 — Guardrails (validação de referências, consistência, coesão semântica)

### Descrição

F7 é a camada de controle de qualidade que roda **antes** de qualquer
saída virar laudo, claim, parecer, orçamento ou documento técnico
oficial da Manta. Três guardrails complementares, cada um com um
recorte de risco distinto.

### Componentes

**7.1 `aluci-guard` — validação de referências factuais**
- Detecta normas ABNT/leis fabricadas, URLs e DOIs inventados, códigos
  SICRO inexistentes.
- Método: regex + lookup em registry local (não depende de busca web
  para cada citação).
- Gatilho: "rodar aluci-guard", "auditar alucinação", "checar
  referências do laudo", "validar este texto", ou automaticamente
  antes de fechar laudo/claim/parecer/orçamento.

**7.2 `consist-guard` — consistência interna do documento**
- Verifica: integridade estrutural (tags balanceadas, fecho correto de
  HTML), consistência numérica (quantum, subtotais, IGV/impostos),
  lógica e ordem de datas, numeração sequencial de capítulos,
  pendências marcadas ("a cargar", "a confirmar", número em branco),
  rastreabilidade (fontes citadas: Dictamen, CGC, AACE, SharePoint).
- Gatilho: "rodar consist-guard", "revisar consistência", "validar a
  tese", "checar o documento", ou ao fechar/enviar qualquer documento
  técnico Manta.

**7.3 `context-guardian` — coesão semântica em sessões longas**
- Preserva contexto completo em sessões longas de trabalho técnico,
  evitando perda de informação por compactação automática de
  histórico, truncamento de output, esquecimento de artefatos/decisões
  anteriores.
- Gatilho: "não compacte", "mantenha o contexto", "continue de onde
  paramos", sessões com múltiplos artefatos/versões em evolução
  (GRs, reequilíbrios, cronogramas, laudos), ou proativamente acima de
  ~10 trocas densas envolvendo artefatos/arquivos técnicos.

### Integrações

- F4 (Extração) aciona `aluci-guard` quando um extrator preenche campo
  com norma/código citado no documento fonte.
- F6 (Trace) exige F7 completo antes de qualquer documento entrar na
  fila de aprovação/gate humano.
- F8 (Padronização) e F7 rodam em conjunto ao fechar um documento:
  F8 garante forma, F7 garante conteúdo confiável e consistente.
- Agentes verticais de F1 (ex. `agente-saneamento`, seção "O que este
  agente NÃO faz") delegam a validação final a F7 em vez de tentar
  auto-validar.

### Exemplo de uso

```
Fechamento de laudo técnico (ex.: GR-04 do contrato Nova Ponte
Tocantins):

1. Documento redigido cita NBR 7187, NBR 6118, código SICRO
   2S07 100 00, e 3 URLs de referência
2. aluci-guard: confirma normas/SICRO existentes no registry;
   sinaliza 1 URL não verificável → marcar "a confirmar"
3. consist-guard: checa que os subtotais de quantum batem com o
   somatório das tabelas, datas em ordem cronológica, capítulos
   numerados sequencialmente sem lacuna
4. Só após os dois PASS: documento segue para F6 (gate humano MN)
```

### API/interface

- Cada guardrail é uma skill invocável por nome ou por gatilho de
  linguagem natural (ver descrições acima).
- Saída padrão: lista de achados classificados por severidade
  (bloqueante / atenção / informativo), nunca um "PASS/FAIL" opaco sem
  detalhe.
- Não sobrescrevem o documento automaticamente — apontam o problema
  para correção humana ou do próprio agente autor.

### Status de implementação

✅ **Operacional** — as três skills existem no catálogo e são
ativáveis hoje (`aluci-guard`, `consist-guard`, `context-guardian`).
Uso é **por convenção/gatilho de linguagem**, não é um hook obrigatório
de pipeline: um agente pode, em tese, fechar um documento sem acionar
F7. Formalizar F7 como *hook obrigatório* antes de qualquer
`upload_file` de documento técnico é melhoria pendente de arquitetura.

---

## F8 — Padronização (style guide, templates, nomenclatura, conventions, checkpoints)

### Descrição

F8 garante que qualquer material produzido pelo ecossistema — relatório,
apresentação, dashboard, aplicativo, documento — seja reconhecível como
Manta: mesma identidade visual, mesma estrutura, mesma nomenclatura de
arquivo e pasta, independente de qual agente ou skill o gerou.

### Componentes

- **`padrao-manta`** (skill central de F8) — aplica logo, cores, marca
  d'água e rastreabilidade completa em apresentações, relatórios,
  dashboards, aplicativos e documentos.
- **Regras de layout obrigatórias para artefatos HTML**:
  - abas verticais em coluna à esquerda (nunca abas horizontais);
  - indicador do objeto do artefato sempre visível;
  - numeração de seções;
  - prioridade para quadros/tabelas — **nunca cards** como formato
    primário de exibição de dados estruturados.
- **Nomenclatura de arquivo/pasta** — convenção `03_Projetos/<Segmento>/`
  para projetos, `agente-<slug>/` para definição de agente,
  `MNT-<ano>-<TAG>` para tickets (ex.: `MNT-2026-UPGRADE-AGENTS-S6S10`).
- **Templates complementares por tipo de entregável**:
  `proposta-comercial`, `proposta-tecnica-rod`, `docx` (memoriais Word
  com padrão de capa/sumário/numeração), `pptx`/`SlidesGPT`
  (apresentações), `xlsx` (planilhas analíticas por disciplina).
- **Checkpoints de fechamento** — F8 roda em conjunto com F7 antes de
  publicar: forma (F8) + conteúdo confiável (F7) são os dois portões
  de saída de qualquer documento oficial.

### Integrações

- F3 (Portal) consome o design system de F8 diretamente na renderização
  de dashboards.
- F6 (Trace) usa a convenção de nomenclatura de F8 para localizar
  versões e tickets no histórico.
- F2 (SharePoint) organiza pastas segundo a árvore canônica que F8
  define (`03_Projetos/*`, `01-agentes-fundamentais/agente-*`).
- Todo agente vertical (F1) que produz artefato outsourcing a
  materialização visual para `padrao-manta` em vez de estilizar
  livremente.

### Exemplo de uso

```
Agente conclui análise e precisa entregar um dashboard React:

1. Conteúdo pronto (dados, tabelas, quantitativos)
2. padrao-manta aplicado: logo Manta, paleta oficial, marca d'água,
   abas verticais à esquerda, tabelas priorizadas sobre cards,
   numeração de seções, rodapé com rastreabilidade
   (fonte, data, versão, ticket)
3. Nome de arquivo segue convenção: <Segmento>-<Objeto>-v<N>.html
4. Publicação via F2, evento registrado em F6
```

### API/interface

- Skill `padrao-manta` invocada sempre que o output for HTML/React/PPTX
  /DOCX/XLSX destinado à Manta ou a clientes.
- Convenção de nomenclatura documentada neste arquivo e em
  `manta-context` (skill de contexto institucional).
- Regra de layout (abas verticais, tabelas > cards, numeração) é
  **obrigatória** para artefatos Manta — não opcional por preferência
  de agente.

### Status de implementação

✅ **Operacional** — `padrao-manta` é skill madura e de uso obrigatório
por convenção em todo material client-facing. Templates
complementares (`docx`, `pptx`, `xlsx`, `proposta-comercial`,
`proposta-tecnica-rod`) operacionais e usados em produção. Ponto em
aberto: não há *linter automático* que rejeite um artefato fora do
padrão antes da publicação — o cumprimento depende do agente autor
aplicar a skill corretamente.

---

## Matriz de status consolidada

| Funcional | Descrição curta | Status |
|---|---|---|
| F1 — IA | routing, model tiering, scaling, prompting | ✅ Operacional |
| F2 — SharePoint | indexação, sync, storage, permissões, versioning | ⚡ Parcial (leitura completa; escrita/pastas v4.2 pendentes) |
| F3 — Portal | interface web, SSO, RBAC | 🆕 Planejado / parcial (portais existem, RBAC central não) |
| F4 — Extração | parser PDF/DWG, OCR, NLP, validation | ✅ Operacional (cobertura desigual por segmento) |
| F5 — Notificação | email, Slack, webhook, subscriptions | ⚡ Parcial (routines e webhook de PR sim; envio ativo de e-mail/Slack não) |
| F6 — Trace | audit log, gates, workflow, versioning | ✅ Operacional para Git/PR; ⚡ parcial para audit log agregado |
| F7 — Guardrails | aluci-guard, consist-guard, context-guardian | ✅ Operacional (uso por convenção, não hook obrigatório) |
| F8 — Padronização | style guide, templates, nomenclatura | ✅ Operacional (sem linter automático de conformidade) |

## Interdependências entre Funcionais

```
F1 (IA) ──decide agente──► F2 (SharePoint) ──fornece doc fonte──► F4 (Extração)
   │                                                                   │
   │                                                          JSON canônico
   ▼                                                                   ▼
F5 (Notificação) ◄──evento──── F6 (Trace) ◄──aprova/rejeita──── F7 (Guardrails)
                                    ▲                                  ▲
                                    │                                  │
                              gate humano MN                    F8 (Padronização)
                                                            (forma do documento)
```

Leitura do diagrama: um pedido entra por F1, que busca a fonte em F2 e
aciona F4 para estruturar o dado. O resultado passa por F7
(confiabilidade de conteúdo) e F8 (forma/identidade visual) antes de
seguir para F6 (gate humano, versionamento). Eventos de F6 podem
disparar F5. Nenhum Funcional opera isolado — a falha de qualquer um
(ex.: pular F7 antes de publicar) é considerada desvio de processo.

## Histórico de versões

- **v1.0.0** (2026-07-31) — primeira versão formal do Eixo F
  (Funcionais), documentando F1-F8 com descrição, componentes,
  integrações, exemplo de uso, API/interface e status de implementação
  para cada um. Complementa o `CLAUDE.md` v4.2 (Eixos 1-3) e o
  `ARQUITETURA-AGENTES-IA.md` v2.0.0 (5 camadas C0-C5), sem alterá-los.

---

_Documento vivo. Alterações via pull request neste repositório,
aprovação MN (gate humano — ver F6), e propagação para SharePoint como
nova versão, seguindo o mesmo processo descrito em
`docs/DEPLOY-v4.2.md`._
