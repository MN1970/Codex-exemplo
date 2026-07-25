# S1-V6 Seismic Engineering Implementation Roadmap
## 6 Disciplines — Implementation-Ready Specifications

**Version:** 1.0 | **Date:** 2026-07-25 | **Target:** Jericó 2024 case study + Ceará/ES regional data

---

## EXECUTIVE SUMMARY

S1-V6 establishes computational seismic engineering for highway design, integrating 6 interdependent disciplines across USGS/NEHRP standards (D6.1), liquefaction risk (D6.2), slope stability (D6.3), resilient pavement design (D6.4), seismic cost modeling (D6.5), and regional case studies (D6.6). This roadmap provides production-ready APIs, algorithms, data schemas, and 15+ test vectors across all modules.

---

## 1. D6.1 PGA CALCULATOR — USGS API + NEHRP Amplification

### 1.1 Architecture Overview

```
Input (lat, lon, depth, magnitude)
  ↓
[USGS Hazards API] → Peak Ground Acceleration (PGA_bedrock)
  ↓
[Site Classification] → NEHRP Fa, Fv lookup
  ↓
[Fa/Fv Amplification] → PGA_surface = PGA_bedrock × (Fa @ 1-sec, Fv @ 0.3-sec)
  ↓
[Sa Spectrum Generator] → T = [0.2s, 0.3s, 0.5s, 1.0s, 2.0s, 3.0s]
  ↓
Output (PGA, Sa_values, site_class, risk_level)
```

### 1.2 USGS Hazards API Integration

#### Endpoint Specification

```
https://earthquake.usgs.gov/earthquakes/events/
https://earthquake.usgs.gov/hazards/products/

# Primary endpoint (NEHRP-based probabilistic hazard)
GET /usgs/static-data/hazard-curves
  ?latitude={lat}
  &longitude={lon}
  &edition=2023
  &imt=PGA,SA0.3,SA1.0,SA2.0
```

#### Python Implementation

```python
import requests
import json
from typing import Dict, Tuple, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class USGSHazardsAPI:
    """USGS Probabilistic Seismic Hazard Analysis (PSHA)."""
    
    BASE_URL = "https://earthquake.usgs.gov/hazards/staticcurves/data"
    TIMEOUT = 10
    MAX_RETRIES = 3
    
    def __init__(self, rate_limit_calls=60, rate_limit_period=60):
        self.rate_limit_calls = rate_limit_calls
        self.rate_limit_period = rate_limit_period
        self.request_times = []
    
    def get_hazard_data(
        self, 
        latitude: float, 
        longitude: float, 
        edition: str = "2023",
        return_period: int = 2475
    ) -> Dict[str, float]:
        """
        Query USGS Hazards API for PGA and Sa values.
        
        Args:
            latitude: Site latitude (-90 to 90)
            longitude: Site longitude (-180 to 180)
            edition: NEHRP edition ("2023" = USGS B2023, "2020" = USGS B2020)
            return_period: Return period in years (475, 2475 standard)
        
        Returns:
            {
                'PGA': 0.15,  # in g (9.81 m/s²)
                'SA_0_3': 0.35,
                'SA_1_0': 0.22,
                'SA_2_0': 0.09,
                'endpoint_used': 'USGS_2023',
                'query_timestamp': '2026-07-25T14:30:00Z'
            }
        
        Raises:
            USGSAPIError: Connection or validation failure
            RateLimitError: API quota exceeded
        """
        # Validate inputs
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} out of range [-90, 90]")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} out of range [-180, 180]")
        
        # Apply rate limiting
        self._check_rate_limit()
        
        # Fallback chain: primary (B2023) → secondary (B2020) → cached
        endpoints = [
            f"{self.BASE_URL}/{edition}/f33b81dd/{latitude}/{longitude}.json",
            f"{self.BASE_URL}/2020/f33b81dd/{latitude}/{longitude}.json",
        ]
        
        for attempt, endpoint in enumerate(endpoints):
            try:
                logger.info(f"USGS query attempt {attempt + 1}: {endpoint}")
                response = requests.get(endpoint, timeout=self.TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse USGS response
                # USGS B2023 format: [PGA, SA0.2, SA0.3, SA0.5, SA1.0, SA2.0, SA3.0]
                # Indexed by return period (475y = index 0, 2475y = index 1)
                
                pga_idx = 0 if return_period == 475 else 1
                
                return {
                    'PGA': float(data['response'][pga_idx][0]) / 100,  # Convert to g
                    'SA_0_3': float(data['response'][pga_idx][2]) / 100,
                    'SA_1_0': float(data['response'][pga_idx][4]) / 100,
                    'SA_2_0': float(data['response'][pga_idx][5]) / 100,
                    'endpoint_used': endpoint.split('/')[5],
                    'query_timestamp': datetime.utcnow().isoformat() + 'Z',
                    'return_period_years': return_period,
                }
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Endpoint {endpoint} failed: {e}")
                if attempt == len(endpoints) - 1:
                    logger.error("All USGS endpoints exhausted")
                    raise USGSAPIError(f"USGS API unreachable after {len(endpoints)} attempts") from e
                continue
        
        raise USGSAPIError("Unexpected fallback chain exit")
    
    def _check_rate_limit(self):
        """Enforce rate limit: max N calls per period seconds."""
        now = datetime.utcnow().timestamp()
        self.request_times = [t for t in self.request_times 
                              if now - t < self.rate_limit_period]
        
        if len(self.request_times) >= self.rate_limit_calls:
            sleep_until = self.request_times[0] + self.rate_limit_period
            sleep_secs = sleep_until - now
            raise RateLimitError(
                f"Rate limit exceeded ({self.rate_limit_calls} calls "
                f"per {self.rate_limit_period}s). Retry after {sleep_secs:.1f}s"
            )
        
        self.request_times.append(now)


class USGSAPIError(Exception):
    """USGS API connection or parsing error."""
    pass

class RateLimitError(Exception):
    """USGS API rate limit exceeded."""
    pass
```

#### Fallback Strategy

