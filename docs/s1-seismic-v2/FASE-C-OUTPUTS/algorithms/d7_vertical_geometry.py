"""
D7.2 Vertical Geometry — Advanced Algorithm
Road design with seismic-adapted slope calculations and PIV radius determination.

Production module for Sprint 2 UAT.
"""

import math
from dataclasses import dataclass
from typing import Tuple, Dict, List
from enum import Enum


class PGACategory(Enum):
    LOW = (0.05, 0.15)      # Low seismic (PGA < 0.15g)
    MODERATE = (0.15, 0.25) # Moderate (0.15g ≤ PGA < 0.25g)
    HIGH = (0.25, 0.35)     # High (0.25g ≤ PGA < 0.35g)
    VERY_HIGH = (0.35, 0.5) # Very high (PGA ≥ 0.35g)


@dataclass
class VerticalGeometryInput:
    """Input parameters for vertical geometry calculation."""
    design_speed_kmh: float          # km/h
    pga: float                        # Peak Ground Acceleration (g)
    slope_deformation_cm: float       # mm of deformation from slope analysis
    terrain_class: str                # "flat", "rolling", "mountainous"
    comfort_factor: float = 1.2       # comfort adjustment (1.0–1.5)

    def validate(self):
        """Validate input parameters."""
        assert 20 <= self.design_speed_kmh <= 120, "Speed must be 20–120 km/h"
        assert 0 <= self.pga <= 0.5, "PGA must be 0–0.5g"
        assert 0 <= self.slope_deformation_cm <= 50, "Deformation must be 0–50 cm"
        assert self.terrain_class in ["flat", "rolling", "mountainous"]
        assert 1.0 <= self.comfort_factor <= 1.5


@dataclass
class VerticalGeometryOutput:
    """Output parameters from vertical geometry calculation."""
    piv_radius_m: float              # Parabolic interpolation radius (m)
    standard_rampa_pct: float         # Standard slope (%)
    seismic_adjusted_rampa_pct: float # Seismic-adjusted slope (%)
    newmark_adjusted_rampa_pct: float # Newmark-adjusted slope after deformation
    comfort_zone: str                 # "acceptable", "marginal", "poor"
    notes: List[str]


