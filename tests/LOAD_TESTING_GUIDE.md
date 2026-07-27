# Load Testing Guide - Manta Maestro

## Overview

This guide covers load testing the Manta Maestro API using Locust, a Python-based load testing framework. Load testing helps validate:

- HPA scaling behavior under realistic load
- API response times and latency percentiles
- Error rates and reliability
- Resource utilization patterns
- Optimal cluster sizing

## Prerequisites

### Installation

```bash
# Install Locust
pip install locust>=2.0.0

# Verify installation
locust --version
```

### API Requirements

Ensure the Manta API exposes required endpoints:

```
GET  /health              # Health check
GET  /ready               # Readiness check
POST /api/v1/routing/query         # Route query to agent
POST /api/v1/search/semantic       # Semantic search
GET  /api/v1/agents/{agent}/status # Agent status
POST /api/v1/claims/analyze        # Claims analysis
GET  /api/v1/projects/{id}/metrics # Project metrics
```

## Load Test Script

The load test script is in `tests/load_test.py` and defines three user profiles:

### 1. MantaAPIUser (General Users)
Simulates typical Manta API usage with weighted tasks:

- **Route Query (weight: 10)** - 50% of traffic
  - Query an agent routing system
  - Most common operation
  
- **Semantic Search (weight: 5)** - 25% of traffic
  - Search documents with AI
  
- **Agent Status (weight: 3)** - 15% of traffic
  - Check agent availability
  
- **Claims Analysis (weight: 2)** - 10% of traffic
  - Create insurance claim analysis
  
- **Project Metrics (weight: 2)** - 10% of traffic
  - Retrieve project KPIs
  
- **Health Check (weight: 1)** - 5% of traffic
  - Low-priority endpoint check

### 2. FastRampUpUser (Load Spike)
Simulates sudden traffic spike with minimal wait:

- Rapid API calls (0.5-2s wait between requests)
- Heavy payload requests
- Typical during system failures/high demand

### 3. SemanticSearchUser (Heavy Compute)
Simulates compute-intensive search operations:

- Complex semantic searches (100 results)
- Document filtering
- Higher latency tolerance
- Less frequent but resource-intensive

## Running Load Tests

### Basic Load Test (Local Development)

```bash
# Start Locust UI (http://localhost:8089)
locust -f tests/load_test.py \
  --host http://localhost:8000

# Run headless (100 users over 5 minutes)
locust -f tests/load_test.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

### Scaling Test (Triggers HPA)

**Goal:** Demonstrate HPA scaling from 2 to 8+ replicas

```bash
# Terminal 1: Run load test (500 concurrent users)
locust -f tests/load_test.py \
  --host https://api.manta.example.com \
  --users 500 \
  --spawn-rate 25 \
  --run-time 15m \
  --headless \
  --csv=results/scaling_test
```

**Terminal 2 (parallel):** Monitor HPA scaling

```bash
# Watch HPA replicas increase in real-time
kubectl get hpa -n manta --watch

# Or use the helper script:
./scripts/setup-autoscaling.sh monitor
```

**Terminal 3 (parallel):** Monitor pod metrics

```bash
# Watch resource utilization
kubectl top pods -n manta -l app=manta-fastapi --containers -w
```

### Ramp-Up Test (Gradual Load Increase)

```bash
locust -f tests/load_test.py \
  --host https://api.manta.example.com \
  --users 1000 \
  --spawn-rate 50 \
  --run-time 30m \
  --headless
```

**Expected behavior:**
- Minutes 0-12: Spawn 50 users/sec → reach 1000 concurrent
- Minutes 12-25: Sustained load at 1000 users
- Minutes 25-30: System stabilizes, HPA scales down

### Spike Test (Sudden Traffic Increase)

```bash
# Use MantaAPIUser spawned very quickly
locust -f tests/load_test.py \
  --host https://api.manta.example.com \
  --users 800 \
  --spawn-rate 200 \
  --run-time 10m \
  --headless