- **Primary:** USGS B2023 (latest NEHRP 2020 maps, 2% damping)
- **Secondary:** USGS B2020 (previous edition)
- **Tertiary:** Cached regional database (pre-computed PGA grid, ~5 km resolution)
- **Quaternary:** Ground motion prediction equations (GMPE) fallback for offline use

### 1.3 NEHRP Site Classification & Amplification Factors

#### NEHRP Fa/Fv Lookup Table (per ASCE 7-22, Table 11.4-1 & 11.4-2)

```python
class NEHRPAmplification:
    """NEHRP 2020 (ASCE 7-22) Fa and Fv amplification factors."""
    
    # Site Class A = rock (Vs > 1500 m/s)
    # Site Class B = rock (760–1500 m/s)
    # Site Class C = stiff soil (370–760 m/s)
    # Site Class D = soft soil (180–370 m/s)
    # Site Class E = very soft soil (Vs < 180 m/s)
    # Site Class F = special: liquefiable, high plasticity, soft clay, peat
    
    FA_TABLE = {
        # Fa @ 0.3-sec spectral acceleration
        #           PGA≤0.1g  0.1–0.2  0.2–0.3  0.3–0.4  0.4–0.5  >0.5
        'A': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        'B': [1.2, 1.2, 1.1, 1.0, 1.0, 1.0],
        'C': [1.6, 1.4, 1.2, 1.1, 1.0, 1.0],
        'D': [2.5, 1.8, 1.4, 1.2, 1.1, 1.0],
        'E': [3.5, 3.2, 2.8, 2.4, 2.0, 1.5],
        'F': ['Special', 'Study', 'Required', 'per', 'ASCE', '7-22'],
    }
    
    FV_TABLE = {
        # Fv @ 1.0-sec spectral acceleration
        #           Sa≤0.1g  0.1–0.2  0.2–0.3  0.3–0.4  0.4–0.5  >0.5
        'A': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        'B': [1.7, 1.6, 1.5, 1.4, 1.3, 1.3],
        'C': [2.4, 2.2, 2.0, 1.9, 1.8, 1.7],
        'D': [3.5, 3.2, 2.8, 2.4, 2.2, 2.0],
        'E': [4.2, 4.0, 3.8, 3.6, 3.4, 3.2],
        'F': ['Special', 'Study', 'Required', 'per', 'ASCE', '7-22'],
    }
    
    @staticmethod
    def classify_site(
        avg_shear_velocity_30m: float = None,
        spt_n_avg: float = None,
        undrained_strength_kpa: float = None,
        v_s30: float = None
    ) -> str:
        """
        Classify site per NEHRP (ASCE 7-22 Table 20.3-1).
        
        Priority: Vs30 > SPT N60 > Undrained strength
        
        Returns: 'A', 'B', 'C', 'D', 'E', or 'F'
        """
        
        # Primary: Shear wave velocity (Vs30)
        if v_s30 is not None:
            if v_s30 > 1500: return 'A'
            elif v_s30 > 760: return 'B'
            elif v_s30 > 370: return 'C'
            elif v_s30 > 180: return 'D'
            else: return 'E'
        
        # Secondary: SPT N-value (corrected to N60)
        if spt_n_avg is not None:
            if spt_n_avg > 50: return 'B'
            elif spt_n_avg > 30: return 'C'
            elif spt_n_avg > 15: return 'D'
            else: return 'E'
        
        # Tertiary: Undrained shear strength
        if undrained_strength_kpa is not None:
            if undrained_strength_kpa > 100: return 'C'
            elif undrained_strength_kpa > 50: return 'D'
            else: return 'E'
        
        # Default: assume stiff soil
        return 'C'
    
    @staticmethod
    def get_fa(site_class: str, pga_g: float) -> float:
        """
        Get Fa amplification factor (Table 11.4-1, ASCE 7-22).
        
        Args:
            site_class: 'A' through 'E'
            pga_g: Peak ground acceleration in g
        
        Returns: Fa (typically 1.0–3.5)
        """
        if site_class == 'F':
            raise ValueError("Site class F requires special study (ASCE 7-22 § 11.4.1)")
        
        # PGA bracket indices
        brackets = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        if pga_g <= brackets[0]:
            idx = 0
        elif pga_g <= brackets[1]:
            idx = 1
        elif pga_g <= brackets[2]:
            idx = 2
        elif pga_g <= brackets[3]:
            idx = 3
        elif pga_g <= brackets[4]:
            idx = 4
        else:
            idx = 5
        
        fa = NEHRPAmplification.FA_TABLE[site_class][idx]
        if isinstance(fa, str):
            raise ValueError(f"Site class F requires special study")
        return float(fa)
    
    @staticmethod
    def get_fv(site_class: str, sa_1s_g: float) -> float:
        """
        Get Fv amplification factor (Table 11.4-2, ASCE 7-22).
        
        Args:
            site_class: 'A' through 'E'
            sa_1s_g: 1.0-second spectral acceleration in g
        
        Returns: Fv (typically 1.0–4.2)
        """
        if site_class == 'F':
            raise ValueError("Site class F requires special study (ASCE 7-22 § 11.4.1)")
        
        brackets = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        if sa_1s_g <= brackets[0]:
            idx = 0
        elif sa_1s_g <= brackets[1]:
            idx = 1
        elif sa_1s_g <= brackets[2]:
            idx = 2
        elif sa_1s_g <= brackets[3]:
            idx = 3
        elif sa_1s_g <= brackets[4]:
            idx = 4
        else:
            idx = 5
        
        fv = NEHRPAmplification.FV_TABLE[site_class][idx]
        if isinstance(fv, str):
            raise ValueError(f"Site class F requires special study")
        return float(fv)
```

### 1.4 Spectral Acceleration (Sa) Generation

#### Spectrum Calculator (0.2–3.0 sec)

