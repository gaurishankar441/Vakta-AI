#!/usr/bin/env bash
set -euo pipefail
EMAIL="${1:-tester@vakta.ai}"
RID="$(docker ps --format '{{.Names}}' | grep -E 'redis' | head -n1 || true)"
[ -n "$RID" ] || { echo "❌ Redis container not found"; exit 2; }

echo "→ request OTP for $EMAIL"
curl -s -X POST http://127.0.0.1:8000/api/auth/otp/request \
  -H 'content-type: application/json' \
  -d "{\"email\":\"$EMAIL\"}" >/dev/null || true

echo "→ read OTP from redis (plain + %40, short poll)"
CODE=""
for i in $(seq 1 24); do
  CODE="$(docker exec -i "$RID" sh -lc "redis-cli --raw GET 'otp:$EMAIL' 2>/dev/null || true" | tr -d '\r\n')"
  [ -n "$CODE" ] || CODE="$(docker exec -i "$RID" sh -lc "redis-cli --raw GET 'otp:${EMAIL//@/%40}' 2>/dev/null || true" | tr -d '\r\n')"
  [ -n "$CODE" ] && break
  sleep 0.25
done
[ -n "$CODE" ] || { echo "❌ OTP not visible yet; run again"; exit 3; }
echo "OTP=$CODE"

RESP="$(curl -s -X POST http://127.0.0.1:8000/api/auth/otp/verify \
  -H 'content-type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"code\":\"$CODE\"}")"
echo "[verify] $RESP"

PY="./.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "❌ python3 not found"; exit 4; }

TOKEN="$("$PY" -c 'import sys,json; d=sys.stdin.read().strip(); print(json.loads(d).get("access_token","") if d.startswith("{") else "")' <<<"$RESP")"
printf '%s' "$TOKEN" > .auth_token
echo "Saved .auth_token: $( [ -n "$TOKEN" ] && echo "${TOKEN:0:28}..." || echo "(empty)")"
[ -n "$TOKEN" ] || { echo "❌ empty token (OTP may have expired). re-run."; exit 5; }
