"""
D7.4-D7.5: Viaria Safety Seismic + Jericó Redesign
Production Implementation for Manta Associados Infrastructure Projects

Module: viaria_safety_jerico
Version: 1.0.0
Status: Production-Ready

Implements:
- D7.4: Viaria Safety Seismic (SSD, tombamento, lane width)
- D7.5: Jericó Redesign (3 cases: Conservative, Balanced, Aggressive)
- Cost-benefit analysis and risk assessment
- Km 45+800 to Km 46+200 design package

Integration: D7.1-D7.3 geometry via GeometryFeedback protocol
"""

import math
import dataclasses
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import json
from datetime import datetime


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

class DesignCase(Enum):
    """Jericó redesign case classification"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Vehicle specifications (NBR 9050, AASHTO)
VEHICLE_SPECS = {
    "light": {
        "mass_kg": 1500,
        "height_cm": 150,
        "wheelbase_m": 2.7,
        "track_width_m": 1.5,
    },
    "truck": {
        "mass_kg": 30000,
        "height_cm": 380,
        "wheelbase_m": 5.5,
        "track_width_m": 2.5,
    },
    "bus": {
        "mass_kg": 12000,
        "height_cm": 350,
        "wheelbase_m": 6.2,
        "track_width_m": 2.5,
    },
}

# Friction coefficients per vehicle and condition
FRICTION_COEFFICIENTS = {
    "dry": 0.75,
    "wet": 0.45,
    "flooded": 0.30,
}

# Seismic parameters (per ABNT NBR 15421 / USGS)
SEISMIC_AMPLIFICATION = 0.18  # 18% seismic amplification factor
TOMBAMENTO_LIMIT = 0.6        # h/d ratio limit
TOMBAMENTO_PGA_THRESHOLD = 0.25  # 0.25g PGA threshold
LANE_WIDTH_SEISMIC_DELTA = 0.5   # +0.5m if PGA > 0.3g

# Jericó baseline parameters
JERICO_BASELINE_RADIUS_M = 350
JERICO_BASELINE_GRADE_PCT = 7.0
JERICO_BASELINE_PIV_M = 1000
JERICO_BASELINE_COST_MILLION_BRL = 35.8
JERICO_BASELINE_SCHEDULE_MONTHS = 22
JERICO_KM_START = 45 + 800/1000  # Km 45+800
JERICO_KM_END = 46 + 200/1000    # Km 46+200


@dataclass
class SeismicParameters:
    """Seismic parameters for safety calculations"""
    pga_g: float  # Peak Ground Acceleration (g units)
    pgv_cm_s: float = 25.0  # Peak Ground Velocity (cm/s) - default: moderate
    predominant_period_s: float = 0.5  # Predominant period (s)

    @property
    def seismic_amplification_factor(self) -> float:
        """Calculate seismic amplification factor"""
        return 1.0 + SEISMIC_AMPLIFICATION

    @property
    def is_high_seismic(self) -> bool:
        """Check if seismic conditions are critical (PGA > 0.3g)"""
        return self.pga_g > 0.3

    @property
    def tombamento_risk(self) -> bool:
        """Check if tombamento risk is present"""
        return self.pga_g >= TOMBAMENTO_PGA_THRESHOLD


@dataclass
class VehicleParameters:
    """Vehicle parameters for stopping distance and stability"""
    vehicle_type: str  # 'light', 'truck', 'bus'
    speed_kmh: float
    mass_kg: Optional[float] = None
    height_cm: Optional[float] = None
    wheelbase_m: Optional[float] = None
    track_width_m: Optional[float] = None
    friction_condition: str = "wet"  # 'dry', 'wet', 'flooded'

    def __post_init__(self):
        """Validate and populate from vehicle_type"""
        if self.vehicle_type not in VEHICLE_SPECS:
            raise ValueError(f"Unknown vehicle type: {self.vehicle_type}")

        spec = VEHICLE_SPECS[self.vehicle_type]
        if self.mass_kg is None:
            self.mass_kg = spec["mass_kg"]
        if self.height_cm is None:
            self.height_cm = spec["height_cm"]
        if self.wheelbase_m is None:
            self.wheelbase_m = spec["wheelbase_m"]
        if self.track_width_m is None:
            self.track_width_m = spec["track_width_m"]

    @property
    def speed_ms(self) -> float:
        """Convert speed to m/s"""
        return self.speed_kmh / 3.6

    @property
    def friction_coefficient(self) -> float:
        """Get friction coefficient for condition"""
        return FRICTION_COEFFICIENTS.get(self.friction_condition, 0.45)

    @property
    def height_m(self) -> float:
        """Convert height to meters"""
        return self.height_cm / 100

    @property
    def height_to_track_ratio(self) -> float:
        """Calculate h/d ratio for tombamento assessment"""
        return self.height_m / self.track_width_m


# ============================================================================
# D7.4: VIARIA SAFETY CALCULATOR
# ============================================================================

@dataclass
class StoppingDistanceResult:
    """Stopping distance calculation result"""
    speed_kmh: float
    reaction_distance_m: float
    braking_distance_m: float
    total_ssd_m: float
    seismic_amplification_factor: float
    total_ssd_seismic_m: float
    grade_percent: float
    friction_coefficient: float
    pga_g: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return dataclasses.asdict(self)


@dataclass
class TombamentoResult:
    """Tombamento (rollover) risk assessment result"""
    vehicle_type: str
    height_to_track_ratio: float
    pga_g: float
    limit_ratio: float = TOMBAMENTO_LIMIT
    is_risk: bool = field(init=False)
    risk_factor: float = field(init=False)
    risk_level: RiskLevel = field(init=False)

    def __post_init__(self):
        """Calculate risk metrics"""
        # Risk increases with h/d ratio and PGA
        self.risk_factor = self.height_to_track_ratio * (1.0 + self.pga_g)
        self.is_risk = (self.height_to_track_ratio > self.limit_ratio) and \
                       (self.pga_g > TOMBAMENTO_PGA_THRESHOLD)

        if self.is_risk and self.pga_g > 0.35:
            self.risk_level = RiskLevel.CRITICAL
        elif self.is_risk:
            self.risk_level = RiskLevel.HIGH
        elif self.risk_factor > 1.2:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "vehicle_type": self.vehicle_type,
            "height_to_track_ratio": self.height_to_track_ratio,
            "pga_g": self.pga_g,
            "limit_ratio": self.limit_ratio,
            "is_risk": self.is_risk,
            "risk_factor": self.risk_factor,
            "risk_level": self.risk_level.value,
        }


@dataclass
class LaneWidthResult:
    """Lane width design result"""
    baseline_width_m: float
    pga_g: float
    seismic_adjustment_m: float = 0.0
    total_width_m: float = field(init=False)

    def __post_init__(self):
        """Calculate total width"""
        if self.pga_g > 0.3:
            self.seismic_adjustment_m = LANE_WIDTH_SEISMIC_DELTA
        self.total_width_m = self.baseline_width_m + self.seismic_adjustment_m

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "baseline_width_m": self.baseline_width_m,
            "pga_g": self.pga_g,
            "seismic_adjustment_m": self.seismic_adjustment_m,
            "total_width_m": self.total_width_m,
        }


class ViariaSafetyCalculator:
    """
    D7.4 Viaria Safety Seismic Calculator

    Calculates:
    - Stopping distance (SSD) with seismic amplification
    - Tombamento (rollover) risk
    - Lane width requirements
    """

    def __init__(self, reaction_time_s: float = 2.5):
        """
        Initialize calculator

        Args:
            reaction_time_s: Driver reaction time (default 2.5s per AASHTO)
        """
        self.reaction_time_s = reaction_time_s

    def calculate_stopping_distance(
        self,
        vehicle: VehicleParameters,
        seismic: SeismicParameters,
        grade_percent: float,
    ) -> StoppingDistanceResult:
        """
        Calculate stopping sight distance (SSD) with seismic amplification

        Formula: SSD = V²/(2×g×(f+tan(grade))) + 18% seismic amplification

        Args:
            vehicle: VehicleParameters
            seismic: SeismicParameters
            grade_percent: Road grade (%)

        Returns:
            StoppingDistanceResult
        """
        # Reaction distance
        reaction_distance = vehicle.speed_ms * self.reaction_time_s

        # Convert grade to decimal and calculate denominator
        grade_decimal = grade_percent / 100.0
        g = 9.81  # m/s²

        # Braking distance: d = v² / (2 × g × (f + tan(grade)))
        denominator = 2.0 * g * (vehicle.friction_coefficient + math.tan(math.atan(grade_decimal)))

        # Protect against division by zero or negative values
        if denominator <= 0:
            denominator = 2.0 * g * vehicle.friction_coefficient

        braking_distance = (vehicle.speed_ms ** 2) / denominator

        # Total SSD without seismic
        total_ssd = reaction_distance + braking_distance

        # Apply seismic amplification (18%)
        amp_factor = seismic.seismic_amplification_factor
        total_ssd_seismic = total_ssd * amp_factor

        return StoppingDistanceResult(
            speed_kmh=vehicle.speed_kmh,
            reaction_distance_m=reaction_distance,
            braking_distance_m=braking_distance,
            total_ssd_m=total_ssd,
            seismic_amplification_factor=amp_factor,
            total_ssd_seismic_m=total_ssd_seismic,
            grade_percent=grade_percent,
            friction_coefficient=vehicle.friction_coefficient,
            pga_g=seismic.pga_g,
        )

    def assess_tombamento(
        self,
        vehicle: VehicleParameters,
        seismic: SeismicParameters,
    ) -> TombamentoResult:
        """
        Assess rollover (tombamento) risk

        Limit: h/d ratio ≤ 0.6 @ PGA > 0.25g

        Args:
            vehicle: VehicleParameters
            seismic: SeismicParameters

        Returns:
            TombamentoResult
        """
        return TombamentoResult(
            vehicle_type=vehicle.vehicle_type,
            height_to_track_ratio=vehicle.height_to_track_ratio,
            pga_g=seismic.pga_g,
        )

    def calculate_lane_width(
        self,
        baseline_width_m: float,
        seismic: SeismicParameters,
    ) -> LaneWidthResult:
        """
        Calculate required lane width with seismic adjustment

        Adjustment: +0.5m if PGA > 0.3g (lateral instability)

        Args:
            baseline_width_m: Baseline lane width (typically 3.6-3.75m)
            seismic: SeismicParameters

        Returns:
            LaneWidthResult
        """
        return LaneWidthResult(
            baseline_width_m=baseline_width_m,
            pga_g=seismic.pga_g,
        )

    def full_safety_assessment(
        self,
        stationing_km: float,
        vehicle: VehicleParameters,
        seismic: SeismicParameters,
        grade_percent: float,
        baseline_lane_width_m: float = 3.6,
    ) -> Dict[str, Any]:
        """
        Comprehensive safety assessment for a section

        Args:
            stationing_km: Road stationing (Km)
            vehicle: VehicleParameters
            seismic: SeismicParameters
            grade_percent: Road grade (%)
            baseline_lane_width_m: Baseline lane width

        Returns:
            Dictionary with SSD, tombamento, and lane width results
        """
        ssd_result = self.calculate_stopping_distance(vehicle, seismic, grade_percent)
        tombamento_result = self.assess_tombamento(vehicle, seismic)
        lane_width_result = self.calculate_lane_width(baseline_lane_width_m, seismic)

        return {
            "stationing_km": stationing_km,
            "vehicle_type": vehicle.vehicle_type,
            "speed_kmh": vehicle.speed_kmh,
            "pga_g": seismic.pga_g,
            "grade_percent": grade_percent,
            "ssd": ssd_result.to_dict(),
            "tombamento": tombamento_result.to_dict(),
            "lane_width": lane_width_result.to_dict(),
            "overall_risk": self._assess_overall_risk(ssd_result, tombamento_result),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _assess_overall_risk(
        ssd: StoppingDistanceResult,
        tombamento: TombamentoResult,
    ) -> RiskLevel:
        """Assess overall safety risk from components"""
        if tombamento.risk_level == RiskLevel.CRITICAL:
            return RiskLevel.CRITICAL
        if tombamento.risk_level == RiskLevel.HIGH:
            return RiskLevel.HIGH
        if ssd.total_ssd_seismic_m > 200:  # Arbitrary critical threshold
            return RiskLevel.HIGH
        if tombamento.risk_level == RiskLevel.MEDIUM or ssd.total_ssd_seismic_m > 120:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


# ============================================================================
# D7.5: JERICÓ REDESIGN ANALYSIS
# ============================================================================

@dataclass
class JericoDesignCase:
    """Single Jericó redesign case specification"""
    case_type: DesignCase
    radius_m: float
    grade_percent: float
    piv_radius_m: float
    estimated_cost_million_brl: float
    estimated_schedule_months: int
    description: str = ""

    @property
    def cost_per_month(self) -> float:
        """Calculate cost per month"""
        return self.estimated_cost_million_brl / self.estimated_schedule_months

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "case_type": self.case_type.value,
            "radius_m": self.radius_m,
            "grade_percent": self.grade_percent,
            "piv_radius_m": self.piv_radius_m,
            "estimated_cost_million_brl": self.estimated_cost_million_brl,
            "estimated_schedule_months": self.estimated_schedule_months,
            "cost_per_month": self.cost_per_month,
            "description": self.description,
        }


@dataclass
class RiskAssessmentMetrics:
    """Risk metrics for a design case"""
    case_type: DesignCase
    stability_risk: RiskLevel
    schedule_risk: RiskLevel
    budget_risk: RiskLevel
    overall_risk: RiskLevel = field(init=False)
    confidence_score: float = 0.0  # 0-100%

    def __post_init__(self):
        """Calculate overall risk"""
        risks = [self.stability_risk, self.schedule_risk, self.budget_risk]
        risk_values = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        avg_risk_value = sum(risk_values[r] for r in risks) / len(risks)

        if avg_risk_value >= 3.5:
            self.overall_risk = RiskLevel.CRITICAL
        elif avg_risk_value >= 2.5:
            self.overall_risk = RiskLevel.HIGH
        elif avg_risk_value >= 1.5:
            self.overall_risk = RiskLevel.MEDIUM
        else:
            self.overall_risk = RiskLevel.LOW

        # Confidence increases with lower risk
        self.confidence_score = max(0, 100 - (avg_risk_value - 1) * 25)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "case_type": self.case_type.value,
            "stability_risk": self.stability_risk.value,
            "schedule_risk": self.schedule_risk.value,
            "budget_risk": self.budget_risk.value,
            "overall_risk": self.overall_risk.value,
            "confidence_score": self.confidence_score,
        }


@dataclass
class CostBenefitAnalysis:
    """Cost-benefit analysis for design cases"""
    conservative: Dict[str, Any]
    balanced: Dict[str, Any]
    aggressive: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "conservative": self.conservative,
            "balanced": self.balanced,
            "aggressive": self.aggressive,
        }


class JericoRedesignAnalysis:
    """
    D7.5 Jericó Redesign Analysis

    Analyzes 3 design cases:
    1. Conservative: Radius 400m, rampa 6.5%, PIV 1200m, cost BRL 42.5M, 28mo
    2. Balanced: Radius 350m, rampa 7.0%, PIV 1000m, cost BRL 35.8M, 22mo (RECOMMENDED)
    3. Aggressive: Radius 300m, rampa 7.5%, PIV 850m, cost BRL 28.2M, 16mo
    """

    # Define the 3 standard cases
    STANDARD_CASES = [
        JericoDesignCase(
            case_type=DesignCase.CONSERVATIVE,
            radius_m=400,
            grade_percent=6.5,
            piv_radius_m=1200,
            estimated_cost_million_brl=42.5,
            estimated_schedule_months=28,
            description="Conservative design: larger radius, gentler grade, robust approach"
        ),
        JericoDesignCase(
            case_type=DesignCase.BALANCED,
            radius_m=350,
            grade_percent=7.0,
            piv_radius_m=1000,
            estimated_cost_million_brl=35.8,
            estimated_schedule_months=22,
            description="Balanced design: moderate radius, standard grade, recommended approach (BASELINE)"
        ),
        JericoDesignCase(
            case_type=DesignCase.AGGRESSIVE,
            radius_m=300,
            grade_percent=7.5,
            piv_radius_m=850,
            estimated_cost_million_brl=28.2,
            estimated_schedule_months=16,
            description="Aggressive design: tight radius, steeper grade, cost-driven approach"
        ),
    ]

    def __init__(self, seismic_params: Optional[SeismicParameters] = None):
        """
        Initialize Jericó analysis

        Args:
            seismic_params: Optional seismic parameters for risk assessment
        """
        self.seismic = seismic_params or SeismicParameters(pga_g=0.25, pgv_cm_s=20)
        self.cases = self.STANDARD_CASES.copy()
        self.safety_calc = ViariaSafetyCalculator()

    def generate_cost_benefit_matrix(self) -> Dict[str, Any]:
        """
        Generate cost-benefit comparison matrix

        Returns:
            Matrix with cost, schedule, stability metrics for each case
        """
        matrix = {}

        for case in self.cases:
            baseline_cost = self.STANDARD_CASES[1].estimated_cost_million_brl  # Balanced
            baseline_schedule = self.STANDARD_CASES[1].estimated_schedule_months  # Balanced

            cost_delta_pct = ((case.estimated_cost_million_brl - baseline_cost) / baseline_cost) * 100
            schedule_delta_pct = ((case.estimated_schedule_months - baseline_schedule) / baseline_schedule) * 100

            # Stability score: higher radius = better lateral stability
            # Normalized: baseline = 100
            stability_score = (case.radius_m / self.STANDARD_CASES[1].radius_m) * 100

            matrix[case.case_type.value] = {
                "case": case.to_dict(),
                "cost_delta_vs_baseline_pct": cost_delta_pct,
                "schedule_delta_vs_baseline_pct": schedule_delta_pct,
                "stability_score": stability_score,
                "cost_efficiency_ratio": case.estimated_cost_million_brl / case.estimated_schedule_months,
            }

        return matrix

    def assess_risks(self) -> Dict[str, RiskAssessmentMetrics]:
        """
        Assess risks for each design case

        Returns:
            Dictionary of RiskAssessmentMetrics per case
        """
        risk_dict = {}

        for case in self.cases:
            # Assess stability risk based on radius
            # Smaller radius = higher risk
            if case.radius_m >= 400:
                stability_risk = RiskLevel.LOW
            elif case.radius_m >= 350:
                stability_risk = RiskLevel.LOW if self.seismic.pga_g < 0.3 else RiskLevel.MEDIUM
            elif case.radius_m >= 300:
                stability_risk = RiskLevel.MEDIUM if self.seismic.pga_g < 0.3 else RiskLevel.HIGH
            else:
                stability_risk = RiskLevel.HIGH

            # Assess schedule risk based on duration
            if case.estimated_schedule_months <= 16:
                schedule_risk = RiskLevel.HIGH if self.seismic.pga_g > 0.25 else RiskLevel.MEDIUM
            elif case.estimated_schedule_months <= 22:
                schedule_risk = RiskLevel.LOW
            else:
                schedule_risk = RiskLevel.LOW

            # Assess budget risk based on cost variance
            avg_cost = sum(c.estimated_cost_million_brl for c in self.cases) / len(self.cases)
            cost_variance = abs(case.estimated_cost_million_brl - avg_cost) / avg_cost

            if cost_variance > 0.2:
                budget_risk = RiskLevel.MEDIUM
            else:
                budget_risk = RiskLevel.LOW

            risk_assessment = RiskAssessmentMetrics(
                case_type=case.case_type,
                stability_risk=stability_risk,
                schedule_risk=schedule_risk,
                budget_risk=budget_risk,
            )

            risk_dict[case.case_type.value] = risk_assessment

        return risk_dict

    def recommend_case(self, priority: str = "balanced") -> Tuple[DesignCase, str]:
        """
        Recommend optimal design case by priority

        Args:
            priority: 'cost', 'schedule', 'stability', or 'balanced'

        Returns:
            Tuple of (recommended DesignCase, reason)
        """
        if priority == "cost":
            case = DesignCase.AGGRESSIVE
            reason = "Minimizes project cost (BRL 28.2M) - suitable for budget-constrained scenarios"
        elif priority == "schedule":
            case = DesignCase.AGGRESSIVE
            reason = "Minimizes project duration (16 months) - suitable for urgent delivery"
        elif priority == "stability":
            case = DesignCase.CONSERVATIVE
            reason = "Maximizes lateral stability (400m radius) - suitable for high-seismic regions"
        else:  # balanced (default)
            case = DesignCase.BALANCED
            reason = "Balances cost (BRL 35.8M), schedule (22mo), and stability - RECOMMENDED"

        return case, reason

    def full_analysis(self) -> Dict[str, Any]:
        """
        Comprehensive Jericó analysis

        Returns:
            Complete analysis with cases, costs, risks, and recommendation
        """
        cost_benefit = self.generate_cost_benefit_matrix()
        risk_assessment = self.assess_risks()
        recommended_case, recommendation_reason = self.recommend_case("balanced")

        return {
            "analysis_type": "Jericó Redesign D7.5",
            "seismic_parameters": {
                "pga_g": self.seismic.pga_g,
                "pgv_cm_s": self.seismic.pgv_cm_s,
                "predominant_period_s": self.seismic.predominant_period_s,
            },
            "cases_analysis": cost_benefit,
            "risk_assessment": {
                k: v.to_dict() for k, v in risk_assessment.items()
            },
            "recommended_case": recommended_case.value,
            "recommendation_reason": recommendation_reason,
            "timestamp": datetime.utcnow().isoformat(),
        }


# ============================================================================
# KM 45+800 TO KM 46+200 DESIGN PACKAGE
# ============================================================================

@dataclass
class SectionDesignPackage:
    """Complete design package for a road section"""
    section_name: str
    km_start: float
    km_end: float
    section_length_m: float
    design_case: DesignCase
    radius_m: float
    grade_percent: float
    piv_radius_m: float
    lane_width_m: float
    shoulder_width_m: float
    superelevation_percent: float
    design_speed_kmh: float
    estimated_cost_million_brl: float
    estimated_schedule_months: int
    estimated_earthwork_m3: float
    estimated_asphalt_m3: float
    estimated_concrete_m3: float
    notes: List[str] = field(default_factory=list)

    @property
    def total_pavement_area_m2(self) -> float:
        """Calculate total pavement area"""
        return (self.lane_width_m * 2 + self.shoulder_width_m * 2) * self.section_length_m

    @property
    def cost_per_km_million_brl(self) -> float:
        """Calculate cost per kilometer"""
        return self.estimated_cost_million_brl / (self.section_length_m / 1000)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = dataclasses.asdict(self)
        data["design_case"] = self.design_case.value
        data["total_pavement_area_m2"] = self.total_pavement_area_m2
        data["cost_per_km_million_brl"] = self.cost_per_km_million_brl
        return data


class Km45800To46200DesignPackage:
    """
    Complete design package for Jericó section Km 45+800 to Km 46+200
    (400m section)
    """

    SECTION_LENGTH_M = 400  # Km 46+200 - Km 45+800

    def __init__(self, design_case: DesignCase = DesignCase.BALANCED):
        """
        Initialize design package

        Args:
            design_case: Which case to design (CONSERVATIVE, BALANCED, AGGRESSIVE)
        """
        self.design_case = design_case
        self.jerico_analysis = JericoRedesignAnalysis()
        self.safety_calc = ViariaSafetyCalculator()

    def generate_design_package(self) -> SectionDesignPackage:
        """
        Generate complete design package for section

        Returns:
            SectionDesignPackage with full specifications
        """
        # Get case parameters
        case_params = {
            DesignCase.CONSERVATIVE: {
                "radius_m": 400,
                "grade_percent": 6.5,
                "piv_radius_m": 1200,
                "cost_million_brl": 42.5,
                "schedule_months": 28,
                "cost_factor": 1.0,  # reference
            },
            DesignCase.BALANCED: {
                "radius_m": 350,
                "grade_percent": 7.0,
                "piv_radius_m": 1000,
                "cost_million_brl": 35.8,
                "schedule_months": 22,
                "cost_factor": 0.843,
            },
            DesignCase.AGGRESSIVE: {
                "radius_m": 300,
                "grade_percent": 7.5,
                "piv_radius_m": 850,
                "cost_million_brl": 28.2,
                "schedule_months": 16,
                "cost_factor": 0.664,
            },
        }

        params = case_params[self.design_case]

        # Proportion costs and schedule to 400m section
        # Assume full project is 1km (simplified)
        section_cost_million_brl = params["cost_million_brl"] * (self.SECTION_LENGTH_M / 1000)
        section_schedule_months = params["schedule_months"]  # Schedule doesn't scale linearly

        # Estimate quantities
        lane_width_m = 3.6
        shoulder_width_m = 1.0
        pavement_width_m = (lane_width_m * 2) + (shoulder_width_m * 2)

        # Earthwork (rough estimate: 2000 m3/km for typical terrain)
        earthwork_m3 = 2000 * (self.SECTION_LENGTH_M / 1000) * params["cost_factor"]

        # Asphalt (20cm thick, typical)
        asphalt_m3 = pavement_width_m * self.SECTION_LENGTH_M * 0.20

        # Concrete (4cm for shoulders, typical)
        concrete_m3 = shoulder_width_m * 2 * self.SECTION_LENGTH_M * 0.04

        notes = []
        if params["grade_percent"] > 7.0:
            notes.append("Steep grade: monitor for vehicle braking performance")
        if params["radius_m"] < 350:
            notes.append("Tight horizontal curve: ensure adequate superelevation and friction")

        return SectionDesignPackage(
            section_name=f"Jericó Km 45+800 to Km 46+200 ({self.design_case.value.capitalize()})",
            km_start=JERICO_KM_START,
            km_end=JERICO_KM_END,
            section_length_m=self.SECTION_LENGTH_M,
            design_case=self.design_case,
            radius_m=params["radius_m"],
            grade_percent=params["grade_percent"],
            piv_radius_m=params["piv_radius_m"],
            lane_width_m=lane_width_m,
            shoulder_width_m=shoulder_width_m,
            superelevation_percent=8.0,  # Typical for curves
            design_speed_kmh=100.0,
            estimated_cost_million_brl=section_cost_million_brl,
            estimated_schedule_months=section_schedule_months,
            estimated_earthwork_m3=earthwork_m3,
            estimated_asphalt_m3=asphalt_m3,
            estimated_concrete_m3=concrete_m3,
            notes=notes,
        )

    def compare_all_cases(self) -> Dict[str, SectionDesignPackage]:
        """
        Generate design packages for all 3 cases

        Returns:
            Dictionary of SectionDesignPackage per case
        """
        packages = {}
        for case in [DesignCase.CONSERVATIVE, DesignCase.BALANCED, DesignCase.AGGRESSIVE]:
            self.design_case = case
            packages[case.value] = self.generate_design_package()
        return packages

    def safety_validation(self, design_package: SectionDesignPackage) -> Dict[str, Any]:
        """
        Validate design package against safety standards

        Args:
            design_package: SectionDesignPackage to validate

        Returns:
            Safety validation results
        """
        seismic = SeismicParameters(pga_g=0.25)  # Jericó seismic profile

        # Test with truck at design speed
        vehicle = VehicleParameters(
            vehicle_type="truck",
            speed_kmh=design_package.design_speed_kmh,
            friction_condition="wet",
        )

        safety_assessment = self.safety_calc.full_safety_assessment(
            stationing_km=JERICO_KM_START,
            vehicle=vehicle,
            seismic=seismic,
            grade_percent=design_package.grade_percent,
            baseline_lane_width_m=design_package.lane_width_m,
        )

        return {
            "design_case": design_package.design_case.value,
            "section": f"Km {design_package.km_start} to Km {design_package.km_end}",
            "design_speed_kmh": design_package.design_speed_kmh,
            "radius_m": design_package.radius_m,
            "grade_percent": design_package.grade_percent,
            "safety_assessment": safety_assessment,
            "passed_validation": safety_assessment["overall_risk"] in [RiskLevel.LOW, RiskLevel.MEDIUM],
        }


# ============================================================================
# INTEGRATED ANALYSIS & RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """
    Integrated recommendation engine for Jericó redesign

    Considers:
    - Stability and safety
    - Cost and budget
    - Schedule and timeline
    - Seismic conditions
    """

    def __init__(self, seismic_params: Optional[SeismicParameters] = None):
        """
        Initialize recommendation engine

        Args:
            seismic_params: Seismic parameters for risk assessment
        """
        self.seismic = seismic_params or SeismicParameters(pga_g=0.25)
        self.jerico_analysis = JericoRedesignAnalysis(self.seismic)

    def recommend_by_priority(
        self,
        budget_million_brl: Optional[float] = None,
        schedule_months: Optional[int] = None,
        stability_critical: bool = False,
    ) -> Dict[str, Any]:
        """
        Recommend design case based on project constraints

        Args:
            budget_million_brl: Available budget (optional constraint)
            schedule_months: Available schedule (optional constraint)
            stability_critical: If True, prioritize stability

        Returns:
            Recommendation with case, rationale, and risk assessment
        """
        analysis = self.jerico_analysis.full_analysis()
        cost_benefit = analysis["cases_analysis"]
        risk_assessment = analysis["risk_assessment"]

        recommendations = {}

        for case_type in [DesignCase.CONSERVATIVE, DesignCase.BALANCED, DesignCase.AGGRESSIVE]:
            case_key = case_type.value
            case_data = cost_benefit[case_key]
            case_params = case_data["case"]
            risk = risk_assessment[case_key]

            # Check constraints
            within_budget = budget_million_brl is None or \
                          case_params["estimated_cost_million_brl"] <= budget_million_brl
            within_schedule = schedule_months is None or \
                            case_params["estimated_schedule_months"] <= schedule_months

            can_execute = within_budget and within_schedule

            # Calculate recommendation score
            score = 50  # Base score

            # Adjust for stability
            risk_penalties = {
                "low": 0,
                "medium": 10,
                "high": 20,
                "critical": 30,
            }
            score -= risk_penalties.get(risk["overall_risk"], 10)

            # Adjust for constraints
            if within_budget:
                score += 10
            if within_schedule:
                score += 10

            # Adjust for stability priority
            if stability_critical:
                if case_type == DesignCase.CONSERVATIVE:
                    score += 15
                elif case_type == DesignCase.AGGRESSIVE:
                    score -= 15

            recommendations[case_key] = {
                "case": case_key,
                "can_execute": can_execute,
                "within_budget": within_budget,
                "within_schedule": within_schedule,
                "recommendation_score": max(0, score),
                "cost_million_brl": case_params["estimated_cost_million_brl"],
                "schedule_months": case_params["estimated_schedule_months"],
                "risk_level": risk["overall_risk"],
            }

        # Select best case: prioritize feasible cases, then by score
        feasible_cases = {k: v for k, v in recommendations.items() if v["can_execute"]}

        if feasible_cases:
            best_case = max(feasible_cases.items(), key=lambda x: x[1]["recommendation_score"])
        else:
            # If no feasible case, select the least infeasible one
            best_case = max(recommendations.items(), key=lambda x: x[1]["recommendation_score"])

        return {
            "recommended_case": best_case[0],
            "recommendation_score": best_case[1]["recommendation_score"],
            "all_recommendations": recommendations,
            "constraints": {
                "budget_million_brl": budget_million_brl,
                "schedule_months": schedule_months,
                "stability_critical": stability_critical,
            },
            "analysis": analysis,
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def export_to_json(data: Dict[str, Any], filename: str) -> None:
    """Export analysis results to JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def export_to_csv_summary(
    packages: Dict[str, SectionDesignPackage],
    filename: str,
) -> None:
    """Export design packages to CSV summary"""
    import csv

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Case", "Radius (m)", "Grade (%)", "PIV (m)",
            "Cost (BRL M)", "Schedule (mo)", "Earthwork (m3)",
            "Asphalt (m3)", "Concrete (m3)"
        ])
        for case_key, package in packages.items():
            writer.writerow([
                case_key,
                package.radius_m,
                package.grade_percent,
                package.piv_radius_m,
                round(package.estimated_cost_million_brl, 2),
                package.estimated_schedule_months,
                round(package.estimated_earthwork_m3, 0),
                round(package.estimated_asphalt_m3, 2),
                round(package.estimated_concrete_m3, 2),
            ])


