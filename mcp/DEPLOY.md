# Deploy Guide — MantaBase MCP v2

**Versão**: 2.0.0 | **Ambientes**: Netlify (ativo), Railway (pendente) | **Status**: P4 em andamento

---

## Ambiente local

### Setup

```bash
cd mcp/
pip install -e ".[dev]"
```

### Variáveis de ambiente

```bash
export MANTABASE_SECRET_KEY="dev-key-change-in-prod"
export SUPABASE_URL="https://project.supabase.co"
export SUPABASE_KEY="your-api-key"
```

### Executar servidor

```bash
python server.py
```

### Rodar testes

```bash
pytest tests/ -v --tb=short
```

---

## Deploy Netlify (ativo)

### Pré-requisitos

- Conta Netlify ligada ao repositório
- Environment variables configuradas no painel

### Configuração

**Arquivo**: `netlify.toml`

```toml
[build]
command = "pip install -e . && python -m pytest tests/ -v"
functions = "functions"

[functions."mcp"]
runtime = "python3.11"
handler = "server.run"
```

### Deploy automático

1. Push para `claude/mantabase-mcp-v2-arch-ala0oo`
2. Netlify detecta `netlify.toml`
3. Build: instala, roda testes
4. Deploy: função serverless em `/.netlify/functions/mcp`

### Secrets (Netlify UI)

- `MANTABASE_SECRET_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Health check

```bash
curl https://<site>.netlify.app/.netlify/functions/mcp/health
```

---

## Deploy Railway (pendente — P4)

### Pré-requisitos

- Conta Railway
- GitHub connected
- Docker instalado localmente (para testes)

### Configuração

**Arquivo**: `railway.toml` + `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY mcp/ mcp/
RUN pip install -e .
HEALTHCHECK --interval=30s --timeout=10s CMD python -c "..."
EXPOSE 8000
CMD ["python", "mcp/server.py"]
```

### Deploy via Railway CLI

```bash
railway init
railway up
```

Ou via GitHub:

1. Conectar repositório em railway.app/new
2. Railway detecta `Dockerfile`
3. Build automático
4. Deploy em `mcp-prod.up.railway.app`

### Secrets (Railway UI)

- `MANTABASE_SECRET_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Health check

```bash
curl https://mcp-prod.up.railway.app/health
```

---

## Eliminar duplicidade (P4)

Escolher **um** ambiente:

| Aspecto | Netlify | Railway |
|---------|---------|---------|
| Cold starts | ~1-2s | ~500ms |
| Pricing | Free tier | Pay-as-you-go |
| Scaling | Automático | Manual |
| Logs | Dashboard | CLI integrado |

**Recomendação**: Railway para produção (melhor latência), Netlify para staging.

---

## CI/CD

### GitHub Actions (futuro)

```yaml
name: MCP v2 CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v
```

### Deploy automático (futuro)

- Push `main` → Netlify staging
- Tag release → Railway produção

---

## Monitoramento

### Logs

**Netlify**: `netlify logs` ou painel web

**Railway**: `railway logs`

### Metrics

- Latência média
- Taxa de erro
- Uso de memória (container)

### Alertas (futuro)

- CI failure → Slack
- Health check fail → Email
- Cold start > 5s → Dashboard

---

## Troubleshooting

### Build failure

```bash
# Localmente
pip install -e . && pytest tests/
```

Se passar localmente mas falhar em CI → diferença de Python/deps.

### Runtime error

```bash
# Verificar logs
netlify logs  # ou railway logs
```

### Secret missing

Verificar `MANTABASE_SECRET_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` em:
- Netlify UI → Site settings → Environment
- Railway UI → Variables

---

## Próximas fases

- [ ] Implementar GitHub Actions CI/CD
- [ ] Monitora logging (Sentry, Datadog)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] API versioning (v1, v2)

---

**Última atualização**: 2026-07-24 | **Ticket**: MNT-2026-UPGRADE-AGENTS-S6S10
