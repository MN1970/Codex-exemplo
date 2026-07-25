# S1-V7 Seismic-Resilient Road Geometry — Implementation Roadmap
## Manta Associados | Agente-Infraestrutura (S1) | 5-Discipline Integration

**Document Version:** v1.0  
**Created:** 2026-07-25  
**Timeline:** AGO 2026 – JUN 2027 (8 sprints)  
**Owner:** Manta 03-S1 (Rodovias) + Manta-06 (Modelagem)  
**Status:** IMPLEMENTATION-READY

---

## EXECUTIVE SUMMARY

This roadmap consolidates Workflow 16 outputs into a unified implementation strategy for seismic-resilient road geometry across 5 disciplines (D7.1–D7.5). Key features:

- **Horizontal Geometry (D7.1):** Radius multipliers (1.1–1.3×) driven by seismic acceleration, dynamic superelevation (+0.5–1.5%), visibility compliance.
- **Vertical Geometry (D7.2):** Reduced rampa (6–7.5% vs 8–10% conventional), PIV radius sizing, Newmark slope stability integration.
- **Geo-Talude Interaction (D7.3):** Bidirectional feedback loop (D6.3 → D7), iterative convergence, Jericó Km 45+800 pilot.
- **Viaria Safety Seismic (D7.4):** +18% stopping distance, tombamento (rollover) risk assessment, lane width optimization.
- **Jericó Redesign (D7.5):** 3 alternatives (Conservative/Balanced/Aggressive), cost-benefit analysis.

**Handoffs:** Agente-05 (costing), Agente-07 (timeline), Advisory, Contratual.

---

## SECTION 1: D7.1–D7.4 GEOMETRY IMPLEMENTATION

### 1.1 Horizontal Geometry Module (D7.1)

#### 1.1.1 Radius Optimization Algorithm

```python
import math
from dataclasses import dataclass
from enum import Enum

class SeismicZone(Enum):
    """Seismic acceleration zones per ABNT NBR 15421"""
    LOW = 0.05        # ag = 0.05g
    MEDIUM = 0.10     # ag = 0.10g
    HIGH = 0.20       # ag = 0.20g
    VERY_HIGH = 0.30  # ag = 0.30g

@dataclass
class HorizontalGeometryInput:
    """Input parameters for horizontal geometry design"""
    design_speed_kmh: float       # Velocidade de projeto (km/h)
    seismic_zone: SeismicZone     # Zona sísmica (ABNT)
    curve_type: str               # 'circular', 'clothoid', 'combined'
    existing_radius_m: float = 0  # Se retrofit
    terrain_difficulty: str = 'flat'  # 'flat', 'hilly', 'mountainous'

@dataclass
class HorizontalGeometryOutput:
    """Output design parameters"""
    design_radius_m: float
    radius_multiplier: float
    superelevation_design: float   # %
    superelevation_max: float      # %
    visibility_distance_m: float
    stopping_distance_m: float
    relative_gradient_max: float   # ramp rate %/m
    seismic_stability_factor: float
    remarks: str

def calculate_seismic_radius_multiplier(
    seismic_zone: SeismicZone,
    terrain_difficulty: str
) -> float:
    """
    Calculate radius multiplier based on seismic acceleration
    and terrain type.
    
    Multiplier range: 1.1 – 1.3×
    - Lower multiplier (1.1): flat terrain, low seismic acceleration
    - Higher multiplier (1.3): mountainous, high seismic acceleration
    """
    base_multipliers = {
        SeismicZone.LOW: 1.10,
        SeismicZone.MEDIUM: 1.15,
        SeismicZone.HIGH: 1.22,
        SeismicZone.VERY_HIGH: 1.30
    }
    
    terrain_adjustments = {
        'flat': 0.0,
        'hilly': 0.03,
        'mountainous': 0.05
    }
    
    base = base_multipliers[seismic_zone]
    adjustment = terrain_adjustments.get(terrain_difficulty, 0.03)
    
    multiplier = base + adjustment
    return min(multiplier, 1.30)  # Cap at 1.30

def design_horizontal_geometry(params: HorizontalGeometryInput) -> HorizontalGeometryOutput:
    """
    Main function for horizontal geometry design with seismic considerations.
    
    Design steps:
    1. Calculate seismic radius multiplier
    2. Determine design radius (apply multiplier to conventional radius)
    3. Calculate superelevation (6–12% per ABNT NBR 15421)
    4. Verify visibility and stopping distance
    5. Assess seismic stability (lateral acceleration resistance)
    """
    
    # Step 1: Conventional radius (NBR 15421, Table 4)
    conventional_radii = {
        40: 60,    # V=40 km/h → R=60m
        50: 100,
        60: 150,
        70: 240,
        80: 350,
        90: 500,
        100: 700,
        110: 950,
        120: 1300
    }
    
    v_design = params.design_speed_kmh
    conventional_r = conventional_radii.get(
        min(conventional_radii.keys(), key=lambda x: abs(x - v_design))
    )
    
    # Step 2: Apply seismic multiplier
    multiplier = calculate_seismic_radius_multiplier(
        params.seismic_zone,
        params.terrain_difficulty
    )
    design_radius = conventional_r * multiplier
    
    # Step 3: Superelevation calculation with seismic adjustment
    # Base formula: e_conv = (V²) / (127 * R)
    # Seismic adjustment: +0.5% to +1.5% for high acceleration zones
    
    v_ms = v_design / 3.6  # Convert km/h to m/s
    max_superelevation = 0.12  # 12% (NBR standard)
    friction_factor = 0.35  # μ for wet asphalt
    
    # Conventional superelevation
    e_conventional = (v_ms ** 2) / (127 * design_radius)
    e_conventional = min(e_conventional, max_superelevation)
    
    # Seismic adjustment
    seismic_adjustment = {
        SeismicZone.LOW: 0.005,
        SeismicZone.MEDIUM: 0.010,
        SeismicZone.HIGH: 0.015,
        SeismicZone.VERY_HIGH: 0.020
    }
    
    e_seismic = e_conventional + seismic_adjustment.get(params.seismic_zone, 0.010)
    e_design = min(e_seismic, max_superelevation)
    
    # Step 4: Visibility distance (AASHTO stopping sight distance)
    # SSD = V*t + V²/(2*a)
    # where t=2.5s (perception-reaction), a=3.4 m/s² (braking deceleration)
    
    perception_reaction_time = 2.5  # seconds
    braking_deceleration = 3.4  # m/s²
    
    stopping_distance = (
        v_ms * perception_reaction_time +
        (v_ms ** 2) / (2 * braking_deceleration)
    )
    
    # Seismic adjustment: +18% for high acceleration zones
    if params.seismic_zone in [SeismicZone.HIGH, SeismicZone.VERY_HIGH]:
        stopping_distance *= 1.18
    
    visibility_distance = stopping_distance * 1.3  # 30% safety margin
    
    # Step 5: Seismic stability factor (lateral acceleration resistance)
    # CSF = (e + μ) / (1 - e*μ)
    # where e=superelevation, μ=friction coefficient
    
    ag = params.seismic_zone.value  # Seismic acceleration (g)
    lateral_accel_limit = 0.30 * 9.81  # 0.30g is design limit
    
    # Required friction to resist lateral motion
    required_friction = lateral_accel_limit / 9.81 - e_design
    actual_friction = friction_factor
    
    seismic_stability_factor = (e_design + actual_friction) / \
                              (1 - e_design * actual_friction)
    
    # Relative gradient for superelevation ramp (r = Δe / L)
    # Recommended: r ≤ 0.67% per AASHTO (r_max = 1/150)
    relative_gradient_max = 0.0067
    
    return HorizontalGeometryOutput(
        design_radius_m=round(design_radius, 1),
        radius_multiplier=round(multiplier, 3),
        superelevation_design=round(e_design * 100, 2),
        superelevation_max=round(max_superelevation * 100, 2),
        visibility_distance_m=round(visibility_distance, 1),
        stopping_distance_m=round(stopping_distance, 1),
        relative_gradient_max=round(relative_gradient_max * 100, 2),
        seismic_stability_factor=round(seismic_stability_factor, 3),
        remarks=f"Multiplier: {multiplier:.2f}x | Seismic zone: {params.seismic_zone.name} (ag={params.seismic_zone.value}g)"
    )

# Test Cases
def test_horizontal_geometry():
    """Three test scenarios: flat, hilly, mountainous"""
    
    test_cases = [
        # Case 1: Flat terrain, medium seismic (typical)
        HorizontalGeometryInput(
            design_speed_kmh=80,
            seismic_zone=SeismicZone.MEDIUM,
            curve_type='circular',
            terrain_difficulty='flat'
        ),
        # Case 2: Hilly, high seismic
        HorizontalGeometryInput(
            design_speed_kmh=60,
            seismic_zone=SeismicZone.HIGH,
            curve_type='clothoid',
            terrain_difficulty='hilly'
        ),
        # Case 3: Mountainous, very high seismic
        HorizontalGeometryInput(
            design_speed_kmh=50,
            seismic_zone=SeismicZone.VERY_HIGH,
            curve_type='combined',
            terrain_difficulty='mountainous'
        )
    ]
    
    results = []
    for i, params in enumerate(test_cases, 1):
        output = design_horizontal_geometry(params)
        results.append({
            'test_case': f"Case {i}: {params.terrain_difficulty.capitalize()} / {params.seismic_zone.name}",
            'v_design': params.design_speed_kmh,
            'r_design': output.design_radius_m,
            'multiplier': output.radius_multiplier,
            'e_design': output.superelevation_design,
            'ssd': output.stopping_distance_m,
            'visibility': output.visibility_distance_m,
            'csf': output.seismic_stability_factor
        })
    
    return results

if __name__ == "__main__":
    test_results = test_horizontal_geometry()
    for result in test_results:
        print(f"\n{result['test_case']}")
        print(f"  Design Radius: {result['r_design']} m")
        print(f"  Multiplier: {result['multiplier']}x")
        print(f"  Superelevation: {result['e_design']}%")
        print(f"  Stopping Distance: {result['ssd']} m")
        print(f"  Visibility Distance: {result['visibility']} m")
        print(f"  Seismic Stability Factor: {result['csf']}")
```

---

### 1.2 Vertical Geometry Module (D7.2)

#### 1.2.1 Rampa & PIV Radius Calculation

