#!/usr/bin/env python3
"""
agent_memory_purge.py — Executa purga agendada de agent_memory (R10 / D4)

Correção D4 (2026-09-13, ver docs/ADR-D1-D4-DECISOES-ARQUITETURAIS.md,
seção "Correção de diagnóstico — 2026-09-13"):

  A versão anterior deste script era MOCKADA: `get_current_memory_metrics()`
  retornava um dict hardcoded e o branch de execução real (`dry_run=False`)
  só setava números fixos com o comentário `# Real execution would go here`
  — nunca chamava o Supabase de fato.

  Esta versão reaproveita a implementação REAL já existente em
  `scripts/agent_memory_cleanup.py` (`MemoryCleanupDB` / SQL via psycopg2,
  `MemoryCleanupOrchestrator`) em vez de duplicar a lógica de limpeza —
  este arquivo não é editado, só importado. `agent_memory_purge.py` passa a
  ser apenas a camada de orquestração "para todos os agentes com cache
  ativo" + relatório/alerta no formato que `agent_memory_purge_job.py` e o
  job agendado (APScheduler/cron) já esperam.

  --dry-run agora é real: propaga para `MemoryCleanupOrchestrator(dry_run=...)`,
  que por sua vez propaga para `MemoryCleanupDB.execute_cleanup(dry_run=...)` —
  em dry-run nenhum DELETE/INSERT é executado (ver agent_memory_cleanup.py).

Cleanup rules aplicadas (mesma fonte de verdade de agent_memory_cleanup.py,
não redefinidas aqui):
  1. Delete expired entries (expires_at <= NOW())
  2. Archive low-rating entries (user_rating < 2, age > 7 days) → agent_memory_archive
  3. LRU eviction se quota > 80%

Agendamento (APScheduler / cron):
  trigger = create_trigger(
    name="agent-memory-purge-daily",
    cron="0 3 * * *",  # Todos os dias às 03:00 UTC
    prompt="Execute purga de agent_memory conforme R10/D4"
  )

Inputs:
  --supabase-url: URL do Supabase (env: SUPABASE_URL)
  --supabase-key: API key (env: SUPABASE_KEY)
  --agent-id: Agente específico (default: ALL — todo agent_id presente em
              agent_memory_quota, consultado em tempo real, não mais uma
              lista fixa)
  --dry-run: Simula purga sem deletar (default: False) — agora real
  --slack-webhook: URL webhook Slack (env: SLACK_WEBHOOK_URL)

Output:
  - Rows deletadas/arquivadas em agent_memory (via agent_memory_cleanup.py)
  - Métricas antes/depois via agent_memory_quota (consulta real)
  - Slack notification (se bytes_freed > 10GB ou rows_deleted > 10000)

Exit codes:
  0: Sucesso
  1: Erro crítico
"""

import sys
import os
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
import time

