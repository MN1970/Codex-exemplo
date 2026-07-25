"""
D6.2 Liquefaction Susceptibility Analysis
==========================================

Implementation of Tokimatsu & Yoshida (1983) Liquefaction Index (LI) algorithm
with Idriss (2004) magnitude scaling factors and empirical depth reduction.

Production-ready for CI/CD integration with D7.3 feedback module.

Author: Manta Associados - Geotechnical Engineering
Version: 1.0.0
Date: 2026-07-25

References:
    - Tokimatsu, K., & Yoshida, H. (1983). Empirical correlation of soil
      liquefaction based on SPT N-value and fines content. Soils and Foundations.
    - Idriss, I. M. (2004). An updated flexible fatigue design curve for
      earthquake-induced cyclic stress. PEER Report.
    - Seed, H. B., & Idriss, I. M. (1971). Simplified procedure for evaluating
      earthquake-induced liquefaction potential. JSMFE.
"""

import math
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional, Union
from abc import ABC, abstractmethod


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============================================================================
# ENUMERATIONS & DATA CLASSES
# ============================================================================

class RiskLevel(Enum):
    """Liquefaction risk classification."""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"


class SoilType(Enum):
    """SPT N-value based soil classification."""
    SAND = "Sand"
    SILTY_SAND = "Silty Sand"
    SANDY_SILT = "Sandy Silt"
    SILT = "Silt"
    CLAY = "Clay"


@dataclass
class LayerData:
    """Single 1m soil layer properties."""
    depth_mid: float  # Depth to layer midpoint (m)
    n_value: int  # Uncorrected SPT N (blows/30cm)
    fines_content: float  # Fines % (silt + clay)
    water_table_depth: float  # Depth to water table (m)
    unit_weight: float  # Total unit weight (kN/m³)
    sigma_v0_prime: float  # Effective vertical stress (kPa)

    def __post_init__(self):
        """Validate layer data."""
        if self.depth_mid < 0:
            raise ValueError("Depth must be >= 0")
        if self.n_value < 0:
            raise ValueError("SPT N-value must be >= 0")
        if not (0 <= self.fines_content <= 100):
            raise ValueError("Fines content must be 0-100%")
        if self.water_table_depth < 0:
            raise ValueError("Water table depth must be >= 0")
        if self.unit_weight <= 0:
            raise ValueError("Unit weight must be > 0")
        if self.sigma_v0_prime <= 0:
            raise ValueError("Effective stress must be > 0")


@dataclass
class SiteConditions:
    """Earthquake and site parameters."""
    magnitude: float  # Earthquake magnitude (Mw)
    peak_accel_g: float  # Peak ground acceleration (fraction of g)
    depth_water_table: float  # Depth to water table (m)
    vs30: float  # Shear wave velocity 0-30m (m/s)

    def __post_init__(self):
        """Validate site conditions."""
        if not (4.0 <= self.magnitude <= 9.0):
            raise ValueError("Magnitude must be 4.0-9.0 Mw")
        if not (0.01 <= self.peak_accel_g <= 2.0):
            raise ValueError("Peak accel must be 0.01-2.0g")
        if self.depth_water_table < 0:
            raise ValueError("Water table depth must be >= 0")
        if self.vs30 <= 0:
            raise ValueError("Vs30 must be > 0 m/s")


@dataclass
class LiquefactionResult:
    """Single layer liquefaction analysis."""
    depth_mid: float
    n_value: int
    n_corrected: int
    crr: float
    csr: float
    msf: float
    rd: float
    fs: float
    li_contribution: float
    soil_type: SoilType
    risk_level: RiskLevel
    notes: str


@dataclass
class SiteAnalysisResult:
    """Complete site liquefaction analysis."""
    site_id: str
    magnitude: float
    peak_accel_g: float
    total_li: float
    risk_level: RiskLevel
    liquefiable_depth: float  # Deepest potentially liquefiable layer (m)
    num_high_risk_layers: int
    layers: List[LiquefactionResult]
    warnings: List[str]
    debug_log: Dict

    def summary(self) -> str:
        """Generate text summary."""
        summary_text = f"""
Liquefaction Analysis Summary - Site {self.site_id}
{'='*60}
Earthquake Conditions:
  - Magnitude: {self.magnitude:.2f} Mw
  - Peak Acceleration: {self.peak_accel_g:.3f}g

Liquefaction Index (Tokimatsu & Yoshida):
  - Total LI: {self.total_li:.3f}
  - Risk Level: {self.risk_level.value}
  - Deepest Liquefiable Layer: {self.liquefiable_depth:.2f}m
  - Number of High-Risk Layers: {self.num_high_risk_layers}

Layer Details:
  Total Layers Analyzed: {len(self.layers)}

Details by Layer:
"""
        for layer in self.layers:
            summary_text += f"""
  Depth {layer.depth_mid:.1f}m ({layer.soil_type.value}):
    - SPT N: {layer.n_value} (corrected: {layer.n_corrected})
    - CRR: {layer.crr:.4f}
    - CSR: {layer.csr:.4f}
    - MSF: {layer.msf:.4f}
    - Depth Reduction (rd): {layer.rd:.4f}
    - Factor of Safety: {layer.fs:.4f}
    - LI Contribution: {layer.li_contribution:.4f}
    - Risk: {layer.risk_level.value}
"""

        if self.warnings:
            summary_text += f"\nWarnings:\n"
            for warning in self.warnings:
                summary_text += f"  - {warning}\n"

        return summary_text


# ============================================================================
# CORRECTION FACTORS & HELPER FUNCTIONS
# ============================================================================

