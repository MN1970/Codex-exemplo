#!/usr/bin/env python3
"""
Phase 2.3: Document Auto-Classification
Analyzes uploaded documents and classifies them to appropriate agents.
"""

import io
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import anthropic
    from pypdf import PdfReader
    import pytesseract
    from PIL import Image
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install anthropic pypdf pytesseract pillow")


logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Document classification result."""
    file_name: str
    file_type: str
    extracted_text: str
    primary_agent: str
    confidence: float
    secondary_agents: List[Tuple[str, float]]
    suggested_folder: str
    classification_reason: str
    timestamp: str


class DocumentExtractor:
    """Extract text from various document formats."""

    @staticmethod
    def extract_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                text = ""
                for page_num, page in enumerate(reader.pages[:3]):  # First 3 pages only
                    text += f"\n--- PAGE {page_num + 1} ---\n"
                    text += page.extract_text() or ""
            return text[:2000]  # First 2000 chars
        except Exception as e:
            logger.error(f"Failed to extract PDF: {e}")
            return ""

    @staticmethod
    def extract_image(file_path: str) -> str:
        """Extract text from image using OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text[:2000]
        except Exception as e:
            logger.error(f"Failed to extract image text: {e}")
            return ""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract text from text file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[:2000]
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return ""

    @classmethod
    def extract_from_file(cls, file_path: str) -> Tuple[str, str]:
        """Extract text based on file type.

        Returns: (text, file_type)
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return cls.extract_pdf(file_path), "pdf"
        elif suffix in [".png", ".jpg", ".jpeg"]:
            return cls.extract_image(file_path), "image"
        elif suffix in [".txt", ".md", ".docx"]:
            return cls.extract_text(file_path), "text"
        else:
            return "", "unknown"


class DocumentClassifier:
    """Classify documents to appropriate agents."""

    # Mapping of segments to agent slugs
    SEGMENT_TO_AGENT = {
        "saneamento": "agente-saneamento",
        "energia": "agente-energia",
        "portos": "agente-portos",
        "aeroportos": "agente-aeroportos",
        "barragens": "agente-barragens",
        "rodovia": "agente-rodovia",
    }

    # Mapping of agent slugs to SharePoint folders
    AGENT_TO_FOLDER = {
        "agente-saneamento": "03_Projetos/Saneamento",
        "agente-energia": "03_Projetos/Energia",
        "agente-portos": "03_Projetos/Portos",
        "agente-aeroportos": "03_Projetos/Aeroportos",
        "agente-barragens": "03_Projetos/Barragens",
        "agente-rodovia": "03_Projetos/Rodovias",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize classifier with Anthropic client."""
        self.client = anthropic.Anthropic(api_key=api_key)

    def classify(self, file_path: str) -> ClassificationResult:
        """Classify a document to the appropriate agent."""
        logger.info(f"Classifying document: {file_path}")

        # Extract text
        extracted_text, file_type = DocumentExtractor.extract_from_file(file_path)
        if not extracted_text:
            logger.warning(f"Could not extract text from {file_path}")
            return ClassificationResult(
                file_name=Path(file_path).name,
                file_type=file_type,
                extracted_text="",
                primary_agent="agente-saneamento",  # Default fallback
                confidence=0.0,
                secondary_agents=[],
                suggested_folder=self.AGENT_TO_FOLDER["agente-saneamento"],
                classification_reason="Could not extract text",
                timestamp=datetime.utcnow().isoformat(),
            )

        # Call Claude for classification
        prompt = self._build_classification_prompt(extracted_text)
        response = self.client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=500,
            system="""Você é especialista em classificar documentos de infraestrutura.
            Analise o documento e classifique-o para o agente mais apropriado.

            Agentes disponíveis:
            - agente-saneamento: água, esgoto, drenagem, AySA
            - agente-energia: transmissão, distribuição, subestações, ANEEL
            - agente-portos: portos, hidrovias, ANTAQ
            - agente-aeroportos: aeroportos, pistas, ANAC
            - agente-barragens: barragens, vertedouros, ICOLD
            - agente-rodovia: rodovias, pavimentos, DNIT

            Responda em JSON com este formato:
            {
              "primary_agent": "agente-xxx",
              "confidence": 0.95,
              "secondary_agents": [
                {"agent": "agente-yyy", "confidence": 0.45}
              ],
              "reason": "Breve explicação"
            }""",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        # Parse response
        response_text = response.content[0].text
        classification_data = self._parse_classification_response(response_text)

        # Build result
        primary_agent = classification_data.get("primary_agent", "agente-saneamento")
        confidence = classification_data.get("confidence", 0.0)
        secondary_agents = [
            (agent["agent"], agent["confidence"])
            for agent in classification_data.get("secondary_agents", [])
        ]
        reason = classification_data.get("reason", "")

        result = ClassificationResult(
            file_name=Path(file_path).name,
            file_type=file_type,
            extracted_text=extracted_text,
            primary_agent=primary_agent,
            confidence=confidence,
            secondary_agents=secondary_agents,
            suggested_folder=self.AGENT_TO_FOLDER.get(primary_agent, "03_Projetos"),
            classification_reason=reason,
            timestamp=datetime.utcnow().isoformat(),
        )

        logger.info(f"Classification complete: {primary_agent} ({confidence:.1%})")
        return result

    @staticmethod
    def _build_classification_prompt(extracted_text: str) -> str:
        """Build prompt for document classification."""
        return f"""Analise este documento e classifique-o para o agente mais apropriado:

DOCUMENTO:
{extracted_text}

Classifique para um dos agentes mencionados baseado no conteúdo.
Retorne JSON com primary_agent, confidence (0-1), secondary_agents, e reason."""

    @staticmethod
    def _parse_classification_response(response_text: str) -> Dict:
        """Parse JSON response from Claude."""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Fallback
        return {
            "primary_agent": "agente-saneamento",
            "confidence": 0.5,
            "secondary_agents": [],
            "reason": "Could not parse classification"
        }

    def to_dict(self, result: ClassificationResult) -> Dict:
        """Convert result to dictionary."""
        return {
            "file_name": result.file_name,
            "file_type": result.file_type,
            "primary_agent": result.primary_agent,
            "confidence": result.confidence,
            "secondary_agents": [
                {"agent": agent, "confidence": conf}
                for agent, conf in result.secondary_agents
            ],
            "suggested_folder": result.suggested_folder,
            "classification_reason": result.classification_reason,
            "timestamp": result.timestamp,
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test with a sample document
    classifier = DocumentClassifier()

    # Create a test PDF file (if needed)
    test_file = "/tmp/test_document.txt"
    with open(test_file, "w") as f:
        f.write("""
        PROJETO DE BARRAGEM CFRD

        Localização: Rio São Francisco
        Tipo: CFRD (Concrete Face Rockfill Dam)
        Altura: 120 metros
        Comprimento: 450 metros

        ESPECIFICAÇÕES:
        - Fundações em rocha: profundidade 25m
        - Face de concreto: 60cm
        - Enrocamento: T1/T2 com permeabilidade
        - Vertedouro: 5.000 m³/s

        CRONOGRAMA:
        - Fase 1: Desvio de rio (6 meses)
        - Fase 2: Construção estrutura (24 meses)
        - Fase 3: Enchimento (6 meses)

        Normas aplicáveis: CBDB, ICOLD, NBR 12218
        """)

    result = classifier.classify(test_file)
    print(f"\n=== Classification Result ===")
    print(f"File: {result.file_name}")
    print(f"Primary Agent: {result.primary_agent} ({result.confidence:.1%})")
    print(f"Suggested Folder: {result.suggested_folder}")
    print(f"Reason: {result.classification_reason}")
    if result.secondary_agents:
        print(f"Secondary Agents:")
        for agent, conf in result.secondary_agents:
            print(f"  - {agent}: {conf:.1%}")

    # Cleanup
    os.remove(test_file)
