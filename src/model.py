"""
Model pipeline to connect surface albedo changes with radiative forcing.

Uses the zero-dimensional balance:

    ΔF_TOA ≈ - (S0 / 4) * Δα * f_area

where Δα is the change in albedo between an initial and final surface state
and f_area scales a regional perturbation to the global mean.
"""

from dataclasses import dataclass
from typing import Tuple

from . import forcing, albedo


@dataclass
class Scenario:
    """
    Representation of a surface albedo perturbation.

    Parameters
    ----------
    initial_albedo : float
        Starting broadband albedo (0-1).
    final_albedo : float
        Ending broadband albedo (0-1).
    area_fraction : float, optional
        Fraction of Earth's surface affected (0-1). Default is global (1.0).
    """

    initial_albedo: float
    final_albedo: float
    area_fraction: float = 1.0

    def forcing(self) -> forcing.ForcingResult:
        """
        Compute top-of-atmosphere forcing for the scenario.

        Positive forcing is downward (warming). A brighter surface (higher albedo)
        yields negative forcing because more solar radiation is reflected.
        """
        initial = albedo.validate_albedo(self.initial_albedo)
        final = albedo.validate_albedo(self.final_albedo)
        delta_alpha = forcing.albedo_difference(initial, final)
        return forcing.delta_radiative_forcing(delta_alpha, area_fraction=self.area_fraction)


def albedo_pipeline(
    surface_type: str,
    albedo_delta: float = 0.0,
    *,
    anchor: albedo.Anchor = "typical",
    area_fraction: float = 1.0,
) -> Tuple[Scenario, forcing.ForcingResult]:
    """
    End-to-end helper: choose a surface class, perturb its albedo, and compute forcing.

    Parameters
    ----------
    surface_type : str
        Surface identifier (see albedo.SURFACE_LIBRARY keys).
    albedo_delta : float, optional
        Additive perturbation to the baseline albedo (e.g., -0.02 for darkening).
    anchor : {'typical', 'min', 'max'}
        Baseline albedo used before perturbation.
    area_fraction : float, optional
        Fraction of Earth's surface affected (0-1).

    Returns
    -------
    scenario : Scenario
        Encodes the initial/final albedo and area fraction.
    forcing_result : ForcingResult
        Radiative forcing diagnostic (W m^-2).
    """
    base = albedo.base_albedo(surface_type, anchor=anchor)
    perturbed = albedo.perturbed_albedo(surface_type, albedo_delta, anchor=anchor)
    scenario = Scenario(initial_albedo=base, final_albedo=perturbed, area_fraction=area_fraction)
    return scenario, scenario.forcing()


__all__ = ["Scenario", "albedo_pipeline"]
