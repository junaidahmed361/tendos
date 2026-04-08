# tendos
Plug-and-play AI cartridge hub — package, distribute, and run composable AI harness configurations locally.
=======
# Tendos

**Plug-and-play AI cartridge hub — package, distribute, and run composable AI harness configurations locally.**

[![CI](https://github.com/tendos-ai/tendos/actions/workflows/ci.yml/badge.svg)](https://github.com/tendos-ai/tendos/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/codecov/c/github/tendos-ai/tendos)](https://codecov.io/gh/tendos-ai/tendos)
[![PyPI](https://img.shields.io/pypi/v/tendos)](https://pypi.org/project/tendos/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)

---

## What is Tendos?

Tendos is an open-source platform for packaging, distributing, and running **AI cartridges** — self-contained units that bundle a model specification (base model + optional LoRA adapters), an agent graph, tool definitions, system prompts, and licensing metadata into a single deployable artifact. Think of cartridges as game cartridges for AI: plug one in, and it runs.

The platform serves two audiences simultaneously. **AI builders** package their fine-tuned models and agent configurations into cartridges and distribute them via the Tendos Hub — with optional pay-per-use monetization. **Domain professionals** (healthcare, legal, finance, etc.) browse the Hub, download cartridges, and stack them into local AI workflows without writing a single line of code. Privacy-first: all inference runs on your hardware by default.

## Quick Start

```bash
# Install
pip install tendos
# or
uv add tendos

# Initialize a new cartridge project
tendos init my-cartridge

# Validate the cartridge manifest
tendos validate my-cartridge/cartridge.json

# Pack into a distributable .cartridge archive
tendos pack my-cartridge/

# Sign the cartridge for integrity verification
tendos sign my-cartridge.cartridge --key ~/.tendos/signing.key
```

## Features

- **Cartridge Specification v1.0** — Open, versioned schema for packaging AI configurations (model, LoRA, agent graph, tools, prompts, licensing) as a single unit
- **Local Runtime** — Execute cartridges on your hardware via Ollama, llama.cpp, or vLLM, with enterprise API fallback
- **Security** — Ed25519 cartridge signing, AES-256-GCM LoRA weight encryption, JWT-based pay-per-use tokens
- **Composability** — Stack cartridges like building blocks; dependency resolution and conflict detection built in
- **Privacy-First** — All data stays on-device by default; opt-in telemetry only
- **Hub Marketplace** — Discover, distribute, and monetize cartridges (coming soon)

## Development

```bash
# Clone and install
git clone https://github.com/tendos-ai/tendos.git
cd tendos
uv sync --all-extras

# Run tests
make test

# Run the full quality suite (lint + typecheck + security + test)
make all

# Format code
make format

# Run pre-commit hooks
make pre-commit
```

### Project Structure

```
src/tendos/
  cartridge/    # Cartridge spec schema, loader, validator
  runtime/      # Local execution engine, model/agent layers
  hub/          # Hub API client and authentication
  security/     # Signing, encryption, JWT tokens
  cli/          # Command-line interface (Click)
tests/
  unit/         # Unit tests (TDD)
  integration/  # Integration tests
```

### Development Philosophy

Tendos follows **test-driven development (TDD)**. Every feature starts with a failing test. The workflow is:

1. Write a test that defines expected behavior
2. Run it — confirm it fails
3. Write the minimum code to make it pass
4. Refactor
5. Repeat

All PRs require passing lint (`ruff`), type checking (`mypy --strict`), security scanning (`bandit`), and a minimum 80% test coverage.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and the PR process.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
