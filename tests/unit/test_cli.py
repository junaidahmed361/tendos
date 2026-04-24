"""Tests for the tendos CLI — TDD."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from tendos.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_cartridge_dir(tmp_path):
    """Create a valid cartridge directory for CLI testing."""
    cartridge_dir = tmp_path / "my-cartridge"
    cartridge_dir.mkdir()
    manifest = {
        "name": "my-cartridge",
        "version": "1.0.0",
        "author": "testuser",
        "domain": "test",
        "description": "A test cartridge",
        "license": "Apache-2.0",
        "model": {"base": "llama-3.3-8b-q4", "source": "ollama"},
        "agent": {"system_prompt": "prompts/system.txt"},
    }
    (cartridge_dir / "cartridge.json").write_text(json.dumps(manifest, indent=2))
    (cartridge_dir / "prompts").mkdir()
    (cartridge_dir / "prompts" / "system.txt").write_text("You are a helpful assistant.")
    return cartridge_dir


class TestCLIRoot:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "tendos" in result.output.lower() or "Tendos" in result.output

    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.1" in result.output


class TestInit:
    def test_init_creates_cartridge_dir(self, runner, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init", "my-new-cartridge"])
            assert result.exit_code == 0
            from pathlib import Path

            cartridge_dir = Path("my-new-cartridge")
            assert cartridge_dir.exists()
            assert (cartridge_dir / "cartridge.json").exists()
            assert (cartridge_dir / "prompts").is_dir()
            assert (cartridge_dir / "harness").is_dir()
            assert (cartridge_dir / "harness" / "harness.yaml").exists()

    def test_init_existing_dir_fails(self, runner, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            from pathlib import Path

            Path("existing").mkdir()
            result = runner.invoke(cli, ["init", "existing"])
            assert result.exit_code != 0


class TestValidate:
    def test_validate_valid_cartridge(self, runner, sample_cartridge_dir):
        result = runner.invoke(cli, ["validate", str(sample_cartridge_dir / "cartridge.json")])
        assert result.exit_code == 0

    def test_validate_invalid_manifest(self, runner, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text('{"name": "Invalid Name!"}')
        result = runner.invoke(cli, ["validate", str(bad)])
        assert result.exit_code != 0


class TestPack:
    def test_pack_creates_archive(self, runner, sample_cartridge_dir, tmp_path):
        output = str(tmp_path / "out.cartridge")
        result = runner.invoke(cli, ["pack", str(sample_cartridge_dir), "--output", output])
        assert result.exit_code == 0
        from pathlib import Path

        assert Path(output).exists()

    def test_pack_invalid_dir_fails(self, runner, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = runner.invoke(cli, ["pack", str(empty)])
        assert result.exit_code != 0


class TestSignAndVerify:
    def test_sign_and_verify_roundtrip(self, runner, sample_cartridge_dir, tmp_path):
        # Pack first
        archive = tmp_path / "test.cartridge"
        runner.invoke(cli, ["pack", str(sample_cartridge_dir), "--output", str(archive)])
        # Generate key
        key_path = tmp_path / "test.key"
        pub_path = tmp_path / "test.pub"
        # Sign
        result = runner.invoke(
            cli,
            [
                "sign",
                str(archive),
                "--key",
                str(key_path),
                "--pub",
                str(pub_path),
                "--generate-key",
            ],
        )
        assert result.exit_code == 0
        sig_path = archive.with_suffix(".cartridge.sig")
        assert sig_path.exists()
        # Verify
        result = runner.invoke(
            cli,
            [
                "verify",
                str(archive),
                "--pub",
                str(pub_path),
                "--sig",
                str(sig_path),
            ],
        )
        assert result.exit_code == 0