# Reaproveita a implementação real de agent_memory_cleanup.py em vez de
# duplicar SQL de DELETE/archive/LRU aqui (ver correção D4 acima).
sys.path.insert(0, str(Path(__file__).parent))
from agent_memory_cleanup import MemoryCleanupDB, MemoryCleanupOrchestrator  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class AgentMemoryPurger:
    """
    Executa purga agendada de agent_memory conforme R10/D4, reaproveitando
    MemoryCleanupDB/MemoryCleanupOrchestrator (agent_memory_cleanup.py) como
    única fonte de verdade de como o purge real é executado.
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        agent_id: Optional[str] = None,
        dry_run: bool = False,
        slack_webhook: Optional[str] = None
    ):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.agent_id = agent_id
        self.dry_run = dry_run
        self.slack_webhook = slack_webhook
        self.repo_root = Path(__file__).parent.parent

        self.db: Optional[MemoryCleanupDB] = None
        self.orchestrator: Optional[MemoryCleanupOrchestrator] = None

        # Métricas coletadas
        self.total_rows_deleted = 0
        self.total_bytes_freed = 0
        self.agents_purged: List[str] = []
        self.agents_failed: List[str] = []
        self.purge_start_time = None
        self.purge_end_time = None

    def _connect(self) -> Tuple[MemoryCleanupDB, MemoryCleanupOrchestrator]:
        """Conecta (uma vez) ao Supabase real via MemoryCleanupDB."""
        if self.db is None:
            self.db = MemoryCleanupDB(self.supabase_url, self.supabase_key)
            self.orchestrator = MemoryCleanupOrchestrator(
                self.db,
                dry_run=self.dry_run,
                slack_webhook=self.slack_webhook
            )
        return self.db, self.orchestrator

    def get_target_agent_ids(self) -> List[str]:
        """
        Lista real de agent_ids a processar.

        Antes: lista fixa hardcoded (manta-03-s1/s2/s8). Agora: se
        --agent-id foi passado, processa só ele; senão consulta
        `agent_memory_quota` (mesma tabela usada por
        MemoryCleanupDB.get_quota_status) para descobrir, em tempo real,
        quais agentes têm cache ativo hoje.
        """
        if self.agent_id:
            return [self.agent_id]

        db, _ = self._connect()
        conn = db.get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT agent_id FROM agent_memory_quota ORDER BY agent_id")
                return [row[0] for row in cur.fetchall()]
        finally:
            db.return_conn(conn)

    def get_current_memory_metrics(self, agent_ids: List[str]) -> Dict[str, Dict]:
        """
        Consulta métricas REAIS de quota por agente (get_quota_status(),
        já implementado em agent_memory_cleanup.py) — substitui o dict
        hardcoded da versão anterior (ver correção D4 no topo do arquivo).
        """
        db, _ = self._connect()
        metrics: Dict[str, Dict] = {}
        for agent_id in agent_ids:
            status = db.get_quota_status(agent_id)
            if status:
                metrics[agent_id] = {
                    "memory_mb": status["current_memory_mb"],
                    "chunk_count": status["chunk_count"],
                    "quota_pct": status["quota_pct"],
                }
        return metrics

    def execute_purge(self) -> bool:
        """
        Executa a purga real, agente a agente, via
        MemoryCleanupOrchestrator.execute_cleanup_for_agent (regras 1-3 de
        agent_memory_cleanup.py). Em --dry-run, nenhuma escrita ocorre —
        a flag é propagada de ponta a ponta até os DELETE/INSERT reais.
        """
        self.purge_start_time = time.time()
        logger.info("=" * 70)
        logger.info("Agent Memory Purge (R10/D4 Policy)")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        logger.info(f"Dry-run mode: {self.dry_run}")
        logger.info("=" * 70)

        try:
            db, orchestrator = self._connect()

            agent_ids = self.get_target_agent_ids()
            if not agent_ids:
                logger.info("Nenhum agent_id encontrado em agent_memory_quota — nada a purgar.")
                self.purge_end_time = time.time()
                return True

            metrics_before = self.get_current_memory_metrics(agent_ids)
            total_before_mb = sum(m.get("memory_mb", 0) for m in metrics_before.values())
            total_chunks_before = sum(m.get("chunk_count", 0) for m in metrics_before.values())
            logger.info("\nMemory metrics BEFORE purge:")
            logger.info(f"  Total memory: {total_before_mb:.2f} MB")
            logger.info(f"  Total chunks: {total_chunks_before}")
            logger.info(f"  Agents: {len(agent_ids)}")

            logger.info(f"\nExecuting purge for {len(agent_ids)} agent(s) via agent_memory_cleanup...")

            for agent_id in agent_ids:
                result = orchestrator.execute_cleanup_for_agent(agent_id, rule_priority=3)

                if result.get("status") != "success":
                    logger.error(f"Purge failed for {agent_id}: {result.get('error')}")
                    self.agents_failed.append(agent_id)
                    continue

                self.agents_purged.append(agent_id)
                for cleanup_result in result.get("cleanup_results", []):
                    self.total_rows_deleted += cleanup_result.get("deleted_count", 0)
                    freed_mb = cleanup_result.get("freed_mb", 0) or 0
                    self.total_bytes_freed += int(freed_mb * 1024 * 1024)

            bytes_freed_gb = self.total_bytes_freed / (1024 ** 3)
            logger.info("\nPurge results:")
            logger.info(f"  Rows deleted/archived: {self.total_rows_deleted}")
            logger.info(f"  Bytes freed: {self.total_bytes_freed:,} ({bytes_freed_gb:.2f} GB)")
            logger.info(f"  Agents affected: {len(self.agents_purged)}")
            if self.agents_failed:
                logger.warning(f"  Agents failed: {self.agents_failed}")

            # Check for alerts
            should_alert = (self.total_bytes_freed > 10 * 1024 ** 3 or
                             self.total_rows_deleted > 10000)

            if should_alert and not self.dry_run:
                logger.warning(f"\nAlert threshold exceeded: {bytes_freed_gb:.2f} GB freed")
                self._send_slack_alert(
                    title="Large Agent Memory Purge",
                    metrics={
                        "rows_deleted": self.total_rows_deleted,
                        "bytes_freed_gb": bytes_freed_gb,
                        "agents_affected": len(self.agents_purged)
                    }
                )

            self.purge_end_time = time.time()
            return len(self.agents_failed) == 0

        except Exception as e:
            logger.error(f"Purge failed: {e}", exc_info=True)
            return False
        finally:
            if self.db is not None:
                self.db.close()

    def _send_slack_alert(self, title: str, metrics: Dict) -> None:
        """
        Envia alerta para Slack via webhook.
        """
        if not self.slack_webhook:
            logger.info("Slack webhook not configured, skipping alert")
            return

        try:
            import requests

            payload = {
                "text": f"🚨 {title}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{title}*\n_Automatic purge triggered by R10/D4 policy_"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Rows Deleted*\n{metrics.get('rows_deleted', 0):,}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*GB Freed*\n{metrics.get('bytes_freed_gb', 0):.2f}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Agents Affected*\n{metrics.get('agents_affected', 0)}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Timestamp*\n{datetime.now(timezone.utc).isoformat()}"
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.slack_webhook, json=payload)
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
            else:
                logger.warning(f"Slack alert failed: {response.status_code}")

        except ImportError:
            logger.warning("requests library not available for Slack alerts")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def generate_report(self) -> Dict:
        """
        Gera relatório de purga.
        """
        duration_ms = (self.purge_end_time - self.purge_start_time) * 1000 if self.purge_end_time else None

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": self.dry_run,
            "agent_id": self.agent_id or "ALL",
            "total_rows_deleted": self.total_rows_deleted,
            "total_bytes_freed": self.total_bytes_freed,
            "total_gb_freed": self.total_bytes_freed / (1024 ** 3),
            "agents_purged": self.agents_purged,
            "agents_failed": self.agents_failed,
            "purge_duration_ms": int(duration_ms) if duration_ms else None,
            "policy_applied": "agent_memory_cleanup.rules_1-3 (expired|low_rating_archived|lru_eviction)",
            "executed_by": "system"
        }

    def run(self) -> Tuple[bool, str]:
        """
        Executa purga e retorna status.
        """
        success = self.execute_purge()
        report = self.generate_report()

        logger.info("\n" + "=" * 70)
        logger.info("PURGE REPORT")
        logger.info("=" * 70)
        logger.info(json.dumps(report, indent=2))
        logger.info("=" * 70)

        if success:
            if self.total_rows_deleted == 0:
                return True, "No purge needed (all entries valid)"
            else:
                return True, f"Purged {self.total_rows_deleted} rows ({report['total_gb_freed']:.2f} GB freed)"
        else:
            if self.agents_failed:
                return False, f"Purge failed for agents: {self.agents_failed}"
            return False, "Purge failed"


def main():
    parser = argparse.ArgumentParser(
        description="Execute scheduled purge of agent_memory cache (R10/D4)"
    )
    parser.add_argument(
        "--supabase-url",
        default=os.getenv("SUPABASE_URL"),
        help="Supabase URL"
    )
    parser.add_argument(
        "--supabase-key",
        default=os.getenv("SUPABASE_KEY"),
        help="Supabase API key"
    )
    parser.add_argument(
        "--agent-id",
        help="Specific agent to purge (default: ALL agents found in agent_memory_quota)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate purge without deleting"
    )
    parser.add_argument(
        "--slack-webhook",
        default=os.getenv("SLACK_WEBHOOK_URL"),
        help="Slack webhook URL for alerts"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if not args.supabase_url:
        logger.error("Missing SUPABASE_URL (set via --supabase-url or env)")
        return 1

    if not args.supabase_key:
        logger.error("Missing SUPABASE_KEY (set via --supabase-key or env)")
        return 1

    purger = AgentMemoryPurger(
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key,
        agent_id=args.agent_id,
        dry_run=args.dry_run,
        slack_webhook=args.slack_webhook
    )

    success, message = purger.run()
    logger.info(f"\nResult: {message}")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
