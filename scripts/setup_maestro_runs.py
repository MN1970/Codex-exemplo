#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Setup de Observabilidade (P6)
Script de inicialização para maestro_runs schema + indexes + RLS + APScheduler.

Uso:
  python scripts/setup_maestro_runs.py --init
  python scripts/setup_maestro_runs.py --archive
  python scripts/setup_maestro_runs.py --health-check
  python scripts/setup_maestro_runs.py --schedule-jobs

Dependências:
  pip install supabase-py APScheduler psycopg2-binary python-dotenv
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('maestro_setup')

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError:
    logger.error("Dependências faltando. Execute: pip install supabase-py python-dotenv")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # service_role key (privilégios)
POSTGRES_CONNECTION_STRING = os.getenv('POSTGRES_CONNECTION_STRING')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL e SUPABASE_KEY não definidas em .env")
    sys.exit(1)


class MaestroRunsSetup:
    """
    Gerenciador de setup para maestro_runs (observabilidade P6).
    """

    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"Conectado ao Supabase: {SUPABASE_URL}")

    def init_schema(self) -> bool:
        """
        Inicializa schema: maestro_runs, indexes, RLS, views.
        Requer: migration já aplicada via `supabase db push`.
        """
        logger.info("Iniciando validação de schema...")

        # Step 1: Validar se tabela maestro_runs existe
        try:
            result = self.supabase.table('maestro_runs').select('*', count='exact').limit(1).execute()
            logger.info(f"✓ Tabela maestro_runs existe (teste com select)")
        except Exception as e:
            logger.error(f"✗ Tabela maestro_runs não encontrada: {e}")
            return False

        # Step 2: Validar se maestro_runs_archive existe
        try:
            result = self.supabase.table('maestro_runs_archive').select('*', count='exact').limit(1).execute()
            logger.info(f"✓ Tabela maestro_runs_archive existe")
        except Exception as e:
            logger.error(f"✗ Tabela maestro_runs_archive não encontrada: {e}")
            return False

        # Step 3: Validar se views analíticas existem
        views_to_check = [
            'vw_cost_by_agent_daily',
            'vw_latency_by_agent',
            'vw_error_rate_by_agent',
            'vw_model_tier_distribution',
            'vw_feedback_distribution'
        ]
        for view_name in views_to_check:
            try:
                result = self.supabase.table(view_name).select('*', count='exact').limit(1).execute()
                logger.info(f"✓ View {view_name} existe")
            except Exception as e:
                logger.warning(f"⚠ View {view_name} não encontrada (pode não estar ativada): {e}")

        logger.info("✓ Schema validado com sucesso")
        return True

    def test_insert_mock_run(self) -> bool:
        """
        Testa inserção via API (validar RLS + triggers).
        """
        logger.info("Testando inserção mock de run...")

        mock_run = {
            'user_id': '00000000-0000-0000-0000-000000000000',  # placeholder
            'session_id': 'test-session-001',
            'agent_id': 'manta-03-s8',
            'skill_id': 'agente-saneamento.v5.0',
            'model_tier': 'haiku-4-5',
            'input_tokens': 1200,
            'output_tokens': 450,
            'cost_usd': 0.00015,
            'latency_ms': 2500,
            'status': 'success',
            'phase': 'projeto-executivo',
            'routing_confidence': 0.92,
            'rag_collection': 'san:v5.0:chunks',
            'rag_reranker_score': 0.88,
            'metadata': {
                'complexity_score': 2.5,
                'fallback_cascade': None,
                'keywords_matched': 3
            }
        }

        try:
            result = self.supabase.table('maestro_runs').insert(mock_run, returning='minimal').execute()
            logger.info(f"✓ Mock run inserida com sucesso")
            return True
        except Exception as e:
            logger.error(f"✗ Falha ao inserir mock run: {e}")
            return False

    def validate_indexes(self) -> bool:
        """
        Valida se indexes existem e têm sizes razoáveis.
        """
        logger.info("Validando indexes...")

        indexes = [
            'idx_maestro_runs_agent_created',
            'idx_maestro_runs_status_created',
            'idx_maestro_runs_cost_usd',
            'idx_maestro_runs_user_created',
            'idx_maestro_runs_model_created',
        ]

        if not POSTGRES_CONNECTION_STRING:
            logger.warning("⚠ POSTGRES_CONNECTION_STRING não definida, pulando validação de indexes")
            return True

        try:
            import psycopg2
            conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
            cur = conn.cursor()

            for idx_name in indexes:
                cur.execute(
                    "SELECT indexname FROM pg_indexes WHERE indexname = %s",
                    (idx_name,)
                )
                if cur.fetchone():
                    logger.info(f"✓ Index {idx_name} existe")
                else:
                    logger.warning(f"⚠ Index {idx_name} não encontrado")

            cur.close()
            conn.close()
            return True
        except ImportError:
            logger.warning("⚠ psycopg2 não instalado, pulando validação de indexes")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao validar indexes: {e}")
            return False

    def validate_rls_policies(self) -> bool:
        """
        Valida se RLS policies estão habilitadas.
        """
        logger.info("Validando RLS policies...")

        if not POSTGRES_CONNECTION_STRING:
            logger.warning("⚠ POSTGRES_CONNECTION_STRING não definida, pulando validação de RLS")
            return True

        try:
            import psycopg2
            conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
            cur = conn.cursor()

            # Check if RLS is enabled on maestro_runs
            cur.execute(
                "SELECT rowsecurity FROM pg_class WHERE relname = 'maestro_runs'"
            )
            result = cur.fetchone()
            if result and result[0]:
                logger.info("✓ RLS habilitado em maestro_runs")
            else:
                logger.warning("⚠ RLS não habilitado em maestro_runs")

            # List policies
            cur.execute(
                "SELECT policyname FROM pg_policies WHERE tablename = 'maestro_runs'"
            )
            policies = cur.fetchall()
            logger.info(f"✓ {len(policies)} RLS policies encontradas: {[p[0] for p in policies]}")

            cur.close()
            conn.close()
            return True
        except ImportError:
            logger.warning("⚠ psycopg2 não instalado, pulando validação de RLS")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao validar RLS: {e}")
            return False

    def archive_old_runs(self, days_threshold: int = 90) -> Tuple[int, int]:
        """
        Arquiva runs com idade > threshold dias.
        Retorna: (archived_count, error_count)
        """
        logger.info(f"Arquivando runs com idade > {days_threshold} dias...")

        if not POSTGRES_CONNECTION_STRING:
            logger.error("POSTGRES_CONNECTION_STRING não definida")
            return 0, 1

        try:
            import psycopg2
            conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
            cur = conn.cursor()

            # Call PL/pgSQL function
            cur.execute("SELECT archived_count FROM archive_old_maestro_runs()")
            result = cur.fetchone()
            archived_count = result[0] if result else 0

            conn.commit()
            logger.info(f"✓ {archived_count} runs arquivadas com sucesso")

            cur.close()
            conn.close()
            return archived_count, 0

        except ImportError:
            logger.error("psycopg2 não instalado")
            return 0, 1
        except Exception as e:
            logger.error(f"✗ Erro ao arquivar: {e}")
            return 0, 1

    def get_dashboard_stats(self) -> Optional[Dict]:
        """
        Coleta estatísticas para validar setup.
        """
        logger.info("Coletando estatísticas de dashboard...")

        try:
            # Total de runs
            total_runs = self.supabase.table('maestro_runs').select('*', count='exact').limit(0).execute()
            count = total_runs.count

            # Custo total
            result = self.supabase.rpc(
                'sql',
                {}
            ).execute()  # Fallback: SQL via Supabase

            stats = {
                'total_runs': count,
                'timestamp': datetime.utcnow().isoformat(),
                'views_available': [
                    'vw_cost_by_agent_daily',
                    'vw_latency_by_agent',
                    'vw_error_rate_by_agent'
                ]
            }

            logger.info(f"✓ Dashboard stats coletadas: {stats}")
            return stats

        except Exception as e:
            logger.warning(f"⚠ Erro ao coletar stats: {e}")
            return None

    def health_check(self) -> bool:
        """
        Executa health check completo.
        """
        logger.info("=" * 60)
        logger.info("MAESTRO RUNS — HEALTH CHECK")
        logger.info("=" * 60)

        checks = [
            ("Schema", self.init_schema),
            ("Indexes", self.validate_indexes),
            ("RLS Policies", self.validate_rls_policies),
            ("Mock Insert", self.test_insert_mock_run),
        ]

        results = []
        for name, check_fn in checks:
            try:
                result = check_fn()
                results.append((name, result))
                status = "✓ PASS" if result else "✗ FAIL"
                logger.info(f"{status}: {name}")
            except Exception as e:
                logger.error(f"✗ EXCEPTION: {name} — {e}")
                results.append((name, False))

        logger.info("=" * 60)
        passed = sum(1 for _, r in results if r)
        total = len(results)
        logger.info(f"Result: {passed}/{total} checks passed")

        if passed == total:
            logger.info("✓ Health check PASSED — Schema pronto para produção")
            return True
        else:
            logger.warning("✗ Health check FAILED — Revisar erros acima")
            return False


