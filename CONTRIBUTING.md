# Contributing to Tendos

Thank you for your interest in contributing to Tendos! This document provides guidelines and instructions for contributing to the project.

## Welcome

Tendos is an open-source AI cartridge hub platform, and we welcome contributions of all kinds:
- Bug reports and feature requests
- Code improvements and bug fixes
- Documentation enhancements
- Test coverage improvements
- Design and UX feedback

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## How to Contribute

### Reporting Issues

- **Bug Reports**: Use the bug report issue template to describe the issue, steps to reproduce, and expected behavior
- **Feature Requests**: Use the feature request issue template to describe the use case and proposed solution
- **Discussions**: Start a discussion for design ideas or questions

### Pull Requests

1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/my-feature`)
3. **Make your changes** following the development guidelines below
4. **Push to your fork** and **create a Pull Request**
5. **Respond to review feedback** promptly

All Pull Requests must:
- Pass all automated checks (tests, linting, type checking)
- Include test coverage for new functionality
- Include documentation updates if applicable
- Follow commit conventions (see below)

## Development Setup

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Getting Started

```bash
# Clone the repository
git clone https://github.com/tendos/tendos.git
cd tendos

# Install dependencies using uv
uv sync

# Run tests
make test

# Run all checks
make all
```

## TDD Workflow

We practice Test-Driven Development (TDD). The expected workflow is:

1. **Write Tests First**: Write failing tests that specify the desired behavior
2. **Make Tests Pass**: Write the minimal code to make the tests pass
3. **Refactor**: Improve code quality while keeping tests passing

```bash
# Write your tests in tests/ directory
# Run tests frequently during development
make test

# Run tests in watch mode (if available)
make test-watch
```

## Code Standards

All code must adhere to the following standards:

### Linting and Formatting

- **Tool**: [ruff](https://github.com/astral-sh/ruff)
- **Command**: `ruff check .` and `ruff format .`
- Run before committing: `make lint`

### Type Checking

- **Tool**: [mypy](https://github.com/python/mypy) in strict mode
- **Configuration**: Strict type checking enabled
- **Command**: `mypy --strict`
- Run before committing: `make type-check`

### Test Coverage

- **Minimum Coverage**: 80% of code must be covered by tests
- **Tool**: [coverage](https://coverage.readthedocs.io/)
- **Command**: `coverage run && coverage report`
- View detailed report: `coverage html`

### Code Quality Checks

Run all checks before submitting:
```bash
make all  # Runs linting, type checking, and tests
```

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, or tooling changes
- **security**: Security-related changes or fixes

### Examples

```
feat(cartridge): add loader for neural network cartridges

Implement support for loading pre-trained neural network models
from cartridge specifications. This enables users to easily package
and distribute trained models.

Closes #42
```

```
fix(cli): handle missing config file gracefully

Previously the CLI would crash with a cryptic error when the config
file was missing. Now it provides a clear error message and suggests
creating a default config.

Fixes #89
```

```
docs: update installation instructions for Python 3.10+

Add clarification about Python version requirements and update
commands to use uv for consistency.
```

## Pull Request Process

1. **Create a fork** of the repository
2. **Create a feature branch** with a descriptive name
3. **Keep commits atomic** - each commit should represent a logical change
4. **Write clear commit messages** using Conventional Commits format
5. **Run all tests locally** before pushing: `make all`
6. **Push to your fork** and **create a Pull Request** against `main`
7. **Fill out the PR template** completely
8. **Respond to review feedback** professionally and promptly
9. **Request review** from maintainers if needed
10. **Squash commits** if requested by reviewers

### PR Checklist

Before submitting:
- [ ] Tests pass locally (`make test`)
- [ ] Code is properly formatted (`ruff format .`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy --strict`)
- [ ] Coverage is 80%+ for new code
- [ ] Commit messages follow conventions
- [ ] Documentation is updated
- [ ] PR template is completed

## Security Vulnerabilities

If you discover a security vulnerability, please do **not** open a public issue. Instead, please report it responsibly by following the guidelines in [SECURITY.md](SECURITY.md).

## Questions?

- Open a discussion in the repository
- Check existing documentation in the `docs/` directory
- Review previous issues and PRs for similar questions

Thank you for contributing to Tendos!