class CorrectionFactors:
    """Static methods for SPT and stress corrections."""

    @staticmethod
    def overburden_correction(sigma_v0_prime: float) -> float:
        """
        CN: Overburden pressure correction (Liao & Whitman, 1986)

        Args:
            sigma_v0_prime: Effective vertical stress (kPa)

        Returns:
            CN correction factor (normalized to 1.0 at 100 kPa)
        """
        if sigma_v0_prime <= 0:
            raise ValueError("Effective stress must be > 0")

        # CN = (100 / sigma_v0')^0.5, normalized
        cn = math.sqrt(100.0 / sigma_v0_prime)

        # Cap CN to 1.7 (upper limit from literature)
        cn = min(cn, 1.7)

        logger.debug(f"CN = {cn:.4f} for σ'_v0 = {sigma_v0_prime:.2f} kPa")
        return cn

    @staticmethod
    def fines_correction(fines_content: float) -> float:
        """
        CE: Fines content correction (Seed et al., 1985)

        Adjusts CRR based on percentage of fines (silt + clay).
        High fines reduce liquefaction potential.

        Args:
            fines_content: Fines percentage (0-100%)

        Returns:
            CE correction factor
        """
        if not (0 <= fines_content <= 100):
            raise ValueError("Fines must be 0-100%")

        # Simplified Seed approach
        if fines_content < 5:
            ce = 1.0
        elif fines_content < 35:
            # Linear interpolation 5%-35%
            ce = 1.0 - 0.01 * (fines_content - 5) / 30
        else:
            # Beyond 35%, clay and silt effects dominate
            # Liquefaction potential decreases significantly
            ce = 0.9

        logger.debug(f"CE = {ce:.4f} for fines = {fines_content:.1f}%")
        return ce

    @staticmethod
    def depth_reduction_factor(depth_mid: float) -> float:
        """
        rd: Depth reduction factor (Idriss & Boulanger, 2008)

        Empirical relationship accounting for confining stress effects.
        Valid 0-20m depth range.

        Args:
            depth_mid: Depth to layer midpoint (m)

        Returns:
            rd factor (1.0 at surface, decreasing with depth)
        """
        if depth_mid < 0:
            raise ValueError("Depth must be >= 0")

        if depth_mid == 0:
            return 1.0

        # Idriss & Boulanger (2008) fits
        if depth_mid <= 9.15:
            rd = 1.0 - 0.00765 * depth_mid
        elif depth_mid <= 20:
            rd = 1.174 - 0.0267 * depth_mid
        else:
            # Beyond 20m, rd approaches ~0.6-0.7 (theoretical limit)
            rd = max(1.174 - 0.0267 * 20, 0.6)
            logger.warning(f"Depth {depth_mid}m exceeds 20m range; rd extrapolated")

        rd = max(rd, 0.6)  # Lower bound

        logger.debug(f"rd = {rd:.4f} at depth = {depth_mid:.2f}m")
        return rd


# ============================================================================
# MAGNITUDE SCALING FACTOR (MSF)
# ============================================================================

class MagnitudeScaling:
    """Idriss (2004) and Idriss & Boulanger (2008) magnitude scaling."""

    @staticmethod
    def idriss_2004_msf(magnitude: float, n_corrected: int) -> float:
        """
        Magnitude Scaling Factor (Idriss, 2004)

        MSF normalizes CRR to M=7.5 earthquake. Reduces CRR for smaller
        magnitudes and increases for larger ones.

        Uses: MSF = (7.5 / M)^2.56 for standard reference magnitude effect

        Args:
            magnitude: Moment magnitude (Mw)
            n_corrected: Normalized SPT N-value (N1_60)

        Returns:
            MSF factor (1.0 at M=7.5, >1 for M<7.5, <1 for M>7.5)
        """
        if not (4.0 <= magnitude <= 9.0):
            raise ValueError("Magnitude must be 4.0-9.0 Mw")

        if n_corrected <= 0:
            raise ValueError("Corrected N must be > 0")

        # Standard form: MSF = (7.5 / M)^k where k ~= 2.4-2.6
        # Reference: Idriss (2004), Idriss & Boulanger (2008)
        k = 2.56
        msf = (7.5 / magnitude) ** k

        # Ensure MSF is within physical bounds
        msf = max(msf, 0.5)  # Lower bound for very high magnitude (M>9)
        msf = min(msf, 2.0)  # Upper bound for very low magnitude (M<4)

        logger.debug(f"MSF = {msf:.4f} for M = {magnitude:.2f}, N1_60 = {n_corrected}")
        return msf

    @staticmethod
    def idriss_boulanger_2008_msf(magnitude: float) -> float:
        """
        Updated MSF from Idriss & Boulanger (2008)

        Slightly refined version, independent of N-value.

        Args:
            magnitude: Moment magnitude (Mw)

        Returns:
            MSF factor
        """
        if not (4.0 <= magnitude <= 9.0):
            raise ValueError("Magnitude must be 4.0-9.0 Mw")

        # Idriss & Boulanger (2008) refinement
        # MSF ≈ (7.5/M)^2.56 for M < 7.5
        # MSF ≈ (7.5/M)^2.56 for M >= 7.5

        if magnitude < 7.5:
            msf = (7.5 / magnitude) ** 2.56
        else:
            # For larger magnitudes, MSF < 1 (unfavorable)
            msf = (7.5 / magnitude) ** 2.56

        msf = max(msf, 0.5)
        msf = min(msf, 2.5)

        return msf


# ============================================================================
# CYCLIC STRESS RATIO (CSR) CALCULATION
# ============================================================================

class CyclicStressRatio:
    """CSR and dynamic stress calculations."""

    @staticmethod
    def calculate_csr(
        peak_accel_g: float,
        sigma_v0: float,
        sigma_v0_prime: float,
        depth_reduction: float,
        gravity: float = 9.81
    ) -> float:
        """
        CSR: Cyclic Stress Ratio (Seed & Idriss, 1971)

        CSR = τ_av / σ_v0 = 0.65 × (a_max/g) × (σ_v0/σ_v0') × rd

        Args:
            peak_accel_g: Peak ground acceleration (fraction of g)
            sigma_v0: Total vertical stress (kPa)
            sigma_v0_prime: Effective vertical stress (kPa)
            depth_reduction: rd factor
            gravity: Gravitational acceleration (m/s²)

        Returns:
            CSR (dimensionless ratio)
        """
        if peak_accel_g <= 0:
            raise ValueError("Peak acceleration must be > 0")
        if sigma_v0 <= 0:
            raise ValueError("Total stress must be > 0")
        if sigma_v0_prime <= 0:
            raise ValueError("Effective stress must be > 0")
        if not (0.5 <= depth_reduction <= 1.0):
            logger.warning(f"rd = {depth_reduction:.4f} outside typical range")

        # Stress ratio
        stress_ratio = sigma_v0 / sigma_v0_prime

        # Seed & Idriss (1971) coefficient
        coefficient = 0.65

        # CSR calculation
        csr = coefficient * peak_accel_g * stress_ratio * depth_reduction

        logger.debug(
            f"CSR = {csr:.4f} from "
            f"a_max={peak_accel_g:.3f}g, σ_v0/σ'_v0={stress_ratio:.3f}, rd={depth_reduction:.4f}"
        )
        return csr


# ============================================================================
# CYCLIC RESISTANCE RATIO (CRR) FROM SPT
# ============================================================================

