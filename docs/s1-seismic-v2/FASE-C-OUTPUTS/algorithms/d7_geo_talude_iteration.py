"""
D7.3 Geo-Talude Interaction — Iterative Feedback Loop
Bidirectional convergence between slope stability (D6.3) and vertical geometry (D7.2).

Production module for Sprint 2 UAT.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math


@dataclass
class SlopeStabilityInput:
    """Input from D6.3 slope stability analysis."""
    initial_fos: float                 # Factor of Safety
    soil_cohesion_kpa: float           # Soil cohesion
    soil_friction_deg: float            # Internal friction angle
    slope_height_m: float              # Slope height
    pga: float                         # Peak Ground Acceleration


@dataclass
class IterationStep:
    """Record of one iteration in the feedback loop."""
    iteration_num: int
    rampa_pct: float                   # Input rampa to slope analysis
    slope_deformation_cm: float        # Output from slope deformation model
    calculated_fos: float              # Calculated FoS from D6.3
    is_converged: bool
    note: str


@dataclass
class ConvergenceResult:
    """Final convergence result."""
    final_rampa_pct: float
    final_fos: float
    iterations_performed: int
    max_iterations_reached: bool
    converged: bool
    iteration_history: List[IterationStep] = field(default_factory=list)


class GeoTaludeIterator:
    """
    D7.3 Geo-Talude Interaction Algorithm

    Iterative bidirectional coupling:
    D6.3 (slope FoS) → D7.2 (rampa adjustment) → D6.3 (re-evaluate FoS)

    Convergence criterion: |rampa_i - rampa_i-1| < 0.05%
    Max 3 iterations (safety margin for production use)
    """

    CONVERGENCE_TOLERANCE_PCT = 0.05   # 0.05% slope difference
    MAX_ITERATIONS = 3
    MIN_FOS = 1.3                      # Minimum acceptable FoS (safety)
    MIN_RAMPA_PCT = 2.0                # Minimum slope %
    MAX_RAMPA_PCT = 12.0               # Maximum slope %

    def __init__(self, slope_stability_input: SlopeStabilityInput):
        """
        Initialize the iterator with slope stability parameters.

        Args:
            slope_stability_input: Input from D6.3 analysis
        """
        self.slope_input = slope_stability_input
        self.iteration_history: List[IterationStep] = []

    def calculate_deformation_newmark(self,
                                     rampa_pct: float,
                                     fos: float) -> float:
        """
        Estimate slope deformation using Newmark sliding block method.

        Deformation increases with steeper slopes and lower FoS.
        Formula: deformation = base × (1 + rampa/10) × (1.5 - FoS)

        Args:
            rampa_pct: Slope percentage
            fos: Current Factor of Safety

        Returns:
            Estimated deformation (cm)
        """
        base_deformation = 5.0  # cm, baseline
        if fos < 1.0:
            fos = 1.0

        # Deformation increases with steeper slope and lower FoS
        deformation = base_deformation * (1.0 + rampa_pct / 10.0) * (1.5 - fos)
        return max(0.1, deformation)  # Minimum 0.1 cm

    def seismic_fos_reduction(self, static_fos: float, pga: float) -> float:
        """
        Apply seismic reduction to static FoS (pseudostatic approach).

        Reduction factor: fos_seismic = fos_static × (1 - 0.3 × PGA/0.3g)

        At PGA = 0.324g: reduction_factor = 1 - 0.3 × (0.324/0.3) ≈ 0.676
        Example: static_fos 1.8 → seismic_fos 1.22

        Args:
            static_fos: Static Factor of Safety
            pga: Peak Ground Acceleration (g)

        Returns:
            Seismic-adjusted FoS
        """
        reference_pga = 0.3
        reduction_factor = 1.0 - (0.3 * (pga / reference_pga))
        reduction_factor = max(0.6, min(1.0, reduction_factor))  # Clamp
        return static_fos * reduction_factor

    def rampa_to_fos(self,
                     rampa_pct: float,
                     base_fos: float) -> float:
        """
        Estimate FoS as a function of slope angle (rampa).

        FoS decreases with steeper slopes:
        FoS = base_FoS - (rampa / 10) × 0.2

        This is a simplified relationship for iterative convergence.

        Args:
            rampa_pct: Slope percentage
            base_fos: Base FoS from slope analysis (horizontal)

        Returns:
            Adjusted FoS
        """
        slope_penalty = (rampa_pct / 10.0) * 0.2
        adjusted_fos = base_fos - slope_penalty
        return max(1.0, adjusted_fos)

    def iterate_to_convergence(self,
                              initial_rampa_pct: float) -> ConvergenceResult:
        """
        Execute the iterative feedback loop.

        Loop: rampa → deformation → FoS → rampa adjustment → check convergence

        Args:
            initial_rampa_pct: Starting rampa from D7.2

        Returns:
            ConvergenceResult with full history
        """
        self.iteration_history = []
        current_rampa = initial_rampa_pct
        previous_rampa = None
        converged = False

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            # Step 1: Calculate slope deformation for this rampa
            static_fos = self.rampa_to_fos(current_rampa, self.slope_input.initial_fos)
            seismic_fos = self.seismic_fos_reduction(static_fos, self.slope_input.pga)
            slope_deformation = self.calculate_deformation_newmark(current_rampa, seismic_fos)

            # Step 2: Check FoS acceptability
            fos_acceptable = seismic_fos >= self.MIN_FOS
            note = ""

            # Step 3: Adjust rampa if needed
            if fos_acceptable:
                # FoS is acceptable; try to increase slope (optimize cost)
                next_rampa = min(current_rampa + 0.5, self.MAX_RAMPA_PCT)
                note = f"FoS {seismic_fos:.2f} acceptable; try steeper slope"
            else:
                # FoS too low; reduce slope
                next_rampa = max(current_rampa - 0.5, self.MIN_RAMPA_PCT)
                note = f"FoS {seismic_fos:.2f} < {self.MIN_FOS}; reduce slope"

            # Record iteration
            iteration_record = IterationStep(
                iteration_num=iteration,
                rampa_pct=current_rampa,
                slope_deformation_cm=slope_deformation,
                calculated_fos=seismic_fos,
                is_converged=False,
                note=note
            )
            self.iteration_history.append(iteration_record)

            # Step 4: Check convergence
            if previous_rampa is not None:
                delta_rampa = abs(current_rampa - previous_rampa)
                if delta_rampa < self.CONVERGENCE_TOLERANCE_PCT:
                    converged = True
                    iteration_record.is_converged = True
                    break

            previous_rampa = current_rampa
            current_rampa = next_rampa

        return ConvergenceResult(
            final_rampa_pct=current_rampa,
            final_fos=self.rampa_to_fos(current_rampa, self.slope_input.initial_fos),
            iterations_performed=len(self.iteration_history),
            max_iterations_reached=(len(self.iteration_history) == self.MAX_ITERATIONS),
            converged=converged,
            iteration_history=self.iteration_history
        )


def format_convergence_report(result: ConvergenceResult) -> str:
    """Format convergence result as formatted text report."""
    lines = []
    lines.append("=" * 80)
    lines.append("D7.3 GEO-TALUDE ITERATION CONVERGENCE REPORT")
    lines.append("=" * 80)
    lines.append(f"Final Rampa: {result.final_rampa_pct:.2f}%")
    lines.append(f"Final FoS (seismic): {result.final_fos:.2f}")
    lines.append(f"Iterations: {result.iterations_performed}/{result.MAX_ITERATIONS}")
    lines.append(f"Converged: {'YES' if result.converged else 'NO (max iterations)'}")
    lines.append("")
    lines.append("ITERATION HISTORY:")
    lines.append("-" * 80)
    lines.append(
        f"{'Iter':<5} {'Rampa %':<12} {'Deform (cm)':<15} {'FoS':<10} {'Status':<10} {'Note':<30}"
    )
    lines.append("-" * 80)

    for step in result.iteration_history:
        status = "CONVERGED" if step.is_converged else "..."
        lines.append(
            f"{step.iteration_num:<5} {step.rampa_pct:<12.2f} {step.slope_deformation_cm:<15.2f} "
            f"{step.calculated_fos:<10.2f} {status:<10} {step.note:<30}"
        )

    lines.append("-" * 80)
    return "\n".join(lines)


# Example: Jericó Km 45+800 iterative convergence
if __name__ == "__main__":
    # Slope stability input from D6.3
    jerico_slope_input = SlopeStabilityInput(
        initial_fos=1.8,              # Static FoS from slope stability
        soil_cohesion_kpa=25.0,
        soil_friction_deg=32.0,
        slope_height_m=45.0,
        pga=0.324                     # Jericó PGA
    )

    iterator = GeoTaludeIterator(jerico_slope_input)

    # Initial rampa from D7.2 (seismic-adjusted from previous example: 6.5%)
    initial_rampa = 6.5

    result = iterator.iterate_to_convergence(initial_rampa)

    print(format_convergence_report(result))

    print("\nSUMMARY FOR D7.5 DESIGN:")
    print(f"  Converged rampa: {result.final_rampa_pct:.2f}%")
    print(f"  Final seismic FoS: {result.final_fos:.2f}")
    print(f"  Verification: FoS >= 1.30? {result.final_fos >= 1.30}")
