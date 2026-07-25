"""
D7.4 Viaria Safety — Stopping Distance & Tombamento (Rollover) Analysis
Advanced safety calculations for seismic-influenced road design.

Production module for Sprint 2 UAT.
"""

from dataclasses import dataclass
from typing import Tuple, Dict
import math


@dataclass
class ViariaInputs:
    """Input parameters for viaria safety analysis."""
    design_speed_kmh: float            # km/h
    pga: float                         # Peak Ground Acceleration (g)
    grade_pct: float                   # Road grade (slope) %
    vehicle_height_m: float            # Vehicle height (m)
    vehicle_width_m: float             # Vehicle width (m)
    pavement_friction_coeff: float = 0.45  # Dry asphalt


@dataclass
class ViariaOutputs:
    """Output from viaria safety analysis."""
    stopping_sight_distance_m: float
    ssd_seismic_amplified_m: float
    tombamento_ratio: float            # h/d ratio
    tombamento_risk_level: str         # "low", "moderate", "high"
    lane_width_adjustment_m: float     # Additional width needed
    minimum_lane_width_m: float        # Total recommended lane width
    notes: list


class StoppingDistanceCalculator:
    """
    Calculate stopping sight distance (SSD) for road design.

    Standard formula: SSD = V²/(2×g×(f + tan(grade))) + 18% seismic amplification
    """

    GRAVITY = 9.81  # m/s²
    REACTION_TIME_S = 2.0  # seconds
    SEISMIC_AMPLIFICATION = 0.18  # 18% longer stopping distance in seismic zones

    def calculate_ssd_standard(self,
                              design_speed_kmh: float,
                              friction_coeff: float,
                              grade_pct: float) -> float:
        """
        Calculate standard stopping sight distance (non-seismic).

        Formula: SSD = V² / (2 × g × (f + sin(grade_angle)))

        Where:
            V = design speed (m/s)
            g = gravity (m/s²)
            f = pavement friction coefficient
            grade = road grade (%)

        Args:
            design_speed_kmh: Design speed in km/h
            friction_coeff: Pavement friction coefficient
            grade_pct: Road grade as percentage

        Returns:
            Stopping sight distance in meters
        """
        v_ms = design_speed_kmh / 3.6  # Convert to m/s

        # Convert grade % to angle
        grade_angle = math.atan(grade_pct / 100.0)
        effective_friction = friction_coeff + math.sin(grade_angle)

        # Braking distance
        braking_distance = (v_ms ** 2) / (2 * self.GRAVITY * effective_friction)

        # Reaction distance (during braking initiation)
        reaction_distance = v_ms * self.REACTION_TIME_S

        ssd = reaction_distance + braking_distance

        return ssd

    def apply_seismic_amplification(self,
                                   standard_ssd: float,
                                   pga: float) -> float:
        """
        Apply seismic amplification to SSD.

        Formula: SSD_seismic = SSD_standard × (1 + 0.18) for PGA >= 0.25g
                              = SSD_standard for PGA < 0.25g

        Args:
            standard_ssd: Standard SSD (m)
            pga: Peak Ground Acceleration (g)

        Returns:
            Seismic-amplified SSD (m)
        """
        if pga >= 0.25:
            return standard_ssd * (1.0 + self.SEISMIC_AMPLIFICATION)
        else:
            return standard_ssd