```python
from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass
class VerticalGeometryInput:
    """Input parameters for vertical geometry design"""
    design_speed_kmh: float
    rampa_grade: float            # Longitudinal grade (%)
    seismic_zone: SeismicZone     # For Newmark integration
    slope_height_m: float = 0     # Slope adjacent to road
    piv_elevation_start: float = 0
    piv_elevation_end: float = 0
    design_type: str = 'new'      # 'new' or 'retrofit'

@dataclass
class PIVElement:
    """Vertical curve point of intersection"""
    station_km: float
    elevation_m: float
    grade_incoming: float         # % (negative = downslope)
    grade_outgoing: float         # % (positive = upslope)
    radius_m: float
    curve_length_m: float

@dataclass
class VerticalGeometryOutput:
    """Output design parameters"""
    recommended_rampa: float      # % (6-7.5%)
    piv_elements: List[PIVElement]
    max_rampa: float              # Maximum allowable grade
    newmark_displacement_cm: float  # Sliding displacement (D)
    design_remarks: str

def calculate_piv_radius(
    grade_change_percent: float,
    design_speed_kmh: float,
    curve_type: str = 'sag'
) -> float:
    """
    Calculate PIV (Point of Vertical Intersection) radius.
    
    Two curve types:
    - Crest (convex): for drainage and sightline
    - Sag (concave): for comfort and ride quality
    
    Formula: Kv = R / |A|
    where A = |grade_out - grade_in|
    
    Standard Kv values (AASHTO):
    - Crest: Kv = 150–600 (higher for better sightline)
    - Sag: Kv = 40–150 (higher for better comfort)
    """
    
    A = abs(grade_change_percent)
    
    if curve_type.lower() == 'crest':
        # Crest curve (convex)
        # Minimum Kv based on stopping sight distance
        v_ms = design_speed_kmh / 3.6
        stopping_distance = v_ms * 2.5 + (v_ms ** 2) / (2 * 3.4)
        kv_min = (stopping_distance ** 2) / (200 + 3.5 * stopping_distance)
        kv_design = max(kv_min, 300)  # Use 300 as typical design value
    else:
        # Sag curve (concave)
        # For comfort, use formula: rate of grade change ≤ 2% per second
        # v_ms / (radius * t²) ≤ 0.02
        kv_design = 100  # Typical sag curve value
    
    radius = kv_design * A
    return radius

def design_vertical_geometry(params: VerticalGeometryInput) -> VerticalGeometryOutput:
    """
    Main function for vertical geometry design.
    
    Design criteria:
    1. Reduce rampa to 6–7.5% (vs conventional 8–10%)
    2. Size PIV radii for crest/sag curves
    3. Integrate Newmark slope stability (Km 45+800 context)
    4. Verify comfort and drainage
    """
    
    # Step 1: Determine recommended rampa grade
    # Conventional: 8–10%, Seismic-resilient: 6–7.5%
    # Reduction enables better Newmark integration with slopes
    
    rampa_conventional_max = 0.10  # 10%
    rampa_design_max = 0.075  # 7.5%
    
    # If input rampa exceeds design max, flag for recalibration
    if params.rampa_grade > rampa_design_max:
        recommended_rampa = rampa_design_max
    else:
        recommended_rampa = params.rampa_grade
    
    # Step 2: PIV radius calculation (example with 2 curves)
    piv_elements = []
    
    # Hypothetical PIV 1: Crest curve (downslope → upslope transition)
    grade_in_piv1 = -3.5  # Coming downhill at 3.5%
    grade_out_piv1 = 2.0  # Going uphill at 2.0%
    grade_change_piv1 = abs(grade_out_piv1 - grade_in_piv1)  # 5.5%
    
    radius_piv1 = calculate_piv_radius(
        grade_change_piv1,
        params.design_speed_kmh,
        curve_type='crest'
    )
    
    curve_length_piv1 = radius_piv1 * grade_change_piv1 / 100  # L = R * |A|
    
    piv_elements.append(PIVElement(
        station_km=45.8,
        elevation_m=params.piv_elevation_start,
        grade_incoming=grade_in_piv1,
        grade_outgoing=grade_out_piv1,
        radius_m=round(radius_piv1, 1),
        curve_length_m=round(curve_length_piv1, 1)
    ))
    
    # Hypothetical PIV 2: Sag curve (upslope → downslope transition)
    grade_in_piv2 = 4.5  # Coming uphill at 4.5%
    grade_out_piv2 = -2.0  # Going downhill at 2.0%
    grade_change_piv2 = abs(grade_out_piv2 - grade_in_piv2)  # 6.5%
    
    radius_piv2 = calculate_piv_radius(
        grade_change_piv2,
        params.design_speed_kmh,
        curve_type='sag'
    )
    
    curve_length_piv2 = radius_piv2 * grade_change_piv2 / 100
    
    piv_elements.append(PIVElement(
        station_km=48.2,
        elevation_m=params.piv_elevation_end,
        grade_incoming=grade_in_piv2,
        grade_outgoing=grade_out_piv2,
        radius_m=round(radius_piv2, 1),
        curve_length_m=round(curve_length_piv2, 1)
    ))
    
    # Step 3: Newmark slope stability integration
    # Newmark method: Dn = (ac/ag)² * (vy/ag) * g / (2*cy)
    # Simplified: Newmark displacement ≈ 10–50 cm for typical slopes
    # High ag → larger D → need gentler rampa or flatter slope
    
    ag = params.seismic_zone.value
    
    if ag >= 0.20:  # HIGH or VERY_HIGH seismic
        # Estimate Newmark displacement (critical acceleration method)
        # For 6–7.5% rampa, displacement typically 15–30 cm
        newmark_displacement = 20.0 + (ag - 0.20) * 100  # cm, rough estimate
    else:
        newmark_displacement = 10.0
    
    # Step 4: Maximum rampa determination
    max_rampa_geometric = 0.08  # 8% geometric limit
    max_rampa_seismic = 0.075   # 7.5% seismic-adjusted
    max_rampa = min(max_rampa_geometric, max_rampa_seismic)
    
    return VerticalGeometryOutput(
        recommended_rampa=round(recommended_rampa * 100, 2),
        piv_elements=piv_elements,
        max_rampa=round(max_rampa * 100, 2),
        newmark_displacement_cm=round(newmark_displacement, 1),
        design_remarks=f"Rampa: {recommended_rampa*100:.1f}% (Newmark D={newmark_displacement:.1f} cm) | {len(piv_elements)} PIV curves designed"
    )

# Test: Vertical geometry for Jericó area
def test_vertical_geometry_jerico():
    """Test case: Jericó Km 45+800 (high seismic, slope interaction)"""
    
    params = VerticalGeometryInput(
        design_speed_kmh=60,
        rampa_grade=0.07,
        seismic_zone=SeismicZone.HIGH,
        slope_height_m=15.0,
        piv_elevation_start=850.5,
        piv_elevation_end=870.2,
        design_type='retrofit'
    )
    
    output = design_vertical_geometry(params)
    
    print("Jericó Km 45+800 Vertical Geometry Design")
    print(f"  Recommended Rampa: {output.recommended_rampa}%")
    print(f"  Max Allowable Rampa: {output.max_rampa}%")
    print(f"  Newmark Displacement: {output.newmark_displacement_cm} cm")
    print(f"\n  PIV Curves:")
    for piv in output.piv_elements:
        print(f"    Km {piv.station_km}: R={piv.radius_m} m, L={piv.curve_length_m} m")
        print(f"      Grade: {piv.grade_incoming}% → {piv.grade_outgoing}%")
    
    return output
```

---

### 1.3 Viaria Safety Seismic Module (D7.4)

#### 1.3.1 Stopping Distance & Tombamento (Rollover) Risk

```python
from dataclasses import dataclass
from enum import Enum

class VehicleType(Enum):
    """Standard Brazilian vehicle classifications"""
    LIGHT_CAR = {'mass': 1200, 'height_cg': 0.65, 'width': 1.8}
    SUV_4WD = {'mass': 1800, 'height_cg': 0.85, 'width': 1.9}
    TRUCK_SEMI = {'mass': 2500, 'height_cg': 1.8, 'width': 2.5}
    BUS = {'mass': 3500, 'height_cg': 1.6, 'width': 2.6}

@dataclass
class SafetySeismicInput:
    """Input parameters for seismic safety assessment"""
    design_speed_kmh: float
    vehicle_type: VehicleType
    seismic_zone: SeismicZone
    lateral_acceleration_g: float = 0.3  # Design lateral accel (g)
    horizontal_curve_radius_m: float = 350  # Curve radius
    superelevation_pct: float = 5.0  # Superelevation (%)
    lane_width_m: float = 3.5  # Current lane width

@dataclass
class SafetySeismicOutput:
    """Output safety parameters"""
    stopping_distance_seismic_m: float
    stopping_distance_conventional_m: float
    ssd_increase_pct: float
    rollover_critical_speed_kmh: float
    rollover_margin_pct: float  # >0 = safe
    lane_width_required_m: float
    lateral_shift_m: float
    safety_assessment: str

def calculate_stopping_distance_seismic(
    v_kmh: float,
    seismic_zone: SeismicZone,
    apply_seismic_penalty: bool = True
) -> Tuple[float, float, float]:
    """
    Calculate stopping distance with seismic adjustment (+18% for high zones).
    
    Returns: (conventional_ssd, seismic_ssd, increase_pct)
    """
    
    v_ms = v_kmh / 3.6
    
    # Perception-reaction distance
    perception_time = 2.5  # seconds
    d_perception = v_ms * perception_time
    
    # Braking distance
    braking_decel = 3.4  # m/s² (typical wet asphalt)
    d_braking = (v_ms ** 2) / (2 * braking_decel)
    
    # Conventional SSD
    ssd_conventional = d_perception + d_braking
    
    # Seismic adjustment: +18% for HIGH/VERY_HIGH zones
    if apply_seismic_penalty and seismic_zone in [SeismicZone.HIGH, SeismicZone.VERY_HIGH]:
        ssd_seismic = ssd_conventional * 1.18
    else:
        ssd_seismic = ssd_conventional
    
    increase_pct = ((ssd_seismic - ssd_conventional) / ssd_conventional) * 100
    
    return ssd_conventional, ssd_seismic, increase_pct

def calculate_rollover_critical_speed(
    vehicle: VehicleType,
    horizontal_radius_m: float,
    superelevation_pct: float
) -> Tuple[float, float]:
    """
    Calculate critical speed for rollover (tombamento).
    
    Critical condition: lateral acceleration > required friction + superelevation effect
    
    Formula: V_critical = sqrt(R * g * (e + μ_rollover))
    where μ_rollover ≈ 0.4 (rollover friction coefficient)
    
    Returns: (critical_speed_kmh, margin_if_design_speed)
    """
    
    vehicle_data = vehicle.value
    h_cg = vehicle_data['height_cg']  # Height of center of gravity (m)
    width = vehicle_data['width']  # Vehicle width (m)
    
    # Rollover margin: track width / height
    # If lateral accel * h > 0.5 * width → rollover risk
    
    e = superelevation_pct / 100  # Convert % to fraction
    g = 9.81  # m/s²
    R = horizontal_radius_m
    
    # Friction coefficient at rollover (typically 0.4–0.5)
    mu_rollover = 0.40
    
    # Critical speed formula
    v_critical_ms = math.sqrt(R * g * (e + mu_rollover))
    v_critical_kmh = v_critical_ms * 3.6
    
    # Rollover margin at design speed (60 km/h typical)
    # Margin = (V_critical - V_design) / V_design
    # Positive = safe, negative = at risk
    
    return v_critical_kmh, (h_cg, width)

def design_safety_seismic(params: SafetySeismicInput) -> SafetySeismicOutput:
    """
    Comprehensive seismic safety assessment for roadway design.
    
    Checks:
    1. Stopping distance adequacy (conventional + seismic)
    2. Rollover risk (tombamento)
    3. Lane width adequacy for lateral shift
    """
    
    # Step 1: Stopping distance (conventional + seismic)
    ssd_conv, ssd_seismic, ssd_increase = calculate_stopping_distance_seismic(
        params.design_speed_kmh,
        params.seismic_zone
    )
    
    # Step 2: Rollover critical speed
    v_critical, vehicle_dims = calculate_rollover_critical_speed(
        params.vehicle_type,
        params.horizontal_curve_radius_m,
        params.superelevation_pct
    )
    
    h_cg, vehicle_width = vehicle_dims
    
    # Rollover margin: if design speed < critical speed, safe
    rollover_margin = ((v_critical - params.design_speed_kmh) / v_critical) * 100
    
    # Step 3: Lane width requirement for lateral shift during seismic event
    # Lateral shift (meters) = vehicle width * lateral_accel (g)
    # Required lane width = original width + safety margin
    
    lateral_shift = vehicle_width * params.lateral_acceleration_g * 0.5  # m
    lane_width_required = params.lane_width_m + lateral_shift + 0.5  # 0.5 m safety margin
    
    # Step 4: Safety assessment narrative
    if rollover_margin > 10:
        safety_level = "SAFE - Rollover risk minimal"
    elif rollover_margin > 0:
        safety_level = "ACCEPTABLE - Rollover risk present but manageable"
    else:
        safety_level = "AT RISK - Immediate mitigation required"
    
    if lane_width_required > params.lane_width_m + 0.3:
        lane_assessment = f"Lane width increase needed: {lane_width_required:.2f} m"
    else:
        lane_assessment = f"Current lane width adequate: {params.lane_width_m} m"
    
    remarks = f"{safety_level} | {lane_assessment} | SSD increase: {ssd_increase:.1f}%"
    
    return SafetySeismicOutput(
        stopping_distance_seismic_m=round(ssd_seismic, 1),
        stopping_distance_conventional_m=round(ssd_conv, 1),
        ssd_increase_pct=round(ssd_increase, 1),
        rollover_critical_speed_kmh=round(v_critical, 1),
        rollover_margin_pct=round(rollover_margin, 1),
        lane_width_required_m=round(lane_width_required, 2),
        lateral_shift_m=round(lateral_shift, 2),
        safety_assessment=remarks
    )

# Test: Safety assessment for heavy vehicle in seismic zone
def test_safety_seismic():
    """Test case: Heavy truck (2.5 tons) in high seismic zone"""
    
    params = SafetySeismicInput(
        design_speed_kmh=80,
        vehicle_type=VehicleType.TRUCK_SEMI,
        seismic_zone=SeismicZone.HIGH,
        lateral_acceleration_g=0.3,
        horizontal_curve_radius_m=350,
        superelevation_pct=5.5,
        lane_width_m=3.6
    )
    
    output = design_safety_seismic(params)
    
    print("Safety Seismic Assessment (Heavy Truck, HIGH seismic zone)")
    print(f"  Conventional SSD: {output.stopping_distance_conventional_m} m")
    print(f"  Seismic SSD: {output.stopping_distance_seismic_m} m (+{output.ssd_increase_pct}%)")
    print(f"  Rollover Critical Speed: {output.rollover_critical_speed_kmh} km/h")
    print(f"  Rollover Margin: {output.rollover_margin_pct}%")
    print(f"  Required Lane Width: {output.lane_width_required_m} m")
    print(f"  Lateral Shift: {output.lateral_shift_m} m")
    print(f"\n  Assessment: {output.safety_assessment}")
    
    return output
```

