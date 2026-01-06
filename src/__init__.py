"""
Albedo-Radiative-Forcing Toolkit

A scientific Python package for calculating top-of-atmosphere radiative forcing
from surface albedo changes using zero-dimensional energy balance models.

This toolkit is designed for climate researchers to perform rapid assessments
of land-surface interventions and their radiative impacts.
"""

__version__ = "0.1.0"
__author__ = "Nurudeen Abdulsalaam"
__license__ = "MIT"

# Import core modules
from . import albedo, forcing, model, validation

# Expose key classes and functions at package level
from .albedo import (
    SURFACE_LIBRARY,
    SurfaceAlbedo,
    base_albedo,
    list_surface_types,
    perturbed_albedo,
    validate_albedo,
)
from .forcing import (
    GEOMETRIC_FACTOR,
    SOLAR_CONSTANT_W_M2,
    ForcingResult,
    albedo_difference,
    delta_radiative_forcing,
    validate_delta_albedo,
)
from .model import (
    Scenario,
    albedo_pipeline,
)
from .validation import (
    BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA,
    ValidationResult,
    expected_forcing_range,
    validate_area_fraction,
    validate_forcing_result,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Modules
    "albedo",
    "forcing",
    "model",
    "validation",
    # Albedo module
    "SurfaceAlbedo",
    "SURFACE_LIBRARY",
    "validate_albedo",
    "list_surface_types",
    "base_albedo",
    "perturbed_albedo",
    # Forcing module
    "SOLAR_CONSTANT_W_M2",
    "GEOMETRIC_FACTOR",
    "ForcingResult",
    "validate_delta_albedo",
    "delta_radiative_forcing",
    "albedo_difference",
    # Model module
    "Scenario",
    "albedo_pipeline",
    # Validation module
    "BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA",
    "ValidationResult",
    "validate_area_fraction",
    "expected_forcing_range",
    "validate_forcing_result",
]
