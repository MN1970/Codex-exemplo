# Exemplo: Usando Background Agents em Skills (S5 + Horizontais)

**Status:** Reference implementation v5.0  
**Segmento:** S5 (Túneis) + horizontais (Claims, Advisory, etc.)  
**Foco:** Long-running tasks sem bloquear user

---

## Cenário: Análise Geotécnica Completa de Túnel (S5)

Usuário submete projeto de túnel de 5 km. Análise exige:
- Processamento de modelo CAD (1.5 MB) → 45s
- Simulação geotécnica → 60s
- Análise de riscos + relatório → 30s
- **Total: ~135s** (exceeds 30s threshold para background)

Sem background: user espera 2+ minutos bloqueado  
Com background: user recebe job_id imediatamente, continua trabalho

---

## PART 1: Iniciar Background Job

### Skill: `agente-s5-analise-geotecnia.v5.0.md`

```python
#!/usr/bin/env python3
"""
Skill: Análise geotécnica de túnel com background processing

Fluxo:
  1. User submete prompt + projeto CAD
  2. Skill dispara background_spawn() se > 30s esperado
  3. Retorna job_id imediatamente
  4. User pode monitorar via background_status(job_id)
"""

import os
import sys
from pathlib import Path

# Imports locais
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from background_agent_framework import background_spawn, background_status
from agent_state_manager import store_result


def estimate_processing_time(file_size_mb: float, analysis_type: str) -> int:
    """
    Estimate processing time (heuristic).
    
    Args:
      file_size_mb: CAD file size
      analysis_type: "basico" | "executivo" | "risco-completo"
    
    Returns:
      Estimated seconds
    """
    base_time = 30
    
    # Size factor
    size_factor = file_size_mb / 1.0  # 1 MB = 30s base
    
    # Analysis type factor
    type_factor = {
        "basico": 1.0,
        "executivo": 1.5,
        "risco-completo": 2.5
    }.get(analysis_type, 1.0)
    
    estimated = int(base_time * size_factor * type_factor)
    return estimated


def should_background(file_size_mb: float, analysis_type: str) -> bool:
    """
    Decide if analysis should run in background.
    
    Threshold: > 30 seconds expected processing time
    """
    estimated = estimate_processing_time(file_size_mb, analysis_type)
    return estimated > 30


def handle_sync_analysis(prompt: str) -> str:
    """
    Handle short analyses synchronously (< 30s).
    
    Args:
      prompt: User prompt
    
    Returns:
      Analysis result
    """
    # Simulated sync analysis
    return f"Quick analysis result for: {prompt[:50]}..."


def handle_background_analysis(
    agent_id: str,
    prompt: str,
    file_size_mb: float,
    analysis_type: str
) -> Dict[str, str]:
    """
    Handle long analyses asynchronously via background job.
    
    Args:
      agent_id: "manta-03-s5"
      prompt: User prompt
      file_size_mb: CAD file size
      analysis_type: "basico" | "executivo" | "risco-completo"
    
    Returns:
      Dict with job_id + status URL
    """
    # Estimate timeout
    estimated_time = estimate_processing_time(file_size_mb, analysis_type)
    timeout_seconds = min(int(estimated_time * 1.5), 600)  # Max 10 min
    
    # Spawn background job
    job_id = background_spawn(
        agent_id=agent_id,
        prompt=prompt,
        timeout_seconds=timeout_seconds,
        metadata={
            "file_size_mb": file_size_mb,
            "analysis_type": analysis_type,
        },
        callback_url=os.getenv("WEBHOOK_COMPLETION_URL")  # Optional
    )
    
    return {
        "status": "processing",
        "job_id": job_id,
        "estimated_duration_seconds": estimated_time,
        "check_status_url": f"/api/jobs/{job_id}/status",
        "message": f"Análise geotécnica iniciada. Job ID: {job_id}\n"
                   f"Tempo estimado: {estimated_time//60}m {estimated_time%60}s\n"
                   f"Verifique status em: /api/jobs/{job_id}/status"
    }


def main():
    """
    Main skill entry point.
    
    Claude passes:
      prompt: "Analise viabilidade de túnel de 5 km em SP..."
      files: [{"name": "tunel_projeto.dwg", "size_mb": 1.5}]
    """
    
    # Parse input
    prompt = "Analise viabilidade geotécnica de túnel de 5 km"
    file_size_mb = 1.5
    analysis_type = "risco-completo"
    agent_id = "manta-03-s5"
    
    # Decide: sync or background?
    if should_background(file_size_mb, analysis_type):
        # BACKGROUND PATH
        result = handle_background_analysis(
            agent_id=agent_id,
            prompt=prompt,
            file_size_mb=file_size_mb,
            analysis_type=analysis_type
        )
        print("\n" + "="*70)
        print("ANÁLISE GEOTÉCNICA — BACKGROUND JOB")
        print("="*70)
        print(f"Status: {result['status']}")
        print(f"Job ID: {result['job_id']}")
        print(f"Tempo estimado: {result['estimated_duration_seconds']}s")
        print(f"URL Status: {result['check_status_url']}")
        print("="*70)
    else:
        # SYNC PATH
        result = handle_sync_analysis(prompt)
        print("\n" + "="*70)
        print("ANÁLISE GEOTÉCNICA — RESULTADO IMEDIATO")
        print("="*70)
        print(result)
        print("="*70)


if __name__ == "__main__":
    main()
```

