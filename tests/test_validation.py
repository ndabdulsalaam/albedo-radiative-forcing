"""
Tests for validation.py module

Tests validation against IPCC benchmarks including:
- Benchmark constants
- ValidationResult dataclass
- Expected forcing ranges
- Validation logic
"""

import pytest
from src.validation import (
    BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA,
    ValidationResult,
    validate_area_fraction,
    expected_forcing_range,
    validate_forcing_result,
)
from src.forcing import delta_radiative_forcing, ForcingResult


class TestBenchmarkConstant:
    """Tests for benchmark sensitivity constant"""

    def test_benchmark_value(self) -> None:
        """Test that benchmark is approximately -340 W/m^2"""
        assert abs(BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA + 340.0) < 10.0


class TestValidationResult:
    """Tests for ValidationResult dataclass"""

    def test_validation_result_creation(self) -> None:
        """Test creation of ValidationResult"""
        result = ValidationResult(
            expected_range_w_m2=(-4.0, -3.0),
            modeled_w_m2=-3.5,
            within_range=True,
            notes="Test note"
        )
        assert result.expected_range_w_m2 == (-4.0, -3.0)
        assert result.modeled_w_m2 == -3.5
        assert result.within_range is True
        assert result.notes == "Test note"

    def test_validation_result_immutable(self) -> None:
        """Test that ValidationResult is frozen"""
        result = ValidationResult((-4.0, -3.0), -3.5, True, "note")
        with pytest.raises(Exception):  # FrozenInstanceError
            result.within_range = False  # type: ignore


class TestValidateAreaFraction:
    """Tests for validate_area_fraction function"""

    def test_valid_area_fractions(self) -> None:
        """Test that valid area fractions pass"""
        assert validate_area_fraction(0.0) == 0.0
        assert validate_area_fraction(0.5) == 0.5
        assert validate_area_fraction(1.0) == 1.0

    def test_invalid_area_fraction_negative(self) -> None:
        """Test that negative area fraction raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            validate_area_fraction(-0.1)

    def test_invalid_area_fraction_too_large(self) -> None:
        """Test that area fraction > 1 raises ValueError"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            validate_area_fraction(1.1)


class TestExpectedForcingRange:
    """Tests for expected_forcing_range function"""

    def test_zero_delta_albedo(self) -> None:
        """Test that zero delta gives zero forcing range"""
        low, high = expected_forcing_range(0.0)
        assert low == 0.0
        assert high == 0.0

    def test_positive_delta_negative_range(self) -> None:
        """Test that positive delta gives negative forcing range"""
        low, high = expected_forcing_range(0.01)
        assert low < 0 and high < 0

    def test_ipcc_benchmark(self) -> None:
        """Test range for +0.01 albedo change"""
        low, high = expected_forcing_range(0.01, area_fraction=1.0, tolerance_fraction=0.2)
        # Expected center: -340 * 0.01 = -3.4
        # With ±20% tolerance: -3.4 ± 0.68 = [-4.08, -2.72]
        assert -4.5 < low < -3.5
        assert -3.0 < high < -2.0

    def test_area_fraction_scaling(self) -> None:
        """Test that area fraction scales the range"""
        full_low, full_high = expected_forcing_range(0.01, area_fraction=1.0)
        half_low, half_high = expected_forcing_range(0.01, area_fraction=0.5)
        
        assert abs(half_low - full_low / 2) < 0.1
        assert abs(half_high - full_high / 2) < 0.1

    def test_tolerance_fraction_effect(self) -> None:
        """Test that tolerance fraction widens the range"""
        narrow_low, narrow_high = expected_forcing_range(0.01, tolerance_fraction=0.1)
        wide_low, wide_high = expected_forcing_range(0.01, tolerance_fraction=0.3)
        
        # Wider tolerance should give wider range
        assert wide_low < narrow_low
        assert wide_high > narrow_high

    def test_symmetric_tolerance(self) -> None:
        """Test that tolerance is symmetric around benchmark"""
        low, high = expected_forcing_range(0.01, tolerance_fraction=0.2)
        center = (low + high) / 2
        benchmark = BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA * 0.01
        assert abs(center - benchmark) < 0.01

    def test_negative_delta_albedo(self) -> None:
        """Test with negative delta (darkening)"""
        low, high = expected_forcing_range(-0.01)
        # Darkening gives positive forcing
        assert low > 0 and high > 0


