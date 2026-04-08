"""Tendos CLI — command-line interface for cartridge management."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from tendos import __version__


@click.group()
@click.version_option(version=__version__, prog_name="tendos")
def cli() -> None:
    """Tendos — Plug-and-play AI cartridge hub."""


@cli.command()
@click.argument("name")
def init(name: str) -> None:
    """Initialize a new cartridge project."""
    cartridge_dir = Path(name)
    if cartridge_dir.exists():
        click.echo(f"Error: Directory '{name}' already exists.", err=True)
        sys.exit(1)

    cartridge_dir.mkdir(parents=True)
    (cartridge_dir / "prompts").mkdir()
    (cartridge_dir / "prompts" / "system.txt").write_text("You are a helpful AI assistant.\n")

    manifest = {
        "name": name,
        "version": "0.1.0",
        "author": "your-username",
        "domain": "general",
        "description": f"A Tendos cartridge: {name}",
        "license": "Apache-2.0",
        "model": {"base": "llama-3.3-8b-q4", "source": "ollama"},
        "agent": {"system_prompt": "prompts/system.txt"},
    }
    (cartridge_dir / "cartridge.json").write_text(json.dumps(manifest, indent=2) + "\n")
    click.echo(f"Cartridge '{name}' initialized at ./{name}/")


@cli.command()
@click.argument("manifest_path")
def validate(manifest_path: str) -> None:
    """Validate a cartridge.json manifest."""
    from tendos.cartridge.loader import CartridgeLoader

    loader = CartridgeLoader()
    path = Path(manifest_path)
    try:
        manifest = loader.load_manifest(path)
        click.echo(f"Valid cartridge: {manifest.name} v{manifest.version}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("cartridge_dir")
@click.option("--output", "-o", default=None, help="Output .cartridge file path")
def pack(cartridge_dir: str, output: str | None) -> None:
    """Pack a cartridge directory into a .cartridge archive."""
    from tendos.cartridge.loader import CartridgeLoader

    loader = CartridgeLoader()
    source = Path(cartridge_dir)
    output_path = Path(f"{source.name}.cartridge") if output is None else Path(output)

    try:
        result = loader.pack(source, output_path)
        click.echo(f"Packed: {result}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Pack failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("archive_path")
@click.option("--key", required=False, help="Path to private key file")
@click.option("--pub", required=False, help="Path to public key file")
@click.option("--generate-key", is_flag=True, help="Generate a new key pair")
def sign(archive_path: str, key: str | None, pub: str | None, generate_key: bool) -> None:
    """Sign a .cartridge archive."""
    from tendos.security.signing import CartridgeSigner, KeyPair

    archive = Path(archive_path)
    if not archive.exists():
        click.echo(f"Archive not found: {archive}", err=True)
        sys.exit(1)

    if generate_key:
        keypair = KeyPair.generate()
        if key:
            key_path = Path(key)
            pub_path = Path(pub) if pub else key_path.with_suffix(".pub")
            keypair.save(key_path, pub_path)
            click.echo(f"Generated key pair: {key_path}, {pub_path}")
    elif key:
        key_path = Path(key)
        pub_path = Path(pub) if pub else key_path.with_suffix(".pub")
        keypair = KeyPair.load(key_path, pub_path)
    else:
        click.echo("Provide --key or --generate-key", err=True)
        sys.exit(1)

    signer = CartridgeSigner(keypair)
    sig = signer.sign_file(archive)
    sig_path = archive.with_suffix(archive.suffix + ".sig")
    sig_path.write_bytes(sig)
    click.echo(f"Signed: {sig_path}")


@cli.command()
@click.argument("archive_path")
@click.option("--pub", required=True, help="Path to public key file")
@click.option("--sig", required=True, help="Path to signature file")
def verify(archive_path: str, pub: str, sig: str) -> None:
    """Verify a .cartridge archive signature."""
    from tendos.security.signing import CartridgeSigner

    archive = Path(archive_path)
    sig_path = Path(sig)
    pub_path = Path(pub)

    for p in [archive, sig_path, pub_path]:
        if not p.exists():
            click.echo(f"File not found: {p}", err=True)
            sys.exit(1)

    public_key_bytes = pub_path.read_bytes()
    signer = CartridgeSigner.from_public_bytes(public_key_bytes)
    signature = sig_path.read_bytes()

    if signer.verify_file(archive, signature):
        click.echo("Signature valid.")
    else:
        click.echo("Signature INVALID!", err=True)
        sys.exit(1)