---

## PART 2: Monitorar Status (User-facing)

### CLI: Check Job Status

```bash
# Check job status
$ python scripts/background_agent_framework.py status <job_id>

Output:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "manta-03-s5",
  "status": "running",
  "prompt": "Analise viabilidade...",
  "created_at": "2026-07-25T14:32:00Z",
  "started_at": "2026-07-25T14:32:05Z",
  "retry_count": 0,
  "timeout_seconds": 300
}
```

### API Endpoint: Job Status

```python
# In your API (FastAPI/Flask example)
@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Check background job status."""
    from background_agent_framework import background_status
    
    result = background_status(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": result["status"],
        "progress": {
            "is_pending": result["status"] == "pending",
            "is_running": result["status"] == "running",
            "is_completed": result["status"] == "completed",
            "is_failed": result["status"] == "failed",
            "is_timeout": result["status"] == "timeout",
        },
        "result": result.get("result"),
        "error": result.get("error"),
        "started_at": result.get("started_at"),
        "completed_at": result.get("completed_at"),
    }
```

---

## PART 3: Agente Recebe Resultado (Hook Integration)

### Hook: `SubagentStop` (settings.json)

Quando agente completa o trabalho, hook `SubagentStop` dispara:

```json
{
  "hooks": {
    "subagent_stop": {
      "enabled": true,
      "steps": [
        {
          "name": "background_store_result",
          "description": "Store background job result in agent_state",
          "script": "scripts/background_job_completion_handler.py",
          "parameters": {
            "job_id": "$JOB_ID",
            "agent_id": "$AGENT_ID",
            "result": "$AGENT_OUTPUT",
            "user_rating": "$USER_FEEDBACK_RATING"
          },
          "on_error": "warn"
        }
      ]
    }
  }
}
```

### Script: `background_job_completion_handler.py`