class TombamentoCalculator:
    """
    Calculate rollover (tombamento) risk for vehicles on road.

    Risk increases with high vehicle height, steep grades, and seismic activity.
    """

    TOMBAMENTO_LIMIT_LOW_SEISMIC = 0.8   # h/d ratio limit for PGA < 0.25g
    TOMBAMENTO_LIMIT_HIGH_SEISMIC = 0.6  # h/d ratio limit for PGA >= 0.25g

    def calculate_tombamento_ratio(self,
                                  vehicle_height_m: float,
                                  vehicle_width_m: float) -> float:
        """
        Calculate tombamento ratio (height-to-distance ratio).

        Ratio = h / (d/2) where d is track width (typically width for stability)

        Vehicles with h/d > 0.6 (high seismic) or > 0.8 (low seismic) are
        at risk of rolling over on curved or sloped roads.

        Args:
            vehicle_height_m: Vehicle height (m)
            vehicle_width_m: Vehicle width (track width in m)

        Returns:
            h/d ratio
        """
        track_width = vehicle_width_m * 0.95  # Approximate track width
        ratio = vehicle_height_m / (track_width / 2.0)
        return ratio

    def assess_tombamento_risk(self,
                              tombamento_ratio: float,
                              pga: float) -> str:
        """
        Assess rollover risk level based on ratio and seismic context.

        Args:
            tombamento_ratio: h/d ratio
            pga: Peak Ground Acceleration (g)

        Returns:
            Risk level: "low", "moderate", "high"
        """
        if pga >= 0.25:
            limit = self.TOMBAMENTO_LIMIT_HIGH_SEISMIC
        else:
            limit = self.TOMBAMENTO_LIMIT_LOW_SEISMIC

        if tombamento_ratio <= limit * 0.8:
            return "low"
        elif tombamento_ratio <= limit:
            return "moderate"
        else:
            return "high"

    def required_lateral_acceleration_limit(self,
                                          design_speed_kmh: float,
                                          tombamento_ratio: float) -> float:
        """
        Calculate maximum safe lateral acceleration (g) before rollover.

        a_max = g / (2 × h/d ratio)

        Args:
            design_speed_kmh: Design speed (km/h)
            tombamento_ratio: h/d ratio

        Returns:
            Maximum safe lateral acceleration (g)
        """
        gravity = 9.81
        a_max = gravity / (2.0 * tombamento_ratio) if tombamento_ratio > 0 else 0
        return a_max


class LaneWidthAdjuster:
    """
    Adjust lane width based on seismic stability concerns.
    """

    STANDARD_LANE_WIDTH_M = 3.6  # Brazil standard

    def calculate_seismic_adjustment(self, pga: float) -> float:
        """
        Calculate lane width adjustment for seismic activity.

        Adjustment:
            PGA < 0.15g: +0.0 m
            0.15g ≤ PGA < 0.25g: +0.25 m
            0.25g ≤ PGA < 0.35g: +0.5 m
            PGA >= 0.35g: +0.75 m

        Args:
            pga: Peak Ground Acceleration (g)

        Returns:
            Lane width adjustment (m)
        """
        if pga < 0.15:
            return 0.0
        elif pga < 0.25:
            return 0.25
        elif pga < 0.35:
            return 0.5
        else:
            return 0.75

    def calculate_minimum_lane_width(self,
                                    standard_width: float,
                                    pga: float) -> float:
        """
        Calculate minimum lane width including seismic adjustment.

        Args:
            standard_width: Standard lane width (m)
            pga: Peak Ground Acceleration (g)

        Returns:
            Minimum recommended lane width (m)
        """
        adjustment = self.calculate_seismic_adjustment(pga)
        return standard_width + adjustment


