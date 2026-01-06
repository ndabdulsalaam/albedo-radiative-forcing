"""
Tests for albedo.py module

Tests surface albedo parameterization including:
- Surface library values
- Validation logic
- Base albedo retrieval
- Perturbation calculations
"""

import dataclasses

import pytest

from src.albedo import (
    SURFACE_LIBRARY,
    base_albedo,
    list_surface_types,
    perturbed_albedo,
    validate_albedo,
)


class TestSurfaceAlbedo:
    """Tests for SurfaceAlbedo dataclass"""

    def test_surface_albedo_immutable(self) -> None:
        """Test that SurfaceAlbedo is frozen (immutable)"""
        surf = SURFACE_LIBRARY["vegetation"]
        with pytest.raises(dataclasses.FrozenInstanceError):
            surf.typical = 0.5  # type: ignore


class TestSurfaceLibrary:
    """Tests for SURFACE_LIBRARY"""

    def test_surface_library_not_empty(self) -> None:
        """Test that surface library contains entries"""
        assert len(SURFACE_LIBRARY) > 0

    def test_all_surfaces_have_valid_albedos(self) -> None:
        """Test that all surface types have albedos in [0, 1]"""
        for name, surf in SURFACE_LIBRARY.items():
            assert 0.0 <= surf.range_min <= 1.0, f"{name} has invalid range_min"
            assert 0.0 <= surf.typical <= 1.0, f"{name} has invalid typical"
            assert 0.0 <= surf.range_max <= 1.0, f"{name} has invalid range_max"

    def test_surface_ranges_ordered(self) -> None:
        """Test that min <= typical <= max for all surfaces"""
        for name, surf in SURFACE_LIBRARY.items():
            assert (
                surf.range_min <= surf.typical <= surf.range_max
            ), f"{name} has incorrect ordering: {surf.range_min} <= {surf.typical} <= {surf.range_max}"

    def test_known_surface_values(self) -> None:
        """Test specific literature-based values"""
        # Vegetation should be relatively dark
        assert SURFACE_LIBRARY["vegetation"].typical < 0.3
        # Snow should be bright
        assert SURFACE_LIBRARY["snow_fresh"].typical > 0.7
        # Desert should be moderately bright
        assert 0.3 <= SURFACE_LIBRARY["desert"].typical <= 0.5


class TestValidateAlbedo:
    """Tests for validate_albedo function"""

    def test_valid_albedos(self) -> None:
        """Test that valid albedos pass validation"""
        assert validate_albedo(0.0) == 0.0
        assert validate_albedo(0.5) == 0.5
        assert validate_albedo(1.0) == 1.0

    def test_invalid_albedos_negative(self) -> None:
        """Test that negative albedos raise ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            validate_albedo(-0.1)

    def test_invalid_albedos_too_large(self) -> None:
        """Test that albedos > 1 raise ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            validate_albedo(1.1)


class TestListSurfaceTypes:
    """Tests for list_surface_types function"""

    def test_returns_iterable(self) -> None:
        """Test that function returns an iterable"""
        result = list_surface_types()
        assert hasattr(result, "__iter__")

    def test_contains_expected_surfaces(self) -> None:
        """Test that common surfaces are in the list"""
        surfaces = list(list_surface_types())
        assert "vegetation" in surfaces
        assert "desert" in surfaces
        assert "urban" in surfaces


class TestBaseAlbedo:
    """Tests for base_albedo function"""

    def test_typical_anchor(self) -> None:
        """Test retrieval with 'typical' anchor"""
        veg_typical = base_albedo("vegetation", anchor="typical")
        assert veg_typical == SURFACE_LIBRARY["vegetation"].typical

    def test_min_anchor(self) -> None:
        """Test retrieval with 'min' anchor"""
        veg_min = base_albedo("vegetation", anchor="min")
        assert veg_min == SURFACE_LIBRARY["vegetation"].range_min

    def test_max_anchor(self) -> None:
        """Test retrieval with 'max' anchor"""
        veg_max = base_albedo("vegetation", anchor="max")
        assert veg_max == SURFACE_LIBRARY["vegetation"].range_max

    def test_case_insensitive(self) -> None:
        """Test that surface type lookup is case-insensitive"""
        lower = base_albedo("vegetation")
        upper = base_albedo("VEGETATION")
        mixed = base_albedo("VeGeTaTiOn")
        assert lower == upper == mixed

    def test_invalid_surface_type(self) -> None:
        """Test that invalid surface type raises KeyError"""
        with pytest.raises(KeyError, match="not found"):
            base_albedo("nonexistent_surface")

    def test_invalid_anchor(self) -> None:
        """Test that invalid anchor raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported anchor"):
            base_albedo("vegetation", anchor="median")  # type: ignore


class TestPerturbedAlbedo:
    """Tests for perturbed_albedo function"""

    def test_zero_perturbation(self) -> None:
        """Test that zero perturbation returns base albedo"""
        base = base_albedo("vegetation")
        perturbed = perturbed_albedo("vegetation", delta=0.0)
        assert perturbed == base

    def test_positive_perturbation(self) -> None:
        """Test brightening (positive delta)"""
        base = base_albedo("vegetation")
        perturbed = perturbed_albedo("vegetation", delta=0.05)
        assert perturbed == base + 0.05

    def test_negative_perturbation(self) -> None:
        """Test darkening (negative delta)"""
        base = base_albedo("vegetation")
        perturbed = perturbed_albedo("vegetation", delta=-0.05)
        assert perturbed == base - 0.05

    def test_clipping_to_zero(self) -> None:
        """Test that albedo is clipped to 0 if perturbation goes negative"""
        # Use a surface with low albedo and large negative perturbation
        perturbed = perturbed_albedo("vegetation", delta=-1.0)
        assert perturbed == 0.0

    def test_clipping_to_one(self) -> None:
        """Test that albedo is clipped to 1 if perturbation exceeds 1"""
        # Use fresh snow (already high albedo) and large positive perturbation
        perturbed = perturbed_albedo("snow_fresh", delta=0.5)
        assert perturbed == 1.0

    def test_different_anchors(self) -> None:
        """Test perturbation with different anchor values"""
        typical = perturbed_albedo("vegetation", delta=0.02, anchor="typical")
        min_val = perturbed_albedo("vegetation", delta=0.02, anchor="min")
        max_val = perturbed_albedo("vegetation", delta=0.02, anchor="max")

        # Should all differ by approximately the same delta from their respective bases
        assert typical != min_val != max_val
        assert min_val < typical < max_val

    def test_physical_bounds_maintained(self) -> None:
        """Test that result is always in [0, 1]"""
        for surface in list_surface_types():
            for delta in [-0.5, -0.1, 0.0, 0.1, 0.5]:
                result = perturbed_albedo(surface, delta)
                assert 0.0 <= result <= 1.0, f"Result {result} out of bounds for {surface} with delta={delta}"
