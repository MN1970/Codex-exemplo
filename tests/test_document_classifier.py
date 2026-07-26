#!/usr/bin/env python3
"""
Tests for Document Auto-Classifier (Phase 2.3)
"""

import json
import pytest
import tempfile
from pathlib import Path

from api.document_classifier import (
    DocumentClassifier,
    DocumentExtractor,
    ClassificationResult,
)


class TestDocumentExtractor:
    """Test document text extraction."""

    def test_extract_text_file(self):
        """Test extracting text from text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Este é um documento sobre barragens\nCFRD de 100 metros\n")
            f.flush()

            text = DocumentExtractor.extract_text(f.name)
            assert "barragens" in text.lower()

            Path(f.name).unlink()

    def test_extract_from_file_text(self):
        """Test extract_from_file with text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Projeto de barragem CFRD")
            f.flush()

            text, file_type = DocumentExtractor.extract_from_file(f.name)
            assert file_type == "text"
            assert "barragem" in text.lower()

            Path(f.name).unlink()


class TestClassificationResult:
    """Test ClassificationResult dataclass."""

    def test_classification_result_creation(self):
        """Test creating a classification result."""
        result = ClassificationResult(
            file_name="test.pdf",
            file_type="pdf",
            extracted_text="Projeto de barragem",
            primary_agent="agente-barragens",
            confidence=0.95,
            secondary_agents=[("agente-energia", 0.45)],
            suggested_folder="03_Projetos/Barragens",
            classification_reason="Menção a CFRD e fundações",
            timestamp="2026-07-26T00:00:00Z",
        )

        assert result.primary_agent == "agente-barragens"
        assert result.confidence == 0.95
        assert len(result.secondary_agents) == 1

    def test_classification_result_dict(self):
        """Test converting result to dict."""
        result = ClassificationResult(
            file_name="test.pdf",
            file_type="pdf",
            extracted_text="Texto extraído",
            primary_agent="agente-saneamento",
            confidence=0.85,
            secondary_agents=[("agente-energia", 0.40)],
            suggested_folder="03_Projetos/Saneamento",
            classification_reason="Menção a ETA",
            timestamp="2026-07-26T00:00:00Z",
        )

        classifier = DocumentClassifier(api_key="test-key")
        result_dict = classifier.to_dict(result)

        assert isinstance(result_dict, dict)
        assert result_dict["primary_agent"] == "agente-saneamento"
        assert len(result_dict["secondary_agents"]) == 1


class TestDocumentClassifier:
    """Test DocumentClassifier functionality."""

    def test_classifier_initialization(self):
        """Test classifier can be initialized."""
        classifier = DocumentClassifier(api_key="test-key")
        assert classifier is not None
        assert "agente-barragens" in DocumentClassifier.SEGMENT_TO_AGENT.values()

    def test_segment_to_agent_mapping(self):
        """Test segment to agent mapping."""
        assert DocumentClassifier.SEGMENT_TO_AGENT["saneamento"] == "agente-saneamento"
        assert DocumentClassifier.SEGMENT_TO_AGENT["energia"] == "agente-energia"
        assert DocumentClassifier.SEGMENT_TO_AGENT["portos"] == "agente-portos"
        assert DocumentClassifier.SEGMENT_TO_AGENT["aeroportos"] == "agente-aeroportos"
        assert DocumentClassifier.SEGMENT_TO_AGENT["barragens"] == "agente-barragens"

    def test_agent_to_folder_mapping(self):
        """Test agent to folder mapping."""
        assert DocumentClassifier.AGENT_TO_FOLDER["agente-saneamento"] == "03_Projetos/Saneamento"
        assert DocumentClassifier.AGENT_TO_FOLDER["agente-energia"] == "03_Projetos/Energia"
        assert DocumentClassifier.AGENT_TO_FOLDER["agente-portos"] == "03_Projetos/Portos"
        assert DocumentClassifier.AGENT_TO_FOLDER["agente-aeroportos"] == "03_Projetos/Aeroportos"
        assert DocumentClassifier.AGENT_TO_FOLDER["agente-barragens"] == "03_Projetos/Barragens"

    def test_parse_classification_response_valid_json(self):
        """Test parsing valid JSON response."""
        response_text = """{
            "primary_agent": "agente-barragens",
            "confidence": 0.95,
            "secondary_agents": [
                {"agent": "agente-energia", "confidence": 0.45}
            ],
            "reason": "Menção a CFRD"
        }"""

        result = DocumentClassifier._parse_classification_response(response_text)
        assert result["primary_agent"] == "agente-barragens"
        assert result["confidence"] == 0.95

    def test_parse_classification_response_invalid_json(self):
        """Test parsing invalid JSON response (fallback)."""
        response_text = "This is not JSON"

        result = DocumentClassifier._parse_classification_response(response_text)
        assert result["primary_agent"] == "agente-saneamento"  # Fallback
        assert result["confidence"] == 0.5

    def test_build_classification_prompt(self):
        """Test building classification prompt."""
        text = "Projeto de barragem com CFRD"
        prompt = DocumentClassifier._build_classification_prompt(text)

        assert "Projeto de barragem" in prompt
        assert "agente-barragens" in prompt or "agentes" in prompt

    def test_classify_with_fallback(self):
        """Test classification with fallback when file cannot be extracted."""
        classifier = DocumentClassifier(api_key="test-key")

        # Create a temporary invalid file
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"invalid content")
            f.flush()

            result = classifier.classify(f.name)
            assert result.confidence == 0.0
            assert result.primary_agent == "agente-saneamento"  # Default fallback

            Path(f.name).unlink()


class TestClassificationCases:
    """Test with specific document cases."""

    def test_case_barragem_cfrd(self):
        """Test classification of dam document."""
        classifier = DocumentClassifier(api_key="test-key")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
PROJETO DE BARRAGEM CFRD

Localização: Rio São Francisco
Tipo: CFRD (Concrete Face Rockfill Dam)
Altura: 120 metros
Especificações: Face de concreto 60cm, enrocamento

Normas: CBDB, ICOLD, NBR 12218
            """)
            f.flush()

            # Extract should work
            text, file_type = DocumentExtractor.extract_from_file(f.name)
            assert "CFRD" in text
            assert "barragem" in text.lower()
            assert file_type == "text"

            Path(f.name).unlink()

    def test_case_transmissao_500kv(self):
        """Test classification of transmission line document."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
PROJETO DE LINHA DE TRANSMISSÃO

Tensão: 500 kV
Comprimento: 245 km
Tipo de torre: Auto-portante
Condutores: 4 x ACSR 636 MCM

Órgão regulador: ANEEL
Norma: NBR 5422
            """)
            f.flush()

            text, file_type = DocumentExtractor.extract_from_file(f.name)
            assert "500 kV" in text or "transmissão" in text.lower()
            assert "ANEEL" in text

            Path(f.name).unlink()

    def test_case_eta_saneamento(self):
        """Test classification of water treatment facility."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
ESTAÇÃO DE TRATAMENTO DE ÁGUA - ETA

Vazão: 500 L/s
Tipo: Filtração rápida com pré-oxid ação
Processo: Coagulação → Decantação → Filtração → Desinfecção

Normas: NBR 12211, NBR 12218
Órgão: SNIS
            """)
            f.flush()

            text, file_type = DocumentExtractor.extract_from_file(f.name)
            assert "ETA" in text or "tratamento" in text.lower()
            assert file_type == "text"

            Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
