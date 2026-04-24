# Tendos

Plug-and-play AI cartridge hub — package, distribute, and run composable AI harness configurations locally, then deploy the same cartridges to hosted Tendos Cloud.

Tendos is building toward "Docker for AI agents and harnesses": portable, signed cartridges with reproducible execution across local machines and managed cloud.

The name and product metaphor come from Nintendo cartridges (plug in and play) combined with Docker-style portability and reproducibility.

[![CI](https://github.com/junaidahmed361/tendos/actions/workflows/ci.yml/badge.svg)](https://github.com/junaidahmed361/tendos/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)

---

## Vision

Small and open language models are making local AI practical. Tendos exists so builders and teams do not have to re-create agent harnesses from scratch for every use case.

A Tendos cartridge is a reusable, swappable unit that can bundle:

- model configuration (base model + optional adapters)
- agent configuration (prompt, nodes, graph, tools)
- security and trust data (checksums, signatures)
- licensing and usage metadata

Long-term direction:

- local-first execution by default (privacy and ownership)
- hosted deployment option via Tendos Cloud (pay to host)
- community ecosystem where creators publish cartridges and users install/compose them quickly

## What is Tendos today?

Tendos currently provides the v0.1 foundation for cartridge packaging and trust:

- Cartridge specification and manifest schema validation
- Cartridge loader for validate/pack/unpack workflows
- Ed25519 signing and signature verification
- AES-256-GCM encryption helpers for protected artifacts
- JWT token utilities for pay-per-use licensing primitives
- Harness YAML declarations for security guardrails, PII redaction, and update/sync policies
- CLI scaffolding for cartridge lifecycle operations

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

# Verify signature
tendos verify my-cartridge.cartridge --pub ~/.tendos/signing.pub --sig my-cartridge.cartridge.sig
```

## Core Principles

- Local-first: run on your hardware first, with cloud as an option
- Portable artifacts: one cartridge format for reuse and sharing
- Trust by default: signing, verification, and integrity checks
- Composability: stack cartridges for domain-specific workflows

## Development

```bash
# Clone and install
git clone https://github.com/junaidahmed361/tendos.git
cd tendos
uv sync --all-extras

# Run tests
make test

# Run full quality suite
make all

# Run pre-commit hooks
make pre-commit
```

### Project Structure

```text
src/tendos/
  cartridge/    # Cartridge schema, loader, validator
  runtime/      # Runtime execution engine (expanding)
  hub/          # Marketplace and registry client (expanding)
  security/     # Signing, encryption, JWT tokens
  cli/          # Command-line interface
tests/
  unit/
  integration/
```

### Quality Gates

All pull requests are expected to pass:

- ruff lint + formatting checks
- mypy strict type checks
- bandit static security scan
- pytest with coverage threshold
- pre-commit hooks

## Roadmap (high level)

1. Local execution runtime for cartridges
2. Lockfile + compatibility checks for reproducibility
3. Community hub for publish/discover/install workflows
4. Tendos Cloud hosted deployment for managed agent execution

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
