"""
Surface albedo parameterization for common land-cover types.

Albedo values represent broadband shortwave reflectance under clear-sky
conditions and are intended for quick energy-balance experiments. Values
are drawn from literature ranges; see inline comments for sources.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Literal

Anchor = Literal["typical", "min", "max"]


@dataclass(frozen=True)
class SurfaceAlbedo:
    """Typical albedo characteristics for a land-surface class."""

    typical: float
    range_min: float
    range_max: float
    note: str


# Typical broadband albedo ranges (unitless) with literature cues:
# - Vegetation: 0.13-0.20, mid ~0.17 (Oke, 1987; IPCC AR5 WG1 Ch8).
# - Desert (bright sand): 0.30-0.45, mid ~0.38 (Sagan et al., 1979).
# - Snow, fresh: 0.70-0.85, mid ~0.78 (Wiscombe & Warren, 1980).
# - Snow, aging/dusty: 0.40-0.60, mid ~0.50 (Wiscombe & Warren, 1980).
# - Urban/built: 0.12-0.20, mid ~0.16 (Taha, 1997; Oke, 1987).
# - Cropland/bare soil: 0.15-0.25, mid ~0.20 (Sellers, 1965).
SURFACE_LIBRARY: Dict[str, SurfaceAlbedo] = {
    "vegetation": SurfaceAlbedo(typical=0.17, range_min=0.13, range_max=0.20, note="closed canopy forest/grass"),
    "desert": SurfaceAlbedo(typical=0.38, range_min=0.30, range_max=0.45, note="bright sand"),
    "snow_fresh": SurfaceAlbedo(typical=0.78, range_min=0.70, range_max=0.85, note="fresh dry snow"),
    "snow_aged": SurfaceAlbedo(typical=0.50, range_min=0.40, range_max=0.60, note="aging or dusty snow"),
    "urban": SurfaceAlbedo(typical=0.16, range_min=0.12, range_max=0.20, note="built environment"),
    "cropland": SurfaceAlbedo(typical=0.20, range_min=0.15, range_max=0.25, note="bare soil or sparse crop"),
}


def validate_albedo(value: float) -> float:
    """Validate an albedo value is within [0, 1]."""
    if not 0.0 <= value <= 1.0:
        raise ValueError("albedo must be between 0 and 1.")
    return value


def list_surface_types() -> Iterable[str]:
    """Return supported surface keys."""
    return SURFACE_LIBRARY.keys()


def _anchor_value(surface: SurfaceAlbedo, anchor: Anchor) -> float:
    if anchor == "typical":
        return surface.typical
    if anchor == "min":
        return surface.range_min
    if anchor == "max":
        return surface.range_max
    raise ValueError(f"Unsupported anchor '{anchor}'. Choose from 'typical', 'min', or 'max'.")


def base_albedo(surface_type: str, *, anchor: Anchor = "typical") -> float:
    """
    Get an unperturbed albedo for a named surface type.

    Parameters
    ----------
    surface_type : str
        Key in SURFACE_LIBRARY (case-insensitive).
    anchor : {'typical', 'min', 'max'}
        Which value to return: the literature mid-point or bounds.
    """
    key = surface_type.lower()
    if key not in SURFACE_LIBRARY:
        raise KeyError(f"Surface type '{surface_type}' not found. Available: {', '.join(SURFACE_LIBRARY)}")
    value = _anchor_value(SURFACE_LIBRARY[key], anchor)
    return validate_albedo(value)


def perturbed_albedo(surface_type: str, delta: float, *, anchor: Anchor = "typical") -> float:
    """
    Apply an additive perturbation to a surface albedo for sensitivity tests.

    The result is clipped to physical bounds [0, 1].

    Parameters
    ----------
    surface_type : str
        Name of the surface in SURFACE_LIBRARY.
    delta : float
        Additive perturbation to the anchor albedo (e.g., -0.02 to darken).
    anchor : {'typical', 'min', 'max'}
        Baseline albedo used before perturbation.
    """
    base = base_albedo(surface_type, anchor=anchor)
    perturbed = base + delta
    # Clip to [0, 1] to avoid unphysical values.
    return validate_albedo(max(0.0, min(1.0, perturbed)))


__all__ = [
    "SurfaceAlbedo",
    "SURFACE_LIBRARY",
    "validate_albedo",
    "list_surface_types",
    "base_albedo",
    "perturbed_albedo",
]
