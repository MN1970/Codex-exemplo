# Fine-Tuning LoRA Guide — Manta Associados

Guia completo para execução de fine-tuning contínuo de modelos verticais (agentes Manta 03-S6..S10) usando LoRA adapters.

**Versão:** 1.0.0  
**Status:** Ativo  
**Última atualização:** 2026-07-27  

---

## 1. Visão Geral

### O que é Fine-tuning LoRA?

LoRA (Low-Rank Adaptation) permite adaptar um modelo base (ex.: Mistral-7B) a um domínio específico sem reescrever os pesos originais. Apenas um pequeno "adapter" (alguns MB) é treinado e salvo, muito mais eficiente que fine-tuning integral.

### Segmentos Suportados

Fine-tuning está disponível para os 5 agentes verticais Manta 03:

| Código | Segmento | Status | Prioridade | Notas |
|--------|----------|--------|-----------|-------|
| S6 | **saneamento** | ✅ Ativo | 🔴 AySA Priority | ETA, ETE, SNIS, Lei 14.026 |
| S7 | energia | ✅ Ativo | Verde | ANEEL, RAP, leilão |
| S8 | portos | ✅ Ativo | Verde | ANTAQ, dragagem, terminal |
| S9 | aeroportos | ✅ Ativo | Verde | ANAC, pista, TPS |
| S10 | barragens | ✅ Ativo | Verde | ICOLD, CBDB, PNSB |

---

## 2. Arquitetura

### Componentes Principais

```
manta-backend/
├── ml/
│   ├── fine_tune_config.yaml       # Configuração de hiperparâmetros por segmento
│   ├── finetuning.py               # Pipeline core (load → prepare → train → save)
│   ├── lora_finetuner.py           # Wrapper de peft.LoraConfig
│   ├── model_registry.py           # Persistência de adapters (local/S3)
│   └── adapters/                   # Diretório local de adapters treinados
├── tasks/
│   └── finetune_job.py             # FineTuneJobManager — CLI + programático
├── routers/
│   └── ml.py                       # FastAPI endpoints: POST /ml/finetune, GET /ml/finetune/{id}
├── data/
│   ├── saneamento_finetune_dataset.json  # 200+ exemplos Q&A
│   ├── energia_finetune_dataset.json
│   └── ...
└── fine_tune_jobs/                # Histórico de execuções (JSON)
```

### Estado da Máquina

```
CREATED
   ↓
QUEUED → RUNNING → COMPLETED
   ↓         ↓
   └─────────→ FAILED
```

Cada transição é persistida em JSON com timestamp e eventos.

---

## 3. Configuração

### fine_tune_config.yaml

Localizado em `manta-backend/ml/fine_tune_config.yaml`, define:

```yaml
defaults:
  base_model: "mistralai/Mistral-7B-v0.1"
  lora:
    rank: 8                    # r=8 (trade-off velocidade/qualidade)
    alpha: 16                  # lora_alpha=2*r
    dropout: 0.05
    target_modules: [q_proj, v_proj]
  training:
    learning_rate: 2.0e-4
    batch_size: 4
    num_epochs: 3
    warmup_steps: 100
    max_seq_length: 512
    gradient_checkpointing: true  # Memory efficiency
    bf16: true                     # bfloat16 mixed precision

segments:
  saneamento:
    dataset_path: "./manta-backend/data/saneamento_finetune_dataset.json"
    training:
      learning_rate: 3.0e-4    # Levemente superior para domínio complexo
      num_epochs: 4
      warmup_steps: 150
```

### Modelo Base

Default: `mistralai/Mistral-7B-v0.1` (7B tokens, ~14GB VRAM com QLoRA)

Requisitos:
- **Rede:** Acesso a huggingface.co para download
- **GPU:** 14-16GB VRAM (fp16/bf16) ou 6-8GB com QLoRA 4-bit
- **CPU:** Não suportado (muito lento)

---

## 4. Dataset Format

### Estrutura esperada

```json
[
  {
    "instruction": "What are the main components of a Wastewater Treatment Plant (ETE)?",
    "output": "A typical ETE (Estação de Tratamento de Esgoto) consists of: 1) Preliminary treatment... [detailed response]",
    "text": "[instruction + output concatenados — opcional, some models prefer this]"
  },
  {
    "instruction": "Explain the design of gravity sanitary sewers according to NBR 9649.",
    "output": "NBR 9649 specifies design criteria... [detailed technical response]",
    "text": "..."
  }
]
```

### Saneamento Dataset Exemplo

Arquivo: `manta-backend/data/saneamento_finetune_dataset.json`