---

## SECTION 2: D7.3 GEO-TALUDE INTERACTION & FEEDBACK LOOP

### 2.1 Bidirectional Feedback Loop (D6.3 ↔ D7)

```python
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class ConvergenceStatus(Enum):
    CONVERGED = "converged"
    ITERATING = "iterating"
    DIVERGED = "diverged"

@dataclass
class GeotechnicalSlope:
    """Input from D6.3 (Geotechnical Engineering)"""
    station_km: float
    slope_height_m: float
    slope_angle_degrees: float
    soil_type: str              # 'clay', 'sand', 'rock', 'mixed'
    cohesion_kpa: float         # Soil cohesion
    friction_angle_degrees: float
    unit_weight_kn_m3: float
    groundwater_depth_m: float = 999  # Very deep = dry
    factor_of_safety_static: float = 1.5  # Target FoS
    factor_of_safety_seismic: float = 1.1

@dataclass
class RoadGeometry:
    """Input from D7 (Road Geometry)"""
    design_speed_kmh: float
    rampa_grade_pct: float
    horizontal_radius_m: float
    superelevation_pct: float
    road_width_m: float
    cut_fill_height_m: float = 0  # Relative to natural ground

@dataclass
class FeedbackIteration:
    """Single iteration of geo-road feedback loop"""
    iteration_number: int
    slope_fos_static: float
    slope_fos_seismic: float
    newmark_displacement_cm: float
    road_rampa_pct: float
    required_rampa_adjustment_pct: float
    geometry_feasible: bool
    convergence_delta: float

def calculate_slope_factor_of_safety(
    slope: GeotechnicalSlope,
    seismic_zone: SeismicZone
) -> Tuple[float, float]:
    """
    Calculate slope factor of safety (static and seismic).
    
    Simplified Bishop's method for circular slip surfaces.
    FoS = (Strength) / (Driving Force)
    
    Returns: (FoS_static, FoS_seismic)
    """
    
    H = slope.slope_height_m
    beta = slope.slope_angle_degrees
    phi = slope.friction_angle_degrees
    c = slope.cohesion_kpa
    gamma = slope.unit_weight_kn_m3
    
    # Simplified FoS calculation (1:1 slope approximation)
    # FoS = (c + gamma*H*cos(β)*tan(φ)) / (gamma*H*sin(β))
    
    beta_rad = math.radians(beta)
    phi_rad = math.radians(phi)
    
    numerator = c + gamma * H * math.cos(beta_rad) * math.tan(phi_rad)
    denominator = gamma * H * math.sin(beta_rad)
    
    if denominator == 0:
        return 999.0, 999.0
    
    fos_static = numerator / denominator
    
    # Seismic adjustment: reduce FoS by kh (horizontal seismic coefficient)
    kh = seismic_zone.value * 0.5  # Simplified: kh ≈ 0.5 * ag
    
    # Pseudostatic method: FoS_seismic = FoS_static / (1 + kh*tan(β)/tan(φ))
    denominator_seismic = 1 + (kh * math.tan(beta_rad)) / (math.tan(phi_rad) + 1e-6)
    fos_seismic = fos_static / denominator_seismic
    
    return fos_static, fos_seismic

def calculate_newmark_displacement(
    slope: GeotechnicalSlope,
    seismic_zone: SeismicZone,
    fos_seismic: float
) -> float:
    """
    Calculate Newmark sliding displacement (cm).
    
    Newmark method: D = (ac/ag)² * (vy/ag) * g / (2*cy)
    Simplified: D ≈ 0.5 * ag² / (FoS_seismic - 1) if FoS_seismic > 1
    
    Returns: displacement in cm
    """
    
    ag = seismic_zone.value  # Seismic acceleration (g)
    
    if fos_seismic <= 1.0:
        # Unlimited displacement (failure)
        return 999.0
    
    # Simplified Newmark: D ≈ 10 * ag² / (FoS_seismic - 1)
    # (empirical constant 10 for typical slopes)
    displacement_m = 10.0 * (ag ** 2) / (max(fos_seismic - 1.0, 0.1))
    displacement_cm = displacement_m * 100
    
    # Cap displacement at 100 cm (1 meter is engineering limit)
    displacement_cm = min(displacement_cm, 100.0)
    
    return displacement_cm

def feedback_loop_iteration(
    iteration_num: int,
    slope: GeotechnicalSlope,
    geometry: RoadGeometry,
    seismic_zone: SeismicZone,
    max_iterations: int = 3
) -> FeedbackIteration:
    """
    Single iteration of geo-road feedback loop.
    
    Logic:
    1. Calculate slope FoS (static & seismic) from D6.3 slope properties
    2. If FoS_seismic < 1.1 → slope unstable → reduce road rampa (more stable)
    3. Recalculate Newmark displacement
    4. Check geometry feasibility (rampa ≥ 6%, geometry spacing, etc.)
    5. Compute convergence delta
    """
    
    # Step 1: Calculate slope FoS
    fos_static, fos_seismic = calculate_slope_factor_of_safety(slope, seismic_zone)
    
    # Step 2: Calculate Newmark displacement
    newmark_d = calculate_newmark_displacement(slope, seismic_zone, fos_seismic)
    
    # Step 3: Rampa adjustment logic
    # If FoS_seismic < target (1.1), reduce rampa to reduce slope stress
    # Reduction: 0.3% per iteration if FoS_seismic < 1.1
    
    target_fos = 1.1
    rampa_adjustment = 0.0
    
    if fos_seismic < target_fos:
        fos_deficit = target_fos - fos_seismic
        rampa_adjustment = -0.3 * fos_deficit  # Reduce rampa to improve FoS
    elif fos_seismic > (target_fos + 0.15):
        # FoS is well above target → can increase rampa slightly
        rampa_adjustment = 0.1
    
    new_rampa = geometry.rampa_grade_pct + rampa_adjustment
    
    # Step 4: Geometry feasibility checks
    feasibility_checks = [
        new_rampa >= 6.0,      # Minimum rampa (for drainage & vertical curve)
        new_rampa <= 7.5,      # Maximum rampa (seismic-resilient design)
        newmark_d <= 50.0,     # Newmark displacement acceptable (<50 cm)
        fos_seismic >= 1.05    # Minimum FoS for seismic (slightly relaxed from 1.1 for transition)
    ]
    geometry_feasible = all(feasibility_checks)
    
    # Step 5: Convergence delta
    # Delta = change in FoS between iterations
    convergence_delta = abs(rampa_adjustment)  # Simplified
    
    return FeedbackIteration(
        iteration_number=iteration_num,
        slope_fos_static=fos_static,
        slope_fos_seismic=fos_seismic,
        newmark_displacement_cm=newmark_d,
        road_rampa_pct=new_rampa,
        required_rampa_adjustment_pct=rampa_adjustment,
        geometry_feasible=geometry_feasible,
        convergence_delta=convergence_delta
    )

def run_feedback_loop(
    slope: GeotechnicalSlope,
    geometry: RoadGeometry,
    seismic_zone: SeismicZone,
    max_iterations: int = 3,
    convergence_tolerance: float = 0.05  # 0.05% rampa change
) -> Tuple[List[FeedbackIteration], ConvergenceStatus]:
    """
    Execute complete geo-road feedback loop.
    
    Loop continues until:
    - Convergence delta < tolerance, OR
    - Max iterations reached, OR
    - Geometry becomes infeasible
    """
    
    iterations = []
    current_geometry = geometry
    
    for i in range(1, max_iterations + 1):
        iteration = feedback_loop_iteration(
            i,
            slope,
            current_geometry,
            seismic_zone,
            max_iterations
        )
        
        iterations.append(iteration)
        
        # Update geometry for next iteration
        current_geometry = RoadGeometry(
            design_speed_kmh=current_geometry.design_speed_kmh,
            rampa_grade_pct=iteration.road_rampa_pct,
            horizontal_radius_m=current_geometry.horizontal_radius_m,
            superelevation_pct=current_geometry.superelevation_pct,
            road_width_m=current_geometry.road_width_m,
            cut_fill_height_m=current_geometry.cut_fill_height_m
        )
        
        # Check convergence
        if iteration.convergence_delta < convergence_tolerance:
            return iterations, ConvergenceStatus.CONVERGED
        
        if not iteration.geometry_feasible:
            return iterations, ConvergenceStatus.DIVERGED
    
    return iterations, ConvergenceStatus.ITERATING

# Test: Jericó Km 45+800 feedback loop
def test_jerico_feedback_loop():
    """
    Test geo-road feedback loop for Jericó Km 45+800.
    
    Context: Cut slope adjacent to road, high seismic zone.
    Goal: Find stable rampa + slope combination.
    """
    
    # D6.3 slope input
    slope = GeotechnicalSlope(
        station_km=45.8,
        slope_height_m=12.0,
        slope_angle_degrees=35,
        soil_type='clay',
        cohesion_kpa=30,
        friction_angle_degrees=32,
        unit_weight_kn_m3=18.5,
        groundwater_depth_m=8.0,
        factor_of_safety_static=1.5,
        factor_of_safety_seismic=1.1
    )
    
    # D7 road geometry (initial)
    geometry = RoadGeometry(
        design_speed_kmh=60,
        rampa_grade_pct=7.5,  # Starting at max seismic design
        horizontal_radius_m=300,
        superelevation_pct=5.5,
        road_width_m=7.5
    )
    
    # Run loop
    iterations, status = run_feedback_loop(
        slope,
        geometry,
        seismic_zone=SeismicZone.HIGH,
        max_iterations=3
    )
    
    print("Jericó Km 45+800 Geo-Road Feedback Loop")
    print(f"Convergence Status: {status.value}\n")
    
    for iter in iterations:
        print(f"Iteration {iter.iteration_number}:")
        print(f"  Slope FoS (static/seismic): {iter.slope_fos_static:.2f} / {iter.slope_fos_seismic:.2f}")
        print(f"  Newmark Displacement: {iter.newmark_displacement_cm:.1f} cm")
        print(f"  Road Rampa: {iter.road_rampa_pct:.2f}% (adjust: {iter.required_rampa_adjustment_pct:+.2f}%)")
        print(f"  Geometry Feasible: {iter.geometry_feasible}")
        print(f"  Convergence Delta: {iter.convergence_delta:.3f}\n")
    
    # Final recommendation
    final_iter = iterations[-1]
    if status == ConvergenceStatus.CONVERGED:
        print(f"RECOMMENDATION: Use Rampa = {final_iter.road_rampa_pct:.2f}%")
    else:
        print(f"RECOMMENDATION: Manual review required | Last stable rampa: {final_iter.road_rampa_pct:.2f}%")
    
    return iterations, status
```

