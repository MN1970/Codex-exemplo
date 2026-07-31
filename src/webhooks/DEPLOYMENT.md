# Cowork Webhook Handler - Deployment Guide

## Pre-Deployment Checklist

### Security
- [ ] Generate strong webhook secret: `openssl rand -hex 32`
- [ ] Store secret in secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Never commit secret to version control
- [ ] Use HTTPS only for webhook endpoints
- [ ] Implement rate limiting on webhook endpoint
- [ ] Set up IP whitelist if available from Cowork
- [ ] Enable WAF rules for webhook endpoint

### Configuration
- [ ] Set `maxRetries` appropriate for your use case (3-5 recommended)
- [ ] Configure `initialBackoffMs` and `maxBackoffMs` based on expected load
- [ ] Set up audit log persistence (file or database)
- [ ] Configure logger level appropriately (info for production)
- [ ] Set up structured logging for log aggregation

### Monitoring
- [ ] Set up monitoring for `/health/webhooks` endpoint
- [ ] Configure alerting for webhook failures
- [ ] Set up metrics collection (queue size, processing time)
- [ ] Monitor audit log growth
- [ ] Set up error tracking (Sentry, DataDog, etc.)

### Testing
- [ ] Run full test suite: `npm test`
- [ ] Load test with expected webhook volume
- [ ] Test signature validation with production secret
- [ ] Test retry logic with failure scenarios
- [ ] Test concurrent webhook processing
- [ ] Verify audit log functionality

### Infrastructure
- [ ] Use Node.js LTS version (18+)
- [ ] Configure process manager (PM2, systemd, etc.)
- [ ] Set up graceful shutdown handling
- [ ] Configure rolling deployments
- [ ] Set up database backups for audit logs
- [ ] Configure auto-scaling if using containers

## Deployment Options

### Docker

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist

EXPOSE 3000

CMD ["node", "dist/webhooks/example-server.js"]
```

Build and run:
```bash
docker build -t cowork-webhooks:latest .
docker run -e WEBHOOK_SECRET="..." -p 3000:3000 cowork-webhooks:latest
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cowork-webhooks
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cowork-webhooks
  template:
    metadata:
      labels:
        app: cowork-webhooks
    spec:
      containers:
      - name: webhooks
        image: cowork-webhooks:latest
        ports:
        - containerPort: 3000
        env:
        - name: WEBHOOK_SECRET
          valueFrom:
            secretKeyRef:
              name: cowork-webhook-secret
              key: secret
        - name: LOG_LEVEL
          value: "info"
        livenessProbe:
          httpGet:
            path: /health/webhooks
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/webhooks
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: cowork-webhooks
spec:
  selector:
    app: cowork-webhooks
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

Deploy:
```bash
kubectl create secret generic cowork-webhook-secret --from-literal=secret="$(openssl rand -hex 32)"
kubectl apply -f webhooks-deployment.yaml
```

### PM2

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'cowork-webhooks',
    script: './dist/webhooks/example-server.js',
    instances: 4,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
      LOG_LEVEL: 'info'
    },
    max_memory_restart: '512M',
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

Start:
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Systemd

```ini
# /etc/systemd/system/cowork-webhooks.service
[Unit]
Description=Cowork Webhook Handler
After=network.target

[Service]
Type=simple
User=cowork
WorkingDirectory=/opt/cowork-webhooks
Environment="NODE_ENV=production"
Environment="PORT=3000"
Environment="WEBHOOK_SECRET=..."
ExecStart=/usr/bin/node /opt/cowork-webhooks/dist/webhooks/example-server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cowork-webhooks
sudo systemctl start cowork-webhooks
sudo systemctl status cowork-webhooks
```

## Post-Deployment

### Verification

1. Check server is running:
```bash
curl http://localhost:3000/health/webhooks
```

2. Send test webhook:
```bash
WEBHOOK_SECRET="your-secret" bash scripts/test-webhook.sh
```

