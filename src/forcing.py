"""
Simplified radiative forcing model for surface albedo changes.

The implementation follows a zero-dimensional energy balance formulation
where a change in planetary albedo (Δα) perturbs the absorbed shortwave
flux at the top of atmosphere:

    ΔF_TOA ≈ - (S0 / 4) * Δα * f_area

S0 is the solar constant and the factor of 1/4 accounts for Earth geometry
(spherical surface area vs. disk intercepted area). The area fraction f_area
lets you scale a regional albedo change to a global-mean forcing by assuming
the perturbation is uniformly distributed over that fraction of the planet.
"""

from dataclasses import dataclass
from typing import Optional

# Physically meaningful constants
SOLAR_CONSTANT_W_M2 = 1361.0  # Current best estimate of total solar irradiance (W m^-2)
GEOMETRIC_FACTOR = 0.25  # Spherical Earth distributes intercepted solar energy over 4x area


@dataclass(frozen=True)
class ForcingResult:
    """Container for forcing diagnostics."""

    delta_albedo: float
    area_fraction: float
    radiative_forcing_w_m2: float


def validate_delta_albedo(delta_albedo: float) -> float:
    """
    Ensure Δα is within physically plausible bounds [-1, 1].

    Values outside this range imply negative or >100% reflectance and are rejected.
    """
    if not -1.0 <= delta_albedo <= 1.0:
        raise ValueError("delta_albedo must be between -1 and 1.")
    return delta_albedo


def delta_radiative_forcing(
    delta_albedo: float,
    *,
    area_fraction: float = 1.0,
    solar_constant: float = SOLAR_CONSTANT_W_M2,
    geometric_factor: float = GEOMETRIC_FACTOR,
) -> ForcingResult:
    """
    Estimate the global-mean top-of-atmosphere radiative forcing from a surface albedo change.

    Parameters
    ----------
    delta_albedo : float
        Change in broadband albedo (final - initial). Positive values mean a brighter surface.
    area_fraction : float, optional
        Fraction of Earth's surface affected by the albedo change (0-1). Defaults to 1.0 (global).
    solar_constant : float, optional
        Total solar irradiance in W m^-2. Defaults to a modern estimate (1361 W m^-2).
    geometric_factor : float, optional
        Accounts for spherical geometry (default 0.25 = 1/4).

    Returns
    -------
    ForcingResult
        Structured result containing the input metadata and the radiative forcing (W m^-2).

    Notes
    -----
    - Forcing is defined positive downward (warming). Brightening the surface (Δα > 0)
      yields a negative forcing because more sunlight is reflected.
    - The calculation assumes the albedo perturbation is evenly distributed over `area_fraction`
      of the globe and that atmospheric adjustments are negligible.
    - This is an instantaneous, zero-feedback estimate; cloud responses, spectral effects,
      and latitudinal insolation gradients are not represented.
    """
    if not 0.0 <= area_fraction <= 1.0:
        raise ValueError("area_fraction must be between 0 and 1.")
    validate_delta_albedo(delta_albedo)

    absorbed_solar_change = -solar_constant * geometric_factor * delta_albedo
    radiative_forcing = absorbed_solar_change * area_fraction

    return ForcingResult(
        delta_albedo=delta_albedo,
        area_fraction=area_fraction,
        radiative_forcing_w_m2=radiative_forcing,
    )


def albedo_difference(initial_albedo: float, final_albedo: float) -> float:
    """
    Compute Δα given initial and final surface (or planetary) albedo values.

    Parameters
    ----------
    initial_albedo : float
        Starting albedo (0-1).
    final_albedo : float
        Ending albedo (0-1).

    Returns
    -------
    float
        Δα = final - initial
    """
    if not 0.0 <= initial_albedo <= 1.0:
        raise ValueError("initial_albedo must be between 0 and 1.")
    if not 0.0 <= final_albedo <= 1.0:
        raise ValueError("final_albedo must be between 0 and 1.")

    return final_albedo - initial_albedo


def example_usage() -> Optional[ForcingResult]:
    """
    Simple, non-executed example to illustrate the API.

    Example
    -------
    >>> delta_alpha = albedo_difference(0.30, 0.28)  # 0.02 darkening
    >>> result = delta_radiative_forcing(delta_alpha, area_fraction=0.5)
    >>> result.radiative_forcing_w_m2
    3.4025
    """
    return None


__all__ = [
    "SOLAR_CONSTANT_W_M2",
    "GEOMETRIC_FACTOR",
    "ForcingResult",
    "validate_delta_albedo",
    "delta_radiative_forcing",
    "albedo_difference",
]