```python
#!/usr/bin/env python3
"""
Handler: Armazena resultado de background job em agent_state.

Chamado por hook SubagentStop após agente completar.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".."))
from scripts.background_agent_framework import get_framework
from scripts.agent_state_manager import store_result


def handle_job_completion(
    job_id: str,
    agent_id: str,
    result: str,
    user_rating: int = None
):
    """
    Process job completion.
    
    Args:
      job_id: Background job UUID
      agent_id: Agent ID
      result: Agente output
      user_rating: User feedback (0-5)
    """
    framework = get_framework()
    
    # 1. Fetch job from DB
    job = framework.get_job_status(job_id)
    if not job:
        print(f"ERROR: Job not found: {job_id}")
        return False
    
    # 2. Update job with result
    from background_agent_framework import JobStatus
    framework.update_job_status(
        job_id,
        JobStatus.COMPLETED,
        result=result,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    # 3. Store in agent_state (enables memory for future sessions)
    store_result(
        agent_id=agent_id,
        session_id=job.get("session_id", "unknown"),
        result_text=result,
        source_prompt=job.get("prompt"),
        user_rating=user_rating
    )
    
    # 4. Invoke callback if configured
    callback_url = job.get("callback_url")
    if callback_url:
        try:
            import requests
            requests.post(
                callback_url,
                json={
                    "job_id": job_id,
                    "status": "completed",
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timeout=10
            )
        except Exception as e:
            print(f"WARNING: Callback failed: {e}")
    
    return True


if __name__ == "__main__":
    from datetime import datetime, timezone
    
    job_id = os.getenv("JOB_ID")
    agent_id = os.getenv("AGENT_ID")
    result = os.getenv("RESULT")
    user_rating = int(os.getenv("USER_RATING", 0)) or None
    
    success = handle_job_completion(job_id, agent_id, result, user_rating)
    sys.exit(0 if success else 1)
```

---

## PART 4: Start Job Queue Processor

### Initialize (at app startup)

```python
# app.py or main.py
from scripts.agent_job_queue import start_queue, stop_queue
import atexit

# Start job queue at startup
if start_queue():
    print("Background job queue started")
else:
    print("WARNING: Failed to start job queue")

# Graceful shutdown
atexit.register(stop_queue)
```

### CLI: Start Processor

```bash
# Terminal 1: Start job queue processor
$ python scripts/agent_job_queue.py start

Output:
2026-07-25 14:32:00 [INFO] Job queue started
2026-07-25 14:32:01 [INFO] Found 5 pending jobs
2026-07-25 14:32:01 [INFO] Spawned worker for job: 550e8400-e29b-41d4-a716-446655440000
2026-07-25 14:32:01 [INFO] Spawned worker for job: 660e8400-e29b-41d4-a716-446655440001
...
```

```bash
# Terminal 2: Monitor
$ python scripts/agent_job_queue.py status

Output:
{
  "is_running": true,
  "active_jobs": 2,
  "max_concurrent": 5,
  "poll_interval_seconds": 1
}
```

---

## PART 5: Full Workflow Example

### User submits long analysis

```
User: "Analise viabilidade geotécnica de túnel de 5 km. Arquivo: tunel.dwg (1.5MB)"

Agent (S5):
  1. Detecta file_size > threshold
  2. Estima tempo: ~135s
  3. Dispara background_spawn()
  4. Retorna job_id imediatamente

User sees:
  ✅ Análise iniciada. Job ID: 550e8400-...
  ⏱️ Tempo estimado: 2m 15s
  🔗 Status: /api/jobs/550e8400-/status
```

### User checks status while working on other projects

```bash
$ curl http://api.manta.local/jobs/550e8400-e29b-41d4-a716-446655440000/status

{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": {
    "is_running": true
  },
  "started_at": "2026-07-25T14:32:05Z",
  "completed_at": null
}
```

### Job completes

```bash
$ curl http://api.manta.local/jobs/550e8400-e29b-41d4-a716-446655440000/status

{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": {
    "is_completed": true
  },
  "result": "Análise geotécnica completa:\n\n## Viabilidade\nViável com ressalvas em 2 seções.\n\n## Riscos\n...",
  "started_at": "2026-07-25T14:32:05Z",
  "completed_at": "2026-07-25T14:34:20Z"
}
```

### User optionally rates result

```bash
$ curl -X POST http://api.manta.local/jobs/550e8400-/rate \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "feedback": "Análise muito completa!"}'

✅ Rating stored. Feedback used for R9 embedding fine-tuning.
```

---

## Tabelas Supabase Envolvidas

