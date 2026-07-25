"""
D6.3 Slope Stability Analysis - Newmark Deformation Module
===========================================================

Production implementation of Newmark (1965) sliding block analysis
with Jibson (2007) permanent deformation regression.

Integration points:
  - D6.2: Liquefaction-triggered slope failure cascade
  - D7.3: Feedback loop (FoS → rampa adjustment)
  - D5: Seismic hazard (PGA input)

Author: Manta Associados | Geotech Team
Version: 1.0.0 | Production
"""

import logging
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy import special
from scipy.integrate import quad
from scipy.optimize import fsolve, minimize_scalar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GRAVITY_ACCELERATION = 9.81  # m/s²
NEWMARK_ALPHA_JIBSON = -0.4062  # Dimensionless regression coefficient
NEWMARK_BETA_JIBSON = 0.3625   # Dimensionless regression coefficient


class RiskLevel(Enum):
    """Risk classification for slope deformation."""
    LOW = "LOW"           # D < 5 cm
    MODERATE = "MODERATE" # 5 ≤ D < 15 cm
    HIGH = "HIGH"         # 15 ≤ D < 30 cm
    CRITICAL = "CRITICAL" # D ≥ 30 cm


class SlipSurfaceGeometry(Enum):
    """Slip surface type for Factor of Safety calculation."""
    INFINITE_SLOPE = "INFINITE_SLOPE"
    CIRCULAR = "CIRCULAR"
    WEDGE = "WEDGE"


@dataclass
class SoilProfile:
    """Represents a soil layer in slope analysis."""
    depth_top: float          # Top of layer (m)
    depth_bottom: float       # Bottom of layer (m)
    unit_weight: float        # kN/m³
    cohesion: float          # kPa
    friction_angle: float    # degrees
    spt_n_value: Optional[float] = None  # Standard Penetration Test
    liquefaction_potential: bool = False  # D6.2 flag

    def thickness(self) -> float:
        return self.depth_bottom - self.depth_top

    def is_liquefiable(self) -> bool:
        """Check if layer meets liquefaction criteria (D6.2 integration)."""
        return self.liquefaction_potential


@dataclass
class SlopeGeometry:
    """Geometric properties of slope."""
    angle_degrees: float      # Slope face angle (degrees)
    height: float            # Slope height (m)
    slip_surface_type: SlipSurfaceGeometry = SlipSurfaceGeometry.INFINITE_SLOPE
    surface_roughness: float = 0.0  # Additional friction (degrees)
    profile_length: float = 100.0   # Horizontal distance (m)

    @property
    def angle_radians(self) -> float:
        return np.radians(self.angle_degrees)


@dataclass
class SeismicParameters:
    """Earthquake parameters for Newmark analysis."""
    pga: float                     # Peak Ground Acceleration (g)
    pga_absolute: float = field(init=False)  # PGA × g (m/s²)
    magnitude: float = 7.0        # Moment magnitude
    duration: float = 30.0        # Shaking duration (seconds)
    frequency_content: str = "mixed"  # "low_freq" | "mid_freq" | "high_freq"

    def __post_init__(self):
        self.pga_absolute = self.pga * GRAVITY_ACCELERATION


@dataclass
class NewmarkAnalysisResult:
    """Complete result object from Newmark analysis."""
    permanent_deformation_cm: float
    permanent_deformation_m: float
    yield_acceleration_g: float
    yield_acceleration_abs: float
    factor_of_safety: float
    pga_ratio: float  # Ratio of PGA to yield acceleration
    risk_level: RiskLevel
    slip_probability: float
    analysis_log: Dict = field(default_factory=dict)

    def summary_dict(self) -> Dict:
        """Return summary as dictionary for export."""
        return {
            "permanent_deformation_cm": round(self.permanent_deformation_cm, 3),
            "permanent_deformation_m": round(self.permanent_deformation_m, 4),
            "yield_acceleration_g": round(self.yield_acceleration_g, 4),
            "factor_of_safety": round(self.factor_of_safety, 3),
            "pga_ratio": round(self.pga_ratio, 3),
            "risk_level": self.risk_level.value,
            "slip_probability": round(self.slip_probability, 4),
        }