class CyclicResistanceRatio:
    """CRR determination from SPT N-value."""

    @staticmethod
    def calculate_crr_from_spt(
        n_value: int,
        sigma_v0_prime: float,
        fines_content: float
    ) -> float:
        """
        CRR: Cyclic Resistance Ratio from SPT (Tokimatsu & Yoshida, 1983)

        CRR normalized to N1_60 and adjusted for fines.

        Args:
            n_value: Uncorrected SPT N (blows/30cm)
            sigma_v0_prime: Effective vertical stress (kPa)
            fines_content: Fines percentage (0-100%)

        Returns:
            CRR at reference M=7.5 (before MSF adjustment)
        """
        if n_value < 0:
            raise ValueError("SPT N must be >= 0")
        if sigma_v0_prime <= 0:
            raise ValueError("Effective stress must be > 0")
        if not (0 <= fines_content <= 100):
            raise ValueError("Fines must be 0-100%")

        # Step 1: Normalize N-value to N1_60
        # N1_60 = N × (100 / σ'_v0)^0.5 × (CE) × (CB)
        # where CB = 1.2 for hammer energy (Japanese SPT ~72%)

        cn = CorrectionFactors.overburden_correction(sigma_v0_prime)
        ce = CorrectionFactors.fines_correction(fines_content)
        cb = 1.2  # Hammer energy ratio (Japanese vs. 60% ASTM)

        n1_60 = n_value * cn * ce * cb

        # Cap N1_60 at reasonable limits
        n1_60 = min(n1_60, 50)

        logger.debug(f"N1_60 = {n1_60:.2f} from N={n_value}, CN={cn:.4f}, CE={ce:.4f}")

        # Step 2: CRR from empirical correlation (Tokimatsu & Yoshida, 1983)
        # For clean sand: CRR = (N1_60 + 15) / 1000 to 0.02 + N1_60/400

        if n1_60 <= 3:
            # Very loose sand - high liquefaction potential
            crr = 0.02
        elif n1_60 <= 30:
            # Linear region - common case
            crr = (n1_60 + 15) / 1000
        elif n1_60 <= 50:
            # Dense sand - lower liquefaction potential
            crr = 0.02 + (n1_60 - 30) / 400
        else:
            # Very dense sand - negligible liquefaction risk
            crr = 0.06

        # For silty sands, reduce CRR slightly
        if fines_content > 35:
            crr *= 0.85

        logger.debug(f"CRR = {crr:.4f}")
        return crr


# ============================================================================
# FACTOR OF SAFETY & LIQUEFACTION INDEX
# ============================================================================

class FactorOfSafety:
    """FS and LI calculations."""

    @staticmethod
    def calculate_fs(
        crr: float,
        csr: float,
        msf: float,
        rd: float
    ) -> float:
        """
        Factor of Safety (Tokimatsu & Yoshida, 1983)

        FS = CRR / (CSR × MSF × rd)

        Note: Some formulations include MSF in numerator and apply
        differently. This follows the Idriss framework where MSF
        accounts for earthquake magnitude.

        Args:
            crr: Cyclic Resistance Ratio (at reference M=7.5)
            csr: Cyclic Stress Ratio
            msf: Magnitude Scaling Factor
            rd: Depth Reduction Factor

        Returns:
            FS (typically 0.5-2.0; < 1 = liquefiable)
        """
        if crr <= 0:
            raise ValueError("CRR must be > 0")
        if csr <= 0:
            raise ValueError("CSR must be > 0")
        if msf <= 0:
            raise ValueError("MSF must be > 0")
        if rd <= 0:
            raise ValueError("rd must be > 0")

        # FS = CRR / (CSR × MSF × rd)
        denominator = csr * msf * rd

        if denominator == 0:
            raise ValueError("Invalid CSR, MSF, or rd combination")

        fs = crr / denominator

        logger.debug(f"FS = CRR/(CSR×MSF×rd) = {crr:.4f}/({csr:.4f}×{msf:.4f}×{rd:.4f}) = {fs:.4f}")
        return fs

    @staticmethod
    def calculate_li_contribution(fs: float) -> float:
        """
        LI Contribution (Tokimatsu & Yoshida, 1983)

        LI_i = max(0, 1 - FS_i)

        If FS >= 1, layer is safe (LI = 0).
        If FS < 1, layer contributes to LI.

        Args:
            fs: Factor of Safety for layer

        Returns:
            LI contribution for this layer (0.0-1.0)
        """
        if fs <= 0:
            raise ValueError("FS must be > 0")

        li = max(0.0, 1.0 - fs)

        # Cap at 1.0 (corresponds to FS = 0, certain liquefaction)
        li = min(li, 1.0)

        logger.debug(f"LI contribution = max(0, 1-{fs:.4f}) = {li:.4f}")
        return li


# ============================================================================
# SOIL TYPE CLASSIFICATION
# ============================================================================

class SoilClassification:
    """Classify soil based on SPT N and fines content."""

    @staticmethod
    def classify(n_value: int, fines_content: float) -> SoilType:
        """
        Classify soil type for reporting.

        Args:
            n_value: SPT N-value
            fines_content: Fines percentage (0-100%)

        Returns:
            SoilType enum
        """
        if fines_content < 5:
            return SoilType.SAND
        elif fines_content < 25:
            return SoilType.SILTY_SAND
        elif fines_content < 50:
            return SoilType.SANDY_SILT
        elif fines_content < 75:
            return SoilType.SILT
        else:
            return SoilType.CLAY


class RiskAssessment:
    """Determine liquefaction risk level."""

    @staticmethod
    def classify_layer_risk(fs: float, li: float) -> RiskLevel:
        """
        Classify single layer liquefaction risk.

        Args:
            fs: Factor of Safety
            li: LI contribution

        Returns:
            RiskLevel enum
        """
        if fs >= 1.2:
            return RiskLevel.VERY_LOW
        elif fs >= 1.0:
            return RiskLevel.LOW
        elif fs >= 0.75:
            return RiskLevel.MODERATE
        elif fs >= 0.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    @staticmethod
    def classify_site_risk(total_li: float) -> RiskLevel:
        """
        Classify overall site liquefaction risk from LI.

        Tokimatsu & Yoshida (1983) thresholds:
        - LI < 5: Very Low risk
        - 5 <= LI < 15: Low risk
        - 15 <= LI < 30: Moderate risk
        - 30 <= LI < 50: High risk
        - LI >= 50: Very High risk

        Args:
            total_li: Total Liquefaction Index

        Returns:
            RiskLevel enum
        """
        if total_li < 5:
            return RiskLevel.VERY_LOW
        elif total_li < 15:
            return RiskLevel.LOW
        elif total_li < 30:
            return RiskLevel.MODERATE
        elif total_li < 50:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================

