#!/usr/bin/env bash
# Create CI/CD step 6 Issue from YOUR machine (agent cannot reach api.github.com).
# Usage (in Terminal.app, after: gh auth login):
#   ./scripts/create_step6_issue.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install gh: https://cli.github.com/  or: brew install gh"
  exit 1
fi

gh auth status

URL="$(gh issue create --repo Sintik1/Qa_Asistant \
  --title "CI/CD ДЗ шаг 6: мониторинг UptimeRobot + health checks" \
  --body "$(cat <<'EOF'
## CI/CD ДЗ шаг 6 — Мониторинг (UptimeRobot)

Parent: #37

### Done
- Commit `3d35a57` — health checks + docs + watcher + tests
- Docs: `docs/UPTIME_SETUP.md`
- Status: **done (awaiting OK)**

EOF
)")"

echo "Created: $URL"