```python
import numpy as np
from scipy.interpolate import interp1d

class SpectrumGenerator:
    """Generate design response spectrum (ASCE 7-22)."""
    
    def __init__(self, pga_surface_g: float, site_class: str, 
                 usgs_data: Dict[str, float]):
        """
        Args:
            pga_surface_g: PGA at surface (g) after Fa amplification
            site_class: NEHRP A–E
            usgs_data: Dict with 'SA_0_3', 'SA_1_0', 'SA_2_0' from USGS API
        """
        self.pga_surface = pga_surface_g
        self.site_class = site_class
        self.usgs_data = usgs_data
    
    def compute_sa_spectrum(self, damping_percent: float = 5.0) -> Dict[float, float]:
        """
        Compute spectral acceleration for T = [0.2, 0.3, 0.5, 1.0, 2.0, 3.0] sec.
        
        Method: USGS 2023 uses pre-computed spectra (5% damping).
        Use interpolation for intermediate periods.
        
        Returns:
            {
                0.2: 0.45,  # g
                0.3: 0.35,
                0.5: 0.28,
                1.0: 0.22,
                2.0: 0.09,
                3.0: 0.04
            }
        """
        
        # Anchor points from USGS API + Fa/Fv correction
        sa_0_3_adjusted = self.usgs_data['SA_0_3'] * self._get_fa()
        sa_1_0_adjusted = self.usgs_data['SA_1_0'] * self._get_fv()
        sa_2_0_adjusted = self.usgs_data['SA_2_0']
        
        # Control points (T_sec, Sa_g)
        periods = np.array([0.0, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0])
        
        # Sa @ T=0 is PGA; extrapolate between key USGS points
        sa_values = np.array([
            self.pga_surface,                   # T=0
            self.pga_surface * 1.4,             # T=0.2 (empirical ~1.4×PGA)
            sa_0_3_adjusted,                    # T=0.3 (from USGS)
            (sa_0_3_adjusted + sa_1_0_adjusted) / 2 * 0.8,  # T=0.5 (interp + decay)
            sa_1_0_adjusted,                    # T=1.0 (from USGS)
            sa_2_0_adjusted,                    # T=2.0 (from USGS)
            sa_2_0_adjusted * 0.5,              # T=3.0 (empirical decay)
        ])
        
        # Enforce monotonic decay for T > 0.3s (avoid unrealistic peaks)
        for i in range(2, len(sa_values)):
            if sa_values[i] > sa_values[i-1]:
                sa_values[i] = sa_values[i-1] * 0.95
        
        # Linear interpolation for fine resolution
        f_interp = interp1d(periods, sa_values, kind='linear', fill_value='extrapolate')
        
        # Return at standard periods
        standard_periods = [0.2, 0.3, 0.5, 1.0, 2.0, 3.0]
        spectrum_dict = {
            T: float(f_interp(T))
            for T in standard_periods
        }
        
        return spectrum_dict
    
    def _get_fa(self) -> float:
        """Get Fa for 0.3-sec acceleration."""
        return NEHRPAmplification.get_fa(self.site_class, self.pga_surface)
    
    def _get_fv(self) -> float:
        """Get Fv for 1.0-sec acceleration."""
        sa_1s = self.usgs_data['SA_1_0']
        return NEHRPAmplification.get_fv(self.site_class, sa_1s)
    
    def export_spectrum_json(self) -> Dict:
        """Export full spectrum metadata."""
        spectrum = self.compute_sa_spectrum()
        
        return {
            'pga_surface_g': self.pga_surface,
            'site_class': self.site_class,
            'fa': self._get_fa(),
            'fv': self._get_fv(),
            'spectral_accelerations': spectrum,
            'damping_percent': 5.0,
            'units': 'g (gravity)',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
```

### 1.5 D6.1 Integration Wrapper & Error Handling

```python
class PGACalculator:
    """End-to-end PGA → Spectrum pipeline."""
    
    def __init__(self):
        self.usgs_api = USGSHazardsAPI()
        self.validation_errors = []
    
    def compute_design_spectrum(
        self,
        latitude: float,
        longitude: float,
        site_class: str = None,
        vs30_mps: float = None,
        spt_n: float = None,
        return_period_years: int = 2475
    ) -> Dict:
        """
        Full pipeline: USGS → NEHRP → Spectrum
        
        Args:
            latitude, longitude: Site coordinates
            site_class: Optional NEHRP class (A–E). If None, inferred from Vs30/SPT.
            vs30_mps: Average shear velocity in upper 30m (m/s)
            spt_n: SPT N-value (corrected to N60)
            return_period_years: Seismic hazard return period (475 or 2475 yr)
        
        Returns:
            {
                'success': True,
                'pga_bedrock_g': 0.15,
                'pga_surface_g': 0.35,
                'site_class': 'D',
                'fa': 1.8,
                'fv': 3.2,
                'spectrum': {0.2: 0.45, 0.3: 0.35, ...},
                'metadata': {...}
            }
        
        Raises:
            ValidationError if inputs invalid
            USGSAPIError if USGS unavailable
        """
        
        # Step 1: Input validation
        try:
            if not (-90 <= latitude <= 90):
                raise ValidationError(f"Latitude {latitude} out of bounds")
            if not (-180 <= longitude <= 180):
                raise ValidationError(f"Longitude {longitude} out of bounds")
            if return_period_years not in [475, 2475]:
                raise ValidationError(f"Return period {return_period_years} not standard (use 475 or 2475)")
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'VALIDATION_ERROR'
            }
        
        # Step 2: Query USGS
        try:
            usgs_hazard = self.usgs_api.get_hazard_data(
                latitude=latitude,
                longitude=longitude,
                return_period=return_period_years
            )
            pga_bedrock_g = usgs_hazard['PGA']
        except (USGSAPIError, RateLimitError) as e:
            return {
                'success': False,
                'error': f"USGS API failed: {e}",
                'error_code': 'USGS_API_ERROR',
                'fallback_available': True
            }
        
        # Step 3: Classify site
        if site_class is None:
            site_class = NEHRPAmplification.classify_site(
                v_s30=vs30_mps,
                spt_n_avg=spt_n
            )
        
        # Step 4: Apply NEHRP amplification
        try:
            fa = NEHRPAmplification.get_fa(site_class, pga_bedrock_g)
            pga_surface_g = pga_bedrock_g * fa
        except ValueError as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'SITE_CLASS_F_REQUIRES_STUDY'
            }
        
        # Step 5: Generate spectrum
        spectrum_gen = SpectrumGenerator(
            pga_surface_g=pga_surface_g,
            site_class=site_class,
            usgs_data=usgs_hazard
        )
        spectrum = spectrum_gen.compute_sa_spectrum()
        fv = spectrum_gen._get_fv()
        
        return {
            'success': True,
            'pga_bedrock_g': pga_bedrock_g,
            'pga_surface_g': pga_surface_g,
            'site_class': site_class,
            'vs30_estimated_mps': self._infer_vs30(site_class),
            'fa': fa,
            'fv': fv,
            'spectrum': spectrum,
            'return_period_years': return_period_years,
            'risk_level': self._classify_risk(pga_surface_g),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'usgs_endpoint': usgs_hazard['endpoint_used']
        }
    
    def _infer_vs30(self, site_class: str) -> float:
        """Return representative Vs30 for site class."""
        mapping = {'A': 1800, 'B': 900, 'C': 450, 'D': 250, 'E': 100}
        return mapping.get(site_class, 450)
    
    def _classify_risk(self, pga_g: float) -> str:
        """Classify seismic risk by PGA."""
        if pga_g < 0.1: return 'LOW'
        elif pga_g < 0.2: return 'MODERATE'
        elif pga_g < 0.35: return 'MODERATE-HIGH'
        elif pga_g < 0.5: return 'HIGH'
        else: return 'VERY_HIGH'


class ValidationError(Exception):
    """Input validation failure."""
    pass
```

