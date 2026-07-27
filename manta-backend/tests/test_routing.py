"""
tests/test_routing.py — Benchmark de acurácia do roteamento semântico
(ml/routing.py) sobre um conjunto sintético fixo de 24 prompts,
cobrindo os 20 agentes Manta (com ênfase extra nos 5 segmentos
prioritários S6–S10 — ver CLAUDE.md, seção "MAPA COMPLETO DE
AGENTES").

Diferente de tests/test_routing_ml.py (que cobre a mecânica da
pipeline: geração de dataset, treino/versionamento, contrato de
predict_agent, fallback), este arquivo valida uma MÉTRICA de
avaliação — routing accuracy — contra um benchmark fixo e legível por
humanos, com um limiar explícito (>= 95%, i.e. no máximo 1 erro em 24).

Roda 100% offline (encoder "hashing" — ver ml/routing.py::HashingEncoder),
sem rede/GPU/download de pesos.
"""
from __future__ import annotations

import pytest

from ml.routing import (
    generate_synthetic_dataset,
    load_agent_data,
    load_routing_model,
    predict_agent,
    train_and_save,
)

# ---------------------------------------------------------------------------
# Benchmark fixo — 24 prompts / 20 agentes (S6-S10 com 2 prompts cada, os
# demais 15 agentes com 1 prompt cada => 15 + 2*5 - 1 = ver contagem exata
# abaixo). Palavras-chave usadas são as MESMAS strings (sem acentuação)
# cadastradas em ml/routing_data.json — o fallback por keyword em
# ml/routing.py faz substring match exato, então usar a grafia acentuada
# quebraria o match determinístico (ver nota em cada bloco de comentário).
# ---------------------------------------------------------------------------

BENCHMARK_PROMPTS: list[tuple[str, str]] = [
    # --- Horizontais (Eixo 1) — 1 prompt cada (11) ---
    ("Preciso de orchestration e agent recommendation para fazer o dispatch certo no maestro.", "manta-00-maestro"),
    ("Tenho um sinistro grave, preciso de loss assessment e claim analysis para a indenization.", "manta-01-claims"),
    ("Preciso de legal review do contract e da negotiation dos terms antes de fechar o agreement.", "manta-02-contratual"),
    ("Vamos avaliar a acquisition de um property, com valuation e zoning para o real estate.", "manta-04-imobiliario"),
    ("Preciso do orcamento com cost analysis e budget planning para o projeto.", "manta-05-orcamento"),
    ("Preciso da modelagem financial model com scenario analysis e VPL do projeto.", "manta-06-modelagem"),
    ("Preciso montar o cronograma com gantt e critical path para os milestones do projeto.", "manta-07-cronograma"),
    ("Buscamos business development com market analysis e partnership para growth commercial.", "manta-13-bd"),
    ("Preciso montar uma apresentacao em pptx com storytelling para o pitch deck.", "manta-14-apresentacoes"),
    ("Preciso de advisory e expert opinion para orientar a strategy do projeto.", "manta-15-advisory"),
    ("Preciso de ai architecture e system design para o agent design da nossa infrastructure design.", "manta-16-arquiteto-ia"),
    # --- Verticais S1-S4 (não-regressão) — 1 prompt cada (4) ---
    ("Preciso de terraplenagem e pavimento CBUQ com asfalto para a rodovia conforme DNIT.", "manta-03-s1-rodovias"),
    ("Preciso projetar a ponte e o viaduto da OAE conforme NBR 7187, com analise estrutural.", "manta-03-s2-oae"),
    ("Preciso avaliar o AMV e o dormente da via permanente da ferrovia para a locomotiva e o vagao.", "manta-03-s3-ferrovia"),
    ("Vou escavar a estacao do metro pelo metodo NATM com secante pile wall na linha 4.", "manta-03-s4-metro"),
    # --- S6 Portos — prioritário, 2 prompts ---
    ("Preciso de dragagem no porto, calado e berco de conteiner conforme a ANTAQ.", "manta-03-s6-portos"),
    ("O terminal de granel precisa de um molhe novo — a ANTAQ pede um estudo de calado.", "manta-03-s6-portos"),
    # --- S7 Aeroportos — 1 prompt ---
    ("Preciso dimensionar a pista de pouso do aeroporto com balizamento e taxiway conforme ANAC e ICAO.", "manta-03-s7-aeroportos"),
    # --- S8 Saneamento — prioridade AySA, 2 prompts ---
    ("Projeto de ETA e ETE, adutora e esgoto conforme SNIS.", "manta-03-s8-saneamento"),
    ("A AySA pediu um estudo de drenagem e saneamento da rede de esgoto conforme a Lei 14.026.", "manta-03-s8-saneamento"),
    # --- S9 Energia — prioridade transmissão/ANEEL, 2 prompts ---
    ("Preciso da RAP de uma LT de 500kV e da subestacao conforme o leilao da ANEEL.", "manta-03-s9-energia"),
    ("O ONS e a EPE pedem um estudo de transmissao, distribuicao e geracao de energia.", "manta-03-s9-energia"),
    # --- S10 Barragens — 2 prompts ---
    ("Preciso de uma analise de barragem CFRD, com vertedouro e gestao de rejeitos.", "manta-03-s10-barragens"),
    ("O ICOLD e o CBDB exigem revisao do TSF e da seguranca hidrica conforme o PNSB.", "manta-03-s10-barragens"),
]

