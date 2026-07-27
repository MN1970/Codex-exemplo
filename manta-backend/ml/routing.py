"""
ml/routing.py — Roteamento semântico dos 20 agentes Manta via embeddings.

Pipeline: Sentence Transformers (all-MiniLM-L6-v2, 384-d, mesmo modelo de
ml/embeddings.py) + Logistic Regression multinomial (scikit-learn),
treinado sobre dados sintéticos gerados a partir de ml/routing_data.json
(20 agentes: Manta 00-01-02-04-05-06-07-13-14-15-16 + Manta 03-S1..S4,
S6..S10 — ver CLAUDE.md, seção "MAPA COMPLETO DE AGENTES").

Uso (treino/CLI):
    python -m ml.routing train
    python -m ml.routing predict "preciso de dragagem no porto"

Uso (programático):
    from ml.routing import load_routing_model, predict_agent

    model = load_routing_model()               # carrega a versão "current"
    agent_slug, confidence, top_3 = predict_agent("preciso de dragagem no porto")

Se a confiança do top-1 embedding ficar abaixo de `confidence_threshold`
(default 0.7), a decisão cai para keyword matching (fallback determinístico
sobre ml/routing_data.json["...]["keywords"]) — nunca retorna vazio se
houver QUALQUER keyword batendo no prompt.

NOTA — dependência de rede (Sentence Transformers): o encoder default
("sentence-transformers") baixa os pesos de all-MiniLM-L6-v2 do Hugging
Face Hub no primeiro uso (cache local depois, igual a ml/embeddings.py).
Em ambientes sem egress para huggingface.co (ex.: este sandbox de dev,
bloqueado por política de proxy), use encoder_name="hashing" — um
encoder determinístico offline (hashing trick, sem rede, sem GPU) que
existe SÓ para permitir treinar/testar a pipeline mecanicamente sem
acesso à internet. Ele não tem qualidade semântica real e não deve ser
usado em produção; o modelo versionado gerado com ele é marcado com
embedding_model="hashing-offline-384d" no manifest para nunca ser
confundido com um artefato de produção.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

logger = logging.getLogger("manta.ml.routing")

# ---------------------------------------------------------------------------
# Constantes / paths
# ---------------------------------------------------------------------------

ML_DIR = Path(__file__).parent
AGENT_DATA_FILE = ML_DIR / "routing_data.json"
MODEL_DIR = ML_DIR / "models"
MANIFEST_FILE = "routing_manifest.json"

DEFAULT_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_TOP_K = 3
DEFAULT_N_PER_AGENT = 10
DEFAULT_TEST_SIZE = 0.2
DEFAULT_SEED = 42
DEFAULT_LOGREG_C = 10.0

# Nome/dimensão do modelo Sentence Transformers — mesmo usado pelo RAG
# (ml/embeddings.py). Mantido como constante própria (em vez de importar
# de ml.embeddings) para este módulo não puxar `sentence_transformers`
# em import time quando só o encoder "hashing" é usado (ex.: testes).
SENTENCE_TRANSFORMER_MODEL_NAME = "all-MiniLM-L6-v2"
SENTENCE_TRANSFORMER_DIMENSIONS = 384
HASHING_ENCODER_DIMENSIONS = 384


# ---------------------------------------------------------------------------
# Encoders (texto -> vetor). Abstração para permitir treinar/testar sem
# depender de rede (huggingface.co) nem de GPU.
# ---------------------------------------------------------------------------


class TextEncoder(Protocol):
    """Interface mínima que qualquer encoder de texto precisa implementar."""

    name: str
    dimensions: int

    def encode(self, texts: List[str]) -> np.ndarray:
        ...


class SentenceTransformerEncoder:
    """Encoder de produção — Sentence Transformers (all-MiniLM-L6-v2).

    Carregamento lazy (só na primeira chamada a `encode`) e cacheado por
    nome de modelo em `_st_model_cache`, para não pagar o custo de carregar
    pesos/inicializar torch mais de uma vez por processo.
    """

    _model_cache: Dict[str, Any] = {}

    def __init__(self, model_name: str = SENTENCE_TRANSFORMER_MODEL_NAME, device: Optional[str] = None):
        self.name = model_name
        self.dimensions = SENTENCE_TRANSFORMER_DIMENSIONS
        self._device = device

    def _load(self):
        cache_key = f"{self.name}::{self._device or 'auto'}"
        cached = SentenceTransformerEncoder._model_cache.get(cache_key)
        if cached is not None:
            return cached

        from sentence_transformers import SentenceTransformer  # import local — evita custo em quem só usa "hashing"

        device = self._device
        if device is None:
            try:
                import torch

                if torch.cuda.is_available():
                    device = "cuda"
                elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    device = "mps"
                else:
                    device = "cpu"
            except ImportError:
                device = "cpu"

        logger.info("routing: carregando SentenceTransformer(%s) em %s...", self.name, device)
        model = SentenceTransformer(self.name, device=device)
        SentenceTransformerEncoder._model_cache[cache_key] = model
        return model

    def encode(self, texts: List[str]) -> np.ndarray:
        model = self._load()
        embeddings = model.encode(
            texts,
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float64)


class HashingEncoder:
    """Encoder offline determinístico (hashing trick, bag-of-words).

    NÃO é um substituto semântico do Sentence Transformers — existe só
    para permitir rodar a pipeline (treino, save/load, predict, testes)
    em ambientes sem egress para huggingface.co, sem GPU e sem depender
    de rede. Modelos treinados com este encoder são marcados no manifest
    com embedding_model="hashing-offline-384d" e NUNCA devem ser
    promovidos a produção.
    """

    def __init__(self, dimensions: int = HASHING_ENCODER_DIMENSIONS):
        self.name = "hashing-offline-384d"
        self.dimensions = dimensions

    def _encode_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimensions, dtype=np.float64)
        tokens = [t for t in text.lower().replace("/", " ").replace("-", " ").split() if t]
        for token in tokens:
            # Duas hashes por token (unigrama "puro" + prefixo de 4 chars)
            # dão um pouco de tolerância a plural/flexão sem precisar de
            # stemmer — ex.: "portos"/"porto" caem em buckets diferentes
            # pela hash cheia, mas colidem no prefixo.
            idx_full = zlib.crc32(token.encode("utf-8")) % self.dimensions
            vec[idx_full] += 1.0
            if len(token) >= 4:
                idx_prefix = zlib.crc32(token[:4].encode("utf-8")) % self.dimensions
                vec[idx_prefix] += 0.5
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def encode(self, texts: List[str]) -> np.ndarray:
        return np.stack([self._encode_one(t) for t in texts])


_default_encoder: Optional[SentenceTransformerEncoder] = None
_encoder_registry: Dict[str, TextEncoder] = {}


def get_encoder(name: str = "sentence-transformers") -> TextEncoder:
    """Factory/cache de encoders por nome.

    Args:
        name: "sentence-transformers" (default, produção) ou "hashing"
            (offline, dev/teste — ver HashingEncoder).
    """
    if name in _encoder_registry:
        return _encoder_registry[name]

    if name == "sentence-transformers":
        encoder: TextEncoder = SentenceTransformerEncoder()
    elif name == "hashing":
        encoder = HashingEncoder()
    else:
        raise ValueError(f"Encoder desconhecido: {name!r} (use 'sentence-transformers' ou 'hashing')")

    _encoder_registry[name] = encoder
    return encoder


def get_default_encoder() -> TextEncoder:
    """Encoder de produção (Sentence Transformers), cacheado como singleton."""
    global _default_encoder
    if _default_encoder is None:
        _default_encoder = get_encoder("sentence-transformers")
    return _default_encoder


# ---------------------------------------------------------------------------
# Dados dos agentes + geração de dados sintéticos
# ---------------------------------------------------------------------------


def load_agent_data(data_file: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Carrega os 20 agentes de ml/routing_data.json."""
    path = Path(data_file) if data_file else AGENT_DATA_FILE
    with open(path, "r", encoding="utf-8") as f:
        agent_data: Dict[str, Dict[str, Any]] = json.load(f)
    logger.info("routing: %d agentes carregados de %s", len(agent_data), path)
    return agent_data


