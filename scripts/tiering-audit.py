#!/usr/bin/env python3
"""
Tiering Audit Script (R7 validation)
Audits tiering decisions against historical runs, validates complexity score formula.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TieringAuditor:
    def __init__(self, repo_root: Path = Path.cwd()):
        self.repo_root = repo_root
        self.claude_md = repo_root / "CLAUDE.md"
        self.stats = {
            "runs_analyzed": 0,
            "tiering_correct": 0,
            "tiering_suboptimal": 0,
            "cost_savings_potential": 0.0,
            "model_distribution": {
                "haiku": 0,
                "sonnet": 0,
                "opus": 0
            }
        }

    def compute_complexity_score(
        self,
        input_tokens: int,
        keywords_matched: int,
        rag_reranker_score_max: float = 0.0,
        files_to_process: int = 0,
        cross_agent_references: int = 0,
        phase: str = None
    ) -> float:
        """
        Compute complexity score using R7 formula.
        Matches the formula in CLAUDE.md apêndice.
        """
        score = 0.0

        # Baseline: keywords (0–3 points)
        score += min(keywords_matched * 1.0, 3.0)

        # RAG reranker signal (0–2 points)
        if rag_reranker_score_max > 0.7:
            score += 2.0
        elif rag_reranker_score_max > 0.5:
            score += 1.0

        # File processing (0–3 points)
        score += min(files_to_process * 1.5, 3.0)

        # Cross-agent dependencies (0–1 point)
        if cross_agent_references > 0:
            score += 1.0

        # Phase multiplier (0–1 point)
        phase_multipliers = {
            "estudo-previo": 0.5,
            "projeto-basico": 0.8,
            "projeto-executivo": 1.2,
            "obra": 1.0,
            "operacao": 0.7,
            "licitacao": 1.1,
            "due-diligence": 1.3,
            "encerramento": 0.9
        }
        if phase in phase_multipliers:
            score *= phase_multipliers[phase]

        return min(score, 10.0)

    def decide_tier(self, input_tokens: int, complexity: float) -> str:
        """Decide model tier based on R7 logic"""
        if input_tokens < 2000 and complexity < 3.0:
            return "haiku-4-5"
        elif input_tokens < 10000 and complexity < 6.0:
            return "sonnet-5"
        else:
            return "opus-5"

    def get_tier_cost(self, tier: str, output_tokens: int = 1000) -> float:
        """Estimate cost for a tier (input + output approximation)"""
        # Costs per 1M tokens (2025 pricing)
        costs = {
            "haiku-4-5": 0.08,
            "sonnet-5": 3.0,
            "opus-5": 15.0
        }
        cost_per_1m = costs.get(tier, 3.0)
        # Very rough estimate: typical run is ~2000 input + 1000 output tokens
        total_tokens = 2000 + output_tokens
        return (total_tokens / 1_000_000) * cost_per_1m

    def audit_sample_run(self, run_data: Dict) -> Dict:
        """Audit a single historical run"""
        input_tokens = run_data.get("input_tokens", 1000)
        keywords_matched = len(run_data.get("keywords", []))
        rag_score = run_data.get("rag_reranker_score_max", 0.0)
        files = len(run_data.get("files", []))
        cross_refs = len(run_data.get("cross_agent_refs", []))
        phase = run_data.get("phase")
        actual_tier = run_data.get("model_tier")
        output_tokens = run_data.get("output_tokens", 1000)

        # Compute what tier SHOULD have been used
        complexity = self.compute_complexity_score(
            input_tokens, keywords_matched, rag_score, files, cross_refs, phase
        )
        recommended_tier = self.decide_tier(input_tokens, complexity)

        # Compare
        is_correct = recommended_tier == actual_tier
        actual_cost = self.get_tier_cost(actual_tier, output_tokens)
        optimal_cost = self.get_tier_cost(recommended_tier, output_tokens)
        savings = actual_cost - optimal_cost

        result = {
            "run_id": run_data.get("run_id"),
            "input_tokens": input_tokens,
            "complexity_score": complexity,
            "actual_tier": actual_tier,
            "recommended_tier": recommended_tier,
            "is_correct": is_correct,
            "actual_cost_usd": actual_cost,
            "optimal_cost_usd": optimal_cost,
            "savings_potential_usd": savings if savings > 0 else 0
        }

        return result

    def run(self) -> Dict:
        """Execute tiering audit"""
        logger.info("=" * 70)
        logger.info("Tiering Audit — R7 Validation (v5.0)")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        # Sample data (in production, this would be loaded from Supabase agent_runs)
        sample_runs = [
            {
                "run_id": "run_001",
                "input_tokens": 1200,
                "output_tokens": 800,
                "keywords": ["saneamento", "ETA"],
                "rag_reranker_score_max": 0.92,
                "files": ["projeto.dwg"],
                "cross_agent_refs": [],
                "phase": "projeto-executivo",
                "model_tier": "haiku-4-5"
            },
            {
                "run_id": "run_002",
                "input_tokens": 5000,
                "output_tokens": 2000,
                "keywords": ["barragem", "vertedouro", "ICOLD"],
                "rag_reranker_score_max": 0.85,
                "files": ["design.dwg", "geotecnia.pdf"],
                "cross_agent_refs": ["agente-geotecnia"],
                "phase": "projeto-executivo",
                "model_tier": "sonnet-5"
            },
            {
                "run_id": "run_003",
                "input_tokens": 15000,
                "output_tokens": 4000,
                "keywords": ["energia", "transmissão", "ANEEL", "leilão"],
                "rag_reranker_score_max": 0.88,
                "files": ["RAP.pdf", "especificacao.dwg", "orçamento.xlsx"],
                "cross_agent_refs": ["agente-orcamento", "agente-bd"],
                "phase": "licitacao",
                "model_tier": "opus-5"
            }
        ]

        logger.info(f"Auditing {len(sample_runs)} sample runs...")

        for run in sample_runs:
            result = self.audit_sample_run(run)
            self.stats["runs_analyzed"] += 1

            if result["is_correct"]:
                self.stats["tiering_correct"] += 1
            else:
                self.stats["tiering_suboptimal"] += 1
                logger.warning(
                    f"Suboptimal tiering: {result['run_id']}\n"
                    f"  Used: {result['actual_tier']} (${result['actual_cost_usd']:.4f})\n"
                    f"  Recommended: {result['recommended_tier']} "
                    f"(${result['optimal_cost_usd']:.4f})\n"
                    f"  Potential savings: ${result['savings_potential_usd']:.4f}"
                )

            self.stats["cost_savings_potential"] += result["savings_potential_usd"]
            self.stats["model_distribution"][result["actual_tier"].split("-")[0]] += 1

        # Summary
        logger.info("=" * 70)
        logger.info("Audit Summary:")
        logger.info(f"  Runs analyzed: {self.stats['runs_analyzed']}")
        logger.info(f"  Correct tiering: {self.stats['tiering_correct']}")
        logger.info(f"  Suboptimal tiering: {self.stats['tiering_suboptimal']}")
        logger.info(
            f"  Total potential savings: ${self.stats['cost_savings_potential']:.4f}/month"
        )
        logger.info(f"  Model distribution: {self.stats['model_distribution']}")

        accuracy = (self.stats["tiering_correct"] / self.stats["runs_analyzed"]
                    if self.stats["runs_analyzed"] > 0 else 0)
        logger.info(f"  Accuracy: {accuracy*100:.1f}%")

        logger.info("=" * 70)
        logger.info(
            "Recommendation: If accuracy < 95%, adjust complexity_score formula"
        )
        logger.info("in CLAUDE.md apêndice and redeploy.")

        return self.stats


if __name__ == "__main__":
    auditor = TieringAuditor()
    stats = auditor.run()
    print(f"\nStats: {json.dumps(stats, indent=2)}")
