"""
Manta Integration Client — Cliente para integração com agentes S1-S10
Orquestra chamadas para manta-05, manta-06 e agentes especializados
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ValidationRequest:
    """Request para validar constante via agente especializado"""
    constant_id: str
    segment: str  # S6-S10
    value: float
    formula: str
    confidence: float

@dataclass
class ValidationResponse:
    """Response da validação"""
    constant_id: str
    agent: str
    approved: bool
    confidence: float
    feedback: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class MantaIntegrationClient:
    """Cliente para chamar agentes Manta dentro do KB Evoluído"""

    AGENT_MAPPING = {
        "S6": "agente-portos",
        "S7": "agente-aeroportos",
        "S8": "agente-saneamento",
        "S9": "agente-energia",
        "S10": "agente-barragens"
    }

    def __init__(self, supabase_url: str, api_key: str):
        """Inicializa cliente"""
        self.supabase_url = supabase_url
        self.api_key = api_key
        self.session_id = None
        logger.info("MantaIntegrationClient inicializado")

    def validate_constant(self, req: ValidationRequest) -> ValidationResponse:
        """Valida constante técnica via agente especializado"""
        agent_name = self.AGENT_MAPPING.get(req.segment)

        if not agent_name:
            logger.error(f"Segmento desconhecido: {req.segment}")
            return ValidationResponse(
                constant_id=req.constant_id,
                agent="UNKNOWN",
                approved=False,
                confidence=0.0,
                feedback="Segmento não mapeado"
            )

        logger.info(f"Validando {req.constant_id} com {agent_name}")

        # Em produção: chamar agente via MCP/REST
        # Simular resposta aqui
        response = ValidationResponse(
            constant_id=req.constant_id,
            agent=agent_name,
            approved=req.confidence >= 0.70,
            confidence=req.confidence,
            feedback=f"Validado por {agent_name}"
        )

        logger.info(f"Resposta: {response.approved} (confidence={response.confidence})")
        return response

    def call_manta_05(self, project_id: str, data: Dict) -> Dict:
        """Chama Manta 05 (Orçamento) para validar custos"""
        logger.info(f"Chamando manta-05 para projeto {project_id}")

        # Simular chamada
        return {
            "project_id": project_id,
            "status": "UPDATED",
            "budget_variance": 0.03,
            "feedback": "Custos validados"
        }

    def call_manta_06(self, project_id: str, models: List[str]) -> Dict:
        """Chama Manta 06 (Modelagem) para validar parâmetros"""
        logger.info(f"Chamando manta-06 para projeto {project_id}")

        # Simular chamada
        return {
            "project_id": project_id,
            "status": "VALIDATED",
            "models_checked": len(models),
            "feedback": "Modelos validados"
        }

    def log_validation(self, response: ValidationResponse):
        """Loga validação em Supabase"""
        logger.info(f"Loggando validação: {response.constant_id} → {response.approved}")

        # Em produção: INSERT em kb.model_feedback
        payload = {
            "constant_id": response.constant_id,
            "agent": response.agent,
            "approved": response.approved,
            "confidence": response.confidence,
            "feedback": response.feedback,
            "timestamp": response.timestamp
        }

        logger.debug(f"Payload: {json.dumps(payload)}")

        return payload

# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Inicializar cliente
    client = MantaIntegrationClient(
        supabase_url="https://xxxxx.supabase.co",
        api_key="xxxxx"
    )

    # Validar constante S8
    req = ValidationRequest(
        constant_id="san:K_RECICLAGEM_UASB_0850",
        segment="S8",
        value=0.85,
        formula="K = (V_rec / V_entrada) * 100",
        confidence=0.92
    )

    resp = client.validate_constant(req)
    client.log_validation(resp)

    # Chamar manta-05
    budget_check = client.call_manta_05("proj_001", {"total_cost": 1500000})
    logger.info(f"Orçamento: {budget_check}")

    # Chamar manta-06
    model_check = client.call_manta_06("proj_001", ["modelo_1", "modelo_2"])
    logger.info(f"Modelos: {model_check}")
