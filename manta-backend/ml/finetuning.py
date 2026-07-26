"""
ml/finetuning.py — Pipeline de fine-tuning LoRA para os agentes verticais
da Manta (saneamento, energia, portos, aeroportos, barragens).

Carrega um modelo base (default: mistralai/Mistral-7B-v0.1), aplica um
adapter LoRA via `peft` e roda o loop de treino com `transformers.Trainer`
sobre o dataset do segmento (`data/{segment}_finetune_dataset.json`).
Salva só o adapter (poucos MB) em vez do modelo inteiro — é assim que o
LoRA barateia o fine-tuning: o peso base nunca é reescrito.

Pipeline (nomes literais usados pelo endpoint POST /ml/finetune e pelos
testes — ver tests/test_finetuning.py):

    tokenizer            = load_base_model(base_model_name)[1]
    dataset              = prepare_dataset(segment, tokenizer)
    trainer              = create_trainer(model, adapter, dataset, tokenizer)
    metrics              = train(trainer)
    adapter_path         = save_adapter(model, path)
    model                = load_adapter(path)

Uso via CLI:

    python -m ml.finetuning run --segment saneamento --epochs 3
    python -m ml.finetuning run --segment saneamento --epochs 1 --demo   # offline, sem GPU/rede

NOTA — rede e GPU: `mistralai/Mistral-7B-v0.1` precisa (a) egress para
huggingface.co para baixar os pesos e (b) uma GPU com ~14-16GB de VRAM
(ou `use_quantization=True` com bitsandbytes + CUDA para caber em ~6GB).
Neste sandbox de desenvolvimento (sem GPU, sem egress para huggingface.co
— mesma limitação documentada em ml/routing.py) isso não é executável.
Por isso este módulo expõe `--demo` / `demo_mode=True`: constrói um
GPT-2 minúsculo do zero (torch puro, sem download) + um tokenizer
BPE treinado localmente nos próprios dados do segmento, e roda a MESMA
pipeline (prepare_dataset → create_trainer → train → save_adapter →
load_adapter) fim-a-fim. É o mesmo princípio do HashingEncoder em
ml/routing.py: um substituto 100% offline para validar mecanicamente a
pipeline, nunca um artefato de produção — `demo_mode=True` marca o
adapter salvo com base_model="demo-tiny-gpt2-offline" para nunca ser
confundido com um fine-tune real de Mistral-7B.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

logger = logging.getLogger("manta.ml.finetuning")

# ---------------------------------------------------------------------------
# Constantes / paths
# ---------------------------------------------------------------------------

ML_DIR = Path(__file__).parent
BACKEND_DIR = ML_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
CONFIG_FILE = ML_DIR / "fine_tune_config.yaml"
DEFAULT_OUTPUT_DIR = ML_DIR / "adapters"

DEFAULT_BASE_MODEL = "mistralai/Mistral-7B-v0.1"
DEMO_BASE_MODEL_NAME = "demo-tiny-gpt2-offline"

# Os 5 segmentos verticais cobertos pelo fine-tuning (Manta 03-S6..S10 —
# ver CLAUDE.md "MAPA COMPLETO DE AGENTES"). Só "saneamento" tem dataset
# real commitado em data/ hoje; os demais aguardam o dataset
# correspondente (ver docs/DEPLOY-v4.2.md checklist).
SUPPORTED_SEGMENTS: Tuple[str, ...] = (
    "saneamento",
    "energia",
    "portos",
    "aeroportos",
    "barragens",
)


# ---------------------------------------------------------------------------
# Configuração (dataclasses)
# ---------------------------------------------------------------------------


@dataclass
class LoRAAdapterConfig:
    """Configuração do adapter LoRA (peft.LoraConfig simplificado)."""

    r: int = 8
    lora_alpha: int = 16
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout: float = 0.05
    bias: str = "none"


@dataclass
class TrainingConfig:
    """Hiperparâmetros do loop de treino (transformers.TrainingArguments)."""

    learning_rate: float = 2.0e-4
    batch_size: int = 4
    num_epochs: int = 3
    max_steps: int = -1
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    logging_steps: int = 10
    save_steps: int = 50
    eval_steps: int = 50
    validation_split: float = 0.1
    max_seq_length: int = 512
    lr_scheduler_type: str = "cosine"
    optim: str = "adamw_torch"


@dataclass
class TrainingMetrics:
    """Métricas coletadas ao final do treino — o que fica gravado em
    metrics.json ao lado do adapter e no registro do job (FineTuneJob)."""

    segment: str
    base_model: str
    loss: float
    perplexity: float
    epoch: float
    num_train_steps: int
    learning_rate: float
    total_time_seconds: float


# ---------------------------------------------------------------------------
# Config YAML (fine_tune_config.yaml) — defaults + overrides por segmento
# ---------------------------------------------------------------------------


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_segment_config(segment: str, config_file: Optional[Path] = None) -> Dict[str, Any]:
    """Carrega `fine_tune_config.yaml`, faz merge de `defaults` +
    `segments[segment]` e devolve o dict resultante (usado por
    prepare_dataset/create_trainer para resolver hiperparâmetros e o
    caminho do dataset sem precisar hardcodar nada por segmento)."""
    path = Path(config_file) if config_file else CONFIG_FILE
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    defaults = raw.get("defaults", {})
    segment_cfg = raw.get("segments", {}).get(segment, {})
    return _deep_merge(defaults, segment_cfg)


def _training_config_from_dict(cfg: Dict[str, Any]) -> TrainingConfig:
    training = cfg.get("training", {})
    evaluation = cfg.get("evaluation", {})
    data = cfg.get("data", {})
    return TrainingConfig(
        learning_rate=training.get("learning_rate", 2.0e-4),
        batch_size=training.get("batch_size", 4),
        num_epochs=training.get("num_epochs", 3),
        max_steps=training.get("max_steps", -1),
        warmup_steps=training.get("warmup_steps", 100),
        weight_decay=training.get("weight_decay", 0.01),
        gradient_accumulation_steps=training.get("gradient_accumulation_steps", 1),
        logging_steps=cfg.get("logging", {}).get("logging_steps", 10),
        save_steps=evaluation.get("save_steps", 50),
        eval_steps=evaluation.get("eval_steps", 50),
        validation_split=evaluation.get("validation_split", 0.1),
        max_seq_length=data.get("max_seq_length", 512),
        lr_scheduler_type=training.get("lr_scheduler_type", "cosine"),
    )


def _lora_config_from_dict(cfg: Dict[str, Any]) -> LoRAAdapterConfig:
    lora = cfg.get("lora", {})
    return LoRAAdapterConfig(
        r=lora.get("rank", 8),
        lora_alpha=lora.get("alpha", 16),
        target_modules=list(lora.get("target_modules", ["q_proj", "v_proj"])),
        lora_dropout=lora.get("dropout", 0.05),
        bias=lora.get("bias", "none"),
    )


def resolve_dataset_path(segment: str, data_dir: Optional[Path] = None) -> Path:
    """Resolve o caminho do dataset de um segmento:
    `manta-backend/data/{segment}_finetune_dataset.json`.

    Não depende do `dataset_path` gravado em fine_tune_config.yaml (esse
    valor assume cwd=raiz do repo; aqui resolvemos sempre relativo a
    este arquivo, então funciona independente de onde o processo for
    iniciado — mesmo princípio de ml/routing.py::AGENT_DATA_FILE).
    """
    base = Path(data_dir) if data_dir else DATA_DIR
    return base / f"{segment}_finetune_dataset.json"


# ---------------------------------------------------------------------------
# Estágio 0 — carregar modelo base + tokenizer (mistral-7b)
# ---------------------------------------------------------------------------


def load_base_model(
    base_model_name: str = DEFAULT_BASE_MODEL,
    use_quantization: bool = True,
    device_map: str = "auto",
    hf_token: Optional[str] = None,
):
    """Carrega o modelo base (default: Mistral-7B) + tokenizer do
    Hugging Face Hub.

    Requer rede (huggingface.co) e, para um modelo de 7B, GPU (16GB+ em
    fp16/bf16, ou ~6-8GB com `use_quantization=True` via bitsandbytes
    4-bit/QLoRA). Sem CUDA disponível, `use_quantization` é
    automaticamente desligado (bitsandbytes não roda em CPU) e o modelo
    carrega em fp32 na CPU — funcional, mas impraticavelmente lento para
    um 7B; use `build_demo_base_model_and_tokenizer()` para validar a
    pipeline nesse cenário.

    Args:
        base_model_name: ID do modelo no HF Hub.
        use_quantization: usa 4-bit (QLoRA) se CUDA + bitsandbytes disponíveis.
        device_map: estratégia de alocação de dispositivo do `accelerate`.
        hf_token: token do HF Hub (modelos gated/privados).

    Returns:
        (model, tokenizer)
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if hf_token:
        from huggingface_hub import login as hf_login

        hf_login(token=hf_token)

    cuda_available = torch.cuda.is_available()
    quantization_config = None

    if use_quantization and cuda_available:
        try:
            from transformers import BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            logger.info("finetuning: usando quantização 4-bit (QLoRA)")
        except ImportError:
            logger.warning("finetuning: bitsandbytes não instalado — seguindo sem quantização")
    elif use_quantization and not cuda_available:
        logger.warning(
            "finetuning: use_quantization=True mas CUDA indisponível — "
            "bitsandbytes exige GPU; carregando sem quantização (fp32/CPU)."
        )

    logger.info("finetuning: carregando tokenizer de %s", base_model_name)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True, token=hf_token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs: Dict[str, Any] = {"trust_remote_code": True, "token": hf_token}
    if quantization_config is not None:
        model_kwargs["quantization_config"] = quantization_config
        model_kwargs["device_map"] = device_map
    elif cuda_available:
        model_kwargs["torch_dtype"] = torch.bfloat16
        model_kwargs["device_map"] = device_map
    else:
        model_kwargs["torch_dtype"] = torch.float32

    logger.info("finetuning: carregando modelo base %s", base_model_name)
    model = AutoModelForCausalLM.from_pretrained(base_model_name, **model_kwargs)

    return model, tokenizer