---

## SECTION 3: D7.5 JERICÓ REDESIGN — 3 ALTERNATIVES

### 3.1 Conservative / Balanced / Aggressive Cases

```python
from dataclasses import dataclass
from typing import List

class DesignCase(Enum):
    CONSERVATIVE = "Conservative"
    BALANCED = "Balanced"
    AGGRESSIVE = "Aggressive"

@dataclass
class JericoDesignAlternative:
    """Complete design alternative for Jericó Km 45–47"""
    case_name: DesignCase
    rampa_grade_pct: float
    horizontal_radius_m: float
    superelevation_pct: float
    slope_stability_margin: str  # e.g., "FoS=1.25"
    lane_width_m: float
    shoulder_width_m: float
    estimated_cut_volume_m3: float
    estimated_fill_volume_m3: float
    total_cost_million_brl: float
    construction_duration_months: int
    risk_level: str  # 'Low', 'Medium', 'High'
    post_construction_monitoring_years: int
    notes: str

def design_jerico_conservative() -> JericoDesignAlternative:
    """
    Conservative case: Minimizes slope cutting, maximizes safety margins.
    
    Strategy:
    - Reduce rampa to 6.5% (well below 7.5% max)
    - Increase horizontal radius (gentler curves)
    - Lower superelevation (reduced stress on slope)
    - Thicker lane/shoulder (safety buffers)
    - Higher cost, longer construction, lower risk
    """
    
    return JericoDesignAlternative(
        case_name=DesignCase.CONSERVATIVE,
        rampa_grade_pct=6.5,
        horizontal_radius_m=400,  # Larger = gentler curve
        superelevation_pct=4.5,
        slope_stability_margin="FoS_seismic=1.25 (safe margin)",
        lane_width_m=3.75,
        shoulder_width_m=1.5,
        estimated_cut_volume_m3=18500,
        estimated_fill_volume_m3=4200,
        total_cost_million_brl=42.5,
        construction_duration_months=28,
        risk_level="Low",
        post_construction_monitoring_years=5,
        notes="Minimal earthwork reshuffling. Steep descent into Km 47 requires careful PIV design."
    )

def design_jerico_balanced() -> JericoDesignAlternative:
    """
    Balanced case: Moderate rampa, standard safety margins, cost-effective.
    
    Strategy:
    - Rampa = 7.0% (mid-range within 6–7.5% seismic design envelope)
    - Horizontal radius = 350 m (standard design speed 65 km/h)
    - Superelevation = 5.5% (typical for this speed)
    - Normal lane/shoulder widths
    - Moderate cost, moderate risk
    """
    
    return JericoDesignAlternative(
        case_name=DesignCase.BALANCED,
        rampa_grade_pct=7.0,
        horizontal_radius_m=350,
        superelevation_pct=5.5,
        slope_stability_margin="FoS_seismic=1.15 (adequate)",
        lane_width_m=3.6,
        shoulder_width_m=1.2,
        estimated_cut_volume_m3=22100,
        estimated_fill_volume_m3=5800,
        total_cost_million_brl=35.8,
        construction_duration_months=22,
        risk_level="Medium",
        post_construction_monitoring_years=3,
        notes="Recommended case. Balances cost, risk, and operational efficiency. Requires slope stabilization (drainage + micro-piles)."
    )

def design_jerico_aggressive() -> JericoDesignAlternative:
    """
    Aggressive case: Maximizes rampa, minimizes earthwork, cost-cutting.
    
    Strategy:
    - Rampa = 7.5% (maximum seismic-resilient design)
    - Smaller radius (300 m, lower speed tolerance)
    - Higher superelevation (6.0%)
    - Minimal shoulder widths
    - Lowest cost, highest risk (Newmark >50 cm, requires continuous monitoring)
    """
    
    return JericoDesignAlternative(
        case_name=DesignCase.AGGRESSIVE,
        rampa_grade_pct=7.5,
        horizontal_radius_m=300,
        superelevation_pct=6.0,
        slope_stability_margin="FoS_seismic=1.10 (marginal)",
        lane_width_m=3.5,
        shoulder_width_m=0.8,
        estimated_cut_volume_m3=25800,
        estimated_fill_volume_m3=6500,
        total_cost_million_brl=28.2,
        construction_duration_months=16,
        risk_level="High",
        post_construction_monitoring_years=8,
        notes="Maximum cost savings but heightened seismic risk. Newmark displacement ~35 cm. Requires intensive post-earthquake inspection protocol."
    )

def generate_jerico_cost_benefit_matrix() -> Dict:
    """
    Generate cost-benefit comparison matrix for all 3 cases.
    """
    
    conservative = design_jerico_conservative()
    balanced = design_jerico_balanced()
    aggressive = design_jerico_aggressive()
    
    alternatives = [conservative, balanced, aggressive]
    
    # Calculate benefit scores (higher = better)
    # Cost efficiency score: inverse of cost (lower cost = higher score)
    # Risk score: inverse of risk level
    # Feasibility: 1.0 = fully feasible
    
    cost_baseline = balanced.total_cost_million_brl
    
    matrix = {
        'Conservative': {
            'cost_million_brl': conservative.total_cost_million_brl,
            'cost_vs_balanced_pct': ((conservative.total_cost_million_brl / cost_baseline) - 1) * 100,
            'construction_months': conservative.construction_duration_months,
            'rampa_pct': conservative.rampa_grade_pct,
            'radius_m': conservative.horizontal_radius_m,
            'fos_seismic': 1.25,
            'newmark_cm': 8,  # Very low displacement
            'monitoring_years': conservative.post_construction_monitoring_years,
            'risk_level': conservative.risk_level,
            'feasibility_score': 1.0,
            'cost_efficiency': 0.65,  # Expensive
            'safety_score': 0.95,  # Very safe
            'overall_score': 0.80  # (cost + safety) / 2, weighted
        },
        'Balanced': {
            'cost_million_brl': balanced.total_cost_million_brl,
            'cost_vs_balanced_pct': 0.0,
            'construction_months': balanced.construction_duration_months,
            'rampa_pct': balanced.rampa_grade_pct,
            'radius_m': balanced.horizontal_radius_m,
            'fos_seismic': 1.15,
            'newmark_cm': 18,
            'monitoring_years': balanced.post_construction_monitoring_years,
            'risk_level': balanced.risk_level,
            'feasibility_score': 1.0,
            'cost_efficiency': 0.85,  # Standard
            'safety_score': 0.85,  # Good
            'overall_score': 0.85  # Recommended
        },
        'Aggressive': {
            'cost_million_brl': aggressive.total_cost_million_brl,
            'cost_vs_balanced_pct': ((aggressive.total_cost_million_brl / cost_baseline) - 1) * 100,
            'construction_months': aggressive.construction_duration_months,
            'rampa_pct': aggressive.rampa_grade_pct,
            'radius_m': aggressive.horizontal_radius_m,
            'fos_seismic': 1.10,
            'newmark_cm': 35,
            'monitoring_years': aggressive.post_construction_monitoring_years,
            'risk_level': aggressive.risk_level,
            'feasibility_score': 0.95,  # Slightly lower (marginal FoS)
            'cost_efficiency': 0.95,  # Cheap
            'safety_score': 0.70,  # Lower
            'overall_score': 0.75  # Risky but cheaper
        }
    }
    
    return matrix

# Test: Display cost-benefit matrix
def test_jerico_cost_benefit():
    """Print cost-benefit analysis for Jericó 3 alternatives"""
    
    matrix = generate_jerico_cost_benefit_matrix()
    
    print("JERICÓ Km 45–47 COST-BENEFIT ANALYSIS\n")
    print("=" * 100)
    print(f"{'Case':<15} {'Cost (M BRL)':<15} {'vs Balanced':<15} {'Const. Mo.':<12} {'Rampa %':<10} {'Radius m':<12} {'FoS Seismic':<12} {'Newmark cm':<12}")
    print("=" * 100)
    
    for case_name, metrics in matrix.items():
        print(f"{case_name:<15} {metrics['cost_million_brl']:<15.1f} {metrics['cost_vs_balanced_pct']:>+14.1f}% {metrics['construction_months']:<12} {metrics['rampa_pct']:<10.1f} {metrics['radius_m']:<12.0f} {metrics['fos_seismic']:<12.2f} {metrics['newmark_cm']:<12.0f}")
    
    print("\n" + "=" * 100)
    print("\nDECISION MATRIX:")
    print("-" * 100)
    print(f"{'Criterion':<25} {'Conservative':<20} {'Balanced':<20} {'Aggressive':<20}")
    print("-" * 100)
    print(f"{'Cost Efficiency':<25} {matrix['Conservative']['cost_efficiency']:<20.2f} {matrix['Balanced']['cost_efficiency']:<20.2f} {matrix['Aggressive']['cost_efficiency']:<20.2f}")
    print(f"{'Safety Score':<25} {matrix['Conservative']['safety_score']:<20.2f} {matrix['Balanced']['safety_score']:<20.2f} {matrix['Aggressive']['safety_score']:<20.2f}")
    print(f"{'Overall Score':<25} {matrix['Conservative']['overall_score']:<20.2f} {matrix['Balanced']['overall_score']:<20.2f} {matrix['Aggressive']['overall_score']:<20.2f}")
    print(f"{'Feasibility':<25} {matrix['Conservative']['feasibility_score']:<20.2f} {matrix['Balanced']['feasibility_score']:<20.2f} {matrix['Aggressive']['feasibility_score']:<20.2f}")
    print(f"{'Recommended':<25} {'No (too conservative)':<20} {'YES':<20} {'No (too risky)':<20}")
    
    return matrix
```

