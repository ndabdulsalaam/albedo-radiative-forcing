"""
Tests for forcing.py module

Tests radiative forcing calculations including:
- Forcing result dataclass
- Delta albedo validation
- Radiative forcing computation
- Albedo difference calculations
"""

import dataclasses

import pytest

from src.forcing import (
    GEOMETRIC_FACTOR,
    SOLAR_CONSTANT_W_M2,
    ForcingResult,
    albedo_difference,
    delta_radiative_forcing,
    validate_delta_albedo,
)


class TestConstants:
    """Tests for physical constants"""

    def test_solar_constant_reasonable(self) -> None:
        """Test that solar constant is in reasonable range"""
        assert 1300 < SOLAR_CONSTANT_W_M2 < 1400

    def test_geometric_factor(self) -> None:
        """Test that geometric factor is 1/4"""
        assert GEOMETRIC_FACTOR == 0.25


class TestForcingResult:
    """Tests for ForcingResult dataclass"""

    def test_forcing_result_creation(self) -> None:
        """Test creation of ForcingResult"""
        result = ForcingResult(delta_albedo=0.01, area_fraction=0.5, radiative_forcing_w_m2=-1.7)
        assert result.delta_albedo == 0.01
        assert result.area_fraction == 0.5
        assert result.radiative_forcing_w_m2 == -1.7

    def test_forcing_result_immutable(self) -> None:
        """Test that ForcingResult is frozen"""
        result = ForcingResult(0.01, 0.5, -1.7)
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.delta_albedo = 0.02  # type: ignore


class TestValidateDeltaAlbedo:
    """Tests for validate_delta_albedo function"""

    def test_valid_delta_albedos(self) -> None:
        """Test that valid delta albedos pass"""
        assert validate_delta_albedo(0.0) == 0.0
        assert validate_delta_albedo(-0.5) == -0.5
        assert validate_delta_albedo(0.5) == 0.5
        assert validate_delta_albedo(-1.0) == -1.0
        assert validate_delta_albedo(1.0) == 1.0

    def test_invalid_delta_too_negative(self) -> None:
        """Test that delta < -1 raises ValueError"""
        with pytest.raises(ValueError, match="between -1 and 1"):
            validate_delta_albedo(-1.1)

    def test_invalid_delta_too_positive(self) -> None:
        """Test that delta > 1 raises ValueError"""
        with pytest.raises(ValueError, match="between -1 and 1"):
            validate_delta_albedo(1.1)


