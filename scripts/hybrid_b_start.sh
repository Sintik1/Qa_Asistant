#!/usr/bin/env bash
# Hybrid B runtime helper (local Mac):
# 1) Ensure Ollama is up on :11434
# 2) Expose local Flask :5001 via public tunnel (Serveo by default)
# 3) Print values for GitHub Variable VITE_API_BASE_URL + CORS
#
# Usage:
#   ./scripts/hybrid_b_start.sh
#   ./scripts/hybrid_b_start.sh --provider cloudflared   # needs working DNS (no Clash fake-IP)
#   ./scripts/hybrid_b_start.sh --provider bore
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="${ROOT}/.tools"
PATH="${TOOLS}:${HOME}/.local/ollama-v0.6.5:${HOME}/.local/bin:${PATH}"
PROVIDER="serveo"
for arg in "$@"; do
  case "$arg" in
    --provider=*) PROVIDER="${arg#*=}" ;;
    --provider) shift_next=1 ;;
    cloudflared|serveo|bore|pinggy) PROVIDER="$arg" ;;
  esac
done

mkdir -p "${ROOT}/logs"

OLLAMA_BIN="${HOME}/.local/ollama-v0.6.5/ollama"
if [[ ! -x "$OLLAMA_BIN" ]]; then
  OLLAMA_BIN="$(command -v ollama || true)"
fi
if [[ -z "${OLLAMA_BIN}" ]]; then
  echo "ERROR: ollama not found. Run ./scripts/setup_ollama.sh 1.5b"
  exit 1
fi

if ! curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null; then
  echo "Starting Ollama…"
  env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
    OLLAMA_HOST=127.0.0.1:11434 OLLAMA_LLM_LIBRARY=cpu \
    nohup "$OLLAMA_BIN" serve >"${ROOT}/logs/ollama-serve.log" 2>&1 &
  echo $! >"${ROOT}/logs/ollama.pid"
  for _ in $(seq 1 40); do
    curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null && break
    sleep 1
  done
fi
if ! curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null; then
  echo "ERROR: Ollama not reachable on :11434 (see logs/ollama-serve.log)"
  exit 1
fi
echo "Ollama OK on http://127.0.0.1:11434"

if ! curl -sf "http://127.0.0.1:5001/api/health" >/dev/null; then
  echo "WARN: Flask not on :5001 — start it first:"
  echo "  set -a && source .env && set +a && .venv/bin/python -m flask --app wsgi run -p 5001 --host 127.0.0.1"
  exit 1
fi
echo "Flask OK on http://127.0.0.1:5001"

API_LOG="${ROOT}/logs/api-tunnel.log"
: >"$API_LOG"
API_PUBLIC=""

start_serveo() {
  nohup ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 \
    -R 80:127.0.0.1:5001 serveo.net >"$API_LOG" 2>&1 &
  echo $! >"${ROOT}/logs/api-tunnel.pid"
  for _ in $(seq 1 40); do
    API_PUBLIC="$(grep -oE 'https://[^[:space:]]+' "$API_LOG" | head -1 | tr -d '\r' || true)"
    if [[ -n "$API_PUBLIC" ]]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

start_cloudflared() {
  local bin="${TOOLS}/cloudflared"
  if [[ ! -x "$bin" ]]; then
    echo "ERROR: ${bin} missing"
    return 1
  fi
  env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
    nohup "$bin" tunnel --url "http://127.0.0.1:5001" --protocol http2 --no-autoupdate \
    >"$API_LOG" 2>&1 &
  echo $! >"${ROOT}/logs/api-tunnel.pid"
  for _ in $(seq 1 40); do
    API_PUBLIC="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$API_LOG" | head -1 || true)"
    if [[ -n "$API_PUBLIC" ]]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

start_bore() {
  local bin="${TOOLS}/bore"
  if [[ ! -x "$bin" ]]; then
    echo "ERROR: ${bin} missing"
    return 1
  fi
  nohup "$bin" local 5001 --to bore.pub >"$API_LOG" 2>&1 &
  echo $! >"${ROOT}/logs/api-tunnel.pid"
  for _ in $(seq 1 40); do
    API_PUBLIC="$(grep -oE 'https?://[^[:space:]]+' "$API_LOG" | head -1 || true)"
    if [[ -n "$API_PUBLIC" ]]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

start_pinggy() {
  nohup ssh -p 443 -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 \
    -R0:127.0.0.1:5001 a.pinggy.io >"$API_LOG" 2>&1 &
  echo $! >"${ROOT}/logs/api-tunnel.pid"
  for _ in $(seq 1 40); do
    API_PUBLIC="$(grep -oE 'https://[a-zA-Z0-9.-]+\.(pinggy\.link|pinggy\.net|run\.pinggy-free\.link)' "$API_LOG" | head -1 || true)"
    if [[ -n "$API_PUBLIC" ]]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

echo "Starting API tunnel via ${PROVIDER}…"
case "$PROVIDER" in
  serveo) start_serveo || true ;;
  cloudflared) start_cloudflared || true ;;
  bore) start_bore || true ;;
  pinggy) start_pinggy || true ;;
  *) echo "Unknown provider: $PROVIDER"; exit 1 ;;
esac

if [[ -z "$API_PUBLIC" ]]; then
  echo "ERROR: could not parse public URL from ${API_LOG}"
  tail -40 "$API_LOG" || true
  exit 1
fi

echo "$API_PUBLIC" >"${ROOT}/logs/api-tunnel.url"
echo
echo "=== Hybrid B public API ==="
echo "Public API: ${API_PUBLIC}"
echo
echo "GitHub Actions Variable:"
echo "  VITE_API_BASE_URL=${API_PUBLIC}"
echo
echo "Flask .env (already local Ollama):"
echo "  CORS_ORIGINS=...,https://sintik1.github.io"
echo "  OAUTH_PUBLIC_APP_URL=https://sintik1.github.io/Qa_Asistant"
echo "  OAUTH_API_PUBLIC_URL=${API_PUBLIC}"
echo
echo "Keep Mac awake. Guide: docs/HYBRID_LOCAL_AI.md"