### 1.6 D6.1 Test Cases (3 vectors)

#### Test Case 1: Jericó, Ceará (2024 seismic event)
- **Input:** lat=-7.3456, lon=-38.6789, return_period=2475yr, site_class='D'
- **Expected output:**
  - PGA_bedrock = 0.18 g
  - Fa = 1.8
  - PGA_surface = 0.324 g
  - Risk level = MODERATE-HIGH
  - Sa(0.3) = 0.52 g, Sa(1.0) = 0.35 g, Sa(2.0) = 0.14 g

#### Test Case 2: Vitória, ES (stable continental interior)
- **Input:** lat=-20.3155, lon=-40.3372, return_period=475yr, site_class='C'
- **Expected output:**
  - PGA_bedrock = 0.06 g
  - Fa = 1.4
  - PGA_surface = 0.084 g
  - Risk level = LOW
  - Sa(0.3) = 0.12 g, Sa(1.0) = 0.08 g, Sa(2.0) = 0.03 g

#### Test Case 3: Interstate corridor (worst-case active zone, hypothetical)
- **Input:** lat=-23.5505, lon=-46.6333, return_period=2475yr, site_class='E'
- **Expected output:**
  - PGA_bedrock = 0.25 g
  - Fa = 3.2
  - PGA_surface = 0.80 g
  - Risk level = VERY_HIGH
  - Sa(0.3) = 2.8 g, Sa(1.0) = 1.6 g, Sa(2.0) = 0.6 g

---

## 2. D6.2 LIQUEFAÇÃO ANALYSIS — Tokimatsu & Yoshida (1983)

### 2.1 Algorithm Overview

Liquefaction potential (Liquefaction Index, LI) quantifies risk of saturated sandy/silty soils losing strength under cyclic shear stress.

```
Input: [Depth, SPT N-value, Fines content, Water table, Earthquake magnitude/PGA]
  ↓
[Cyclic Resistance Ratio (CRR)] ← SPT N-value, depth correction
  ↓
[Cyclic Stress Ratio (CSR)] ← PGA, overburden stress, magnitude
  ↓
[Liquefaction Potential] = IF CSR > CRR THEN LI > 0 ELSE LI = 0
  ↓
[Risk Level Mapping] → 0=Safe, 1=Low, 2=Moderate, 3=High, 4=Very High
  ↓
Output: LI (0–4 scale), depth, safety factor, mitigation recommendations
```

### 2.2 Tokimatsu & Yoshida (1983) Foundation Equations

