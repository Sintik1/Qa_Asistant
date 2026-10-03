#!/usr/bin/env bash
# Local study setup for Mac (esp. M1 8GB / macOS 13 Ventura).
# Usage: ./scripts/setup_ollama.sh [1.5b|3b]
set -euo pipefail

SIZE="${1:-1.5b}"
MODEL="qwen2.5:1.5b"
case "$SIZE" in
  1.5b|1.5|small) MODEL="qwen2.5:1.5b" ;;
  3b|3) MODEL="qwen2.5:3b" ;;
  7b|7)
    echo "WARN: qwen2.5:7b is heavy for 8GB RAM. Prefer 1.5b."
    MODEL="qwen2.5:7b"
    ;;
  *)
    echo "Unknown size '$SIZE'. Use: 1.5b | 3b"
    exit 1
    ;;
esac

MAC_VER="$(sw_vers -productVersion 2>/dev/null || echo unknown)"
echo "macOS: ${MAC_VER}"

export PATH="${HOME}/.local/bin:${PATH}"

# Latest Ollama.app (0.35+) needs macOS 14+. On Ventura 13 use pinned 0.6.5.
need_legacy=0
if [[ "$(uname -s)" == "Darwin" ]]; then
  major="${MAC_VER%%.*}"
  if [[ "$major" -lt 14 ]]; then
    need_legacy=1
  fi
fi

if [[ "$need_legacy" -eq 1 ]]; then
  echo "Detected macOS < 14 → install Ollama v0.6.5 (minos 13) into ~/.local/ollama-v0.6.5"
  INST="${HOME}/.local/ollama-v0.6.5"
  TGZ="/tmp/ollama-darwin-0.6.5.tgz"
  if [[ ! -x "${INST}/ollama" ]]; then
    curl -fsSL -o "$TGZ" \
      "https://github.com/ollama/ollama/releases/download/v0.6.5/ollama-darwin.tgz"
    rm -rf "$INST"
    mkdir -p "$INST"
    tar -xzf "$TGZ" -C "$INST"
  fi
  mkdir -p "${HOME}/.local/bin"
  ln -sf "${INST}/ollama" "${HOME}/.local/bin/ollama"
else
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Install Ollama from https://ollama.com then re-run."
    exit 1
  fi
fi

if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Starting ollama serve..."
  ollama serve >/tmp/ollama-serve.log 2>&1 &
  sleep 3
fi

echo "Pulling ${MODEL} ..."
ollama pull "${MODEL}"

echo
echo "Done. Put in .env:"
echo "  AI_PROVIDER=ollama"
echo "  AI_OLLAMA_SIZE=${SIZE}"
echo "  QA_ASISTANT_MODEL=${MODEL}"
echo "  QA_ASISTANT_API_URL=http://localhost:11434/v1/chat/completions"
echo
echo "Keep server running: ollama serve"
echo "Smoke: curl -s http://localhost:11434/api/tags | jq"
