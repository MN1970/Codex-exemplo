# 🚀 Production Deployment — Maestro Sync Server

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Date:** 2026-07-31

---

## 📋 Pré-requisitos

- Docker 24.0+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space
- SSL certificate (for HTTPS)
- Environment variables configured

---

## 🔧 Setup Inicial (15 minutos)

### 1️⃣ Preparar Servidor

```bash
# SSH into production server
ssh user@prod-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/maestro
cd /opt/maestro

# Clone repository
git clone https://github.com/MN1970/Codex-exemplo.git .
```

### 2️⃣ Configurar Variáveis de Ambiente

```bash
# Create .env.prod file
cat > .env.prod << 'EOF'
# Node environment
NODE_ENV=production
MCP_PORT=3001
LOG_LEVEL=info

# Claude AI / Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Cowork API
COWORK_API_URL=https://cowork.example.com/api
COWORK_API_TOKEN=token_xxxxx

# MCP Server authentication
MCP_API_TOKEN=secure-token-xxxxx

# Docker
COMPOSE_PROJECT_NAME=maestro-prod
EOF

# Proteger arquivo
chmod 600 .env.prod
```

### 3️⃣ Configurar SSL/TLS

```bash
# Create certificates directory
mkdir -p certs

# Option A: Use Let's Encrypt (recomendado)
certbot certonly --standalone \
  -d maestro.example.com \
  -d api.maestro.example.com

# Copy certificates
sudo cp /etc/letsencrypt/live/maestro.example.com/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/maestro.example.com/privkey.pem certs/key.pem
sudo chown -R $(id -u):$(id -g) certs/

# Option B: Use self-signed (apenas desenvolvimento)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem -keyout certs/key.pem -days 365 \
  -subj "/CN=maestro.example.com"
```

### 4️⃣ Atualizar Configuração Nginx

```bash
# Update nginx.conf com seu domínio
sed -i 's/maestro.example.com/seu-dominio.com/g' nginx.conf

# Verify nginx configuration
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t
```

---

## 🐳 Deploy com Docker Compose

### Build da Imagem

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Ou: usar pre-built image
docker pull mn1970/maestro:1.0.0
```

### Iniciar Serviços

```bash
# Iniciar todos os serviços
docker-compose -f docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f maestro-sync-server
```

### Health Check

```bash
# Verificar saúde do serviço
curl https://maestro.example.com/health

# Esperado:
# {
#   "status": "operational",
#   "service": "MCP Maestro Sync Server",
#   "version": "1.0.0",
#   "features": [...]
# }
```

---

## 🔐 Segurança em Produção

### 1. API Authentication

```bash
# Adicionar autenticação ao .env.prod
export MCP_API_TOKEN="super-secret-token-32-chars-minimum"

# Todos os requests devem incluir header:
curl -H "X-API-Key: super-secret-token-32-chars-minimum" \
  https://maestro.example.com/mcp/agents
```

### 2. CORS (Cross-Origin)

Se integrado com sites externos, configure CORS:

```typescript
// Em src/mcp-server.ts
import cors from 'cors';

app.use(cors({
  origin: ['https://claude.ai', 'https://seu-site.com'],
  credentials: true,
  optionsSuccessStatus: 200
}));
```

### 3. Rate Limiting

Está configurado no nginx.conf:
- API endpoints: 100 req/s
- Webhooks: 50 req/s

### 4. WAF (Web Application Firewall)

```bash
# Ativar ModSecurity no nginx
docker run -d \
  -p 8443:443 \
  -p 8080:80 \
  -e SERVERNAME=maestro.example.com \
  -e CERTNAME=letsencrypt \
  -e PARANOIA=2 \
  ghcr.io/coreruleset/modsecurity-docker:latest
```

---

## 📊 Monitoramento

### Health Check Automático

```bash
# Criar script de monitoramento
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://maestro.example.com/health)
  if [ "$STATUS" != "200" ]; then
    echo "Alert: Service unhealthy (HTTP $STATUS)"
    # Send alert via email/Slack
  fi
  sleep 300
done
EOF

chmod +x monitor.sh
./monitor.sh &
```

### Logs

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f --tail=100 maestro-sync-server

# Salvar logs localmente
docker-compose -f docker-compose.prod.yml logs maestro-sync-server > logs.txt

# Análise de logs (grep de errors)
docker-compose -f docker-compose.prod.yml logs maestro-sync-server | grep ERROR
```

### Métricas

```bash
# Verificar uso de recursos
docker stats maestro-sync-prod

# Esperado:
# CONTAINER      CPU %    MEM USAGE / LIMIT
# maestro-sync   0.1%     120MiB / 512MiB
```

---

## 🔄 Atualizações & Rollback

### Atualizar para Nova Versão