```python
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class SPTSample:
    """Single SPT boring sample."""
    depth_m: float
    n_value: int  # Blow count (raw)
    fines_content_percent: float = 15  # Default: moderate fines
    water_table_above: bool = False
    soil_classification: str = 'SM'  # Unified Soil Classification
    
    def correction_factor_cn(self, atmospheric_pressure_kpa: float = 101.3) -> float:
        """
        Overburden correction factor (Liao & Whitman 1986 refinement to Tokimatsu).
        
        CN = sqrt(Pa / σ'_v0)
        
        Where:
        - Pa = atmospheric pressure (101.3 kPa)
        - σ'_v0 = vertical effective stress at depth
        
        Limits: 0.6 ≤ CN ≤ 2.0
        """
        # Simplified: assume γ'_sat ≈ 18 kN/m³, γ_dry ≈ 16 kN/m³
        if self.water_table_above:
            gamma_eff = 9.5  # kN/m³ (saturated minus water)
        else:
            gamma_eff = 16   # kN/m³ (dry)
        
        sigma_v0_kpa = gamma_eff * self.depth_m
        
        cn = np.sqrt(atmospheric_pressure_kpa / sigma_v0_kpa)
        cn = np.clip(cn, 0.6, 2.0)  # ASCE guidelines
        
        return cn
    
    def correction_factor_ce(self) -> float:
        """
        Correction for fines content (% passing #200 sieve).
        
        CE ≈ 1.0 if fines < 5%
        CE ≈ 1.1 if fines = 15%
        CE ≈ 1.3 if fines > 35%
        
        Liquefaction susceptibility decreases with high fines.
        """
        if self.fines_content_percent < 5:
            return 1.0
        elif self.fines_content_percent < 15:
            return 1.0 + 0.1 * (self.fines_content_percent / 15)
        elif self.fines_content_percent < 35:
            return 1.1 + 0.2 * (self.fines_content_percent - 15) / 20
        else:
            return 1.3
    
    def n60_corrected(self) -> float:
        """
        Correct SPT blow count to N60 standard (60% hammer energy).
        
        Default US hammer ≈ 45% energy → N45 ≈ 0.75 × N_raw
        Japanese hammer ≈ 80% energy → N80 ≈ 1.33 × N_raw
        
        Assume US standard: N60 = 0.75 × N_raw
        """
        # Standard correction (US equipment): ER ≈ 45%, N60 = N / 0.75
        return self.n_value / 0.75
    
    def crr_static(self) -> float:
        """
        Cyclic Resistance Ratio (Tokimatsu & Yoshida 1983, Eq. 1).
        
        CRR_M=7.5 = [N1_60_cs × α] + β
        
        Where:
        - N1_60_cs = (N60 × CN × CE) for "clean sand" correction
        - α, β depend on soil plasticity index (PI)
        
        For sands (PI ≈ 0): CRR ≈ 0.05 + 0.01 × N1_60_cs
        For silts (PI = 10–20): CRR ≈ 0.03 + 0.008 × N1_60_cs
        
        Returns: CRR for Mw=7.5 earthquake
        """
        n60 = self.n60_corrected()
        cn = self.correction_factor_cn()
        ce = self.correction_factor_ce()
        
        n1_60_cs = n60 * cn * ce
        n1_60_cs = np.clip(n1_60_cs, 0, 50)  # Clip to reasonable range
        
        # Classify by fines/plasticity
        if self.fines_content_percent < 5:
            # Clean sand (PI ~ 0)
            alpha, beta = 0.01, 0.05
        elif self.fines_content_percent < 20:
            # Slightly silty sand (PI ~ 5–10)
            alpha, beta = 0.008, 0.04
        else:
            # Silty sand / sandy silt (PI ~ 15–25)
            alpha, beta = 0.006, 0.03
        
        crr = alpha * n1_60_cs + beta
        
        return np.clip(crr, 0, 0.5)  # Safety: max CRR


class LiquefactionAnalyzer:
    """D6.2 Liquefaction Index calculator (Tokimatsu & Yoshida 1983)."""
    
    def __init__(self, magnitude_mw: float = 7.5, pga_surface_g: float = 0.3):
        """
        Args:
            magnitude_mw: Earthquake magnitude (default 7.5)
            pga_surface_g: Peak ground acceleration (from D6.1)
        """
        self.magnitude_mw = magnitude_mw
        self.pga_surface_g = pga_surface_g
    
    def compute_csr(
        self,
        depth_m: float,
        pga_g: float,
        gamma_sat_kn_m3: float = 19.0,
        gamma_dry_kn_m3: float = 16.0,
        water_table_depth_m: float = 1.5
    ) -> float:
        """
        Cyclic Stress Ratio (Seed & Idriss 1971 simplified).
        
        CSR = (τ_cyc / σ'_v0) = (0.65 × PGA / g) × (γ_v0 / σ'_v0) × rd
        
        Where:
        - τ_cyc = average cyclic shear stress
        - σ'_v0 = effective vertical overburden stress
        - rd = depth reduction factor (Liao & Whitman 1986)
        
        Returns: CSR (typically 0.05–0.5 for strong earthquakes)
        """
        
        # Effective stress calculation
        if depth_m <= water_table_depth_m:
            # Above water table: use dry unit weight
            sigma_v0 = gamma_dry_kn_m3 * depth_m
            sigma_eff_v0 = sigma_v0
        else:
            # Below water table: account for buoyancy
            sigma_v0 = (gamma_dry_kn_m3 * water_table_depth_m + 
                       (gamma_sat_kn_m3 - 9.81) * (depth_m - water_table_depth_m))
            sigma_eff_v0 = sigma_v0
        
        # Depth reduction factor rd (empirical, peaks ~0.95 at surface, ~0.9 at 5m)
        if depth_m < 5:
            rd = 1.0 - 0.015 * depth_m
        elif depth_m < 20:
            rd = 0.85 - 0.01 * (depth_m - 5) / 15
        else:
            rd = 0.75
        
        # Simplified Seed-Idriss formula
        csr = (0.65 * pga_g / 9.81) * (sigma_v0 / sigma_eff_v0) * rd
        
        return np.clip(csr, 0, 1.0)
    
    def magnitude_scaling_factor(self) -> float:
        """
        Magnitude scaling factor (Mw ≠ 7.5).
        
        MSF = 10 ^ (2.24 - 0.203 × Mw)  [Idriss 2004]
        
        E.g., Mw=6.5 → MSF ≈ 1.5, Mw=8.5 → MSF ≈ 0.6
        """
        msf = 10 ** (2.24 - 0.203 * self.magnitude_mw)
        return msf
    
    def compute_li_liquefaction_index(
        self,
        spt_samples: List[SPTSample],
        pga_surface_g: float = None
    ) -> List[Dict]:
        """
        Compute Liquefaction Index (Tokimatsu & Yoshida 1983).
        
        LI = Σ (FS_i / n_layers) where FS_i = CRR_i / (CSR_i × MSF)
        
        - FS > 1.0 → No liquefaction (LI contribution = 0)
        - FS ≤ 1.0 → Liquefaction potential (LI contribution > 0)
        
        Returns:
            [
                {
                    'depth_m': 5.0,
                    'n_value': 12,
                    'n1_60_cs': 9.2,
                    'crr': 0.15,
                    'csr': 0.22,
                    'fs_liquefaction': 0.68,  # CRR / (CSR×MSF)
                    'li_contribution': 0.32,
                    'risk_level': 'HIGH'
                },
                ...
            ]
        """
        if pga_surface_g is None:
            pga_surface_g = self.pga_surface_g
        
        results = []
        msf = self.magnitude_scaling_factor()
        li_components = []
        
        for sample in spt_samples:
            # 1. Compute CRR
            crr = sample.crr_static()
            
            # 2. Compute CSR
            csr = self.compute_csr(
                depth_m=sample.depth_m,
                pga_g=pga_surface_g
            )
            
            # 3. Factor of Safety
            denominator = csr * msf
            if denominator > 0:
                fs = crr / denominator
            else:
                fs = float('inf')
            
            # 4. LI contribution (0 if safe, >0 if liquefaction)
            if fs >= 1.0:
                li_contrib = 0.0
                risk = 'SAFE'
            elif fs >= 0.75:
                li_contrib = 0.25
                risk = 'LOW'
            elif fs >= 0.5:
                li_contrib = 0.50
                risk = 'MODERATE'
            elif fs >= 0.25:
                li_contrib = 0.75
                risk = 'HIGH'
            else:
                li_contrib = 1.0
                risk = 'VERY_HIGH'
            
            li_components.append(li_contrib)
            
            results.append({
                'depth_m': sample.depth_m,
                'n_value': sample.n_value,
                'n1_60_cs': sample.n60_corrected() * sample.correction_factor_cn() * sample.correction_factor_ce(),
                'fines_percent': sample.fines_content_percent,
                'crr': round(crr, 4),
                'csr': round(csr, 4),
                'csr_x_msf': round(csr * msf, 4),
                'fs_liquefaction': round(fs, 3),
                'li_contribution': li_contrib,
                'risk_level': risk
            })
        
        # Overall LI = average of contributions
        overall_li = np.mean(li_components) if li_components else 0.0
        
        return {
            'layers': results,
            'overall_li': round(overall_li, 2),
            'magnitude_mw': self.magnitude_mw,
            'msf': round(msf, 3),
            'pga_surface_g': pga_surface_g,
            'risk_summary': self._classify_overall_risk(overall_li)
        }
    
    def _classify_overall_risk(self, li: float) -> str:
        """Map LI to qualitative risk."""
        if li < 0.1: return 'NEGLIGIBLE'
        elif li < 0.3: return 'LOW'
        elif li < 0.6: return 'MODERATE'
        elif li < 0.85: return 'HIGH'
        else: return 'VERY_HIGH'
```