class LiquefactionAnalyzer:
    """
    Production-grade D6.2 Liquefaction analysis engine.

    Implements Tokimatsu & Yoshida (1983) with Idriss (2004) magnitude scaling
    and empirical depth reduction factors.
    """

    def __init__(self, site_id: str = "SITE-001", verbose: bool = False):
        """
        Initialize analyzer.

        Args:
            site_id: Unique site identifier
            verbose: Enable debug logging
        """
        self.site_id = site_id
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.info(f"LiquefactionAnalyzer initialized for {site_id}")

    def analyze_layer(
        self,
        layer: LayerData,
        site_conditions: SiteConditions
    ) -> LiquefactionResult:
        """
        Analyze single 1m soil layer.

        Args:
            layer: LayerData object with soil properties
            site_conditions: SiteConditions with earthquake parameters

        Returns:
            LiquefactionResult with FS, LI, and risk classification
        """
        logger.info(f"Analyzing layer at depth {layer.depth_mid}m")

        try:
            # 1. Soil classification
            soil_type = SoilClassification.classify(
                layer.n_value,
                layer.fines_content
            )

            # 2. Check if layer is saturated (below water table)
            if layer.depth_mid > layer.water_table_depth:
                is_saturated = True
            else:
                is_saturated = False
                logger.debug(f"Layer at {layer.depth_mid}m is above water table")

            # 3. CRR calculation (SPT-based)
            crr = CyclicResistanceRatio.calculate_crr_from_spt(
                layer.n_value,
                layer.sigma_v0_prime,
                layer.fines_content
            )

            # 4. CSR calculation (dynamic stress)
            # Calculate total stress if not already done
            sigma_v0 = layer.sigma_v0_prime + 9.81 * (
                0.0 if layer.depth_mid < layer.water_table_depth
                else (layer.depth_mid - layer.water_table_depth)
            )

            rd = CorrectionFactors.depth_reduction_factor(layer.depth_mid)

            csr = CyclicStressRatio.calculate_csr(
                site_conditions.peak_accel_g,
                sigma_v0,
                layer.sigma_v0_prime,
                rd
            )

            # 5. Magnitude scaling
            n_corrected = int(
                layer.n_value *
                CorrectionFactors.overburden_correction(layer.sigma_v0_prime) *
                CorrectionFactors.fines_correction(layer.fines_content) *
                1.2
            )

            msf = MagnitudeScaling.idriss_2004_msf(
                site_conditions.magnitude,
                n_corrected
            )

            # 6. Factor of Safety
            fs = FactorOfSafety.calculate_fs(crr, csr, msf, rd)

            # 7. LI contribution
            li = FactorOfSafety.calculate_li_contribution(fs)

            # 8. Risk assessment
            risk_level = RiskAssessment.classify_layer_risk(fs, li)

            # 9. Generate notes
            notes = []
            if not is_saturated:
                notes.append("Above water table - no liquefaction risk")
            if layer.fines_content > 35:
                notes.append("High fines content - reduced liquefaction potential")
            if layer.n_value == 0:
                notes.append("Very loose material (N=0)")
            if fs > 1.3:
                notes.append("Low liquefaction risk for this layer")
            elif fs < 0.75:
                notes.append("HIGH - Significant liquefaction potential")

            result = LiquefactionResult(
                depth_mid=layer.depth_mid,
                n_value=layer.n_value,
                n_corrected=n_corrected,
                crr=crr,
                csr=csr,
                msf=msf,
                rd=rd,
                fs=fs,
                li_contribution=li,
                soil_type=soil_type,
                risk_level=risk_level,
                notes="; ".join(notes) if notes else "Standard soil layer"
            )

            logger.info(
                f"Layer {layer.depth_mid}m: FS={fs:.3f}, LI={li:.3f}, "
                f"Risk={risk_level.value}"
            )

            return result

        except Exception as e:
            logger.error(f"Error analyzing layer at {layer.depth_mid}m: {e}")
            raise

    def analyze_site(
        self,
        layers: List[LayerData],
        site_conditions: SiteConditions,
        water_table_depth: Optional[float] = None
    ) -> SiteAnalysisResult:
        """
        Analyze complete site - all layers.

        Args:
            layers: List of LayerData objects (1m thick each)
            site_conditions: SiteConditions object
            water_table_depth: Override water table depth if provided

        Returns:
            SiteAnalysisResult with total LI and layer-by-layer breakdown
        """
        logger.info(
            f"Starting site analysis: {len(layers)} layers, "
            f"M={site_conditions.magnitude:.2f}, PGA={site_conditions.peak_accel_g:.3f}g"
        )

        if not layers:
            raise ValueError("At least one layer required")

        # Sort layers by depth
        layers_sorted = sorted(layers, key=lambda l: l.depth_mid)

        results = []
        total_li = 0.0
        liquefiable_depth = 0.0
        high_risk_count = 0
        warnings = []
        debug_log = {}

        for layer in layers_sorted:
            # Override water table if provided
            if water_table_depth is not None:
                layer.water_table_depth = water_table_depth

            # Analyze layer
            result = self.analyze_layer(layer, site_conditions)
            results.append(result)

            # Accumulate LI (only for saturated layers)
            if layer.depth_mid >= layer.water_table_depth:
                total_li += result.li_contribution

                # Track deepest liquefiable layer
                if result.fs < 1.0:
                    liquefiable_depth = layer.depth_mid

            # Count high-risk layers
            if result.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                high_risk_count += 1

            # Depth warning
            if layer.depth_mid > 20:
                warnings.append(
                    f"Depth {layer.depth_mid}m exceeds empirical range (0-20m) "
                    f"for rd factor"
                )

        # Overall risk classification
        overall_risk = RiskAssessment.classify_site_risk(total_li)

        # Validation warnings
        if site_conditions.magnitude < 6.0:
            warnings.append(
                f"Low magnitude ({site_conditions.magnitude:.2f}) - "
                f"liquefaction potential limited"
            )

        if len(layers_sorted) < 3:
            warnings.append("Limited number of layers - consider extended survey")

        # Store debug info
        debug_log = {
            "num_layers": len(layers_sorted),
            "avg_n": sum(l.n_value for l in layers_sorted) / len(layers_sorted),
            "avg_fines": sum(l.fines_content for l in layers_sorted) / len(layers_sorted),
            "csr_range": (
                min(r.csr for r in results),
                max(r.csr for r in results)
            ),
            "fs_range": (
                min(r.fs for r in results),
                max(r.fs for r in results)
            )
        }

        site_result = SiteAnalysisResult(
            site_id=self.site_id,
            magnitude=site_conditions.magnitude,
            peak_accel_g=site_conditions.peak_accel_g,
            total_li=total_li,
            risk_level=overall_risk,
            liquefiable_depth=liquefiable_depth,
            num_high_risk_layers=high_risk_count,
            layers=results,
            warnings=warnings,
            debug_log=debug_log
        )

        logger.info(
            f"Site analysis complete: LI={total_li:.3f}, "
            f"Risk={overall_risk.value}, "
            f"High-risk layers={high_risk_count}"
        )

        return site_result

    def export_csv(self, result: SiteAnalysisResult, filename: str) -> None:
        """
        Export layer-by-layer results to CSV.

        Args:
            result: SiteAnalysisResult object
            filename: Output CSV filename
        """
        import csv

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    "Depth (m)", "Soil Type", "N-value", "N-corrected",
                    "Fines %", "CRR", "CSR", "MSF", "rd", "FS", "LI",
                    "Risk Level", "Notes"
                ])

                # Data rows
                for layer in result.layers:
                    writer.writerow([
                        f"{layer.depth_mid:.2f}",
                        layer.soil_type.value,
                        layer.n_value,
                        layer.n_corrected,
                        f"{layer.fs:.4f}",
                        f"{layer.crr:.4f}",
                        f"{layer.csr:.4f}",
                        f"{layer.msf:.4f}",
                        f"{layer.rd:.4f}",
                        f"{layer.fs:.4f}",
                        f"{layer.li_contribution:.4f}",
                        layer.risk_level.value,
                        layer.notes
                    ])

            logger.info(f"Results exported to {filename}")

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise


