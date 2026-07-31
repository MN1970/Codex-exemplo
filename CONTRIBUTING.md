# Contributing to Codex Hub MCP

Obrigado por considerar contribuir ao Codex Hub! Este documento descreve como configurar o ambiente local, seguir padrões de código, rodar testes e enviar contribuições.

---

## Setup Local

### Pré-requisitos

- **Node.js** >= 18.0.0
- **npm** >= 9.0.0
- **Docker** e **Docker Compose** (opcional, mas recomendado)
- **Git**

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/manta-associados/codex-hub-mcp.git
   cd codex-hub-mcp
   ```

2. Instale as dependências (usa `npm ci` para reprodutibilidade):
   ```bash
   npm ci
   ```

3. **Opção A: Desenvolvimento local direto**
   ```bash
   npm run dev
   ```
   O servidor inicia em `http://localhost:3000` com hot-reload via `tsx`.

4. **Opção B: Com Docker Compose** (recomendado)
   ```bash
   docker-compose up
   ```
   Isso sobe:
   - App (Node) na porta 3000
   - PostgreSQL na porta 5432
   - Redis na porta 6379

5. Verifique a instalação:
   ```bash
   curl http://localhost:3000/health
   ```

### Variáveis de Ambiente

Crie um arquivo `.env.local` na raiz do projeto (não é versionado):

```env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
SUPABASE_URL=http://localhost:3000
SUPABASE_ANON_KEY=seu_anon_key_aqui
REDIS_URL=redis://localhost:6379
LOG_LEVEL=debug
```

### Parar os containers

```bash
docker-compose down
```

Para remover volumes (reset completo do banco):
```bash
docker-compose down -v
```

---

## Coding Standards

### TypeScript Strict Mode

Todos os arquivos TypeScript devem ser escritos com **strict mode ativado**. Verifique `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

**Checklist:**
- Sempre declare tipos explícitos para parâmetros e retornos
- Não use `any` — use `unknown` se necessário
- Ative `strict` mesmo em desenvolvimento

Exemplo correto:
```typescript
function processAgent(id: string, config: AgentConfig): Promise<void> {
  // implementação
}
```

Exemplo incorreto:
```typescript
function processAgent(id: any, config: any) {
  // falta tipos e tipos implícitos
}
```

### Linting com ESLint

Executar linting:
```bash
npm run lint
```

Corrigir automaticamente:
```bash
npm run lint:fix
```

**Regras principais** (`.eslintrc.json`):
- Sem variáveis não utilizadas
- Sem console.log em produção (use logger pino)
- Sem tipos implícitos
- Máximo 100 caracteres por linha (readability)

### Type Checking

Antes de fazer commit, verifique tipos:
```bash
npm run type-check
```

Isso executa TypeScript em modo `--noEmit` sem compilar.

### Convenções de Código

- **Nomes de variáveis:** camelCase
- **Nomes de tipos/interfaces:** PascalCase
- **Constantes:** UPPER_SNAKE_CASE
- **Imports:** agrupe por origem (stdlib → deps → local)
  ```typescript
  import { readFile } from 'fs/promises';
  import express from 'express';
  import { AgentConfig } from './types.js';
  ```

### Organização de pastas

```
src/
  ├── index.ts                 # entry point
  ├── types/                   # TypeScript interfaces
  ├── services/                # business logic
  ├── handlers/                # MCP request handlers
  ├── utils/                   # helpers e utilities
  ├── db/                       # database queries
  ├── middleware/              # express middleware
  └── config.ts                # configuração centralizada
```

---

## Testing Requirements

### Cobertura Mínima

**> 70% de cobertura de código** é obrigatório. PRs que reduzem cobertura serão rejeitadas.

Rodar testes:
```bash
npm run test
```

Com coverage report:
```bash
npm run test:coverage
```

Modo watch (desenvolvimento):
```bash
npm run test:watch
```

### Escrevendo Testes

Use Jest + **supertest** para testes de API. Exemplo:

```typescript
import request from 'supertest';
import { app } from '../src/index';

describe('POST /agents', () => {
  it('should create an agent with valid config', async () => {
    const res = await request(app)
      .post('/agents')
      .send({
        name: 'agente-portos',
        tier: 'Sonnet',
      });

    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.name).toBe('agente-portos');
  });

  it('should reject invalid tier', async () => {
    const res = await request(app)
      .post('/agents')
      .send({ name: 'test', tier: 'InvalidModel' });

    expect(res.status).toBe(400);
  });
});
```

### Coverage por módulo

- **handlers/**: >= 90% (críticos)
- **services/**: >= 80%
- **utils/**: >= 70%
- **db/**: >= 75%

Se um módulo fica abaixo, aumente antes de fazer merge.

---

## Commit Messages (Conventional Commits)

Siga o padrão **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Tipos permitidos

- **feat**: nova feature
- **fix**: correção de bug
- **refactor**: reorganização sem mudança de comportamento
- **perf**: otimização de performance
- **test**: adição ou correção de testes
- **docs**: documentação
- **chore**: build, deps, CI (não afeta código)
- **style**: formatação, espaços (sem lógica)

### Exemplos

```
feat(agents): add saneamento segment support

