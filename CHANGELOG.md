# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial package structure with proper Python packaging
- Core modules: `albedo.py`, `forcing.py`, `model.py`, `validation.py`
- Comprehensive test suite with 100+ test cases
- CI/CD pipelines with GitHub Actions
- Pre-commit hooks for code quality
- MIT license
- PyPI publishing workflow

### Changed
- Migrated to modern `pyproject.toml` configuration
- Updated requirements with version constraints

### Fixed
- Package now installable via pip

## [0.1.0] - 2026-01-06

### Added
- Initial release of albedo-radiative-forcing toolkit by Nurudeen Abdulsalaam
- Zero-dimensional energy balance model for TOA forcing calculations
- Surface albedo parameterization for common land-cover types
- IPCC benchmark validation
- Jupyter notebook demonstrations
- Comprehensive documentation
