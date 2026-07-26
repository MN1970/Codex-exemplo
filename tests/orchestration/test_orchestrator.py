#!/usr/bin/env python3
"""
Tests for Maestro Orchestrator Agent (Phase 2.2)
"""

import pytest
from maestro.orchestrator import (
    MaestroOrchestrator,
    OrchestratorInput,
    OrchestratorOutput,
)


class TestOrchestratorBasics:
    """Basic orchestrator functionality tests."""

    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = MaestroOrchestrator(api_key="test-key")
        assert orchestrator is not None
        assert orchestrator.model == "claude-opus-4-1-20250805"

    def test_input_dataclass(self):
        """Test OrchestratorInput dataclass."""
        test_input = OrchestratorInput(
            user_prompt="Test prompt",
            primary_agent="agente-barragens",
            primary_response="Test response from agent 1",
            secondary_agent="agente-energia",
            secondary_response="Test response from agent 2",
            routing_scores={"agente-barragens": 0.95, "agente-energia": 0.88},
            ambiguity_reason="Score gap < 10%",
        )
        assert test_input.primary_agent == "agente-barragens"
        assert test_input.routing_scores["agente-energia"] == 0.88

    def test_output_dataclass(self):
        """Test OrchestratorOutput dataclass."""
        test_output = OrchestratorOutput(
            merged_response="Test response",
            primary_responsibility="agente-barragens",
            secondary_responsibility="agente-energia",
            cross_concerns=["Concern 1", "Concern 2"],
            coordination_requirements="Sync required",
            recommended_lead="agente-barragens",
            confidence=0.85,
            handoff_points=[],
            timestamp="2026-07-26T00:00:00Z",
        )
        assert test_output.confidence == 0.85
        assert len(test_output.cross_concerns) == 2

    def test_orchestrator_to_dict(self):
        """Test conversion to dictionary."""
        orchestrator = MaestroOrchestrator(api_key="test-key")
        test_output = OrchestratorOutput(
            merged_response="Test response",
            primary_responsibility="agente-barragens",
            secondary_responsibility="agente-energia",
            cross_concerns=["Concern 1"],
            coordination_requirements="Sync",
            recommended_lead="agente-barragens",
            confidence=0.85,
            handoff_points=[],
            timestamp="2026-07-26T00:00:00Z",
        )

        result_dict = orchestrator.to_dict(test_output)
        assert isinstance(result_dict, dict)
        assert result_dict["confidence"] == 0.85
        assert result_dict["primary_responsibility"] == "agente-barragens"


class TestOrchestratorPromptBuilding:
    """Test prompt construction."""

    def test_build_orchestration_prompt(self):
        """Test prompt building."""
        orchestrator = MaestroOrchestrator(api_key="test-key")
        test_input = OrchestratorInput(
            user_prompt="Design a dam",
            primary_agent="agente-barragens",
            primary_response="Dam response",
            secondary_agent="agente-energia",
            secondary_response="Energy response",
            routing_scores={"agente-barragens": 0.95, "agente-energia": 0.88},
            ambiguity_reason="Cross-domain query",
        )

        prompt = orchestrator._build_orchestration_prompt(test_input)
        assert "Maestro Orchestrator" in prompt
        assert "agente-barragens" in prompt
        assert "agente-energia" in prompt
        assert "Design a dam" in prompt


class TestOrchestratorParsing:
    """Test response parsing."""

    def test_parse_orchestrator_response(self):
        """Test parsing of orchestrator response."""
        orchestrator = MaestroOrchestrator(api_key="test-key")
        test_input = OrchestratorInput(
            user_prompt="Design a dam with transmission",
            primary_agent="agente-barragens",
            primary_response="Dam design",
            secondary_agent="agente-energia",
            secondary_response="Energy design",
            routing_scores={"agente-barragens": 0.95, "agente-energia": 0.88},
        )

        response_text = """
## Visão Integrada

### Responsabilidade Primária: agente-barragens
Barragem de concreto com fundações em rocha.

### Responsabilidade Secundária: agente-energia
Transmissão de 500kV integrada ao projeto.

### Cross-Concerns (Requerem Coordenação)
- Fundações compartilhadas: Escavação da barragem impacta SE
- Cronograma: LT deve esperar enchimento
- Ambiental: Permissões compartilhadas

### Sequência Recomendada
1. Fundações da barragem
2. Estrutura de barragem
3. Fundações da SE

### Pontos de Handoff
1. Quando barragem finalizar, SE coloca estruturas

### Agente Recomendado para Liderar
agente-barragens deve coordenar pois afeta cronograma geral
"""

        result = orchestrator._parse_orchestrator_response(response_text, test_input)
        assert result.primary_responsibility == "agente-barragens"
        assert result.secondary_responsibility == "agente-energia"
        assert len(result.cross_concerns) >= 2
        assert "agente-barragens" in result.recommended_lead


class TestOrchestratorCases:
    """Test with example cases from specification."""

    def test_case_uhe_cfrd_lt(self):
        """Test UHE + CFRD + LT case."""
        test_input = OrchestratorInput(
            user_prompt="Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE.",
            primary_agent="agente-barragens",
            primary_response="""
A barragem CFRD (Concrete Face Rockfill Dam) de 100m é viável.
Recomendações:
1. Fundações: Escavação até rocha sã, limpeza de fraturas
2. Estrutura: Face de concreto 60cm, enrocamento T1/T2
3. Vertedouro: Dimensionado para Q100
            """,
            secondary_agent="agente-energia",
            secondary_response="""
A LT 500kV é apropriada para esta capacidade de UHE.
Recomendações:
1. Traçado: Evita ocupação da cota do reservatório
2. Estruturas: Torres auto-portantes para vãos de 400m
3. Subestação: Locada em cota elevada para segurança hidrológica
            """,
            routing_scores={"agente-barragens": 0.95, "agente-energia": 0.88},
            ambiguity_reason="Consulta abrange barragem e transmissão",
        )

        assert test_input.primary_agent == "agente-barragens"
        assert test_input.secondary_agent == "agente-energia"
        assert test_input.routing_scores["agente-barragens"] > test_input.routing_scores["agente-energia"]

    def test_case_ete_subestacao(self):
        """Test ETE + Subestação case."""
        test_input = OrchestratorInput(
            user_prompt="ETE com gerador de backup conectado à subestação vizinha.",
            primary_agent="agente-saneamento",
            primary_response="""
ETE dimensionada para 100 L/s.
Recomendações:
1. Tratamento: Lodo ativado com alagado construído
2. Consumo elétrico: 50 kW (ar, elevatórias)
3. Backup: Gerador diesel 75 kVA
            """,
            secondary_agent="agente-energia",
            secondary_response="""
Subestação 13.8 kV / 220V próxima à ETE.
Recomendações:
1. Trafo: 225 kVA (normal + backup)
2. Alimentação: LT a 13.8 kV da subestação principal
3. Conexão gerador: Sincronismo com rede
            """,
            routing_scores={"agente-saneamento": 0.90, "agente-energia": 0.85},
            ambiguity_reason="Cross-domain: saneamento + energia",
        )

        assert test_input.primary_agent == "agente-saneamento"
        assert "gerador" in test_input.primary_response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
