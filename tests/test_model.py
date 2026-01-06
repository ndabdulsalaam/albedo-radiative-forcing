"""
Tests for model.py module

Tests the model pipeline including:
- Scenario class
- Pipeline orchestration
- End-to-end workflows
"""

import pytest

from src import albedo
from src.forcing import ForcingResult
from src.model import Scenario, albedo_pipeline


class TestScenario:
    """Tests for Scenario class"""

    def test_scenario_creation(self) -> None:
        """Test basic scenario creation"""
        scenario = Scenario(initial_albedo=0.3, final_albedo=0.28, area_fraction=0.5)
        assert scenario.initial_albedo == 0.3
        assert scenario.final_albedo == 0.28
        assert scenario.area_fraction == 0.5

    def test_scenario_default_area_fraction(self) -> None:
        """Test that area_fraction defaults to 1.0"""
        scenario = Scenario(initial_albedo=0.3, final_albedo=0.28)
        assert scenario.area_fraction == 1.0

    def test_scenario_forcing_calculation(self) -> None:
        """Test forcing calculation from scenario"""
        scenario = Scenario(initial_albedo=0.30, final_albedo=0.28, area_fraction=0.5)  # Darkening by 0.02
        result = scenario.forcing()

        assert isinstance(result, ForcingResult)
        assert result.delta_albedo == pytest.approx(-0.02)
        assert result.area_fraction == 0.5
        # Darkening should give positive forcing (warming)
        assert result.radiative_forcing_w_m2 > 0

    def test_scenario_brightening(self) -> None:
        """Test scenario with brightening (albedo increase)"""
        scenario = Scenario(initial_albedo=0.20, final_albedo=0.25, area_fraction=1.0)  # Brightening by 0.05
        result = scenario.forcing()

        # Brightening should give negative forcing (cooling)
        assert result.radiative_forcing_w_m2 < 0

    def test_scenario_invalid_initial_albedo(self) -> None:
        """Test that invalid initial albedo raises error"""
        scenario = Scenario(initial_albedo=1.5, final_albedo=0.5)
        with pytest.raises(ValueError):
            scenario.forcing()

    def test_scenario_invalid_final_albedo(self) -> None:
        """Test that invalid final albedo raises error"""
        scenario = Scenario(initial_albedo=0.5, final_albedo=-0.1)
        with pytest.raises(ValueError):
            scenario.forcing()