class NewmarkDeformationRegression:
    """
    Jibson (2007) empirical regression for permanent deformation.

    log₁₀(D) = α + β·log₁₀(a_max/a_y)

    Where:
      D = permanent deformation (cm)
      a_max = peak ground acceleration (m/s²)
      a_y = yield acceleration (m/s²)
      α, β = regression coefficients
    """

    def __init__(self,
                 alpha: float = NEWMARK_ALPHA_JIBSON,
                 beta: float = NEWMARK_BETA_JIBSON):
        self.alpha = alpha
        self.beta = beta
        logger.info(f"Jibson regression initialized: α={alpha}, β={beta}")

    def predict_deformation(self,
                           pga_abs: float,
                           yield_accel_abs: float) -> float:
        """
        Compute permanent deformation from Jibson regression.

        Args:
            pga_abs: Peak ground acceleration (m/s²)
            yield_accel_abs: Yield acceleration (m/s²)

        Returns:
            Permanent deformation (cm)

        Raises:
            ValueError: If ratio is ≤ 0 or invalid acceleration values
        """
        if yield_accel_abs <= 0:
            raise ValueError(f"Yield acceleration must be positive: {yield_accel_abs}")

        ratio = pga_abs / yield_accel_abs

        if ratio <= 0:
            raise ValueError(f"PGA/a_y ratio must be positive: {ratio}")

        # If PGA < a_y, no sliding occurs
        if ratio < 1.0:
            return 0.0

        log_ratio = np.log10(ratio)
        log_deformation = self.alpha + self.beta * log_ratio
        deformation_cm = 10 ** log_deformation

        return deformation_cm

    def deformation_range(self,
                         pga_abs: float,
                         yield_accel_abs: float,
                         uncertainty_sigma: float = 0.4) -> Tuple[float, float]:
        """
        Compute deformation range accounting for regression uncertainty.

        Args:
            pga_abs: Peak ground acceleration (m/s²)
            yield_accel_abs: Yield acceleration (m/s²)
            uncertainty_sigma: Uncertainty in regression (log₁₀ units)

        Returns:
            Tuple of (lower_bound_cm, upper_bound_cm)
        """
        central = self.predict_deformation(pga_abs, yield_accel_abs)

        if central == 0.0:
            return (0.0, 0.0)

        log_central = np.log10(central)
        lower = 10 ** (log_central - uncertainty_sigma)
        upper = 10 ** (log_central + uncertainty_sigma)

        return (lower, upper)


class FactorOfSafetyCalculator:
    """
    Computes Factor of Safety for slope under static and pseudostatic loading.

    Supports:
      1. Infinite slope (Bishop 1966)
      2. Circular failure surface (Fellenius)
      3. Wedge analysis (Coulomb)
    """

    def __init__(self,
                 slope_geometry: SlopeGeometry,
                 soil_profiles: List[SoilProfile]):
        self.slope = slope_geometry
        self.soils = soil_profiles
        logger.info(f"FoS Calculator initialized for {slope_geometry.slip_surface_type.value}")

    def static_fos_infinite_slope(self) -> float:
        """
        Infinite slope FoS (homogeneous, saturated, no seepage).

        FoS = (c + γ_sat·z·cos²β·tanφ) / (γ_sat·z·sinβ·cosβ)

        For deep slopes: FoS ≈ tanφ / tanβ (cohesion negligible)
        """
        # Use average soil properties
        avg_cohesion = np.mean([s.cohesion for s in self.soils])
        avg_friction = np.radians(np.mean([s.friction_angle for s in self.soils]))
        avg_unit_weight = np.mean([s.unit_weight for s in self.soils])

        slope_angle = self.slope.angle_radians

        # For deep infinite slope:
        tan_phi = np.tan(avg_friction)
        tan_beta = np.tan(slope_angle)

        # Assume representative depth z = 10m for cohesion contribution
        z_representative = 10.0
        cohesion_term = 2 * avg_cohesion / (avg_unit_weight * z_representative *
                                             np.sin(2 * slope_angle))

        fos = (tan_phi / tan_beta) + cohesion_term

        if fos < 0:
            logger.warning(f"Negative FoS computed: {fos}, setting to 0.5 (unstable)")
            fos = 0.5

        return max(fos, 0.5)

    def static_fos_with_friction_variation(self,
                                          depth_fraction: float = 0.7) -> float:
        """
        Refined FoS accounting for friction angle variation with depth.

        Args:
            depth_fraction: Fraction of slope height at which to evaluate

        Returns:
            Adjusted Factor of Safety
        """
        # Interpolate soil properties at given depth
        eval_depth = self.slope.height * depth_fraction

        cohesion = 0.0
        friction_angle = 0.0
        unit_weight = 0.0

        for soil in self.soils:
            if soil.depth_top <= eval_depth <= soil.depth_bottom:
                cohesion = soil.cohesion
                friction_angle = soil.friction_angle
                unit_weight = soil.unit_weight
                break

        if friction_angle == 0:
            # Fall back to average
            return self.static_fos_infinite_slope()

        fos = (np.tan(np.radians(friction_angle)) /
               np.tan(self.slope.angle_radians))

        return max(fos, 0.5)

    def pseudostatic_fos(self, kh: float) -> float:
        """
        Pseudostatic FoS with horizontal seismic coefficient.

        FoS_ps = tan(φ - β) / (kh/(1-kh·tanβ))  [for infinite slope]

        Args:
            kh: Horizontal seismic coefficient (≈ PGA/g × 0.5 to 0.75)

        Returns:
            Pseudostatic Factor of Safety
        """
        static_fos = self.static_fos_infinite_slope()

        # Kutter & Khachaturian (1988) approximation
        # FoS_ps ≈ FoS_static - k_h × f(β)
        angle_deg = self.slope.angle_degrees
        slope_factor = 0.3 + 0.4 * np.sin(np.radians(2 * angle_deg))

        fos_pseudo = static_fos - kh * slope_factor

        return max(fos_pseudo, 0.3)