def build_demo_base_model_and_tokenizer(
    demo_texts: List[str],
    n_embd: int = 64,
    n_layer: int = 2,
    n_head: int = 2,
    block_size: int = 64,
    vocab_size: int = 800,
):
    """Constrói um GPT-2 minúsculo do zero (pesos aleatórios, SEM
    download) + um tokenizer BPE treinado localmente em `demo_texts`.

    Substituto 100% offline de `load_base_model()` para dev/CI sem
    GPU/rede — ver nota no topo do módulo. NUNCA usar em produção
    (`base_model_name` fica marcado como DEMO_BASE_MODEL_NAME
    justamente para isso).

    Returns:
        (model, tokenizer)
    """
    import tempfile

    import torch
    from tokenizers import ByteLevelBPETokenizer
    from transformers import GPT2Config, GPT2LMHeadModel, GPT2TokenizerFast

    special_tokens = ["<pad>", "<s>", "</s>", "<unk>"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        bpe = ByteLevelBPETokenizer()
        bpe.train_from_iterator(
            demo_texts,
            vocab_size=vocab_size,
            min_frequency=1,
            special_tokens=special_tokens,
        )
        bpe.save_model(tmp_dir)

        tokenizer = GPT2TokenizerFast(
            vocab_file=str(Path(tmp_dir) / "vocab.json"),
            merges_file=str(Path(tmp_dir) / "merges.txt"),
        )
        tokenizer.add_special_tokens(
            {"pad_token": "<pad>", "bos_token": "<s>", "eos_token": "</s>", "unk_token": "<unk>"}
        )
        tokenizer.model_max_length = block_size

    config = GPT2Config(
        vocab_size=len(tokenizer),
        n_positions=block_size,
        n_ctx=block_size,
        n_embd=n_embd,
        n_layer=n_layer,
        n_head=n_head,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        name_or_path=DEMO_BASE_MODEL_NAME,
    )
    torch.manual_seed(42)  # inicialização determinística — reprodutibilidade do smoke test
    model = GPT2LMHeadModel(config)
    # `PreTrainedModel.__init__` copia `config.name_or_path` para
    # `self.name_or_path` na hora da construção (não é uma property viva
    # sobre o config) — é ESTE atributo que o peft grava em
    # adapter_config.json["base_model_name_or_path"]. Setar de novo aqui
    # (redundante com o `name_or_path=` acima, mas explícito) garante que
    # load_adapter() consiga detectar "isso é um adapter demo" mais
    # tarde sem depender de uma leitura implícita do config.
    model.name_or_path = DEMO_BASE_MODEL_NAME

    logger.info(
        "finetuning: modelo demo offline construído (%s params, vocab=%d)",
        f"{model.num_parameters():,}", len(tokenizer),
    )
    return model, tokenizer


# ---------------------------------------------------------------------------
# Estágio 1 — prepare_dataset(segment)
# ---------------------------------------------------------------------------


def prepare_dataset(
    segment: str,
    tokenizer,
    max_seq_length: int = 512,
    num_examples: Optional[int] = None,
    dataset_path: Optional[Path] = None,
):
    """Carrega e tokeniza o dataset de um segmento
    (`data/{segment}_finetune_dataset.json`).

    O JSON é uma lista de exemplos `{"instruction", "output"}` (o campo
    `"text"` pré-concatenado é usado quando presente — ver
    data/saneamento_finetune_dataset.json — senão é construído aqui).

    Args:
        segment: um de SUPPORTED_SEGMENTS (ex.: "saneamento").
        tokenizer: tokenizer já carregado (de load_base_model() ou
            build_demo_base_model_and_tokenizer()).
        max_seq_length: tamanho máximo de sequência (truncation+padding).
        num_examples: limita a N exemplos (smoke tests).
        dataset_path: caminho alternativo (default: resolve_dataset_path(segment)).

    Returns:
        datasets.Dataset tokenizado (colunas input_ids/attention_mask/labels).

    Raises:
        FileNotFoundError: se o dataset do segmento ainda não existir.
    """
    from datasets import Dataset

    path = Path(dataset_path) if dataset_path else resolve_dataset_path(segment)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset do segmento {segment!r} não encontrado em {path}. "
            f"Adicione data/{segment}_finetune_dataset.json (ver "
            "data/saneamento_finetune_dataset.json como referência de formato)."
        )

    logger.info("finetuning: carregando dataset de %s", path)
    with open(path, "r", encoding="utf-8") as f:
        raw_examples = json.load(f)

    texts = [
        item.get("text") or f"{item.get('instruction', '')}\n{item.get('output', '')}".strip()
        for item in raw_examples
    ]
    dataset = Dataset.from_dict({"text": texts})

    if num_examples:
        dataset = dataset.select(range(min(num_examples, len(dataset))))

    def _tokenize(batch):
        tokens = tokenizer(
            batch["text"],
            max_length=max_seq_length,
            truncation=True,
            padding="max_length",
        )
        tokens["labels"] = [ids.copy() for ids in tokens["input_ids"]]
        return tokens

    dataset = dataset.map(_tokenize, batched=True, remove_columns=["text"])
    logger.info("finetuning: dataset[%s] preparado — %d exemplos", segment, len(dataset))
    return dataset