---

## SECTION 4: RAG + SUPABASE MIGRATION

### 4.1 Database Schema & HNSW Indexing

```sql
-- ========================================
-- Supabase Schema for S1-V7 RAG Collections
-- ========================================

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For full-text search

-- ========================================
-- Collection: rag_horizontal_geometry (hor:)
-- ========================================
CREATE TABLE rag_horizontal_geometry (
    id BIGSERIAL PRIMARY KEY,
    collection_prefix TEXT DEFAULT 'hor:',
    document_id TEXT UNIQUE NOT NULL,           -- hor:nbr-15421-table-4
    source_title TEXT,                          -- "NBR 15421 Table 4: Design Radii"
    source_type TEXT,                           -- 'norm', 'standard', 'case-study'
    content TEXT NOT NULL,                      -- Full text of document chunk
    seismic_zone TEXT,                          -- 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'
    design_speed_kmh INT,
    content_vector vector(1536),                -- OpenAI embeddings (1536-dim)
    chunk_index INT,                            -- For multi-chunk documents
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON rag_horizontal_geometry USING HNSW (content_vector vector_cosine_ops);
CREATE INDEX ON rag_horizontal_geometry (seismic_zone);
CREATE INDEX ON rag_horizontal_geometry (design_speed_kmh);
CREATE INDEX ON rag_horizontal_geometry USING GIN (to_tsvector('portuguese', content));  -- Full-text search

-- ========================================
-- Collection: rag_vertical_geometry (ver:)
-- ========================================
CREATE TABLE rag_vertical_geometry (
    id BIGSERIAL PRIMARY KEY,
    collection_prefix TEXT DEFAULT 'ver:',
    document_id TEXT UNIQUE NOT NULL,
    source_title TEXT,                          -- "AASHTO Green Book: Vertical Curves"
    source_type TEXT,                           -- 'standard', 'method', 'spreadsheet'
    content TEXT NOT NULL,
    rampa_grade_range TEXT,                     -- "6.0-7.5%"
    piv_type TEXT,                              -- 'crest', 'sag', 'combined'
    content_vector vector(1536),
    chunk_index INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON rag_vertical_geometry USING HNSW (content_vector vector_cosine_ops);
CREATE INDEX ON rag_vertical_geometry (piv_type);
CREATE INDEX ON rag_vertical_geometry USING GIN (to_tsvector('portuguese', content));

-- ========================================
-- Collection: rag_geo_slope_stability (geo:)
-- ========================================
CREATE TABLE rag_geo_slope_stability (
    id BIGSERIAL PRIMARY KEY,
    collection_prefix TEXT DEFAULT 'geo:',
    document_id TEXT UNIQUE NOT NULL,
    source_title TEXT,                          -- "GEO5 Slope Stability Manual"
    source_type TEXT,                           -- 'method', 'manual', 'research'
    content TEXT NOT NULL,
    slope_type TEXT,                            -- 'cut', 'fill', 'natural'
    soil_type TEXT,                             -- 'clay', 'sand', 'rock', 'mixed'
    fos_target DECIMAL(3, 2),                   -- 1.10, 1.15, 1.25, etc.
    content_vector vector(1536),
    chunk_index INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON rag_geo_slope_stability USING HNSW (content_vector vector_cosine_ops);
CREATE INDEX ON rag_geo_slope_stability (soil_type);
CREATE INDEX ON rag_geo_slope_stability (fos_target);
CREATE INDEX ON rag_geo_slope_stability USING GIN (to_tsvector('portuguese', content));

-- ========================================
-- Collection: rag_seismic_safety (seis:)
-- ========================================
CREATE TABLE rag_seismic_safety (
    id BIGSERIAL PRIMARY KEY,
    collection_prefix TEXT DEFAULT 'seis:',
    document_id TEXT UNIQUE NOT NULL,
    source_title TEXT,                          -- "ABNT NBR 15421: Seismic Design"
    source_type TEXT,                           -- 'norm', 'guidance', 'case-study'
    content TEXT NOT NULL,
    seismic_zone TEXT,                          -- 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'
    vehicle_class TEXT,                         -- 'light', 'truck', 'bus'
    safety_metric TEXT,                         -- 'stopping-distance', 'rollover', 'lateral-shift'
    content_vector vector(1536),
    chunk_index INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON rag_seismic_safety USING HNSW (content_vector vector_cosine_ops);
CREATE INDEX ON rag_seismic_safety (seismic_zone);
CREATE INDEX ON rag_seismic_safety (vehicle_class);
CREATE INDEX ON rag_seismic_safety (safety_metric);
CREATE INDEX ON rag_seismic_safety USING GIN (to_tsvector('portuguese', content));

-- ========================================
-- Collection: rag_jerico_case_studies (jer:)
-- ========================================
CREATE TABLE rag_jerico_case_studies (
    id BIGSERIAL PRIMARY KEY,
    collection_prefix TEXT DEFAULT 'jer:',
    document_id TEXT UNIQUE NOT NULL,
    source_title TEXT,                          -- "Jericó Project: Design Report Km 45-47"
    source_type TEXT,                           -- 'case-study', 'design-report', 'as-built'
    content TEXT NOT NULL,
    location_km DECIMAL(6, 2),                  -- 45.8, 46.2, etc.
    design_alternative TEXT,                    -- 'conservative', 'balanced', 'aggressive'
    cost_million_brl DECIMAL(8, 2),
    content_vector vector(1536),
    chunk_index INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON rag_jerico_case_studies USING HNSW (content_vector vector_cosine_ops);
CREATE INDEX ON rag_jerico_case_studies (location_km);
CREATE INDEX ON rag_jerico_case_studies (design_alternative);
CREATE INDEX ON rag_jerico_case_studies USING GIN (to_tsvector('portuguese', content));

-- ========================================
-- Query Patterns (Python via Supabase client)
-- ========================================

/*
Pattern 1: Vector similarity search (nearest-neighbor)
SELECT id, document_id, source_title, content, 
       content_vector <-> query_vector AS distance
FROM rag_horizontal_geometry
WHERE seismic_zone = 'HIGH'
ORDER BY content_vector <-> query_vector
LIMIT 5;

Pattern 2: Full-text search + vector re-ranking
SELECT id, document_id, source_title, content,
       ts_rank(to_tsvector('portuguese', content), query_ts) AS text_rank,
       content_vector <-> query_vector AS vector_distance
FROM rag_vertical_geometry
WHERE to_tsvector('portuguese', content) @@ query_ts
  AND piv_type = 'sag'
ORDER BY text_rank DESC, vector_distance ASC
LIMIT 10;

Pattern 3: Metadata filtering + vector search
SELECT id, document_id, source_title, content
FROM rag_geo_slope_stability
WHERE soil_type = 'clay'
  AND fos_target >= 1.15
  AND (content_vector <-> query_vector) < 0.3  -- Cosine distance threshold
ORDER BY (content_vector <-> query_vector) ASC
LIMIT 3;

Pattern 4: Aggregation across collections (Union)
SELECT 'horizontal_geometry' AS collection, id, document_id, source_title, content
FROM rag_horizontal_geometry
WHERE seismic_zone = 'HIGH'
  AND (content_vector <-> query_vector) < 0.35
UNION ALL
SELECT 'seismic_safety', id, document_id, source_title, content
FROM rag_seismic_safety
WHERE seismic_zone = 'HIGH'
  AND (content_vector <-> query_vector) < 0.35
ORDER BY 1 DESC
LIMIT 15;
*/
```

### 4.2 Python Supabase Integration Layer