class VerticalGeometryCalculator:
    """
    D7.2 Vertical Geometry Algorithm

    Calculates PIV radius and rampa (slope) with seismic adjustments.
    Reference: Jericó Highway, Km 45+800–46+200 segment.
    """

    # Constants
    GRAVITY = 9.81  # m/s²
    NEWMARK_THRESHOLD_CM = 10.0  # Deformation threshold for adjustment

    def __init__(self):
        self.pga_bounds = {
            PGACategory.LOW: (0.0, 0.15),
            PGACategory.MODERATE: (0.15, 0.25),
            PGACategory.HIGH: (0.25, 0.35),
            PGACategory.VERY_HIGH: (0.35, 0.5),
        }

    def classify_pga(self, pga: float) -> PGACategory:
        """Classify PGA into seismic category."""
        if pga < 0.15:
            return PGACategory.LOW
        elif pga < 0.25:
            return PGACategory.MODERATE
        elif pga < 0.35:
            return PGACategory.HIGH
        else:
            return PGACategory.VERY_HIGH

    def calculate_piv_radius(self,
                            design_speed_kmh: float,
                            delta_alpha_deg: float,
                            comfort_factor: float = 1.2) -> float:
        """
        PIV radius calculation with comfort factor.

        Formula: R = (V²) / (2 × g × sin(Δα/2)) × comfort_factor

        Where:
            V = design speed (m/s)
            g = gravity (m/s²)
            Δα = change in grade angle (radians)
            comfort_factor = 1.0–1.5 (1.2 recommended for standard comfort)

        Args:
            design_speed_kmh: Design speed in km/h
            delta_alpha_deg: Change in grade angle in degrees
            comfort_factor: Comfort adjustment multiplier

        Returns:
            PIV radius in meters
        """
        v_ms = design_speed_kmh / 3.6  # Convert km/h to m/s
        delta_alpha_rad = math.radians(delta_alpha_deg)

        # Avoid division by zero for very small angles
        sin_term = math.sin(delta_alpha_rad / 2)
        if sin_term < 0.001:
            sin_term = 0.001

        radius = (v_ms ** 2) / (2 * self.GRAVITY * sin_term)
        adjusted_radius = radius * comfort_factor

        return adjusted_radius

    def calculate_standard_rampa(self, terrain_class: str) -> float:
        """
        Standard rampa (slope) based on terrain classification.

        Args:
            terrain_class: "flat", "rolling", "mountainous"

        Returns:
            Standard slope as percentage
        """
        rampa_map = {
            "flat": 4.0,
            "rolling": 6.0,
            "mountainous": 8.0,
        }
        return rampa_map.get(terrain_class, 6.0)

    def calculate_seismic_reduction_factor(self, pga: float) -> float:
        """
        Calculate seismic reduction factor for rampa.

        Formula: factor = 1 - 0.15 × (PGA / 0.3g)

        Reduces slope when PGA increases to account for seismic hazard.
        At PGA = 0.324g (Jericó): factor = 1 - 0.15 × (0.324/0.3) ≈ 0.838

        Args:
            pga: Peak Ground Acceleration (g)

        Returns:
            Reduction factor (0.5–1.0)
        """
        reference_pga = 0.3  # Reference PGA (g)
        factor = 1.0 - (0.15 * (pga / reference_pga))
        # Clamp to reasonable bounds
        return max(0.5, min(1.0, factor))

    def calculate_seismic_adjusted_rampa(self,
                                       standard_rampa: float,
                                       pga: float) -> float:
        """
        Apply seismic adjustment to standard rampa.

        Formula: rampa_seismic = rampa_std × (1 - 0.15 × PGA/0.3g)

        Args:
            standard_rampa: Standard slope (%)
            pga: Peak Ground Acceleration (g)

        Returns:
            Seismic-adjusted slope (%)
        """
        factor = self.calculate_seismic_reduction_factor(pga)
        adjusted = standard_rampa * factor
        return round(adjusted, 2)

    def calculate_newmark_adjustment(self,
                                   seismic_rampa: float,
                                   slope_deformation_cm: float) -> Tuple[float, bool]:
        """
        Newmark integration: adjust rampa if slope deformation exceeds threshold.

        Formula: If deformation > 10cm, reduce rampa by 5% per 10cm above threshold.

        Args:
            seismic_rampa: Seismic-adjusted slope (%)
            slope_deformation_cm: Slope deformation from D6.3 (cm)

        Returns:
            Tuple of (adjusted_rampa_pct, is_adjusted)
        """
        if slope_deformation_cm <= self.NEWMARK_THRESHOLD_CM:
            return seismic_rampa, False

        # Reduction: -5% per 10cm above threshold
        excess_cm = slope_deformation_cm - self.NEWMARK_THRESHOLD_CM
        reduction_pct = (excess_cm / 10.0) * 0.05
        adjusted = seismic_rampa - (seismic_rampa * reduction_pct)

        return max(2.0, round(adjusted, 2)), True  # Min 2% slope

    def get_comfort_zone(self,
                        piv_radius_m: float,
                        design_speed_kmh: float) -> str:
        """
        Classify vertical alignment comfort based on PIV radius.

        Args:
            piv_radius_m: PIV radius (m)
            design_speed_kmh: Design speed (km/h)

        Returns:
            Comfort classification
        """
        # Minimum radius for design speed
        v_ms = design_speed_kmh / 3.6
        min_radius_strict = (v_ms ** 2) / (2 * self.GRAVITY * 0.1)  # 0.1 rad minimum

        if piv_radius_m > min_radius_strict * 1.5:
            return "acceptable"
        elif piv_radius_m > min_radius_strict * 1.0:
            return "marginal"
        else:
            return "poor"

    def calculate(self, inputs: VerticalGeometryInput) -> VerticalGeometryOutput:
        """
        Full D7.2 calculation: PIV + rampa with seismic adjustments.

        Args:
            inputs: VerticalGeometryInput object

        Returns:
            VerticalGeometryOutput with all calculated values
        """
        inputs.validate()
        notes = []

        # Step 1: Calculate PIV radius
        delta_alpha = 2.0  # Typical vertical curve deflection
        piv_radius = self.calculate_piv_radius(
            inputs.design_speed_kmh,
            delta_alpha,
            inputs.comfort_factor
        )
        notes.append(f"PIV radius: {piv_radius:.1f}m (comfort factor {inputs.comfort_factor})")

        # Step 2: Standard rampa
        standard_rampa = self.calculate_standard_rampa(inputs.terrain_class)
        notes.append(f"Standard rampa ({inputs.terrain_class}): {standard_rampa}%")

        # Step 3: Seismic adjustment
        pga_category = self.classify_pga(inputs.pga)
        seismic_rampa = self.calculate_seismic_adjusted_rampa(
            standard_rampa,
            inputs.pga
        )
        notes.append(f"Seismic adjustment (PGA {inputs.pga}g, {pga_category.name}): {seismic_rampa}%")

        # Step 4: Newmark adjustment
        newmark_rampa, is_newmark_adjusted = self.calculate_newmark_adjustment(
            seismic_rampa,
            inputs.slope_deformation_cm
        )
        if is_newmark_adjusted:
            notes.append(
                f"Newmark adjustment (deformation {inputs.slope_deformation_cm}cm): "
                f"{newmark_rampa}%"
            )
        else:
            notes.append(
                f"Newmark check: deformation {inputs.slope_deformation_cm}cm "
                f"< {self.NEWMARK_THRESHOLD_CM}cm (no adjustment)"
            )

        # Step 5: Comfort zone
        comfort = self.get_comfort_zone(piv_radius, inputs.design_speed_kmh)
        notes.append(f"Comfort zone: {comfort}")

        return VerticalGeometryOutput(
            piv_radius_m=round(piv_radius, 1),
            standard_rampa_pct=standard_rampa,
            seismic_adjusted_rampa_pct=seismic_rampa,
            newmark_adjusted_rampa_pct=newmark_rampa,
            comfort_zone=comfort,
            notes=notes
        )