# Templates usados para gerar frases sintéticas de treino a partir das
# keywords/nome de cada agente. Cada agente recebe exatamente
# len(_SYNTHETIC_TEMPLATES) exemplos (10 por padrão) — um por template,
# ciclando pela lista de keywords do agente (embaralhada de forma
# determinística por seed, para não enviesar sempre para a 1a/2a keyword).
_SYNTHETIC_TEMPLATES: List[str] = [
    "Preciso de ajuda com {kw}",
    "Qual agente cuida de {kw}?",
    "Tenho uma dúvida técnica sobre {kw}",
    "Como avaliar {kw} neste projeto?",
    "Buscando consultoria especializada em {kw}",
    "O projeto envolve {kw} e também {kw2}",
    "{name}: preciso de suporte sobre {kw}",
    "Pode me orientar sobre questões de {kw}?",
    "Qual a abordagem recomendada para {kw}?",
    "Precisamos de uma análise técnica envolvendo {kw}",
]


def generate_synthetic_dataset(
    agent_data: Dict[str, Dict[str, Any]],
    n_per_agent: int = DEFAULT_N_PER_AGENT,
    seed: int = DEFAULT_SEED,
) -> Tuple[List[str], List[str]]:
    """Gera dataset sintético de treino: n_per_agent exemplos por agente.

    Determinístico dado o mesmo (agent_data, n_per_agent, seed) — cada
    agente tem sua ordem de keywords embaralhada com uma seed derivada
    (seed + crc32(slug)) para não repetir sempre o mesmo padrão entre
    agentes, mas continuar 100% reprodutível.

    Args:
        agent_data: dict slug -> {"name", "keywords", "description", ...}
        n_per_agent: quantos exemplos sintéticos gerar por agente
        seed: seed base para o shuffle determinístico das keywords

    Returns:
        (texts, labels) — listas paralelas, len == len(agent_data) * n_per_agent
    """
    texts: List[str] = []
    labels: List[str] = []

    templates = _SYNTHETIC_TEMPLATES
    if n_per_agent > len(templates):
        # Repete o ciclo de templates se pedirem mais exemplos que templates existentes.
        reps = (n_per_agent // len(templates)) + 1
        templates = (templates * reps)[:n_per_agent]
    else:
        templates = templates[:n_per_agent]

    for slug, info in agent_data.items():
        name = info.get("name", slug)
        keywords = list(info.get("keywords", [])) or [name]

        rng = random.Random(seed + (zlib.crc32(slug.encode("utf-8")) & 0xFFFF))
        shuffled = keywords[:]
        rng.shuffle(shuffled)

        for i, template in enumerate(templates):
            kw = shuffled[i % len(shuffled)]
            kw2 = shuffled[(i + 1) % len(shuffled)]
            text = template.format(kw=kw, kw2=kw2, name=name)
            texts.append(text)
            labels.append(slug)

    logger.info(
        "routing: dataset sintético gerado — %d exemplos (%d agentes x %d/agente)",
        len(texts), len(agent_data), n_per_agent,
    )
    return texts, labels


# ---------------------------------------------------------------------------
# Treino + versionamento
# ---------------------------------------------------------------------------


@dataclass
class TrainingResult:
    version: int
    model_path: Path
    metrics: Dict[str, Any]
    embedding_model: str
    embedding_dimensions: int
    num_agents: int
    num_samples: int


def _read_manifest(model_dir: Path) -> Dict[str, Any]:
    manifest_path = model_dir / MANIFEST_FILE
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_version": None, "versions": []}


def _write_manifest(model_dir: Path, manifest: Dict[str, Any]) -> None:
    manifest_path = model_dir / MANIFEST_FILE
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def _next_version(manifest: Dict[str, Any]) -> int:
    versions = [v["version"] for v in manifest.get("versions", [])]
    return (max(versions) + 1) if versions else 1


def train_and_save(
    data_file: Optional[Path] = None,
    model_dir: Optional[Path] = None,
    encoder: Optional[TextEncoder] = None,
    encoder_name: str = "sentence-transformers",
    n_per_agent: int = DEFAULT_N_PER_AGENT,
    test_size: float = DEFAULT_TEST_SIZE,
    seed: int = DEFAULT_SEED,
    C: float = DEFAULT_LOGREG_C,
    notes: Optional[str] = None,
) -> TrainingResult:
    """Treina o classificador de roteamento semântico e salva um pickle versionado.

    Pipeline:
      1. Carrega os 20 agentes de routing_data.json.
      2. Gera n_per_agent exemplos sintéticos por agente (~200 no total).
      3. Gera embeddings (Sentence Transformers por padrão, ou `encoder`).
      4. Split estratificado train/test (avaliação honesta, held-out).
      5. Treina LogisticRegression multinomial sobre o split de treino,
         calcula métricas no split de teste.
      6. Reajusta (refit) a LogisticRegression final sobre TODOS os dados
         sintéticos (prática padrão: métricas vêm do holdout, mas o
         artefato de produção usa o máximo de dado disponível).
      7. Salva o bundle via joblib em models/routing_model_v{N}.joblib e
         atualiza o manifesto (routing_manifest.json) — versão N vira
         "current_version".

    Args:
        data_file: path alternativo para routing_data.json (default: ml/routing_data.json)
        model_dir: diretório de modelos (default: ml/models/)
        encoder: instância de TextEncoder já construída (tem prioridade sobre encoder_name)
        encoder_name: "sentence-transformers" (default) ou "hashing" (offline/dev/teste)
        n_per_agent: exemplos sintéticos por agente (default 10)
        test_size: proporção para o split de avaliação (default 0.2)
        seed: seed determinística (dataset sintético + split + classificador)
        C: inverso da força de regularização da LogisticRegression (default 10.0
            — dataset pequeno/balanceado por classe se beneficia de menos
            regularização que o default do sklearn (C=1.0) para não achatar
            demais as probabilidades entre 20 classes)
        notes: nota livre opcional gravada no manifesto (ex.: "offline demo build")

    Returns:
        TrainingResult com a versão salva e as métricas de avaliação.
    """
    model_dir = Path(model_dir) if model_dir else MODEL_DIR
    model_dir.mkdir(parents=True, exist_ok=True)

    agent_data = load_agent_data(data_file)
    agent_keywords = {slug: info.get("keywords", []) for slug, info in agent_data.items()}

    texts, labels = generate_synthetic_dataset(agent_data, n_per_agent=n_per_agent, seed=seed)

    enc = encoder or get_encoder(encoder_name)
    logger.info("routing: gerando embeddings com encoder=%s (dim=%d)...", enc.name, enc.dimensions)
    X = enc.encode(texts)
    y = np.asarray(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y,
    )

    logger.info("routing: treinando LogisticRegression (%d treino / %d teste)...", len(y_train), len(y_test))
    eval_clf = LogisticRegression(max_iter=2000, C=C, random_state=seed)
    eval_clf.fit(X_train, y_train)

    y_pred = eval_clf.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "num_agents": len(agent_data),
        "num_train_samples": int(len(y_train)),
        "num_test_samples": int(len(y_test)),
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
    }
    logger.info(
        "routing: eval — accuracy=%.4f precision=%.4f recall=%.4f f1=%.4f",
        metrics["accuracy"], metrics["precision"], metrics["recall"], metrics["f1"],
    )

    # Refit final sobre 100% dos dados sintéticos (produção usa tudo).
    final_clf = LogisticRegression(max_iter=2000, C=C, random_state=seed)
    final_clf.fit(X, y)

    manifest = _read_manifest(model_dir)
    version = _next_version(manifest)
    created_at = datetime.now(timezone.utc).isoformat()

    bundle = {
        "version": version,
        "created_at": created_at,
        "embedding_model": enc.name,
        "embedding_dimensions": enc.dimensions,
        "classifier": final_clf,
        "classes": list(final_clf.classes_),
        "agent_data": agent_data,
        "agent_keywords": agent_keywords,
        "metrics": metrics,
        "training_config": {
            "n_per_agent": n_per_agent,
            "test_size": test_size,
            "seed": seed,
            "num_samples": len(texts),
        },
    }

    model_filename = f"routing_model_v{version}.joblib"
    model_path = model_dir / model_filename
    joblib.dump(bundle, model_path)
    logger.info("routing: modelo salvo em %s", model_path)

    manifest.setdefault("versions", []).append(
        {
            "version": version,
            "file": model_filename,
            "created_at": created_at,
            "embedding_model": enc.name,
            "num_agents": len(agent_data),
            "num_samples": len(texts),
            "metrics": {k: v for k, v in metrics.items() if k != "classification_report"},
            "notes": notes,
        }
    )
    manifest["current_version"] = version
    _write_manifest(model_dir, manifest)

    return TrainingResult(
        version=version,
        model_path=model_path,
        metrics=metrics,
        embedding_model=enc.name,
        embedding_dimensions=enc.dimensions,
        num_agents=len(agent_data),
        num_samples=len(texts),
    )


