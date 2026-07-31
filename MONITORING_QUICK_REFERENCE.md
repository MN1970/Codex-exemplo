# Monitoring & Observability - Quick Reference

**TL;DR** - Essential APIs and patterns for common tasks.

---

## 🚀 Get Started in 2 Minutes

```typescript
import { ObservabilityManager } from "./src/services/monitoring";

// 1. Initialize
const obs = new ObservabilityManager("my-service", "production");

// 2. Record metric
obs.metrics.recordHistogram("latency_ms", 245);

// 3. Get status
console.log(obs.getSystemStatus());

// 4. Shutdown
obs.shutdown();
```

---

## 📊 Metrics Quick Reference

### Counter (Incremental)
```typescript
// Increment by 1
obs.metrics.incrementCounter("requests_total");

// Increment by custom amount
obs.metrics.incrementCounter("requests_total", 5);

// With labels
obs.metrics.incrementCounter("requests_total", 1, {
  method: "GET",
  status: "200"
});
```

### Gauge (Absolute Value)
```typescript
// Set current value
obs.metrics.setGauge("queue_depth", 45);

// With labels
obs.metrics.setGauge("memory_usage_mb", 512, {
  service: "sync"
});
```

### Histogram (Distribution)
```typescript
// Record value
obs.metrics.recordHistogram("latency_ms", 245);

// With labels
obs.metrics.recordHistogram("latency_ms", 245, {
  endpoint: "/api/sync"
});

// Get aggregations
const agg = obs.metrics.aggregateMetrics("latency_ms");
console.log(agg.p95); // 95th percentile
```

---

## 🚨 Alerts Quick Reference

### Register Alert Rule
```typescript
obs.alerts.registerRule({
  id: "high-latency",
  name: "High Latency Alert",
  metricName: "sync_latency_ms",
  operator: ">",
  threshold: 5000,
  severity: AlertSeverity.WARNING,
  enabled: true,
  slackWebhook: process.env.SLACK_WEBHOOK_URL,
});
```

### Evaluate Rules
```typescript
// Check if value triggers alerts
const alerts = obs.alerts.evaluateRules("sync_latency_ms", 7000);

if (alerts.length > 0) {
  console.log("Alert triggered:", alerts[0].message);
}
```

### Manage Alerts
```typescript
// Get active (unresolved) alerts
const active = obs.alerts.getActiveAlerts();

// Resolve an alert
obs.alerts.resolveAlert(alert.id);

// Get history
const history = obs.alerts.getAlertHistory(100);

// Clean up old resolved alerts
obs.alerts.pruneAlerts(86400000); // 24h
```

### Operators
```typescript
operator: ">"   // Greater than
operator: "<"   // Less than
operator: ">="  // Greater or equal
operator: "<="  // Less or equal
operator: "=="  // Equal
operator: "!="  // Not equal
```

### Severities
```typescript
AlertSeverity.INFO       // Informational
AlertSeverity.WARNING    // Warning
AlertSeverity.ERROR      // Error
AlertSeverity.CRITICAL   // Critical
```

---

## 🔍 Tracing Quick Reference

### Start Trace
```typescript
const traceContext = obs.tracing.startTrace();
// { traceId: "...", spanId: "...", flags: 1 }
```

### Create Span
```typescript
const span = obs.tracing.createSpan(
  traceContext,
  "operation_name",
  { key: "value" } // metadata
);
```

### End Span
```typescript
obs.tracing.endSpan(span, {
  status: "success",
  records: 150
});
```

### Export Trace (OpenTelemetry format)
```typescript
const trace = obs.tracing.exportTrace(traceContext.traceId);
console.log(trace);
```

---

## 📝 Logging Quick Reference

```typescript
// Info
obs.logger.info({ userId: "123" }, "User logged in");

// Warning
obs.logger.warn({ code: "RATE_LIMIT" }, "Rate limit warning");

// Error
obs.logger.error({ error: err.message }, "Operation failed");

// Debug (development only)
obs.logger.debug({ payload }, "Processing data");
```

