# Codex Hub – MCP Server

Codex Hub é o Model Context Protocol (MCP) server central da Manta Associados que orquestra a comunicação entre agentes IA especializados e sistemas externos. Funciona como hub de integração para o Maestro (roteador inteligente), conectando SharePoint, Supabase, Git e Claude via protocolos padronizados.

## Quick Start

```bash
# Instalar dependências
npm ci

# Executar em desenvolvimento (com watch)
npm run dev

# Em outro terminal, testar a saúde do servidor
curl http://localhost:3000/health
```

O servidor inicia em `http://localhost:3000` com suporte a MCP tools, health checks e webhooks.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Claude / Maestro                      │
│              (MCP Client Consumer)                        │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     ▼
        ┌────────────────────────────────┐
        │   Codex Hub MCP Server         │
        │    (localhost:3000)            │
        ├────────────────────────────────┤
        │                                │
        │  ┌──────────┐ ┌────────────┐  │
        │  │ Services │ │  Adapters  │  │
        │  ├──────────┤ ├────────────┤  │
        │  │ Maestro  │ │ Git        │  │
        │  │ Router   │ │ Adapter    │  │
        │  ├──────────┤ │            │  │
        │  │ Agent    │ │ Cowork     │  │
        │  │ Details  │ │ Adapter    │  │
        │  └──────────┘ │            │  │
        │               │ State      │  │
        │               │ Manager    │  │
        │               └────────────┘  │
        └────────────────────────────────┘
             │          │          │
             ▼          ▼          ▼
        ┌────────┐ ┌────────┐ ┌────────┐
        │ GitHub │ │SharePt │ │Supabase│
        │  API   │ │ Online │ │  API   │
        └────────┘ └────────┘ └────────┘
```

## Project Structure

```
codex-hub/
├── src/
│   ├── adapters/
│   │   ├── git-adapter.ts          # Integração com GitHub/Git
│   │   ├── cowork-adapter.ts       # Bridge com Claude Cowork
│   │   └── state-manager.ts        # Gerenciamento de estado compartilhado
│   ├── services/
│   │   ├── maestro-router.ts       # Roteamento inteligente de requisições
│   │   ├── get-agent-details.ts    # Leitura de metadados dos agentes
│   │   └── __tests__/              # Testes unitários
│   └── (index.ts em implementação)
├── tests/                           # Testes de integração
├── docs/
│   ├── COWORK-INTEGRATION.md
│   └── DEPLOY-v4.2.md
├── .claude/
│   └── agents/                      # Definições canônicas dos agentes
│       ├── agente-portos.md
│       ├── agente-aeroportos.md
│       ├── agente-saneamento.md
│       ├── agente-energia.md
│       └── agente-barragens.md
├── supabase/                        # Migrações e tipos
├── sharepoint/                      # Mapeamento de pastas SP
├── .env.example                     # Variáveis de ambiente
├── package.json
├── tsconfig.json
├── jest.config.js
├── Dockerfile
├── docker-compose.yml
└── CLAUDE.md                        # Registry mestre dos agentes
```

## API / Tools

O Codex Hub expõe as seguintes 4 ferramentas MCP primárias:

### 1. **Maestro Router** (`maestro-router.ts`)
Roteador inteligente que classifica requisições de candidatos IA para agentes verticais (S1–S10) com base em keywords semânticas e histórico de requisição.

- Entrada: prompt do usuário, contexto do projeto
- Saída: agente recomendado (S1: Rodovias, S2: OAE, S3: Ferrovia, etc.)

### 2. **Get Agent Details** (`get-agent-details.ts`)
Leitura de metadados canônicos dos agentes (versão, tier, skills, RAG collections) a partir do registro mestre no Supabase.

- Entrada: agent_id (ex: "manta-03-s8")
- Saída: JSON com definição completa + endpoints

### 3. **Git Adapter** (`git-adapter.ts`)
Ponte bidirecional com repositórios GitHub (Codex-exemplo, manta-hub) para sincronizar CLAUDE.md, agentes .md e pushes automáticos.

- Operações: clone, pull, commit, push com validação de assinatura

### 4. **Cowork Adapter** (`cowork-adapter.ts`)
Integração com o runtime do Claude Cowork para gerenciamento de sessões, chat persistente e estado de candidatos.

- Operações: criar/atualizar sessão, registrar eventos, broadcast

## Testing

```bash
# Executar testes com Jest
npm run test

# Com watch mode (reexecuta ao salvar)
npm run test:watch

# Com coverage report
npm run test:coverage

# Lint TypeScript
npm run lint
npm run lint:fix

# Type check sem emitir código
npm run type-check
```

Testes residem em `src/**/__tests__` (colocado do lado do código) e em `tests/` para testes de integração.

## Deployment

### Docker (Recomendado)

```bash
# Build da imagem
npm run docker:build

# Executar container
npm run docker:run

# Ou usando docker-compose (com Supabase local)
npm run docker:compose

# Parar containers
npm run docker:compose:down
```

Build usa multi-stage: builder (compile + test + lint) → runtime (distribuição minimalista com nodejs:20-alpine).

### Staging / Produção

```bash
# Preparação (build → test → lint)
npm run deploy

# Deploy para staging
npm run deploy:staging

# Deploy para produção
npm run deploy:prod
```

Cada deploy executa pipeline de validação; scripts em `scripts/deploy-*.js` gerenciam versioning e rollback.

## Contributing Guidelines

1. **Branch & Commit**
   - Criar feature branch: `git checkout -b feature/descricao`
   - Commits descritivos: `feat: adicionar roteador Maestro`, `fix: validação de agente`
   - Seguir convenção [Conventional Commits](https://www.conventionalcommits.org/)

2. **Code Quality**
   - Sempre rodar `npm run lint:fix` antes de commitar
   - Passar em `npm run test` e `npm run type-check`
   - Comentar código complexo; incluir docstrings em serviços

3. **Pull Requests**
   - Descrever mudanças em linguagem clara
   - Referenciar issues (`fixes #123`)
   - Aguardar aprovação de reviewer (idealmente MN ou tech lead)
   - Squash commits antes de merge: `git rebase -i origin/main`

4. **Agentes & CLAUDE.md**
   - Alterações em `.claude/agents/*.md` ou `CLAUDE.md` seguem gate humano (aprovação MN)
   - Não fazer push direto para main; usar PR + code review
   - Atualizar versão em `CLAUDE.md` (ex: v4.2 → v4.3)

5. **Environment Variables**
   - Copiar `.env.example` → `.env.local` para desenvolvimento local
   - Nunca commitar `.env` ou secrets em código
   - Documentar novas variáveis em `.env.example`

6. **Testing**
   - Adicionar testes para novos endpoints/adaptadores
   - Manter cobertura acima de 80% para mudanças
   - Testar integração com Supabase, SharePoint e Git antes de merge

---

**Versão:** v1.0.0 | **Node:** ≥18.0.0 | **npm:** ≥9.0.0 | **License:** MIT