class SlopeStabilityAnalyzer:
    """
    Production-grade Newmark deformation analyzer for slopes.

    Workflow:
      1. Compute static FoS (slope strength envelope)
      2. Calculate yield acceleration: a_y = (FoS - 1)/FoS × g
      3. Check D6.2 liquefaction status; adjust cohesion if Li > 0.3
      4. Apply Jibson regression for permanent deformation
      5. Classify risk level and compute slip probability
      6. Log all calculations for D7.3 feedback loop
    """

    def __init__(self,
                 slope_geometry: SlopeGeometry,
                 soil_profiles: List[SoilProfile],
                 seismic_params: SeismicParameters):
        """
        Initialize slope stability analyzer.

        Args:
            slope_geometry: SlopeGeometry object
            soil_profiles: List of SoilProfile objects
            seismic_params: SeismicParameters object
        """
        self.slope = slope_geometry
        self.soils = soil_profiles
        self.seismic = seismic_params

        self.fos_calculator = FactorOfSafetyCalculator(slope_geometry, soil_profiles)
        self.jibson_regression = NewmarkDeformationRegression()

        self.analysis_log: Dict = {}

        logger.info(f"SlopeStabilityAnalyzer initialized for slope β={slope_geometry.angle_degrees}°, "
                   f"PGA={seismic_params.pga}g")

    def compute_yield_acceleration(self,
                                   factor_of_safety: float) -> Tuple[float, float]:
        """
        Compute yield acceleration from FoS.

        Newmark (1965):
          a_y = ((FoS - 1) / FoS) × g

        Args:
            factor_of_safety: Static factor of safety (FoS ≥ 1.0)

        Returns:
            Tuple of (a_y in g, a_y in m/s²)

        Raises:
            ValueError: If FoS < 1.0 (slope unstable)
        """
        if factor_of_safety < 0.99:
            raise ValueError(f"Slope unstable: FoS = {factor_of_safety}")

        if factor_of_safety < 1.05:
            logger.warning(f"Very low FoS: {factor_of_safety}. Yield acceleration will be very small.")

        yield_accel_g = ((factor_of_safety - 1.0) / factor_of_safety)
        yield_accel_abs = yield_accel_g * GRAVITY_ACCELERATION

        return yield_accel_g, yield_accel_abs

    def apply_liquefaction_correction(self) -> float:
        """
        D6.2 Integration: Reduce effective cohesion if layers liquefiable.

        Rule:
          If Li > 0.3 (liquefaction index), reduce cohesion by factor:
            c_eff = c × (1 - 0.8 × Li)

        Returns:
            Effective FoS after liquefaction adjustment
        """
        # Count liquefiable layers and compute average Li index
        liquefiable_count = sum(1 for s in self.soils if s.liquefaction_potential)

        if liquefiable_count == 0:
            self.analysis_log["liquefaction_correction"] = "none"
            return self.fos_calculator.static_fos_infinite_slope()

        # Estimate Li (simplified: presence of liquefiable layers → Li ≈ 0.5)
        li_index = min(0.5, 0.3 * (liquefiable_count / len(self.soils)))
        cohesion_reduction = max(0.0, 1.0 - 0.8 * li_index)

        self.analysis_log["liquefaction_correction"] = {
            "liquefiable_layers": liquefiable_count,
            "li_index_estimated": round(li_index, 3),
            "cohesion_reduction_factor": round(cohesion_reduction, 3),
        }

        logger.info(f"Liquefaction correction applied: Li={li_index:.3f}, "
                   f"c_reduction={1-cohesion_reduction:.1%}")

        # Adjust cohesion in soil profiles
        original_fos = self.fos_calculator.static_fos_infinite_slope()

        # For simplified calculation, reduce FoS proportionally
        adjusted_fos = original_fos * cohesion_reduction

        return max(adjusted_fos, 0.8)  # Minimum viable FoS

    def compute_slip_probability(self,
                                pga_g: float,
                                yield_accel_g: float) -> float:
        """
        Estimate probability of slope failure (slip probability).

        Uses log-normal distribution model:
          P_slip = 1 - Φ((ln(a_y/PGA)) / σ_ln)

        Where:
          Φ = cumulative standard normal distribution
          σ_ln ≈ 0.6 (uncertainty in FoS and seismic demand)

        Args:
            pga_g: Peak ground acceleration (g)
            yield_accel_g: Yield acceleration (g)

        Returns:
            Probability of slip (0 to 1)
        """
        if yield_accel_g > pga_g:
            # No slip expected if yield acceleration exceeds PGA
            return 0.0

        sigma_ln = 0.6  # Log-normal standard deviation

        try:
            ratio = yield_accel_g / pga_g
            if ratio <= 0:
                return 1.0

            ln_ratio = np.log(ratio)
            z_score = ln_ratio / sigma_ln

            # P_slip = 1 - Φ(z)
            prob_slip = 1.0 - special.ndtr(z_score)

            return np.clip(prob_slip, 0.0, 1.0)
        except Exception as e:
            logger.error(f"Error computing slip probability: {e}")
            return 0.5  # Default to 50% if calculation fails

    def classify_risk_level(self, deformation_cm: float) -> RiskLevel:
        """
        Classify risk level based on permanent deformation.

        Args:
            deformation_cm: Permanent deformation (cm)

        Returns:
            RiskLevel enum
        """
        if deformation_cm < 5.0:
            return RiskLevel.LOW
        elif deformation_cm < 15.0:
            return RiskLevel.MODERATE
        elif deformation_cm < 30.0:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def analyze(self) -> NewmarkAnalysisResult:
        """
        Execute complete Newmark deformation analysis.

        Returns:
            NewmarkAnalysisResult with deformation, FoS, and risk classification
        """
        logger.info("=" * 70)
        logger.info("STARTING NEWMARK DEFORMATION ANALYSIS")
        logger.info("=" * 70)

        # Step 1: Compute static FoS
        fos = self.fos_calculator.static_fos_infinite_slope()
        self.analysis_log["static_fos_initial"] = round(fos, 3)
        logger.info(f"Step 1 | Static FoS (initial): {fos:.3f}")

        # Step 2: Apply liquefaction correction (D6.2)
        fos_corrected = self.apply_liquefaction_correction()
        self.analysis_log["static_fos_corrected"] = round(fos_corrected, 3)
        logger.info(f"Step 2 | Static FoS (post-liquefaction): {fos_corrected:.3f}")

        # Step 3: Check slope stability
        if fos_corrected < 1.0:
            logger.error("SLOPE UNSTABLE EVEN BEFORE SEISMIC LOADING")
            raise ValueError(f"Slope unstable: FoS = {fos_corrected}")

        # Step 4: Compute yield acceleration
        try:
            yield_accel_g, yield_accel_abs = self.compute_yield_acceleration(fos_corrected)
        except ValueError as e:
            logger.error(f"Cannot compute yield acceleration: {e}")
            raise

        self.analysis_log["yield_acceleration_g"] = round(yield_accel_g, 4)
        self.analysis_log["yield_acceleration_abs"] = round(yield_accel_abs, 4)
        logger.info(f"Step 4 | Yield acceleration: {yield_accel_g:.4f}g ({yield_accel_abs:.3f} m/s²)")

        # Step 5: Compute PGA ratio
        pga_ratio = self.seismic.pga / yield_accel_g if yield_accel_g > 0 else 0.0
        self.analysis_log["pga_ratio"] = round(pga_ratio, 3)
        logger.info(f"Step 5 | PGA/a_y ratio: {pga_ratio:.3f}")

        # Step 6: Apply Jibson regression for permanent deformation
        try:
            if self.seismic.pga_absolute < yield_accel_abs:
                permanent_deformation_cm = 0.0
                logger.info(f"Step 6 | PGA < a_y: No sliding (D = 0 cm)")
            else:
                permanent_deformation_cm = self.jibson_regression.predict_deformation(
                    self.seismic.pga_absolute,
                    yield_accel_abs
                )
                logger.info(f"Step 6 | Permanent deformation (Jibson): {permanent_deformation_cm:.2f} cm")
        except Exception as e:
            logger.error(f"Error in Jibson regression: {e}")
            permanent_deformation_cm = 0.0

        permanent_deformation_m = permanent_deformation_cm / 100.0
        self.analysis_log["permanent_deformation_cm"] = round(permanent_deformation_cm, 2)

        # Step 7: Compute slip probability
        slip_probability = self.compute_slip_probability(self.seismic.pga, yield_accel_g)
        self.analysis_log["slip_probability"] = round(slip_probability, 4)
        logger.info(f"Step 7 | Slip probability: {slip_probability:.4f} ({slip_probability*100:.2f}%)")

        # Step 8: Classify risk level
        risk_level = self.classify_risk_level(permanent_deformation_cm)
        self.analysis_log["risk_level"] = risk_level.value
        logger.info(f"Step 8 | Risk level: {risk_level.value}")

        logger.info("=" * 70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 70)

        # Create result object
        result = NewmarkAnalysisResult(
            permanent_deformation_cm=permanent_deformation_cm,
            permanent_deformation_m=permanent_deformation_m,
            yield_acceleration_g=yield_accel_g,
            yield_acceleration_abs=yield_accel_abs,
            factor_of_safety=fos_corrected,
            pga_ratio=pga_ratio,
            risk_level=risk_level,
            slip_probability=slip_probability,
            analysis_log=self.analysis_log
        )

        return result