- Implemented agente-saneamento S8 routing
- Added SNIS document handler
- Created rag_chunks collection for saneamento

Closes #42
```

```
fix(db): handle null migration timestamps

Ensure migration runner doesn't crash on missing timestamps.

Fixes #103
```

```
docs: update CONTRIBUTING setup steps
```

### Regras

- **Subject**: imperativo, não capitalized, sem ponto no final (50 char máx)
- **Body**: explique o "porquê", não o "o quê"
- **Footer**: referência issues com `Closes #123` ou `Fixes #456`
- Sem linhas > 100 caracteres

**Git hook automático**: considere adicionar husky + commitlint para validação local:
```bash
npm install --save-dev husky @commitlint/config-conventional @commitlint/cli
npx husky install
npx husky add .husky/commit-msg 'npx --no commitlint --edit "$1"'
```

---

## PR Process

### Antes de abrir a PR

1. **Faça um fork** e crie uma branch descritiva:
   ```bash
   git checkout -b feat/agente-saneamento
   ```

2. **Atualize da main**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

3. **Rode a suíte completa localmente**:
   ```bash
   npm run type-check
   npm run lint
   npm run test:coverage
   npm run build
   ```
   Todos devem passar.

4. **Faça commits atômicos** seguindo Conventional Commits

### Abrindo a PR

1. Abra a PR contra `main`
2. Use o template: `PR title` deve seguir `<type>(<scope>): <description>`
3. **Descrição obrigatória**:
   - Resumo das mudanças
   - Contexto (por quê)
   - Como testar
   - Screenshots/logs se aplicável
   - Links para issues/tickets

Exemplo:
```markdown
## Description
Adiciona suporte ao segmento Saneamento (S8) com integração SNIS.

## Changes
- [ ] Novo handler para documentos de saneamento
- [ ] Coleção RAG `rag_chunks` populada
- [ ] Routing no Maestro atualizado
- [ ] Testes de integração

## Testing
```bash
npm run test -- --testPathPattern=saneamento
```

Closes #42
```

### Requisitos para Merge

- [ ] **CI passes** (GitHub Actions ou similar)
  - Type check ✓
  - Lint ✓
  - Tests ✓ (coverage > 70%)
  - Build ✓
- [ ] **Pelo menos 1 aprovação** de code review
- [ ] **Sem conflitos** com `main`
- [ ] **Commits limpos** (rebase interativo se necessário)
- [ ] **Documentação atualizada** se foi mudança de API

### Code Review

Esperamos:
- Código legível e bem comentado
- Testes para novas features
- Sem hardcodes ou secrets
- Performance aceitável
- Sem dead code

Reviewers podem solicitar mudanças. Faça push novos commits (não force-push) até approval.

---

## Troubleshooting

### Problema: Dependências não instalam

**Solução:**
```bash
rm -rf node_modules package-lock.json
npm ci
```

### Problema: Porta 3000 já em uso

**Solução:**
```bash
lsof -i :3000
kill -9 <PID>
# ou altere PORT no .env.local
PORT=3001 npm run dev
```

### Problema: Docker Compose falha

**Verifique containers:**
```bash
docker-compose ps
docker-compose logs app
docker-compose logs supabase
```

**Reset completo:**
```bash
docker-compose down -v
docker-compose up --build
```

### Problema: Testes falham localmente

1. **Verifique NODE_ENV:**
   ```bash
   echo $NODE_ENV  # deve ser 'development' ou 'test'
   ```

2. **Limpe cache Jest:**
   ```bash
   npm run test -- --clearCache
   ```

3. **Rode teste único:**
   ```bash
   npm run test -- --testNamePattern="AgentService"
   ```

### Problema: Type checking falha

**Verifique imports:**
```bash
npm run type-check
# Saída mostra arquivos problemáticos
```

Erros comuns:
- Falta `as const` em tipos literais
- Função esperada, valor fornecido
- Propriedade não existe na interface

### Problema: ESLint recusa commit

**Corrija automaticamente:**
```bash
npm run lint:fix
```

Se ainda falhar, edite manualmente os erros listados em:
```bash
npm run lint
```

### Problema: Coverage abaixo de 70%

```bash
npm run test:coverage
# Abre coverage/index.html (se usar ferramenta gráfica)
```

Adicione testes para módulos em vermelho:
```bash
# Exemplo: src/services/AgentService.ts tem 40%
npm run test -- --testPathPattern=AgentService --coverage
```

---

## Stack & Versões

| Ferramenta | Versão | Uso |
|------------|--------|-----|
| Node.js | >= 18.0.0 | Runtime |
| TypeScript | 5.3.3 | Type safety |
| Jest | 29.7.0 | Testing framework |
| ESLint | 8.56.0 | Code linting |
| Express | 4.18.2 | HTTP server |
| Pino | 8.17.0 | Logger |
| Supabase | 2.38.0 | Database client |
| Docker Compose | 3.8 | Local infra |

---

## Contato

- Issues: Abra uma [issue no GitHub](https://github.com/manta-associados/codex-hub-mcp/issues)
- Perguntas: Abra uma discussion
- Secretos/security: contato privado em security@manta-associados.com

---

Obrigado por contribuir! 🙏