class TestValidateForcingResult:
    """Tests for validate_forcing_result function"""

    def test_valid_result_within_range(self) -> None:
        """Test that result within expected range passes validation"""
        # Create a forcing result that should be valid
        forcing_result = delta_radiative_forcing(0.01, area_fraction=1.0)
        validation = validate_forcing_result(forcing_result)
        
        assert isinstance(validation, ValidationResult)
        assert validation.within_range is True
        assert "Within expected range" in validation.notes

    def test_valid_result_matches_modeled_value(self) -> None:
        """Test that validation contains the modeled value"""
        forcing_result = delta_radiative_forcing(0.01, area_fraction=1.0)
        validation = validate_forcing_result(forcing_result)
        
        assert validation.modeled_w_m2 == forcing_result.radiative_forcing_w_m2

    def test_validation_range_reasonable(self) -> None:
        """Test that expected range is reasonable"""
        forcing_result = delta_radiative_forcing(0.01, area_fraction=1.0)
        validation = validate_forcing_result(forcing_result)
        
        low, high = validation.expected_range_w_m2
        assert low < high
        assert low < validation.modeled_w_m2 < high

    def test_custom_tolerance(self) -> None:
        """Test validation with custom tolerance"""
        forcing_result = delta_radiative_forcing(0.01, area_fraction=1.0)
        
        narrow = validate_forcing_result(forcing_result, tolerance_fraction=0.05)
        wide = validate_forcing_result(forcing_result, tolerance_fraction=0.5)
        
        narrow_low, narrow_high = narrow.expected_range_w_m2
        wide_low, wide_high = wide.expected_range_w_m2
        
        # Wider tolerance gives wider range
        assert wide_low < narrow_low
        assert wide_high > narrow_high

    def test_area_fraction_validation(self) -> None:
        """Test that area fraction is properly considered"""
        # Half globe
        forcing_result = delta_radiative_forcing(0.01, area_fraction=0.5)
        validation = validate_forcing_result(forcing_result)
        
        # Should still be within range (scaled appropriately)
        assert validation.within_range is True

    def test_zero_forcing_validates(self) -> None:
        """Test that zero forcing validates"""
        forcing_result = delta_radiative_forcing(0.0)
        validation = validate_forcing_result(forcing_result)
        assert validation.within_range is True

    def test_extreme_values_might_fail(self) -> None:
        """Test that extremely unrealistic values might fail validation"""
        # Create an artificial ForcingResult with unrealistic forcing
        # For delta=0.01, expected is ~-3.4, so 100 W/m^2 should fail
        bad_result = ForcingResult(
            delta_albedo=0.01,
            area_fraction=1.0,
            radiative_forcing_w_m2=100.0  # Unrealistic
        )
        validation = validate_forcing_result(bad_result, tolerance_fraction=0.2)
        assert validation.within_range is False
        assert "Outside expected range" in validation.notes


class TestIntegrationWithForcing:
    """Integration tests combining forcing and validation"""

    def test_typical_scenario_validates(self) -> None:
        """Test that typical scenarios pass validation"""
        deltas = [-0.05, -0.02, -0.01, 0.01, 0.02, 0.05]
        
        for delta in deltas:
            forcing_result = delta_radiative_forcing(delta, area_fraction=0.5)
            validation = validate_forcing_result(forcing_result)
            assert validation.within_range is True

    def test_validation_across_area_fractions(self) -> None:
        """Test validation works for different area fractions"""
        area_fractions = [0.1, 0.25, 0.5, 0.75, 1.0]
        
        for area in area_fractions:
            forcing_result = delta_radiative_forcing(0.01, area_fraction=area)
            validation = validate_forcing_result(forcing_result)
            assert validation.within_range is True

    def test_benchmark_comparison(self) -> None:
        """Test that our model matches IPCC benchmark closely"""
        # For unit albedo change, should get ~-340 W/m^2
        forcing_result = delta_radiative_forcing(1.0, area_fraction=1.0)
        
        # Check it's close to benchmark
        expected = BENCHMARK_SENSITIVITY_W_M2_PER_DELTA_ALPHA
        assert abs(forcing_result.radiative_forcing_w_m2 - expected) < 10.0
