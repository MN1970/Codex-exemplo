"""
D6.2 Liquefaction Analysis - Quick Start Guide
===============================================

Copy-paste examples for common analysis scenarios.
"""

import sys
import os

# Add current directory to path for module import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from liquefaction_d62 import (
    LiquefactionAnalyzer,
    LayerData,
    SiteConditions,
    D73FeedbackInterface,
    RiskLevel
)


# ============================================================================
# EXAMPLE 1: Simple single-layer analysis
# ============================================================================

def example_1_single_layer():
    """Analyze a single layer at 5m depth."""

    analyzer = LiquefactionAnalyzer(site_id="SITE-EXAMPLE-1")

    layer = LayerData(
        depth_mid=5.0,
        n_value=15,
        fines_content=20.0,
        water_table_depth=2.0,
        unit_weight=19.5,
        sigma_v0_prime=85.0
    )

    site = SiteConditions(
        magnitude=7.5,
        peak_accel_g=0.35,
        depth_water_table=2.0,
        vs30=180.0
    )

    result = analyzer.analyze_site([layer], site)

    print("\n" + "="*70)
    print("EXAMPLE 1: Single Layer Analysis")
    print("="*70)
    print(result.summary())

    return result


# ============================================================================
# EXAMPLE 2: Multi-layer stratified profile
# ============================================================================

def example_2_stratified_profile():
    """Analyze a 10-layer stratified soil profile."""

    analyzer = LiquefactionAnalyzer(site_id="SITE-EXAMPLE-2", verbose=False)

    # Define 10 layers (1m thick each, from 0.5m to 9.5m)
    layers = [
        LayerData(depth_mid=0.5, n_value=3, fines_content=12.0,
                  water_table_depth=-1.0, unit_weight=18.5, sigma_v0_prime=10.0),
        LayerData(depth_mid=1.5, n_value=6, fines_content=15.0,
                  water_table_depth=-1.0, unit_weight=18.8, sigma_v0_prime=25.0),
        LayerData(depth_mid=2.5, n_value=10, fines_content=18.0,
                  water_table_depth=2.0, unit_weight=19.0, sigma_v0_prime=40.0),
        LayerData(depth_mid=3.5, n_value=14, fines_content=20.0,
                  water_table_depth=2.0, unit_weight=19.2, sigma_v0_prime=55.0),
        LayerData(depth_mid=4.5, n_value=18, fines_content=18.0,
                  water_table_depth=2.0, unit_weight=19.4, sigma_v0_prime=70.0),
        LayerData(depth_mid=5.5, n_value=22, fines_content=15.0,
                  water_table_depth=2.0, unit_weight=19.6, sigma_v0_prime=85.0),
        LayerData(depth_mid=6.5, n_value=26, fines_content=12.0,
                  water_table_depth=2.0, unit_weight=19.8, sigma_v0_prime=100.0),
        LayerData(depth_mid=7.5, n_value=30, fines_content=10.0,
                  water_table_depth=2.0, unit_weight=20.0, sigma_v0_prime=115.0),
        LayerData(depth_mid=8.5, n_value=35, fines_content=8.0,
                  water_table_depth=2.0, unit_weight=20.2, sigma_v0_prime=130.0),
        LayerData(depth_mid=9.5, n_value=40, fines_content=5.0,
                  water_table_depth=2.0, unit_weight=20.4, sigma_v0_prime=145.0),
    ]

    site = SiteConditions(
        magnitude=7.3,
        peak_accel_g=0.32,
        depth_water_table=2.0,
        vs30=190.0
    )

    result = analyzer.analyze_site(layers, site)

    print("\n" + "="*70)
    print("EXAMPLE 2: Stratified 10-Layer Profile")
    print("="*70)
    print(result.summary())

    # Export to CSV for spreadsheet review
    analyzer.export_csv(result, "/tmp/example2_liquefaction.csv")
    print("\nCSV exported to: /tmp/example2_liquefaction.csv")

    return result


# ============================================================================
# EXAMPLE 3: Sensitivity analysis - varying earthquake magnitude
# ============================================================================

def example_3_magnitude_sensitivity():
    """Compare liquefaction risk across different earthquake magnitudes."""

    print("\n" + "="*70)
    print("EXAMPLE 3: Magnitude Sensitivity Analysis")
    print("="*70)

    analyzer = LiquefactionAnalyzer(site_id="SITE-EXAMPLE-3", verbose=False)

    # Use same soil layer for all scenarios
    layer = LayerData(
        depth_mid=4.0,
        n_value=16,
        fines_content=22.0,
        water_table_depth=2.0,
        unit_weight=19.2,
        sigma_v0_prime=70.0
    )

    magnitudes = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5]
    pga = 0.30  # Fixed PGA

    print(f"\nSoil Properties:")
    print(f"  Depth: 4.0m | N: 16 | Fines: 22% | σ'_v0: 70 kPa")
    print(f"  Fixed PGA: {pga}g | vs30: 180 m/s")
    print(f"\nMagnitude | FS     | LI    | Risk Level")
    print("-" * 50)

    for mag in magnitudes:
        site = SiteConditions(
            magnitude=mag,
            peak_accel_g=pga,
            depth_water_table=2.0,
            vs30=180.0
        )

        result = analyzer.analyze_site([layer], site)
        layer_result = result.layers[0]

        print(f"  M {mag:.1f}   | {layer_result.fs:6.3f} | {result.total_li:5.3f} | {result.risk_level.value}")