# ============================================================================
# D7.3 INTEGRATION HOOK
# ============================================================================

class D73FeedbackInterface:
    """
    Interface for D7.3 Feedback & Verification Module.

    Provides structured output for independent verification and
    feedback automation.
    """

    @staticmethod
    def prepare_feedback_package(
        result: SiteAnalysisResult,
        analyst_notes: str = "",
        next_steps: List[str] = None
    ) -> Dict:
        """
        Prepare structured feedback package for D7.3.

        Args:
            result: SiteAnalysisResult from analyzer
            analyst_notes: Additional notes from geotechnical engineer
            next_steps: Recommended actions

        Returns:
            Dictionary suitable for JSON serialization to D7.3
        """
        if next_steps is None:
            next_steps = []

        # Prepare layer summaries
        layer_summaries = []
        for layer in result.layers:
            layer_summaries.append({
                "depth_m": layer.depth_mid,
                "soil_type": layer.soil_type.value,
                "spt_n": layer.n_value,
                "crr": round(layer.crr, 6),
                "csr": round(layer.csr, 6),
                "fs": round(layer.fs, 4),
                "li_contribution": round(layer.li_contribution, 4),
                "risk_level": layer.risk_level.value
            })

        package = {
            "d6_2_analysis": {
                "version": "1.0.0",
                "site_id": result.site_id,
                "earthquake_conditions": {
                    "magnitude_mw": result.magnitude,
                    "peak_accel_g": result.peak_accel_g
                },
                "results": {
                    "total_liquefaction_index": round(result.total_li, 4),
                    "overall_risk_level": result.risk_level.value,
                    "liquefiable_depth_m": result.liquefiable_depth,
                    "num_high_risk_layers": result.num_high_risk_layers,
                    "num_total_layers": len(result.layers)
                },
                "layer_details": layer_summaries,
                "warnings": result.warnings,
                "analyst_notes": analyst_notes,
                "recommended_next_steps": next_steps,
                "debug_statistics": result.debug_log
            }
        }

        return package

    @staticmethod
    def export_json(
        result: SiteAnalysisResult,
        filename: str,
        analyst_notes: str = "",
        next_steps: List[str] = None
    ) -> None:
        """
        Export D7.3-compatible JSON feedback package.

        Args:
            result: SiteAnalysisResult
            filename: Output JSON filename
            analyst_notes: Optional notes
            next_steps: Optional recommended actions
        """
        import json

        package = D73FeedbackInterface.prepare_feedback_package(
            result,
            analyst_notes=analyst_notes,
            next_steps=next_steps
        )

        try:
            with open(filename, 'w') as f:
                json.dump(package, f, indent=2)

            logger.info(f"D7.3 feedback package exported to {filename}")

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise


# ============================================================================
# UNIT TESTS
# ============================================================================

import unittest


class TestCorrectionFactors(unittest.TestCase):
    """Test SPT correction factor calculations."""

    def test_overburden_correction_100kpa(self):
        """CN should equal 1.0 at reference 100 kPa."""
        cn = CorrectionFactors.overburden_correction(100.0)
        self.assertAlmostEqual(cn, 1.0, places=3)

    def test_overburden_correction_low_stress(self):
        """CN should be > 1.0 for low effective stress."""
        cn = CorrectionFactors.overburden_correction(50.0)
        self.assertGreater(cn, 1.0)

    def test_overburden_correction_high_stress(self):
        """CN should be < 1.0 for high effective stress."""
        cn = CorrectionFactors.overburden_correction(200.0)
        self.assertLess(cn, 1.0)

    def test_overburden_correction_cap(self):
        """CN should be capped at 1.7."""
        cn = CorrectionFactors.overburden_correction(1.0)  # Very low stress
        self.assertLessEqual(cn, 1.7)

    def test_fines_correction_clean_sand(self):
        """CE should be 1.0 for clean sand (< 5% fines)."""
        ce = CorrectionFactors.fines_correction(2.0)
        self.assertEqual(ce, 1.0)

    def test_fines_correction_high_fines(self):
        """CE should be < 1.0 for high fines content."""
        ce_low = CorrectionFactors.fines_correction(10.0)
        ce_high = CorrectionFactors.fines_correction(50.0)
        self.assertGreater(ce_low, ce_high)

    def test_depth_reduction_surface(self):
        """rd should be 1.0 at surface (0m depth)."""
        rd = CorrectionFactors.depth_reduction_factor(0.0)
        self.assertEqual(rd, 1.0)

    def test_depth_reduction_decreasing(self):
        """rd should decrease with depth."""
        rd_0 = CorrectionFactors.depth_reduction_factor(0.0)
        rd_5 = CorrectionFactors.depth_reduction_factor(5.0)
        rd_10 = CorrectionFactors.depth_reduction_factor(10.0)

        self.assertGreater(rd_0, rd_5)
        self.assertGreater(rd_5, rd_10)

    def test_depth_reduction_bounds(self):
        """rd should always be 0.6-1.0."""
        for depth in [0, 5, 10, 15, 20, 25, 30]:
            rd = CorrectionFactors.depth_reduction_factor(depth)
            self.assertGreaterEqual(rd, 0.6)
            self.assertLessEqual(rd, 1.0)