Contém **200+ exemplos** cobrindo:
- ETA (Estação de Tratamento de Água)
- ETE (Estação de Tratamento de Esgoto)
- Adutoras e redes de distribuição
- SNIS (Sistema Nacional de Informações sobre Saneamento)
- Lei 14.026/2020
- NBR 9649, NBR 12211, NBR 12209
- Operação e manutenção

**Qualidade:** Exemplos detalhados, multi-parte, com terminologia técnica autêntica

---

## 5. Execução — CLI

### Comando Básico

```bash
cd /home/user/Codex-exemplo/manta-backend

# Rodar fine-tuning para saneamento (3 épocas, padrão)
python -m tasks.finetune_job \
    --segment saneamento \
    --epochs 3

# Com learning rate customizado
python -m tasks.finetune_job \
    --segment saneamento \
    --epochs 4 \
    --lr 3.0e-4

# Modo demo (offline, sem GPU — apenas para testes)
python -m tasks.finetune_job \
    --segment saneamento \
    --epochs 1 \
    --demo
```

### Opções

| Opção | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `--segment` | str | (obrigatório) | saneamento\|energia\|portos\|aeroportos\|barragens |
| `--epochs` | int | 3 | Número de épocas |
| `--lr` | float | (config.yaml) | Learning rate override |
| `--base-model` | str | mistralai/Mistral-7B-v0.1 | Modelo base |
| `--no-quantization` | flag | False | Desabilita 4-bit QLoRA |
| `--demo` | flag | False | Modo offline com GPT-2 minúsculo (CI/testes) |
| `--job-dir` | str | ./fine_tune_jobs | Diretório de persistência |

### Output

```
2026-07-27 14:30:45 - manta.tasks.finetune_job - INFO - FineTuneJobManager initialized: job_id=a1b2c3d4-e5f6-..., segment=saneamento, epochs=3, demo_mode=False

================================================================================
Manta Fine-Tuning Job Manager
================================================================================
Segment:       saneamento
Epochs:        3
LR:            (from config)
Base model:    (from config)
Quantization:  enabled
Demo mode:     False
Job dir:       (default)
================================================================================

2026-07-27 14:30:45 - manta.ml.finetuning - INFO - Loading dataset: saneamento_finetune_dataset.json (200 examples)
2026-07-27 14:31:02 - manta.ml.finetuning - INFO - Training loop started...
  Epoch 1/3 ████████████████░░░░ 50% loss=2.1432
  Epoch 2/3 ████████████████████ 100% loss=1.8734
  Epoch 3/3 ████████████████████ 100% loss=1.7621

2026-07-27 14:45:30 - manta.tasks.finetune_job - INFO - Fine-tuning completed successfully: loss=1.7621, perplexity=5.84, time=900.3s

================================================================================
Job Summary
================================================================================
Job ID:        a1b2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7
Status:        completed
Created:       2026-07-27T14:30:45.123456+00:00
Completed:     2026-07-27T14:45:30.987654+00:00

================================================================================
Metrics
================================================================================
Loss:          1.762100
Perplexity:    5.8412
Train steps:   450
Total time:    900.3s
Adapter:       /home/user/Codex-exemplo/manta-backend/ml/adapters/saneamento_a1b2c3d4_20260727_143045
================================================================================
```

### Persistência

Cada run gera um arquivo JSON em `manta-backend/fine_tune_jobs/`:

```json
{
  "job_id": "a1b2c3d4-e5f6-...",
  "segment": "saneamento",
  "status": "completed",
  "created_at": "2026-07-27T14:30:45.123456+00:00",
  "completed_at": "2026-07-27T14:45:30.987654+00:00",
  "epochs": 3,
  "learning_rate": 3.0e-4,
  "base_model": "mistralai/Mistral-7B-v0.1",
  "use_quantization": true,
  "demo_mode": false,
  "events": [
    {
      "timestamp": "2026-07-27T14:30:45.200000+00:00",
      "event": "started",
      "status": "queued"
    },
    {
      "timestamp": "2026-07-27T14:30:46.000000+00:00",
      "event": "training",
      "status": "running",
      "details": {"segment": "saneamento", "epochs": 3}
    },
    {
      "timestamp": "2026-07-27T14:45:30.800000+00:00",
      "event": "completed",
      "status": "completed",
      "details": {
        "loss": 1.7621,
        "perplexity": 5.8412,
        "epoch": 3.0,
        "num_train_steps": 450,
        "total_time_seconds": 900.3
      }
    }
  ],
  "metrics": {
    "segment": "saneamento",
    "base_model": "mistralai/Mistral-7B-v0.1",
    "loss": 1.7621,
    "perplexity": 5.8412,
    "epoch": 3.0,
    "num_train_steps": 450,
    "learning_rate": 3.0e-4,
    "total_time_seconds": 900.3,
    "adapter_path": "/home/user/Codex-exemplo/manta-backend/ml/adapters/saneamento_a1b2c3d4_20260727_143045",
    "adapter_name": "saneamento_a1b2c3d4_20260727_143045"
  },
  "error_message": null
}
```

