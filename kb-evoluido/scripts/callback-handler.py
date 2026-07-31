"""
Callback Handler — FastAPI service para capturar rejeições e feedback
Recebe eventos de agentes, detecta padrões, e dispara retraining automático
"""

import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class CallbackHandler:
    """Handler para callbacks de rejeição de constantes"""

    def __init__(self):
        self.rejections = defaultdict(list)
        self.approvals = defaultdict(list)
        self.pattern_threshold = 3  # 3+ rejeições = padrão detectado
        self.pattern_window = timedelta(weeks=2)

    def on_rejection(self, constant_id: str, agent: str, reason: str, confidence: float):
        """Callback quando agente rejeita constante"""
        event = {
            "type": "REJECTION",
            "constant_id": constant_id,
            "agent": agent,
            "reason": reason,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

        self.rejections[constant_id].append(event)
        logger.warning(f"Rejeição: {constant_id} (confidence={confidence}, razão={reason})")

        # Verificar padrão
        pattern = self.detect_pattern(constant_id)
        if pattern:
            logger.error(f"⚠️ PADRÃO DETECTADO: {constant_id} — {len(pattern)} rejeições")
            self.trigger_retraining(constant_id, pattern)

    def on_approval(self, constant_id: str, agent: str, confidence: float):
        """Callback quando agente aprova constante"""
        event = {
            "type": "APPROVAL",
            "constant_id": constant_id,
            "agent": agent,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

        self.approvals[constant_id].append(event)
        logger.info(f"Aprovação: {constant_id} (confidence={confidence})")

    def detect_pattern(self, constant_id: str) -> List[Dict]:
        """Detecta se há padrão de rejeições (3+ em 2 semanas)"""
        if constant_id not in self.rejections:
            return []

        rejections = self.rejections[constant_id]

        # Filtrar últimas 2 semanas
        cutoff = datetime.now() - self.pattern_window
        recent = [r for r in rejections
                  if datetime.fromisoformat(r["timestamp"]) > cutoff]

        if len(recent) >= self.pattern_threshold:
            return recent

        return []

    def trigger_retraining(self, constant_id: str, pattern: List[Dict]):
        """Dispara retraining automático quando padrão detectado"""
        logger.error(f"🔄 Triggering retraining para {constant_id}")

        # Analisar razões comuns
        reasons = defaultdict(int)
        for rejection in pattern:
            reasons[rejection["reason"]] += 1

        top_reason = max(reasons.items(), key=lambda x: x[1])[0]

        retraining_job = {
            "constant_id": constant_id,
            "pattern_detected": True,
            "rejections_count": len(pattern),
            "top_reason": top_reason,
            "action": "RETRAINING_STARTED",
            "timestamp": datetime.now().isoformat()
        }

        # Em produção: criar job no Airflow
        logger.info(f"Retraining job: {json.dumps(retraining_job)}")

        return retraining_job

    def get_feedback_summary(self) -> Dict:
        """Retorna resumo de feedback"""
        total_rejections = sum(len(v) for v in self.rejections.values())
        total_approvals = sum(len(v) for v in self.approvals.values())

        return {
            "timestamp": datetime.now().isoformat(),
            "total_rejections": total_rejections,
            "total_approvals": total_approvals,
            "approval_rate": total_approvals / (total_approvals + total_rejections)
            if (total_approvals + total_rejections) > 0 else 0,
            "patterns_detected": len([c for c in self.rejections.keys()
                                    if self.detect_pattern(c)])
        }

# ============================================================================
# EXEMPLO COM FASTAPI
# ============================================================================

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn

    app = FastAPI(title="KB Evoluído Callback Handler")
    handler = CallbackHandler()

    @app.post("/callback/rejection")
    async def handle_rejection(data: Dict):
        """Endpoint para receber rejeições"""
        try:
            handler.on_rejection(
                constant_id=data["constant_id"],
                agent=data["agent"],
                reason=data["reason"],
                confidence=data["confidence"]
            )
            return {"status": "OK", "action": "logged"}
        except Exception as e:
            logger.error(f"Erro ao processar rejeição: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/callback/approval")
    async def handle_approval(data: Dict):
        """Endpoint para receber aprovações"""
        try:
            handler.on_approval(
                constant_id=data["constant_id"],
                agent=data["agent"],
                confidence=data["confidence"]
            )
            return {"status": "OK", "action": "logged"}
        except Exception as e:
            logger.error(f"Erro ao processar aprovação: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/feedback/summary")
    async def get_summary():
        """Retorna resumo de feedback"""
        return handler.get_feedback_summary()

    @app.get("/health")
    async def health():
        """Health check"""
        return {"status": "OK", "service": "callback-handler"}

    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)
        uvicorn.run(app, host="127.0.0.1", port=8001)

except ImportError:
    # FastAPI não disponível, definir handler básico
    handler = CallbackHandler()
    logger.warning("FastAPI não instalado, executando em modo standalone")

    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)

        # Simular callbacks
        handler.on_rejection("san:K_RECICLAGEM_UASB", "agente-saneamento",
                           "fórmula desatualizada (IWA 2023)", 0.65)
        handler.on_rejection("san:K_RECICLAGEM_UASB", "agente-saneamento",
                           "fórmula desatualizada (IWA 2023)", 0.68)
        handler.on_rejection("san:K_RECICLAGEM_UASB", "agente-saneamento",
                           "fórmula desatualizada (IWA 2023)", 0.70)

        summary = handler.get_feedback_summary()
        logger.info(f"Resumo: {json.dumps(summary, indent=2)}")
