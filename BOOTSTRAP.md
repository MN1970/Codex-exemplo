# Bootstrap Script - Codex Hub MCP

Inicializa o ambiente completo da Manta Maestro v4.2 para Docker build.

## Overview

O script `scripts/bootstrap.sh` automatiza o setup completo do projeto:

1. **Validação de pré-requisitos** (Node.js >= 18, npm >= 9)
2. **Instalação de dependências** (`npm ci`)
3. **Setup do banco de dados** (migrations + seed dos 20 agentes Manta)
4. **Compilação TypeScript** (`npm run build`)
5. **Testes e linting** (`npm run test`, `npm run lint`)
6. **Health checks** (validação de estrutura e schema)
7. **Output**: "Ready for Docker build"

## Uso Rápido

```bash
# Bootstrap completo
./scripts/bootstrap.sh

# Pular database setup (para dev local)
./scripts/bootstrap.sh --skip-db

# Pular health checks
./scripts/bootstrap.sh --skip-health-check

# Ambas opções
./scripts/bootstrap.sh --skip-db --skip-health-check
```

## Arquivos Criados/Modificados

### Scripts
- `scripts/bootstrap.sh` - Script principal (executável)

### Migrations Supabase
- `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` - Routing rules e RAG collections (S6-S10)
- `supabase/migrations/2026_07_31_agents_seed_v4_2.sql` - Seed dos 20 agentes (novo)

### Dados
- `src/data/agents-seed.json` - JSON com dados dos 20 agentes

### Logs
- `.bootstrap.log` - Log detalhado da execução (criado na raiz do projeto)

## Agentes Seedados (v4.2)

### Horizontais (11)
- **manta-00** - Maestro (Router) - Haiku→Sonnet
- **manta-01** - Claims - Opus
- **manta-02** - Contratual - Sonnet
- **manta-04** - Imobiliário - Sonnet
- **manta-05** - Orçamento - Sonnet
- **manta-06** - Modelagem - Sonnet/Opus
- **manta-07** - Cronograma - Sonnet
- **manta-13** - Business Development - Sonnet
- **manta-14** - Apresentações - Sonnet
- **manta-15** - Advisory - Sonnet/Opus
- **manta-16** - Arquiteto IA - Opus

### Verticais (10)
- **manta-03-s1** - Infraestrutura / Rodovias
- **manta-03-s2** - Infraestrutura / OAE (Pontes, Viadutos)
- **manta-03-s3** - Infraestrutura / Ferrovia
- **manta-03-s4** - Infraestrutura / Metrô
- **manta-03-s5** - Infraestrutura / Túneis (parcial)
- **manta-03-s6** - Portos (novo v4.2)
- **manta-03-s7** - Aeroportos (novo v4.2)
- **manta-03-s8** - Saneamento (novo v4.2) - PRIORIDADE AySA
- **manta-03-s9** - Energia (novo v4.2)
- **manta-03-s10** - Barragens (novo v4.2)

**Total: 20 agentes registrados**

## Output do Bootstrap

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ READY FOR DOCKER BUILD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Próximos passos:
  1. Build Docker image:
     npm run docker:build

  2. Rodar com Docker Compose:
     npm run docker:compose

  3. Ou rodar localmente:
     npm run dev