# ============================================================================
# EXAMPLE 4: PGA sensitivity (fixed magnitude)
# ============================================================================

def example_4_pga_sensitivity():
    """Compare liquefaction risk across different peak accelerations."""

    print("\n" + "="*70)
    print("EXAMPLE 4: Peak Acceleration Sensitivity Analysis")
    print("="*70)

    analyzer = LiquefactionAnalyzer(site_id="SITE-EXAMPLE-4", verbose=False)

    layer = LayerData(
        depth_mid=4.0,
        n_value=16,
        fines_content=22.0,
        water_table_depth=2.0,
        unit_weight=19.2,
        sigma_v0_prime=70.0
    )

    pga_values = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    magnitude = 7.5  # Fixed magnitude

    print(f"\nSoil Properties:")
    print(f"  Depth: 4.0m | N: 16 | Fines: 22% | σ'_v0: 70 kPa")
    print(f"  Fixed M: {magnitude:.1f} | vs30: 180 m/s")
    print(f"\nPGA    | FS     | LI    | Risk Level")
    print("-" * 45)

    for pga in pga_values:
        site = SiteConditions(
            magnitude=magnitude,
            peak_accel_g=pga,
            depth_water_table=2.0,
            vs30=180.0
        )

        result = analyzer.analyze_site([layer], site)
        layer_result = result.layers[0]

        print(f" {pga:.2f}g  | {layer_result.fs:6.3f} | {result.total_li:5.3f} | {result.risk_level.value}")


# ============================================================================
# EXAMPLE 5: D7.3 Feedback Integration
# ============================================================================

def example_5_d73_integration():
    """Prepare liquefaction analysis for D7.3 feedback module."""

    analyzer = LiquefactionAnalyzer(site_id="PROJECT-2026-001")

    # Analyze site
    layers = [
        LayerData(depth_mid=2.0, n_value=8, fines_content=15.0,
                  water_table_depth=1.5, unit_weight=19.0, sigma_v0_prime=35.0),
        LayerData(depth_mid=4.0, n_value=14, fines_content=20.0,
                  water_table_depth=1.5, unit_weight=19.3, sigma_v0_prime=70.0),
        LayerData(depth_mid=6.0, n_value=22, fines_content=18.0,
                  water_table_depth=1.5, unit_weight=19.6, sigma_v0_prime=105.0),
    ]

    site = SiteConditions(
        magnitude=7.4,
        peak_accel_g=0.36,
        depth_water_table=1.5,
        vs30=175.0
    )

    result = analyzer.analyze_site(layers, site)

    print("\n" + "="*70)
    print("EXAMPLE 5: D7.3 Feedback Integration")
    print("="*70)
    print(result.summary())

    # Prepare feedback package for D7.3
    feedback_json = "/tmp/d73_feedback_example5.json"

    D73FeedbackInterface.export_json(
        result,
        feedback_json,
        analyst_notes="Preliminary liquefaction assessment based on exploratory boring program (3 boreholes)",
        next_steps=[
            "Advanced laboratory testing (cyclic triaxial) on key layers",
            "Detailed CPT analysis at depths 2-6m",
            "Mitigation design if LI > 15 (ground improvement recommended)",
            "Final liquefaction assessment report by 2026-09-30"
        ]
    )

    print(f"\nD7.3 Feedback JSON exported to: {feedback_json}")

    return result


# ============================================================================
# EXAMPLE 6: Risk-based classification
# ============================================================================

def example_6_risk_classification():
    """Classify liquefaction risk across different site conditions."""

    print("\n" + "="*70)
    print("EXAMPLE 6: Risk Classification Matrix")
    print("="*70)

    analyzer = LiquefactionAnalyzer(site_id="SITE-EXAMPLE-6", verbose=False)

    # Test different N-value and depth combinations
    test_cases = [
        ("Very Loose", 5, 2.0),
        ("Loose", 10, 3.0),
        ("Moderate", 18, 5.0),
        ("Dense", 28, 7.0),
        ("Very Dense", 40, 9.0),
    ]

    site = SiteConditions(
        magnitude=7.5,
        peak_accel_g=0.35,
        depth_water_table=1.5,
        vs30=175.0
    )

    print(f"\nSoil Description | SPT N | Depth | FS     | LI    | Risk Level")
    print("-" * 70)

    for desc, n_val, depth in test_cases:
        layer = LayerData(
            depth_mid=depth,
            n_value=n_val,
            fines_content=18.0,
            water_table_depth=1.5,
            unit_weight=19.2,
            sigma_v0_prime=depth * 20.0  # Approximate
        )

        result = analyzer.analyze_site([layer], site)
        layer_result = result.layers[0]

        print(f"{desc:16} | {n_val:5} | {depth:5.1f}m | {layer_result.fs:6.3f} | {result.total_li:5.3f} | {result.risk_level.value}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("*" * 70)
    print("* D6.2 LIQUEFACTION ANALYSIS - QUICK START EXAMPLES")
    print("*" * 70)

    # Run all examples
    example_1_single_layer()
    example_2_stratified_profile()
    example_3_magnitude_sensitivity()
    example_4_pga_sensitivity()
    example_5_d73_integration()
    example_6_risk_classification()

    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70 + "\n")