class ViariaSafetyAnalyzer:
    """
    D7.4 Viaria Safety Analysis

    Comprehensive safety calculations including:
    - Stopping sight distance (SSD)
    - Rollover (tombamento) risk
    - Lane width requirements
    """

    def __init__(self):
        self.ssd_calc = StoppingDistanceCalculator()
        self.tombamento_calc = TombamentoCalculator()
        self.lane_width_adjuster = LaneWidthAdjuster()

    def analyze(self, inputs: ViariaInputs) -> ViariaOutputs:
        """
        Perform complete viaria safety analysis.

        Args:
            inputs: ViariaInputs object

        Returns:
            ViariaOutputs with all safety metrics
        """
        notes = []

        # 1. Stopping sight distance
        ssd_standard = self.ssd_calc.calculate_ssd_standard(
            inputs.design_speed_kmh,
            inputs.pavement_friction_coeff,
            inputs.grade_pct
        )
        notes.append(f"Standard SSD: {ssd_standard:.1f}m")

        ssd_seismic = self.ssd_calc.apply_seismic_amplification(
            ssd_standard,
            inputs.pga
        )
        amplification_pct = ((ssd_seismic - ssd_standard) / ssd_standard * 100) if ssd_standard > 0 else 0
        if amplification_pct > 0:
            notes.append(f"Seismic amplification: +{amplification_pct:.1f}% → {ssd_seismic:.1f}m")

        # 2. Tombamento analysis
        tombamento_ratio = self.tombamento_calc.calculate_tombamento_ratio(
            inputs.vehicle_height_m,
            inputs.vehicle_width_m
        )
        notes.append(f"Tombamento ratio (h/d): {tombamento_ratio:.3f}")

        tombamento_risk = self.tombamento_calc.assess_tombamento_risk(
            tombamento_ratio,
            inputs.pga
        )
        notes.append(f"Rollover risk: {tombamento_risk}")

        # 3. Lane width adjustment
        lane_width_adjustment = self.lane_width_adjuster.calculate_seismic_adjustment(inputs.pga)
        minimum_lane_width = self.lane_width_adjuster.calculate_minimum_lane_width(
            self.lane_width_adjuster.STANDARD_LANE_WIDTH_M,
            inputs.pga
        )
        if lane_width_adjustment > 0:
            notes.append(f"Lane width adjustment: +{lane_width_adjustment:.2f}m → {minimum_lane_width:.2f}m")

        return ViariaOutputs(
            stopping_sight_distance_m=round(ssd_standard, 1),
            ssd_seismic_amplified_m=round(ssd_seismic, 1),
            tombamento_ratio=round(tombamento_ratio, 3),
            tombamento_risk_level=tombamento_risk,
            lane_width_adjustment_m=lane_width_adjustment,
            minimum_lane_width_m=round(minimum_lane_width, 2),
            notes=notes
        )


# Example: Jericó Km 45+800 viaria safety
if __name__ == "__main__":
    jerico_viaria = ViariaInputs(
        design_speed_kmh=80,
        pga=0.324,
        grade_pct=7.0,  # 7% upgrade
        vehicle_height_m=3.2,  # Heavy truck
        vehicle_width_m=2.6,
        pavement_friction_coeff=0.45
    )

    analyzer = ViariaSafetyAnalyzer()
    result = analyzer.analyze(jerico_viaria)

    print("=" * 80)
    print("D7.4 VIARIA SAFETY ANALYSIS — JERICÓ KM 45+800")
    print("=" * 80)
    print(f"Design Speed: {jerico_viaria.design_speed_kmh} km/h")
    print(f"PGA: {jerico_viaria.pga}g")
    print(f"Grade: {jerico_viaria.grade_pct}%")
    print(f"Vehicle: H={jerico_viaria.vehicle_height_m}m, W={jerico_viaria.vehicle_width_m}m")
    print()
    print("STOPPING SIGHT DISTANCE:")
    print(f"  Standard SSD: {result.stopping_sight_distance_m} m")
    print(f"  Seismic-amplified SSD: {result.ssd_seismic_amplified_m} m")
    print()
    print("ROLLOVER (TOMBAMENTO) ANALYSIS:")
    print(f"  h/d Ratio: {result.tombamento_ratio:.3f}")
    print(f"  Risk Level: {result.tombamento_risk_level.upper()}")
    print()
    print("LANE WIDTH:")
    print(f"  Adjustment for seismic: +{result.lane_width_adjustment_m:.2f}m")
    print(f"  Minimum lane width: {result.minimum_lane_width_m:.2f}m")
    print()
    print("DETAILED NOTES:")
    for note in result.notes:
        print(f"  • {note}")
