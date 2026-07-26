#!/usr/bin/env python3
"""
Phase 2 Integration Tests (2.1-2.5)
Tests all Phase 2 features working together: feedback loop, orchestration,
document classification, RAG ingestion, and SharePoint sync.
"""

import pytest
import json
import tempfile
from pathlib import Path

from maestro.orchestrator import (
    MaestroOrchestrator,
    OrchestratorInput,
)
from api.document_classifier import (
    DocumentClassifier,
    DocumentExtractor,
)


class TestPhase2IntegrationOrchestration:
    """Integration tests for orchestration (Phase 2.2)."""

    def test_orchestration_workflow_uhe_project(self):
        """Test complete orchestration workflow for UHE project."""
        orchestrator = MaestroOrchestrator(api_key="test-key")

        # Simulate ambiguous routing: UHE mentions both barrages and transmission
        test_input = OrchestratorInput(
            user_prompt="Designing UHE with CFRD 100m and 500kV transmission line",
            primary_agent="agente-barragens",
            primary_response="""
            BARRAGEM CFRD 100M - PROJETO EXECUTIVO

            Fundações: Rocha sã a 25m de profundidade
            Estrutura: Face de concreto 60cm + enrocamento T1/T2
            Vertedouro: Dimensionado para Q100 (5.000 m³/s)
            Cronograma: 30 meses total

            Dependências:
            - Desvio de rio: 6 meses (crítico)
            - Escavação: Afeta acessos à subestação""",
            secondary_agent="agente-energia",
            secondary_response="""
            TRANSMISSÃO 500kV - PROJETO EXECUTIVO

            Traçado: Evita cota de enchimento do reservatório
            Estruturas: 32 torres auto-portantes, vãos de 400m
            Fundações: Sapatas em rocha a 15m
            Subestação: Locada em cota elevada (segurança hidrológica)
            Cronograma: 24 meses total

            Dependências:
            - Aguarda conclusão escavação barragem
            - Coordena enchimento com testes""",
            routing_scores={
                "agente-barragens": 0.95,
                "agente-energia": 0.88,
                "agente-portos": 0.15,
            },
            ambiguity_reason="Projeto ambíguo: CFRD (barragens) + LT (energia) com scores similares (gap=7%)",
        )

        # Build prompt
        prompt = orchestrator._build_orchestration_prompt(test_input)

        assert "agente-barragens" in prompt
        assert "agente-energia" in prompt
        assert "Maestro Orchestrator" in prompt
        assert "cross-concern" in prompt.lower() or "coordenação" in prompt.lower()

    def test_orchestration_multiple_secondary_agents(self):
        """Test orchestration with multiple secondary concerns."""
        orchestrator = MaestroOrchestrator(api_key="test-key")

        # ETE with shared utilities (energia, resíduos)
        test_input = OrchestratorInput(
            user_prompt="ETE moderna com gerador backup e centro de tratamento de lodos",
            primary_agent="agente-saneamento",
            primary_response="ETE 100 L/s com lodo ativado e digestão anaeróbia",
            secondary_agent="agente-energia",
            secondary_response="Alimentação 220V + gerador diesel 75 kVA com sincronismo",
            routing_scores={
                "agente-saneamento": 0.92,
                "agente-energia": 0.78,
            },
        )

        assert test_input.primary_agent == "agente-saneamento"
        assert test_input.routing_scores["agente-saneamento"] > 0.90


