"""Tests for cartridge loading, packing, and unpacking — TDD."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tendos.cartridge.loader import CartridgeLoader
from tendos.cartridge.schema import CartridgeManifest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sample_cartridge_dir(tmp_path: Path) -> Path:
    """Create a minimal valid cartridge directory."""
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
    prompts_dir = cartridge_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "system.txt").write_text("You are a helpful assistant.")
    return cartridge_dir


@pytest.fixture
def loader() -> CartridgeLoader:
    return CartridgeLoader()


class TestCartridgeLoader:
    def test_load_manifest(self, loader: CartridgeLoader, sample_cartridge_dir: Path):
        manifest = loader.load_manifest(sample_cartridge_dir / "cartridge.json")
        assert isinstance(manifest, CartridgeManifest)
        assert manifest.name == "my-cartridge"

    def test_load_missing_manifest_raises(self, loader: CartridgeLoader, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            loader.load_manifest(tmp_path / "nonexistent" / "cartridge.json")

    def test_load_invalid_json_raises(self, loader: CartridgeLoader, tmp_path: Path):
        bad_file = tmp_path / "cartridge.json"
        bad_file.write_text("{invalid json")
        with pytest.raises(ValueError, match="Invalid JSON"):
            loader.load_manifest(bad_file)

    def test_validate_cartridge_dir(self, loader: CartridgeLoader, sample_cartridge_dir: Path):
        errors = loader.validate_directory(sample_cartridge_dir)
        assert errors == []

    def test_validate_missing_manifest(self, loader: CartridgeLoader, tmp_path: Path):
        errors = loader.validate_directory(tmp_path)
        assert any("cartridge.json" in e for e in errors)

    def test_validate_missing_system_prompt(
        self, loader: CartridgeLoader, sample_cartridge_dir: Path
    ):
        (sample_cartridge_dir / "prompts" / "system.txt").unlink()
        errors = loader.validate_directory(sample_cartridge_dir)
        assert any("system_prompt" in e.lower() or "prompts/system.txt" in e for e in errors)

    def test_pack_creates_archive(
        self, loader: CartridgeLoader, sample_cartridge_dir: Path, tmp_path: Path
    ):
        archive_path = tmp_path / "my-cartridge.cartridge"
        result = loader.pack(sample_cartridge_dir, archive_path)
        assert result.exists()
        assert result.suffix == ".cartridge"
        assert result.stat().st_size > 0

    def test_unpack_restores_contents(
        self, loader: CartridgeLoader, sample_cartridge_dir: Path, tmp_path: Path
    ):
        archive_path = tmp_path / "my-cartridge.cartridge"
        loader.pack(sample_cartridge_dir, archive_path)
        unpack_dir = tmp_path / "unpacked"
        loader.unpack(archive_path, unpack_dir)
        assert (unpack_dir / "cartridge.json").exists()
        assert (unpack_dir / "prompts" / "system.txt").exists()
        manifest = loader.load_manifest(unpack_dir / "cartridge.json")
        assert manifest.name == "my-cartridge"

    def test_pack_validates_first(self, loader: CartridgeLoader, tmp_path: Path):
        """Packing an invalid cartridge directory should raise."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        with pytest.raises(ValueError, match="Cannot pack invalid"):
            loader.pack(empty_dir, tmp_path / "out.cartridge")