class TestMagnitudeScaling(unittest.TestCase):
    """Test MSF calculations."""

    def test_msf_decreases_with_magnitude(self):
        """MSF should decrease for larger magnitudes."""
        msf_6 = MagnitudeScaling.idriss_2004_msf(6.0, 20)
        msf_8 = MagnitudeScaling.idriss_2004_msf(8.0, 20)

        self.assertGreater(msf_6, msf_8)

    def test_msf_bounds(self):
        """MSF should stay within 0.5-2.0."""
        for magnitude in [4.0, 5.0, 6.0, 7.5, 8.0, 9.0]:
            msf = MagnitudeScaling.idriss_2004_msf(magnitude, 20)
            self.assertGreaterEqual(msf, 0.5)
            self.assertLessEqual(msf, 2.0)


class TestCyclicStressRatio(unittest.TestCase):
    """Test CSR calculation."""

    def test_csr_proportional_to_pga(self):
        """CSR should increase with peak acceleration."""
        csr_1 = CyclicStressRatio.calculate_csr(
            0.1, 150, 100, 0.95
        )
        csr_2 = CyclicStressRatio.calculate_csr(
            0.2, 150, 100, 0.95
        )

        self.assertGreater(csr_2, csr_1)

    def test_csr_reasonable_range(self):
        """CSR should be 0.01-1.0 for typical conditions."""
        csr = CyclicStressRatio.calculate_csr(
            0.3, 150, 100, 0.95
        )
        self.assertGreater(csr, 0.01)
        self.assertLess(csr, 1.0)


class TestCyclicResistanceRatio(unittest.TestCase):
    """Test CRR from SPT."""

    def test_crr_increases_with_n(self):
        """CRR should increase with SPT N-value."""
        crr_10 = CyclicResistanceRatio.calculate_crr_from_spt(10, 100, 15)
        crr_30 = CyclicResistanceRatio.calculate_crr_from_spt(30, 100, 15)

        self.assertGreater(crr_30, crr_10)

    def test_crr_zero_n(self):
        """CRR should be low for N=0 (very loose)."""
        crr = CyclicResistanceRatio.calculate_crr_from_spt(0, 100, 15)
        self.assertLess(crr, 0.05)

    def test_crr_high_fines_reduction(self):
        """CRR should be lower for high fines content."""
        crr_low_fines = CyclicResistanceRatio.calculate_crr_from_spt(20, 100, 5)
        crr_high_fines = CyclicResistanceRatio.calculate_crr_from_spt(20, 100, 50)

        self.assertGreater(crr_low_fines, crr_high_fines)


class TestFactorOfSafety(unittest.TestCase):
    """Test FS and LI calculations."""

    def test_fs_safe_layer(self):
        """FS > 1 indicates safe layer."""
        fs = FactorOfSafety.calculate_fs(
            crr=0.30,
            csr=0.15,
            msf=1.0,
            rd=0.95
        )
        self.assertGreater(fs, 1.0)

    def test_fs_liquefiable_layer(self):
        """FS < 1 indicates liquefiable layer."""
        fs = FactorOfSafety.calculate_fs(
            crr=0.10,
            csr=0.20,
            msf=1.0,
            rd=0.95
        )
        self.assertLess(fs, 1.0)

    def test_li_contribution_safe(self):
        """LI = 0 for FS >= 1."""
        li = FactorOfSafety.calculate_li_contribution(1.2)
        self.assertEqual(li, 0.0)

    def test_li_contribution_liquefiable(self):
        """LI = 1 - FS for FS < 1."""
        li = FactorOfSafety.calculate_li_contribution(0.5)
        self.assertAlmostEqual(li, 0.5, places=3)

    def test_li_contribution_bounds(self):
        """LI should always be 0.0-1.0."""
        for fs in [0.2, 0.5, 1.0, 2.0]:
            li = FactorOfSafety.calculate_li_contribution(fs)
            self.assertGreaterEqual(li, 0.0)
            self.assertLessEqual(li, 1.0)


class TestRiskAssessment(unittest.TestCase):
    """Test risk classification."""

    def test_layer_risk_very_low(self):
        """FS >= 1.2 is Very Low risk."""
        risk = RiskAssessment.classify_layer_risk(fs=1.3, li=0.0)
        self.assertEqual(risk, RiskLevel.VERY_LOW)

    def test_layer_risk_high(self):
        """0.5 <= FS < 0.75 is High risk."""
        risk = RiskAssessment.classify_layer_risk(fs=0.6, li=0.4)
        self.assertEqual(risk, RiskLevel.HIGH)

    def test_site_risk_very_low(self):
        """LI < 5 is Very Low site risk."""
        risk = RiskAssessment.classify_site_risk(3.0)
        self.assertEqual(risk, RiskLevel.VERY_LOW)

    def test_site_risk_moderate(self):
        """15 <= LI < 30 is Moderate site risk."""
        risk = RiskAssessment.classify_site_risk(20.0)
        self.assertEqual(risk, RiskLevel.MODERATE)

    def test_site_risk_very_high(self):
        """LI >= 50 is Very High site risk."""
        risk = RiskAssessment.classify_site_risk(60.0)
        self.assertEqual(risk, RiskLevel.VERY_HIGH)


class TestLayerDataValidation(unittest.TestCase):
    """Test LayerData validation."""

    def test_valid_layer(self):
        """Valid layer should initialize without error."""
        layer = LayerData(
            depth_mid=5.0,
            n_value=15,
            fines_content=20.0,
            water_table_depth=2.0,
            unit_weight=19.0,
            sigma_v0_prime=80.0
        )
        self.assertEqual(layer.depth_mid, 5.0)

    def test_invalid_depth(self):
        """Negative depth should raise error."""
        with self.assertRaises(ValueError):
            LayerData(
                depth_mid=-1.0,
                n_value=15,
                fines_content=20.0,
                water_table_depth=2.0,
                unit_weight=19.0,
                sigma_v0_prime=80.0
            )

    def test_invalid_fines(self):
        """Fines > 100% should raise error."""
        with self.assertRaises(ValueError):
            LayerData(
                depth_mid=5.0,
                n_value=15,
                fines_content=150.0,
                water_table_depth=2.0,
                unit_weight=19.0,
                sigma_v0_prime=80.0
            )