---

## 6. Execução — Web API

### Criar Job (POST /ml/finetune)

```bash
curl -X POST http://localhost:8000/ml/finetune \
  -H "Content-Type: application/json" \
  -d '{
    "segment": "saneamento",
    "epochs": 3,
    "use_quantization": true,
    "demo_mode": false
  }'
```

**Response (202 Accepted):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "org_id": null,
  "segment": "saneamento",
  "base_model": "mistralai/Mistral-7B-v0.1",
  "epochs": 3,
  "status": "queued",
  "adapter_name": null,
  "adapter_path": null,
  "loss": null,
  "perplexity": null,
  "num_train_steps": null,
  "error_message": null,
  "created_at": "2026-07-27T14:30:45.123456+00:00",
  "started_at": null,
  "completed_at": null
}
```

### Consultar Status (GET /ml/finetune/{job_id})

```bash
curl http://localhost:8000/ml/finetune/550e8400-e29b-41d4-a716-446655440000
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "segment": "saneamento",
  "status": "running",
  "started_at": "2026-07-27T14:30:50.234567+00:00",
  "loss": null,
  "perplexity": null,
  "adapter_path": null
}
```

Após conclusão:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "segment": "saneamento",
  "status": "completed",
  "loss": 1.7621,
  "perplexity": 5.8412,
  "num_train_steps": 450,
  "adapter_path": "/home/user/Codex-exemplo/manta-backend/ml/adapters/saneamento_...",
  "completed_at": "2026-07-27T14:45:30.987654+00:00"
}
```

### Listar Jobs (GET /ml/finetune)

```bash
# Listar todos os jobs
curl "http://localhost:8000/ml/finetune?limit=10"

# Listar jobs de um segmento
curl "http://localhost:8000/ml/finetune?segment=saneamento&limit=10"
```

**Response:**

```json
[
  {
    "id": "550e8400-...",
    "segment": "saneamento",
    "status": "completed",
    "loss": 1.7621,
    "perplexity": 5.8412,
    "created_at": "2026-07-27T14:30:45.123456+00:00",
    "completed_at": "2026-07-27T14:45:30.987654+00:00"
  },
  {
    "id": "660e9500-...",
    "segment": "energia",
    "status": "running",
    "created_at": "2026-07-27T15:00:00.000000+00:00"
  }
]
```

---

## 7. Monitoramento em Tempo Real (WebSocket)

### Conectar ao WebSocket

```javascript
// Cliente JavaScript
const jobId = "550e8400-e29b-41d4-a716-446655440000";
const ws = new WebSocket(`ws://localhost:8000/ws/finetuning/${jobId}`);

