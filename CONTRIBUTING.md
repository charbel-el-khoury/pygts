# Contributing to pyGTS

Thank you for considering contributing to pyGTS! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/charbel-el-khoury/pygts.git
cd pygts
```

2. Create a virtual environment and install in development mode:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

3. Install pre-commit hooks (optional):
```bash
pip install pre-commit
pre-commit install
```

## Code Style

This project follows Python community standards:

- **Formatting**: We use [Black](https://black.readthedocs.io/) with an 88-character line length
- **Linting**: We use [Ruff](https://docs.astral.sh/ruff/) for fast linting
- **Type Hints**: Type hints are encouraged but not required
- **Docstrings**: All public functions must have docstrings following Google style

Run formatting and linting:
```bash
black src/
ruff check src/
```

## Testing

We use pytest for testing. Please add tests for any new functionality.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scratch_env --cov-report=term-missing
```

## Documentation

- Update docstrings for any changed functions
- Update README.md for user-facing changes
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/) format

## Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "Add feature: description of feature"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request with:
   - Clear description of changes
   - Link to related issues
   - Test results (if applicable)

5. Ensure CI checks pass

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Package version
- Minimal code example to reproduce
- Error messages and stack traces

## Feature Requests

Feature requests are welcome! Please:
- Check existing issues first
- Clearly describe the use case
- Explain why the feature would be useful

## Questions?

Feel free to open an issue for questions or discussion.

Thank you for contributing! 🌳
