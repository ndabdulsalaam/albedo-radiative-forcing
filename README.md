# Albedo-Radiative-Forcing Toolkit

[![Tests](https://github.com/ndabdulsalaam/albedo-radiative-forcing/workflows/Tests/badge.svg)](https://github.com/ndabdulsalaam/albedo-radiative-forcing/actions)
[![Code Quality](https://github.com/ndabdulsalaam/albedo-radiative-forcing/workflows/Code%20Quality/badge.svg)](https://github.com/ndabdulsalaam/albedo-radiative-forcing/actions)
[![codecov](https://codecov.io/gh/ndabdulsalaam/albedo-radiative-forcing/branch/main/graph/badge.svg)](https://codecov.io/gh/ndabdulsalaam/albedo-radiative-forcing)
[![PyPI version](https://badge.fury.io/py/albedo-radiative-forcing.svg)](https://badge.fury.io/py/albedo-radiative-forcing)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A scientific Python package for calculating top-of-atmosphere (TOA) radiative forcing from surface albedo changes using zero-dimensional energy balance models.

## Background

Surface albedo—the fraction of incoming shortwave radiation reflected by the surface—modulates the planet's energy balance. Brighter surfaces reduce absorbed solar energy; darker surfaces increase it. Top-of-atmosphere (TOA) radiative forcing quantifies this perturbation and is a key diagnostic in climate assessments.

## Features

- **Scientifically rigorous**: Literature-based albedo values with IPCC benchmark validation
- **Easy to use**: Simple API for researchers and climate scientists
- **Well-tested**: Comprehensive test suite with >90% code coverage
- **Type-safe**: Full type annotations for better IDE support
- **Extensible**: Modular design for custom scenarios and sensitivity analyses

## Installation

### From PyPI (recommended)

```bash
pip install albedo-radiative-forcing
```

### From source

```bash
git clone https://github.com/ndabdulsalaam/albedo-radiative-forcing.git
cd albedo-radiative-forcing
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from src import albedo_pipeline, validate_forcing_result

# Calculate forcing from vegetation darkening
scenario, forcing = albedo_pipeline(
    surface_type="vegetation",
    albedo_delta=-0.02,  # 2% darkening
    area_fraction=0.5    # Affecting half the globe
)

print(f"Radiative forcing: {forcing.radiative_forcing_w_m2:.2f} W/m²")

# Validate against IPCC benchmark
validation = validate_forcing_result(forcing)
print(f"Within expected range: {validation.within_range}")
```

### Available Surface Types

```python
from src.albedo import SURFACE_LIBRARY, list_surface_types

# List all available surfaces
print(list(list_surface_types()))
# ['vegetation', 'desert', 'snow_fresh', 'snow_aged', 'urban', 'cropland']

# View surface parameters
import pandas as pd
df = pd.DataFrame.from_dict(SURFACE_LIBRARY, orient='index')
print(df)
```

### Sensitivity Analysis

```python
from src import albedo_pipeline
import pandas as pd

# Test multiple perturbations
results = []
for delta in [-0.05, -0.02, 0.0, 0.02, 0.05]:
    _, forcing = albedo_pipeline("urban", delta, area_fraction=0.2)
    results.append({
        'delta_albedo': delta,
        'forcing_W_m2': forcing.radiative_forcing_w_m2
    })

df = pd.DataFrame(results)
print(df)
```

### Custom Scenarios

```python
from src.model import Scenario

# Define a custom albedo change scenario
scenario = Scenario(
    initial_albedo=0.30,  # Dark vegetation
    final_albedo=0.20,    # Cropland
    area_fraction=0.15    # 15% of Earth's surface
)

forcing_result = scenario.forcing()
print(f"ΔF_TOA = {forcing_result.radiative_forcing_w_m2:.2f} W/m²")
```

## Model Formulation

The toolkit uses a zero-dimensional shortwave energy balance:

```
ΔF_TOA ≈ - (S₀ / 4) × Δα × f_area
```

Where:
- **S₀** = Solar constant (~1361 W/m²)
- **Δα** = Albedo perturbation (final - initial)
- **f_area** = Fraction of Earth's surface affected (0-1)
- **1/4** = Geometric factor (spherical Earth)

### Surface Classes

| Surface Type | Typical Albedo | Range | Literature Source |
|-------------|----------------|-------|-------------------|
| Vegetation  | 0.17 | 0.13-0.20 | Oke (1987), IPCC AR5 |
| Desert      | 0.38 | 0.30-0.45 | Sagan et al. (1979) |
| Snow (fresh)| 0.78 | 0.70-0.85 | Wiscombe & Warren (1980) |
| Snow (aged) | 0.50 | 0.40-0.60 | Wiscombe & Warren (1980) |
| Urban       | 0.16 | 0.12-0.20 | Taha (1997), Oke (1987) |
| Cropland    | 0.20 | 0.15-0.25 | Sellers (1965) |

## Validation

The model is validated against IPCC-style benchmark sensitivity:

- **Benchmark**: Δα = +0.01 → ΔF ≈ -3.4 W/m² (global mean)
- **Tolerance**: ±20% to account for uncertainties

```python
from src.validation import validate_forcing_result, expected_forcing_range

# Check if result is within expected range
low, high = expected_forcing_range(delta_albedo=0.01, area_fraction=1.0)
print(f"Expected range: [{low:.2f}, {high:.2f}] W/m²")
```

## Assumptions and Limitations

- ⚠️ **Zero-dimensional**: Global-mean scaling; no latitude/season/cloud variability
- ⚠️ **Instantaneous forcing**: No feedbacks (clouds, water vapor, circulation)
- ⚠️ **Broadband albedo**: Spectral and bidirectional effects neglected
- ⚠️ **Uniform application**: Heterogeneous land cover not represented
- ⚠️ **Clear-sky**: Aerosol and cloud interactions outside scope

This toolkit provides **first-order estimates** for early-stage sensitivity analyses. For detailed assessments, use coupled Earth system models.

## Use Cases

### Climate Mitigation Research
- Snow darkening from soot/pollution
- Deforestation/reforestation albedo impacts
- Urban cool roof initiatives
- Desert greening projects

### Policy Analysis
- Rapid assessment of land-surface interventions
- Comparison of mitigation strategies
- Educational demonstrations

### Integration
- Input for integrated assessment models
- Benchmarking for complex climate models
- Uncertainty quantification studies

## Documentation

- **API Reference**: See docstrings in source code
- **Examples**: Check `notebooks/demo.ipynb`
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md)

## Development

```bash
# Clone repository
git clone https://github.com/ndabdulsalaam/albedo-radiative-forcing.git
cd albedo-radiative-forcing

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest --cov=src

# Run code quality checks
pre-commit run --all-files
```

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{albedo_radiative_forcing,
  title = {Albedo-Radiative-Forcing Toolkit},
  author = {Nurudeen Abdulsalaam},
  year = {2026},
  url = {https://github.com/ndabdulsalaam/albedo-radiative-forcing},
  version = {0.1.0},
  license = {MIT}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- 📝 [Open an issue](https://github.com/ndabdulsalaam/albedo-radiative-forcing/issues)
- 💬 [Start a discussion](https://github.com/ndabdulsalaam/albedo-radiative-forcing/discussions)
- 📧 Contact: ndabdulsalaam@gmail.com

## Acknowledgments

- Albedo values from peer-reviewed literature (see inline citations)
- IPCC AR5 Working Group 1 for benchmark sensitivities
- Climate science community for feedback and validation

---

**Made with ❤️ for climate science research**
