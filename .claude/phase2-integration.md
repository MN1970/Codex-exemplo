# Phase 2: Integration Architecture

**Scope:** System initialization, request flow, monitoring, deployment  
**Dependencies:** phase2-router.md, phase2-routing-rules.md  
**Status:** Ready for implementation

---

## 1. SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                │
│                    POST /api/maestro                                 │
│              { prompt, context, sessionId }                          │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │   MaestroRouter (Manta 00)│ ← Phase 2: Router
         │  • dispatch(prompt)       │
         │  • routeToSegment()       │
         │  • detectComplexity()     │
         │  • selectPattern()        │
         └────────────┬──────────────┘
                      │
                      ▼ RoutingDecision {agents, models, priority, pattern}
         ┌────────────────────────────────┐
         │  AdaptiveModelSelector        │ ← Phase 2: Model Selection
         │  • selectModels()             │
         │  • classifyVolumeBand()       │
         │  • apply decision matrix      │
         └────────────┬───────────────────┘
                      │
                      ▼ {primaryModel, secondaryModel}
         ┌────────────────────────────────┐
         │  QPrioDispatcher               │ ← Phase 2: Queue Dispatcher
         │  • enqueue(task, routing)      │
         │  • start() [main loop]         │
         │  • dispatch(task)              │
         │  • routeToPattern()            │
         └────────────┬───────────────────┘
                      │
        ┌─────────────┼──────────────┬─────────────┐
        ▼             ▼              ▼             ▼
    ┌──────┐   ┌─────────┐   ┌────────────┐  ┌─────────┐
    │Direct│   │Pipeline │   │ Parallel   │  │ Fan-Out │
    │1 agent│  │3-4 agents│  │8 agents    │  │16+ agents│
    │<30s  │   │5-10 min  │   │10-20 min   │  │30min-2h │
    └──┬───┘   └────┬────┘   └─────┬──────┘  └────┬────┘
       │            │              │             │
       │            ▼              ▼             ▼
       │      ┌─────────────────────────┐  (async, no barrier)
       │      │ Agent Execution Pool    │
       │      │                         │
       │      │ • Manta 00-07, 13-16    │
       │      │ • agente-infraestrutura │
       │      │ • agente-saneamento     │
       │      │ • agente-energia        │
       │      │ • agente-portos         │
       │      │ • agente-aeroportos     │
       │      │ • agente-barragens      │
       │      └────────┬────────────────┘
       │               │
       └───────────────┼───────────────────┐
                       ▼                   ▼
            ┌──────────────────────┐  ┌────────────────┐
            │  RAG Learning Log    │  │ User Response  │
            │                      │  │ {taskId, status│
            │ Supabase insert:     │  │  agents, ETA}  │
            │ • token_count        │  └────────────────┘
            │ • complexity         │
            │ • segment            │
            │ • wall_clock         │
            │ • cost               │
            └──────────────────────┘
```

---

## 2. REQUEST FLOW (DETAILED)

### 2.1 Complete User Journey

```
[User]
  │
  ├─ "Análise de edital de saneamento para AySA"
  │
  └─→ POST /api/maestro
      │
      ├─ STEP 1: Router Analysis (10ms)
      │  ├─ tokenCount = 1200
      │  ├─ keywords = [análise, edital, saneamento, AySA]
      │  ├─ complexity = alta (edital → alta)
      │  ├─ segment = S8 (saneamento|AySA) → 0.95 confidence
      │  ├─ phase = EVTE (edital → processo competitivo)
      │  ├─ priority = Q16 (normal)
      │  └─ pattern = pipeline (médio volume)
      │
      ├─ STEP 2: Model Selection (5ms)
      │  ├─ band = médio (500–2000 tokens)
      │  ├─ complexity = alta
      │  ├─ matrix[médio][alta] = Sonnet + Sonnet
      │  └─ models = [sonnet, sonnet]
      │
      ├─ STEP 3: Agent Roster (5ms)
      │  ├─ vertical: agente-saneamento
      │  ├─ phase: Manta 02 (legal), Manta 15 (advisory)
      │  ├─ complexity: Manta 05 (budget)
      │  └─ roster = [agente-saneamento, Manta 02, Manta 15, Manta 05]
      │
      ├─ STEP 4: Enqueue (2ms)
      │  └─ QPrio.enqueue(task, routing) → Q16 queue
      │
      └─ STEP 5: Return to User (5ms)
         └─ HTTP 200 {
              taskId: "task_a1b2c3",
              status: "QUEUED",
              priority: "Q16",
              agents: ["agente-saneamento", "Manta 02", "Manta 15", "Manta 05"],
              models: ["sonnet", "sonnet"],
              pattern: "pipeline",
              estimatedWaitMs: 45000,
              estimatedDurationMs: 600000
            }