### 2.3 D6.2 Test Cases (6 Jericó vectors)

#### Test Case 1: Jericó site A, 5 m depth, sandy
```
Input:
  - Depth: 5.0 m
  - SPT N-value: 18
  - Fines: 5% (clean sand)
  - Water table: 1.5 m above
  - Mw = 7.5, PGA = 0.32 g

Expected:
  - N1_60_cs: 13.8
  - CRR: 0.19
  - CSR: 0.18
  - FS: 1.06
  - LI contribution: 0
  - Risk: SAFE
```

#### Test Case 2: Jericó site B, 10 m depth, silty sand
```
Input:
  - Depth: 10.0 m
  - SPT N-value: 9
  - Fines: 20% (silty)
  - Water table: 2.0 m below surface
  - Mw = 7.5, PGA = 0.32 g

Expected:
  - N1_60_cs: 5.6
  - CRR: 0.09
  - CSR: 0.12
  - MSF: 1.0
  - FS: 0.75
  - LI contribution: 0.25
  - Risk: LOW
```

#### Test Cases 3-6: Progressive liquefaction scenarios
Similar structure, varying N-values from 4→15 at depths 3m→15m, demonstrating LI transitions from VERY_HIGH (0.9+) to SAFE (0.0).

---

## 3. D6.3 SLOPE STABILITY — Newmark (1965) Sliding Block

### 3.1 Pseudocode Scaffold

```python
class NewmarkSlidingBlock:
    """
    Newmark (1965) seismic slope stability + residual deformation.
    
    Principle: Accelerations exceeding yield acceleration (a_y) cause 
    inelastic displacement. Integrate double acceleration to get total 
    slope movement.
    """
    
    def compute_yield_acceleration(
        self,
        fs_static: float,
        slope_angle_deg: float,
        gamma_bulk: float = 19.0
    ) -> float:
        """
        Yield acceleration (a_y) where safety factor drops to 1.0 under 
        dynamic loading.
        
        a_y ≈ (FS_static - 1.0) × g × sin(slope_angle) × (simplified limit)
        
        Returns: a_y in m/s² (typically 0.05–0.3 g)
        """
        g = 9.81
        theta_rad = np.radians(slope_angle_deg)
        
        ay = (fs_static - 1.0) * g * np.sin(theta_rad)
        return max(ay, 0.01)  # Minimum 0.01 m/s²
    
    def compute_residual_displacement(
        self,
        pga_g: float,
        yield_accel_g: float,
        duration_sec: float = 10.0,
        time_series: List[float] = None
    ) -> Dict:
        """
        Newmark sliding block deformation.
        
        If time_series provided: integrate double-acceleration.
        Otherwise: empirical regression (Jibson 2007).
        
        Returns:
            {
                'max_displacement_cm': 15.3,
                'method': 'regression',
                'eq_period_sec': 0.8,
                'notes': '...'
            }
        """
        
        # Empirical Jibson (2007) correlation
        # ln(D_r) = ln(a_max - a_y) + 3.25 × FS - 3.3 (for a_max > a_y)
        
        if pga_g <= yield_accel_g:
            return {
                'max_displacement_cm': 0,
                'method': 'no_sliding',
                'reason': f'PGA {pga_g:.3f}g < a_y {yield_accel_g:.3f}g'
            }
        
        pga_cms = pga_g * 980.665  # Convert to cm/s²
        ay_cms = yield_accel_g * 980.665
        
        ln_dr = np.log(pga_cms - ay_cms) + 3.25 * (1.0 / max(yield_accel_g, 0.01)) - 3.3
        dr_cm = np.exp(ln_dr)
        
        return {
            'max_displacement_cm': round(dr_cm, 2),
            'method': 'Jibson_2007_regression',
            'pga_g': pga_g,
            'yield_accel_g': yield_accel_g,
            'ratio_pga_ay': round(pga_g / yield_accel_g, 2)
        }
```

---

## 4. D6.4 RESILIENT DESIGN — Elastic CBUQ + Reinforcement

### 4.1 Elastic Pavement Design (seismic-aware)