# ---------------------------------------------------------------------------
# Estágio 2 — setup do adapter LoRA (peft) + create_trainer(model, adapter, dataset)
# ---------------------------------------------------------------------------


def build_lora_config(adapter: Optional[Union["LoRAAdapterConfig", Dict[str, Any]]] = None):
    """Constrói um `peft.LoraConfig` a partir de LoRAAdapterConfig/dict
    (ou defaults, se `adapter` for None)."""
    from peft import LoraConfig, TaskType

    if adapter is None:
        adapter = LoRAAdapterConfig()
    elif isinstance(adapter, dict):
        adapter = LoRAAdapterConfig(**adapter)

    return LoraConfig(
        r=adapter.r,
        lora_alpha=adapter.lora_alpha,
        target_modules=adapter.target_modules,
        lora_dropout=adapter.lora_dropout,
        bias=adapter.bias,
        task_type=TaskType.CAUSAL_LM,
    )


def apply_lora_adapter(model, adapter: Optional[Union["LoRAAdapterConfig", Dict[str, Any]]] = None):
    """Aplica o adapter LoRA ao modelo base via `peft.get_peft_model`
    (no-op — devolve `model` como está — se já for um `PeftModel`)."""
    from peft import PeftModel, get_peft_model

    if isinstance(model, PeftModel):
        logger.info("finetuning: modelo já é um PeftModel, pulando get_peft_model()")
        return model

    lora_config = build_lora_config(adapter)
    logger.info("finetuning: aplicando LoRA — r=%d alpha=%d targets=%s", lora_config.r, lora_config.lora_alpha, lora_config.target_modules)
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def create_trainer(
    model,
    adapter: Optional[Union["LoRAAdapterConfig", Dict[str, Any]]],
    dataset,
    tokenizer,
    training_config: Optional[TrainingConfig] = None,
    output_dir: Optional[Path] = None,
):
    """Estágio 2 da pipeline: aplica `adapter` (LoRA) ao `model` (se
    ainda não aplicado) e monta o `transformers.Trainer` pronto para
    `train()`.

    Args:
        model: modelo base (de load_base_model() / build_demo_base_model_and_tokenizer()).
        adapter: LoRAAdapterConfig (ou dict/None para defaults) — configura o adapter LoRA.
        dataset: Dataset tokenizado (de prepare_dataset()).
        tokenizer: tokenizer correspondente ao modelo/dataset.
        training_config: hiperparâmetros de treino (default: TrainingConfig()).
        output_dir: diretório de checkpoints (default: ML_DIR/adapters/_trainer_tmp).

    Returns:
        transformers.Trainer
    """
    from transformers import DataCollatorForLanguageModeling, Trainer, TrainingArguments

    model = apply_lora_adapter(model, adapter)

    cfg = training_config or TrainingConfig()
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR / "_trainer_tmp"
    out_dir.mkdir(parents=True, exist_ok=True)

    if cfg.validation_split > 0 and len(dataset) >= 4:
        split = dataset.train_test_split(test_size=cfg.validation_split, seed=42)
        train_dataset, eval_dataset = split["train"], split["test"]
    else:
        train_dataset, eval_dataset = dataset, None

    import torch

    training_args = TrainingArguments(
        output_dir=str(out_dir),
        overwrite_output_dir=True,
        num_train_epochs=cfg.num_epochs,
        max_steps=cfg.max_steps,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        learning_rate=cfg.learning_rate,
        warmup_steps=cfg.warmup_steps,
        weight_decay=cfg.weight_decay,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        logging_steps=cfg.logging_steps,
        logging_dir=str(out_dir / "logs"),
        save_strategy="no",  # o adapter é salvo explicitamente via save_adapter()
        eval_strategy="steps" if eval_dataset else "no",
        eval_steps=cfg.eval_steps if eval_dataset else None,
        lr_scheduler_type=cfg.lr_scheduler_type,
        optim=cfg.optim,
        bf16=torch.cuda.is_available(),
        report_to=[],  # sem wandb/tensorboard por padrão (evita I/O extra em CI/demo)
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    return trainer


# ---------------------------------------------------------------------------
# Estágio 3 — train()
# ---------------------------------------------------------------------------


def train(
    trainer,
    segment: str = "unknown",
    base_model_name: str = DEFAULT_BASE_MODEL,
) -> TrainingMetrics:
    """Estágio 3 da pipeline: roda `trainer.train()`, avalia (se houver
    eval_dataset) e devolve as métricas coletadas.

    Args:
        trainer: transformers.Trainer (de create_trainer()).
        segment: rótulo do segmento (só para as métricas/registro).
        base_model_name: rótulo do modelo base (só para as métricas/registro).

    Returns:
        TrainingMetrics
    """
    import math

    logger.info("finetuning: iniciando treino (segment=%s, base_model=%s)", segment, base_model_name)
    start = time.time()
    result = trainer.train()
    elapsed = time.time() - start

    eval_metrics = trainer.evaluate() if trainer.eval_dataset is not None else {}
    eval_loss = eval_metrics.get("eval_loss", result.training_loss)
    try:
        perplexity = math.exp(eval_loss) if eval_loss < 20 else float("inf")
    except (OverflowError, ValueError):
        perplexity = float("inf")

    metrics = TrainingMetrics(
        segment=segment,
        base_model=base_model_name,
        loss=float(result.training_loss),
        perplexity=float(perplexity),
        epoch=float(result.metrics.get("epoch", 0.0)),
        num_train_steps=int(result.global_step),
        learning_rate=float(trainer.args.learning_rate),
        total_time_seconds=elapsed,
    )
    logger.info("finetuning: treino concluído — %s", asdict(metrics))
    return metrics


# ---------------------------------------------------------------------------
# Estágio 4 — save_adapter(model, path)
# ---------------------------------------------------------------------------


def save_adapter(
    model,
    path: Union[str, Path],
    tokenizer=None,
    metrics: Optional[TrainingMetrics] = None,
) -> str:
    """Estágio 4 da pipeline: salva SÓ o adapter LoRA (poucos MB — o
    peso base do modelo não é reescrito) + tokenizer + metrics.json.

    Args:
        model: PeftModel treinado (de create_trainer()/train()).
        path: diretório de destino.
        tokenizer: se fornecido, também é salvo em `path` (necessário
            para load_adapter() poder gerar texto sem redownload).
        metrics: se fornecido, gravado em `path/metrics.json`.

    Returns:
        `str(path)` — o caminho onde o adapter foi salvo.
    """
    out_path = Path(path)
    out_path.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(str(out_path))
    if tokenizer is not None:
        tokenizer.save_pretrained(str(out_path))

    if metrics is not None:
        with open(out_path / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)

    logger.info("finetuning: adapter salvo em %s", out_path)
    return str(out_path)


# ---------------------------------------------------------------------------
# Estágio 5 — load_adapter(path)
# ---------------------------------------------------------------------------


def load_adapter(
    path: Union[str, Path],
    base_model=None,
    base_model_name: Optional[str] = None,
    use_quantization: bool = False,
    hf_token: Optional[str] = None,
):
    """Estágio 5 da pipeline: carrega um adapter LoRA previamente salvo
    (via save_adapter()) e devolve o modelo pronto para `generate()`.

    Args:
        path: diretório do adapter (o que save_adapter() devolveu).
        base_model: modelo base já carregado (pula load_base_model() se fornecido —
            útil para reaproveitar um modelo já em memória).
        base_model_name: nome do modelo base a carregar se `base_model`
            for None (default: lê `adapter_config.json["base_model_name_or_path"]`
            gravado pelo peft dentro de `path`).
        use_quantization: repassado a load_base_model() se precisar carregar o base.
        hf_token: repassado a load_base_model().

    Returns:
        PeftModel (adapter + base) pronto para inferência.
    """
    import os

    from peft import PeftModel

    adapter_path = Path(path)
    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter não encontrado em: {adapter_path}")

    adapter_config_file = adapter_path / "adapter_config.json"
    recorded_base_name = None
    if adapter_config_file.exists():
        with open(adapter_config_file, "r", encoding="utf-8") as f:
            recorded_base_name = json.load(f).get("base_model_name_or_path")

    is_demo_adapter = recorded_base_name == DEMO_BASE_MODEL_NAME

    if base_model is None:
        if is_demo_adapter:
            raise ValueError(
                "Adapter foi treinado em modo demo (demo-tiny-gpt2-offline) — "
                "passe `base_model=` explicitamente (o modelo demo não é "
                "recarregável do Hub, precisa ser reconstruído em memória, "
                "ver build_demo_base_model_and_tokenizer())."
            )
        resolved_name = base_model_name or recorded_base_name or DEFAULT_BASE_MODEL
        base_model, _ = load_base_model(
            resolved_name, use_quantization=use_quantization, hf_token=hf_token
        )

    logger.info("finetuning: carregando adapter de %s", adapter_path)
    # `base_model_name_or_path` de um adapter demo não é um repo real do
    # HF Hub — sem HF_HUB_OFFLINE, PeftModel.from_pretrained ainda tenta
    # um HEAD remoto para checar arquivos extras (config.json) antes de
    # desistir, gastando ~30s em retries contra o proxy neste sandbox
    # sem egress. Força modo offline só para esta chamada quando for
    # claramente um adapter demo (evita esse custo sem afetar o
    # carregamento de adapters reais, que precisam do Hub disponível).
    previous_offline_flag = os.environ.get("HF_HUB_OFFLINE")
    if is_demo_adapter:
        os.environ["HF_HUB_OFFLINE"] = "1"
    try:
        model = PeftModel.from_pretrained(base_model, str(adapter_path))
    finally:
        if is_demo_adapter:
            if previous_offline_flag is None:
                os.environ.pop("HF_HUB_OFFLINE", None)
            else:
                os.environ["HF_HUB_OFFLINE"] = previous_offline_flag
    return model


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 128, temperature: float = 0.7) -> str:
    """Helper de inferência — gera texto com o modelo (base ou +adapter)."""
    import torch

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.pad_token_id,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# ---------------------------------------------------------------------------
# Orquestrador de alto nível — usado pelo endpoint POST /ml/finetune e pelo CLI
# ---------------------------------------------------------------------------


