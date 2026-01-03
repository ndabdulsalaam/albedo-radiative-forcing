"""
Simple entry points to compose albedo change scenarios with forcing diagnostics.

This module can be extended to chain together albedo inputs, forcing calculations,
and validation routines.
"""

from dataclasses import dataclass

from . import forcing, albedo


@dataclass
class Scenario:
    """Minimal representation of an albedo perturbation scenario."""

    initial_albedo: float
    final_albedo: float
    area_fraction: float = 1.0

    def forcing(self) -> forcing.ForcingResult:
        """Compute TOA forcing for the scenario."""
        initial = albedo.validate_albedo(self.initial_albedo)
        final = albedo.validate_albedo(self.final_albedo)
        delta_alpha = forcing.albedo_difference(initial, final)
        return forcing.delta_radiative_forcing(delta_alpha, area_fraction=self.area_fraction)
