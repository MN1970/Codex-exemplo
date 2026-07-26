# manta-frontend

Skeleton React + Vite + TypeScript para o front-end da Manta Associados.

## Stack

- **React 19** + **TypeScript** + **Vite**
- **react-router-dom** — roteamento
- **axios** — cliente HTTP (`src/api/client.ts`)
- **zustand** — estado global (`src/store/`)
- **Tailwind CSS v4** + componentes estilo **shadcn/ui** (`src/components/ui/`)
- **ESLint** + **Prettier**
- Tema **light/dark** persistido em `localStorage`

## Estrutura

```
src/
├── api/            # cliente axios + módulos de endpoint (um arquivo por recurso)
├── components/
│   ├── ui/         # componentes shadcn/ui (Button, Card, ...)
│   └── layout/      # Header, Layout (casca da aplicação)
├── hooks/          # hooks reutilizáveis
├── lib/            # utils (cn, env)
├── pages/          # rotas
├── store/          # zustand stores (theme, app, ...)
├── styles/         # globals.css (Tailwind + tokens de tema)
├── types/          # tipos compartilhados
├── App.tsx         # definição das rotas
└── main.tsx        # bootstrap da aplicação
```

Novos componentes shadcn podem ser adicionados com `npx shadcn@latest add <componente>`
(configuração em `components.json`).

## Desenvolvimento

```bash
npm install
cp .env.example .env   # ajuste VITE_API_BASE_URL conforme o backend
npm run dev             # http://localhost:5173
```

Scripts disponíveis:

| Script                 | Descrição                                |
| ---------------------- | ---------------------------------------- |
| `npm run dev`          | servidor de desenvolvimento (porta 5173) |
| `npm run build`        | typecheck + build de produção em `dist/` |
| `npm run preview`      | serve o build de produção localmente     |
| `npm run lint`         | ESLint                                   |
| `npm run lint:fix`     | ESLint com autofix                       |
| `npm run format`       | Prettier (escreve)                       |
| `npm run format:check` | Prettier (somente verifica)              |
| `npm run typecheck`    | `tsc` sem emitir arquivos                |

## Docker

```bash
docker compose up --build
# ou
docker build -t manta-frontend .
docker run -p 5173:5173 manta-frontend
```

Build multi-stage: compila com Node 22 e serve os estáticos via Nginx na
porta **5173**, com fallback de SPA (`try_files ... /index.html`) para o
roteamento do react-router.

## Variáveis de ambiente

| Variável            | Descrição                                             | Default          |
| ------------------- | ----------------------------------------------------- | ---------------- |
| `VITE_API_BASE_URL` | base URL do backend consumido por `src/api/client.ts` | `/api`           |
| `VITE_APP_NAME`     | nome exibido no header                                | `Manta Frontend` |
