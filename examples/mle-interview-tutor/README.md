# MLE Interview Tutor Tendo

Containerized local interview tutoring cartridge aligned with daily lesson runner constraints.

Model:
- `qwen2.5-coder:3b` (fast, solid coding-oriented Qwen model for local startup)

## Files

- `cartridge.json` — cartridge manifest
- `prompts/system.txt` — tutoring system contract (subtopic counters + practical-first flow)
- `harness/harness.yaml` — container launcher and governance declarations
- `harness/Dockerfile` — self-contained runtime image (Ollama + hermes-compatible entrypoint)
- `harness/hermes` — in-container shim handling `hermes chat` arguments

## Run

```bash
uv run tendos validate examples/mle-interview-tutor/cartridge.json
uv run tendos run examples/mle-interview-tutor --dry-run
uv run tendos run examples/mle-interview-tutor
```

Notes:
- First run may download `qwen2.5-coder:3b` inside container.
- Model cache persists in Docker volume `tendos-mle-ollama` for faster subsequent launches.