TOTAL REQUEST TIME: ~25ms

---

[Queue Processing]
  │
  ├─ Wait: 45–60 sec (Q16 queue depth)
  │
  └─→ EXECUTION (via pipeline pattern)
     │
     ├─ Stage 1: Analysis (60 sec)
     │  └─ agente-saneamento
     │     Input: "Análise de edital de saneamento para AySA"
     │     Model: Sonnet
     │     Output: Technical analysis + findings
     │
     ├─ Stage 2: Synthesis (parallel, 120 sec)
     │  ├─ Manta 02 (legal)
     │  │  Input: Stage 1 output
     │  │  Model: Sonnet
     │  │  Output: Legal risks + contract terms
     │  │
     │  └─ Manta 15 (advisory)
     │     Input: Stage 1 output
     │     Model: Sonnet
     │     Output: Market positioning + recommendations
     │
     ├─ Stage 3: Assembly (30 sec)
     │  └─ Manta 05 (budget)
     │     Input: [Stage 2 outputs]
     │     Model: Sonnet
     │     Output: Integrated proposal + budget estimate
     │
     └─ COMPLETE (240 sec total = 4 min)

[Final Result]
  │
  └─→ Webhook to /api/maestro/callback/{taskId}
     └─ {
          taskId: "task_a1b2c3",
          status: "COMPLETE",
          result: { ... },
          wallClockMs: 240000,
          costCents: 2500
        }
```

---

## 3. INITIALIZATION CODE

```javascript
// index.js or maestro-server.js

const express = require('express');
const { MaestroRouter } = require('./phase2-router');
const { AdaptiveModelSelector } = require('./phase2-router');
const { QPrioDispatcher } = require('./phase2-router');
const Supabase = require('@supabase/supabase-js');

// ─────────────────────────────────────────────────────────────────
// 1. INITIALIZE SUPABASE (RAG Learning Log)
// ─────────────────────────────────────────────────────────────────

const supabase = Supabase.createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// ─────────────────────────────────────────────────────────────────
// 2. INITIALIZE AGENT POOL
// ─────────────────────────────────────────────────────────────────

const agentPool = {
  // Horizontal agents
  'Manta 00': new Agent('maestro', 'claude-sonnet'),
  'Manta 01': new Agent('claims', 'claude-opus'),
  'Manta 02': new Agent('contratual', 'claude-sonnet'),
  'Manta 04': new Agent('imobiliario', 'claude-sonnet'),
  'Manta 05': new Agent('orcamento', 'claude-sonnet'),
  'Manta 06': new Agent('modelagem', 'claude-opus'),
  'Manta 07': new Agent('cronograma', 'claude-sonnet'),
  'Manta 13': new Agent('bd', 'claude-sonnet'),
  'Manta 14': new Agent('apresentacoes', 'claude-sonnet'),
  'Manta 15': new Agent('advisory', 'claude-opus'),
  'Manta 16': new Agent('arquiteto-ia', 'claude-opus'),
  
  // Vertical segment agents
  'agente-infraestrutura-S1': new Agent('infraestrutura-S1', 'claude-sonnet'),
  'agente-infraestrutura-S2': new Agent('infraestrutura-S2', 'claude-sonnet'),
  'agente-infraestrutura-S3': new Agent('infraestrutura-S3', 'claude-sonnet'),
  'agente-infraestrutura-S4': new Agent('infraestrutura-S4', 'claude-sonnet'),
  'agente-saneamento': new Agent('saneamento', 'claude-sonnet'),
  'agente-energia': new Agent('energia', 'claude-sonnet'),
  'agente-portos': new Agent('portos', 'claude-sonnet'),
  'agente-aeroportos': new Agent('aeroportos', 'claude-sonnet'),
  'agente-barragens': new Agent('barragens', 'claude-sonnet')
};

