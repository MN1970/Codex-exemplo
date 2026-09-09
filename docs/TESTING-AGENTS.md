# Testando agentes — guia de referência

Este documento explica a suíte de testes de agentes deste repositório
(`tests/`) e o workflow `.github/workflows/agent-test.yml` que a
executa em CI. Leia isto antes de adicionar um novo agente vertical ou
de alterar um existente.

## Visão geral do pipeline

| Job     | O que valida                                              | Precisa de secret?              | Velocidade |
|---------|------------------------------------------------------------|----------------------------------|------------|
| `lint`  | Markdown, YAML, schema do frontmatter dos agentes           | Não                               | segundos   |
| `unit`  | Schema completo + consistência `CLAUDE.md` ↔ `.claude/agents/` | Não                          | segundos   |
| `rag`   | Consistência das coleções RAG (registro/CLAUDE.md/migrações) + verificação live opcional | Não (live é opcional) | segundos–1min |
| `smoke` | 5 perguntas reais por agente → resposta da API Anthropic em <30s | `ANTHROPIC_API_KEY`         | ~1–2 min/agente |

Todos os jobs rodam em paralelo. Um job final, `all-checks`, agrega o
resultado dos 4 — **é esse o check a marcar como obrigatório** em
`Settings → Branches → Branch protection rules → Require status
checks to pass` no GitHub, para efetivamente bloquear merge quando
qualquer teste falhar (workflows não configuram branch protection
sozinhos).

Trigger: `pull_request` para `main` (quando o PR toca em
`.claude/agents/**`, `CLAUDE.md`, `supabase/migrations/**` ou
`tests/**`) e `push` para `main` e para branches `agent/**` /
`agents/**`.

## Secrets necessários (Settings → Secrets and variables → Actions)

| Secret                       | Usado por | Obrigatório em |
|-------------------------------|-----------|-----------------|
| `ANTHROPIC_API_KEY`            | job `smoke` | `main` (via `REQUIRE_SMOKE_TESTS`); opcional em PRs de fork |
| `SUPABASE_URL`                 | job `rag`   | opcional — sem ele, só a consistência estática roda |
| `SUPABASE_SERVICE_ROLE_KEY`    | job `rag`   | opcional — idem |

**Importante sobre PRs de fork:** GitHub não expõe secrets de
repositório para workflows disparados por PRs de forks externos. Por
isso os testes `smoke` e a verificação live de `rag` são projetados
para **pular (skip)**, não falhar, quando o secret correspondente está
ausente — o merge continua bloqueado pelos jobs `lint`/`unit`/pelas
checagens estáticas de `rag`, que nunca precisam de secret. Em `main`
(push direto, sempre com acesso a secrets), as variáveis de ambiente
`REQUIRE_SMOKE_TESTS` / `REQUIRE_RAG_LIVE_TESTS` forçam falha em vez de
skip caso o secret tenha sido removido por engano.

## Rodando localmente

```bash
pip install -r tests/requirements.txt

# lint (schema do frontmatter, parte rápida)
python -m pytest tests/unit/test_agent_schema.py -v

# unit completo (schema + consistência com CLAUDE.md)
python -m pytest -m unit -v

# RAG — só a parte estática (sem secrets)
python -m pytest -m rag -v

# RAG — com verificação live
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
python -m pytest -m rag -v

# smoke — chamadas reais à API (custam tokens!)
export ANTHROPIC_API_KEY=sk-ant-...
python -m pytest -m smoke -v
# ou só um agente:
python -m pytest tests/smoke/test_agent_smoke.py -k agente-portos -v
```

Lint de markdown/yaml (mesmo config usado no CI):

```bash
pip install yamllint
yamllint -c .yamllint.yml .github/workflows tests/rag/collections.yaml tests/smoke/model_map.yaml tests/smoke/queries
npx markdownlint-cli2 "**/*.md"
```

## Como adicionar testes para um novo agente

Digamos que você está criando `agente-edificacoes` (S6 na nomenclatura
v5, ou o próximo segmento livre). Passos:

### 1. Criar o arquivo do agente

`.claude/agents/agente-edificacoes.md` com o frontmatter padrão:

```markdown
---
name: agente-edificacoes
description: Manta 03-SN — Especialista em [domínio]. Roteia quando o usuário menciona [palavras-chave separadas por vírgula, as mesmas usadas no routing do Maestro].
tools: [Read, Grep, Glob, Bash, WebSearch, WebFetch]
model: sonnet
---

# Agente Edificações (Manta 03-SN)

## Contexto de domínio
...

## Ordem canônica de raciocínio
...

## Ferramentas e integrações
...

## Handoff com outros agentes
...

## O que este agente NÃO faz
...
```

Requisitos que os testes `unit` **vão cobrar automaticamente** (ver
`tests/unit/test_agent_schema.py`):

- `name:` no frontmatter == nome do arquivo (sem `.md`).
- `description:` com pelo menos 80 caracteres e contendo a palavra
  "Roteia"/"roteia" (é o que o Maestro usa para decidir o dispatch).
- `tools:` não vazio e só com tools da allowlist
  (`tests/lib/agent_loader.py::ALLOWED_TOOLS` — adicione lá se
  precisar de uma tool nova, ex: `Task`).