---

## 📈 Status & Export Quick Reference

### Get System Status
```typescript
const status = obs.getSystemStatus();
// {
//   timestamp: "...",
//   health: {
//     metrics: { latency, successRate, queueDepth, errorRate },
//     alerts: { active: 0, list: [...] }
//   },
//   dashboard: { /* all metrics */ }
// }
```

### Get Key Metrics
```typescript
const metrics = obs.metrics.getKeyMetrics();
// {
//   latency: { mean, p95, p99 },
//   successRate: 99.5,
//   queueDepth: 45,
//   errorRate: 0.5
// }
```

### Get Prometheus Metrics
```typescript
const prometheus = obs.getPrometheusMetrics();
// # TYPE sync_latency_ms histogram
// sync_latency_ms 245 1690000000000
```

---

## 🔧 Express Integration Quick Reference

### Apply Middleware
```typescript
import { createObservabilityMiddleware } from "./monitoring";

app.use(createObservabilityMiddleware(obs));
// All requests now have:
// - X-Trace-ID header
// - X-Span-ID header
// - Automatic latency recording
// - Success/error tracking
```

### Expose Metrics Endpoint
```typescript
app.get("/metrics", (req, res) => {
  res.type("text/plain");
  res.send(obs.getPrometheusMetrics());
});
```

### Health Check
```typescript
app.get("/health", (req, res) => {
  const status = obs.getSystemStatus();
  const isHealthy = status.health.alerts.active === 0;
  res.status(isHealthy ? 200 : 503).json({ ok: isHealthy });
});
```

---

## ⚙️ Configuration Quick Reference

### Production Config
```typescript
import { productionConfig, applyConfig } from "./examples/monitoring-config";

const obs = new ObservabilityManager("my-service", "production");
applyConfig(obs, productionConfig);
```

### Staging Config
```typescript
import { stagingConfig, applyConfig } from "./examples/monitoring-config";

const obs = new ObservabilityManager("my-service", "staging");
applyConfig(obs, stagingConfig);
```

### Get Config by Environment
```typescript
import { getConfig } from "./examples/monitoring-config";

const config = getConfig(process.env.NODE_ENV);
applyConfig(obs, config);
```

---

## 🧹 Maintenance Quick Reference

### Clean Up Old Data
```typescript
// Remove metrics > 1 hour
obs.metrics.pruneMetrics(3600000);

// Remove resolved alerts > 24 hours
obs.alerts.pruneAlerts(86400000);

// Remove traces > 1 hour
obs.tracing.pruneTraces(3600000);
```

### Reset All Metrics (development only)
```typescript
obs.metrics.reset();
```

### Shutdown Cleanly
```typescript
obs.shutdown();
// Clears cleanup interval
// Graceful teardown
```

---

## 🎯 Common Patterns

### Pattern 1: Monitor Function Execution
```typescript
async function syncData() {
  const startTime = Date.now();
  
  try {
    // ... do work ...
    
    const duration = Date.now() - startTime;
    obs.metrics.recordHistogram("sync_duration_ms", duration);
    obs.metrics.incrementCounter("sync_success");
  } catch (error) {
    obs.metrics.incrementCounter("sync_error");
    obs.logger.error({ error }, "Sync failed");
    throw error;
  }
}
```

### Pattern 2: Monitor API Endpoint
```typescript
app.get("/api/users", async (req, res) => {
  const startTime = Date.now();
  
  try {
    const users = await fetchUsers();
    
    obs.metrics.recordHistogram(
      "api_latency_ms",
      Date.now() - startTime,
      { endpoint: "/api/users" }
    );
    
    res.json(users);
  } catch (error) {
    obs.metrics.incrementCounter("api_error", 1, {
      endpoint: "/api/users"
    });
    res.status(500).json({ error: error.message });
  }
});
```

