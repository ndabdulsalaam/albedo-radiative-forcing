"""
Shared validation helpers for the radiative forcing toolkit.
"""


def validate_area_fraction(value: float) -> float:
    """Ensure area fraction is within [0, 1]."""
    if not 0.0 <= value <= 1.0:
        raise ValueError("area_fraction must be between 0 and 1.")
    return value
