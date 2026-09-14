"""
Maestro OS — D3 Model Fallback Policy
Regra de fallback de tier de modelo (ADR D1-D4, D3), corrigida
2026-09-13 contra o código real do repositório.

Regra:
- Haiku <-> Sonnet: fallback livre em qualquer direção. Só log
  informativo, sem aviso ao usuário.
- Opus: agentes cujo frontmatter declara `model: opus` (hoje:
  agente-claims, agente-advisory, agente-arquiteto-ia — ver
  `opus_required_agents` na config, não hardcoded aqui) NUNCA
  degradam automaticamente quando `tier_requested == "opus"`.
  Em vez disso, retry com backoff via `RateLimiter`
  (`src/maestro/queue_executor.py`, reaproveitado por composição).
  Se os retries se esgotarem, retorna
  `status="awaiting_human_decision"` com `tier_used=None` — nunca
  degrada silenciosamente para um tier inferior.
- Nunca faz upgrade automático de tier (ex.: Haiku escalando sozinho
  para Opus). Isso é uma decisão de custo que exige aprovação humana.

Nota: `scripts/fallback_strategy.py` (auto-escalonamento de segmento
vertical para Opus, via cadeia de Markov) foi avaliado e descartado
como base para este módulo — resolve outro problema e faz o oposto
do que o D3 pede (escala sem gate humano). Não é usado aqui.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Iterable, Optional

from .queue_executor import RateLimiter

logger = logging.getLogger("maestro.model_fallback")

TIER_ORDER = ("haiku", "sonnet", "opus")


@dataclass
class FallbackDecision:
    """Resultado de uma decisão de tier — estruturado para log/auditoria.

    `status` é um de: "ok" (tier_used definido, sem degradação),
    "degraded" (fallback aplicado, tier_used < tier_requested),
    "awaiting_human_decision" (Opus indisponível, retries esgotados,
    tier_used=None — nada deve ser gerado com tier inferior).
    """
    agent_slug: str
    tier_requested: str
    tier_used: Optional[str]
    status: str
    reason: str
    escalation_notified_human: bool = False
    retries_attempted: int = 0

    def as_log_dict(self) -> dict:
        """Formato pronto para quem for logar (D4) ou notificar (F5)."""
        return {
            "agent_slug": self.agent_slug,
            "tier_requested": self.tier_requested,
            "tier_used": self.tier_used,
            "status": self.status,
            "reason": self.reason,
            "escalation_notified_human": self.escalation_notified_human,
        }


class ModelTierPolicy:
    """
    Decide qual tier de modelo usar para um agente, aplicando o
    fallback assimétrico do D3.

    Uso:
        policy = ModelTierPolicy(opus_required_agents=["agente-claims", ...])
        decision = await policy.resolve(
            agent_slug="agente-claims",
            tier_requested="opus",
            model_call=lambda tier: invoke_model(tier),
        )

    `opus_required_agents` é passada explicitamente (lista de slugs
    cujo frontmatter `model:` é `opus`) em vez de reler os `.md` em
    runtime — quem monta o Orchestrator é responsável por manter essa
    lista sincronizada com `.claude/agents/*.md` (D2 cobre esse
    sync de forma mais ampla).
    """

    def __init__(
        self,
        opus_required_agents: Optional[Iterable[str]] = None,
        max_opus_retries: int = 4,
    ):
        self.opus_required_agents = set(opus_required_agents or ())
        self.rate_limiter = RateLimiter(max_retries=max_opus_retries)

    def _requires_opus_no_fallback(self, agent_slug: str, tier_requested: str) -> bool:
        return tier_requested == "opus" and agent_slug in self.opus_required_agents

    async def resolve(
        self,
        agent_slug: str,
        tier_requested: str,
        model_call=None,
    ) -> FallbackDecision:
        """
        Resolve o tier efetivo para uma chamada.

        Args:
            agent_slug: slug do agente (e.g. "agente-claims")
            tier_requested: "haiku" | "sonnet" | "opus"
            model_call: callable opcional `async def(tier) -> Any` que
                tenta de fato invocar o modelo no tier dado. Se None,
                assume-se que a checagem é só de política (sem I/O) e
                `tier_used == tier_requested` em caso de sucesso trivial.

        Returns:
            FallbackDecision
        """
        if tier_requested not in TIER_ORDER:
            raise ValueError(f"tier_requested inválido: {tier_requested!r}")

        if self._requires_opus_no_fallback(agent_slug, tier_requested):
            return await self._resolve_opus_no_fallback(agent_slug, tier_requested, model_call)

        # Haiku <-> Sonnet (ou Opus não-crítico): fallback livre, log informativo.
        if model_call is None:
            logger.info(
                "tier_ok agent=%s tier_requested=%s tier_used=%s",
                agent_slug, tier_requested, tier_requested,
            )
            return FallbackDecision(
                agent_slug=agent_slug,
                tier_requested=tier_requested,
                tier_used=tier_requested,
                status="ok",
                reason="tier disponível, sem fallback necessário",
            )

        try:
            await model_call(tier_requested)
            return FallbackDecision(
                agent_slug=agent_slug,
                tier_requested=tier_requested,
                tier_used=tier_requested,
                status="ok",
                reason="tier disponível, sem fallback necessário",
            )
        except Exception as exc:
            fallback_tier = self._free_fallback_tier(tier_requested)
            if fallback_tier is None:
                # Não há tier inferior livre para degradar (ex.: já é haiku).
                logger.warning(
                    "tier_unavailable_no_fallback agent=%s tier_requested=%s error=%s",
                    agent_slug, tier_requested, exc,
                )
                return FallbackDecision(
                    agent_slug=agent_slug,
                    tier_requested=tier_requested,
                    tier_used=None,
                    status="awaiting_human_decision",
                    reason=f"tier indisponível e sem fallback livre mais baixo: {exc}",
                )

            logger.info(
                "tier_fallback agent=%s tier_requested=%s tier_used=%s reason=%s",
                agent_slug, tier_requested, fallback_tier, exc,
            )
            return FallbackDecision(
                agent_slug=agent_slug,
                tier_requested=tier_requested,
                tier_used=fallback_tier,
                status="degraded",
                reason=f"fallback livre haiku<->sonnet: {exc}",
            )

    def _free_fallback_tier(self, tier_requested: str) -> Optional[str]:
        """Fallback livre é só entre haiku e sonnet, nunca upgrade, nunca para/de opus aqui."""
        if tier_requested == "sonnet":
            return "haiku"
        if tier_requested == "haiku":
            return None  # já é o tier mais baixo, nada abaixo para degradar
        return None

    async def _resolve_opus_no_fallback(
        self,
        agent_slug: str,
        tier_requested: str,
        model_call,
    ) -> FallbackDecision:
        """
        Opus para agente crítico (claims/advisory/arquiteto-ia): sem
        degradação automática. Retry com backoff (RateLimiter
        reaproveitado de queue_executor.py). Esgotados os retries,
        retorna awaiting_human_decision — nunca gera com tier inferior.
        """
        if model_call is None:
            # Nenhuma chamada real para testar — nada a fazer além de
            # confirmar a política (usado em testes/dry-run).
            return FallbackDecision(
                agent_slug=agent_slug,
                tier_requested=tier_requested,
                tier_used=tier_requested,
                status="ok",
                reason="opus disponível (sem model_call, política apenas)",
            )

        last_error: Optional[Exception] = None
        retries_attempted = 0

        while not self.rate_limiter.is_exhausted():
            await self.rate_limiter.wait_if_throttled()
            try:
                await model_call(tier_requested)
                self.rate_limiter.record_success()
                return FallbackDecision(
                    agent_slug=agent_slug,
                    tier_requested=tier_requested,
                    tier_used=tier_requested,
                    status="ok",
                    reason="opus disponível após retry" if retries_attempted else "opus disponível",
                    retries_attempted=retries_attempted,
                )
            except Exception as exc:
                last_error = exc
                retries_attempted += 1
                self.rate_limiter.record_rate_limit()

        logger.error(
            "opus_unavailable_awaiting_human agent=%s retries=%s error=%s",
            agent_slug, retries_attempted, last_error,
        )
        return FallbackDecision(
            agent_slug=agent_slug,
            tier_requested=tier_requested,
            tier_used=None,
            status="awaiting_human_decision",
            reason=(
                f"Opus indisponível após {retries_attempted} retries — "
                f"agente {agent_slug} não permite fallback automático "
                f"(último erro: {last_error})"
            ),
            escalation_notified_human=False,
            retries_attempted=retries_attempted,
        )
