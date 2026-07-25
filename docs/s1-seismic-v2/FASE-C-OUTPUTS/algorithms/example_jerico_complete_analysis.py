#!/usr/bin/env python3
"""
PRODUCTION EXAMPLE: D6.2-D6.5 Complete Seismic Geotechnical Analysis
Jericó Site Case Study (Km 45+800 Critical Slope)

This script demonstrates the complete workflow:
  1. D6.2 Liquefaction Analysis across 6 boreholes
  2. D6.3 Newmark Deformation for slope failure
  3. D6.4 Resilient Design specifications
  4. D6.5 Post-Disaster Costing estimates

Usage:
  python example_jerico_complete_analysis.py

Output:
  - Console: Real-time analysis results
  - jerico_analysis_report.txt: Full report
  - jerico_liquefaction_summary.csv: Depth-by-depth liquefaction data
  - jerico_cost_breakdown.csv: Cost scenario analysis
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

# Import algorithm modules
from seismic_geotechnical_d6_algorithms import (
    LiquefactionAnalyzer,
    NewmarkDeformationCalculator,
    ResilientDesignModifier,
    PostDisasterCostingModel,
    JericoTestVectors
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class JericoCompleteAnalysis:
    """Orchestrates D6.2-D6.5 analysis for Jericó site."""

    def __init__(self):
        self.analyzer = LiquefactionAnalyzer(site_name="Jerico_Km45800")
        self.newmark = NewmarkDeformationCalculator()
        self.modifier = ResilientDesignModifier()
        self.costing = PostDisasterCostingModel()
        self.jerico = JericoTestVectors()

        self.boreholes = self.jerico.get_jerico_borehole_data()
        self.seismic = self.jerico.get_seismic_parameters()
        self.slope = self.jerico.get_slope_properties()

        self.report_lines = []
        self.liquefaction_data = []
        self.cost_scenarios = []

    def add_report_line(self, line: str = ""):
        """Add line to report buffer."""
        self.report_lines.append(line)
        print(line)

    def print_header(self, title: str):
        """Print formatted section header."""
        self.add_report_line()
        self.add_report_line("=" * 80)
        self.add_report_line(f" {title}")
        self.add_report_line("=" * 80)
        self.add_report_line()

    def print_subheader(self, title: str):
        """Print formatted subsection header."""
        self.add_report_line()
        self.add_report_line(f"--- {title} ---")
        self.add_report_line()

    def run_liquefaction_analysis(self) -> Dict[str, List]:
        """Execute D6.2: Complete liquefaction analysis for all boreholes."""
        self.print_header("D6.2: LIQUEFACTION ANALYSIS")

        self.add_report_line(f"Site: {self.analyzer.site_name}")
        self.add_report_line(f"Seismic Parameters:")
        self.add_report_line(f"  - PGA: {self.seismic['pga_g']:.3f}g")
        self.add_report_line(f"  - Magnitude: M{self.seismic['magnitude_mw']:.1f}")
        self.add_report_line(f"  - Description: {self.seismic['description']}")
        self.add_report_line()

        results_by_borehole = {}

        for i, borehole in enumerate(self.boreholes, 1):
            self.print_subheader(
                f"Borehole {i}/6: {borehole['borehole_id']} "
                f"({borehole['description']})"
            )

            results = self.analyzer.analyze_borehole(
                borehole_id=borehole["borehole_id"],
                depths_m=borehole["depths_m"],
                spt_n_values=borehole["spt_n_values"],
                fines_content_pcts=borehole["fines_content_pcts"],
                pga_g=self.seismic["pga_g"],
                magnitude_mw=self.seismic["magnitude_mw"]
            )

            results_by_borehole[borehole["borehole_id"]] = results

            # Print depth-by-depth summary
            self.add_report_line(f"{'Depth':>6} {'N':>5} {'FC':>5} {'Ky':>7} "
                                f"{'FoS':>7} {'LI':>7} {'Risk Level':<25}")
            self.add_report_line("-" * 70)

            for result in results:
                self.add_report_line(
                    f"{result.depth_m:6.1f}m {result.spt_n_value:5d} "
                    f"{result.fines_content_pct:5.1f}% {result.rd_factor:7.3f} "
                    f"{result.factor_of_safety:7.3f} {result.liquefaction_index:7.3f} "
                    f"{result.risk_level}"
                )

                # Store for CSV export
                self.liquefaction_data.append({
                    "borehole": borehole["borehole_id"],
                    "depth_m": result.depth_m,
                    "spt_n": result.spt_n_value,
                    "fines_pct": result.fines_content_pct,
                    "n_corrected": result.n_corrected,
                    "rd_factor": result.rd_factor,
                    "msf_factor": result.msf_factor,
                    "csr": result.csr,
                    "crr": result.crr_factor,
                    "fos": result.factor_of_safety,
                    "liquefaction_index": result.liquefaction_index,
                    "risk_level": result.risk_level
                })

            # Summary for this borehole
            max_li = max(r.liquefaction_index for r in results)
            min_fos = min(r.factor_of_safety for r in results)
            critical_depth = max(
                (r.depth_m for r in results),
                key=lambda d: results[[r.depth_m for r in results].index(d)].liquefaction_index
            )

            self.add_report_line()
            self.add_report_line(f"BOREHOLE SUMMARY ({borehole['borehole_id']}):")
            self.add_report_line(f"  - Max Liquefaction Index: {max_li:.3f}")
            self.add_report_line(f"  - Min Factor of Safety: {min_fos:.3f}")
            self.add_report_line(f"  - Critical depth: ~{critical_depth:.1f}m")

        return results_by_borehole

    def run_slope_stability_analysis(self, max_li: float):
        """Execute D6.3: Newmark deformation analysis."""
        self.print_header("D6.3: NEWMARK SLOPE DEFORMATION ANALYSIS")

        self.add_report_line(f"Slope Location: Km {self.slope['location_km']:.1f}")
        self.add_report_line(f"Critical Failure Surface: {self.slope['failure_surface_depth_m']:.1f}m depth")
        self.add_report_line(f"Slope Angle: {self.slope['slope_angle_deg']}°")
        self.add_report_line(f"Static Factor of Safety: {self.slope['static_fos']:.2f}")
        self.add_report_line()

        result = self.newmark.analyze_slope(
            depth_m=self.slope["failure_surface_depth_m"],
            slope_fos=self.slope["static_fos"],
            pga_g=self.seismic["pga_g"],
            magnitude_mw=self.seismic["magnitude_mw"]
        )

        self.add_report_line("ANALYSIS RESULTS:")
        self.add_report_line(f"  - Yield Acceleration (Ky): {result.ay_g:.4f}g")
        self.add_report_line(f"  - Max Acceleration (PGA × 1.2): {result.an_max_g:.4f}g")
        self.add_report_line(f"  - Residual Displacement: {result.residual_displacement_cm:.1f}cm")
        self.add_report_line(f"  - Damage Potential: {result.damage_potential}")
        self.add_report_line()

        # Assess seismic impact
        if result.residual_displacement_cm > 20:
            assessment = "SEVERE - Pavement/embankment rehabilitation required"
        elif result.residual_displacement_cm > 10:
            assessment = "SIGNIFICANT - Remedial measures recommended"
        else:
            assessment = "MODERATE - Monitoring and maintenance"

        self.add_report_line(f"ENGINEERING ASSESSMENT: {assessment}")
        self.add_report_line()

        return result

    def run_resilient_design_analysis(self, max_li: float):
        """Execute D6.4: Resilient design specifications."""
        self.print_header("D6.4: RESILIENT DESIGN SPECIFICATIONS")

        self.add_report_line(f"Hazard Metrics:")
        self.add_report_line(f"  - Peak Ground Acceleration: {self.seismic['pga_g']:.3f}g")
        self.add_report_line(f"  - Max Liquefaction Index: {max_li:.3f}")
        self.add_report_line(f"  - Slope FoS: {self.slope['static_fos']:.2f}")
        self.add_report_line()

        design_spec = self.modifier.generate_design_specification(
            pga_g=self.seismic["pga_g"],
            li=max_li,
            barrier_length_m=500,  # 500m critical section
            use_geotextile=True
        )

        self.add_report_line("PAVEMENT DESIGN MODIFICATIONS:")
        self.add_report_line(f"  - CBUQ Binder Content Modifier: {design_spec['cbuq_modifier']:.2%}")

        if design_spec["cbuq_modifier"] > 1.0:
            binder_increase_pct = (design_spec["cbuq_modifier"] - 1.0) * 100
            self.add_report_line(f"    → Increase binder content by {binder_increase_pct:.1f}%")
            self.add_report_line(f"    → Use softer PG grade (e.g., PG 60-16 instead of 64-16)")
        self.add_report_line()

        self.add_report_line("GEOTEXTILE REINFORCEMENT:")
        friction_increase = design_spec["geotextile_friction_increase"]
        self.add_report_line(f"  - Friction Angle Increase: {friction_increase:.2%}")
        self.add_report_line(f"  - Recommended Type: Non-woven polypropylene (150-300 g/m²)")
        self.add_report_line(f"  - Installation: At base of fill or within critical layer")
        self.add_report_line()

        self.add_report_line("DAMPENED ENERGY-DISSIPATION BARRIER:")
        self.add_report_line(f"  - Installation Length: 500m")
        self.add_report_line(f"  - Type: Elastomeric-faced barrier blocks")
        self.add_report_line(f"  - Function: Reduce seismic wave propagation")
        self.add_report_line(f"  - Estimated Cost: BRL {design_spec['barrier_cost_brl']:,.0f}")
        self.add_report_line()

        return design_spec

    def run_post_disaster_costing(self, max_li: float):
        """Execute D6.5: Post-disaster cost estimation."""
        self.print_header("D6.5: POST-DISASTER COST ESTIMATION (SICRO 2024)")

        self.add_report_line(f"Project Area: {self.slope['affected_area_m2']:,}m²")
        self.add_report_line(f"Location: Jericó, Km {self.slope['location_km']:.1f}")
        self.add_report_line()

        # Analyze three scenarios: light, moderate, severe
        scenarios = ["light", "moderate", "severe"]

        self.add_report_line("COST BREAKDOWN BY DAMAGE SCENARIO:")
        self.add_report_line()

        scenario_costs = []

        for scenario in scenarios:
            costs = self.costing.estimate_total_disaster_cost(
                pga_g=self.seismic["pga_g"],
                li=max_li,
                slope_fos=self.slope["static_fos"],
                affected_area_m2=self.slope["affected_area_m2"],
                scenario=scenario
            )

            scenario_costs.append(costs)

            self.add_report_line(f"{scenario.upper()} DAMAGE SCENARIO:")
            self.add_report_line(
                f"  - Liquefaction Repair: BRL {costs['liquefaction_cost_brl']:,.0f}"
            )
            self.add_report_line(
                f"  - Slope Failure Repair: BRL {costs['slope_failure_cost_brl']:,.0f}"
            )
            self.add_report_line(
                f"  - TOTAL COST: BRL {costs['total_cost_brl']:,.0f}"
            )

            if costs["hazard_levels"]:
                self.add_report_line(f"  - Hazard Notes: {'; '.join(costs['hazard_levels'])}")

            self.add_report_line()

            # Store for CSV export
            self.cost_scenarios.append({
                "scenario": scenario,
                "liquefaction_cost_brl": costs["liquefaction_cost_brl"],
                "slope_failure_cost_brl": costs["slope_failure_cost_brl"],
                "total_cost_brl": costs["total_cost_brl"]
            })

        # Expected loss calculation (probabilistic)
        moderate_cost = scenario_costs[1]["total_cost_brl"]
        light_cost = scenario_costs[0]["total_cost_brl"]
        severe_cost = scenario_costs[2]["total_cost_brl"]

        # Simple probability weighting: Light 20%, Moderate 60%, Severe 20%
        expected_loss = (0.20 * light_cost) + (0.60 * moderate_cost) + (0.20 * severe_cost)

        self.add_report_line()
        self.add_report_line("PROBABILISTIC EXPECTED LOSS:")
        self.add_report_line(f"  - Assuming: Light 20%, Moderate 60%, Severe 20%")
        self.add_report_line(f"  - Expected Annual Loss: BRL {expected_loss:,.0f}")
        self.add_report_line()

        return scenario_costs

    def export_csv_reports(self):
        """Export analysis data to CSV files."""
        import csv

        # D6.2 Liquefaction CSV
        liquefaction_csv = "jerico_liquefaction_summary.csv"
        with open(liquefaction_csv, 'w', newline='') as f:
            fieldnames = list(self.liquefaction_data[0].keys()) if self.liquefaction_data else []
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.liquefaction_data)

        logger.info(f"Exported liquefaction data to {liquefaction_csv}")

        # D6.5 Cost Scenarios CSV
        cost_csv = "jerico_cost_breakdown.csv"
        with open(cost_csv, 'w', newline='') as f:
            fieldnames = list(self.cost_scenarios[0].keys()) if self.cost_scenarios else []
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.cost_scenarios)

        logger.info(f"Exported cost scenarios to {cost_csv}")

    def save_report(self):
        """Save complete report to text file."""
        report_file = "jerico_analysis_report.txt"

        with open(report_file, 'w') as f:
            f.write("\n".join(self.report_lines))

        logger.info(f"Complete report saved to {report_file}")

    def run_complete_analysis(self):
        """Execute full D6.2-D6.5 analysis workflow."""
        self.print_header("JERICÓ SITE COMPLETE SEISMIC GEOTECHNICAL ANALYSIS")

        self.add_report_line(f"Generated: {datetime.now().isoformat()}")
        self.add_report_line(f"Project: Jericó Highway Project")
        self.add_report_line(f"Critical Section: Km {self.slope['location_km']:.1f}")
        self.add_report_line()

        try:
            # ========== D6.2: LIQUEFACTION ==========
            liquefaction_results = self.run_liquefaction_analysis()

            # Get maximum LI across all boreholes for subsequent analysis
            max_li = 0.0
            for bh_results in liquefaction_results.values():
                bh_max_li = max(r.liquefaction_index for r in bh_results)
                max_li = max(max_li, bh_max_li)

            self.add_report_line()
            self.add_report_line(f"OVERALL MAX LIQUEFACTION INDEX: {max_li:.3f}")

            # ========== D6.3: SLOPE STABILITY ==========
            slope_result = self.run_slope_stability_analysis(max_li)

            # ========== D6.4: RESILIENT DESIGN ==========
            design_spec = self.run_resilient_design_analysis(max_li)

            # ========== D6.5: COST ESTIMATION ==========
            cost_scenarios = self.run_post_disaster_costing(max_li)

            # ========== SUMMARY & RECOMMENDATIONS ==========
            self.print_header("SUMMARY & ENGINEERING RECOMMENDATIONS")

            self.add_report_line("FINDINGS:")
            self.add_report_line()

            # D6.2 findings
            if max_li > 0.30:
                self.add_report_line(f"1. LIQUEFACTION RISK: HIGH (LI = {max_li:.3f})")
                self.add_report_line("   → Implement liquefaction mitigation measures")
                self.add_report_line("   → Consider ground improvement (grouting, densification)")
                self.add_report_line("   → Enhanced drainage design for susceptible layers")
            else:
                self.add_report_line(f"1. LIQUEFACTION RISK: MODERATE (LI = {max_li:.3f})")
                self.add_report_line("   → Standard design with seismic considerations")

            self.add_report_line()

            # D6.3 findings
            if slope_result.residual_displacement_cm > 15:
                self.add_report_line(f"2. SLOPE STABILITY: CRITICAL ({slope_result.residual_displacement_cm:.1f}cm)")
                self.add_report_line("   → Slope stabilization measures required")
                self.add_report_line("   → Consider tie-back anchors or berms")
                self.add_report_line("   → Implement real-time monitoring system")
            else:
                self.add_report_line(f"2. SLOPE STABILITY: ACCEPTABLE ({slope_result.residual_displacement_cm:.1f}cm)")

            self.add_report_line()

            # D6.4 findings
            self.add_report_line("3. RESILIENT DESIGN MODIFICATIONS:")
            self.add_report_line(f"   → CBUQ binder adjustment: +{(design_spec['cbuq_modifier']-1.0)*100:.1f}%")
            self.add_report_line("   → Geotextile reinforcement: Recommended")
            self.add_report_line("   → Energy-dissipation barrier: 500m length, BRL {design_spec['barrier_cost_brl']:,.0f}")

            self.add_report_line()

            # D6.5 findings
            self.add_report_line("4. POST-DISASTER COST ESTIMATES:")
            moderate_cost = cost_scenarios[1]["total_cost_brl"]
            self.add_report_line(f"   → Moderate damage scenario: BRL {moderate_cost:,.0f}")
            self.add_report_line(f"   → Cost-benefit ratio favors proactive mitigation")

            self.add_report_line()
            self.add_report_line()

            self.print_header("IMPLEMENTATION ROADMAP")

            self.add_report_line("PHASE 1 (Design - 0-3 months):")
            self.add_report_line("  - Finalize site investigation (CPT, dynamic testing)")
            self.add_report_line("  - Detailed D-value and damping analysis")
            self.add_report_line("  - Slope remediation design (if FoS < 1.2)")
            self.add_report_line()

            self.add_report_line("PHASE 2 (Preparation - 3-6 months):")
            self.add_report_line("  - Ground improvement works (if required)")
            self.add_report_line("  - Procurement of special materials (geotextile, barriers)")
            self.add_report_line("  - Installation of monitoring instrumentation")
            self.add_report_line()

            self.add_report_line("PHASE 3 (Construction - 6-12 months):")
            self.add_report_line("  - Modified CBUQ placement with enhanced binder")
            self.add_report_line("  - Geotextile installation at critical depths")
            self.add_report_line("  - Energy-dissipation barrier installation")
            self.add_report_line()

            self.add_report_line("PHASE 4 (Monitoring - Ongoing):")
            self.add_report_line("  - Real-time seismic monitoring network")
            self.add_report_line("  - Bi-annual maintenance inspections")
            self.add_report_line("  - Post-earthquake rapid assessment protocol")
            self.add_report_line()

            # Export data and save report
            self.export_csv_reports()
            self.save_report()

            self.print_header("ANALYSIS COMPLETE")
            self.add_report_line("All output files have been generated.")
            self.add_report_line("  - jerico_analysis_report.txt")
            self.add_report_line("  - jerico_liquefaction_summary.csv")
            self.add_report_line("  - jerico_cost_breakdown.csv")

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            raise


def main():
    """Main execution entry point."""
    try:
        print("\n" + "=" * 80)
        print(" JERICÓ SITE: COMPLETE D6.2-D6.5 SEISMIC GEOTECHNICAL ANALYSIS")
        print("=" * 80 + "\n")

        analysis = JericoCompleteAnalysis()
        analysis.run_complete_analysis()

        print("\n" + "=" * 80)
        print(" ANALYSIS SUCCESSFULLY COMPLETED")
        print("=" * 80 + "\n")

        return 0

    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