### agent_jobs (Job Queue)
```sql
id (UUID)
agent_id (TEXT) — "manta-03-s5"
status (TEXT) — "pending" | "running" | "completed" | "failed" | "timeout"
prompt (TEXT)
result (TEXT)
created_at (TIMESTAMPTZ)
started_at (TIMESTAMPTZ)
completed_at (TIMESTAMPTZ)
retry_count (INT)
timeout_seconds (INT)
callback_url (TEXT)
metadata (JSONB)
```

### agent_memory (Result Storage)
```sql
— Via store_result() na completion handler
agent_id (TEXT)
session_id (TEXT)
memory_key = "result:output"
memory_value (JSONB) — { "text": "Análise completa..." }
user_rating (SMALLINT) — 0-5
expires_at (TIMESTAMPTZ) — NOW() + 480 min
```

### agent_state (Metrics & Embeddings)
```sql
— Via update_agent_state() na completion handler
agent_id (TEXT)
avg_user_rating (FLOAT8) — Média de ratings (R9)
feedback_count (INT)
embedding_vector (vector[1536]) — Último resultado embedado
total_memory_size_bytes (BIGINT)
```

### agent_job_metrics (Aggregations)
```sql
— Auto-populated by trigger on completion
agent_id (TEXT)
total_jobs (INT)
completed_jobs (INT)
failed_jobs (INT)
success_rate (FLOAT8) — %
avg_duration_seconds (FLOAT8)
```

---

## Troubleshooting

### Job stays in "pending" for hours

**Check:** Is job queue processor running?

```bash
$ python scripts/agent_job_queue.py status
```

If not, start it:

```bash
$ python scripts/agent_job_queue.py start &
```

### Job times out on first attempt

**Check:** Agent code may be slow. Increase timeout:

```python
job_id = background_spawn(
    agent_id="manta-03-s5",
    prompt="...",
    timeout_seconds=600  # 10 min instead of 5
)
```

Retry happens automatically (max 2x).

### Memory grows over time

**Check:** Expired memories are not purged. Trigger cleanup:

```bash
$ python scripts/agent_state_manager.py purge --agent-id manta-03-s5
```

Or configure cron job (APScheduler):

```python
from agent_state_manager import get_manager
manager = get_manager()
# Cleanup daily at 3 AM UTC
scheduler.add_job(
    lambda: manager.purge_expired_memories(),
    CronTrigger(hour=3),
    id="memory_purge_daily"
)
```

---

## Integration with CLAUDE.md v5.0

Background agents implement **P7** (Orquestração em Background):

```
Maestro (R1) rota prompt → Agente vertical (S1-S10)
     ↓
Agente detecta long-running task (> 30s)
     ↓
Dispara background_spawn() → job_id
     ↓
Retorna job_id ao user imediatamente
     ↓
JobQueue processor (APScheduler) monitora agent_jobs
     ↓
Quando status=completed:
  - Callback webhook (se configurado)
  - Store em agent_memory + agent_state (R9 feedback loop)
  - Atualiza agent_job_metrics
     ↓
User consulta /api/jobs/{job_id}/status
     ↓
Opcionalmente rate resultado (0-5 stars)
     ↓
Rating agregado em agent_state.avg_user_rating (R9)
     ↓
Embedding fine-tuning semanal (R9 feedback loop)
```

---

## Files Delivered

```
scripts/
  ├── background_agent_framework.py    — Core: spawn, status, list
  ├── agent_state_manager.py           — Store/retrieve state
  ├── agent_job_queue.py               — APScheduler + worker threads
  └── example_background_agent_skill.md (this file)

supabase/migrations/
  └── 2026_07_25_agent_background_jobs.sql — agent_jobs schema + triggers
```

---

**Versão:** v5.0  
**Status:** Ready for S5 (Túneis) + horizontais  
**Segmento Piloto:** Manta 03-S5, Claims (Manta 01)  
**Próximos passos:** Integrar em agentes verticais; monitorar latência, sucesso, custo
