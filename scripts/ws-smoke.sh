#!/usr/bin/env bash
set -euo pipefail
WS_BASE="${1:-ws://127.0.0.1:8000/ws/audio}"
WAV="${2:-test_16k.wav}"

PY="./.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "❌ python3 not found"; exit 1; }

# ensure websockets present (client deps)
"$PY" -c 'import websockets' 2>/dev/null || { "$PY" -m pip install -q --upgrade pip >/dev/null; "$PY" -m pip install -q websockets >/dev/null; }

[ -f .auth_token ] || { echo "❌ .auth_token missing; run: ./scripts/ws-login.sh <email>"; exit 2; }
TOKEN="$(tr -d '\r\n' < .auth_token)"
[ -n "$TOKEN" ] || { echo "❌ .auth_token empty; re-login"; exit 3; }

URL="${WS_BASE}?token=${TOKEN}"
echo "WS_URL=$URL"
WS_URL="$URL" "$PY" ws_file_tts_client_stable.py "$WAV"
