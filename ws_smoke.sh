#!/usr/bin/env bash
set -euo pipefail

# Pick a Python (prefer the venv)
PY="${PY:-./.venv/bin/python}"
[ -x "$PY" ] || PY="$(command -v python3)"

# Ensure websockets client is importable (quietly install if missing)
"$PY" - <<'PY' 2>/dev/null || "$PY" -m pip install -q websockets
import websockets  # noqa
PY

echo "== 1) Get fresh token via OTP =="
EMAIL="${EMAIL:-tester@vakta.ai}"
./scripts/ws-login.sh "$EMAIL" >/dev/null

TOK="$(tr -d '\r\n' < .auth_token)"
LEN=${#TOK}
DOTS="$(printf "%s" "$TOK" | grep -o '\.' | wc -l | tr -d '[:space:]')"
echo "token len: $LEN dots: $DOTS"
if [ "$DOTS" -ne 2 ]; then
  echo "❌ bad token format (expected 2 dots)"; exit 1
fi

echo "— header —"
"$PY" ws_audio_ping.py --mode header

echo "— query —"
"$PY" ws_audio_ping.py --mode query

echo "✅ WS smoke test passed"