ws.onopen = () => {
  console.log("Connected to finetune job stream");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Event:", message);
  // message = {
  //   "type": "status_update|metrics|error",
  //   "data": {...}
  // }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};
```

### Tipos de Mensagens

**Status Update:**
```json
{
  "type": "status_update",
  "data": {
    "status": "running",
    "message": "Epoch 1/3 started",
    "timestamp": "2026-07-27T14:31:00.000000Z"
  }
}
```

**Métricas em Progresso:**
```json
{
  "type": "metrics",
  "data": {
    "epoch": 1,
    "step": 50,
    "loss": 2.1432,
    "learning_rate": 3.0e-4,
    "timestamp": "2026-07-27T14:32:15.000000Z"
  }
}
```

**Erro:**
```json
{
  "type": "error",
  "data": {
    "error": "CUDA out of memory",
    "timestamp": "2026-07-27T14:35:00.000000Z"
  }
}
```

---

## 8. Persistência de Adapters

### Local (Desenvolvimento/Produção pequena)

Adapters salvos em `manta-backend/ml/adapters/`:

```
adapters/
├── saneamento_a1b2c3d4_20260727_143045/
│   ├── adapter_config.json
│   ├── adapter_model.bin
│   └── tokenizer_config.json
├── energia_b2c3d4e5_20260727_150000/
│   ├── adapter_config.json
│   ├── adapter_model.bin
│   └── tokenizer_config.json
└── ...
```

### S3 (Produção grande escala)

Configure em `fine_tune_config.yaml`:

```yaml
deployment:
  adapter_storage: "s3"

monitoring:
  s3_checkpoint_bucket: "my-manta-adapters"
```

Adapters são salvos em:
```
s3://my-manta-adapters/adapters/saneamento_a1b2c3d4_20260727_143045/
```

---

## 9. Troubleshooting

### Problema: "CUDA out of memory"

**Solução:**
- Reduzir `batch_size` em `fine_tune_config.yaml` (de 4 para 2)
- Ativar `gradient_accumulation_steps: 2`
- Usar `use_quantization: true` (QLoRA 4-bit)

```yaml
training:
  batch_size: 2
  gradient_accumulation_steps: 2
  gradient_checkpointing: true
```

### Problema: "mistralai/Mistral-7B-v0.1 not found"

**Solução:**
- Verificar conexão com huggingface.co
- Usar mode demo com `--demo` para testes offline
- Ou usar um modelo alternativo com `--base-model`

```bash
python -m tasks.finetune_job --segment saneamento --demo
```

### Problema: "Dataset file not found"

**Solução:**
- Verificar que `manta-backend/data/{segment}_finetune_dataset.json` existe
- O path é relativo a `BACKEND_DIR` automaticamente

```bash
ls -la /home/user/Codex-exemplo/manta-backend/data/saneamento_finetune_dataset.json
```

### Problema: "High training loss" ou "Perplexity > 20"

**Solução:**
- Dataset pode estar imbalanceado ou de qualidade baixa
- Aumentar `num_epochs` em `fine_tune_config.yaml`
- Verificar exemplos em saneamento_finetune_dataset.json
- Considerar data augmentation (backtranslation, paraphrase)

---

## 10. Best Practices

### 1. Validação de Dataset

Antes de treinar, verificar exemplos:

```bash
python -c "
import json
with open('manta-backend/data/saneamento_finetune_dataset.json') as f:
    data = json.load(f)
    print(f'Total examples: {len(data)}')
    print(f'First example instruction length: {len(data[0][\"instruction\"])} chars')
    print(f'First example output length: {len(data[0][\"output\"])} chars')
"
```

### 2. Monitoramento em Produção

Usar API endpoints para monitorar jobs remotamente:

```bash
#!/bin/bash
JOB_ID="550e8400-e29b-41d4-a716-446655440000"

while true; do
  STATUS=$(curl -s http://localhost:8000/ml/finetune/$JOB_ID | jq -r '.status')
  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]]; then
    echo "Job finished with status: $STATUS"
    curl -s http://localhost:8000/ml/finetune/$JOB_ID | jq '.metrics'
    break
  fi
  echo "Status: $STATUS..."
  sleep 30
done
```

### 3. Versionamento de Adapters

Nome recomendado para adapters:

```
{segment}_{version}_{date}_{hash}

Ex.: saneamento_v1.0_20260727_a1b2c3d4
```

Registrar no banco (`model_registry.py`) com tags:

```python
registry.save_adapter(
    segment="saneamento",
    base_model="mistralai/Mistral-7B-v0.1",
    adapter_name="saneamento_v1.0_20260727_a1b2c3d4",
    local_path="./ml/adapters/saneamento_a1b2c3d4_...",
    loss=1.7621,
    perplexity=5.8412,
    tags='{"aysaprority": true, "production": true}',
    notes="Fine-tuned on ETA, ETE, SNIS examples. Ready for AySA deployment."
)
```

### 4. CI/CD Pipeline

No `.github/workflows/`, adicionar job de smoke test:

```yaml
finetune-smoke-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Run demo fine-tune (offline)
      run: |
        cd manta-backend
        python -m tasks.finetune_job \
          --segment saneamento \
          --epochs 1 \
          --demo
```

---

## 11. Próximos Passos

- [ ] Implementar Dashboard de métricas (Tensorboard/Grafana)
- [ ] Integrar com SharePoint para RAG vector store update
- [ ] Suporte a multi-GPU (DDP) para datasets maiores
- [ ] A/B testing entre adapters antes de deployment
- [ ] Mecanismo de rollback automático se perplexity > threshold
- [ ] Integração com agentes Manta para inference em tempo real

---

## 12. Contatos e Suporte

- **Responsável:** Manta Associados AI/ML team
- **Email:** neves@mantaassociados.com (Maestro contact)
- **Repo:** https://github.com/manta-associados/Codex-exemplo
- **Slack:** #manta-ml-finetune
