# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-24

### Added

- Harness YAML declaration support in cartridge manifest (`harness` block) for:
  - security guardrails
  - PII redaction policy
  - update/sync procedures
- Loader validation for harness YAML file path when `harness.yaml_path` is provided
- CLI `tendos init` now scaffolds `harness/harness.yaml`
- Dogfood example cartridge: `examples/hermes-local-agent/`

### Changed

- Removed non-existent project email addresses from governance and security documentation
- Updated security reporting guidance to GitHub Security Advisory workflow

## [0.1.0] - 2026-04-07

### Added

- Initial cartridge specification (v1.0) with Pydantic schema validation
- Cartridge loader: create, validate, pack, and unpack `.cartridge` archives
- Security module: Ed25519 cartridge signing, verification, AES-256-GCM LoRA weight encryption
- JWT token management for pay-per-use licensing
- CLI scaffolding: `tendos init`, `tendos validate`, `tendos pack`, `tendos sign`, `tendos verify`
- Full test suite with >80% coverage target
- CI/CD via GitHub Actions (lint, typecheck, security scan, test matrix Python 3.10-3.13)
- Pre-commit hooks (ruff, mypy, bandit)
- uv-based package management
- Apache 2.0 open-source licensing
- Contributing guidelines and security policy