// ─────────────────────────────────────────────────────────────────
// 3. INITIALIZE MAESTRO COMPONENTS
// ─────────────────────────────────────────────────────────────────

const router = new MaestroRouter();
const selector = new AdaptiveModelSelector();
const dispatcher = new QPrioDispatcher(agentPool);

// Start main dispatcher loop
dispatcher.start();

console.log('✅ Maestro initialized');
console.log(`   Agents: ${Object.keys(agentPool).length}`);
console.log(`   Queues: Q0 (critical), Q16 (normal), Q∞ (background)`);

// ─────────────────────────────────────────────────────────────────
// 4. HTTP SERVER SETUP
// ─────────────────────────────────────────────────────────────────

const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────
// ENDPOINT 1: POST /api/maestro — Submit Task
// ─────────────────────────────────────────────────────────────────

app.post('/api/maestro', async (req, res) => {
  const { prompt, context = {} } = req.body;
  
  if (!prompt || prompt.trim().length === 0) {
    return res.status(400).json({ error: 'prompt required' });
  }
  
  try {
    // STEP 1: Route
    const routing = router.dispatch(prompt, context);
    
    // STEP 2: Select models
    const { primaryModel, secondaryModel } = selector.selectModels(
      routing.metadata.tokenCount,
      routing.metadata.complexity,
      routing.metadata.segment
    );
    routing.models = [primaryModel, secondaryModel];
    
    // STEP 3: Create task
    const task = {
      id: generateUUID(),
      prompt: prompt.slice(0, 5000), // truncate for storage
      context,
      timestamp: Date.now(),
      clientIp: req.ip,
      userId: req.headers['x-user-id'] || 'anon'
    };
    
    // STEP 4: Enqueue
    const queuedTask = dispatcher.enqueue(task, routing);
    
    // STEP 5: Estimate wait time
    const queueStats = dispatcher.getQueueStats();
    const estimatedWaitMs = estimateQueueWait(
      routing.priority,
      queueStats[routing.priority]
    );
    
    // STEP 6: Return response
    return res.json({
      taskId: task.id,
      status: 'QUEUED',
      priority: routing.priority,
      queuePosition: queueStats[routing.priority],
      estimatedWaitMs,
      agents: routing.agents,
      models: routing.models,
      pattern: routing.pattern,
      metadata: routing.metadata
    });
    
  } catch (error) {
    console.error('[Maestro] Error:', error);
    return res.status(500).json({ error: error.message });
  }
});

// ─────────────────────────────────────────────────────────────────
// ENDPOINT 2: GET /api/maestro/task/:taskId — Get Task Status
// ─────────────────────────────────────────────────────────────────

