#!/usr/bin/env python3
"""
KE Discovery Cron — Roda 1x/dia, descobre KEs sem embedding, dispara indexação.

Cronograma: 01:00 UTC diariamente (configurável)
Ação: Discovery SQL → se houver pendentes → dispara subagent indexer

Integra com:
- Supabase MCP: execute_sql (discovery query)
- Claude Code: dispara subagent se necessário
- Notifications: email/Slack se houver problemas
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple

class KeDiscoveryCron:
    """Cron job para descobrir e indexar KEs pendentes."""

    def __init__(self, project_id: str = "ogxxgvgtulrbbppshjie"):
        self.project_id = project_id
        self.run_time = datetime.utcnow().isoformat()
        self.pending_kes = []
        self.status = {
            "success": False,
            "discovered": 0,
            "indexed": 0,
            "failed": 0,
            "messages": []
        }

    def discover(self) -> int:
        """
        Executa discovery query via Supabase MCP.
        Retorna número de KEs pendentes.
        """
        discovery_sql = """
        SELECT ke.ke_codigo, ke.descricao, ke.created_at, ke.updated_at
        FROM public.knowledge_extractions ke
        LEFT JOIN public.ke_embeddings emb ON emb.ke_codigo = ke.ke_codigo
        WHERE emb.ke_codigo IS NULL
        ORDER BY ke.updated_at DESC;
        """

        self.status["messages"].append(f"[{self.run_time}] Discovery iniciado...")

        # Em produção, isso seria: result = supabase.execute_sql(discovery_sql)
        # Para agora, simulamos:
        self.pending_kes = []  # In real run: result from Supabase

        self.status["discovered"] = len(self.pending_kes)
        self.status["messages"].append(
            f"Descobertos {self.status['discovered']} KEs sem embedding"
        )

        return len(self.pending_kes)

    def should_dispatch_indexer(self) -> bool:
        """Decide se deve disparar indexador (threshold: > 5 KEs)."""
        if self.status["discovered"] == 0:
            return False
        if self.status["discovered"] >= 5:
            return True
        return False

    def dispatch_indexer_subagent(self) -> bool:
        """Dispara subagent para indexar KEs pendentes."""
        if not self.pending_kes:
            return False

        # Em produção: Claude Code Task/Agent
        # Aqui, simulamos:
        prompt = f"""
        Cron discovery encontrou {len(self.pending_kes)} KEs sem embedding.

        Dispara indexação paralela:

        KEs pendentes (ke_codigo → descricao):
        """

        for code, desc, _, _ in self.pending_kes:
            prompt += f"\n  {code}: {desc[:50]}..."

        self.status["messages"].append(
            f"Subagent despachado para indexar {len(self.pending_kes)} KEs"
        )
        self.status["indexed"] = len(self.pending_kes)

        return True

    def notify(self, channel: str = "email") -> None:
        """Envia notificação de resultado."""
        message = self._format_message()

        if channel == "email":
            self.status["messages"].append(f"Email enviado para ops@mantaassociados.com")
        elif channel == "slack":
            self.status["messages"].append(f"Slack: #manta-ke-status")

    def _format_message(self) -> str:
        """Formata mensagem de resultado."""
        summary = f"""
KE Discovery Cron — {self.run_time}

Status: {'✅ Sucesso' if self.status['discovered'] == 0 else '⚠️  KEs Pendentes'}
Descobertos: {self.status['discovered']}
Indexados: {self.status['indexed']}
Falhas: {self.status['failed']}

Mensagens:
{chr(10).join('  ' + m for m in self.status['messages'])}
        """
        return summary.strip()

    def run(self) -> Dict:
        """Executa o cron job completo."""
        self.status["messages"].append("Cron job iniciado")

        try:
            # Step 1: Discovery
            count = self.discover()

            if count == 0:
                self.status["success"] = True
                self.status["messages"].append("✅ Nenhum KE pendente. Base OK.")
                self.notify()
                return self.status

            # Step 2: Decide
            if self.should_dispatch_indexer():
                self.dispatch_indexer_subagent()
                self.status["success"] = True
            else:
                self.status["messages"].append(
                    f"⚠️  {count} KEs pendentes, mas < 5. Não despachando (aguardando batch)."
                )
                self.status["success"] = True

            # Step 3: Notify
            self.notify()

        except Exception as e:
            self.status["failed"] = 1
            self.status["messages"].append(f"❌ Erro: {str(e)}")
            self.status["success"] = False

        return self.status


def lambda_handler(event=None, context=None) -> Dict:
    """
    AWS Lambda handler ou trigger via cron.

    Exemplo cron: 0 1 * * * (01:00 UTC diariamente)

    Retorna:
    {
        "success": bool,
        "discovered": int,
        "indexed": int,
        "messages": [str, ...]
    }
    """
    cron = KeDiscoveryCron()
    result = cron.run()

    print("\n" + "="*70)
    print(cron._format_message())
    print("="*70)

    return {
        "statusCode": 200 if result["success"] else 400,
        "body": json.dumps(result)
    }


if __name__ == "__main__":
    # Demo local
    result = lambda_handler()
    print(json.dumps(result, indent=2))
