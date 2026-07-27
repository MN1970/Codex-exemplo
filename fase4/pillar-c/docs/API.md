# OpenTelemetry SDK API Reference

Complete guide for integrating OpenTelemetry instrumentation into applications.

## Python FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI
from instrumentation import (
    setup_otel_instrumentation,
    instrument_fastapi_app,
    get_tracer,
    get_meter,
)

# Initialize OTEL (call before app.run())
setup_otel_instrumentation(
    service_name="my-service",
    jaeger_host="jaeger.observability",
    jaeger_port=4317,
    prometheus_port=8000
)

# Create FastAPI app
app = FastAPI()

# Instrument it
instrument_fastapi_app(app)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Custom Span Creation

```python
from instrumentation import get_tracer
from opentelemetry import trace

@app.post("/process")
async def process_data(data: dict):
    tracer = get_tracer("process-handler")
    
    with tracer.start_as_current_span("process") as span:
        span.set_attributes({
            "data.size": len(data),
            "user_id": data.get("user_id"),
        })
        
        try:
            result = await expensive_operation(data)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
```

### Custom Metrics

```python
from metrics import get_metrics

@app.post("/merge")
async def merge_pr(pr: MergeRequest):
    metrics = get_metrics()
    
    # Counter: track merge successes
    metrics.git_merge_success_count.add(
        1,
        attributes={
            "branch": pr.branch,
            "author": pr.author,
        }
    )
    
    # Histogram: record latency
    metrics.git_pr_review_time.record(
        pr.review_time_seconds,
        attributes={"branch": pr.branch}
    )
    
    # Gauge: update current rate
    metrics.git_merge_success_rate.set(0.95)
    
    return {"status": "merged"}
```

### W3C TraceContext Propagation

```python
from fastapi import Header
from instrumentation import W3CTraceContextPropagator
import requests

@app.post("/chain-operation")
async def chain_operation(
    data: dict,
    traceparent: str = Header(None),
    tracestate: str = Header(None),
):
    # Extract incoming trace context
    trace_ctx = W3CTraceContextPropagator.extract_trace_context({
        "traceparent": traceparent,
        "tracestate": tracestate,
    })
    
    tracer = get_tracer("chain-operation")
    with tracer.start_as_current_span("operation") as span:
        # Call downstream service with trace context
        headers = W3CTraceContextPropagator.inject_trace_context({
            "trace_id": span.get_span_context().trace_id.to_bytes().hex(),
            "span_id": span.get_span_context().span_id.to_bytes().hex(),
            "trace_flags": "01",
        })
        
        response = requests.post(
            "http://next-service/process",
            json=data,
            headers=headers
        )
        
        return response.json()
```

### Database Instrumentation

```python
from instrumentation import instrument_sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")
instrument_sqlalchemy(engine)

@app.get("/data/{id}")
async def get_data(id: int):
    # Automatically traced
    result = db.query(Data).filter(Data.id == id).first()
    return result
```

---

## Go HTTP Server Integration

### Basic Setup

```go
package main

import (
    "context"
    "net/http"
    "os"
)

func main() {
    ctx := context.Background()
    
    // Initialize OTEL
    shutdown, err := InitializeOTel(ctx, "my-service")
    if err != nil {
        panic(err)
    }
    defer shutdown(ctx)
    
    // Initialize metrics
    metrics, err := InitializeMetrics(ctx)
    if err != nil {
        panic(err)
    }
    
    // Create router
    mux := http.NewServeMux()
    mux.HandleFunc("/health", healthCheck)
    mux.HandleFunc("/process", processData)
    
    // Start server
    http.ListenAndServe(":8080", mux)
}
```

### Custom Span Creation

