# WebSocket Monitoring — Real-time Fine-Tuning Progress

Guia para monitorar jobs de fine-tuning em tempo real via WebSocket.

## Visão Geral

O endpoint WebSocket `/ws/finetune/{job_id}` fornece stream de eventos em tempo real durante o treinamento:

- **status_update**: Mudança de estado (queued → running → completed|failed)
- **metrics**: Métricas de treino em progresso (loss, learning rate por epoch/step)
- **error**: Erro durante execução
- **job_status**: Status inicial quando cliente conecta

## JavaScript Client

### Exemplo Básico

```javascript
class FineTuneMonitor {
  constructor(jobId, handlers = {}) {
    this.jobId = jobId;
    this.handlers = {
      onStatusChange: handlers.onStatusChange || (() => {}),
      onMetrics: handlers.onMetrics || (() => {}),
      onError: handlers.onError || (() => {}),
      onConnect: handlers.onConnect || (() => {}),
      onDisconnect: handlers.onDisconnect || (() => {}),
    };
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ml/ws/finetune/${this.jobId}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`[${this.jobId}] Connected to finetune monitor`);
      this.handlers.onConnect();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this._handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error(`[${this.jobId}] WebSocket error:`, error);
      this.handlers.onError(error);
    };

    this.ws.onclose = () => {
      console.log(`[${this.jobId}] Disconnected from finetune monitor`);
      this.handlers.onDisconnect();
    };
  }

  _handleMessage(message) {
    const { type, data, timestamp } = message;

    switch (type) {
      case 'job_status':
        console.log(`[${this.jobId}] Initial status:`, data);
        break;

      case 'status_update':
        console.log(
          `[${this.jobId}] Status changed: ${data.old_status} → ${data.new_status}`
        );
        this.handlers.onStatusChange(data);
        break;

      case 'metrics':
        console.log(`[${this.jobId}] Epoch ${data.epoch} - Loss: ${data.loss.toFixed(4)}`);
        this.handlers.onMetrics(data);
        break;

      case 'error':
        console.error(`[${this.jobId}] Error:`, data.error);
        this.handlers.onError(data);
        break;

      default:
        console.warn(`[${this.jobId}] Unknown message type: ${type}`);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Uso
const jobId = "550e8400-e29b-41d4-a716-446655440000";
const monitor = new FineTuneMonitor(jobId, {
  onStatusChange: (data) => {
    console.log(`Job status: ${data.new_status}`);
    // Atualizar UI
  },
  onMetrics: (data) => {
    console.log(`Loss: ${data.loss}, LR: ${data.learning_rate}`);
    // Atualizar gráficos
  },
  onError: (error) => {
    console.error("Training failed:", error);
    // Mostrar erro na UI
  },
  onConnect: () => {
    console.log("Monitor connected");
  },
  onDisconnect: () => {
    console.log("Monitor disconnected");
  },
});

monitor.connect();

// Desconectar (opcionalmente)
// setTimeout(() => monitor.disconnect(), 5000);
```

### React Component