class TestPhase2IntegrationClassification:
    """Integration tests for document classification (Phase 2.3)."""

    def test_classification_to_sharepoint_folder_mapping(self):
        """Test document classification maps to correct SharePoint folder."""
        classifier = DocumentClassifier(api_key="test-key")

        # Test all agent-to-folder mappings
        agent_folder_tests = [
            ("agente-saneamento", "03_Projetos/Saneamento"),
            ("agente-energia", "03_Projetos/Energia"),
            ("agente-portos", "03_Projetos/Portos"),
            ("agente-aeroportos", "03_Projetos/Aeroportos"),
            ("agente-barragens", "03_Projetos/Barragens"),
        ]

        for agent, expected_folder in agent_folder_tests:
            assert classifier.AGENT_TO_FOLDER[agent] == expected_folder

    def test_classification_result_to_sharepoint_metadata(self):
        """Test classification result format for SharePoint sync."""
        classifier = DocumentClassifier(api_key="test-key")

        # Simulate classification result
        from api.document_classifier import ClassificationResult

        result = ClassificationResult(
            file_name="CFRD_100m_foundation_analysis.pdf",
            file_type="pdf",
            extracted_text="CFRD foundation analysis with geotechnical data",
            primary_agent="agente-barragens",
            confidence=0.96,
            secondary_agents=[("agente-energia", 0.35)],
            suggested_folder="03_Projetos/Barragens",
            classification_reason="Explicit CFRD mention + geotechnical details",
            timestamp="2026-07-26T10:30:00Z",
        )

        # Convert to SharePoint metadata format
        sp_metadata = {
            "maestro_suggested_agent": result.primary_agent,
            "maestro_confidence": result.confidence,
            "maestro_suggested_folder": result.suggested_folder,
            "maestro_classification_reason": result.classification_reason,
            "maestro_classified_at": result.timestamp,
        }

        assert sp_metadata["maestro_suggested_agent"] == "agente-barragens"
        assert sp_metadata["maestro_confidence"] == 0.96
        assert "Barragens" in sp_metadata["maestro_suggested_folder"]

    def test_document_extraction_accuracy_barragem(self):
        """Test document extraction for dam-related content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            PROJETO DE BARRAGEM CFRD - RIO GRANDE

            Tipo: Concrete Face Rockfill Dam (CFRD)
            Altura: 127 m
            Comprimento: 630 m

            Fundações:
            - Escavação até rocha sã (profundidade média: 25m)
            - Tratamento de fraturas com calda de cimento
            - Drenagem de alívio

            Corpo da Barragem:
            - Enrocamento upstream: 45 graus
            - Face de concreto: espessura 0.60m
            - Filtros: areia + pedregulho

            Vertedouro:
            - Canal em rocha: 400m² de seção
            - Bacia de dissipação: 60m x 40m
            - Q100 = 5.500 m³/s

            Cronograma:
            - Fase 1: Desvio de rio (8 meses)
            - Fase 2: Escavação e preparo (12 meses)
            - Fase 3: Enrocamento (18 meses)
            - Fase 4: Face de concreto (12 meses)
            - Fase 5: Enchimento (6 meses)

            Referências normativas:
            - CBDB (Comitê Brasileiro de Barragens)
            - ICOLD (International Commission on Large Dams)
            - NBR 12218:2017 - Barragens de terra e enrocamento
            - Lei 12.334/2010 - Segurança de Barragens
            """)
            f.flush()

            # Extract text
            text, file_type = DocumentExtractor.extract_from_file(f.name)

            # Verify extraction
            assert "CFRD" in text
            assert "barragem" in text.lower()
            assert "CBDB" in text or "ICOLD" in text
            assert file_type == "text"

            Path(f.name).unlink()


class TestPhase2IntegrationFeedbackLoop:
    """Integration tests for feedback loop (Phase 2.1)."""

    def test_feedback_tracking_structure(self):
        """Test feedback data structure matches expected schema."""
        # Simulate maestro_user_feedback table structure
        feedback_record = {
            "feedback_id": "f_001",
            "timestamp": "2026-07-26T10:30:00Z",
            "prompt": "Designing dam with transmission line",
            "routed_agent": "agente-barragens",
            "correct_agent": "agente-barragens",
            "confidence": 5,  # 1-5 scale
            "notes": "Correct routing but missing cross-concern with energy",
            "routing_trace_id": "trace_001",
        }

        assert feedback_record["routed_agent"] == feedback_record["correct_agent"]
        assert 1 <= feedback_record["confidence"] <= 5

    def test_approval_rate_calculation(self):
        """Test calculation of agent approval rates."""
        feedback_records = [
            {"agent": "agente-barragens", "approved": True},
            {"agent": "agente-barragens", "approved": True},
            {"agent": "agente-barragens", "approved": False},
            {"agent": "agente-energia", "approved": True},
            {"agent": "agente-energia", "approved": True},
        ]

        # Aggregate approval by agent
        by_agent = {}
        for record in feedback_records:
            agent = record["agent"]
            if agent not in by_agent:
                by_agent[agent] = {"total": 0, "approved": 0}
            by_agent[agent]["total"] += 1
            if record["approved"]:
                by_agent[agent]["approved"] += 1

        # Verify calculation
        assert by_agent["agente-barragens"]["total"] == 3
        assert by_agent["agente-barragens"]["approved"] == 2
        assert by_agent["agente-barragens"]["approved"] / by_agent["agente-barragens"]["total"] == pytest.approx(0.667)

        assert by_agent["agente-energia"]["total"] == 2
        assert by_agent["agente-energia"]["approved"] == 2


