# Contributing to Albedo-Radiative-Forcing

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/ndabdulsalaam/albedo-radiative-forcing.git
cd albedo-radiative-forcing
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode with all development dependencies.

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

This will automatically run code quality checks before each commit.

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_albedo.py

# Run specific test
pytest tests/test_albedo.py::TestValidateAlbedo::test_valid_albedos
```

### Code Quality Checks

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with MyPy
mypy src/

# Run all checks at once
pre-commit run --all-files
```

### Running Notebooks

```bash
jupyter notebook notebooks/demo.ipynb
```

## Code Style Guidelines

- **Line length**: 120 characters maximum
- **Formatting**: Use Black (configured in `pyproject.toml`)
- **Type hints**: All public functions must have type annotations
- **Docstrings**: Use NumPy-style docstrings for all public APIs
- **Imports**: Organize with isort (automated by pre-commit)

## Testing Requirements

- All new features must include tests
- Maintain test coverage ≥90%
- Tests should cover:
  - Happy path (normal usage)
  - Edge cases (boundary values)
  - Error cases (invalid inputs)
  - Integration scenarios

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   pytest --cov=src
   pre-commit run --all-files
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

## Commit Message Guidelines

Follow conventional commits format:

```
type(scope): brief description

Detailed explanation if needed.

Fixes #123
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

**Examples**:
- `feat(albedo): add new surface type for tundra`
- `fix(forcing): correct area fraction validation`
- `docs(readme): update installation instructions`
- `test(validation): add IPCC benchmark tests`

## Adding New Surface Types

To add a new surface type to the albedo library:

1. Add entry to `SURFACE_LIBRARY` in `src/albedo.py`
2. Include literature reference in comments
3. Add tests in `tests/test_albedo.py`
4. Update documentation

## Reporting Issues

When reporting bugs, please include:

- Python version
- Operating system
- Minimal reproducible example
- Expected vs actual behavior
- Full error traceback

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Contact maintainers for security issues

Thank you for contributing! 🌍