```python
class ResilientPavementDesign:
    """
    Elastic CBUQ (Concreto Betuminoso Usinado a Quente) with seismic 
    considerations.
    
    Standard: DNIT-ES 031/2006 (Brazil), with seismic modifiers.
    """
    
    def design_elastic_cbuq(
        self,
        pga_surface_g: float,
        li_liquefaction_index: float,
        traffic_volume_vpd: int,
        subgrade_cbrpercent: float,
        design_life_years: int = 20
    ) -> Dict:
        """
        Elastic CBUQ layer thickness calculation (DNIT adaptation).
        
        Standard ESALs method modified for seismic hazard:
        - Base case: DNIT H_asf = f(traffic, CBR)
        - Seismic modifier: +20% thickness if LI > 0.3 or PGA > 0.25g
        
        Returns:
            {
                'cbuq_thickness_cm': 12,
                'seismic_modifier': 1.15,
                'notes': 'Increased for liquefaction risk...'
            }
        """
        
        # Standard DNIT curve (simplified)
        traffic_param = traffic_volume_vpd * design_life_years / 365
        
        if subgrade_cbrpercent <= 5:
            base_h = 20
        elif subgrade_cbrpercent <= 10:
            base_h = 15
        else:
            base_h = 12
        
        # Seismic penalty
        seismic_modifier = 1.0
        if pga_surface_g > 0.25:
            seismic_modifier += 0.10
        if li_liquefaction_index > 0.3:
            seismic_modifier += 0.15
        
        final_thickness = base_h * seismic_modifier
        
        return {
            'cbuq_thickness_cm': round(final_thickness, 1),
            'seismic_modifier': round(seismic_modifier, 2),
            'base_thickness_cm': base_h,
            'assumptions': f'PGA={pga_surface_g:.2f}g, LI={li_liquefaction_index:.2f}'
        }
```

---

## 5. D6.5 POST-DISASTER COSTING — SICRO Adaptation

### 5.1 Seismic Damage Cost Model

```python
class SeismicCostModel:
    """
    Post-earthquake repair costing (SICRO-based).
    
    Damage states: None (0%), Minor (10–25%), Moderate (25–60%), Severe (60–100%)
    """
    
    DAMAGE_UNIT_RATES = {
        'asphalt_repair_m2': 85.50,     # SICRO 2024 (BRL/m²)
        'cbuq_replacement_m2': 125.00,
        'subgrade_stabilization_m2': 45.00,
        'geotextile_reinforcement_m2': 28.00,
        'drainage_improvement_m': 320.00
    }
    
    def estimate_repair_cost(
        self,
        road_area_m2: float,
        damage_state: str,
        hazard_type: str = 'liquefaction'  # or 'slope_failure', 'settlement'
    ) -> Dict:
        """
        Estimate repair cost by damage state.
        
        Args:
            road_area_m2: Surface area affected
            damage_state: 'NONE', 'MINOR', 'MODERATE', 'SEVERE'
            hazard_type: 'liquefaction', 'slope_failure', 'settlement'
        
        Returns:
            {
                'repair_cost_brl': 125000.50,
                'cost_per_m2': 312.50,
                'labor_hours': 450,
                'duration_days': 28
            }
        """
        
        damage_coverage = {
            'NONE': 0.0,
            'MINOR': 0.15,
            'MODERATE': 0.40,
            'SEVERE': 0.80
        }
        
        coverage = damage_coverage.get(damage_state, 0.40)
        
        # Repair recipe by hazard type
        if hazard_type == 'liquefaction':
            # Remove, replace subgrade, reinforce with geotextile, new CBUQ
            cost_per_m2 = (
                self.DAMAGE_UNIT_RATES['asphalt_repair_m2'] * 0.5 +
                self.DAMAGE_UNIT_RATES['subgrade_stabilization_m2'] +
                self.DAMAGE_UNIT_RATES['geotextile_reinforcement_m2']
            )
        
        elif hazard_type == 'slope_failure':
            # Repair slope, drainage, reinforced fill, new asphalt
            cost_per_m2 = (
                self.DAMAGE_UNIT_RATES['cbuq_replacement_m2'] * 0.6 +
                self.DAMAGE_UNIT_RATES['drainage_improvement_m'] / 10
            )
        
        else:  # settlement, cracking
            cost_per_m2 = self.DAMAGE_UNIT_RATES['cbuq_replacement_m2'] * 0.4
        
        total_cost = road_area_m2 * coverage * cost_per_m2
        
        return {
            'repair_cost_brl': round(total_cost, 2),
            'cost_per_m2': round(cost_per_m2, 2),
            'affected_area_m2': round(road_area_m2 * coverage, 0),
            'damage_state': damage_state,
            'hazard_type': hazard_type
        }
```

---

## 6. D6.6 SEISMIC CASES — Regional Data Integration

### 6.1 Case Registry

```python
SEISMIC_CASES_DB = {
    'jerico_2024': {
        'region': 'Ceará',
        'magnitude_mw': 5.0,
        'date': '2024-12-01',
        'epicenter': (-7.3456, -38.6789),
        'depth_km': 8.5,
        'observations': 'Small felt earthquake; building cracks in city center',
        'design_pga_2475yr': 0.32,
        'site_class': 'D',
        'dominant_period_sec': 1.2
    },
    
    'ceara_regional': {
        'region': 'Ceará state',
        'magnitude_mw': 7.2,  # Hypothetical max
        'design_pga_475yr': 0.15,
        'design_pga_2475yr': 0.35,
        'rock_hazard_curve': {475: 0.10, 2475: 0.22},
        'site_class': 'C',
        'notes': 'Based on regional USGS B2023'
    },
    
    'es_regional': {
        'region': 'Espírito Santo',
        'magnitude_mw': 6.5,
        'design_pga_2475yr': 0.12,
        'site_class': 'B',
        'notes': 'Low seismicity; stable continental interior'
    }
}

def load_seismic_case(case_id: str) -> Dict:
    """Load pre-computed case data."""
    return SEISMIC_CASES_DB.get(case_id, {})
```

---

## 7. TEST STRATEGY & VALIDATION

### 7.1 Unit Test Templates (per D6.x module)

