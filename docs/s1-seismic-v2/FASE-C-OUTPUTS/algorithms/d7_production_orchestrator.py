"""
D7 Production Orchestrator — Integration & UAT
Unified interface for D7.2–D7.5 algorithms with test cases and UAT workflows.

Sprint 2 production-ready module.
"""

from dataclasses import dataclass
from typing import Dict, List
import json

# Import all D7 modules
from d7_vertical_geometry import (
    VerticalGeometryCalculator,
    VerticalGeometryInput,
    VerticalGeometryOutput,
)
from d7_geo_talude_iteration import (
    GeoTaludeIterator,
    SlopeStabilityInput,
    ConvergenceResult,
)
from d7_viaria_safety import (
    ViariaSafetyAnalyzer,
    ViariaInputs,
    ViariaOutputs,
)
from d7_jerico_design_cases import (
    JericoDesignPackage,
    DesignCase,
)


@dataclass
class D7WorkflowStep:
    """Single step in D7 design workflow."""
    step_name: str
    module: str
    status: str  # "pending", "running", "complete", "error"
    output_data: Dict = None
    error_message: str = None


class D7ProductionWorkflow:
    """
    D7 Production Workflow Orchestrator

    Complete workflow:
    1. D7.2 Vertical Geometry (PIV + rampa)
    2. D7.3 Geo-Talude Iteration (feedback loop → convergence)
    3. D7.4 Viaria Safety (SSD + tombamento + lane width)
    4. D7.5 Design Cases (3 scenarios with detailed packages)
    """

    def __init__(self):
        self.steps: List[D7WorkflowStep] = []
        self.vertical_geometry_calc = VerticalGeometryCalculator()
        self.viaria_safety_analyzer = ViariaSafetyAnalyzer()
        self.jerico_package = JericoDesignPackage()

    def log_step(self, step: D7WorkflowStep):
        """Log a workflow step."""
        self.steps.append(step)
        status_symbol = {
            "pending": "⏳",
            "running": "🔄",
            "complete": "✓",
            "error": "✗"
        }
        print(f"{status_symbol.get(step.status, '?')} {step.step_name} [{step.module}]")
        if step.error_message:
            print(f"   ERROR: {step.error_message}")

    def execute_jerico_full_workflow(self) -> Dict:
        """
        Execute complete D7 workflow for Jericó Km 45+800 reference case.

        Returns:
            Dictionary with all results from D7.2 through D7.5
        """
        results = {}

        # ==================== D7.2: VERTICAL GEOMETRY ====================
        step_d72 = D7WorkflowStep("D7.2 Vertical Geometry Calculation", "d7_vertical_geometry.py", "running")
        self.log_step(step_d72)

        try:
            geo_input = VerticalGeometryInput(
                design_speed_kmh=80,
                pga=0.324,
                slope_deformation_cm=8.5,
                terrain_class="mountainous",
                comfort_factor=1.2
            )
            geo_output = self.vertical_geometry_calc.calculate(geo_input)

            step_d72.status = "complete"
            step_d72.output_data = {
                "piv_radius_m": geo_output.piv_radius_m,
                "standard_rampa_pct": geo_output.standard_rampa_pct,
                "seismic_adjusted_rampa_pct": geo_output.seismic_adjusted_rampa_pct,
                "newmark_adjusted_rampa_pct": geo_output.newmark_adjusted_rampa_pct,
                "comfort_zone": geo_output.comfort_zone,
            }
            results["d7_2_vertical_geometry"] = step_d72.output_data
            self.log_step(step_d72)

            print(f"   → PIV Radius: {geo_output.piv_radius_m}m")
            print(f"   → Final Rampa: {geo_output.newmark_adjusted_rampa_pct}%")

        except Exception as e:
            step_d72.status = "error"
            step_d72.error_message = str(e)
            self.log_step(step_d72)
            return results

        # ==================== D7.3: GEO-TALUDE ITERATION ====================
        step_d73 = D7WorkflowStep("D7.3 Geo-Talude Iteration Feedback", "d7_geo_talude_iteration.py", "running")
        self.log_step(step_d73)

        try:
            slope_input = SlopeStabilityInput(
                initial_fos=1.8,
                soil_cohesion_kpa=25.0,
                soil_friction_deg=32.0,
                slope_height_m=45.0,
                pga=0.324
            )
            iterator = GeoTaludeIterator(slope_input)
            convergence_result = iterator.iterate_to_convergence(
                geo_output.newmark_adjusted_rampa_pct
            )

            step_d73.status = "complete"
            step_d73.output_data = {
                "final_rampa_pct": convergence_result.final_rampa_pct,
                "final_fos": convergence_result.final_fos,
                "iterations": convergence_result.iterations_performed,
                "converged": convergence_result.converged,
                "iteration_history": [
                    {
                        "iteration": s.iteration_num,
                        "rampa": s.rampa_pct,
                        "deformation_cm": s.slope_deformation_cm,
                        "fos": s.calculated_fos,
                    }
                    for s in convergence_result.iteration_history
                ]
            }
            results["d7_3_geo_talude_iteration"] = step_d73.output_data
            self.log_step(step_d73)

            print(f"   → Converged: {convergence_result.converged}")
            print(f"   → Final Rampa: {convergence_result.final_rampa_pct:.2f}%")
            print(f"   → Final FoS: {convergence_result.final_fos:.2f}")
            print(f"   → Iterations: {convergence_result.iterations_performed}")

        except Exception as e:
            step_d73.status = "error"
            step_d73.error_message = str(e)
            self.log_step(step_d73)
            return results

        # ==================== D7.4: VIARIA SAFETY ====================
        step_d74 = D7WorkflowStep("D7.4 Viaria Safety Analysis", "d7_viaria_safety.py", "running")
        self.log_step(step_d74)

        try:
            viaria_input = ViariaInputs(
                design_speed_kmh=80,
                pga=0.324,
                grade_pct=convergence_result.final_rampa_pct,
                vehicle_height_m=3.2,
                vehicle_width_m=2.6,
                pavement_friction_coeff=0.45
            )
            viaria_output = self.viaria_safety_analyzer.analyze(viaria_input)

            step_d74.status = "complete"
            step_d74.output_data = {
                "stopping_sight_distance_m": viaria_output.stopping_sight_distance_m,
                "ssd_seismic_amplified_m": viaria_output.ssd_seismic_amplified_m,
                "tombamento_ratio": viaria_output.tombamento_ratio,
                "tombamento_risk_level": viaria_output.tombamento_risk_level,
                "lane_width_adjustment_m": viaria_output.lane_width_adjustment_m,
                "minimum_lane_width_m": viaria_output.minimum_lane_width_m,
            }
            results["d7_4_viaria_safety"] = step_d74.output_data
            self.log_step(step_d74)

            print(f"   → SSD (standard): {viaria_output.stopping_sight_distance_m}m")
            print(f"   → SSD (seismic): {viaria_output.ssd_seismic_amplified_m}m")
            print(f"   → Tombamento Risk: {viaria_output.tombamento_risk_level}")
            print(f"   → Min Lane Width: {viaria_output.minimum_lane_width_m}m")

        except Exception as e:
            step_d74.status = "error"
            step_d74.error_message = str(e)
            self.log_step(step_d74)
            return results

        # ==================== D7.5: DESIGN CASES ====================
        step_d75 = D7WorkflowStep("D7.5 Jericó 3-Case Design Package", "d7_jerico_design_cases.py", "running")
        self.log_step(step_d75)

        try:
            design_cases_summary = {}
            for case_type in [DesignCase.CONSERVATIVE, DesignCase.BALANCED, DesignCase.AGGRESSIVE]:
                case = self.jerico_package.cases[case_type]
                design_cases_summary[case_type.value] = {
                    "radius_m": case.horizontal_radius_m,
                    "rampa_pct": case.vertical_rampa_pct,
                    "piv_radius_m": case.piv_radius_m,
                    "cost_brl_m": case.total_cost_brl_millions,
                    "duration_months": case.total_duration_months,
                    "minimum_fos": case.minimum_fos,
                    "tombamento_ratio": case.tombamento_ratio,
                }

            step_d75.status = "complete"
            step_d75.output_data = design_cases_summary
            results["d7_5_design_cases"] = step_d75.output_data
            self.log_step(step_d75)

            for case_type, data in design_cases_summary.items():
                print(f"   → {case_type.upper()}: BRL {data['cost_brl_m']:.1f}M, {data['duration_months']}m")

        except Exception as e:
            step_d75.status = "error"
            step_d75.error_message = str(e)
            self.log_step(step_d75)
            return results

        # ==================== WORKFLOW SUMMARY ====================
        print("\n" + "=" * 80)
        print("D7 WORKFLOW EXECUTION COMPLETE")
        print("=" * 80)

        complete_steps = sum(1 for s in self.steps if s.status == "complete")
        total_steps = len(self.steps)
        print(f"Steps completed: {complete_steps}/{total_steps}")

        if complete_steps == total_steps:
            print("✓ ALL STEPS SUCCESSFUL — Ready for UAT")
        else:
            print(f"✗ {total_steps - complete_steps} steps failed")

        return results