# Watch HPA aggressively scale up
kubectl get hpa -n manta -w
```

### Stress Test (Maximum Load)

```bash
# Push to cluster limits
locust -f tests/load_test.py \
  --host https://api.manta.example.com \
  --users 2000 \
  --spawn-rate 100 \
  --run-time 20m \
  --headless
```

**Expected:**
- HPA scales to maxReplicas (10)
- Some requests may fail (expected at limits)
- Document maximum sustainable load

## Locust Web UI

For interactive testing with the Locust web interface:

```bash
# Start Locust UI
locust -f tests/load_test.py \
  --host https://api.manta.example.com

# Open browser to http://localhost:8089
```

**UI Workflow:**
1. Enter number of users to spawn
2. Enter spawn rate (users/sec)
3. Click "Start swarming"
4. Watch real-time statistics
5. Monitor response times, error rates
6. Download results as CSV

## Test Results Analysis

### CSV Output Format

Load test generates CSV results with columns:

```
Type,Name,# requests,# failures,Median (ms),Average (ms),Min (ms),Max (ms),
GET,/health,500,0,52,85,10,2150
POST,/api/v1/routing/query,5000,12,850,1200,100,8500
POST,/api/v1/search/semantic,2500,5,2100,2800,500,12000
```

### Metrics to Evaluate

**Response Times:**
- p50 (Median): < 500ms
- p95: < 3s
- p99: < 5s
- Max: < 15s

**Error Rate:**
- Total errors: < 1%
- 5xx errors: < 0.5%
- Timeout errors: 0%

**Throughput:**
- At 500 users: > 100 RPS
- At 1000 users: > 150 RPS
- Latency < 5s p95 at all load levels

**Scaling:**
- Scale-up time: 2-5 minutes (2→8 replicas)
- Replicas reached: 8+ (indicating load was applied)
- Scale-down time: 5-10 minutes after load stops

### Example Test Report

```
Load Test: 500 Concurrent Users (15 minutes)

Timing:
- Spawn Phase: 0-2 min (ramp to 500 users)
- Load Phase: 2-13 min (sustained 500 users)
- Cool-down: 13-15 min (traffic drops)

Results:
- Total Requests: 150,000
- Successful: 148,500 (99%)
- Failed: 1,500 (1%)
- Average RPS: ~170

Response Times:
- p50: 650ms
- p95: 2.8s
- p99: 4.5s
- max: 12.3s

Scaling:
- Initial replicas: 2
- Peak replicas: 8
- Scale-up duration: 3 min
- Final replicas: 3

Cost Impact:
- Peak cost: 8 replicas × $X/hour
- Baseline cost: 2 replicas × $X/hour
- Load test cost: ~$Y
```

## Customizing Load Tests

### Add New User Profile

Edit `tests/load_test.py`:

```python
class CustomUser(HttpUser):
    """Custom user profile for specific scenario."""
    
    wait_time = between(1, 3)
    
    @task(20)
    def my_task(self):
        self.client.get("/api/v1/endpoint")
```

### Adjust Task Weights

Modify task decorators to change traffic distribution:

```python
@task(10)  # 10x more frequent than weight:1 tasks
def popular_task(self):
    pass

@task(1)   # Low priority
def rare_task(self):
    pass
```

### Modify Request Payloads

Update payload in tasks:

```python
payload = {
    "query": "custom query",
    "param1": "value1",
    "param2": 123,
}
self.client.post("/api/endpoint", json=payload)
```

## Best Practices

### 1. Test Incrementally

```bash
# Start small
locust -f tests/load_test.py --users 50 --run-time 5m

# Increase gradually
locust -f tests/load_test.py --users 100 --run-time 5m
locust -f tests/load_test.py --users 200 --run-time 5m
locust -f tests/load_test.py --users 500 --run-time 10m
```

### 2. Monitor Cluster Health

Run in parallel terminals:

```bash
# Terminal 1: Load test
locust -f tests/load_test.py --users 500 --run-time 15m

