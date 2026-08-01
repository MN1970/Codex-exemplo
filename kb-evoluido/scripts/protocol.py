"""
RAG Refresh Protocol — Notifica agentes quando KB é atualizado
WebSocket + Polling + Retry automático com backoff exponencial
"""

import json
import logging
import asyncio
from typing import Dict, List, Callable, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class RAGRefreshProtocol:
    """Protocolo para sincronizar agentes com KB atualizado"""

    def __init__(self, agents: List[str], supabase_url: str, api_key: str):
        """
        Args:
            agents: Lista de agentes para notificar (S6-S10)
            supabase_url: URL Supabase
            api_key: API key Supabase
        """
        self.agents = agents
        self.supabase_url = supabase_url
        self.api_key = api_key
        self.last_sync = None
        self.retry_config = {
            "max_retries": 4,
            "backoff": [2, 4, 8, 16]  # exponencial: 2s, 4s, 8s, 16s
        }

    def notify_agents(self, kb_version: str, updated_constants: List[str]) -> Dict:
        """Notifica todos os agentes sobre atualização KB"""
        logger.info(f"📢 Notificando agentes sobre KB v{kb_version}")

        notifications = {}

        for agent in self.agents:
            notification = {
                "agent": agent,
                "kb_version": kb_version,
                "constants_updated": updated_constants,
                "timestamp": datetime.now().isoformat(),
                "action": "RELOAD_KB"
            }

            success = self._send_notification(agent, notification)
            notifications[agent] = success

            if success:
                logger.info(f"✅ {agent} notificado")
            else:
                logger.warning(f"⚠️ {agent} não respondeu (retry automático)")

        return notifications

    def _send_notification(self, agent: str, payload: Dict) -> bool:
        """Envia notificação para um agente com retry automático"""
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Em produção: fazer HTTP POST para agente
                logger.debug(f"Tentativa {attempt + 1}: enviando para {agent}")

                # Simular delay de rede
                time.sleep(0.1)

                # Simular sucesso
                return True

            except Exception as e:
                if attempt < self.retry_config["max_retries"] - 1:
                    backoff = self.retry_config["backoff"][attempt]
                    logger.warning(f"Falha (retry em {backoff}s): {str(e)}")
                    time.sleep(backoff)
                else:
                    logger.error(f"Falha após {attempt + 1} tentativas")
                    return False

        return False

    def poll_kb_updates(self, poll_interval: int = 300) -> Dict:
        """Poll KB para detectar atualizações (fallback para webhook)"""
        logger.info(f"📡 Iniciando poll KB (intervalo: {poll_interval}s)")

        updates = {
            "kb_version": "v1.0",
            "last_update": datetime.now().isoformat(),
            "constants_changed": [],
            "agents_notified": 0
        }

        # Em produção: query Supabase kb_audit_log desde last_sync
        # if new entries: notify_agents()

        return updates

    def get_agent_status(self) -> Dict:
        """Retorna status de sincronização de agentes"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents_total": len(self.agents),
            "agents_synced": len([a for a in self.agents]),  # Em produção: query status
            "last_sync": self.last_sync,
            "protocol": "RAG_REFRESH_v1.0"
        }

class WebSocketManager:
    """Gerencia conexões WebSocket para notificações em tempo real"""

    def __init__(self):
        self.connections: Dict[str, List] = {}
        logger.info("WebSocketManager inicializado")

    async def connect(self, agent: str, websocket):
        """Registra agente para notificações"""
        if agent not in self.connections:
            self.connections[agent] = []

        self.connections[agent].append(websocket)
        logger.info(f"Agent {agent} conectado (total: {len(self.connections[agent])})")

    async def disconnect(self, agent: str, websocket):
        """Remove agente da lista de notificações"""
        if agent in self.connections:
            self.connections[agent].remove(websocket)
            logger.info(f"Agent {agent} desconectado")

    async def broadcast(self, message: Dict):
        """Envia mensagem para todos os agentes conectados"""
        logger.info(f"📢 Broadcasting: {message}")

        for agent, connections in self.connections.items():
            for conn in connections:
                try:
                    # Em produção: enviar via WebSocket
                    logger.debug(f"Enviando para {agent}: {json.dumps(message)}")
                except Exception as e:
                    logger.error(f"Erro ao enviar para {agent}: {str(e)}")

# ============================================================================
# EXEMPLO COM FASTAPI WEBSOCKET
# ============================================================================

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    import uvicorn

    app = FastAPI(title="RAG Refresh Protocol")
    manager = WebSocketManager()

    @app.websocket("/ws/agent/{agent_name}")
    async def websocket_endpoint(agent_name: str, websocket: WebSocket):
        """WebSocket endpoint para agentes"""
        await websocket.accept()
        await manager.connect(agent_name, websocket)

        try:
            while True:
                data = await websocket.receive_text()
                logger.info(f"Recebido de {agent_name}: {data}")

                # Processar mensagem (ack, status, etc)
                response = {
                    "agent": agent_name,
                    "message": "ACK",
                    "timestamp": datetime.now().isoformat()
                }

                await websocket.send_json(response)

        except WebSocketDisconnect:
            await manager.disconnect(agent_name, websocket)
            logger.info(f"{agent_name} desconectado")

    @app.post("/kb-updated")
    async def kb_updated(data: Dict):
        """Endpoint para disparar notificação KB atualizado"""
        logger.info(f"KB atualizado: v{data['version']}")

        message = {
            "event": "KB_UPDATED",
            "version": data["version"],
            "constants": data.get("constants", []),
            "timestamp": datetime.now().isoformat()
        }

        await manager.broadcast(message)

        return {"status": "broadcasted", "agents": len(manager.connections)}

    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)
        uvicorn.run(app, host="127.0.0.1", port=8002)

except ImportError:
    logger.warning("FastAPI não instalado para WebSocket mode")

# ============================================================================
# EXEMPLO STANDALONE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    protocol = RAGRefreshProtocol(
        agents=["agente-saneamento", "agente-energia", "agente-portos",
                "agente-aeroportos", "agente-barragens"],
        supabase_url="https://xxxxx.supabase.co",
        api_key="xxxxx"
    )

    # Simular atualização KB
    result = protocol.notify_agents(
        kb_version="v1.1",
        updated_constants=["san:K_RECICLAGEM_UASB", "ene:R_LT_TORRE"]
    )

    logger.info(f"Resultado: {json.dumps(result, indent=2)}")

    # Status
    status = protocol.get_agent_status()
    logger.info(f"Status agentes: {json.dumps(status, indent=2)}")