# ---------------------------------------------------------------------------
# Carregamento + inferência
# ---------------------------------------------------------------------------


@dataclass
class RoutingModel:
    version: int
    created_at: str
    embedding_model: str
    embedding_dimensions: int
    classifier: LogisticRegression
    classes: List[str]
    agent_data: Dict[str, Dict[str, Any]]
    agent_keywords: Dict[str, List[str]]
    metrics: Dict[str, Any]
    model_dir: Path = field(repr=False)


_model_cache: Dict[Tuple[str, Optional[int]], RoutingModel] = {}


def load_routing_model(version: Optional[int] = None, model_dir: Optional[Path] = None) -> RoutingModel:
    """Carrega um modelo de roteamento treinado (RoutingModel) a partir do manifesto.

    Args:
        version: versão específica a carregar; None = usa "current_version" do manifesto.
        model_dir: diretório de modelos (default: ml/models/)

    Returns:
        RoutingModel pronto para uso em predict_agent().

    Raises:
        FileNotFoundError: se não houver manifesto/versão treinada ainda
            (rode `python -m ml.routing train` primeiro).
    """
    resolved_dir = Path(model_dir) if model_dir else MODEL_DIR
    cache_key = (str(resolved_dir), version)
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    manifest = _read_manifest(resolved_dir)
    if not manifest.get("versions"):
        raise FileNotFoundError(
            f"Nenhum modelo de roteamento treinado em {resolved_dir}. "
            "Rode `python -m ml.routing train` (ou train_and_save()) primeiro."
        )

    target_version = version if version is not None else manifest.get("current_version")
    entry = next((v for v in manifest["versions"] if v["version"] == target_version), None)
    if entry is None:
        raise FileNotFoundError(f"Versão {target_version} não encontrada no manifesto de {resolved_dir}")

    bundle = joblib.load(resolved_dir / entry["file"])

    model = RoutingModel(
        version=bundle["version"],
        created_at=bundle["created_at"],
        embedding_model=bundle["embedding_model"],
        embedding_dimensions=bundle["embedding_dimensions"],
        classifier=bundle["classifier"],
        classes=bundle["classes"],
        agent_data=bundle["agent_data"],
        agent_keywords=bundle["agent_keywords"],
        metrics=bundle["metrics"],
        model_dir=resolved_dir,
    )
    _model_cache[cache_key] = model
    logger.info("routing: modelo v%d carregado (%s, %d agentes)", model.version, model.embedding_model, len(model.agent_data))
    return model