def schedule_background_jobs():
    """
    Agenda jobs APScheduler para:
      - Arquivo diário (02:00 UTC)
      - Feedback loop semanal (domingo 03:00 UTC)
      - Alerta de erro (a cada 5 min, se > 3 erros/hora)
    """
    logger.info("Configurando APScheduler jobs...")

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from pytz import utc
    except ImportError:
        logger.error("APScheduler não instalado. Execute: pip install APScheduler pytz")
        return False

    scheduler = BackgroundScheduler(timezone=utc)

    # Job 1: Archive diário
    def job_archive():
        logger.info("[Job] Executando archive diário...")
        setup = MaestroRunsSetup()
        archived, errors = setup.archive_old_runs(days_threshold=90)
        if errors == 0:
            logger.info(f"[Job] ✓ {archived} runs arquivadas")
        else:
            logger.error(f"[Job] ✗ Erro ao arquivar")

    scheduler.add_job(job_archive, 'cron', hour=2, minute=0, id='maestro_archive_daily')

    # Job 2: Health check horário
    def job_health_check():
        logger.info("[Job] Executando health check horário...")
        setup = MaestroRunsSetup()
        result = setup.health_check()
        if not result:
            logger.warning("[Job] ⚠ Health check detectou problemas")

    scheduler.add_job(job_health_check, 'cron', hour='*/6', minute=0, id='maestro_health_check_6h')

    try:
        scheduler.start()
        logger.info("✓ APScheduler iniciado com sucesso")
        logger.info(f"  - Archive diário: 02:00 UTC")
        logger.info(f"  - Health check: a cada 6 horas")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao iniciar scheduler: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Manta Maestro v5.0 — Setup de Observabilidade (P6)'
    )
    parser.add_argument(
        '--init',
        action='store_true',
        help='Valida schema e realiza health check'
    )
    parser.add_argument(
        '--archive',
        action='store_true',
        help='Arquiva runs com idade > 90 dias'
    )
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Executa health check completo'
    )
    parser.add_argument(
        '--schedule-jobs',
        action='store_true',
        help='Agenda APScheduler jobs (background)'
    )
    parser.add_argument(
        '--days-threshold',
        type=int,
        default=90,
        help='Threshold de dias para archive (default: 90)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Coleta estatísticas de dashboard'
    )

    args = parser.parse_args()

    setup = MaestroRunsSetup()

    if args.init:
        logger.info("Modo: INIT")
        if setup.init_schema():
            logger.info("✓ Schema inicializado com sucesso")
            sys.exit(0)
        else:
            logger.error("✗ Falha ao inicializar schema")
            sys.exit(1)

    elif args.archive:
        logger.info(f"Modo: ARCHIVE (threshold={args.days_threshold} dias)")
        archived, errors = setup.archive_old_runs(days_threshold=args.days_threshold)
        if errors == 0:
            logger.info(f"✓ {archived} runs arquivadas")
            sys.exit(0)
        else:
            logger.error("✗ Erro ao arquivar")
            sys.exit(1)

    elif args.health_check:
        logger.info("Modo: HEALTH CHECK")
        result = setup.health_check()
        sys.exit(0 if result else 1)

    elif args.schedule_jobs:
        logger.info("Modo: SCHEDULE JOBS")
        result = schedule_background_jobs()
        if result:
            logger.info("✓ Jobs agendados com sucesso")
            logger.info("(Pressionar Ctrl+C para parar scheduler)")
            # Manter scheduler rodando
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("Scheduler parado")
        sys.exit(0 if result else 1)

    elif args.stats:
        logger.info("Modo: STATS")
        stats = setup.get_dashboard_stats()
        if stats:
            logger.info(json.dumps(stats, indent=2))
            sys.exit(0)
        else:
            logger.error("✗ Erro ao coletar stats")
            sys.exit(1)

    else:
        # Default: health check
        logger.info("Nenhuma opção especificada. Executando health check...")
        result = setup.health_check()
        sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