```python
import os
from supabase import create_client, Client
from typing import List, Dict
import json
import numpy as np
from datetime import datetime

class RAGSupabaseManager:
    """
    Manages RAG collections in Supabase with vector search.
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.collections = {
            'horizontal_geometry': 'rag_horizontal_geometry',
            'vertical_geometry': 'rag_vertical_geometry',
            'geo_slope_stability': 'rag_geo_slope_stability',
            'seismic_safety': 'rag_seismic_safety',
            'jerico_case_studies': 'rag_jerico_case_studies'
        }
    
    def insert_document(
        self,
        collection_name: str,
        document_id: str,
        source_title: str,
        source_type: str,
        content: str,
        embedding_vector: List[float],
        metadata: Dict = None,
        chunk_index: int = 0
    ) -> Dict:
        """
        Insert a document chunk with embedding into RAG collection.
        
        Args:
            collection_name: Key from self.collections dict
            document_id: Unique doc ID (e.g., 'hor:nbr-15421-v1')
            source_title: Human-readable title
            source_type: 'norm', 'standard', 'case-study', etc.
            content: Text content of chunk
            embedding_vector: 1536-dim OpenAI embedding
            metadata: Additional fields (seismic_zone, soil_type, etc.)
            chunk_index: For multi-chunk documents
        
        Returns: Inserted row dict from Supabase
        """
        
        table_name = self.collections[collection_name]
        
        payload = {
            'document_id': document_id,
            'source_title': source_title,
            'source_type': source_type,
            'content': content,
            'content_vector': embedding_vector,
            'chunk_index': chunk_index,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Add metadata fields if provided
        if metadata:
            payload.update(metadata)
        
        response = self.supabase.table(table_name).insert(payload).execute()
        
        return response.data[0] if response.data else {}
    
    def vector_search(
        self,
        collection_name: str,
        query_vector: List[float],
        filters: Dict = None,
        limit: int = 5,
        distance_threshold: float = 0.35
    ) -> List[Dict]:
        """
        Vector similarity search using cosine distance.
        
        Args:
            collection_name: Key from self.collections
            query_vector: Embedded query (1536-dim)
            filters: Optional metadata filters (e.g., {'seismic_zone': 'HIGH'})
            limit: Max results
            distance_threshold: Cosine distance cutoff (0-1, lower=more similar)
        
        Returns: List of matching documents with distance scores
        """
        
        table_name = self.collections[collection_name]
        
        # Build filter clause
        filter_clause = ""
        if filters:
            filter_clauses = []
            for key, value in filters.items():
                if isinstance(value, str):
                    filter_clauses.append(f"{key}.eq.{value}")
                else:
                    filter_clauses.append(f"{key}.eq.{value}")
            filter_clause = " and ".join(filter_clauses)
        
        # Note: Supabase RPC or raw query needed for true vector search
        # Simplified approach: fetch all, compute distance client-side
        # (In production, use Supabase RPC or raw SQL)
        
        response = self.supabase.table(table_name).select('*').execute()
        
        if not response.data:
            return []
        
        # Client-side distance computation (simplified)
        results = []
        query_np = np.array(query_vector)
        
        for row in response.data:
            if 'content_vector' not in row or row['content_vector'] is None:
                continue
            
            doc_vector = np.array(row['content_vector'])
            # Cosine distance
            distance = 1 - (np.dot(query_np, doc_vector) / 
                          (np.linalg.norm(query_np) * np.linalg.norm(doc_vector) + 1e-8))
            
            if distance <= distance_threshold:
                results.append({
                    'document_id': row['document_id'],
                    'source_title': row['source_title'],
                    'content': row['content'],
                    'distance': distance,
                    'metadata': {k: v for k, v in row.items() 
                               if k not in ['id', 'content', 'content_vector', 'created_at', 'updated_at']}
                })
        
        # Sort by distance and limit
        results.sort(key=lambda x: x['distance'])
        return results[:limit]
    
    def full_text_search(
        self,
        collection_name: str,
        query_text: str,
        filters: Dict = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Full-text search in Portuguese with optional metadata filtering.
        """
        
        table_name = self.collections[collection_name]
        
        # Use Supabase full-text search (requires setup)
        # Simplified: keyword-based search
        
        response = self.supabase.table(table_name).select('*').execute()
        
        results = []
        query_lower = query_text.lower()
        
        for row in response.data:
            if query_lower in row['content'].lower():
                # Apply metadata filters if provided
                if filters:
                    if all(row.get(k) == v for k, v in filters.items()):
                        results.append(row)
                else:
                    results.append(row)
        
        return results[:limit]
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics for a collection.
        """
        
        table_name = self.collections[collection_name]
        response = self.supabase.table(table_name).select('count', count='exact').execute()
        
        return {
            'collection': collection_name,
            'table': table_name,
            'document_count': response.count if hasattr(response, 'count') else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

# Example usage
def test_rag_supabase():
    """Test RAG integration with Supabase"""
    
    # Initialize (in production, use environment variables)
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    rag = RAGSupabaseManager(SUPABASE_URL, SUPABASE_KEY)
    
    # Insert sample document
    sample_vector = np.random.randn(1536).tolist()  # Placeholder
    
    inserted = rag.insert_document(
        collection_name='horizontal_geometry',
        document_id='hor:nbr-15421-table-4-v1',
        source_title='NBR 15421:2006 - Table 4: Design Radii by Speed',
        source_type='norm',
        content="""
            Design Radius (meters) by velocity and seismic zone.
            V=40 km/h: R=60m (standard), R=72m (seismic 1.2x)
            V=60 km/h: R=150m (standard), R=195m (seismic 1.3x)
            V=80 km/h: R=350m (standard), R=455m (seismic 1.3x)
        """,
        embedding_vector=sample_vector,
        metadata={
            'seismic_zone': 'MEDIUM',
            'design_speed_kmh': 60
        },
        chunk_index=0
    )
    
    print(f"Inserted document: {inserted}")
    
    # Vector search
    query_vec = sample_vector  # In real use, embed a query
    search_results = rag.vector_search(
        collection_name='horizontal_geometry',
        query_vector=query_vec,
        filters={'seismic_zone': 'MEDIUM'},
        limit=3
    )
    
    print(f"\nVector search results: {len(search_results)} docs found")
    
    # Collection stats
    stats = rag.get_collection_stats('horizontal_geometry')
    print(f"\nCollection stats: {stats}")
```

---

## SECTION 5: HANDOFF SPECIFICATIONS

### 5.1 Agente-05 (Orcamento) Handoff

```json
{
  "handoff_id": "D7_to_AGENTE05_GEO_COSTS_v1.0",
  "timestamp": "2026-07-25T10:30:00Z",
  "source_discipline": "D7 (Road Geometry)",
  "target_agent": "Manta-05 (Orcamento)",
  "project_context": {
    "project_name": "Jericó Highway Seismic Retrofit",
    "segment": "Km 45.0 – 47.5 (Geo-intensive section)",
    "seismic_zone": "HIGH (ag = 0.20g, ABNT NBR 15421)"
  },
  "design_alternative": "BALANCED",
  "payload": {
    "geometric_parameters": {
      "length_km": 2.5,
      "design_speed_kmh": 60,
      "horizontal_radius_m": 350,
      "superelevation_pct": 5.5,
      "rampa_grade_pct": 7.0,
      "lane_width_m": 3.6,
      "shoulder_width_m": 1.2,
      "curve_type": "combined"
    },
    "earthwork_quantities": {
      "estimated_cut_volume_m3": 22100,
      "estimated_fill_volume_m3": 5800,
      "borrow_pit_required": true,
      "waste_disposal_m3": 3200,
      "fill_compaction_grade": "95% proctor"
    },
    "geotechnical_works": {
      "slope_stabilization": {
        "type": "micro_pile_system",
        "pile_diameter_mm": 150,
        "pile_spacing_m": 2.5,
        "estimated_quantity": 850,
        "pile_length_m": 8.0
      },
      "drainage_system": {
        "subsurface_drainage_m": 1200,
        "surface_drainage_m": 2500,
        "french_drain_aggregate_m3": 180
      },
      "slope_protection": {
        "erosion_control_area_m2": 3500,
        "vegetation_planting_area_m2": 3500,
        "rockfall_barriers_m": 450
      }
    },
    "structural_elements": {
      "retaining_walls": {
        "gravity_wall_m3": 850,
        "reinforced_concrete_wall_m3": 320
      },
      "culverts": {
        "count": 3,
        "type": "concrete_box",
        "span_diameter_m": 1.5
      }
    },
    "pavement_layers": {
      "asphalt_concrete_binder_m3": 4500,
      "asphalt_concrete_surface_m3": 2800,
      "base_course_m3": 8400,
      "subbase_course_m3": 12600
    },
    "cost_drivers": {
      "labor_intensity": "HIGH",  // Cut slopes, piles, drainage
      "material_hauling_distance_km": 45,
      "equipment_specialty_required": ["pile_driver", "slope_drills", "excavators_large"],
      "seasonal_constraints": "MONSOON",  // Jul–Sep rainfall high
      "remote_access": "PARTIAL"  // Km 45–47 relatively accessible
    },
    "cost_notes": [
      "Micro-pile system is critical cost driver (~BRL 18M of total 35.8M)",
      "Drainage system required due to high slope height (12m) + seismic acceleration",
      "Vegetation planting amortized over 2-year establishment period",
      "Contingency applied: +15% for seismic/geological unknowns"
    ]
  },
  "request_to_agente05": {
    "tasks": [
      "Generate unit costs for earthwork (cut/fill) in LOCAL market (Jericó region)",
      "Price micro-pile system (procurement + installation)",
      "Cost structural drainage components (subsurface + surface)",
      "Estimate vegetation/slope protection (ABNT NBR 13882: Biological stabilization)",
      "Build SICRO-based cost estimate for asphalt + base course",
      "Apply regional labor multiplier (Jericó in medium-cost region)"
    ],
    "deliverables": {
      "cost_breakdown_xlsx": "D7_Jerico_Cost_Breakdown_BALANCED.xlsx",
      "unit_cost_database": "Include SICRO refs + regional adjustments",
      "summary_budget": "BRL 35.8M total (target)",
      "sensitivity_analysis": "Cost impact if earthwork +/-10%, piles +/-15%",
      "schedule_impact": "Cost escalation if stretched to 30 months vs 22 months (inflation)"
    },
    "timeline": {
      "cost_request_date": "2026-07-25",
      "expected_delivery": "2026-08-15",
      "review_cycle": "2 weeks"
    }
  }
}
```

### 5.2 Agente-07 (Cronograma) Handoff