def _keyword_fallback(
    prompt: str,
    agent_data: Dict[str, Dict[str, Any]],
    agent_keywords: Dict[str, List[str]],
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """Fallback determinístico por keyword matching (sem ML).

    Score = (nº de keywords do agente encontradas no prompt) / (nº total
    de keywords do agente) — mesma heurística usada historicamente em
    ml/routing_classifier.py, para manter o comportamento de fallback
    consistente entre as duas gerações do classificador.
    """
    prompt_lower = prompt.lower()
    scores: Dict[str, float] = {}

    for slug, keywords in agent_keywords.items():
        if not keywords:
            continue
        matches = sum(1 for kw in keywords if kw.lower() in prompt_lower)
        if matches > 0:
            scores[slug] = matches / len(keywords)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [
        {
            "agent_slug": slug,
            "agent_name": agent_data.get(slug, {}).get("name", slug),
            "confidence": float(score),
            "method": "keyword_fallback",
        }
        for slug, score in ranked
    ]


def _merge_top_k(primary: List[Dict[str, Any]], secondary: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    """Junta duas listas de predições preservando ordem e sem duplicar agent_slug."""
    seen: set = set()
    merged: List[Dict[str, Any]] = []
    for item in list(primary) + list(secondary):
        if item["agent_slug"] in seen:
            continue
        seen.add(item["agent_slug"])
        merged.append(item)
        if len(merged) >= top_k:
            break
    return merged


def predict_agent(
    prompt: str,
    top_k: int = DEFAULT_TOP_K,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    model: Optional[RoutingModel] = None,
    encoder: Optional[TextEncoder] = None,
    use_fallback: bool = True,
) -> Tuple[str, float, List[Dict[str, Any]]]:
    """Prediz o(s) agente(s) mais relevante(s) para um prompt.

    Args:
        prompt: texto do usuário (ex.: "preciso de dragagem no porto")
        top_k: quantas predições retornar em `top_3` (default 3)
        confidence_threshold: se a confiança do top-1 do embedding ficar
            abaixo disso, cai para keyword fallback (default 0.7)
        model: RoutingModel já carregado (default: load_routing_model())
        encoder: TextEncoder já construído (default: o mesmo do model.embedding_model,
            resolvido via get_encoder — assume "sentence-transformers" salvo
            quando o modelo foi treinado com "hashing", nesse caso resolve
            automaticamente para o encoder "hashing")
        use_fallback: se False, desliga o keyword fallback e sempre
            retorna a predição do embedding (mesmo com baixa confiança)

    Returns:
        (agent_slug, confidence, top_3) onde:
          - agent_slug: slug do agente escolhido (embedding ou fallback)
          - confidence: confiança associada a essa escolha (0.0-1.0)
          - top_3: lista de até top_k dicts {agent_slug, agent_name, confidence, method}

    Raises:
        ValueError: prompt vazio/whitespace.
        FileNotFoundError: nenhum modelo treinado (ver load_routing_model()).
    """
    if not prompt or not prompt.strip():
        raise ValueError("prompt não pode ser vazio")

    model = model or load_routing_model()

    if encoder is None:
        encoder_name = "hashing" if model.embedding_model == "hashing-offline-384d" else "sentence-transformers"
        encoder = get_encoder(encoder_name)

    vector = encoder.encode([prompt])
    proba = model.classifier.predict_proba(vector)[0]
    classes = model.classifier.classes_

    order = np.argsort(proba)[::-1][:top_k]
    embedding_top: List[Dict[str, Any]] = [
        {
            "agent_slug": str(classes[idx]),
            "agent_name": model.agent_data.get(str(classes[idx]), {}).get("name", str(classes[idx])),
            "confidence": float(proba[idx]),
            "method": "embedding",
        }
        for idx in order
    ]

    best = embedding_top[0]

    if not use_fallback or best["confidence"] >= confidence_threshold:
        return best["agent_slug"], best["confidence"], embedding_top

    logger.info(
        "routing: confiança baixa (%.4f < %.4f) para %r, tentando keyword fallback...",
        best["confidence"], confidence_threshold, prompt[:80],
    )
    fallback_results = _keyword_fallback(prompt, model.agent_data, model.agent_keywords, top_k=top_k)

    if fallback_results:
        merged = _merge_top_k(fallback_results, embedding_top, top_k=top_k)
        top = merged[0]
        return top["agent_slug"], top["confidence"], merged

    # Sem match de keyword nenhum — devolve o embedding mesmo com baixa confiança.
    return best["agent_slug"], best["confidence"], embedding_top


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_train(args: argparse.Namespace) -> None:
    result = train_and_save(
        encoder_name=args.encoder,
        n_per_agent=args.n_per_agent,
        test_size=args.test_size,
        seed=args.seed,
        C=args.C,
        notes=args.notes,
    )
    print("=" * 70)
    print(f"Modelo salvo: {result.model_path} (v{result.version})")
    print(f"Encoder: {result.embedding_model} (dim={result.embedding_dimensions})")
    print(f"Agentes: {result.num_agents} | Amostras sintéticas: {result.num_samples}")
    print(f"Accuracy (holdout): {result.metrics['accuracy']:.4f}")
    print(f"F1 (holdout):       {result.metrics['f1']:.4f}")
    print("=" * 70)


def _cli_predict(args: argparse.Namespace) -> None:
    agent_slug, confidence, top_3 = predict_agent(
        args.prompt,
        top_k=args.top_k,
        confidence_threshold=args.threshold,
    )
    print(f"\nPrompt: {args.prompt}")
    print(f"-> Agente: {agent_slug} (confiança: {confidence:.2%})")
    print("Top-3:")
    for i, item in enumerate(top_3, 1):
        print(f"  {i}. {item['agent_name']} ({item['agent_slug']}) — {item['confidence']:.2%} [{item['method']}]")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Manta — roteamento semântico (Sentence Transformers + LogisticRegression)")
    sub = parser.add_subparsers(dest="command", required=True)

    train_parser = sub.add_parser("train", help="Treina e salva uma nova versão do modelo")
    train_parser.add_argument("--encoder", default="sentence-transformers", choices=["sentence-transformers", "hashing"])
    train_parser.add_argument("--n-per-agent", type=int, default=DEFAULT_N_PER_AGENT)
    train_parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE)
    train_parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    train_parser.add_argument("--C", type=float, default=DEFAULT_LOGREG_C)
    train_parser.add_argument("--notes", default=None)
    train_parser.set_defaults(func=_cli_train)

    predict_parser = sub.add_parser("predict", help="Roda uma predição usando o modelo current")
    predict_parser.add_argument("prompt", type=str)
    predict_parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    predict_parser.add_argument("--threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD)
    predict_parser.set_defaults(func=_cli_predict)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
