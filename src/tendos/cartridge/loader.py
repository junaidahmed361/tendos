"""Cartridge loader — load, validate, pack, and unpack cartridge archives."""

from __future__ import annotations

import json
import tarfile
from typing import TYPE_CHECKING

from pydantic import ValidationError

from tendos.cartridge.schema import CartridgeManifest

if TYPE_CHECKING:
    from pathlib import Path


class CartridgeLoader:
    """Load, validate, pack, and unpack .cartridge archives."""

    def load_manifest(self, path: Path) -> CartridgeManifest:
        """Load and validate a cartridge.json manifest file."""
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        text = path.read_text(encoding="utf-8")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}") from e
        try:
            return CartridgeManifest(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid cartridge manifest: {e}") from e

    def validate_directory(self, cartridge_dir: Path) -> list[str]:
        """Validate a cartridge directory structure. Returns list of error strings."""
        errors: list[str] = []
        manifest_path = cartridge_dir / "cartridge.json"
        if not manifest_path.exists():
            errors.append("Missing cartridge.json manifest file")
            return errors
        try:
            manifest = self.load_manifest(manifest_path)
        except (ValueError, FileNotFoundError) as e:
            errors.append(f"Invalid manifest: {e}")
            return errors
        # Validate referenced files exist
        prompt_path = cartridge_dir / manifest.agent.system_prompt
        if not prompt_path.exists():
            errors.append(f"Missing system_prompt file: {manifest.agent.system_prompt}")
        for lora in manifest.model.loras:
            lora_path = cartridge_dir / lora.path
            if not lora_path.exists():
                errors.append(f"Missing LoRA adapter: {lora.path}")
        for tool in manifest.agent.tools:
            tool_path = cartridge_dir / tool.definition_path
            if not tool_path.exists():
                errors.append(f"Missing tool definition: {tool.definition_path}")
        if manifest.agent.dag_path:
            dag_path = cartridge_dir / manifest.agent.dag_path
            if not dag_path.exists():
                errors.append(f"Missing DAG file: {manifest.agent.dag_path}")
        return errors

    def pack(self, cartridge_dir: Path, output_path: Path) -> Path:
        """Pack a cartridge directory into a .cartridge archive (tar.gz)."""
        errors = self.validate_directory(cartridge_dir)
        if errors:
            raise ValueError(f"Cannot pack invalid cartridge: {'; '.join(errors)}")
        with tarfile.open(output_path, "w:gz") as tar:
            for item in sorted(cartridge_dir.rglob("*")):
                arcname = item.relative_to(cartridge_dir)
                tar.add(item, arcname=str(arcname))
        return output_path

    def unpack(self, archive_path: Path, output_dir: Path) -> Path:
        """Unpack a .cartridge archive to a directory."""
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        output_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive_path, "r:gz") as tar:
            # Use filter="data" on Python 3.12+ for security;
            # fall back to basic extractall on older versions.
            import sys

            if sys.version_info >= (3, 12):
                tar.extractall(path=output_dir, filter="data")  # noqa: S202  # nosec B202
            else:
                tar.extractall(path=output_dir)  # noqa: S202  # nosec B202
        return output_dir
