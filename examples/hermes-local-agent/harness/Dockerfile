FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates curl jq zstd \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama runtime in-container.
RUN curl -fsSL https://ollama.com/install.sh | sh

# Minimal hermes-compatible wrapper for cartridge dogfood runs.
COPY harness/hermes /usr/local/bin/hermes
RUN chmod +x /usr/local/bin/hermes

ENTRYPOINT ["hermes"]