# ============================================================================
# MAIN EXECUTION EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example: Full D7.4-D7.5 analysis

    # D7.4: Viaria Safety Assessment
    print("=" * 80)
    print("D7.4: VIARIA SAFETY SEISMIC ASSESSMENT")
    print("=" * 80)

    seismic = SeismicParameters(pga_g=0.25, pgv_cm_s=22)
    vehicle = VehicleParameters(
        vehicle_type="truck",
        speed_kmh=100,
        friction_condition="wet",
    )

    safety_calc = ViariaSafetyCalculator()
    assessment = safety_calc.full_safety_assessment(
        stationing_km=45.8,
        vehicle=vehicle,
        seismic=seismic,
        grade_percent=7.0,
        baseline_lane_width_m=3.6,
    )

    print("\nStopping Distance:")
    print(f"  Total SSD (no seismic): {assessment['ssd']['total_ssd_m']:.2f} m")
    print(f"  Total SSD (with seismic 18%): {assessment['ssd']['total_ssd_seismic_m']:.2f} m")

    print("\nTombamento (Rollover) Risk:")
    print(f"  h/d ratio: {assessment['tombamento']['height_to_track_ratio']:.3f}")
    print(f"  Risk level: {assessment['tombamento']['risk_level']}")

    print("\nLane Width:")
    print(f"  Baseline: {assessment['lane_width']['baseline_width_m']:.2f} m")
    print(f"  Seismic adjustment: {assessment['lane_width']['seismic_adjustment_m']:.2f} m")
    print(f"  Total width: {assessment['lane_width']['total_width_m']:.2f} m")

    print("\nOverall Safety Risk:", assessment['overall_risk'].value)

    # D7.5: Jericó Redesign Analysis
    print("\n" + "=" * 80)
    print("D7.5: JERICÓ REDESIGN ANALYSIS (3 CASES)")
    print("=" * 80)

    jerico = JericoRedesignAnalysis(seismic)
    full_analysis = jerico.full_analysis()

    print("\nCost-Benefit Analysis:")
    for case_key, case_data in full_analysis["cases_analysis"].items():
        case_info = case_data["case"]
        print(f"\n  {case_key.upper()}:")
        print(f"    Radius: {case_info['radius_m']} m")
        print(f"    Grade: {case_info['grade_percent']}%")
        print(f"    Cost: BRL {case_info['estimated_cost_million_brl']} M")
        print(f"    Schedule: {case_info['estimated_schedule_months']} months")
        print(f"    Cost/month: BRL {case_data['cost_efficiency_ratio']:.2f} M/mo")

    print("\nRisk Assessment:")
    for case_key, risk_data in full_analysis["risk_assessment"].items():
        print(f"\n  {case_key.upper()}:")
        print(f"    Stability: {risk_data['stability_risk']}")
        print(f"    Schedule: {risk_data['schedule_risk']}")
        print(f"    Budget: {risk_data['budget_risk']}")
        print(f"    Overall: {risk_data['overall_risk']}")

    print(f"\nRecommendation: {full_analysis['recommended_case'].upper()}")
    print(f"Reason: {full_analysis['recommendation_reason']}")

    # D7.5: Km 45+800 to Km 46+200 Design Packages
    print("\n" + "=" * 80)
    print("KM 45+800 TO KM 46+200 DESIGN PACKAGES")
    print("=" * 80)

    section_pkg = Km45800To46200DesignPackage()
    all_packages = section_pkg.compare_all_cases()

    for case_key, package in all_packages.items():
        print(f"\n{case_key.upper()}:")
        print(f"  Radius: {package.radius_m} m")
        print(f"  Grade: {package.grade_percent}%")
        print(f"  Lane Width: {package.lane_width_m} m")
        print(f"  Cost: BRL {package.estimated_cost_million_brl:.2f} M")
        print(f"  Schedule: {package.estimated_schedule_months} months")
        print(f"  Pavement Area: {package.total_pavement_area_m2:.0f} m²")

    # Recommendation Engine
    print("\n" + "=" * 80)
    print("RECOMMENDATION ENGINE")
    print("=" * 80)

    recommender = RecommendationEngine(seismic)
    recommendation = recommender.recommend_by_priority(
        budget_million_brl=40,
        schedule_months=24,
        stability_critical=False,
    )

    print(f"\nRecommended Case: {recommendation['recommended_case'].upper()}")
    print(f"Recommendation Score: {recommendation['recommendation_score']:.0f}/100")

    print("\nExecutability Matrix:")
    for case_key, rec_data in recommendation["all_recommendations"].items():
        status = "✓" if rec_data["can_execute"] else "✗"
        print(f"  {status} {case_key}: Score {rec_data['recommendation_score']:.0f} - "
              f"Risk {rec_data['risk_level']}")