```

## Estrutura do Script

```bash
bootstrap.sh
├── Utility Functions (log, error handling)
├── Argument Parsing (--skip-db, --skip-health-check)
├── validate_prerequisites()        # Node, npm, git
├── install_dependencies()          # npm ci
├── wait_for_database()            # healthcheck DB
├── run_migrations()               # SQL migrations
├── seed_agents()                  # 20 agentes Manta
├── build_project()                # npm run build
├── run_linting()                  # ESLint, type-check
├── run_tests()                    # npm run test
├── check_application_health()     # Validação
├── verify_database_schema()       # Schema check
├── show_summary()                 # Resumo
└── show_ready_status()           # Output "Ready for docker build"
```

## Tratamento de Erros

O script implementa:

- **Exit on error** (`set -e`) - Para em qualquer erro
- **Exit on pipe failure** (`set -o pipefail`) - Captura erros em pipes
- **Exit on unset variables** (`set -u`) - Valida variáveis
- **Trap cleanup** - Função cleanup ao sair
- **Colored output** - Verde (sucesso), Vermelho (erro), Amarelo (warning)
- **Logging** - Todos os outputs salvos em `.bootstrap.log`

## Pré-requisitos

### Sistema
- **Node.js** >= 18.0.0
- **npm** >= 9.0.0
- **git** (opcional, para context)
- **psql** (opcional, para direct DB seed)
- **supabase CLI** (opcional, para migrations)

### Ambiente
- Arquivo `package.json` na raiz do projeto
- Diretório `src/` existente
- Supabase configurado (ou será setup no Docker)

## Variáveis de Ambiente

Opcionais (usadas para database operations):

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
NODE_ENV=development|production
```

## Docker Integration

### Build com Bootstrap

```bash
# O Dockerfile já inclui o bootstrap no build:
# RUN npm ci
# RUN npm run build && npm run test && npm run lint

# Rodar bootstrap antes de build:
./scripts/bootstrap.sh
npm run docker:build
```

### Docker Compose

```bash
# Com bootstrap setup completo:
./scripts/bootstrap.sh
npm run docker:compose

# Verificar status:
docker ps
curl http://localhost:3000/health
```

## Troubleshooting

### "Node.js não encontrado"
```bash
node --version  # deve ser v18 ou superior
nvm use 18 || brew install node@18
```

### "npm ci falhou"
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm ci
```

### "Banco de dados não respondeu"
```bash
# Se usando Docker:
docker compose up -d postgres
sleep 10
./scripts/bootstrap.sh

# Se local:
psql -U postgres -d postgres -c "SELECT 1"
```

### "Seed dos agentes falhou"
```bash
# Verificar se DATABASE_URL está definido:
echo $DATABASE_URL

# Se não, pode ignorar para containers (será executado no startup)
./scripts/bootstrap.sh --skip-db
```

### "Testes falharam"
```bash
# Ver detalhes do test failure:
tail -100 .bootstrap.log

# Rodar testes manualmente:
npm run test

# Ou sem parar no erro:
npm run test -- --passWithNoTests
```

## Performance

Tempo típico de execução (development machine):
- Validação: ~1s
- npm ci: ~30-60s (primeira vez, depois ~10s com cache)
- Migrations: ~2s
- Seed data: ~3-5s
- Build: ~10-20s
- Tests: ~5-15s
- Linting: ~3-5s
- Health checks: ~2s

**Total: ~1-2 minutos (primeira vez) / ~1 minuto (depois)**

## Logs e Debugging

Todos os outputs são salvos em `.bootstrap.log`:

```bash
# Ver log completo
cat .bootstrap.log

# Ver apenas erros
grep "✗" .bootstrap.log

# Ver status de sucesso
grep "✓" .bootstrap.log

# Tail em tempo real (enquanto script roda)
tail -f .bootstrap.log
```

## Ticket de Referência

- **MNT-2026-UPGRADE-AGENTS-S6S10** - Expansão S6-S10 (Portos, Aeroportos, Saneamento, Energia, Barragens)
- **v4.2** - Versão Manta Maestro com 20 agentes

## Próximos Passos

Após bootstrap bem-sucedido:

```bash
# 1. Verificar agentes no banco
psql $DATABASE_URL -c "SELECT code, name, status FROM agents ORDER BY code;"

# 2. Rodar em desenvolvimento
npm run dev

# 3. Ou build Docker
npm run docker:build
docker run -p 3000:3000 codex-hub-mcp:latest

# 4. Health check
curl http://localhost:3000/health
```

## Referência Completa

- CLAUDE.md - Registro mestre dos agentes (projeto)
- docker-compose.yml - Configuração Docker
- Dockerfile - Multi-stage build
- package.json - Dependências e scripts
- supabase/migrations/ - Migration files

---

**Versão**: 4.2  
**Data**: 2026-07-31  
**Autor**: Manta Associados  
**Licença**: MIT