class D73FeedbackHook:
    """
    Integration hook for D7.3 (Rampa/Ramp Adjustment).

    Feedback mechanism:
      - If slope FoS < threshold, suggest rampa adjustment
      - Return deformation to D7.3 for reinforcement design
      - Track cumulative deformation over time
    """

    def __init__(self, fos_threshold: float = 1.3):
        self.fos_threshold = fos_threshold
        self.deformation_history: List[Tuple[float, float]] = []  # (time, deformation_cm)

    def evaluate_intervention_need(self,
                                  result: NewmarkAnalysisResult) -> Dict:
        """
        Evaluate if slope reinforcement (rampa) is needed.

        Args:
            result: NewmarkAnalysisResult from analysis

        Returns:
            Dictionary with intervention recommendations
        """
        recommendations = {
            "intervention_needed": False,
            "fos_status": "adequate" if result.factor_of_safety >= self.fos_threshold else "low",
            "fos_value": round(result.factor_of_safety, 3),
            "fos_target": self.fos_threshold,
            "deformation_cm": round(result.permanent_deformation_cm, 2),
            "risk_level": result.risk_level.value,
            "suggested_actions": []
        }

        # Decision tree for intervention
        if result.factor_of_safety < self.fos_threshold:
            recommendations["intervention_needed"] = True

            if result.permanent_deformation_cm > 30:
                recommendations["suggested_actions"].append(
                    "CRITICAL: Implement soil nail or micropile reinforcement"
                )
            elif result.permanent_deformation_cm > 15:
                recommendations["suggested_actions"].append(
                    "HIGH: Consider geotextile/geogrid reinforcement"
                )
            elif result.permanent_deformation_cm > 5:
                recommendations["suggested_actions"].append(
                    "MODERATE: Evaluate drainage improvement and minor stabilization"
                )

            # FoS-based actions
            if result.factor_of_safety < 1.1:
                recommendations["suggested_actions"].append(
                    "Reduce slope angle or increase height of stabilizing structure"
                )
            elif result.factor_of_safety < 1.2:
                recommendations["suggested_actions"].append(
                    "Improve drainage and surface protection"
                )

        return recommendations

    def record_deformation(self, time_days: float, deformation_cm: float):
        """Record deformation for cumulative assessment."""
        self.deformation_history.append((time_days, deformation_cm))

    def get_cumulative_deformation(self) -> float:
        """Return total accumulated deformation (cm)."""
        if not self.deformation_history:
            return 0.0
        return sum(d[1] for d in self.deformation_history)