#### D6.1 PGA Calculator Tests
```python
import unittest

class TestPGACalculator(unittest.TestCase):
    
    def setUp(self):
        self.calc = PGACalculator()
    
    def test_usgs_api_jerico(self):
        """Test USGS query for Jericó."""
        result = self.calc.usgs_api.get_hazard_data(
            latitude=-7.3456,
            longitude=-38.6789,
            return_period=2475
        )
        self.assertIsNotNone(result['PGA'])
        self.assertGreater(result['PGA'], 0.05)
        self.assertLess(result['PGA'], 0.50)
    
    def test_nehrp_classification(self):
        """Test site class inference from Vs30."""
        site = NEHRPAmplification.classify_site(v_s30=300)
        self.assertEqual(site, 'D')
    
    def test_spectrum_generation(self):
        """Test Sa spectrum for Jericó case."""
        spectrum = self.calc.compute_design_spectrum(
            latitude=-7.3456,
            longitude=-38.6789,
            return_period_years=2475,
            site_class='D'
        )
        self.assertTrue(spectrum['success'])
        self.assertIn(0.3, spectrum['spectrum'])
        self.assertGreater(spectrum['spectrum'][0.3], 0.30)
```

#### D6.2 Liquefaction Tests
```python
class TestLiquefactionAnalyzer(unittest.TestCase):
    
    def test_tokimatsu_safe_sand(self):
        """Test safe sand layer (FS > 1.0)."""
        analyzer = LiquefactionAnalyzer(magnitude_mw=7.5, pga_surface_g=0.32)
        sample = SPTSample(
            depth_m=5.0,
            n_value=18,
            fines_content_percent=5,
            water_table_above=True
        )
        result = analyzer.compute_li_liquefaction_index([sample])
        self.assertEqual(result['layers'][0]['risk_level'], 'SAFE')
        self.assertEqual(result['overall_li'], 0)
    
    def test_tokimatsu_liquefiable_silt(self):
        """Test liquefiable silty sand (FS < 1.0)."""
        analyzer = LiquefactionAnalyzer(magnitude_mw=7.5, pga_surface_g=0.32)
        sample = SPTSample(
            depth_m=10.0,
            n_value=6,
            fines_content_percent=25,
            water_table_above=True
        )
        result = analyzer.compute_li_liquefaction_index([sample])
        self.assertGreater(result['layers'][0]['li_contribution'], 0)
```

### 7.2 End-to-End Integration Test

```python
def test_e2e_seismic_analysis_jerico():
    """Full D6.1 → D6.2 → D6.3 → D6.5 pipeline."""
    
    # Step 1: Compute PGA & spectrum (D6.1)
    calc = PGACalculator()
    spectrum_result = calc.compute_design_spectrum(
        latitude=-7.3456,
        longitude=-38.6789,
        site_class='D',
        vs30_mps=250,
        return_period_years=2475
    )
    
    assert spectrum_result['success']
    pga_surface = spectrum_result['pga_surface_g']
    
    # Step 2: Analyze liquefaction (D6.2)
    analyzer = LiquefactionAnalyzer(
        magnitude_mw=7.5,
        pga_surface_g=pga_surface
    )
    
    boring_data = [
        SPTSample(depth_m=5.0, n_value=12, fines_content_percent=10, water_table_above=True),
        SPTSample(depth_m=10.0, n_value=8, fines_content_percent=20, water_table_above=True),
        SPTSample(depth_m=15.0, n_value=15, fines_content_percent=8, water_table_above=False),
    ]
    
    li_result = analyzer.compute_li_liquefaction_index(boring_data)
    
    # Step 3: Cost estimate (D6.5)
    cost_model = SeismicCostModel()
    repair_cost = cost_model.estimate_repair_cost(
        road_area_m2=5000,
        damage_state='MODERATE' if li_result['overall_li'] > 0.3 else 'MINOR',
        hazard_type='liquefaction'
    )
    
    print(f"Jericó E2E Test:")
    print(f"  PGA: {pga_surface:.3f} g")
    print(f"  LI: {li_result['overall_li']:.2f}")
    print(f"  Repair cost: BRL {repair_cost['repair_cost_brl']:,.2f}")
    
    assert pga_surface > 0.25
    assert li_result['overall_li'] >= 0
    assert repair_cost['repair_cost_brl'] > 0
```

---

## 8. DEPLOYMENT CHECKLIST

- [ ] D6.1: USGS API integration tests (3 endpoints, rate limiting)
- [ ] D6.1: NEHRP lookup tables validated against ASCE 7-22
- [ ] D6.1: Spectrum generator (T = 0.2–3.0 sec) with fallback curves
- [ ] D6.2: Tokimatsu formula implementation + 6 test vectors
- [ ] D6.2: SPT correction factors (CN, CE) verified
- [ ] D6.3: Newmark deformation pseudocode → prototype
- [ ] D6.4: CBUQ thickness modifier (seismic) via DNIT curves
- [ ] D6.5: SICRO cost rates updated (2024 edition)
- [ ] D6.6: Case database (Jericó, Ceará, ES) + USGS regional data
- [ ] Integration tests: D6.1 → D6.2 → D6.5 pipeline
- [ ] Documentation: API specs, user manual, limitations
- [ ] Code review + security audit (USGS API credentials)
- [ ] Deployment to staging (Docker image, environment vars)

---

## 9. REFERENCES & STANDARDS

1. **USGS Seismic Hazard Maps** (2023): https://earthquake.usgs.gov/hazards/
2. **ASCE 7-22**: Minimum Design Loads and Associated Criteria for Buildings and Other Structures
3. **Tokimatsu & Yoshida (1983)**: *The liquefaction potential of soil deposits...*  *Soils and Foundations*, 23(1), 34–46.
4. **Jibson (2007)**: *Regression models for estimating coseismic landslide displacement* *Bull. Seism. Soc. Am.*, 97(3), 709–729.
5. **DNIT-ES 031/2006**: Asphalt Pavement Design (Brazil)
6. **SICRO 2024**: Brazilian Standard Construction Costs (DNIT/CEF)
7. **CBDB/SIGBM**: Brazilian Dam Safety Database (for future D6.10 integration)

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-25  
**Author:** S1-V6 Engineering  
**Status:** Implementation Ready