### Pattern 3: Queue Monitoring
```typescript
async function enqueueJob(job) {
  queue.push(job);
  
  // Update queue depth metric
  obs.metrics.setGauge("queue_depth", queue.length);
  
  // Check if queue is too deep
  obs.alerts.evaluateRules("queue_depth", queue.length);
}
```

### Pattern 4: Distributed Trace
```typescript
async function processOrder(orderId) {
  const trace = obs.tracing.startTrace();
  
  try {
    const span1 = obs.tracing.createSpan(trace, "fetch_order", { orderId });
    const order = await fetchOrder(orderId);
    obs.tracing.endSpan(span1);
    
    const span2 = obs.tracing.createSpan(trace, "validate_order");
    await validateOrder(order);
    obs.tracing.endSpan(span2);
    
    const span3 = obs.tracing.createSpan(trace, "process_payment");
    await processPayment(order);
    obs.tracing.endSpan(span3);
    
    return { success: true, traceId: trace.traceId };
  } catch (error) {
    obs.logger.error({ error, traceId: trace.traceId }, "Order processing failed");
    throw error;
  }
}
```

---

## 🚨 Alert Setup Examples

### High Latency
```typescript
{
  name: "High Latency",
  metricName: "sync_latency_ms",
  operator: ">",
  threshold: 5000,
  severity: AlertSeverity.WARNING,
}
```

### Error Rate
```typescript
{
  name: "High Error Rate",
  metricName: "error_rate_percent",
  operator: ">",
  threshold: 5,
  severity: AlertSeverity.ERROR,
}
```

### Resource Exhaustion
```typescript
{
  name: "DB Pool Exhausted",
  metricName: "db_pool_connections",
  operator: "==",
  threshold: 100,
  severity: AlertSeverity.CRITICAL,
}
```

### Queue Depth
```typescript
{
  name: "Queue Backing Up",
  metricName: "queue_depth",
  operator: ">",
  threshold: 100,
  severity: AlertSeverity.WARNING,
}
```

---

## 📊 Grafana Queries Cheat Sheet

```promql
# Latency percentiles
histogram_quantile(0.95, rate(sync_latency_ms[5m]))

# Error rate percentage
(rate(requests_error[5m]) / rate(requests_total[5m])) * 100

# Throughput (requests per second)
rate(requests_total[1m])

# Average queue depth
avg_over_time(queue_depth[5m])

# CPU usage trend
avg_over_time(cpu_usage_percent[5m])
```

---

## 🔄 Environment Variables

```bash
# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_WEBHOOK_STAGING=https://hooks.slack.com/services/YOUR/STAGING/WEBHOOK
SLACK_WEBHOOK_PROD=https://hooks.slack.com/services/YOUR/PROD/WEBHOOK

# Logging
NODE_ENV=production|staging|development
LOG_LEVEL=debug|info|warn|error

# Server
PORT=3000
METRICS_ENDPOINT=/metrics
HEALTH_ENDPOINT=/health
```

---

## ⏱️ Default Thresholds (Production)

| Metric | Warning | Critical |
|--------|---------|----------|
| Latency (P95) | > 3000ms | > 30000ms |
| Error Rate | > 5% | > 10% |
| Queue Depth | > 100 | > 500 |
| CPU Usage | > 75% | > 90% |
| DB Connections | > 90 | == 100 |

---

## 🧪 Testing Alerts

### Trigger Error Rate Alert
```bash
curl -X POST http://localhost:3000/api/test/error-spike?count=20
```

### Trigger Latency Alert
```bash
curl -X POST http://localhost:3000/api/test/high-latency?latency=40000
```

### Check Active Alerts
```bash
curl http://localhost:3000/alerts/active
```

---

## 📚 Resources

- **Full Documentation**: `src/services/MONITORING_README.md`
- **Examples**: `src/services/examples/`
- **Tests**: `src/services/__tests__/monitoring.test.ts`
- **Config**: `src/services/examples/monitoring-config.ts`

---

**Version**: 1.0.0 | **Quick Ref** | **Ready for Production**