ACCURACY_THRESHOLD = 0.95


# ---------------------------------------------------------------------------
# Fixtures — treino offline (encoder hashing) isolado em tmp_path, igual ao
# padrão já usado em tests/test_routing_ml.py.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def agent_data():
    return load_agent_data()


@pytest.fixture(scope="module")
def trained_model(tmp_path_factory, agent_data):
    model_dir = tmp_path_factory.mktemp("routing_benchmark_models")
    train_and_save(model_dir=model_dir, encoder_name="hashing", notes="benchmark de acuracia (test_routing.py)")
    return load_routing_model(model_dir=model_dir)


# ---------------------------------------------------------------------------
# Sanidade do próprio benchmark (antes de medir qualquer coisa do modelo)
# ---------------------------------------------------------------------------


def test_benchmark_has_exactly_24_prompts():
    assert len(BENCHMARK_PROMPTS) == 24


def test_benchmark_covers_all_20_agents(agent_data):
    covered = {slug for _, slug in BENCHMARK_PROMPTS}
    assert covered == set(agent_data.keys()), (
        f"benchmark não cobre todos os 20 agentes — faltando: {set(agent_data.keys()) - covered}"
    )


def test_benchmark_prompts_are_non_empty_and_unique():
    prompts = [p for p, _ in BENCHMARK_PROMPTS]
    assert all(p.strip() for p in prompts)
    assert len(set(prompts)) == len(prompts), "há prompts duplicados no benchmark"


# ---------------------------------------------------------------------------
# Métrica principal — routing accuracy sobre os 24 prompts
# ---------------------------------------------------------------------------


def test_routing_accuracy_meets_95_percent_threshold(trained_model):
    """Roda os 24 prompts do benchmark contra o modelo treinado (hashing,
    offline) e mede a accuracy = acertos / total. O requisito de negócio
    é >= 95% (no máximo 1 erro nos 24 prompts fixos)."""
    mismatches: list[str] = []
    correct = 0

    for prompt, expected_slug in BENCHMARK_PROMPTS:
        agent_slug, confidence, _top_3 = predict_agent(prompt, model=trained_model)
        if agent_slug == expected_slug:
            correct += 1
        else:
            mismatches.append(
                f"prompt={prompt!r} esperado={expected_slug!r} obtido={agent_slug!r} (confidence={confidence:.3f})"
            )

    accuracy = correct / len(BENCHMARK_PROMPTS)

    assert accuracy >= ACCURACY_THRESHOLD, (
        f"routing accuracy {accuracy:.2%} abaixo do limiar {ACCURACY_THRESHOLD:.0%} "
        f"({correct}/{len(BENCHMARK_PROMPTS)} corretos). Mismatches:\n" + "\n".join(mismatches)
    )


def test_routing_accuracy_per_priority_segment(trained_model):
    """Quebra a mesma métrica por segmento prioritário (S6-S10) — útil
    para localizar rapidamente qual vertical regrediu, sem re-rodar o
    benchmark inteiro manualmente."""
    priority_prefixes = {
        "manta-03-s6-portos": "Portos",
        "manta-03-s7-aeroportos": "Aeroportos",
        "manta-03-s8-saneamento": "Saneamento",
        "manta-03-s9-energia": "Energia",
        "manta-03-s10-barragens": "Barragens",
    }
    per_segment_cases = [(p, e) for p, e in BENCHMARK_PROMPTS if e in priority_prefixes]
    assert len(per_segment_cases) == 9  # 2+1+2+2+2

    for prompt, expected_slug in per_segment_cases:
        agent_slug, confidence, top_3 = predict_agent(prompt, model=trained_model)
        assert agent_slug == expected_slug, (
            f"segmento prioritário {priority_prefixes[expected_slug]} errou: "
            f"prompt={prompt!r} obtido={agent_slug!r} top_3={top_3!r}"
        )
        assert confidence > 0.0


def test_predict_agent_returns_well_formed_result_for_every_benchmark_prompt(trained_model):
    """Sanity check estrutural (independente de acerto/erro): todo prompt do
    benchmark tem que produzir o contrato de retorno documentado em
    predict_agent, nunca uma exceção ou estrutura malformada."""
    for prompt, _expected_slug in BENCHMARK_PROMPTS:
        agent_slug, confidence, top_3 = predict_agent(prompt, model=trained_model)
        assert isinstance(agent_slug, str) and agent_slug in set(trained_model.classes)
        assert 0.0 <= confidence <= 1.0
        assert 1 <= len(top_3) <= 3
        for item in top_3:
            assert {"agent_slug", "agent_name", "confidence", "method"} <= item.keys()


# ---------------------------------------------------------------------------
# Synthetic dataset — 10 exemplos/segmento (ênfase nos 5 segmentos
# prioritários S6-S10 citados no ticket de expansão v4.2)
# ---------------------------------------------------------------------------


def test_synthetic_dataset_has_10_examples_per_priority_segment(agent_data):
    texts, labels = generate_synthetic_dataset(agent_data)  # default n_per_agent=10
    priority_segments = [
        "manta-03-s6-portos",
        "manta-03-s7-aeroportos",
        "manta-03-s8-saneamento",
        "manta-03-s9-energia",
        "manta-03-s10-barragens",
    ]
    assert len(texts) == len(agent_data) * 10
    for slug in priority_segments:
        assert labels.count(slug) == 10, f"segmento {slug} não tem exatamente 10 exemplos sintéticos"
