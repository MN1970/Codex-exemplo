#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Hook SubagentStop
Grava runs em maestro_runs quando subagente termina (P6 observabilidade).

Este arquivo é acionado automaticamente pelo Claude Code SDK quando:
  - event.type == 'subagent_stop'
  - um agente/subagente completa execução

Integração esperada em .claude/settings.json:
  {
    "hooks": {
      "SubagentStop": {
        "enabled": true,
        "handler": "./.claude/hooks/subagentstop_maestro_observability.py",
        "async": true,
        "timeout_ms": 5000
      }
    }
  }
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[P6-Observability] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('maestro_observability')

try:
    from supabase import create_client, Client
except ImportError:
    logger.warning("supabase-py não instalado. Instale via: pip install supabase-py")
    sys.exit(1)


# =====================================================================
# CONFIGURAÇÃO
# =====================================================================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # service_role key com privilégios

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL e SUPABASE_KEY não definidas em .env")
    sys.exit(1)

# Cached client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Retorna client Supabase singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# =====================================================================
# HELPERS
# =====================================================================

def calculate_run_cost(
    model_tier: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calcula custo USD baseado em input/output tokens e model_tier.
    Preços conforme CLAUDE.md R7 (2026-07-25).

    Args:
        model_tier: 'haiku-4-5' | 'sonnet-5' | 'opus-5'
        input_tokens: Tokens de entrada
        output_tokens: Tokens de saída

    Returns:
        cost_usd: Custo em USD (arredondado para 6 decimais)
    """
    # Preço por 1M de tokens (excl. cache hits, etc.)
    pricing = {
        'haiku-4-5': {
            'input': 0.08,
            'output': 0.24
        },
        'sonnet-5': {
            'input': 3.0,
            'output': 15.0
        },
        'opus-5': {
            'input': 15.0,
            'output': 75.0
        }
    }

    if model_tier not in pricing:
        logger.warning(f"Unknown model_tier: {model_tier}. Usando sonnet-5 como fallback.")
        model_tier = 'sonnet-5'

    rates = pricing[model_tier]
    cost = (input_tokens * rates['input'] / 1_000_000) + \
           (output_tokens * rates['output'] / 1_000_000)

    return round(cost, 6)


def extract_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai e normaliza dados do event SubagentStop.

    Esperado:
    {
        'agent_id': str,
        'skill_id': str,
        'session_id': str,
        'user_id': str,
        'model_tier': str,
        'input_tokens': int,
        'output_tokens': int,
        'latency_ms': int,
        'status': 'success' | 'timeout' | 'error',
        'error_message': str | None,
        'context': {
            'phase': str | None,
            'routing_confidence': float,
            'rag_collection': str | None,
            'rag_reranker_score': float | None,
            'complexity_score': float,
            'fallback_model': str | None,
            'keywords_matched': int
        }
    }
    """
    context = event.get('context', {})

    return {
        'agent_id': event.get('agent_id', 'unknown'),
        'skill_id': event.get('skill_id', 'unknown.v5.0'),
        'session_id': event.get('session_id', ''),
        'user_id': event.get('user_id', '00000000-0000-0000-0000-000000000000'),
        'model_tier': event.get('model_tier', 'sonnet-5'),
        'input_tokens': event.get('input_tokens', 0),
        'output_tokens': event.get('output_tokens', 0),
        'latency_ms': event.get('latency_ms', 0),
        'status': event.get('status', 'unknown'),
        'error_message': event.get('error_message'),
        'phase': context.get('phase'),
        'routing_confidence': context.get('routing_confidence', 0.0),
        'rag_collection': context.get('rag_collection'),
        'rag_reranker_score': context.get('rag_reranker_score'),
        'complexity_score': context.get('complexity_score', 0.0),
        'fallback_model': context.get('fallback_model'),
        'keywords_matched': context.get('keywords_matched', 0)
    }


def validate_run_record(record: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valida record antes de inserir em maestro_runs.

    Returns:
        (is_valid, error_message)
    """
    # Validações básicas
    if not record['session_id']:
        return False, "session_id is required"

    if record['model_tier'] not in ['haiku-4-5', 'sonnet-5', 'opus-5']:
        return False, f"Invalid model_tier: {record['model_tier']}"

    if record['status'] not in ['success', 'timeout', 'error']:
        return False, f"Invalid status: {record['status']}"

    if record['input_tokens'] < 0 or record['output_tokens'] < 0:
        return False, "Tokens cannot be negative"

    if record['latency_ms'] < 0:
        return False, "Latency cannot be negative"

    if record['routing_confidence'] < 0.0 or record['routing_confidence'] > 1.0:
        return False, "routing_confidence must be 0.0-1.0"

    return True, ""


# =====================================================================
# MAIN: GRAVA RUN EM maestro_runs
# =====================================================================

def on_subagent_stop(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hook principal: acionado quando subagente termina.

    Grava run em maestro_runs (tabela imutável P6).

    Args:
        event: Evento SubagentStop com dados de execução

    Returns:
        {
            'success': bool,
            'run_id': str,
            'message': str
        }
    """
    logger.info(f"Hook SubagentStop acionado para agent: {event.get('agent_id', 'unknown')}")

    try:
        # Step 1: Extrair dados do event
        data = extract_event_data(event)
        logger.debug(f"Event data extraído: {data}")

        # Step 2: Calcular custo
        cost_usd = calculate_run_cost(
            data['model_tier'],
            data['input_tokens'],
            data['output_tokens']
        )
        logger.debug(f"Custo calculado: ${cost_usd}")

        # Step 3: Preparar record para maestro_runs
        run_id = str(uuid4())
        record = {
            'run_id': run_id,
            'user_id': data['user_id'],
            'session_id': data['session_id'],
            'agent_id': data['agent_id'],
            'skill_id': data['skill_id'],
            'model_tier': data['model_tier'],
            'input_tokens': data['input_tokens'],
            'output_tokens': data['output_tokens'],
            'cost_usd': cost_usd,
            'latency_ms': data['latency_ms'],
            'status': data['status'],
            'error_message': data['error_message'],
            'phase': data['phase'],
            'routing_confidence': data['routing_confidence'],
            'rag_collection': data['rag_collection'],
            'rag_reranker_score': data['rag_reranker_score'],
            'metadata': {
                'complexity_score': data['complexity_score'],
                'fallback_model': data['fallback_model'],
                'keywords_matched': data['keywords_matched'],
                'hooked_at': datetime.utcnow().isoformat(),
                'hook_version': '5.0'
            }
        }

        logger.debug(f"Record preparado: {json.dumps(record, default=str)}")

        # Step 4: Validar record
        is_valid, error_msg = validate_run_record(record)
        if not is_valid:
            logger.error(f"Validação falhou: {error_msg}")
            return {
                'success': False,
                'run_id': run_id,
                'message': f"Validation failed: {error_msg}"
            }

        # Step 5: Inserir em maestro_runs
        supabase = get_supabase_client()
        result = supabase.table('maestro_runs').insert(record, returning='minimal').execute()

        logger.info(
            f"✓ Run gravada com sucesso: {run_id} "
            f"(agent={data['agent_id']}, status={data['status']}, cost=${cost_usd})"
        )

        return {
            'success': True,
            'run_id': run_id,
            'message': f"Run {run_id} recorded in maestro_runs"
        }

    except Exception as e:
        logger.error(f"✗ Erro ao gravar run: {type(e).__name__}: {e}", exc_info=True)

        # Não deixar falhas de observabilidade impactarem a execução
        return {
            'success': False,
            'run_id': None,
            'message': f"Failed to record run: {str(e)}"
        }


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == '__main__':
    # Teste local: rodar hook com event mock
    mock_event = {
        'agent_id': 'manta-03-s8',
        'skill_id': 'agente-saneamento.v5.0',
        'session_id': 'test-session-001',
        'user_id': '550e8400-e29b-41d4-a716-446655440000',
        'model_tier': 'sonnet-5',
        'input_tokens': 1200,
        'output_tokens': 450,
        'latency_ms': 2500,
        'status': 'success',
        'error_message': None,
        'context': {
            'phase': 'projeto-executivo',
            'routing_confidence': 0.92,
            'rag_collection': 'san:v5.0:chunks',
            'rag_reranker_score': 0.88,
            'complexity_score': 2.5,
            'fallback_model': None,
            'keywords_matched': 3
        }
    }

    logger.info("=" * 70)
    logger.info("TESTE LOCAL: SubagentStop Hook")
    logger.info("=" * 70)

    result = on_subagent_stop(mock_event)

    logger.info(f"Resultado: {json.dumps(result, indent=2)}")
    logger.info("=" * 70)