# Example: Jericó Km 45+800 (high seismic context)
if __name__ == "__main__":
    calculator = VerticalGeometryCalculator()

    jerico_inputs = VerticalGeometryInput(
        design_speed_kmh=80,
        pga=0.324,  # Jericó PGA
        slope_deformation_cm=8.5,  # From slope stability analysis
        terrain_class="mountainous",
        comfort_factor=1.2
    )

    result = calculator.calculate(jerico_inputs)

    print("=" * 70)
    print("D7.2 VERTICAL GEOMETRY — JERICÓ KM 45+800")
    print("=" * 70)
    print(f"Design Speed: {jerico_inputs.design_speed_kmh} km/h")
    print(f"PGA: {jerico_inputs.pga}g")
    print(f"Slope Deformation: {jerico_inputs.slope_deformation_cm} cm")
    print(f"\nOUTPUTS:")
    print(f"  PIV Radius: {result.piv_radius_m} m")
    print(f"  Standard Rampa: {result.standard_rampa_pct}%")
    print(f"  Seismic-adjusted Rampa: {result.seismic_adjusted_rampa_pct}%")
    print(f"  Newmark-adjusted Rampa: {result.newmark_adjusted_rampa_pct}%")
    print(f"  Comfort Zone: {result.comfort_zone}")
    print(f"\nNOTES:")
    for note in result.notes:
        print(f"  • {note}")