class TestIntegrationJerico(unittest.TestCase):
    """Integration tests with Jericó test cases."""

    def test_jerico_case_1_loose_sand_shallow(self):
        """
        Jericó Test Case 1: Loose sand at shallow depth.
        Expected: Individual layer has very high risk; site LI low due to single 1m layer.
        """
        analyzer = LiquefactionAnalyzer(site_id="JERICO-001")

        layer = LayerData(
            depth_mid=2.0,
            n_value=8,
            fines_content=10.0,
            water_table_depth=1.5,
            unit_weight=19.0,
            sigma_v0_prime=30.0
        )

        site_conditions = SiteConditions(
            magnitude=7.5,
            peak_accel_g=0.40,
            depth_water_table=1.5,
            vs30=150.0
        )

        result = analyzer.analyze_site([layer], site_conditions)

        # Individual layer should be very high risk
        self.assertEqual(result.layers[0].risk_level, RiskLevel.VERY_HIGH)
        # Site LI will be < 5 due to single layer, so site risk is VERY_LOW
        self.assertLess(result.total_li, 5.0)
        self.assertGreater(result.layers[0].li_contribution, 0.5)

    def test_jerico_case_2_dense_sand_deep(self):
        """
        Jericó Test Case 2: Dense sand at depth.
        Expected: Low liquefaction risk.
        """
        analyzer = LiquefactionAnalyzer(site_id="JERICO-002")

        layer = LayerData(
            depth_mid=12.0,
            n_value=35,
            fines_content=5.0,
            water_table_depth=2.0,
            unit_weight=20.0,
            sigma_v0_prime=160.0
        )

        site_conditions = SiteConditions(
            magnitude=7.0,
            peak_accel_g=0.30,
            depth_water_table=2.0,
            vs30=200.0
        )

        result = analyzer.analyze_site([layer], site_conditions)

        # Dense sand should have low risk
        self.assertIn(result.risk_level, [RiskLevel.VERY_LOW, RiskLevel.LOW])

    def test_jerico_case_3_silty_sand_moderate(self):
        """
        Jericó Test Case 3: Silty sand, moderate conditions.
        Expected: Individual layer has high risk; site LI low due to single layer.
        """
        analyzer = LiquefactionAnalyzer(site_id="JERICO-003")

        layer = LayerData(
            depth_mid=6.0,
            n_value=20,
            fines_content=25.0,
            water_table_depth=3.0,
            unit_weight=19.5,
            sigma_v0_prime=100.0
        )

        site_conditions = SiteConditions(
            magnitude=6.8,
            peak_accel_g=0.35,
            depth_water_table=3.0,
            vs30=180.0
        )

        result = analyzer.analyze_site([layer], site_conditions)

        # Individual layer should have elevated risk (FS < 1)
        self.assertLess(result.layers[0].fs, 1.2)
        # Site LI will be < 5, so site risk is VERY_LOW despite layer risk
        self.assertLess(result.total_li, 5.0)

    def test_jerico_case_4_multiple_layers(self):
        """
        Jericó Test Case 4: Stratified profile with 5 layers.
        Expected: LI calculation across all layers.
        """
        analyzer = LiquefactionAnalyzer(site_id="JERICO-004")

        layers = [
            LayerData(
                depth_mid=1.5,
                n_value=5,
                fines_content=15.0,
                water_table_depth=0.5,
                unit_weight=18.5,
                sigma_v0_prime=20.0
            ),
            LayerData(
                depth_mid=3.5,
                n_value=10,
                fines_content=20.0,
                water_table_depth=0.5,
                unit_weight=19.0,
                sigma_v0_prime=60.0
            ),
            LayerData(
                depth_mid=5.5,
                n_value=18,
                fines_content=18.0,
                water_table_depth=0.5,
                unit_weight=19.5,
                sigma_v0_prime=100.0
            ),
            LayerData(
                depth_mid=7.5,
                n_value=25,
                fines_content=12.0,
                water_table_depth=0.5,
                unit_weight=20.0,
                sigma_v0_prime=140.0
            ),
            LayerData(
                depth_mid=9.5,
                n_value=35,
                fines_content=8.0,
                water_table_depth=0.5,
                unit_weight=20.5,
                sigma_v0_prime=180.0
            )
        ]

        site_conditions = SiteConditions(
            magnitude=7.5,
            peak_accel_g=0.38,
            depth_water_table=0.5,
            vs30=170.0
        )

        result = analyzer.analyze_site(layers, site_conditions)

        # Should have positive LI
        self.assertGreater(result.total_li, 0.0)
        # Should have 5 layer results
        self.assertEqual(len(result.layers), 5)

    def test_jerico_case_5_high_magnitude(self):
        """
        Jericó Test Case 5: High magnitude earthquake (8.5).
        Expected: Larger MSF for lower magnitude → lower FS for lower magnitude.
        """
        analyzer = LiquefactionAnalyzer(site_id="JERICO-005")

        layer = LayerData(
            depth_mid=4.0,
            n_value=15,
            fines_content=22.0,
            water_table_depth=2.0,
            unit_weight=19.2,
            sigma_v0_prime=70.0
        )

        site_conditions_low_mag = SiteConditions(
            magnitude=6.5,
            peak_accel_g=0.35,
            depth_water_table=2.0,
            vs30=175.0
        )

        site_conditions_high_mag = SiteConditions(
            magnitude=8.5,
            peak_accel_g=0.35,  # Same PGA
            depth_water_table=2.0,
            vs30=175.0
        )

        result_low = analyzer.analyze_site([layer], site_conditions_low_mag)
        result_high = analyzer.analyze_site([layer], site_conditions_high_mag)

        # Lower magnitude (6.5) has higher MSF → lower FS → higher LI than M8.5
        # This is because MSF = (7.5/M)^2.56, so M=6.5 has larger MSF
        self.assertGreater(result_low.total_li, result_high.total_li)

    def test_jerico_case_6_above_water_table(self):
        """
        Jericó Test Case 6: Layer above water table.
        Expected: No liquefaction (LI = 0).
        """
        analyzer = LiquefactionAnalyzer(site_id="JERICO-006")

        layer = LayerData(
            depth_mid=1.0,
            n_value=10,
            fines_content=15.0,
            water_table_depth=3.0,  # Above water table
            unit_weight=18.5,
            sigma_v0_prime=15.0
        )

        site_conditions = SiteConditions(
            magnitude=7.5,
            peak_accel_g=0.40,
            depth_water_table=3.0,
            vs30=160.0
        )

        result = analyzer.analyze_site([layer], site_conditions)

        # Above water table should have no liquefaction
        self.assertEqual(result.total_li, 0.0)
        self.assertEqual(result.risk_level, RiskLevel.VERY_LOW)


