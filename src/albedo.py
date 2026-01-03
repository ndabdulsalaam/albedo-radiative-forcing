"""
Utilities for working with surface or planetary albedo inputs.

Currently a placeholder; expand with spatial aggregation or scenario loaders
as the project grows.
"""


def validate_albedo(value: float) -> float:
    """Clamp and validate an albedo value between 0 and 1."""
    if not 0.0 <= value <= 1.0:
        raise ValueError("albedo must be between 0 and 1.")
    return value