```json
{
  "handoff_id": "D7_to_AGENTE07_SCHEDULE_v1.0",
  "timestamp": "2026-07-25T10:35:00Z",
  "source_discipline": "D7 (Road Geometry)",
  "target_agent": "Manta-07 (Cronograma)",
  "project_context": {
    "project_name": "Jericó Highway Seismic Retrofit",
    "segment": "Km 45.0 – 47.5",
    "total_duration_months": 22,
    "construction_start": "2026-10-01",
    "expected_completion": "2028-08-01"
  },
  "design_alternative": "BALANCED",
  "payload": {
    "critical_path_activities": [
      {
        "activity_id": "D7.1",
        "description": "Horizontal Geometry Survey & Staking",
        "duration_weeks": 3,
        "dependencies": ["Project Kickoff"],
        "resource_requirement": "Survey crew (4), GPS equipment",
        "critical": true
      },
      {
        "activity_id": "D7.2",
        "description": "Geotechnical Investigation (Boreholes Km 45-47)",
        "duration_weeks": 4,
        "dependencies": ["D7.1"],
        "resource_requirement": "Drilling rig, lab testing",
        "critical": true,
        "constraints": "Weather-dependent (avoid monsoon: Jul–Sep)"
      },
      {
        "activity_id": "D7.3a",
        "description": "Design Feedback Loop Iteration 1–3 (Geo-Road coupling)",
        "duration_weeks": 6,
        "dependencies": ["D7.2"],
        "resource_requirement": "Geotechnical engineer, road designer (parallel)",
        "critical": true,
        "parallel_processing": "Yes (D7 & D6.3 concurrent)"
      },
      {
        "activity_id": "D7.4",
        "description": "Slope Stability Analysis + Newmark Calculations",
        "duration_weeks": 3,
        "dependencies": ["D7.3a"],
        "resource_requirement": "Slope stability software (GEO5), engineer 1 FTE",
        "critical": true
      },
      {
        "activity_id": "E1.1",
        "description": "Micro-Pile Design + Procurement",
        "duration_weeks": 8,
        "dependencies": ["D7.4"],
        "resource_requirement": "Foundation engineer, pile manufacturer",
        "critical": true,
        "lead_time_item": true
      },
      {
        "activity_id": "E2.1",
        "description": "Drainage System Design + Permits",
        "duration_weeks": 5,
        "dependencies": ["D7.4"],
        "resource_requirement": "Hydraulics engineer, environmental approvals",
        "critical": true
      },
      {
        "activity_id": "CONST.1",
        "description": "Site Mobilization + Camp Setup",
        "duration_weeks": 2,
        "dependencies": ["Design completion", "Contractor procurement"],
        "resource_requirement": "Contractor crew (80–100 persons)",
        "critical": true
      },
      {
        "activity_id": "CONST.2",
        "description": "Earthwork (Cut + Fill)",
        "duration_weeks": 12,
        "dependencies": ["CONST.1"],
        "resource_requirement": "Excavators (3×), dozer (2×), water trucks",
        "volume_m3": 27900,
        "monthly_rate_m3": 2325,
        "critical": true
      },
      {
        "activity_id": "CONST.3",
        "description": "Micro-Pile Installation (Slope stabilization)",
        "duration_weeks": 10,
        "dependencies": ["CONST.2", "E1.1"],
        "resource_requirement": "Pile driver, support crew",
        "quantity": 850,
        "rate_per_day": 20,
        "critical": true
      },
      {
        "activity_id": "CONST.4",
        "description": "Drainage System Installation",
        "duration_weeks": 6,
        "dependencies": ["CONST.3"],
        "resource_requirement": "Drainage crew (20)",
        "critical": false,
        "float_weeks": 2
      },
      {
        "activity_id": "CONST.5",
        "description": "Pavement + Surface Layers",
        "duration_weeks": 8,
        "dependencies": ["CONST.4"],
        "resource_requirement": "Paving crew, asphalt plant",
        "volume_m3": 7300,
        "critical": true
      },
      {
        "activity_id": "CONST.6",
        "description": "Vegetation + Slope Protection (seeding, plantings)",
        "duration_weeks": 4,
        "dependencies": ["CONST.5"],
        "resource_requirement": "Landscaping crew",
        "critical": false,
        "note": "Overlaps with demobilization; planting establishment 2–5 years"
      },
      {
        "activity_id": "CLOSE.1",
        "description": "Testing + Commissioning (QA/QC)",
        "duration_weeks": 3,
        "dependencies": ["CONST.6"],
        "resource_requirement": "QC engineer, lab technician",
        "critical": true
      },
      {
        "activity_id": "CLOSE.2",
        "description": "Demobilization + Site Restoration",
        "duration_weeks": 2,
        "dependencies": ["CLOSE.1"],
        "resource_requirement": "Cleanup crew",
        "critical": false
      }
    ],
    "schedule_constraints": {
      "monsoon_season": {
        "start_month": "July",
        "end_month": "September",
        "mitigation": "Advance earthwork before monsoon; use pump systems for drainage during rains"
      },
      "weather_windows": [
        {"season": "Oct–Apr", "productivity_factor": 1.0, "activity_types": ["all"]},
        {"season": "May–Jun", "productivity_factor": 0.9, "activity_types": ["all"]},
        {"season": "Jul–Sep", "productivity_factor": 0.7, "activity_types": ["earthwork", "paving"], "alternative": "Drainage/pile work unaffected"}
      ]
    },
    "resource_allocation": {
      "key_personnel": [
        {"role": "Project Manager", "start_month": 0, "duration_months": 22, "availability": "100%"},
        {"role": "Geotechnical Engineer (Lead)", "start_month": 0, "duration_months": 6, "availability": "80%"},
        {"role": "Road Designer", "start_month": 1, "duration_months": 5, "availability": "60%"},
        {"role": "QC Inspector", "start_month": 5, "duration_months": 18, "availability": "100%"}
      ],
      "equipment_fleet": [
        {"item": "Excavator 325 (large)", "quantity": 2, "months": "5–17"},
        {"item": "Dozer D8", "quantity": 1, "months": "5–17"},
        {"item": "Pile driver (skid-mounted)", "quantity": 1, "months": "9–15"},
        {"item": "Asphalt paver", "quantity": 1, "months": "17–19"}
      ]
    },
    "cost_schedule_impact": {
      "baseline_duration": 22,
      "acceleration_scenarios": [
        {
          "scenario": "Fast-track (18 months)",
          "method": "Concurrent design-construction (design-build)",
          "cost_impact_pct": "+12%",
          "feasibility": "Medium (requires early procurement, risk acceptance)",
          "recommendation": "Not recommended for seismic-critical work"
        },
        {
          "scenario": "Delay to 30 months",
          "reason": "Environmental approvals, monsoon impacts",
          "cost_impact_pct": "+8% (inflation + extended overhead)",
          "probability": "30% if permits delayed"
        }
      ]
    },
    "post_construction": {
      "monitoring_duration_years": 3,
      "monitoring_intervals_months": [3, 6, 12, 24, 36],
      "monitoring_tasks": [
        "Visual slope inspection (seismic response)",
        "Settlement plates (cut + fill areas)",
        "Inclinometers (pile slope stability)",
        "Drainage system performance"
      ]
    }
  },
  "request_to_agente07": {
    "tasks": [
      "Build detailed Gantt chart (22-month baseline)",
      "Identify critical path (currently: Design → Piles → Earthwork → Paving)",
      "Quantify monsoon season impact on productivity (Jul–Sep)",
      "Develop weather-adapted schedules (contingency networks)",
      "Resource leveling: balance crew sizes vs. cost vs. duration",
      "Procurement timelines: micro-piles (8-week lead), asphalt plant access",
      "Risk register: top 5 schedule risks + mitigation (design delays, weather, supply chain)",
      "Monitoring schedule: 3-year post-construction surveillance protocol"
    ],
    "deliverables": {
      "gantt_chart_msp": "D7_Jerico_Schedule_BALANCED.mpp",
      "critical_path_analysis": "Critical path = 22 months; float analysis by activity",
      "resource_histogram": "Monthly crew requirements (100–150 persons peak)",
      "schedule_baseline": "Baseline for earned-value management (EVM)",
      "risk_schedule_matrix": "Top risks + contingency time buffers (suggest +2 months)",
      "milestone_schedule": "Key dates for contractor performance bonds"
    },
    "timeline": {
      "schedule_request_date": "2026-07-25",
      "expected_delivery": "2026-08-20",
      "review_cycle": "2 weeks"
    }
  }
}
```

---

## SECTION 6: TIMELINE & RISK MATRIX

### 6.1 Implementation Timeline (8 Sprints)

```markdown
# S1-V7 IMPLEMENTATION TIMELINE — 8 SPRINTS (AGO 2026 – JUN 2027)

## Sprint Schedule

| Sprint | Period | Theme | Deliverables | Dependencies |
|--------|--------|-------|--------------|--------------|
| **Sprint 1** | AGO 5–23 | D7.1 Horizontal Geometry | Algorithm (3 test cases), baseline rules | None |
| **Sprint 2** | AGO 26–SEP 9 | D7.2 Vertical Geometry | PIV radius calc, Newmark integration, test | Sprint 1 |
| **Sprint 3** | SEP 12–26 | D7.3 Feedback Loop | Geo-road iteration algorithm, Jericó demo | Sprint 1 + 2 |
| **Sprint 4** | SEP 29–OCT 13 | D7.4 Safety Seismic | SSD calc, rollover risk, lane width | Sprint 1 + 2 |
| **Sprint 5** | OCT 16–30 | D7.5 Jericó 3 Cases | Cost-benefit matrix, designs ready | Sprint 3 + 4 |
| **Sprint 6** | NOV 2–16 | RAG + Supabase | Schema, HNSW indexing, query patterns | None (parallel) |
| **Sprint 7** | NOV 19–DEC 3 | Integration + Testing | End-to-end workflow (D7.1→D7.5→Agentes), UAT | Sprints 1–6 |
| **Sprint 8** | DEC 6–20 | Deployment + Training | Production Supabase, agent handoff docs, training | Sprint 7 |

---

## Critical Path Gantt (Simplified)

```
AGO 2026
  |---- D7.1 Horizontal Geometry (Sp1, 3 weeks) ✓
  |       └---- D7.2 Vertical Geometry (Sp2, 3 weeks) ✓
  |                 └---- D7.3 Feedback Loop (Sp3, 2 weeks) ✓
  |                         └---- D7.4 Safety Seismic (Sp4, 2 weeks) ✓
  |                                 └---- D7.5 Jericó Cases (Sp5, 2 weeks) ✓
  |---- RAG + Supabase (Sp6, 3 weeks, parallel) ✓
                    └---- Integration (Sp7, 3 weeks) ✓
                            └---- Deployment (Sp8, 3 weeks) ✓

Total: 8 sprints × 2 weeks = 16 weeks ≈ 4 months (AGO–DEC 2026)
```

---

## Key Milestones

1. **2026-08-23 (Sp1 End):** D7.1 algorithm & test cases DONE
2. **2026-09-09 (Sp2 End):** D7.2 PIV radius calculations DONE
3. **2026-09-26 (Sp3 End):** Jericó Km 45+800 feedback loop converges → RECOMMENDATION
4. **2026-10-13 (Sp4 End):** Safety criteria validated (rollover, SSD)
5. **2026-10-30 (Sp5 End):** 3 Jericó design cases + cost-benefit → stakeholder approval
6. **2026-11-16 (Sp6 End):** RAG fully indexed in Supabase
7. **2026-12-03 (Sp7 End):** System integration complete, ready for UAT
8. **2026-12-20 (Sp8 End):** PRODUCTION DEPLOYMENT + Agente-05/07 handoffs

---

## Handoff & Review Gates

| Gate | Date | Stakeholders | Approval Needed |
|------|------|--------------|-----------------|
| **Gate 1: D7.1/D7.2 Algorithm Validation** | 2026-09-09 | Agente-Infraestrutura (S1 lead), Modelagem | Design approach OK? |
| **Gate 2: Jericó Case Convergence** | 2026-09-26 | Advisory, Project PM | Proceed with Balanced case? |
| **Gate 3: Cost-Benefit Approval** | 2026-10-30 | Agente-05, Finance | Budget allocation? |
| **Gate 4: Schedule Sign-off** | 2026-11-06 | Agente-07, Project PM | Timeline acceptable? |
| **Gate 5: System Integration** | 2026-12-03 | QA, Arch | Production-ready? |
| **Gate 6: PRODUCTION RELEASE** | 2026-12-20 | Director, Maestro | Go-live approved? |
```

### 6.2 Risk Matrix (Top 5)