- `model:` um de `haiku`/`sonnet`/`opus` (ou combinação com `/`, ex:
  `sonnet/opus`).
- Corpo com as seções `## Contexto de domínio` e `## Handoff` (podem
  ter texto depois do título, ex: "## Handoff com outros agentes").
- Corpo com pelo menos 500 caracteres (não pode ser um stub).
- Título do corpo no padrão `# Agente X (Manta 03-SN)`, e o código
  `Manta 03-SN` deve também aparecer na `description:` (pega
  copy-paste malfeito entre agentes).

### 2. Registrar no CLAUDE.md

Adicione uma linha na tabela "Eixo 2 — Verticais por segmento" e (se
aplicável) uma regra em "ROUTING — Maestro". O teste
`tests/unit/test_registry_consistency.py` falha se o arquivo existir
sem entrada no CLAUDE.md, ou vice-versa.

### 3. Criar as 5 perguntas de smoke test

`tests/smoke/queries/agente-edificacoes.yaml`:

```yaml
- prompt: "Pergunta realista nº 1 que um usuário faria a este agente."
  expect_any: ["termo1", "termo2"]   # pelo menos um deve aparecer na resposta (case-insensitive)

- prompt: "Pergunta nº 2..."
  expect_any: ["..."]

# ... até 5 entradas no total (mínimo obrigatório, o teste falha com menos)
```

Nenhuma outra mudança de código é necessária — `test_agent_smoke.py`
descobre o arquivo automaticamente pelo nome (`<slug-do-agente>.yaml`)
e roda os 5 casos como testes parametrizados
(`agente-edificacoes-q1` … `agente-edificacoes-q5`), cada um com
limite de 30s.

Escolha os `expect_any` com cuidado: são uma checagem de **relevância
mínima** (o agente não alucinou um domínio completamente diferente),
não de corretude técnica — isso continua sendo responsabilidade de QA
humano / da skill `aluci-guard` antes de qualquer entrega a cliente.

### 4. (Se o agente tiver coleção RAG própria) Registrar em collections.yaml

Adicione em `tests/rag/collections.yaml`:

```yaml
  - name: edificacoes
    storage_prefix: "edi:"
    min_chunks: 0   # trocar para > 0 quando a coleção estiver populada em produção
```

E garanta que a mesma coleção apareça na tabela "RAG — Coleções em
Supabase" do `CLAUDE.md` e em algum arquivo de
`supabase/migrations/*.sql` — os 3 lugares são checados por
`tests/rag/test_rag_collections.py` e precisam ficar em sincronia.

### 5. Adicionar ao matrix do smoke job

Em `.github/workflows/agent-test.yml`, job `smoke`, adicione o slug à
lista da matrix:

```yaml
    strategy:
      matrix:
        agent:
          - agente-portos
          - agente-aeroportos
          - agente-saneamento
          - agente-energia
          - agente-barragens
          - agente-edificacoes   # <- novo
```

(Sem isso, o teste do novo agente ainda roda dentro do job `smoke` se
disparado manualmente, mas não terá sua própria entrada paralela/isolada
no CI nem seu próprio artifact de relatório.)

### 6. Rodar localmente antes de abrir o PR

```bash
python -m pytest -m unit -v -k agente-edificacoes
python -m pytest -m rag -v -k edificacoes
ANTHROPIC_API_KEY=sk-ant-... python -m pytest tests/smoke/test_agent_smoke.py -k agente-edificacoes -v
```

## Artefatos gerados pelo CI

Cada job publica seu próprio JUnit XML (e o job `unit` também publica
cobertura) como artifact do workflow run:

- `test-report-lint`
- `test-report-unit` (+ `unit-coverage.xml`)
- `test-report-rag`
- `test-report-smoke-<agente>` (um por agente na matrix)
- `test-report-full` (bundle agregado, gerado pelo job `report`)

O job `report` também publica um resumo consolidado via
`dorny/test-reporter` (visível na aba "Checks" do PR e no Step
Summary do run).

## Atualizando o mapeamento de modelo (smoke tests)

`tests/smoke/model_map.yaml` traduz o tier declarado no frontmatter do
agente (`model: sonnet`) para um model ID real da API. Quando a
Anthropic lançar um novo modelo e a Manta quiser migrar os agentes,
atualize **só este arquivo** — nenhum `.claude/agents/*.md` precisa
mudar, porque eles declaram apenas o tier.

## Por que RAG e smoke usam "skip" em vez de "fail" quando falta secret

Este repositório é a fonte canônica versionada dos agentes, mas quem
abre PR nem sempre tem acesso aos secrets de produção (ex:
colaboradores externos, PRs de fork, ambientes de sandbox). Bloquear
todo PR nesses casos tornaria o repositório inutilizável para
contribuições legítimas de schema/documentação. Por isso:

- `lint` e `unit` **nunca** dependem de secret — são sempre um gate
  real e obrigatório.
- `rag` e `smoke` degradam de forma graciosa (skip) quando o secret
  falta, mas na branch `main` (onde secrets sempre estão disponíveis)
  as variáveis `REQUIRE_SMOKE_TESTS` / `REQUIRE_RAG_LIVE_TESTS` forçam
  falha real em vez de skip silencioso — então um secret revogado por
  engano ainda quebra o pipeline de `main`, só não quebra PRs de fork.