# Terminal 2: HPA
kubectl get hpa -n manta -w

# Terminal 3: Metrics
kubectl top pods -n manta -w

# Terminal 4: Events
kubectl get events -n manta -w --sort-by=.metadata.creationTimestamp
```

### 3. Test Real Endpoints

Use actual API URLs:
- Development: `http://localhost:8000`
- Staging: `https://staging-api.manta.example.com`
- Production: Use separate load testing window

### 4. Document Results

Save results with timestamps:

```bash
mkdir -p results/$(date +%Y-%m-%d)
locust -f tests/load_test.py \
  --host https://api.manta.example.com \
  --users 500 \
  --run-time 15m \
  --csv=results/$(date +%Y-%m-%d)/scaling_500_users
```

### 5. Verify Error Responses

Add assertions to verify API responses:

```python
@task
def check_response(self):
    response = self.client.get("/api/v1/endpoint")
    if response.status_code != 200:
        self.client.events.request.fire(request_type="GET", name="/api", response_length=0)
```

## Troubleshooting Load Tests

### Connection Refused

**Error:** `connection refused`

**Solution:**
```bash
# Check API is running
curl http://localhost:8000/health

# Check firewall/network
telnet api.manta.example.com 443
```

### High Error Rate During Test

**Error:** > 5% request failures

**Diagnosis:**
```bash
# Check pod logs
kubectl logs deployment/manta-maestro-fastapi -n manta --tail=100

# Check API metrics
kubectl top pods -n manta

# Check HPA status
kubectl describe hpa manta-maestro-fastapi -n manta
```

**Solutions:**
- Increase resource requests/limits
- Raise HPA maxReplicas
- Reduce spawn rate
- Add more nodes to cluster

### Locust Not Spawning Users

**Error:** Users stuck at 0

**Diagnosis:**
```bash
# Check Locust logs
# Verify API connectivity
curl -v http://localhost:8000/health

# Test with fewer users
locust -f tests/load_test.py --users 10 --spawn-rate 1
```

### Metrics Not Collecting

**Error:** No response times recorded

**Diagnosis:**
```bash
# Verify Locust can reach API
locust -f tests/load_test.py --stop-timeout 0 -u 1 --run-time 10s

# Check API response
curl -X POST http://localhost:8000/api/v1/routing/query \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'
```

## Advanced Scenarios

### Multi-Stage Load Test

```bash
#!/bin/bash

# Stage 1: Warm up (100 users, 2 min)
echo "Stage 1: Warm-up..."
locust -f tests/load_test.py \
  --users 100 --spawn-rate 10 --run-time 2m --headless

# Stage 2: Scale test (500 users, 10 min)
echo "Stage 2: Scaling..."
locust -f tests/load_test.py \
  --users 500 --spawn-rate 25 --run-time 10m --headless

# Stage 3: Stress test (1000 users, 5 min)
echo "Stage 3: Stress..."
locust -f tests/load_test.py \
  --users 1000 --spawn-rate 50 --run-time 5m --headless

echo "Test complete!"
```

### Distributed Load Testing

```bash
# Master node
locust -f tests/load_test.py \
  --master \
  --host https://api.manta.example.com

# Worker 1 (separate terminal/machine)
locust -f tests/load_test.py \
  --worker \
  --master-host localhost

# Worker 2 (separate terminal/machine)
locust -f tests/load_test.py \
  --worker \
  --master-host localhost
```

## References

- [Locust Official Documentation](https://docs.locust.io/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [API Performance Best Practices](https://www.nginx.com/blog/inside-nginx-how-we-designed-for-performance-scale/)

---

**Last Updated:** 2026-07-27
**Maintainer:** Manta DevOps Team