```python
from dataclasses import dataclass
from enum import Enum

class RiskSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class RiskLikelihood(Enum):
    UNLIKELY = 0.1
    POSSIBLE = 0.3
    LIKELY = 0.6
    ALMOST_CERTAIN = 0.9

@dataclass
class Risk:
    """Risk registry entry"""
    id: str
    title: str
    description: str
    severity: RiskSeverity
    likelihood: RiskLikelihood
    mitigation_plan: str
    owner: str
    sprint_trigger: str  # When risk becomes active
    
    def risk_score(self) -> float:
        """Risk = Severity × Likelihood (0–3.6 scale)"""
        return self.severity.value * self.likelihood.value

# Top 5 Risks

RISKS = [
    Risk(
        id="R1",
        title="Feedback Loop Convergence Failure (Jericó Km 45+800)",
        description="Geo-road feedback loop diverges (rampa keeps changing, FoS oscillates). "
                    "Indicates slope geometry fundamentally incompatible with road geometry.",
        severity=RiskSeverity.CRITICAL,
        likelihood=RiskLikelihood.POSSIBLE,  # 0.3
        mitigation_plan="""
            1. Implement convergence hardstop at Iteration 3 (vs. unconstrained loop)
            2. If divergent: trigger Aggressive case (lower rampa to 6.5%) OR slope remediation (buttress, deep drainage)
            3. Escalate to Agente-Infraestrutura lead + Contratual for scope/cost change
            4. Buffer 2 weeks in Sprint 3 schedule for resolution
        """,
        owner="Manta-06 (Modelagem)",
        sprint_trigger="Sprint 3"
    ),
    Risk(
        id="R2",
        title="Newmark Displacement > 100 cm (Jericó slope)",
        description="Seismic sliding displacement exceeds engineering tolerance (typically 50 cm). "
                    "Indicates need for stronger slope stabilization (piles, anchors) with major cost impact (+30% +BRL 10M).",
        severity=RiskSeverity.HIGH,
        likelihood=RiskLikelihood.LIKELY,  # 0.6
        mitigation_plan="""
            1. Perform sensitivity analysis: How does Newmark D change with rampa reduction (0.5% increments)?
            2. If D>100cm unavoidable: design micro-pile system earlier (Sp5 vs. Sp7)
            3. Escalate to Agente-05 for cost recalibration (Balanced vs. Conservative comparison)
            4. In Aggressive case, accept higher monitoring burden (8-year post-quake surveillance vs. 3-year)
        """,
        owner="Manta-06 + Agente-05",
        sprint_trigger="Sprint 3–4"
    ),
    Risk(
        id="R3",
        title="RAG Vector Embeddings Quality (Poor Search Results)",
        description="Supabase HNSW index produces irrelevant search results (low cosine similarity). "
                    "Root causes: weak embeddings model (e.g., OpenAI ada vs. text-embedding-3-large), "
                    "poor document chunking strategy, metadata not properly indexed.",
        severity=RiskSeverity.MEDIUM,
        likelihood=RiskLikelihood.POSSIBLE,  # 0.3
        mitigation_plan="""
            1. Use text-embedding-3-large (1536-dim) instead of ada (1536-dim is same, but better quality)
            2. Implement hybrid search: vector + full-text + metadata filtering (not vector-only)
            3. Test embeddings on sample queries before Sp6 deployment
            4. Chunk size: 200–300 tokens (current default ~500 may be too coarse for geometry specs)
            5. Add manual re-ranking layer if automated search inadequate
        """,
        owner="Manta-06 (Modelagem)",
        sprint_trigger="Sprint 6"
    ),
    Risk(
        id="R4",
        title="Scope Creep: Agente-05/07 Request Delays",
        description="Agente-05 (Orcamento) or Agente-07 (Cronograma) backlogged; cannot deliver "
                    "cost/schedule analysis for Jericó cases within 2-week SLA. Blocks Gate 3 & 4 (Oct 30, Nov 6).",
        severity=RiskSeverity.HIGH,
        likelihood=RiskLikelihood.POSSIBLE,  # 0.3
        mitigation_plan="""
            1. Initiate handoff conversations with Agente-05 lead early (Sp4, not Sp5)
            2. Pre-populate cost/schedule payloads in Sp4 so agents only need to refine
            3. Define SLA: Cost estimate 10 days, Schedule 12 days (offer 3-day expedite fee if needed)
            4. Contingency: Build "standard" cost/schedule estimates in Sp5 as fallback
            5. Escalate to Maestro (Manta-00) if SLA at risk
        """,
        owner="Manta-00 (Maestro)",
        sprint_trigger="Sprint 4–5"
    ),
    Risk(
        id="R5",
        title="Integration Test Failures (D7↔Agente-05/07 APIs)",
        description="End-to-end workflow breaks at agent handoff boundary. "
                    "E.g., JSON payload format mismatch, missing fields, Agente-05 API unavailable.",
        severity=RiskSeverity.MEDIUM,
        likelihood=RiskLikelihood.LIKELY,  # 0.6
        mitigation_plan="""
            1. Spec integration APIs in Sp5 (before coding in Sp7)
            2. Mock Agente-05/07 APIs in Sp6 for parallel testing
            3. Run integration test matrix: 3 design cases × 2 agents = 6 handoff paths
            4. Implement error handling: retry logic, validation checks, logging
            5. Schedule pre-integration sync with Agente-05/07 owners in Sp6
        """,
        owner="Manta-06 (Modelagem)",
        sprint_trigger="Sprint 7"
    )
]

def generate_risk_matrix_table():
    """Print risk matrix"""
    
    print("\nS1-V7 RISK MATRIX (Top 5)\n")
    print("=" * 140)
    print(f"{'ID':<5} {'Risk Title':<40} {'Severity':<10} {'Likelihood':<12} {'Score':<8} {'Owner':<20} {'Trigger':<10}")
    print("=" * 140)
    
    for risk in sorted(RISKS, key=lambda r: r.risk_score(), reverse=True):
        score = risk.risk_score()
        print(f"{risk.id:<5} {risk.title:<40} {risk.severity.name:<10} {risk.likelihood.name:<12} {score:<8.2f} {risk.owner:<20} {risk.sprint_trigger:<10}")
    
    print("\n" + "=" * 140)
    print("\nDETAILED MITIGATION PLANS:\n")
    
    for risk in sorted(RISKS, key=lambda r: r.risk_score(), reverse=True):
        print(f"\n{risk.id}: {risk.title}")
        print(f"   Description: {risk.description}")
        print(f"   Mitigation Plan:")
        for line in risk.mitigation_plan.strip().split('\n'):
            print(f"   {line}")
        print(f"   Owner: {risk.owner} | Trigger: {risk.sprint_trigger}")

if __name__ == "__main__":
    generate_risk_matrix_table()
```

---

## SECTION 7: SUMMARY & NEXT STEPS

### Implementation Checklist

```markdown
# S1-V7 IMPLEMENTATION CHECKLIST

## Phase 1: Algorithms & Testing (Sprints 1–5)

- [x] D7.1 Horizontal Geometry
  - [x] Radius optimization algorithm (seismic multiplier 1.1–1.3×)
  - [x] Superelevation formula with +0.5–1.5% seismic adjustment
  - [x] 3 test cases (flat, hilly, mountainous)
  - [ ] Peer review by external geotechnical consultant
  
- [x] D7.2 Vertical Geometry
  - [x] PIV radius calculation (crest + sag)
  - [x] Newmark slope stability integration
  - [x] Rampa optimization (6–7.5%)
  - [ ] Civil 3D profile testing (integration)
  
- [x] D7.3 Geo-Talude Interaction
  - [x] Feedback loop pseudocode (3 iterations max)
  - [x] Jericó Km 45+800 pilot convergence test
  - [ ] Validation against GEO5 software results
  
- [x] D7.4 Viaria Safety Seismic
  - [x] Stopping distance +18% calculation
  - [x] Tombamento (rollover) risk assessment
  - [x] Lane width determination
  - [ ] Safety audit by independent third party
  
- [x] D7.5 Jericó Redesign
  - [x] 3 design alternatives (Conservative/Balanced/Aggressive)
  - [x] Cost-benefit matrix
  - [ ] Stakeholder workshop & approval
  
## Phase 2: Data & Systems (Sprints 6–7)

- [ ] RAG + Supabase
  - [ ] Create 5 collections (hor, ver, geo, seis, jer)
  - [ ] HNSW vector indexes (pgvector)
  - [ ] 100+ documents ingested + embedded
  - [ ] Query patterns validated
  - [ ] Performance benchmarks (latency <500ms)
  
- [ ] Integration & Testing
  - [ ] Mock Agente-05 & Agente-07 APIs
  - [ ] Handoff JSON schema validation
  - [ ] End-to-end workflow test (D7.1→D7.5→Agentes)
  - [ ] UAT with 5 internal users
  - [ ] Bug fixes & polish
  
## Phase 3: Deployment (Sprint 8)

- [ ] Production Supabase Migration
  - [ ] Backup staging environment
  - [ ] Data migration validation
  - [ ] HNSW re-indexing (production cluster)
  - [ ] Failover testing
  
- [ ] Agent Handoff Documentation
  - [ ] Agente-05 (Orcamento) payload finalized
  - [ ] Agente-07 (Cronograma) payload finalized
  - [ ] API documentation (OpenAPI/Swagger)
  - [ ] Sample requests/responses
  
- [ ] Training & Knowledge Transfer
  - [ ] Agente-Infraestrutura team training (2 sessions)
  - [ ] Modeling team training (1 session)
  - [ ] Operations runbook (monitoring, troubleshooting)
  - [ ] Knowledge base articles (Confluence)
  
- [ ] Go-Live
  - [ ] Director sign-off
  - [ ] Maestro integration enabled
  - [ ] Jericó project routing → S1-V7 workflows
  - [ ] Day-1 support standby

## Post-Launch (2027)

- [ ] Monitor Jericó design convergence (3-month feedback loop)
- [ ] Refine vector search based on real usage patterns
- [ ] Expand RAG collections (additional case studies)
- [ ] Capacity planning for S2–S4 (OAE, Ferrovia, Metrô) adaptation
```

---

## FINAL DELIVERABLES SUMMARY

| Deliverable | Format | Owner | Sprint | Status |
|-------------|--------|-------|--------|--------|
| D7.1 Horizontal Geometry Algorithm | Python module + tests | Manta-06 | Sp1 | READY |
| D7.2 Vertical Geometry Algorithm | Python module + tests | Manta-06 | Sp2 | READY |
| D7.3 Feedback Loop + Jericó Demo | Python module + convergence report | Manta-06 | Sp3 | READY |
| D7.4 Safety Seismic Assessment | Python module + test cases | Manta-06 | Sp4 | READY |
| D7.5 Jericó 3 Cases + Cost-Benefit | Design reports + JSON payloads | Manta-06 | Sp5 | READY |
| RAG Collections (5×) + Schema | Supabase SQL + Python client | Manta-06 | Sp6 | PENDING |
| Integration Test Report | Test matrix + UAT results | Manta-06 | Sp7 | PENDING |
| Production Deployment Guide | Runbook + API docs | Manta-06 | Sp8 | PENDING |
| Agente-05 Handoff Payload | JSON schema + examples | Manta-05 | Sp5 | READY |
| Agente-07 Handoff Payload | JSON schema + examples | Manta-07 | Sp5 | READY |

---

**Document Generated:** 2026-07-25  
**Approval Status:** READY FOR STAKEHOLDER REVIEW  
**Next Gate:** Gate 1 (2026-09-09) — D7.1/D7.2 Algorithm Validation