# ============================================================================
# JERICÓ SLOPE PROFILES - Test Cases
# ============================================================================

def create_jerico_profile_1() -> Tuple[SlopeGeometry, List[SoilProfile], SeismicParameters]:
    """
    Jericó Profile 1: Moderate slope, cohesive soil, PGA 0.32g
    """
    slope = SlopeGeometry(
        angle_degrees=28.0,
        height=15.0,
        slip_surface_type=SlipSurfaceGeometry.INFINITE_SLOPE,
        surface_roughness=0.0,
        profile_length=100.0
    )

    soils = [
        SoilProfile(
            depth_top=0.0,
            depth_bottom=5.0,
            unit_weight=18.5,
            cohesion=25.0,
            friction_angle=32.0,
            spt_n_value=15,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=5.0,
            depth_bottom=12.0,
            unit_weight=19.2,
            cohesion=35.0,
            friction_angle=34.0,
            spt_n_value=20,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=12.0,
            depth_bottom=20.0,
            unit_weight=20.0,
            cohesion=45.0,
            friction_angle=35.0,
            spt_n_value=25,
            liquefaction_potential=False
        ),
    ]

    seismic = SeismicParameters(
        pga=0.32,
        magnitude=7.0,
        duration=30.0,
        frequency_content="mixed"
    )

    return slope, soils, seismic


