"""
LoRA Fine-tuner for Manta segments (saneamento, energia, portos, etc).

Wrapper around transformers + peft for QLoRA fine-tuning on base models
(Mistral-7B, Llama 2, etc). Saves adapter weights locally and tracks metrics.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset, load_dataset
from huggingface_hub import login as hf_login

logger = logging.getLogger(__name__)


@dataclass
class LoRAConfig:
    """LoRA configuration for fine-tuning."""
    r: int = 8
    lora_alpha: int = 16
    target_modules: list = None
    lora_dropout: float = 0.05
    bias: str = "none"
    task_type: str = "CAUSAL_LM"

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "v_proj"]


@dataclass
class TrainingMetrics:
    """Training metrics collected during fine-tuning."""
    segment: str
    base_model: str
    loss: float
    perplexity: float
    epoch: int
    num_train_steps: int
    learning_rate: float
    total_time_seconds: float


class LoRAFinetuner:
    """
    Fine-tunes a base model with LoRA on domain-specific data.
    Supports QLoRA (quantization + LoRA) for memory-efficient training.
    """

    def __init__(
        self,
        base_model_name: str = "mistralai/Mistral-7B-v0.1",
        output_dir: str = "./lora_adapters",
        segment: str = "saneamento",
        use_quantization: bool = True,
        hf_token: Optional[str] = None,
    ):
        """
        Initialize LoRA fine-tuner.

        Args:
            base_model_name: HuggingFace model ID (e.g., mistralai/Mistral-7B-v0.1)
            output_dir: Directory to save adapter weights
            segment: Domain segment (saneamento, energia, portos, etc)
            use_quantization: Use 4-bit quantization (QLoRA) to save memory
            hf_token: HuggingFace API token for private models
        """
        self.base_model_name = base_model_name
        self.output_dir = Path(output_dir)
        self.segment = segment
        self.use_quantization = use_quantization
        self.hf_token = hf_token

        if self.hf_token:
            hf_login(token=self.hf_token)

        self.model = None
        self.tokenizer = None
        self.metrics = None

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.adapter_path = self.output_dir / f"{segment}_adapter"

        logger.info(
            f"Initialized LoRAFinetuner for segment={segment}, "
            f"base_model={base_model_name}"
        )

    def _load_quantization_config(self) -> BitsAndBytesConfig:
        """Load 4-bit quantization config for QLoRA."""
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

    def load_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """
        Load base model and tokenizer from HuggingFace.

        Returns:
            Tuple of (model, tokenizer)
        """
        logger.info(f"Loading model: {self.base_model_name}")

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_name,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Model with optional quantization
        model_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16,
            "device_map": "auto",
        }

        if self.use_quantization:
            model_kwargs["quantization_config"] = self._load_quantization_config()
            logger.info("Using 4-bit quantization (QLoRA)")

        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            **model_kwargs,
        )

        logger.info("Model and tokenizer loaded successfully")
        return self.model, self.tokenizer

    def apply_lora_config(self, lora_config: Optional[LoRAConfig] = None) -> None:
        """
        Apply LoRA configuration to the model.

        Args:
            lora_config: LoRA configuration (uses defaults if None)
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model_and_tokenizer() first.")

        if lora_config is None:
            lora_config = LoRAConfig()

        logger.info(f"Applying LoRA config: {asdict(lora_config)}")

        peft_config = LoraConfig(
            r=lora_config.r,
            lora_alpha=lora_config.lora_alpha,
            target_modules=lora_config.target_modules,
            lora_dropout=lora_config.lora_dropout,
            bias=lora_config.bias,
            task_type=TaskType.CAUSAL_LM,
        )

        self.model = get_peft_model(self.model, peft_config)
        self.model.print_trainable_parameters()

    def prepare_dataset(
        self,
        dataset_path: str,
        max_seq_length: int = 512,
        num_examples: Optional[int] = None,
    ) -> Dataset:
        """
        Prepare dataset for fine-tuning.

        Args:
            dataset_path: Path to JSON/CSV dataset or HuggingFace dataset name
            max_seq_length: Maximum sequence length for tokenization
            num_examples: Limit to N examples (for testing)

        Returns:
            Tokenized Dataset
        """
        logger.info(f"Loading dataset from: {dataset_path}")

        # Load dataset
        if dataset_path.endswith(".json"):
            with open(dataset_path) as f:
                data = json.load(f)
            dataset = Dataset.from_dict({
                "text": [
                    f"{item.get('instruction', '')}\n{item.get('output', '')}"
                    for item in data
                ]
            })
        else:
            dataset = load_dataset(dataset_path, split="train")

        if num_examples:
            dataset = dataset.select(range(min(num_examples, len(dataset))))

        # Tokenize
        def tokenize_fn(example):
            tokens = self.tokenizer(
                example["text"],
                max_length=max_seq_length,
                truncation=True,
                padding="max_length",
            )
            tokens["labels"] = tokens["input_ids"].copy()
            return tokens

        dataset = dataset.map(tokenize_fn, batched=True, remove_columns=["text"])
        logger.info(f"Dataset prepared: {len(dataset)} examples")
        return dataset

    def train(
        self,
        dataset_path: str,
        learning_rate: float = 2e-4,
        batch_size: int = 4,
        num_epochs: int = 3,
        max_steps: int = -1,
        warmup_steps: int = 100,
        weight_decay: float = 0.01,
        gradient_accumulation_steps: int = 1,
        logging_steps: int = 10,
        save_steps: int = 50,
        eval_steps: int = 50,
        validation_split: float = 0.1,
    ) -> TrainingMetrics:
        """
        Fine-tune the model on the dataset.

        Args:
            dataset_path: Path to training dataset
            learning_rate: Learning rate for optimizer
            batch_size: Batch size per device
            num_epochs: Number of training epochs
            max_steps: Maximum training steps (-1 = use all data)
            warmup_steps: Number of warmup steps
            weight_decay: Weight decay for AdamW
            gradient_accumulation_steps: Gradient accumulation steps
            logging_steps: Logging frequency
            save_steps: Save checkpoint frequency
            eval_steps: Evaluation frequency
            validation_split: Fraction of data for validation

        Returns:
            TrainingMetrics object
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model_and_tokenizer() first.")

        logger.info(f"Preparing training dataset from: {dataset_path}")
        dataset = self.prepare_dataset(dataset_path)

        # Train/eval split
        if validation_split > 0:
            dataset_split = dataset.train_test_split(
                test_size=validation_split, seed=42
            )
            train_dataset = dataset_split["train"]
            eval_dataset = dataset_split["test"]
        else:
            train_dataset = dataset
            eval_dataset = None

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.adapter_path),
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            max_steps=max_steps,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            weight_decay=weight_decay,
            gradient_accumulation_steps=gradient_accumulation_steps,
            logging_steps=logging_steps,
            logging_dir=str(self.output_dir / "logs"),
            save_steps=save_steps,
            eval_strategy="steps" if eval_dataset else "no",
            eval_steps=eval_steps if eval_dataset else None,
            save_strategy="steps",
            load_best_model_at_end=True if eval_dataset else False,
            lr_scheduler_type="cosine",
            optim="paged_adamw_32bit",
            fp16=True if not self.use_quantization else False,
            bf16=True if self.use_quantization else False,
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=DataCollatorForLanguageModeling(
                self.tokenizer, mlm=False
            ),
        )

        logger.info("Starting training...")
        train_result = trainer.train()

        # Save adapter
        logger.info(f"Saving adapter to: {self.adapter_path}")
        self.model.save_pretrained(str(self.adapter_path))
        self.tokenizer.save_pretrained(str(self.adapter_path))

        # Calculate perplexity
        eval_results = trainer.evaluate() if eval_dataset else {}
        eval_loss = eval_results.get("eval_loss", train_result.training_loss)
        perplexity = torch.exp(torch.tensor(eval_loss)).item()

        self.metrics = TrainingMetrics(
            segment=self.segment,
            base_model=self.base_model_name,
            loss=float(train_result.training_loss),
            perplexity=perplexity,
            epoch=num_epochs,
            num_train_steps=train_result.global_step,
            learning_rate=learning_rate,
            # `TrainOutput` (transformers) só expõe (global_step, training_loss,
            # metrics) — não existe atributo `training_time_in_seconds`.
            # O tempo de parede real vem de metrics["train_runtime"] (chave
            # populada pelo Trainer ao final de `.train()`).
            total_time_seconds=train_result.metrics.get("train_runtime", 0.0),
        )

        logger.info(f"Training completed. Metrics: {asdict(self.metrics)}")
        return self.metrics

    def save_metrics(self) -> str:
        """
        Save training metrics to JSON.

        Returns:
            Path to metrics file
        """
        if self.metrics is None:
            raise ValueError("No metrics available. Run training first.")

        metrics_path = self.adapter_path / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(asdict(self.metrics), f, indent=2)

        logger.info(f"Metrics saved to: {metrics_path}")
        return str(metrics_path)

    def load_adapter(self, adapter_path: str) -> Any:
        """
        Load a previously saved LoRA adapter.

        Args:
            adapter_path: Path to adapter directory

        Returns:
            Model with loaded adapter
        """
        from peft import PeftModel

        if self.model is None:
            self.load_model_and_tokenizer()

        logger.info(f"Loading adapter from: {adapter_path}")
        self.model = PeftModel.from_pretrained(self.model, adapter_path)
        return self.model

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> str:
        """
        Generate text using the fine-tuned model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            Generated text
        """
        if self.model is None:
            raise ValueError("Model not loaded.")

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    finetuner = LoRAFinetuner(
        base_model_name="mistralai/Mistral-7B-v0.1",
        segment="saneamento",
        output_dir="./lora_adapters",
    )

    # Load model
    finetuner.load_model_and_tokenizer()
    finetuner.apply_lora_config()

    # Train (requires dataset)
    # metrics = finetuner.train(
    #     dataset_path="./saneamento_finetune_dataset.json",
    #     num_epochs=3,
    #     batch_size=4,
    # )
    # finetuner.save_metrics()