class TestAlbedoPipeline:
    """Tests for albedo_pipeline function"""

    def test_pipeline_basic_usage(self) -> None:
        """Test basic pipeline usage"""
        scenario, forcing_result = albedo_pipeline(surface_type="vegetation", albedo_delta=-0.02, area_fraction=0.5)

        assert isinstance(scenario, Scenario)
        assert isinstance(forcing_result, ForcingResult)
        assert scenario.area_fraction == 0.5
        # Darkening should give positive forcing
        assert forcing_result.radiative_forcing_w_m2 > 0

    def test_pipeline_zero_delta(self) -> None:
        """Test pipeline with zero perturbation"""
        scenario, forcing_result = albedo_pipeline(surface_type="vegetation", albedo_delta=0.0)

        assert scenario.initial_albedo == scenario.final_albedo
        assert forcing_result.radiative_forcing_w_m2 == 0.0

    def test_pipeline_different_surfaces(self) -> None:
        """Test pipeline with different surface types"""
        for surface in ["vegetation", "desert", "snow_fresh", "urban"]:
            scenario, forcing_result = albedo_pipeline(surface_type=surface, albedo_delta=0.01)
            assert isinstance(scenario, Scenario)
            assert isinstance(forcing_result, ForcingResult)

    def test_pipeline_anchor_typical(self) -> None:
        """Test pipeline with typical anchor"""
        scenario, _ = albedo_pipeline(surface_type="vegetation", anchor="typical")
        expected_base = albedo.base_albedo("vegetation", anchor="typical")
        assert scenario.initial_albedo == expected_base

    def test_pipeline_anchor_min(self) -> None:
        """Test pipeline with min anchor"""
        scenario, _ = albedo_pipeline(surface_type="vegetation", anchor="min")
        expected_base = albedo.base_albedo("vegetation", anchor="min")
        assert scenario.initial_albedo == expected_base

    def test_pipeline_anchor_max(self) -> None:
        """Test pipeline with max anchor"""
        scenario, _ = albedo_pipeline(surface_type="vegetation", anchor="max")
        expected_base = albedo.base_albedo("vegetation", anchor="max")
        assert scenario.initial_albedo == expected_base

    def test_pipeline_positive_delta(self) -> None:
        """Test pipeline with positive perturbation (brightening)"""
        scenario, forcing_result = albedo_pipeline(surface_type="urban", albedo_delta=0.05)  # Brightening

        assert scenario.final_albedo > scenario.initial_albedo
        # Brightening gives negative forcing (cooling)
        assert forcing_result.radiative_forcing_w_m2 < 0

    def test_pipeline_negative_delta(self) -> None:
        """Test pipeline with negative perturbation (darkening)"""
        scenario, forcing_result = albedo_pipeline(surface_type="urban", albedo_delta=-0.05)  # Darkening

        assert scenario.final_albedo < scenario.initial_albedo
        # Darkening gives positive forcing (warming)
        assert forcing_result.radiative_forcing_w_m2 > 0

    def test_pipeline_area_fraction_scaling(self) -> None:
        """Test that area fraction properly scales in pipeline"""
        _, full = albedo_pipeline("vegetation", -0.02, area_fraction=1.0)
        _, half = albedo_pipeline("vegetation", -0.02, area_fraction=0.5)

        assert abs(half.radiative_forcing_w_m2 - full.radiative_forcing_w_m2 / 2) < 0.01

    def test_pipeline_invalid_surface(self) -> None:
        """Test that invalid surface type raises error"""
        with pytest.raises(KeyError):
            albedo_pipeline("nonexistent_surface")

    def test_pipeline_clipping_behavior(self) -> None:
        """Test that extreme deltas are clipped to [0, 1]"""
        # Try to darken snow beyond physical limits
        scenario, _ = albedo_pipeline(surface_type="snow_fresh", albedo_delta=-1.0)  # Large darkening

        # Final albedo should be clipped to 0
        assert scenario.final_albedo >= 0.0


class TestEndToEndWorkflows:
    """Integration tests for complete workflows"""

    def test_deforestation_scenario(self) -> None:
        """Test realistic deforestation scenario (vegetation -> cropland)"""
        # Deforestation typically darkens surface slightly
        veg_albedo = albedo.base_albedo("vegetation")
        crop_albedo = albedo.base_albedo("cropland")

        delta = crop_albedo - veg_albedo
        scenario, forcing_result = albedo_pipeline(
            surface_type="vegetation", albedo_delta=delta, area_fraction=0.1  # 10% of Earth surface
        )

        assert isinstance(forcing_result, ForcingResult)
        # Result should be measurable but small (only 10% of globe)
        assert abs(forcing_result.radiative_forcing_w_m2) < 10.0

    def test_snow_darkening_scenario(self) -> None:
        """Test snow darkening from pollution/soot"""
        scenario, forcing_result = albedo_pipeline(
            surface_type="snow_fresh",
            albedo_delta=-0.1,  # 10% darkening from soot
            area_fraction=0.15,  # ~15% of Earth (polar regions)
        )

        # Darkening gives positive forcing (warming)
        assert forcing_result.radiative_forcing_w_m2 > 0

    def test_urban_cool_roof_scenario(self) -> None:
        """Test urban cool roof initiative (brightening)"""
        scenario, forcing_result = albedo_pipeline(
            surface_type="urban",
            albedo_delta=0.08,  # Cool roofs brighten by ~8%
            area_fraction=0.02,  # ~2% of Earth is urban
        )

        # Brightening gives negative forcing (cooling)
        assert forcing_result.radiative_forcing_w_m2 < 0

    def test_multiple_scenarios_comparison(self) -> None:
        """Test comparing multiple scenarios"""
        scenarios = []

        # Different perturbations on same surface
        for delta in [-0.05, -0.02, 0.0, 0.02, 0.05]:
            _, forcing = albedo_pipeline("vegetation", delta, area_fraction=0.5)
            scenarios.append((delta, forcing.radiative_forcing_w_m2))

        # Check monotonic relationship: more darkening -> more positive forcing
        for i in range(len(scenarios) - 1):
            delta1, forcing1 = scenarios[i]
            delta2, forcing2 = scenarios[i + 1]
            assert delta1 < delta2
            assert forcing1 > forcing2  # More negative delta -> more positive forcing