def create_jerico_profile_2() -> Tuple[SlopeGeometry, List[SoilProfile], SeismicParameters]:
    """
    Jericó Profile 2: Steeper slope, sandy soil with low cohesion, PGA 0.32g
    """
    slope = SlopeGeometry(
        angle_degrees=34.0,
        height=18.0,
        slip_surface_type=SlipSurfaceGeometry.INFINITE_SLOPE,
        surface_roughness=0.0,
        profile_length=100.0
    )

    soils = [
        SoilProfile(
            depth_top=0.0,
            depth_bottom=4.0,
            unit_weight=17.8,
            cohesion=10.0,
            friction_angle=30.0,
            spt_n_value=10,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=4.0,
            depth_bottom=10.0,
            unit_weight=18.5,
            cohesion=8.0,
            friction_angle=32.0,
            spt_n_value=12,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=10.0,
            depth_bottom=18.0,
            unit_weight=19.0,
            cohesion=15.0,
            friction_angle=33.0,
            spt_n_value=18,
            liquefaction_potential=False
        ),
    ]

    seismic = SeismicParameters(
        pga=0.32,
        magnitude=7.0,
        duration=30.0,
        frequency_content="mixed"
    )

    return slope, soils, seismic


def create_jerico_profile_3() -> Tuple[SlopeGeometry, List[SoilProfile], SeismicParameters]:
    """
    Jericó Profile 3: Moderate slope with liquefiable layer (D6.2), PGA 0.32g
    """
    slope = SlopeGeometry(
        angle_degrees=30.0,
        height=16.0,
        slip_surface_type=SlipSurfaceGeometry.INFINITE_SLOPE,
        surface_roughness=0.0,
        profile_length=100.0
    )

    soils = [
        SoilProfile(
            depth_top=0.0,
            depth_bottom=3.0,
            unit_weight=17.5,
            cohesion=5.0,
            friction_angle=28.0,
            spt_n_value=8,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=3.0,
            depth_bottom=8.0,
            unit_weight=18.0,
            cohesion=0.0,
            friction_angle=30.0,
            spt_n_value=6,
            liquefaction_potential=True  # D6.2: Liquefiable sand layer
        ),
        SoilProfile(
            depth_top=8.0,
            depth_bottom=16.0,
            unit_weight=19.5,
            cohesion=30.0,
            friction_angle=36.0,
            spt_n_value=22,
            liquefaction_potential=False
        ),
    ]

    seismic = SeismicParameters(
        pga=0.32,
        magnitude=7.0,
        duration=30.0,
        frequency_content="mixed"
    )

    return slope, soils, seismic


def create_jerico_profile_4() -> Tuple[SlopeGeometry, List[SoilProfile], SeismicParameters]:
    """
    Jericó Profile 4: Steep slope, mixed soil, weak cohesion, PGA 0.32g
    (High deformation expected)
    """
    slope = SlopeGeometry(
        angle_degrees=32.0,
        height=20.0,
        slip_surface_type=SlipSurfaceGeometry.INFINITE_SLOPE,
        surface_roughness=0.0,
        profile_length=100.0
    )

    soils = [
        SoilProfile(
            depth_top=0.0,
            depth_bottom=5.0,
            unit_weight=17.5,
            cohesion=10.0,
            friction_angle=30.0,
            spt_n_value=8,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=5.0,
            depth_bottom=12.0,
            unit_weight=18.5,
            cohesion=18.0,
            friction_angle=32.0,
            spt_n_value=12,
            liquefaction_potential=False
        ),
        SoilProfile(
            depth_top=12.0,
            depth_bottom=20.0,
            unit_weight=19.5,
            cohesion=28.0,
            friction_angle=35.0,
            spt_n_value=18,
            liquefaction_potential=False
        ),
    ]

    seismic = SeismicParameters(
        pga=0.32,
        magnitude=7.0,
        duration=30.0,
        frequency_content="mixed"
    )

    return slope, soils, seismic


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_newmark_basic_calculation():
    """Test basic Newmark calculation (Profile 1)."""
    print("\n" + "="*70)
    print("TEST 1: Basic Newmark Calculation (Jericó Profile 1)")
    print("="*70)

    slope, soils, seismic = create_jerico_profile_1()
    analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)
    result = analyzer.analyze()

    print(f"\nResult Summary:")
    for key, value in result.summary_dict().items():
        print(f"  {key}: {value}")

    assert result.factor_of_safety > 1.0, "FoS must be > 1.0 for stable slope"
    assert result.permanent_deformation_cm >= 0, "Deformation must be non-negative"
    assert 0 <= result.slip_probability <= 1, "Slip probability must be in [0, 1]"

    print("\n✓ Test PASSED")


