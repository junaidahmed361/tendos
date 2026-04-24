# Hermes Local Agent Tendo (Dogfood)

This example tendo demonstrates a local cartridge that launches Hermes with a memory-friendly Ollama base model.

Model choice:
- `qwen2.5:3b` (small enough for most local setups while still useful)

## Files

- `cartridge.json` — cartridge manifest
- `prompts/system.txt` — system prompt
- `harness/harness.yaml` — harness declarations and launcher command

## Run locally

```bash
# From repo root
uv run tendos validate examples/hermes-local-agent/cartridge.json
uv run tendos pack examples/hermes-local-agent/

# Ensure model exists locally
ollama pull qwen2.5:3b

# Launch using harness command (direct)
hermes --model ollama/qwen2.5:3b --prompt-file examples/hermes-local-agent/prompts/system.txt
```