class TestDeltaRadiativeForcing:
    """Tests for delta_radiative_forcing function"""

    def test_zero_delta_albedo(self) -> None:
        """Test that zero albedo change gives zero forcing"""
        result = delta_radiative_forcing(0.0)
        assert result.radiative_forcing_w_m2 == 0.0

    def test_positive_delta_gives_negative_forcing(self) -> None:
        """Test that brightening (positive delta) gives negative forcing (cooling)"""
        result = delta_radiative_forcing(0.01)
        assert result.radiative_forcing_w_m2 < 0.0

    def test_negative_delta_gives_positive_forcing(self) -> None:
        """Test that darkening (negative delta) gives positive forcing (warming)"""
        result = delta_radiative_forcing(-0.01)
        assert result.radiative_forcing_w_m2 > 0.0

    def test_ipcc_benchmark_value(self) -> None:
        """Test against IPCC benchmark: +0.01 albedo -> ~-3.4 W/m^2"""
        result = delta_radiative_forcing(0.01, area_fraction=1.0)
        expected = -SOLAR_CONSTANT_W_M2 * GEOMETRIC_FACTOR * 0.01
        assert abs(result.radiative_forcing_w_m2 - expected) < 0.01

    def test_unit_albedo_change(self) -> None:
        """Test that unit albedo change gives ~-340 W/m^2"""
        result = delta_radiative_forcing(1.0, area_fraction=1.0)
        expected = -SOLAR_CONSTANT_W_M2 * GEOMETRIC_FACTOR
        assert abs(result.radiative_forcing_w_m2 - expected) < 1.0

    def test_area_fraction_scaling(self) -> None:
        """Test that area fraction correctly scales forcing"""
        full = delta_radiative_forcing(0.01, area_fraction=1.0)
        half = delta_radiative_forcing(0.01, area_fraction=0.5)
        assert abs(half.radiative_forcing_w_m2 - full.radiative_forcing_w_m2 / 2) < 0.01

    def test_invalid_area_fraction_negative(self) -> None:
        """Test that negative area fraction raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            delta_radiative_forcing(0.01, area_fraction=-0.1)

    def test_invalid_area_fraction_too_large(self) -> None:
        """Test that area fraction > 1 raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            delta_radiative_forcing(0.01, area_fraction=1.1)

    def test_custom_solar_constant(self) -> None:
        """Test with custom solar constant"""
        custom_s0 = 1400.0
        result = delta_radiative_forcing(0.01, solar_constant=custom_s0, area_fraction=1.0)
        expected = -custom_s0 * GEOMETRIC_FACTOR * 0.01
        assert abs(result.radiative_forcing_w_m2 - expected) < 0.01

    def test_custom_geometric_factor(self) -> None:
        """Test with custom geometric factor"""
        custom_geom = 0.3
        result = delta_radiative_forcing(0.01, geometric_factor=custom_geom, area_fraction=1.0)
        expected = -SOLAR_CONSTANT_W_M2 * custom_geom * 0.01
        assert abs(result.radiative_forcing_w_m2 - expected) < 0.01

    def test_result_contains_inputs(self) -> None:
        """Test that result contains the input parameters"""
        delta = 0.05
        area = 0.75
        result = delta_radiative_forcing(delta, area_fraction=area)
        assert result.delta_albedo == delta
        assert result.area_fraction == area


class TestAlbedoDifference:
    """Tests for albedo_difference function"""

    def test_no_change(self) -> None:
        """Test that identical albedos give zero difference"""
        assert albedo_difference(0.5, 0.5) == 0.0

    def test_brightening(self) -> None:
        """Test positive delta for brightening"""
        delta = albedo_difference(0.3, 0.4)
        assert delta == pytest.approx(0.1)

    def test_darkening(self) -> None:
        """Test negative delta for darkening"""
        delta = albedo_difference(0.4, 0.3)
        assert delta == pytest.approx(-0.1)

    def test_order_matters(self) -> None:
        """Test that order of arguments matters (final - initial)"""
        forward = albedo_difference(0.3, 0.4)
        backward = albedo_difference(0.4, 0.3)
        assert forward == -backward

    def test_invalid_initial_albedo_negative(self) -> None:
        """Test that negative initial albedo raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            albedo_difference(-0.1, 0.5)

    def test_invalid_initial_albedo_too_large(self) -> None:
        """Test that initial albedo > 1 raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            albedo_difference(1.1, 0.5)

    def test_invalid_final_albedo_negative(self) -> None:
        """Test that negative final albedo raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            albedo_difference(0.5, -0.1)

    def test_invalid_final_albedo_too_large(self) -> None:
        """Test that final albedo > 1 raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            albedo_difference(0.5, 1.1)

    def test_extreme_values(self) -> None:
        """Test with extreme but valid values"""
        # Complete darkening
        assert albedo_difference(1.0, 0.0) == -1.0
        # Complete brightening
        assert albedo_difference(0.0, 1.0) == 1.0


class TestIntegration:
    """Integration tests combining multiple functions"""

    def test_albedo_difference_to_forcing(self) -> None:
        """Test workflow: compute delta, then forcing"""
        initial = 0.3
        final = 0.28  # Darkening by 0.02
        delta = albedo_difference(initial, final)
        result = delta_radiative_forcing(delta, area_fraction=0.5)

        # Darkening should give positive forcing (warming)
        assert result.radiative_forcing_w_m2 > 0
        # Should be approximately half of full-globe value
        full_result = delta_radiative_forcing(delta, area_fraction=1.0)
        assert abs(result.radiative_forcing_w_m2 - full_result.radiative_forcing_w_m2 / 2) < 0.01