class TestD73Integration(unittest.TestCase):
    """Test D7.3 feedback interface."""

    def test_feedback_package_creation(self):
        """Feedback package should contain required fields."""
        analyzer = LiquefactionAnalyzer(site_id="TEST-D73")

        layers = [
            LayerData(
                depth_mid=3.0,
                n_value=12,
                fines_content=18.0,
                water_table_depth=2.0,
                unit_weight=19.0,
                sigma_v0_prime=50.0
            )
        ]

        site_conditions = SiteConditions(
            magnitude=7.5,
            peak_accel_g=0.35,
            depth_water_table=2.0,
            vs30=170.0
        )

        result = analyzer.analyze_site(layers, site_conditions)

        package = D73FeedbackInterface.prepare_feedback_package(
            result,
            analyst_notes="Test analysis",
            next_steps=["Field verification", "Extended boring program"]
        )

        # Check required fields
        self.assertIn("d6_2_analysis", package)
        self.assertIn("version", package["d6_2_analysis"])
        self.assertIn("site_id", package["d6_2_analysis"])
        self.assertIn("results", package["d6_2_analysis"])
        self.assertIn("layer_details", package["d6_2_analysis"])

        # Verify data integrity
        results = package["d6_2_analysis"]["results"]
        self.assertAlmostEqual(
            results["total_liquefaction_index"],
            result.total_li,
            places=4
        )


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def demo_jerico_analysis():
    """Demonstration: Run all 6 Jericó test cases."""

    print("\n" + "="*70)
    print("D6.2 LIQUEFACTION ANALYSIS - JERICÓ TEST CASES")
    print("="*70 + "\n")

    # Test Case 1: Loose sand, shallow
    print("\n[TEST CASE 1] Loose Sand at Shallow Depth")
    print("-" * 70)
    analyzer_1 = LiquefactionAnalyzer(site_id="JERICO-001", verbose=False)

    layer_1 = LayerData(
        depth_mid=2.0,
        n_value=8,
        fines_content=10.0,
        water_table_depth=1.5,
        unit_weight=19.0,
        sigma_v0_prime=30.0
    )

    site_1 = SiteConditions(
        magnitude=7.5,
        peak_accel_g=0.40,
        depth_water_table=1.5,
        vs30=150.0
    )

    result_1 = analyzer_1.analyze_site([layer_1], site_1)
    print(result_1.summary())

    # Test Case 2: Dense sand, deep
    print("\n[TEST CASE 2] Dense Sand at Depth")
    print("-" * 70)
    analyzer_2 = LiquefactionAnalyzer(site_id="JERICO-002", verbose=False)

    layer_2 = LayerData(
        depth_mid=12.0,
        n_value=35,
        fines_content=5.0,
        water_table_depth=2.0,
        unit_weight=20.0,
        sigma_v0_prime=160.0
    )

    site_2 = SiteConditions(
        magnitude=7.0,
        peak_accel_g=0.30,
        depth_water_table=2.0,
        vs30=200.0
    )

    result_2 = analyzer_2.analyze_site([layer_2], site_2)
    print(result_2.summary())

    # Test Case 3: Silty sand, moderate
    print("\n[TEST CASE 3] Silty Sand, Moderate Conditions")
    print("-" * 70)
    analyzer_3 = LiquefactionAnalyzer(site_id="JERICO-003", verbose=False)

    layer_3 = LayerData(
        depth_mid=6.0,
        n_value=20,
        fines_content=25.0,
        water_table_depth=3.0,
        unit_weight=19.5,
        sigma_v0_prime=100.0
    )

    site_3 = SiteConditions(
        magnitude=6.8,
        peak_accel_g=0.35,
        depth_water_table=3.0,
        vs30=180.0
    )

    result_3 = analyzer_3.analyze_site([layer_3], site_3)
    print(result_3.summary())

    # Test Case 4: Multi-layer profile
    print("\n[TEST CASE 4] Stratified 5-Layer Profile")
    print("-" * 70)
    analyzer_4 = LiquefactionAnalyzer(site_id="JERICO-004", verbose=False)

    layers_4 = [
        LayerData(depth_mid=1.5, n_value=5, fines_content=15.0,
                  water_table_depth=0.5, unit_weight=18.5, sigma_v0_prime=20.0),
        LayerData(depth_mid=3.5, n_value=10, fines_content=20.0,
                  water_table_depth=0.5, unit_weight=19.0, sigma_v0_prime=60.0),
        LayerData(depth_mid=5.5, n_value=18, fines_content=18.0,
                  water_table_depth=0.5, unit_weight=19.5, sigma_v0_prime=100.0),
        LayerData(depth_mid=7.5, n_value=25, fines_content=12.0,
                  water_table_depth=0.5, unit_weight=20.0, sigma_v0_prime=140.0),
        LayerData(depth_mid=9.5, n_value=35, fines_content=8.0,
                  water_table_depth=0.5, unit_weight=20.5, sigma_v0_prime=180.0)
    ]

    site_4 = SiteConditions(
        magnitude=7.5,
        peak_accel_g=0.38,
        depth_water_table=0.5,
        vs30=170.0
    )

    result_4 = analyzer_4.analyze_site(layers_4, site_4)
    print(result_4.summary())

    # Test Case 5: High magnitude earthquake
    print("\n[TEST CASE 5] High Magnitude Earthquake (M8.5)")
    print("-" * 70)
    analyzer_5 = LiquefactionAnalyzer(site_id="JERICO-005", verbose=False)

    layer_5 = LayerData(
        depth_mid=4.0,
        n_value=15,
        fines_content=22.0,
        water_table_depth=2.0,
        unit_weight=19.2,
        sigma_v0_prime=70.0
    )

    site_5 = SiteConditions(
        magnitude=8.5,
        peak_accel_g=0.35,
        depth_water_table=2.0,
        vs30=175.0
    )

    result_5 = analyzer_5.analyze_site([layer_5], site_5)
    print(result_5.summary())

    # Test Case 6: Above water table
    print("\n[TEST CASE 6] Layer Above Water Table")
    print("-" * 70)
    analyzer_6 = LiquefactionAnalyzer(site_id="JERICO-006", verbose=False)

    layer_6 = LayerData(
        depth_mid=1.0,
        n_value=10,
        fines_content=15.0,
        water_table_depth=3.0,
        unit_weight=18.5,
        sigma_v0_prime=15.0
    )

    site_6 = SiteConditions(
        magnitude=7.5,
        peak_accel_g=0.40,
        depth_water_table=3.0,
        vs30=160.0
    )

    result_6 = analyzer_6.analyze_site([layer_6], site_6)
    print(result_6.summary())

    print("\n" + "="*70)
    print("ALL TEST CASES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys

    # Run unit tests if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running unit tests...\n")
        unittest.main(argv=[sys.argv[0]], exit=False, verbosity=2)
    else:
        # Run demonstration
        demo_jerico_analysis()