```jsx
import { useEffect, useState } from 'react';

export function FineTuneJobMonitor({ jobId }) {
  const [status, setStatus] = useState('connecting');
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(
      `${protocol}//${window.location.host}/ml/ws/finetune/${jobId}`
    );

    ws.onopen = () => {
      console.log('Connected');
      setStatus('connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'status_update':
          setStatus(message.data.new_status);
          setEvents((prev) => [
            ...prev,
            {
              type: 'status',
              timestamp: message.timestamp,
              data: message.data,
            },
          ]);
          break;

        case 'metrics':
          setMetrics(message.data);
          setEvents((prev) => [
            ...prev,
            {
              type: 'metrics',
              timestamp: message.timestamp,
              data: message.data,
            },
          ]);
          break;

        case 'error':
          setError(message.data.error);
          setEvents((prev) => [
            ...prev,
            {
              type: 'error',
              timestamp: message.timestamp,
              data: message.data,
            },
          ]);
          break;

        case 'job_status':
          setStatus(message.data.status);
          break;

        default:
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error');
    };

    ws.onclose = () => {
      console.log('Disconnected');
      setStatus('disconnected');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [jobId]);

  return (
    <div className="finetune-monitor">
      <h2>Fine-Tuning Job: {jobId}</h2>

      <div className="status">
        <p>Status: <strong>{status}</strong></p>
      </div>

      {metrics && (
        <div className="metrics">
          <h3>Current Metrics</h3>
          <p>Epoch: {metrics.epoch}</p>
          <p>Loss: {metrics.loss?.toFixed(4)}</p>
          <p>Learning Rate: {metrics.learning_rate?.toExponential(2)}</p>
          {metrics.perplexity && <p>Perplexity: {metrics.perplexity?.toFixed(2)}</p>}
        </div>
      )}

      {error && (
        <div className="error">
          <p>Error: {error}</p>
        </div>
      )}

      <div className="events">
        <h3>Events</h3>
        <ul>
          {events.map((event, idx) => (
            <li key={idx}>
              [{event.timestamp}] {event.type}: {JSON.stringify(event.data)}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

## Python Client (asyncio)

```python
import asyncio
import json
import websockets

class FineTuneMonitorAsync:
    def __init__(self, job_id: str, base_url: str = "ws://localhost:8000"):
        self.job_id = job_id
        self.ws_url = f"{base_url}/ml/ws/finetune/{job_id}"
        self.running = False

    async def monitor(self, callback=None):
        """
        Monitor job em background. Callback recebe (type, data).
        """
        self.running = True
        try:
            async with websockets.connect(self.ws_url) as ws:
                print(f"Connected to {self.ws_url}")

                while self.running:
                    try:
                        message_json = await asyncio.wait_for(ws.recv(), timeout=60)
                        message = json.loads(message_json)

                        if callback:
                            callback(message["type"], message["data"])
                        else:
                            self._default_handler(message["type"], message["data"])

                    except asyncio.TimeoutError:
                        print("WebSocket timeout (no messages for 60s)")
                    except Exception as e:
                        print(f"Error receiving message: {e}")
                        break

        except Exception as e:
            print(f"Connection error: {e}")

    def _default_handler(self, msg_type, data):
        """Default message handler."""
        if msg_type == "status_update":
            print(f"Status: {data['old_status']} → {data['new_status']}")
        elif msg_type == "metrics":
            print(
                f"Epoch {data.get('epoch')} - Loss: {data.get('loss', 'N/A'):.4f}"
            )
        elif msg_type == "error":
            print(f"Error: {data['error']}")
        elif msg_type == "job_status":
            print(f"Job status: {data['status']}")

    def stop(self):
        """Stop monitoring."""
        self.running = False

# Uso
async def main():
    monitor = FineTuneMonitorAsync(
        job_id="550e8400-e29b-41d4-a716-446655440000"
    )

    # Monitorar por 5 minutos
    try:
        await asyncio.wait_for(monitor.monitor(), timeout=300)
    except asyncio.TimeoutError:
        print("Monitoring timeout")
    finally:
        monitor.stop()

asyncio.run(main())
```

## Padrões de Uso

### 1. Monitorar até Conclusão

```javascript
async function monitorUntilComplete(jobId, timeout = 3600000) {
  return new Promise((resolve, reject) => {
    const monitor = new FineTuneMonitor(jobId, {
      onStatusChange: (data) => {
        if (data.new_status === 'completed') {
          monitor.disconnect();
          resolve({ status: 'completed', jobId });
        } else if (data.new_status === 'failed') {
          monitor.disconnect();
          reject(new Error(`Job failed: ${jobId}`));
        }
      },
      onError: (error) => {
        monitor.disconnect();
        reject(error);
      },
    });

    monitor.connect();

    setTimeout(() => {
      monitor.disconnect();
      reject(new Error('Monitoring timeout'));
    }, timeout);
  });
}

// Uso
try {
  const result = await monitorUntilComplete(jobId);
  console.log('Job completed:', result);
} catch (error) {
  console.error('Job failed or timed out:', error);
}
```

### 2. Dashboard com Métricas em Tempo Real

```jsx
export function FineTuneMetricsDashboard({ jobId }) {
  const [lossHistory, setLossHistory] = useState([]);
  const [lrHistory, setLrHistory] = useState([]);

  return (
    <FineTuneJobMonitor
      jobId={jobId}
      handlers={{
        onMetrics: (data) => {
          setLossHistory((prev) => [
            ...prev,
            { step: data.step, loss: data.loss },
          ]);
          setLrHistory((prev) => [
            ...prev,
            { step: data.step, lr: data.learning_rate },
          ]);
        },
      }}
    >
      <LineChart data={lossHistory} title="Training Loss" />
      <LineChart data={lrHistory} title="Learning Rate" />
    </FineTuneJobMonitor>
  );
}
```

### 3. Notificações Push/Email

```javascript
const monitor = new FineTuneMonitor(jobId, {
  onStatusChange: async (data) => {
    if (data.new_status === 'completed') {
      // Enviar notificação
      await fetch('/api/notify', {
        method: 'POST',
        body: JSON.stringify({
          type: 'finetune_complete',
          jobId,
          message: `Fine-tuning job ${jobId} completed`,
        }),
      });

      // Enviar email
      await fetch('/api/email', {
        method: 'POST',
        body: JSON.stringify({
          to: 'user@example.com',
          subject: 'Fine-tuning Complete',
          body: `Job ${jobId} completed successfully`,
        }),
      });
    }
  },
  onError: async (error) => {
    await fetch('/api/notify', {
      method: 'POST',
      body: JSON.stringify({
        type: 'finetune_error',
        jobId,
        message: `Fine-tuning failed: ${error.error}`,
      }),
    });
  },
});

monitor.connect();
```

## Mensagens de Exemplo

### Quando conecta

```json
{
  "type": "job_status",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "segment": "saneamento",
    "status": "running",
    "epochs": 3,
    "created_at": "2026-07-27T14:30:45.123456+00:00",
    "started_at": "2026-07-27T14:30:50.234567+00:00"
  },
  "timestamp": "2026-07-27T14:30:51.000000Z"
}
```

### Status update (running)

```json
{
  "type": "status_update",
  "data": {
    "old_status": "queued",
    "new_status": "running",
    "job_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": "2026-07-27T14:30:50.234567Z"
}
```

### Métricas durante treino

```json
{
  "type": "metrics",
  "data": {
    "epoch": 1,
    "step": 50,
    "loss": 2.1432,
    "learning_rate": 3.0e-4,
    "gradient_norm": 0.234
  },
  "timestamp": "2026-07-27T14:32:15.123456Z"
}
```

### Status update (completed)

```json
{
  "type": "status_update",
  "data": {
    "old_status": "running",
    "new_status": "completed",
    "job_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": "2026-07-27T14:45:30.987654Z"
}
```

### Error

```json
{
  "type": "error",
  "data": {
    "error": "CUDA out of memory",
    "job_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": "2026-07-27T14:35:00.000000Z"
}
```

## Limitações & Considerações

1. **WebSocket requer HTTP/2 ou HTTPS em produção** — HTTP/1.1 com proxies pode ter issues
2. **Conexões são stateless** — se o servidor recicla, clientes precisam reconectar
3. **Sem persistência de eventos** — se o cliente desconectar, perde histórico (use API GET para recuperar)
4. **Broadcast limitado** — eventos são enviados a todos os clientes de um job, considere rate limiting se muitas conexões