class D7UATTestSuite:
    """
    D7 UAT (User Acceptance Test) Suite

    Comprehensive test cases for all modules.
    """

    def __init__(self):
        self.test_results: List[Dict] = []

    def test_d72_vertical_geometry(self) -> bool:
        """Test D7.2 Vertical Geometry module."""
        print("\nTEST: D7.2 Vertical Geometry")
        print("-" * 60)

        calc = VerticalGeometryCalculator()

        # Test 1: Standard calculation
        inputs = VerticalGeometryInput(
            design_speed_kmh=80,
            pga=0.324,
            slope_deformation_cm=8.5,
            terrain_class="mountainous",
            comfort_factor=1.2
        )
        output = calc.calculate(inputs)

        assert output.piv_radius_m > 500, "PIV radius should be > 500m"
        assert 5.0 <= output.newmark_adjusted_rampa_pct <= 8.0, "Rampa should be 5–8%"
        assert output.comfort_zone in ["acceptable", "marginal", "poor"]

        print("✓ Test 1: Standard calculation passed")

        # Test 2: Seismic reduction factor
        factor_high = calc.calculate_seismic_reduction_factor(0.324)
        factor_low = calc.calculate_seismic_reduction_factor(0.1)
        assert factor_high < factor_low, "Higher PGA should give lower factor"

        print("✓ Test 2: Seismic reduction factor passed")

        # Test 3: Newmark adjustment
        rampa, adjusted = calc.calculate_newmark_adjustment(6.5, 12.0)
        assert adjusted == True, "Deformation > 10cm should trigger adjustment"
        assert rampa < 6.5, "Adjusted rampa should be less than input"

        print("✓ Test 3: Newmark adjustment passed")

        return True

    def test_d73_geo_talude_iteration(self) -> bool:
        """Test D7.3 Geo-Talude Iteration module."""
        print("\nTEST: D7.3 Geo-Talude Iteration")
        print("-" * 60)

        slope_input = SlopeStabilityInput(
            initial_fos=1.8,
            soil_cohesion_kpa=25.0,
            soil_friction_deg=32.0,
            slope_height_m=45.0,
            pga=0.324
        )

        iterator = GeoTaludeIterator(slope_input)

        # Test 1: Convergence
        result = iterator.iterate_to_convergence(6.5)
        assert result.iterations_performed <= 3, "Should converge in ≤ 3 iterations"
        assert result.final_fos >= 1.25, "Final FoS should be acceptable"

        print("✓ Test 1: Convergence achieved")

        # Test 2: Deformation estimation
        deformation = iterator.calculate_deformation_newmark(7.0, 1.35)
        assert 0 < deformation < 20, "Deformation should be reasonable"

        print("✓ Test 2: Deformation calculation passed")

        return True

    def test_d74_viaria_safety(self) -> bool:
        """Test D7.4 Viaria Safety module."""
        print("\nTEST: D7.4 Viaria Safety")
        print("-" * 60)

        analyzer = ViariaSafetyAnalyzer()

        viaria_input = ViariaInputs(
            design_speed_kmh=80,
            pga=0.324,
            grade_pct=7.0,
            vehicle_height_m=3.2,
            vehicle_width_m=2.6
        )

        output = analyzer.analyze(viaria_input)

        # Test 1: SSD
        assert output.stopping_sight_distance_m > 100, "SSD should be > 100m"
        assert output.ssd_seismic_amplified_m > output.stopping_sight_distance_m, \
            "Seismic SSD should be > standard SSD"

        print("✓ Test 1: SSD calculation passed")

        # Test 2: Tombamento
        assert 0 < output.tombamento_ratio < 1.0, "Tombamento ratio should be 0–1"
        assert output.tombamento_risk_level in ["low", "moderate", "high"]

        print("✓ Test 2: Tombamento assessment passed")

        # Test 3: Lane width
        assert output.lane_width_adjustment_m >= 0, "Lane adjustment should be non-negative"
        assert output.minimum_lane_width_m >= 3.6, "Min lane width >= 3.6m"

        print("✓ Test 3: Lane width calculation passed")

        return True

    def test_d75_design_cases(self) -> bool:
        """Test D7.5 Design Cases module."""
        print("\nTEST: D7.5 Jericó Design Cases")
        print("-" * 60)

        package = JericoDesignPackage()

        # Test 1: All cases created
        assert len(package.cases) == 3, "Should have 3 design cases"

        print("✓ Test 1: All 3 cases created")

        # Test 2: Case progression (Conservative → Aggressive)
        conservative = package.cases[DesignCase.CONSERVATIVE]
        balanced = package.cases[DesignCase.BALANCED]
        aggressive = package.cases[DesignCase.AGGRESSIVE]

        assert conservative.total_cost_brl_millions > balanced.total_cost_brl_millions > aggressive.total_cost_brl_millions
        assert conservative.total_duration_months > balanced.total_duration_months > aggressive.total_duration_months
        assert conservative.minimum_fos > balanced.minimum_fos > aggressive.minimum_fos

        print("✓ Test 2: Case progression verified")

        # Test 3: All cases have complete data
        for case in [conservative, balanced, aggressive]:
            assert case.total_cost_brl_millions > 0
            assert case.total_duration_months > 0
            assert len(case.schedule_phases) > 0
            assert len(case.cost_breakdown) > 0
            assert len(case.risks) > 0

        print("✓ Test 3: All cases have complete data")

        return True

    def run_all_tests(self) -> bool:
        """Run all UAT tests."""
        print("\n" + "=" * 80)
        print("D7 UAT TEST SUITE")
        print("=" * 80)

        tests = [
            self.test_d72_vertical_geometry,
            self.test_d73_geo_talude_iteration,
            self.test_d74_viaria_safety,
            self.test_d75_design_cases,
        ]

        passed = 0
        failed = 0

        for test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"✗ Test failed with error: {e}")
                failed += 1

        print("\n" + "=" * 80)
        print(f"TEST RESULTS: {passed} passed, {failed} failed")
        print("=" * 80)

        return failed == 0


