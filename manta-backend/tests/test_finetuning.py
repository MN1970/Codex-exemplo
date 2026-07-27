"""
tests/test_finetuning.py — Suíte de `ml/lora_finetuner.py` (LoRA/QLoRA
fine-tuning dos adapters de segmento: saneamento, energia, portos,
aeroportos, barragens).

Roda 100% offline/CPU, sem baixar nenhum modelo real (Mistral-7B etc.):

  - Um tokenizer BPE minúsculo é TREINADO na hora (via `tokenizers`,
    biblioteca já usada internamente por `transformers`) a partir de um
    corpus local de ~8 frases — sem tocar em huggingface.co.
  - Um GPT2LMHeadModel minúsculo (poucas camadas/dimensões) é
    construído a partir de um `GPT2Config` do zero (pesos aleatórios,
    nunca `from_pretrained`) — mesma família de arquitetura (causal LM)
    que `LoRAFinetuner` foi escrito para treinar, só que pequeno o
    bastante para rodar em CPU em segundos.
  - `bitsandbytes` (quantização 4-bit / `paged_adamw_32bit`) não está
    instalado neste ambiente de CI/sandbox — `TrainingArguments` é
    interceptado por uma subclasse fina só para trocar o optimizer por
    `adamw_torch` e desligar fp16/bf16 (ambos frágeis em CPU puro sem
    hardware dedicado). O restante do pipeline (tokenização, LoRA via
    peft, `Trainer.train()`, cálculo de métricas) roda EXATAMENTE como
    em produção.

O que é validado, ligado aos requisitos do ticket:
  - "training roda sem erros": `LoRAFinetuner.train()` completa sem
    levantar exceção, ponta a ponta, sobre um dataset e modelo reais
    (não mockado) — inclusive salva o adapter em disco.
  - "training loss diminui": a loss média do último terço dos passos de
    treino (capturados via `trainer.state.log_history`) é estritamente
    menor que a do primeiro terço, no mesmo `train()` — não duas
    chamadas separadas, então a comparação é livre de variância entre
    runs.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import pytest
import torch
from tokenizers import ByteLevelBPETokenizer
from transformers import GPT2Config, GPT2LMHeadModel, GPT2TokenizerFast, Trainer, TrainingArguments

import ml.lora_finetuner as lora_finetuner_module
from ml.lora_finetuner import LoRAConfig, LoRAFinetuner, TrainingMetrics

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Corpus minúsculo de domínio (saneamento) usado só para treinar o BPE
# tokenizer local e alimentar o dataset de fine-tuning do teste — não
# tem relação com nenhum modelo real baixado da rede.
TINY_CORPUS = [
    "ETA e ETE tratam agua e esgoto conforme normas SNIS",
    "adutora leva agua bruta ate a estacao de tratamento",
    "drenagem urbana evita alagamentos nas cidades",
    "rede coletora de esgoto segue a NBR 9649",
    "lodo ativado remove materia organica no tratamento secundario",
    "reservatorio de agua potavel precisa de manutencao regular",
    "outorga de uso da agua e exigida pela ANA",
    "perdas de agua na distribuicao reduzem eficiencia do sistema",
]


# ---------------------------------------------------------------------------
# Helpers — tokenizer/modelo minúsculos e 100% offline
# ---------------------------------------------------------------------------


def _build_tiny_tokenizer(tok_dir: Path) -> GPT2TokenizerFast:
    """Treina um ByteLevelBPE tokenizer na hora a partir de TINY_CORPUS
    (nenhum download — `train_from_iterator` roda inteiramente local) e
    o recarrega como GPT2TokenizerFast a partir do diretório local."""
    tok_dir.mkdir(parents=True, exist_ok=True)
    bpe = ByteLevelBPETokenizer()
    bpe.train_from_iterator(TINY_CORPUS, vocab_size=100, min_frequency=1, special_tokens=["<|endoftext|>"])
    bpe.save_model(str(tok_dir))

    tokenizer = GPT2TokenizerFast.from_pretrained(str(tok_dir))
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def _build_tiny_causal_lm(vocab_size: int) -> GPT2LMHeadModel:
    """GPT2LMHeadModel minúsculo com pesos aleatórios (sem from_pretrained,
    sem rede) — usado como substituto do modelo real (Mistral-7B) só para
    exercitar a mecânica de LoRAFinetuner.train() em CPU."""
    config = GPT2Config(
        vocab_size=vocab_size,
        n_positions=512,  # tem que cobrir max_seq_length default (512) do prepare_dataset
        n_ctx=512,
        n_embd=16,
        n_layer=2,
        n_head=2,
    )
    return GPT2LMHeadModel(config)


class _CPUSafeTrainingArguments(TrainingArguments):
    """`ml.lora_finetuner.train()` monta `TrainingArguments` com
    `optim="paged_adamw_32bit"` e fp16/bf16 sempre ligado (um dos dois) —
    dependências de `bitsandbytes`/hardware que não existem neste
    ambiente de CPU puro. Esta subclasse fina troca só esses três campos
    por equivalentes CPU-friendly; todo o resto do pipeline (LoRA,
    tokenização, loop de treino do Trainer) roda sem mais nenhuma
    alteração."""

    def __init__(self, *args, **kwargs):
        kwargs["fp16"] = False
        kwargs["bf16"] = False
        if kwargs.get("optim") == "paged_adamw_32bit":
            kwargs["optim"] = "adamw_torch"
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="module")
def module_monkeypatch():
    """`monkeypatch` builtin fixture is function-scoped only — este
    wrapper dá um `MonkeyPatch` com escopo de módulo para que
    `capturing_trainer`/`tiny_finetuner` (que também precisam ser
    module-scoped, para `train()` rodar uma única vez para todo o
    arquivo) possam usá-lo e desfazer o patch ao final do módulo."""
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="module")
def capturing_trainer(module_monkeypatch):
    """Monkeypatcha `Trainer`/`TrainingArguments` dentro do módulo
    ml.lora_finetuner e devolve a lista (mutável) de instâncias de
    Trainer criadas — permite inspecionar `trainer.state.log_history`
    depois que `finetuner.train()` retorna, sem o método `train()`
    precisar expor o Trainer internamente."""
    captured: list[Trainer] = []

    class _CapturingTrainer(Trainer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            captured.append(self)

    module_monkeypatch.setattr(lora_finetuner_module, "TrainingArguments", _CPUSafeTrainingArguments)
    module_monkeypatch.setattr(lora_finetuner_module, "Trainer", _CapturingTrainer)
    return captured


@pytest.fixture(scope="module")
def tiny_finetuner(tmp_path_factory) -> LoRAFinetuner:
    """LoRAFinetuner com modelo/tokenizer minúsculos já atribuídos
    diretamente (bypassa `load_model_and_tokenizer()`, que baixaria um
    modelo real da rede) — `use_quantization=True` só para o cálculo
    interno de precisão em `train()`; nenhuma quantização de fato ocorre
    porque `load_model_and_tokenizer()`/`_load_quantization_config()`
    nunca são chamados neste fluxo de teste."""
    base_dir = tmp_path_factory.mktemp("lora_finetuner")
    tokenizer = _build_tiny_tokenizer(base_dir / "tok")
    model = _build_tiny_causal_lm(vocab_size=len(tokenizer))

    finetuner = LoRAFinetuner(
        base_model_name="tiny-offline-gpt2-test",
        output_dir=str(base_dir / "adapters"),
        segment="saneamento",
        use_quantization=True,
    )
    finetuner.model = model
    finetuner.tokenizer = tokenizer
    return finetuner


@pytest.fixture(scope="module")
def tiny_dataset_path(tmp_path_factory) -> str:
    data = [{"instruction": sentence, "output": ""} for sentence in TINY_CORPUS]
    path = tmp_path_factory.mktemp("lora_finetuner_data") / "tiny_dataset.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# LoRAConfig / TrainingMetrics — dataclasses puras (sem I/O nem torch)
# ---------------------------------------------------------------------------


def test_lora_config_defaults_to_q_proj_v_proj_when_target_modules_omitted():
    config = LoRAConfig()
    assert config.target_modules == ["q_proj", "v_proj"]
    assert config.r == 8
    assert config.lora_alpha == 16
    assert config.bias == "none"
    assert config.task_type == "CAUSAL_LM"


def test_lora_config_respects_explicit_target_modules():
    config = LoRAConfig(target_modules=["c_attn"])
    assert config.target_modules == ["c_attn"]


def test_training_metrics_asdict_contains_all_fields():
    metrics = TrainingMetrics(
        segment="saneamento",
        base_model="tiny-offline-gpt2-test",
        loss=1.23,
        perplexity=3.4,
        epoch=3,
        num_train_steps=42,
        learning_rate=2e-4,
        total_time_seconds=12.5,
    )
    data = asdict(metrics)
    assert data == {
        "segment": "saneamento",
        "base_model": "tiny-offline-gpt2-test",
        "loss": 1.23,
        "perplexity": 3.4,
        "epoch": 3,
        "num_train_steps": 42,
        "learning_rate": 2e-4,
        "total_time_seconds": 12.5,
    }


# ---------------------------------------------------------------------------
# LoRAFinetuner — inicialização e guard clauses
# ---------------------------------------------------------------------------


def test_finetuner_init_creates_output_and_adapter_paths(tmp_path):
    finetuner = LoRAFinetuner(output_dir=str(tmp_path / "out"), segment="energia")
    assert Path(finetuner.output_dir).is_dir()
    assert finetuner.adapter_path == Path(finetuner.output_dir) / "energia_adapter"


def test_apply_lora_config_raises_if_model_not_loaded(tmp_path):
    finetuner = LoRAFinetuner(output_dir=str(tmp_path / "out"), segment="portos")
    with pytest.raises(ValueError, match="Model not loaded"):
        finetuner.apply_lora_config()


def test_generate_raises_if_model_not_loaded(tmp_path):
    finetuner = LoRAFinetuner(output_dir=str(tmp_path / "out"), segment="portos")
    with pytest.raises(ValueError, match="Model not loaded"):
        finetuner.generate("qualquer prompt")


def test_save_metrics_raises_if_no_training_happened_yet(tmp_path):
    finetuner = LoRAFinetuner(output_dir=str(tmp_path / "out"), segment="aeroportos")
    with pytest.raises(ValueError, match="No metrics available"):
        finetuner.save_metrics()


def test_train_raises_if_model_not_loaded(tmp_path):
    finetuner = LoRAFinetuner(output_dir=str(tmp_path / "out"), segment="barragens")
    with pytest.raises(ValueError, match="Model not loaded"):
        finetuner.train(dataset_path="qualquer_coisa.json")


def test_prepare_dataset_loads_via_datasets_library_for_non_json_path(tiny_finetuner, monkeypatch):
    """`prepare_dataset` só usa o branch `json.load` quando o path termina
    em `.json`; qualquer outro path (ex.: nome de dataset do HF Hub) cai
    no branch `load_dataset(...)`. Mocka `load_dataset` para cobrir esse
    branch sem precisar de rede."""
    from datasets import Dataset

    fake_dataset = Dataset.from_dict({"text": [f"{s}\n" for s in TINY_CORPUS]})

    def _fake_load_dataset(path, split="train"):
        assert split == "train"
        return fake_dataset

    monkeypatch.setattr(lora_finetuner_module, "load_dataset", _fake_load_dataset)

    dataset = tiny_finetuner.prepare_dataset("nome-generico-de-dataset-no-hf-hub", max_seq_length=32)
    assert len(dataset) == len(TINY_CORPUS)
    assert "input_ids" in dataset.column_names


# ---------------------------------------------------------------------------
# prepare_dataset — tokenização (sem precisar rodar o Trainer)
# ---------------------------------------------------------------------------


def test_prepare_dataset_builds_input_ids_and_labels(tiny_finetuner, tiny_dataset_path):
    dataset = tiny_finetuner.prepare_dataset(tiny_dataset_path, max_seq_length=32)

    assert len(dataset) == len(TINY_CORPUS)
    assert "input_ids" in dataset.column_names
    assert "attention_mask" in dataset.column_names
    assert "labels" in dataset.column_names

    first = dataset[0]
    assert len(first["input_ids"]) == 32  # padding="max_length"
    assert first["labels"] == first["input_ids"]  # tokenize_fn copia input_ids -> labels


def test_prepare_dataset_respects_num_examples_limit(tiny_finetuner, tiny_dataset_path):
    dataset = tiny_finetuner.prepare_dataset(tiny_dataset_path, max_seq_length=32, num_examples=3)
    assert len(dataset) == 3


# ---------------------------------------------------------------------------
# train() — execução real ponta a ponta (modelo/tokenizer minúsculos)
# ---------------------------------------------------------------------------


NUM_EPOCHS = 60
BATCH_SIZE = 2
# 8 exemplos / batch_size=2 = 4 steps/epoch — puramente aritmético,
# determinístico independente de qualquer seed.
EXPECTED_STEPS = (len(TINY_CORPUS) // BATCH_SIZE) * NUM_EPOCHS


@pytest.fixture(scope="module")
def trained_tiny_result(tiny_finetuner, tiny_dataset_path, capturing_trainer):
    """Roda LoRAFinetuner.train() de ponta a ponta (LoRA real via peft,
    Trainer real, sem mocks no caminho de treino em si) e devolve
    (finetuner, metrics, captured_trainers) para os testes abaixo
    reaproveitarem sem re-treinar."""
    torch.manual_seed(42)

    tiny_finetuner.apply_lora_config(
        LoRAConfig(r=8, lora_alpha=16, target_modules=["c_attn", "wte"], lora_dropout=0.0)
    )

    metrics = tiny_finetuner.train(
        dataset_path=tiny_dataset_path,
        learning_rate=5e-2,
        batch_size=BATCH_SIZE,
        num_epochs=NUM_EPOCHS,
        warmup_steps=0,
        logging_steps=1,
        save_steps=1_000_000,  # não interessa checkpoint intermediário neste teste
        eval_steps=1_000_000,
        gradient_accumulation_steps=1,
        validation_split=0.0,  # sem holdout -> sem overhead de eval, mais rápido
    )
    return tiny_finetuner, metrics, capturing_trainer


def test_train_runs_without_errors_and_returns_training_metrics(trained_tiny_result):
    _finetuner, metrics, _captured = trained_tiny_result

    assert isinstance(metrics, TrainingMetrics)
    assert metrics.segment == "saneamento"
    assert metrics.base_model == "tiny-offline-gpt2-test"
    assert metrics.epoch == NUM_EPOCHS
    assert metrics.learning_rate == 5e-2
    assert metrics.num_train_steps == EXPECTED_STEPS

    assert math.isfinite(metrics.loss) and metrics.loss > 0
    assert math.isfinite(metrics.perplexity) and metrics.perplexity > 0
    # total_time_seconds vem de train_result.metrics["train_runtime"] —
    # regressão direta do bug corrigido em ml/lora_finetuner.py (o
    # `TrainOutput` do transformers não tem atributo
    # `training_time_in_seconds`; usar isso quebrava train() com
    # AttributeError em toda chamada real).
    assert metrics.total_time_seconds > 0


def test_train_saves_lora_adapter_to_disk(trained_tiny_result):
    finetuner, _metrics, _captured = trained_tiny_result
    assert finetuner.adapter_path.exists()
    assert (finetuner.adapter_path / "adapter_config.json").exists()
    assert any(finetuner.adapter_path.glob("adapter_model.*"))


def test_train_loss_decreases_over_the_run(trained_tiny_result):
    """'training loss diminui' — compara a loss média do primeiro terço
    dos passos logados com a do último terço, dentro do MESMO `train()`
    (não duas chamadas separadas), eliminando variância entre runs."""
    _finetuner, _metrics, captured = trained_tiny_result
    trainer = captured[-1]

    losses = [entry["loss"] for entry in trainer.state.log_history if "loss" in entry]
    assert len(losses) >= 10  # logging_steps=1 -> ~EXPECTED_STEPS entradas

    third = len(losses) // 3
    first_avg = sum(losses[:third]) / third
    last_avg = sum(losses[-third:]) / third

    assert last_avg < first_avg, (
        f"loss não caiu: primeiro terço avg={first_avg:.4f}, último terço avg={last_avg:.4f}"
    )


def test_save_metrics_writes_json_matching_training_metrics(trained_tiny_result):
    finetuner, metrics, _captured = trained_tiny_result
    metrics_path = finetuner.save_metrics()

    assert Path(metrics_path).exists()
    saved = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
    assert saved == asdict(metrics)


def test_generate_produces_text_after_training(trained_tiny_result):
    finetuner, _metrics, _captured = trained_tiny_result
    output = finetuner.generate("agua e esgoto", max_tokens=8)
    assert isinstance(output, str) and len(output) > 0


def test_load_adapter_loads_saved_peft_adapter_onto_fresh_base_model(trained_tiny_result, tmp_path):
    """Simula o caso de uso real de `load_adapter`: um processo separado
    (ex.: servindo inferência) carrega um modelo base do zero e aplica o
    adapter LoRA já treinado/salvo por outro processo — aqui, o adapter
    salvo por `trained_tiny_result`."""
    finetuner, _metrics, _captured = trained_tiny_result

    fresh_model = _build_tiny_causal_lm(vocab_size=len(finetuner.tokenizer))
    loader = LoRAFinetuner(output_dir=str(tmp_path / "loader_out"), segment="saneamento")
    loader.model = fresh_model
    loader.tokenizer = finetuner.tokenizer

    loaded_model = loader.load_adapter(str(finetuner.adapter_path))

    assert loaded_model is loader.model
    assert type(loaded_model).__name__ == "PeftModelForCausalLM"


@pytest.fixture
def finetuner_with_eval_split(tmp_path):
    """Setup independente (não reaproveita `tiny_finetuner`/`trained_tiny_result`,
    que ficam com o modelo já LoRA-wrapped e sem holdout) só para exercitar
    o branch `validation_split > 0` de `train()` — poucas épocas, propositalmente
    rápido, esta asserção é só 'roda sem erro', não métrica de loss."""
    tokenizer = _build_tiny_tokenizer(tmp_path / "tok")
    model = _build_tiny_causal_lm(vocab_size=len(tokenizer))
    finetuner = LoRAFinetuner(
        base_model_name="tiny-offline-gpt2-test",
        output_dir=str(tmp_path / "adapters"),
        segment="energia",
        use_quantization=True,
    )
    finetuner.model = model
    finetuner.tokenizer = tokenizer
    finetuner.apply_lora_config(LoRAConfig(r=4, lora_alpha=8, target_modules=["c_attn"], lora_dropout=0.0))
    return finetuner


def test_train_with_validation_split_runs_eval_branch_without_errors(
    finetuner_with_eval_split, tiny_dataset_path, capturing_trainer
):
    metrics = finetuner_with_eval_split.train(
        dataset_path=tiny_dataset_path,
        learning_rate=5e-2,
        batch_size=2,
        num_epochs=2,
        warmup_steps=0,
        logging_steps=1,
        save_steps=1_000_000,
        eval_steps=1,
        validation_split=0.25,  # 8 exemplos -> 6 treino / 2 eval (branch train_test_split)
    )
    assert isinstance(metrics, TrainingMetrics)
    assert math.isfinite(metrics.loss)
    assert math.isfinite(metrics.perplexity)


# ---------------------------------------------------------------------------
# Synthetic datasets — 10 exemplos/segmento (data/*_finetune_dataset.json)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("segment", ["saneamento", "energia", "portos", "aeroportos", "barragens"])
def test_segment_finetune_dataset_has_at_least_10_well_formed_examples(segment):
    path = DATA_DIR / f"{segment}_finetune_dataset.json"
    assert path.exists(), f"dataset sintético ausente para o segmento {segment!r}: {path}"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 10, f"segmento {segment!r} tem só {len(data)} exemplo(s), esperado >= 10"

    for item in data:
        assert isinstance(item, dict)
        assert item.get("instruction", "").strip(), f"exemplo sem 'instruction' em {segment}"
        assert item.get("output", "").strip(), f"exemplo sem 'output' em {segment}"