app.get('/api/maestro/task/:taskId', async (req, res) => {
  const { taskId } = req.params;
  
  try {
    // Query Supabase for task status
    const { data, error } = await supabase
      .from('maestro_tasks')
      .select('*')
      .eq('task_id', taskId)
      .single();
    
    if (error) return res.status(404).json({ error: 'task not found' });
    
    return res.json(data);
    
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
});

// ─────────────────────────────────────────────────────────────────
// ENDPOINT 3: GET /api/maestro/stats — Queue Statistics
// ─────────────────────────────────────────────────────────────────

app.get('/api/maestro/stats', (req, res) => {
  const queueStats = dispatcher.getQueueStats();
  
  return res.json({
    timestamp: new Date().toISOString(),
    queues: {
      critical: { count: queueStats.Q0, label: 'Q0' },
      normal: { count: queueStats.Q16, label: 'Q16' },
      background: { count: queueStats['Q∞'], label: 'Q∞' }
    },
    total: queueStats.total,
    agents: {
      active: Object.keys(agentPool).length,
      horizontal: 11,
      vertical: 9
    },
    uptime: process.uptime(),
    pid: process.pid
  });
});

// ─────────────────────────────────────────────────────────────────
// ENDPOINT 4: GET /api/maestro/health — Health Check
// ─────────────────────────────────────────────────────────────────

app.get('/api/maestro/health', (req, res) => {
  return res.json({
    status: 'ok',
    dispatcher: dispatcher.isRunning ? 'running' : 'stopped',
    agents: Object.keys(agentPool).length,
    timestamp: new Date().toISOString()
  });
});

// ─────────────────────────────────────────────────────────────────
// ERROR HANDLING
// ─────────────────────────────────────────────────────────────────

app.use((err, req, res, next) => {
  console.error('[Maestro] Uncaught error:', err);
  res.status(500).json({ error: 'internal server error' });
});

// ─────────────────────────────────────────────────────────────────
// START SERVER
// ─────────────────────────────────────────────────────────────────

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Maestro listening on port ${PORT}`);
});

// ─────────────────────────────────────────────────────────────────
// GRACEFUL SHUTDOWN
// ─────────────────────────────────────────────────────────────────

process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  dispatcher.stop();
  process.exit(0);
});

// ─────────────────────────────────────────────────────────────────
// HELPER FUNCTIONS
// ─────────────────────────────────────────────────────────────────

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

function estimateQueueWait(priority, queueLength) {
  const baseWaitMs = {
    'Q0': 2000,   // 2 sec
    'Q16': 30000, // 30 sec
    'Q∞': 300000  // 5 min (best effort)
  };
  
  const processingTimeMs = {
    'Q0': 30000,  // 30 sec per task
    'Q16': 300000, // 5 min per task
    'Q∞': 600000  // 10 min per task
  };
  
  return baseWaitMs[priority] + (queueLength * processingTimeMs[priority]);
}
```

---

## 4. CLIENT USAGE EXAMPLES

### 4.1 JavaScript Client

```javascript
class MaestroClient {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }

  async submitTask(prompt, context = {}) {
    const response = await fetch(`${this.baseUrl}/api/maestro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, context })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getTaskStatus(taskId) {
    const response = await fetch(`${this.baseUrl}/api/maestro/task/${taskId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async waitForTask(taskId, maxWaitMs = 3600000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitMs) {
      const task = await this.getTaskStatus(taskId);
      
      if (task.status === 'COMPLETE') {
        return task;
      }
      
      if (task.status === 'FAILED') {
        throw new Error(`Task failed: ${task.error}`);
      }
      
      // Poll every 5 seconds
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
    
    throw new Error('Task timeout');
  }

  async getStats() {
    const response = await fetch(`${this.baseUrl}/api/maestro/stats`);
    return response.json();
  }
}

// Usage
const maestro = new MaestroClient();

const task = await maestro.submitTask(
  'Análise de edital de saneamento para AySA',
  { projectId: 'proj_123' }
);

console.log(`Task queued: ${task.taskId}`);
console.log(`Estimated wait: ${task.estimatedWaitMs}ms`);
console.log(`Agents: ${task.agents.join(', ')}`);

const result = await maestro.waitForTask(task.taskId);
console.log('Result:', result);
```

### 4.2 Python Client

```python
import requests
import time
import uuid
from typing import Optional, Dict, Any

class MaestroClient:
    def __init__(self, base_url: str = 'http://localhost:3000'):
        self.base_url = base_url
    
    def submit_task(self, prompt: str, context: Dict = None) -> Dict:
        """Submit a task to Maestro"""
        response = requests.post(
            f'{self.base_url}/api/maestro',
            json={'prompt': prompt, 'context': context or {}}
        )
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        response = requests.get(f'{self.base_url}/api/maestro/task/{task_id}')
        response.raise_for_status()
        return response.json()
    
    def wait_for_task(self, task_id: str, max_wait_sec: int = 3600) -> Dict:
        """Poll until task completes"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_sec:
            task = self.get_task_status(task_id)
            
            if task['status'] == 'COMPLETE':
                return task
            
            if task['status'] == 'FAILED':
                raise RuntimeError(f"Task failed: {task.get('error')}")
            
            time.sleep(5)  # Poll every 5 seconds
        
        raise TimeoutError('Task timeout')
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        response = requests.get(f'{self.base_url}/api/maestro/stats')
        response.raise_for_status()
        return response.json()

# Usage
maestro = MaestroClient()

task = maestro.submit_task(
    'Análise de edital de saneamento para AySA',
    context={'projectId': 'proj_123'}
)

print(f"Task queued: {task['taskId']}")
print(f"Estimated wait: {task['estimatedWaitMs']}ms")
print(f"Agents: {', '.join(task['agents'])}")

result = maestro.wait_for_task(task['taskId'])
print(f"Result: {result}")
```

---

## 5. MONITORING & OBSERVABILITY

### 5.1 Metrics to Track

```javascript
// Metrics dashboard (via Prometheus or similar)

// Queue metrics
maestro_queue_depth{priority="Q0"}      // Count
maestro_queue_depth{priority="Q16"}     // Count
maestro_queue_depth{priority="Q∞"}      // Count

maestro_queue_wait_ms{priority="Q0"}    // Histogram
maestro_queue_wait_ms{priority="Q16"}   // Histogram
maestro_queue_wait_ms{priority="Q∞"}    // Histogram

// Execution metrics
maestro_execution_duration_ms{pattern="direct"}
maestro_execution_duration_ms{pattern="pipeline"}
maestro_execution_duration_ms{pattern="parallel"}
maestro_execution_duration_ms{pattern="fan-out"}

maestro_execution_success_rate{segment="S1"}
maestro_execution_success_rate{segment="S8"}
// etc.

// Model metrics
maestro_model_tokens_used{model="haiku"}
maestro_model_tokens_used{model="sonnet"}
maestro_model_tokens_used{model="opus"}

maestro_model_cost_cents{model="haiku"}
maestro_model_cost_cents{model="sonnet"}
maestro_model_cost_cents{model="opus"}

// Routing metrics
maestro_routes_to_segment{segment="S1"}
maestro_routes_to_segment{segment="S8"}
// etc.
```

### 5.2 Logging

```javascript
// Log format (JSON)
{
  "timestamp": "2026-08-08T14:32:15Z",
  "level": "INFO",
  "component": "maestro",
  "event": "task_complete",
  "taskId": "task_a1b2c3",
  "priority": "Q16",
  "segment": "S8",
  "agents": ["agente-saneamento", "Manta 02", "Manta 15", "Manta 05"],
  "pattern": "pipeline",
  "status": "COMPLETE",
  "wallClockMs": 240000,
  "costCents": 2500,
  "tokenCount": 1200,
  "complexity": "alta"
}
```

---

## 6. DEPLOYMENT CHECKLIST

### Pre-Production

- [ ] **Code Review**
  - [ ] Router implementation reviewed
  - [ ] Model selection matrix validated
  - [ ] Queue dispatcher tested
  - [ ] Integration points verified

- [ ] **Database**
  - [ ] Supabase tables created (maestro_tasks, rag_learning_log)
  - [ ] Indexes created (task_id, status, created_at)
  - [ ] Backups configured
  - [ ] Monitoring alerts set up

- [ ] **Agent Pool**
  - [ ] All 20 agents configured and tested
  - [ ] Model tier assignments verified
  - [ ] API keys / credentials loaded from env

- [ ] **Testing**
  - [ ] Unit tests: router, selector, dispatcher
  - [ ] Integration tests: full request flow (small/medium/large)
  - [ ] Load test: 100 tasks in Q16 queue
  - [ ] Failover test: 1 agent down → system handles gracefully

- [ ] **Documentation**
  - [ ] README.md with API examples
  - [ ] Runbook for on-call support
  - [ ] Monitoring dashboard screenshots
  - [ ] Decision tree diagram

### Production Deployment

- [ ] **Preparation**
  - [ ] Stage environment validated (mirrors prod)
  - [ ] Rollback plan documented
  - [ ] On-call team trained
  - [ ] Stakeholders notified

- [ ] **Deployment**
  - [ ] Deploy router, selector, dispatcher code
  - [ ] Enable monitoring and alerts
  - [ ] Gradual traffic ramp (5% → 25% → 100%)
  - [ ] Monitor error rates, queue depth, latency

- [ ] **Post-Deployment**
  - [ ] First 4 hours: continuous monitoring
  - [ ] First 24 hours: daily check-in
  - [ ] First week: weekly analysis of RAG learning log
  - [ ] Gate: human approval before full production

---

## 7. TROUBLESHOOTING

### Issue: Queue Depth Growing

```javascript
// Symptom: Q16 queue grows indefinitely
// Root cause: Agents too slow or stuck

// Mitigation:
1. Check agent logs for errors
2. Increase timeouts if legitimate slowness
3. Scale agent pool (add more instances)
4. Implement circuit breaker: cancel tasks after 2x estimated time

// Code:
class CircuitBreaker {
  async dispatch(task) {
    const estimatedTime = this.estimateDuration(task);
    const timeoutMs = estimatedTime * 2.5; // 2.5x multiplier
    
    return Promise.race([
      this.executeTask(task),
      this.timeoutAfter(timeoutMs)
    ]);
  }
  
  timeoutAfter(ms) {
    return new Promise((_, reject) =>
      setTimeout(() => reject(new Error('TIMEOUT')), ms)
    );
  }
}
```

### Issue: Wrong Segment Routing

```javascript
// Symptom: S8 task routed to S1
// Root cause: Keyword overlap or regex too broad

// Mitigation:
1. Add more specific keywords to S8 regex
2. Use negative lookahead to exclude false positives
3. Log all routing decisions to debug query

// Example:
// Before: /rodovia|pavimento|CBUQ|BGS|.../ (too broad)
// After: /(?<!saneamento.*)rodovia(?!.*saneamento)/i (specific)
```

### Issue: Model Exhaustion (All Tokens Used)

```javascript
// Symptom: Requests fail with "token quota exceeded"
// Root cause: Daily/monthly API token limit hit

// Mitigation:
1. Check current usage: API dashboard
2. Implement token budgeting per priority/segment
3. Queue background tasks (Q∞) until next billing cycle
4. Alert when approaching 80% quota

// Code:
class TokenBudget {
  async checkBudget(model, tokenCount) {
    const remaining = await this.getRemainingTokens(model);
    
    if (remaining < tokenCount * 1.2) { // 20% safety margin
      const alert = {
        model,
        remaining,
        needed: tokenCount,
        severity: 'HIGH'
      };
      this.alertOncall(alert);
      throw new Error('INSUFFICIENT_TOKENS');
    }
  }
}
```

---

## 8. RELATED DOCUMENTS

- **phase2-router.md** — Core implementation (MaestroRouter, AdaptiveModelSelector, QPrioDispatcher)
- **phase2-routing-rules.md** — Routing keyword reference (S1–S10 decision table)
- **CLAUDE.md** — Master agent registry (source of truth)
- **(Phase 3)** rag-indexing.md — RAG collection setup (Supabase pgvector)
- **(Phase 4)** end-to-end-test.md — Integration testing & validation

---

**Status:** Phase 2 integration architecture complete. Ready for Phase 3 (RAG indexing).

**Next Steps:**
1. Implement phase2-router.md in chosen language (JS/Python/Go)
2. Deploy to staging environment
3. Run integration tests with 3 decision examples
4. Gate: human review before production
5. Move to Phase 3: RAG indexing in Supabase