# Main execution
if __name__ == "__main__":
    # ==================== EXECUTE WORKFLOW ====================
    print("=" * 80)
    print("D7 PRODUCTION ORCHESTRATOR — SPRINT 2 UAT EXECUTION")
    print("=" * 80)
    print()

    workflow = D7ProductionWorkflow()
    workflow_results = workflow.execute_jerico_full_workflow()

    # ==================== RUN UAT TESTS ====================
    print("\n")
    uat = D7UATTestSuite()
    uat_passed = uat.run_all_tests()

    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("SPRINT 2 DELIVERY STATUS")
    print("=" * 80)

    if uat_passed:
        print("✓ All UAT tests PASSED")
        print("✓ Production code ready for deployment")
        print("✓ Jericó Km 45+800–46+200 design package complete")
    else:
        print("✗ Some UAT tests FAILED — review errors above")

    # Save results to JSON for reporting
    output_json = {
        "sprint": "Sprint 2",
        "modules": ["D7.2", "D7.3", "D7.4", "D7.5"],
        "workflow_status": "complete" if all(s.status == "complete" for s in workflow.steps) else "incomplete",
        "uat_status": "PASSED" if uat_passed else "FAILED",
        "jerico_location": "Km 45+800 to 46+200 (400m segment)",
        "pga": "0.324g (high seismic zone)",
        "workflow_results": workflow_results,
    }

    print("\nResults JSON output:")
    print(json.dumps(output_json, indent=2, default=str))