@dataclass
class FineTuneResult:
    segment: str
    base_model: str
    adapter_path: str
    metrics: TrainingMetrics


def run_finetuning_pipeline(
    segment: str,
    epochs: Optional[int] = None,
    base_model_name: Optional[str] = None,
    output_dir: Optional[Path] = None,
    use_quantization: bool = True,
    lora_config: Optional[LoRAAdapterConfig] = None,
    hf_token: Optional[str] = None,
    max_examples: Optional[int] = None,
    demo_mode: bool = False,
) -> FineTuneResult:
    """Roda a pipeline completa (load_base_model/demo → prepare_dataset →
    create_trainer → train → save_adapter) para um segmento e devolve o
    resultado. É esta função que o endpoint POST /ml/finetune dispara em
    background e que o CLI (`python -m ml.finetuning run`) chama.

    Args:
        segment: um de SUPPORTED_SEGMENTS.
        epochs: sobrescreve `num_epochs` do fine_tune_config.yaml (obrigatório
            vindo do payload da API — POST /ml/finetune {segment, epochs}).
        base_model_name: default DEFAULT_BASE_MODEL (ignorado se demo_mode=True).
        output_dir: default ML_DIR/adapters/{segment}_adapter_{timestamp}.
        use_quantization: repassado a load_base_model() (ignorado em demo_mode).
        lora_config: sobrescreve o LoRA do fine_tune_config.yaml.
        hf_token: repassado a load_base_model().
        max_examples: limita o dataset (smoke tests).
        demo_mode: usa build_demo_base_model_and_tokenizer() em vez do
            Mistral-7B real — ver docstring do módulo.

    Returns:
        FineTuneResult (adapter_path + métricas)
    """
    if segment not in SUPPORTED_SEGMENTS:
        raise ValueError(f"Segmento desconhecido: {segment!r}. Use um de {SUPPORTED_SEGMENTS}")

    segment_cfg = load_segment_config(segment)
    training_cfg = _training_config_from_dict(segment_cfg)
    if epochs is not None:
        training_cfg.num_epochs = epochs
    adapter_cfg = lora_config or _lora_config_from_dict(segment_cfg)

    resolved_base_model = DEMO_BASE_MODEL_NAME if demo_mode else (base_model_name or segment_cfg.get("base_model", DEFAULT_BASE_MODEL))

    if demo_mode:
        dataset_path = resolve_dataset_path(segment)
        with open(dataset_path, "r", encoding="utf-8") as f:
            raw_examples = json.load(f)
        demo_texts = [item.get("text", "") for item in raw_examples]

        model, tokenizer = build_demo_base_model_and_tokenizer(demo_texts)
        adapter_cfg = LoRAAdapterConfig(
            r=adapter_cfg.r,
            lora_alpha=adapter_cfg.lora_alpha,
            target_modules=["c_attn"],  # arquitetura GPT-2 (Conv1D), não q_proj/v_proj
            lora_dropout=adapter_cfg.lora_dropout,
            bias=adapter_cfg.bias,
        )
        training_cfg.max_seq_length = min(training_cfg.max_seq_length, 64)
        training_cfg.batch_size = min(training_cfg.batch_size, 2)
    else:
        model, tokenizer = load_base_model(
            resolved_base_model, use_quantization=use_quantization, hf_token=hf_token
        )

    dataset = prepare_dataset(
        segment, tokenizer, max_seq_length=training_cfg.max_seq_length, num_examples=max_examples
    )

    out_dir = (
        Path(output_dir)
        if output_dir
        else DEFAULT_OUTPUT_DIR / f"{segment}_adapter_{int(time.time())}"
    )

    trainer = create_trainer(
        model, adapter_cfg, dataset, tokenizer, training_config=training_cfg, output_dir=out_dir / "_checkpoints"
    )
    metrics = train(trainer, segment=segment, base_model_name=resolved_base_model)
    adapter_path = save_adapter(trainer.model, out_dir, tokenizer=tokenizer, metrics=metrics)

    return FineTuneResult(
        segment=segment, base_model=resolved_base_model, adapter_path=adapter_path, metrics=metrics
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_run(args) -> None:
    result = run_finetuning_pipeline(
        segment=args.segment,
        epochs=args.epochs,
        base_model_name=args.base_model,
        use_quantization=not args.no_quantization,
        demo_mode=args.demo,
        max_examples=args.max_examples,
    )
    print("=" * 70)
    print(f"Segmento:      {result.segment}")
    print(f"Base model:    {result.base_model}")
    print(f"Adapter salvo: {result.adapter_path}")
    print(f"Loss:          {result.metrics.loss:.4f}")
    print(f"Perplexity:    {result.metrics.perplexity:.4f}")
    print(f"Steps:         {result.metrics.num_train_steps}")
    print(f"Tempo (s):     {result.metrics.total_time_seconds:.1f}")
    print("=" * 70)


def main() -> int:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Manta — fine-tuning LoRA por segmento")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Roda a pipeline completa de fine-tuning para um segmento")
    run_parser.add_argument("--segment", required=True, choices=SUPPORTED_SEGMENTS)
    run_parser.add_argument("--epochs", type=int, default=None)
    run_parser.add_argument("--base-model", default=None)
    run_parser.add_argument("--no-quantization", action="store_true")
    run_parser.add_argument("--max-examples", type=int, default=None)
    run_parser.add_argument(
        "--demo", action="store_true",
        help="Modo offline: GPT-2 minúsculo construído do zero, sem GPU/rede (ver docstring do módulo)",
    )
    run_parser.set_defaults(func=_cli_run)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