```go
func processData(w http.ResponseWriter, r *http.Request) {
    ctx, span := tracer.Start(r.Context(), "process-data")
    defer span.End()
    
    // Set attributes
    span.SetAttributes(
        attribute.String("user_id", r.URL.Query().Get("user")),
        attribute.Int("batch_size", len(data)),
    )
    
    // Simulate work
    if err := process(ctx, data); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "processing failed")
        http.Error(w, "Internal error", http.StatusInternalServerError)
        return
    }
    
    span.SetStatus(codes.Ok, "")
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}
```

### Custom Metrics

```go
func mergeHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    
    // Counter
    metrics.GitMergeSuccessCount.Add(ctx, 1)
    
    // Histogram
    startTime := time.Now()
    // ... do work ...
    metrics.GitPRReviewTime.Record(
        ctx,
        time.Since(startTime).Seconds(),
    )
    
    // Gauge
    metrics.GitMergeSuccessRate.Record(ctx, 0.95)
}
```

### W3C TraceContext Propagation

```go
import "go.opentelemetry.io/otel/trace"

func chainedOperation(w http.ResponseWriter, r *http.Request) {
    ctx, span := tracer.Start(r.Context(), "chained-op")
    defer span.End()
    
    // Extract incoming trace context
    incomingTrace := ExtractTraceContext(r)
    if incomingTrace != nil {
        span.SetAttributes(
            attribute.String("trace.parent_id", incomingTrace.SpanID),
        )
    }
    
    // Create outgoing request
    req, _ := http.NewRequestWithContext(ctx, "POST", 
        "http://next-service/process", 
        bytes.NewReader(payload))
    
    // Inject trace context
    InjectTraceContext(req, &W3CTraceContext{
        TraceID:    span.SpanContext().TraceID().String(),
        SpanID:     span.SpanContext().SpanID().String(),
        TraceFlags: "01",
    })
    
    // Make request
    resp, _ := http.DefaultClient.Do(req)
    defer resp.Body.Close()
}
```

---

## Environment Variables

```bash
# Jaeger Configuration
export JAEGER_HOST=jaeger.observability.svc.cluster.local
export JAEGER_PORT=4317
export OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc

# Prometheus Configuration
export PROMETHEUS_PORT=8000
export PROMETHEUS_URL=http://prometheus:9090

# Application Configuration
export SERVICE_NAME=my-service
export ENVIRONMENT=production
export VERSION=1.0.0

# Sampling Configuration
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling
```

---

## Metric Recording Examples

### Counters (Always Increasing)

```python
# Python
metrics.git_merge_success_count.add(1, attributes={"branch": "main"})

# Go
metrics.GitMergeSuccessCount.Add(ctx, 1)
```

### Gauges (Can Go Up/Down)

```python
# Python
metrics.git_merge_success_rate.set(0.95)
metrics.cpu_usage_percent.set(45.2)

# Go
metrics.GitMergeSuccessRate.Record(ctx, 0.95)
metrics.CPUUsagePercent.Record(ctx, 45.2)
```

### Histograms (Distribution)

```python
# Python
metrics.git_pr_review_time.record(3600.5, attributes={"branch": "main"})

# Go
metrics.GitPRReviewTime.Record(ctx, 3600.5)
```

---

## Error Handling & Exceptions

```python
from opentelemetry import trace

try:
    result = dangerous_operation()
except Exception as e:
    # Record exception in span
    tracer.get_current_span().record_exception(e)
    # Set error status
    tracer.get_current_span().set_status(
        trace.Status(trace.StatusCode.ERROR, str(e))
    )
    raise
```

---

## Instrumenting External Libraries

### Requests Library

```python
from instrumentation import instrument_requests

instrument_requests()

# Now all requests are automatically traced
import requests
response = requests.get("http://api.example.com/data")
```

### SQLAlchemy

```python
from instrumentation import instrument_sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("postgresql://...")
instrument_sqlalchemy(engine)

# All SQL queries are now traced
```

---

## Performance Considerations

### Sampling
```python
# Reduce overhead: sample 10% of traces
setup_otel_instrumentation(
    service_name="my-service",
    jaeger_host="jaeger",
)

# Configure via environment
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # 10%
```