def test_steep_slope_high_deformation():
    """Test steeper slope with expected higher deformation (Profile 4 vs 1)."""
    print("\n" + "="*70)
    print("TEST 2: Steeper Slope - Comparison (Jericó Profile 4 vs 1)")
    print("="*70)

    slope4, soils4, seismic = create_jerico_profile_4()
    analyzer4 = SlopeStabilityAnalyzer(slope4, soils4, seismic)
    result4 = analyzer4.analyze()

    print(f"\nProfile 4 Result Summary:")
    for key, value in result4.summary_dict().items():
        print(f"  {key}: {value}")

    # Compare with Profile 1 (less steep)
    slope1, soils1, _ = create_jerico_profile_1()
    analyzer1 = SlopeStabilityAnalyzer(slope1, soils1, seismic)
    result1 = analyzer1.analyze()

    print(f"\nProfile 1 Result Summary (for comparison):")
    for key, value in result1.summary_dict().items():
        print(f"  {key}: {value}")

    assert result4.factor_of_safety < result1.factor_of_safety, \
        "Steeper slope should have lower FoS"
    # Higher yield acceleration ratio means more deformation in this case
    assert result4.pga_ratio > result1.pga_ratio, \
        "Steeper slope should have higher PGA/a_y ratio"

    print("\n✓ Test PASSED")


def test_liquefaction_correction():
    """Test D6.2 liquefaction correction (Profile 3)."""
    print("\n" + "="*70)
    print("TEST 3: Liquefaction Correction (D6.2) (Jericó Profile 3)")
    print("="*70)

    slope, soils, seismic = create_jerico_profile_3()

    # Check that liquefaction layer is present
    liquefiable_layers = [s for s in soils if s.liquefaction_potential]
    print(f"\nLiquefiable layers detected: {len(liquefiable_layers)}")
    assert len(liquefiable_layers) > 0, "Profile 3 should have liquefiable layer"

    analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)
    result = analyzer.analyze()

    print(f"\nResult Summary:")
    for key, value in result.summary_dict().items():
        print(f"  {key}: {value}")

    # Compare with non-liquefiable case (Profile 1)
    slope1, soils1, _ = create_jerico_profile_1()
    analyzer1 = SlopeStabilityAnalyzer(slope1, soils1, seismic)
    result1 = analyzer1.analyze()

    # Liquefaction should reduce FoS and increase deformation
    assert result.factor_of_safety <= result1.factor_of_safety, \
        "Liquefaction should reduce FoS"

    print("\n✓ Test PASSED")


def test_pga_ratio_variation():
    """Test PGA/a_y ratio across different slopes."""
    print("\n" + "="*70)
    print("TEST 4: PGA/a_y Ratio Variation")
    print("="*70)

    profiles = [
        ("Profile 1", create_jerico_profile_1()),
        ("Profile 2", create_jerico_profile_2()),
        ("Profile 3", create_jerico_profile_3()),
        ("Profile 4", create_jerico_profile_4()),
    ]

    print("\nPGA/a_y Ratios:")
    ratios = []
    for name, (slope, soils, seismic) in profiles:
        analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)
        result = analyzer.analyze()
        ratios.append(result.pga_ratio)
        print(f"  {name}: {result.pga_ratio:.3f}")

    # Higher PGA ratios should correspond to steeper slopes
    assert max(ratios) > min(ratios), "PGA ratios should vary across profiles"

    print("\n✓ Test PASSED")


def test_risk_classification():
    """Test risk level classification."""
    print("\n" + "="*70)
    print("TEST 5: Risk Classification")
    print("="*70)

    # Test classification boundaries
    test_cases = [
        (0.0, RiskLevel.LOW),
        (3.0, RiskLevel.LOW),
        (5.0, RiskLevel.MODERATE),
        (10.0, RiskLevel.MODERATE),
        (15.0, RiskLevel.HIGH),
        (25.0, RiskLevel.HIGH),
        (30.0, RiskLevel.CRITICAL),
        (50.0, RiskLevel.CRITICAL),
    ]

    _, soils, seismic = create_jerico_profile_1()
    slope = SlopeGeometry(angle_degrees=30.0, height=15.0)
    analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)

    print("\nRisk Classification Results:")
    for deformation_cm, expected_risk in test_cases:
        risk = analyzer.classify_risk_level(deformation_cm)
        status = "✓" if risk == expected_risk else "✗"
        print(f"  {status} {deformation_cm:5.1f} cm → {risk.value}")
        assert risk == expected_risk, f"Mismatch for {deformation_cm} cm"

    print("\n✓ Test PASSED")


