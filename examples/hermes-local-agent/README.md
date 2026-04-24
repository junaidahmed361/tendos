# Hermes Local Agent Tendo (Dogfood)

This example tendo demonstrates a self-contained local cartridge that launches Hermes-compatible chat inside a container with an in-container Ollama runtime.

Model choice:
- `qwen2.5:0.5b` (small enough for most local setups)

## Files

- `cartridge.json` — cartridge manifest
- `prompts/system.txt` — system prompt
- `harness/harness.yaml` — harness declarations and container launcher command
- `harness/Dockerfile` — self-contained runtime image (Ollama + hermes-compatible entrypoint)
- `harness/hermes` — hermes-compatible wrapper used inside the container

## Run locally

```bash
# From repo root
uv run tendos validate examples/hermes-local-agent/cartridge.json
uv run tendos pack examples/hermes-local-agent/

# Ensure Docker is available
# Build + run the self-contained cartridge runtime
uv run tendos run examples/hermes-local-agent
```
