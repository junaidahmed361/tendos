"""Tendos CLI — command-line interface for cartridge management."""

from __future__ import annotations

import json
import os
import subprocess  # nosec B404
import sys
from pathlib import Path

import click
import yaml

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
    (cartridge_dir / "harness").mkdir()
    (cartridge_dir / "prompts" / "system.txt").write_text("You are a helpful AI assistant.\n")
    (cartridge_dir / "harness" / "harness.yaml").write_text(
        """
security_guardrails:
  - prompt_injection_detection
  - tool_allowlist
pii_redaction:
  enabled: true
  strategy: mask
update_sync:
  strategy: signed_pull
  interval: weekly
  signed_updates_required: true
""".lstrip()
    )

    manifest = {
        "name": name,
        "version": "0.1.0",
        "author": "your-username",
        "domain": "general",
        "description": f"A Tendos cartridge: {name}",
        "license": "Apache-2.0",
        "model": {"base": "llama-3.3-8b-q4", "source": "ollama"},
        "agent": {"system_prompt": "prompts/system.txt"},
        "harness": {"yaml_path": "harness/harness.yaml"},
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
@click.argument("cartridge_path")
@click.option("--dry-run", is_flag=True, help="Print launcher command without executing")
def run(cartridge_path: str, dry_run: bool) -> None:
    """Run a cartridge harness launcher command."""
    from tendos.cartridge.loader import CartridgeLoader

    source_path = Path(cartridge_path)
    cartridge_dir = source_path if source_path.is_dir() else source_path.parent
    manifest_path = source_path / "cartridge.json" if source_path.is_dir() else source_path

    loader = CartridgeLoader()
    try:
        manifest = loader.load_manifest(manifest_path)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Run failed: {e}", err=True)
        sys.exit(1)

    launcher: dict[str, object] | None = None
    if manifest.harness and manifest.harness.yaml_path:
        harness_path = cartridge_dir / manifest.harness.yaml_path
        if not harness_path.exists():
            click.echo(f"Run failed: Missing harness yaml: {manifest.harness.yaml_path}", err=True)
            sys.exit(1)
        parsed = yaml.safe_load(harness_path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            raw_launcher = parsed.get("launcher")
            if isinstance(raw_launcher, dict):
                launcher = raw_launcher

    if launcher is None and manifest.harness and manifest.harness.declarations:
        raw_launcher = manifest.harness.declarations.custom_config.get("launcher")
        if isinstance(raw_launcher, dict):
            launcher = raw_launcher

    if launcher is None:
        click.echo("Run failed: harness launcher definition not found", err=True)
        sys.exit(1)

    launcher_type = launcher.get("type", "command")
    if launcher_type not in {"command", "docker"}:
        click.echo("Run failed: launcher.type must be 'command' or 'docker'", err=True)
        sys.exit(1)

    if launcher_type == "docker":
        image_obj = launcher.get("image")
        image = (
            image_obj
            if isinstance(image_obj, str)
            else f"tendos/{manifest.name}:{manifest.version}"
        )

        build_obj = launcher.get("build")
        build_cmd: list[str] | None = None
        if isinstance(build_obj, dict):
            context_obj = build_obj.get("context", ".")
            if not isinstance(context_obj, str) or not context_obj:
                click.echo(
                    "Run failed: launcher.build.context must be a non-empty string", err=True
                )
                sys.exit(1)
            context_dir = (cartridge_dir / context_obj).resolve()
            build_cmd = ["docker", "build", "-t", image]
            dockerfile_obj = build_obj.get("dockerfile")
            if isinstance(dockerfile_obj, str) and dockerfile_obj:
                build_cmd.extend(["-f", str((cartridge_dir / dockerfile_obj).resolve())])
            build_cmd.append(str(context_dir))

        command_obj = launcher.get("command")
        args_obj = launcher.get("args", [])
        if command_obj is not None and (not isinstance(command_obj, str) or not command_obj):
            click.echo(
                "Run failed: launcher.command must be a non-empty string when provided", err=True
            )
            sys.exit(1)
        if not isinstance(args_obj, list) or any(not isinstance(v, str) for v in args_obj):
            click.echo("Run failed: launcher.args must be a list of strings", err=True)
            sys.exit(1)
        args: list[str] = args_obj

        env_args: list[str] = []
        raw_env = launcher.get("env", {})
        if isinstance(raw_env, dict):
            for key, value in raw_env.items():
                env_args.extend(["-e", f"{key}={value}"])

        port_args: list[str] = []
        ports_obj = launcher.get("ports", [])
        if isinstance(ports_obj, list) and all(isinstance(v, str) for v in ports_obj):
            for port in ports_obj:
                port_args.extend(["-p", port])

        volume_args: list[str] = []
        volumes_obj = launcher.get("volumes", [])
        if isinstance(volumes_obj, list) and all(isinstance(v, str) for v in volumes_obj):
            for volume in volumes_obj:
                volume_args.extend(["-v", volume])

        docker_run_cmd = ["docker", "run", "--rm", *env_args, *port_args, *volume_args, image]
        if isinstance(command_obj, str) and command_obj:
            docker_run_cmd.append(command_obj)
        docker_run_cmd.extend(args)

        if build_cmd is not None:
            click.echo(f"Launcher build command: {' '.join(build_cmd)}")
        click.echo(f"Launcher command: {' '.join(docker_run_cmd)}")
        if dry_run:
            return

        if build_cmd is not None:
            build_result = subprocess.run(  # noqa: S603  # nosec B603
                build_cmd,
                cwd=cartridge_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if build_result.stdout:
                click.echo(build_result.stdout.rstrip("\n"))
            if build_result.stderr:
                click.echo(build_result.stderr.rstrip("\n"), err=True)
            if build_result.returncode != 0:
                click.echo(
                    f"Run failed: docker build exited with code {build_result.returncode}",
                    err=True,
                )
                sys.exit(build_result.returncode)

        run_result = subprocess.run(  # noqa: S603  # nosec B603
            docker_run_cmd,
            cwd=cartridge_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if run_result.stdout:
            click.echo(run_result.stdout.rstrip("\n"))
        if run_result.stderr:
            click.echo(run_result.stderr.rstrip("\n"), err=True)
        if run_result.returncode != 0:
            click.echo(f"Run failed: launcher exited with code {run_result.returncode}", err=True)
            sys.exit(run_result.returncode)
        return

    command = launcher.get("command")
    args_obj = launcher.get("args", [])
    if not isinstance(command, str) or not command:
        click.echo("Run failed: launcher.command must be a non-empty string", err=True)
        sys.exit(1)
    if not isinstance(args_obj, list) or any(not isinstance(v, str) for v in args_obj):
        click.echo("Run failed: launcher.args must be a list of strings", err=True)
        sys.exit(1)
    args = args_obj

    cmd = [command, *args]
    click.echo(f"Launcher command: {' '.join(cmd)}")
    if dry_run:
        return

    env = os.environ.copy()
    raw_env = launcher.get("env", {})
    if isinstance(raw_env, dict):
        env.update({str(k): str(v) for k, v in raw_env.items()})

    run_cwd = cartridge_dir
    raw_cwd = launcher.get("cwd")
    if isinstance(raw_cwd, str) and raw_cwd:
        run_cwd = cartridge_dir / raw_cwd

    result = subprocess.run(  # noqa: S603  # nosec B603
        cmd,
        cwd=run_cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        click.echo(result.stdout.rstrip("\n"))
    if result.stderr:
        click.echo(result.stderr.rstrip("\n"), err=True)
    if result.returncode != 0:
        click.echo(f"Run failed: launcher exited with code {result.returncode}", err=True)
        sys.exit(result.returncode)


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