### Batch Processing
```python
# Python automatically batches spans before export
# Default: 512 spans per batch, 5 second timeout

# Go: default batching in Prometheus reader
# Default: 60 second scrape interval
```

### Resource Limits
```python
# Set appropriate limits in container
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

---

## Common Patterns

### Distributed Trace Example

```
User Request
  ↓
Service A (receives request)
  ├─ Create span: trace_id=abc123
  ├─ Call Service B (inject traceparent header)
  └─ Log: trace_id=abc123
  
  ↓ HTTP with traceparent=00-abc123-xyz789-01
  
Service B
  ├─ Extract traceparent from header
  ├─ Create child span: parent_span_id=xyz789
  ├─ Call Service C (inject updated headers)
  └─ Log: trace_id=abc123, parent_span_id=xyz789
  
  ↓ HTTP with updated traceparent
  
Service C
  ├─ Extract traceparent
  ├─ Create grandchild span
  └─ Execute business logic
  
All three services' spans appear in single trace in Jaeger!
```

### Multi-Service Example

```python
# Service A (API Gateway)
@app.post("/order")
async def create_order(order: Order):
    metrics.git_merge_success_count.add(1)
    
    # Call Service B
    response = await http_client.post(
        "http://service-b/validate",
        headers=inject_trace_context(),
        json=order.dict()
    )
    
    return response.json()

# Service B (Validation Service)
@app.post("/validate")
async def validate(order: dict, traceparent: str = Header(None)):
    trace_ctx = extract_trace_context({"traceparent": traceparent})
    
    # Now in same trace as Service A!
    metrics.ml_predictions_total.add(1)
    
    # Call Service C
    result = await model.predict(order)
    return {"valid": result}

# Service C (ML Inference Service)
@app.post("/infer")
async def infer(data: dict, traceparent: str = Header(None)):
    # Extract trace context
    # Now all three services in same trace!
    inference_time = measure_inference(data)
    metrics.ml_inference_latency.record(inference_time)
    return {"prediction": 0.95}
```

---

## Testing

### Unit Testing with OTEL

```python
import pytest
from instrumentation import setup_otel_instrumentation

@pytest.fixture
def tracer():
    setup_otel_instrumentation("test-service")
    yield get_tracer("test")

def test_merge(tracer):
    with tracer.start_as_current_span("test_merge") as span:
        result = merge_pr({"pr_id": "123", "branch": "main"})
        assert result.status == "merged"
```

### Load Testing

```bash
# Python
pip install locust

# locustfile.py
from locust import HttpUser, task

class ApiUser(HttpUser):
    @task
    def merge_pr(self):
        self.client.post("/merge", json={
            "pr_id": "123",
            "branch": "main"
        })

# Run
locust -f locustfile.py --host=http://localhost:8080
```

---

## Troubleshooting

### Spans Not Appearing in Jaeger

```bash
# 1. Verify JAEGER_HOST is correct
echo $JAEGER_HOST

# 2. Test connectivity
curl -i http://$JAEGER_HOST:4317

# 3. Check application logs for errors
grep -i "otel\|jaeger\|exporter" app.log

# 4. Verify service_name is set
export SERVICE_NAME=my-service
```

### Metrics Not in Prometheus

```bash
# 1. Verify metrics endpoint
curl http://localhost:8000/metrics | grep manta_

# 2. Check Prometheus scrape config
kubectl get configmap -n observability prometheus-config -o yaml | grep -A 10 "manta"

# 3. Verify targets scraping
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="manta")'
```

---

## References

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry Go Documentation](https://opentelemetry.io/docs/instrumentation/go/)
- [W3C TraceContext Specification](https://www.w3.org/TR/trace-context/)
- [Prometheus Client Libraries](https://prometheus.io/docs/instrumenting/clientlibs/)

---

**Last Updated:** 2026-01-15  
**Version:** 1.0.0