3. Check audit log:
```bash
curl http://localhost:3000/webhooks/audit-log?limit=10
```

### Monitoring Setup

#### Prometheus Metrics

```typescript
import express from 'express';
import prometheus from 'prom-client';

const app = express();
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

app.get('/metrics', async (_req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(await prometheus.register.metrics());
});
```

#### Grafana Dashboard

Create dashboard with panels:
- Queue size over time
- Processing rate
- Error rate
- P95 processing time
- Handler success/failure counts

#### CloudWatch Alarms (AWS)

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cowork-webhook-queue-size \
  --metric-name QueueSize \
  --namespace CoworkWebhooks \
  --statistic Average \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

### Log Aggregation

#### ELK Stack (Elasticsearch, Logstash, Kibana)

```json
{
  "filter": {
    "grok": {
      "match": {
        "message": "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}"
      }
    }
  },
  "output": {
    "elasticsearch": {
      "hosts": ["elasticsearch:9200"],
      "index": "cowork-webhooks-%{+YYYY.MM.dd}"
    }
  }
}
```

#### CloudWatch Logs

```typescript
const logger = pino(
  pino.transport({
    target: 'pino-aws-cloudwatch-transport',
    options: {
      logGroupName: '/aws/lambda/cowork-webhooks',
      logStreamName: 'production'
    }
  })
);
```

## Scaling Considerations

### Horizontal Scaling

- Keep webhook handler stateless (all state in queue/audit log)
- Use load balancer for multiple instances
- Shared audit log database (RDS, DynamoDB)
- Shared webhook secret configuration

### Performance Tuning

1. **Queue Processing**: Adjust interval based on latency requirements
2. **Worker Count**: Can increase with PM2 or container replicas
3. **Backoff Strategy**: Tune for your error rate and expected retry duration
4. **Audit Log**: Consider database persistence for high volume

### Database Persistence

For audit logs with persistent storage:

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

// In CoworkWebhookHandler
private async writeAuditLogFile(entry: AuditLogEntry): Promise<void> {
  const query = `
    INSERT INTO webhook_audit_logs 
    (timestamp, delivery_id, event, status, error, duration, retry_count, ip_address)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
  `;

  await pool.query(query, [
    entry.timestamp,
    entry.deliveryId,
    entry.event,
    entry.status,
    entry.error,
    entry.duration,
    entry.retryCount,
    entry.ipAddress
  ]);
}
```

## Troubleshooting

### Queue Backlog

Check status:
```bash
curl http://localhost:3000/webhooks/status | jq '.queueSize'
```

If queue is growing:
1. Check handler errors in audit log
2. Increase number of worker instances
3. Investigate handler implementation for performance issues

### High Failure Rate

```bash
curl http://localhost:3000/webhooks/audit-log?limit=50 | \
  jq '.entries[] | select(.status == "failed")'
```

Common causes:
- Handler timeout (increase timeout or optimize handler)
- External service unavailable (implement fallback)
- Signature validation failure (verify secret is correct)

### Memory Leaks

Monitor memory usage:
```bash
node --max_old_space_size=2048 dist/webhooks/example-server.js
```

If memory grows:
- Check for unclosed database connections in handlers
- Reduce audit log retention (limit in-memory entries)
- Profile with `--inspect` flag

## Rollback Plan

1. Keep previous version running on separate port
2. Update load balancer to route to old version
3. Investigate issue in new version
4. Fix and redeploy after thorough testing

```bash
# Keep previous version
npm run build:previous
PORT=3001 npm start

# Update load balancer config
# Then after fix:
npm run build
PORT=3000 npm start
```

## Compliance & Auditing

- Store audit logs for minimum 90 days
- Implement log retention policy
- Enable TLS 1.2+ for all webhooks
- Document security controls
- Conduct security audit before production
- Regular penetration testing

## Support & Maintenance

- Monitor logs daily
- Review metrics weekly
- Update dependencies monthly
- Security patches: immediately
- Full backups: daily
- Test disaster recovery: quarterly
