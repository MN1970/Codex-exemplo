#!/usr/bin/env python3
"""
cost_analyzer.py — Cost modeling and ROI analysis for v5.0

Objetivo:
  Modela custo esperado por segmento (S6-S10) com R7 tiering automático.
  Calcula: cost/run, cost/mês, break-even, ROI vs v4.2, savings timeline.

Saída:
  - rag_evals/cost_analysis.json (detailed cost model)
  - rag_evals/cost_roi_summary.txt (ROI + break-even analysis)

Entradas:
  - benchmark_maestro.json (tiering distribution + costs)
  - CLAUDE.md (skill v5.0 pinning, RAG collections)
  - Tech debt cost (estimated overhead, time spent)

Execução:
  $ python scripts/cost_analyzer.py --baseline-cost 0.10 --tech-debt-hours 200
"""

import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class CostAnalyzer:
    """Analyzes costs and ROI for v5.0."""

    def __init__(self, baseline_cost_per_run: float = 0.10):
        """
        Initialize cost analyzer.

        Args:
            baseline_cost_per_run: Cost per run in v4.2 (default $0.10)
        """
        self.baseline_cost = baseline_cost_per_run

        # Model costs (per 1M tokens)
        self.model_costs = {
            "haiku": 0.08 / 1_000_000,
            "sonnet": 3.0 / 1_000_000,
            "opus": 15.0 / 1_000_000
        }

        # Operational costs (monthly)
        self.operational_costs = {
            "rag_storage_monthly": 50.0,      # Supabase storage for RAG
            "embedding_inference_monthly": 100.0,  # Infinity/Hugging Face
            "reranker_inference_monthly": 150.0,   # Cross-encoder reranker
            "monitoring_monthly": 50.0,       # Grafana + logging
            "orchestration_monthly": 50.0      # APScheduler + background tasks
        }

    def estimate_tier_distribution(self, expected_avg_complexity: float = 4.5) -> Dict[str, float]:
        """
        Estimate tier distribution based on average complexity.

        Args:
            expected_avg_complexity: Average complexity score (0-10)

        Returns:
            Dict with tier percentages
        """
        # Heuristic: higher complexity = more Opus/Sonnet usage
        if expected_avg_complexity < 3.0:
            return {"haiku": 0.60, "sonnet": 0.35, "opus": 0.05}
        elif expected_avg_complexity < 6.0:
            return {"haiku": 0.30, "sonnet": 0.55, "opus": 0.15}
        else:
            return {"haiku": 0.10, "sonnet": 0.40, "opus": 0.50}

    def estimate_tokens_per_run(self, tier: str) -> Tuple[int, int]:
        """
        Estimate input and output tokens per run by tier.

        Returns:
            (input_tokens, output_tokens)
        """
        token_estimates = {
            "haiku": (1200, 800),
            "sonnet": (2000, 1500),
            "opus": (3000, 2000)
        }
        return token_estimates.get(tier, (2000, 1000))

    def calculate_cost_per_run(
        self,
        tier: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for a single run.

        Args:
            tier: Model tier ("haiku", "sonnet", "opus")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        cost_per_token = self.model_costs[tier]
        # Input is ~3x cheaper than output in Claude pricing
        input_cost = (input_tokens * cost_per_token) / 3.0
        output_cost = output_tokens * cost_per_token
        return input_cost + output_cost

    def project_monthly_cost(
        self,
        tier_distribution: Dict[str, float],
        runs_per_month: int = 10000
    ) -> Dict[str, Any]:
        """
        Project monthly costs based on tier distribution.

        Args:
            tier_distribution: Dict with tier percentages (sum=1.0)
            runs_per_month: Expected runs per month

        Returns:
            Dict with cost breakdown
        """
        tier_costs = {}
        total_model_cost = 0.0

        for tier, percentage in tier_distribution.items():
            runs_for_tier = int(runs_per_month * percentage)
            input_tokens, output_tokens = self.estimate_tokens_per_run(tier)
            cost_per_run = self.calculate_cost_per_run(tier, input_tokens, output_tokens)
            tier_monthly_cost = cost_per_run * runs_for_tier

            tier_costs[tier] = {
                "runs": runs_for_tier,
                "cost_per_run": round(cost_per_run, 6),
                "monthly_cost": round(tier_monthly_cost, 2)
            }

            total_model_cost += tier_monthly_cost

        operational_cost = sum(self.operational_costs.values())

        return {
            "tier_costs": tier_costs,
            "total_model_cost_monthly": round(total_model_cost, 2),
            "total_operational_cost_monthly": round(operational_cost, 2),
            "total_monthly_cost": round(total_model_cost + operational_cost, 2),
            "cost_per_run_avg": round(
                (total_model_cost / runs_per_month) if runs_per_month > 0 else 0, 6
            ),
            "runs_per_month": runs_per_month
        }

    def calculate_roi(
        self,
        v5_cost_per_run: float,
        tech_debt_hours: float = 200,
        hourly_rate: float = 150.0,
        baseline_cost_per_run: float = None,
        projections_months: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate ROI and break-even.

        Args:
            v5_cost_per_run: Cost per run in v5.0
            tech_debt_hours: Hours spent on v5.0 development
            hourly_rate: Hourly rate for developer cost
            baseline_cost_per_run: Cost per run in v4.2 (uses self.baseline_cost if None)
            projections_months: Number of months to project

        Returns:
            ROI analysis dict
        """
        if baseline_cost_per_run is None:
            baseline_cost_per_run = self.baseline_cost

        # Tech debt cost
        tech_debt_cost = tech_debt_hours * hourly_rate

        # Monthly cost difference
        runs_per_month = 10000  # Assumed
        monthly_savings = (baseline_cost_per_run - v5_cost_per_run) * runs_per_month

        # Break-even
        break_even_months = (
            tech_debt_cost / monthly_savings
            if monthly_savings > 0 else float('inf')
        )

        # ROI over time
        roi_data = []
        for month in range(0, projections_months + 1):
            cumulative_savings = monthly_savings * month - tech_debt_cost
            roi_pct = (
                (cumulative_savings / tech_debt_cost * 100)
                if tech_debt_cost > 0 else 0
            )
            roi_data.append({
                "month": month,
                "cumulative_savings_usd": round(cumulative_savings, 2),
                "roi_pct": round(roi_pct, 1),
                "break_even": cumulative_savings > 0
            })

        return {
            "tech_debt_cost_usd": round(tech_debt_cost, 2),
            "baseline_cost_per_run": round(baseline_cost_per_run, 6),
            "v5_cost_per_run": round(v5_cost_per_run, 6),
            "cost_savings_per_run": round(baseline_cost_per_run - v5_cost_per_run, 6),
            "savings_percentage": round(
                (1.0 - (v5_cost_per_run / baseline_cost_per_run)) * 100, 1
            ) if baseline_cost_per_run > 0 else 0.0,
            "monthly_savings_usd": round(monthly_savings, 2),
            "break_even_months": round(break_even_months, 1) if break_even_months != float('inf') else None,
            "roi_projection_months": roi_data
        }

    def segment_cost_analysis(
        self,
        segment_name: str,
        complexity_profile: str = "mixed",
        monthly_runs: int = 1500
    ) -> Dict[str, Any]:
        """
        Analyze costs for a specific segment (S6-S10).

        Args:
            segment_name: Segment name (e.g., "S6-Portos")
            complexity_profile: "low", "medium", "high", "mixed"
            monthly_runs: Estimated monthly runs for segment

        Returns:
            Segment cost analysis
        """
        complexity_map = {
            "low": 2.5,
            "medium": 4.5,
            "high": 7.5,
            "mixed": 4.5
        }

        avg_complexity = complexity_map.get(complexity_profile, 4.5)
        tier_dist = self.estimate_tier_distribution(avg_complexity)
        monthly_costs = self.project_monthly_cost(tier_dist, monthly_runs)

        return {
            "segment": segment_name,
            "complexity_profile": complexity_profile,
            "average_complexity": avg_complexity,
            "monthly_runs": monthly_runs,
            "tier_distribution": tier_dist,
            "costs": monthly_costs
        }

    def load_benchmark_results(self, filepath: Path) -> Dict[str, Any]:
        """Load benchmark results from file."""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load benchmark results: {e}")
            return {}

    def generate_report(
        self,
        segments: List[Dict[str, str]],
        benchmark_file: Path = None,
        tech_debt_hours: float = 200,
        output_dir: Path = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive cost analysis report.

        Args:
            segments: List of segment dicts with name, profile, monthly_runs
            benchmark_file: Path to benchmark_maestro.json
            tech_debt_hours: Hours spent on v5.0
            output_dir: Output directory

        Returns:
            Complete analysis report
        """
        if output_dir is None:
            output_dir = Path("rag_evals")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load benchmark if available
        benchmark_result = {}
        if benchmark_file and benchmark_file.exists():
            benchmark_result = self.load_benchmark_results(benchmark_file)
            logger.info(f"Loaded benchmark results from {benchmark_file}")

        # Extract v5.0 cost from benchmark if available
        v5_cost_per_run = benchmark_result.get("cost_metrics", {}).get("avg_cost_per_run_usd", 0.06)

        # Segment analysis
        segment_analyses = []
        total_monthly_runs = 0
        total_monthly_cost = 0.0

        for segment_config in segments:
            analysis = self.segment_cost_analysis(
                segment_name=segment_config["name"],
                complexity_profile=segment_config.get("profile", "mixed"),
                monthly_runs=segment_config.get("monthly_runs", 1500)
            )
            segment_analyses.append(analysis)
            total_monthly_runs += segment_config.get("monthly_runs", 1500)
            total_monthly_cost += analysis["costs"]["total_monthly_cost"]

        # Overall ROI
        roi_analysis = self.calculate_roi(
            v5_cost_per_run=v5_cost_per_run,
            tech_debt_hours=tech_debt_hours,
            baseline_cost_per_run=self.baseline_cost
        )

        # v4.2 baseline for comparison
        v4_2_monthly_cost = self.baseline_cost * total_monthly_runs

        report = {
            "analysis_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "5.0",
                "baseline_version": "4.2",
                "segments_analyzed": len(segment_analyses),
                "total_monthly_runs_projected": total_monthly_runs,
                "tech_debt_hours": tech_debt_hours
            },
            "baseline_v4_2": {
                "cost_per_run_usd": round(self.baseline_cost, 6),
                "monthly_cost_usd": round(v4_2_monthly_cost, 2),
                "annual_cost_usd": round(v4_2_monthly_cost * 12, 2)
            },
            "v5_0_projection": {
                "cost_per_run_usd": round(v5_cost_per_run, 6),
                "monthly_cost_usd": round(total_monthly_cost, 2),
                "annual_cost_usd": round(total_monthly_cost * 12, 2)
            },
            "savings": {
                "monthly_savings_usd": round(v4_2_monthly_cost - total_monthly_cost, 2),
                "annual_savings_usd": round((v4_2_monthly_cost - total_monthly_cost) * 12, 2),
                "savings_percentage": round(
                    (1.0 - (total_monthly_cost / v4_2_monthly_cost)) * 100, 1
                ) if v4_2_monthly_cost > 0 else 0.0
            },
            "roi_analysis": roi_analysis,
            "segment_costs": segment_analyses,
            "operational_costs_monthly": {
                k: v for k, v in self.operational_costs.items()
            },
            "operational_costs_total_monthly": sum(self.operational_costs.values())
        }

        return report


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Cost analysis and ROI modeling for v5.0"
    )
    parser.add_argument(
        "--baseline-cost",
        type=float,
        default=0.10,
        help="Cost per run in v4.2 (default: $0.10)"
    )
    parser.add_argument(
        "--tech-debt-hours",
        type=float,
        default=200,
        help="Hours spent on v5.0 development (default: 200)"
    )
    parser.add_argument(
        "--benchmark-file",
        default="rag_evals/benchmark_maestro.json",
        help="Path to benchmark results JSON"
    )
    parser.add_argument(
        "--output-dir",
        default="rag_evals",
        help="Output directory (default: rag_evals)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting cost analysis...")

    # Segment definitions (S6-S10 + existing S1-S4)
    segments = [
        {"name": "S1-Rodovias", "profile": "medium", "monthly_runs": 2000},
        {"name": "S2-OAE", "profile": "high", "monthly_runs": 1200},
        {"name": "S3-Ferrovia", "profile": "medium", "monthly_runs": 800},
        {"name": "S4-Metrô", "profile": "high", "monthly_runs": 1000},
        {"name": "S6-Portos", "profile": "medium", "monthly_runs": 1500},
        {"name": "S7-Aeroportos", "profile": "high", "monthly_runs": 1200},
        {"name": "S8-Saneamento", "profile": "medium", "monthly_runs": 2000},
        {"name": "S9-Energia", "profile": "high", "monthly_runs": 1800},
        {"name": "S10-Barragens", "profile": "high", "monthly_runs": 1000},
    ]

    try:
        analyzer = CostAnalyzer(baseline_cost_per_run=args.baseline_cost)
        output_dir = Path(args.output_dir)

        # Generate report
        report = analyzer.generate_report(
            segments=segments,
            benchmark_file=Path(args.benchmark_file) if args.benchmark_file else None,
            tech_debt_hours=args.tech_debt_hours,
            output_dir=output_dir
        )

        # Write JSON report
        json_path = output_dir / "cost_analysis.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"JSON report: {json_path}")

        # Write summary
        summary_path = output_dir / "cost_roi_summary.txt"
        with open(summary_path, "w") as f:
            f.write("COST ANALYSIS & ROI REPORT (v5.0)\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Analysis Date: {report['analysis_metadata']['timestamp']}\n")
            f.write(f"Segments: {report['analysis_metadata']['segments_analyzed']}\n")
            f.write(f"Monthly Runs: {report['analysis_metadata']['total_monthly_runs_projected']:,}\n\n")

            f.write("BASELINE (v4.2)\n")
            f.write("-" * 70 + "\n")
            f.write(f"Cost per run:  ${report['baseline_v4_2']['cost_per_run_usd']:.6f}\n")
            f.write(f"Monthly cost:  ${report['baseline_v4_2']['monthly_cost_usd']:>10,.2f}\n")
            f.write(f"Annual cost:   ${report['baseline_v4_2']['annual_cost_usd']:>10,.2f}\n\n")

            f.write("v5.0 PROJECTION\n")
            f.write("-" * 70 + "\n")
            f.write(f"Cost per run:  ${report['v5_0_projection']['cost_per_run_usd']:.6f}\n")
            f.write(f"Monthly cost:  ${report['v5_0_projection']['monthly_cost_usd']:>10,.2f}\n")
            f.write(f"Annual cost:   ${report['v5_0_projection']['annual_cost_usd']:>10,.2f}\n\n")

            f.write("SAVINGS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Monthly savings: ${report['savings']['monthly_savings_usd']:>10,.2f}\n")
            f.write(f"Annual savings:  ${report['savings']['annual_savings_usd']:>10,.2f}\n")
            f.write(f"Savings %:       {report['savings']['savings_percentage']:>10.1f}%\n\n")

            f.write("ROI ANALYSIS\n")
            f.write("-" * 70 + "\n")
            roi = report['roi_analysis']
            f.write(f"Tech debt cost:  ${roi['tech_debt_cost_usd']:>10,.2f}\n")
            f.write(f"Monthly savings: ${roi['monthly_savings_usd']:>10,.2f}\n")
            f.write(f"Cost per run (baseline): ${roi['baseline_cost_per_run']:.6f}\n")
            f.write(f"Cost per run (v5.0):    ${roi['v5_cost_per_run']:.6f}\n")
            f.write(f"Savings per run:        ${roi['cost_savings_per_run']:.6f}\n")

            if roi['break_even_months']:
                f.write(f"Break-even:      {roi['break_even_months']:>10.1f} months\n")
            else:
                f.write(f"Break-even:      Never (no savings)\n")

            f.write("\nROI PROJECTION (12 months)\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Month':<8} {'Cumulative Savings':<25} {'ROI %':<12} {'Break-even':<12}\n")
            f.write("-" * 70 + "\n")
            for entry in roi['roi_projection_months'][::2]:  # Print every 2 months
                f.write(f"{entry['month']:<8} ${entry['cumulative_savings_usd']:>20,.2f} {entry['roi_pct']:>10.1f}% {'Yes' if entry['break_even'] else 'No':<12}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("SEGMENT COST SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            for segment in report['segment_costs']:
                f.write(f"\n{segment['segment']}\n")
                f.write(f"  Profile: {segment['complexity_profile'].upper()}\n")
                f.write(f"  Monthly runs: {segment['monthly_runs']:,}\n")
                f.write(f"  Monthly cost: ${segment['costs']['total_monthly_cost']:,.2f}\n")
                f.write(f"  Cost per run: ${segment['costs']['cost_per_run_avg']:.6f}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("KEY TAKEAWAYS\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"1. R7 tiering reduces cost by {report['savings']['savings_percentage']:.1f}% overall\n")
            f.write(f"2. Break-even in {roi['break_even_months'] or 'N/A'} months\n")
            f.write(f"3. Annual savings: ${report['savings']['annual_savings_usd']:,.2f}\n")
            f.write(f"4. Cost per run: ${roi['v5_cost_per_run']:.6f} (vs ${roi['baseline_cost_per_run']:.6f} in v4.2)\n")
            f.write(f"5. Operational costs (monthly): ${report['operational_costs_total_monthly']:,.2f}\n")

        logger.info(f"Summary: {summary_path}")

        # Print to console
        print("\n" + "=" * 70)
        print("COST ANALYSIS & ROI")
        print("=" * 70)
        print(f"\nBaseline (v4.2):     ${report['baseline_v4_2']['cost_per_run_usd']:.6f}/run")
        print(f"v5.0 projection:     ${report['v5_0_projection']['cost_per_run_usd']:.6f}/run")
        print(f"Savings per run:     ${roi['cost_savings_per_run']:.6f} ({roi['savings_percentage']:.1f}%)")
        print(f"\nMonthly savings:     ${report['savings']['monthly_savings_usd']:,.2f}")
        print(f"Annual savings:      ${report['savings']['annual_savings_usd']:,.2f}")
        print(f"Break-even:          {roi['break_even_months'] or 'N/A'} months")
        print("=" * 70 + "\n")

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
