"""
Validation helpers to compare modeled forcing against literature benchmarks.

Approach
--------
We compare modeled top-of-atmosphere forcing from an albedo perturbation
against a simple, published sensitivity used in IPCC assessments:

    ΔF_TOA ≈ - (S0 / 4) * Δα * f_area

where S0/4 ≈ 340 W m^-2. A +0.01 albedo increase globally should yield about
-3.4 W m^-2 (downward-positive convention). We allow a tolerance band to
acknowledge uncertainties (cloud masking, spectral effects, regional gradients).

This module reports whether modeled values fall within an expected range and
documents key uncertainty sources, not as a formal skill score but as a
sanity check against first-order energy balance expectations.
"""

from dataclasses import dataclass
from typing import Tuple

from . import forcing as forcing_mod

# Benchmark sensitivity from zero-dimensional energy balance (IPCC AR5 Ch8 uses
# similar S0/4 scaling). Per-unit albedo change => -340 W m^-2; per 0.01 => -3.4.
BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA = -340.0


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of forcing validation."""

    expected_range_w_m2: Tuple[float, float]
    modeled_w_m2: float
    within_range: bool
    notes: str


def validate_area_fraction(value: float) -> float:
    """Ensure area fraction is within [0, 1]."""
    if not 0.0 <= value <= 1.0:
        raise ValueError("area_fraction must be between 0 and 1.")
    return value


def expected_forcing_range(
    delta_albedo: float,
    area_fraction: float = 1.0,
    *,
    tolerance_fraction: float = 0.2,
) -> Tuple[float, float]:
    """
    Compute an expected forcing interval based on IPCC-style shortwave sensitivity.

    Parameters
    ----------
    delta_albedo : float
        Change in broadband albedo (positive = brighter).
    area_fraction : float
        Fraction of Earth's surface affected (0-1).
    tolerance_fraction : float
        Symmetric fractional tolerance around the benchmark (default ±20%).

    Returns
    -------
    (low, high) : tuple of float
        Expected forcing bounds (W m^-2).
    """
    validate_area_fraction(area_fraction)
    benchmark = BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA * delta_albedo * area_fraction
    spread = abs(benchmark) * tolerance_fraction
    return benchmark - spread, benchmark + spread


def validate_forcing_result(
    result: forcing_mod.ForcingResult,
    *,
    tolerance_fraction: float = 0.2,
) -> ValidationResult:
    """
    Compare a modeled forcing result to benchmark ranges.

    The benchmark uses ΔF_TOA ≈ -340 * Δα * f_area W m^-2. We check whether
    the modeled value lies within ±tolerance_fraction of that estimate.

    Uncertainty sources (not explicitly modeled):
    - Cloud masking and cloud-albedo interactions.
    - Spectral and bidirectional reflectance effects not captured by broadband Δα.
    - Latitudinal/seasonal insolation gradients vs. global-mean scaling.
    - Rapid atmospheric adjustments (aerosols, water vapor) absent from this model.
    """
    expected_low, expected_high = expected_forcing_range(
        result.delta_albedo, area_fraction=result.area_fraction, tolerance_fraction=tolerance_fraction
    )
    within = expected_low <= result.radiative_forcing_w_m2 <= expected_high
    notes = (
        "Within expected range based on S0/4 scaling."
        if within
        else "Outside expected range; revisit Δα, area fraction, or applicability of global-mean scaling."
    )
    return ValidationResult(
        expected_range_w_m2=(expected_low, expected_high),
        modeled_w_m2=result.radiative_forcing_w_m2,
        within_range=within,
        notes=notes,
    )


__all__ = [
    "BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA",
    "ValidationResult",
    "validate_area_fraction",
    "expected_forcing_range",
    "validate_forcing_result",
]