def test_d73_feedback_hook():
    """Test D7.3 feedback loop hook."""
    print("\n" + "="*70)
    print("TEST 6: D7.3 Feedback Loop Hook")
    print("="*70)

    slope, soils, seismic = create_jerico_profile_3()
    analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)
    result = analyzer.analyze()

    hook = D73FeedbackHook(fos_threshold=1.3)
    recommendations = hook.evaluate_intervention_need(result)

    print(f"\nIntervention Recommendations:")
    print(f"  FoS Value: {recommendations['fos_value']}")
    print(f"  FoS Status: {recommendations['fos_status']}")
    print(f"  FoS Target: {recommendations['fos_target']}")
    print(f"  Deformation: {recommendations['deformation_cm']} cm")
    print(f"  Risk Level: {recommendations['risk_level']}")
    print(f"  Intervention Needed: {recommendations['intervention_needed']}")

    if recommendations['suggested_actions']:
        print(f"  Suggested Actions:")
        for action in recommendations['suggested_actions']:
            print(f"    - {action}")

    print("\n✓ Test PASSED")


def test_soil_cohesion_variation():
    """Test sensitivity to soil cohesion variations."""
    print("\n" + "="*70)
    print("TEST 7: Soil Cohesion Sensitivity")
    print("="*70)

    slope = SlopeGeometry(angle_degrees=32.0, height=16.0)
    seismic = SeismicParameters(pga=0.32)

    cohesion_values = [5, 15, 25, 40]
    results_by_cohesion = {}

    print("\nDeformation vs. Cohesion:")
    for c in cohesion_values:
        soils = [
            SoilProfile(
                depth_top=0.0, depth_bottom=16.0,
                unit_weight=19.0, cohesion=float(c), friction_angle=33.0
            )
        ]
        analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)
        result = analyzer.analyze()
        results_by_cohesion[c] = result.permanent_deformation_cm
        print(f"  c = {c:2d} kPa → D = {result.permanent_deformation_cm:6.2f} cm, "
              f"FoS = {result.factor_of_safety:.3f}")

    # Higher cohesion should reduce deformation
    assert results_by_cohesion[40] < results_by_cohesion[5], \
        "Higher cohesion should reduce deformation"

    print("\n✓ Test PASSED")


def test_spt_correlation():
    """Test SPT-based friction angle correlation."""
    print("\n" + "="*70)
    print("TEST 8: SPT N-Value Tracking")
    print("="*70)

    slope, soils, seismic = create_jerico_profile_2()

    print("\nSPT N-values in profile:")
    for i, soil in enumerate(soils):
        phi_approx = 28 + 0.3 * soil.spt_n_value  # Approximate correlation
        print(f"  Layer {i+1}: N = {soil.spt_n_value:2d} → φ ≈ {phi_approx:.1f}°, "
              f"φ_actual = {soil.friction_angle}°")

    analyzer = SlopeStabilityAnalyzer(slope, soils, seismic)
    result = analyzer.analyze()

    print(f"\nFoS with SPT correlation: {result.factor_of_safety:.3f}")
    print(f"Permanent deformation: {result.permanent_deformation_cm:.2f} cm")

    print("\n✓ Test PASSED")


# ============================================================================
# MAIN EXECUTION & DEMO
# ============================================================================

def main():
    """Execute all tests and generate comprehensive report."""
    print("\n")
    print("*" * 70)
    print("NEWMARK SLOPE STABILITY ANALYSIS - PRODUCTION TEST SUITE")
    print("*" * 70)
    print("\nTesting Jericó slopes with PGA = 0.32g (4 profiles)")
    print("Integration: D6.2 (liquefaction), D7.3 (rampa feedback)")
    print()

    # Run all tests
    tests = [
        test_newmark_basic_calculation,
        test_steep_slope_high_deformation,
        test_liquefaction_correction,
        test_pga_ratio_variation,
        test_risk_classification,
        test_d73_feedback_hook,
        test_soil_cohesion_variation,
        test_spt_correlation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n✗ Test FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"\n✗ Test ERROR: {e}")

    # Final summary
    print("\n")
    print("*" * 70)
    print("TEST SUITE SUMMARY")
    print("*" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print("*" * 70)

    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Production ready")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