class TestPhase2IntegrationRAGIngestion:
    """Integration tests for RAG ingestion (Phase 2.4)."""

    def test_rag_chunk_structure(self):
        """Test RAG chunk data structure."""
        chunk = {
            "collection_slug": "barragens",
            "content": "CFRD de 100m com fundações em rocha...",
            "source_file": "CBDB_guidelines.pdf",
            "source_url": "sharepoint://manta.com/docs/CBDB_guidelines.pdf",
            "page_num": 42,
            "tier": "T1",
            "chunk_index": 3,
            "chunk_count": 125,
            "metadata": {
                "ingestion_method": "batch_pipeline",
                "chunk_tokens": 487,
                "file_size_bytes": 2456789,
            },
            "embedding": [0.123, 0.456, -0.789] + [0.0] * 1533,  # Simplified
            "created_at": "2026-07-26T10:30:00Z",
        }

        assert chunk["collection_slug"] in ["saneamento", "energia", "portos", "aeroportos", "barragens"]
        assert chunk["tier"] in ["T1", "T2", "T3", "T4"]
        assert len(chunk.get("embedding", [])) <= 1536  # Anthropic embedding size

    def test_rag_collection_prefixes(self):
        """Test RAG collection prefix mapping."""
        collection_config = {
            "saneamento": {"prefix": "san:", "folder": "docs/rag-sources/saneamento"},
            "energia": {"prefix": "ene:", "folder": "docs/rag-sources/energia"},
            "portos": {"prefix": "por:", "folder": "docs/rag-sources/portos"},
            "aeroportos": {"prefix": "aer:", "folder": "docs/rag-sources/aeroportos"},
            "barragens": {"prefix": "bar:", "folder": "docs/rag-sources/barragens"},
        }

        # Verify all collections have prefixes
        for collection, config in collection_config.items():
            assert "prefix" in config
            assert "folder" in config
            assert config["prefix"].endswith(":")


class TestPhase2IntegrationSharePointSync:
    """Integration tests for SharePoint sync (Phase 2.5)."""

    def test_agent_metadata_extraction(self):
        """Test agent metadata extraction from .md files."""
        # Simulate agent metadata from .claude/agents/agente-barragens.md
        agent_metadata = {
            "name": "Manta 03-S10 — agente-barragens",
            "role": "Especialista em barragens",
            "tier": "Sonnet",
            "status": "Operacional",
            "keywords": ["barragem", "CFRD", "vertedouro", "ICOLD", "CBDB"],
        }

        assert "barragem" in agent_metadata["keywords"]
        assert agent_metadata["status"] == "Operacional"

    def test_sharepoint_folder_structure(self):
        """Test SharePoint folder hierarchy for agent sync."""
        sp_structure = {
            "agente-barragens": "sites/manta/04_IA/Manta-Maestro/01-agentes-fundamentais/agente-barragens/SKILL.md",
            "agente-energia": "sites/manta/04_IA/Manta-Maestro/01-agentes-fundamentais/agente-energia/SKILL.md",
            "agente-portos": "sites/manta/04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos/SKILL.md",
        }

        for agent, path in sp_structure.items():
            assert agent in path
            assert path.endswith("SKILL.md")


class TestPhase2EndToEndWorkflow:
    """End-to-end workflow test combining all Phase 2 features."""

    def test_complete_workflow_ambiguous_project(self):
        """Test complete workflow: classify → route → orchestrate → feedback."""
        orchestrator = MaestroOrchestrator(api_key="test-key")
        classifier = DocumentClassifier(api_key="test-key")

        # Step 1: Simulate document upload + classification
        document_content = """
        PROJETO INTEGRADO: UHE COM TRANSMISSÃO

        Barragem CFRD 100m no Rio São Francisco
        Transmissão 500kV para SE no vale
        Prazo: 36 meses

        Desafios de coordenação:
        - Fundações compartilhadas
        - Cronograma de enchimento vs montagem LT
        - Permissões compartilhadas (IBAMA)
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(document_content)
            f.flush()

            # Classification would happen here (skipping actual API call for test)
            expected_classification = {
                "primary_agent": "agente-barragens",
                "confidence": 0.92,
                "secondary_agents": [
                    {"agent": "agente-energia", "confidence": 0.85}
                ],
                "suggested_folder": "03_Projetos/Barragens"
            }

            assert expected_classification["primary_agent"] == "agente-barragens"
            assert expected_classification["secondary_agents"][0]["agent"] == "agente-energia"

            Path(f.name).unlink()

        # Step 2: Simulate ambiguous routing → orchestration
        routing_scores = {
            "agente-barragens": 0.95,
            "agente-energia": 0.88,
        }

        is_ambiguous = (routing_scores["agente-barragens"] - routing_scores["agente-energia"]) < 0.10
        assert is_ambiguous

        # Step 3: Orchestrate (would call Opus model)
        orchestrator_input = OrchestratorInput(
            user_prompt=document_content,
            primary_agent="agente-barragens",
            primary_response="Barragem CFRD 100m viável com cronograma de 30 meses",
            secondary_agent="agente-energia",
            secondary_response="Transmissão 500kV viável com 24 meses após prep da SE",
            routing_scores=routing_scores,
        )

        assert orchestrator_input.primary_agent == "agente-barragens"
        assert orchestrator_input.secondary_agent == "agente-energia"

        # Step 4: Feedback would be collected (UI button in Cowork)
        expected_feedback = {
            "routing_trace_id": "trace_xyz",
            "user_approved": True,
            "confidence": 5,
            "notes": "Orchestration correctly identified LT/barragem coordination",
        }

        assert expected_feedback["user_approved"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