```bash
# 1. Pull nova versão
git pull origin main

# 2. Rebuild imagem
docker-compose -f docker-compose.prod.yml build

# 3. Parar versão antiga (sem perder dados)
docker-compose -f docker-compose.prod.yml down

# 4. Iniciar nova versão
docker-compose -f docker-compose.prod.yml up -d

# 5. Verificar saúde
curl https://maestro.example.com/health
```

### Rollback Automático

```bash
# Se health check falhar, voltar versão anterior
docker-compose -f docker-compose.prod.yml down
git checkout HEAD~1
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔌 Integração com Claude AI

### Registrar MCP Server

1. Acesse: **claude.ai → Settings → Claude Code → MCP Servers**
2. Adicione:

```json
{
  "name": "maestro-sync-prod",
  "command": "curl",
  "args": [
    "-X", "POST",
    "-H", "Content-Type: application/json",
    "-H", "X-API-Key: seu-api-token",
    "-d", "@-",
    "https://maestro.example.com/mcp/sync-prompt"
  ]
}
```

### Ou via SSH tunnel (mais seguro)

```bash
# SSH config
Host maestro-prod
  HostName maestro.example.com
  User maestro-user
  Port 22
  LocalForward 3001 localhost:3001

# Connect
ssh maestro-prod

# No Claude: localhost:3001 fica disponível
```

---

## ⚙️ Backup & Recovery

### Backup Automático

```bash
#!/bin/bash
# backup.sh - Executar diariamente via cron

BACKUP_DIR="/backups/maestro"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup de dados
docker-compose -f /opt/maestro/docker-compose.prod.yml exec -T \
  maestro-sync-server \
  tar czf - /app/data > $BACKUP_DIR/maestro-$TIMESTAMP.tar.gz

# Manter últimos 30 dias
find $BACKUP_DIR -name "maestro-*.tar.gz" -mtime +30 -delete

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR/maestro-$TIMESTAMP.tar.gz \
  s3://seu-bucket/backups/maestro/
```

### Cron Job

```bash
# Adicionar ao crontab
0 2 * * * /opt/maestro/backup.sh >> /var/log/maestro-backup.log 2>&1
```

### Restaurar de Backup

```bash
# Extrair backup
tar xzf maestro-YYYYMMDD_HHMMSS.tar.gz -C /opt/maestro/

# Reiniciar serviço
docker-compose -f docker-compose.prod.yml restart maestro-sync-server
```

---

## 📈 Scaling & Performance

### Load Balancing

Para múltiplas instâncias:

```yaml
# docker-compose.prod.yml
services:
  maestro-1:
    build: .
    environment:
      INSTANCE_ID: 1
  maestro-2:
    build: .
    environment:
      INSTANCE_ID: 2
  maestro-3:
    build: .
    environment:
      INSTANCE_ID: 3

  nginx:
    depends_on:
      - maestro-1
      - maestro-2
      - maestro-3
    # nginx upstream roteia entre as 3 instâncias
```

### Resource Limits

```yaml
# docker-compose.prod.yml
services:
  maestro-sync-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🧪 Testing em Produção

```bash
# 1. Testar roteamento
curl -X POST https://maestro.example.com/mcp/route \
  -H "X-API-Key: seu-token" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "ETA com adução"}'

# 2. Testar sincronização
curl -X POST https://maestro.example.com/mcp/sync-prompt \
  -H "X-API-Key: seu-token" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Linha transmissão 500kV"}'

# 3. Testar status
curl https://maestro.example.com/mcp/sync-status \
  -H "X-API-Key: seu-token"
```

---

## 📞 Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker logs maestro-sync-prod

# Problemas comuns:
# - Port já em uso: sudo lsof -i :3001
# - Variáveis de ambiente faltando: docker-compose config
# - SSL certificate inválido: openssl x509 -in cert.pem -text
```

### Alto uso de memória

```bash
# Limpar cache
docker system prune -a

# Reduzir NODE_ENV
export NODE_ENV=production
docker-compose restart
```

### Sincronização lenta

```bash
# Aumentar worker processes
# Em nginx.conf: worker_processes auto

# Aumentar keepalive connections
# Em src/mcp-server.ts: connection pooling

# Escalona horizontalmente
# Adicione mais instâncias no docker-compose
```

---

## ✅ Production Checklist

- [ ] Docker e Docker Compose instalados
- [ ] SSL certificate configurado
- [ ] Variáveis de ambiente definidas
- [ ] Nginx configuration validada
- [ ] Health check respondendo
- [ ] API authentication funcionando
- [ ] Rate limiting ativo
- [ ] Logs centralizados
- [ ] Backup script rodando
- [ ] Monitoramento configurado
- [ ] Claude AI integrado
- [ ] Testes passando em produção
- [ ] Documentação atualizada
- [ ] Plano de contingência pronto

---

## 🎯 Status

**Production Ready:** ✅  
**Last Updated:** 2026-07-31  
**Maintained By:** Manta Associados  
**Support:** support@mantaassociados.com

---

**Parabéns!** Seu Maestro Sync Server está em produção! 🚀
