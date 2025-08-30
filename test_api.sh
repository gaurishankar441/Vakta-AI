#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:8000"
EMAIL="make+$(date +%s)@example.com"
PASS="pass"

echo "== SIGNUP =="
curl -s -X POST "$BASE/api/v1/auth/signup" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | jq .

echo "== LOGIN =="
LOGIN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")

echo "$LOGIN" | jq .
TOKEN=$(echo "$LOGIN" | jq -r .access_token)
echo "TOKEN=${TOKEN:0:20}..."

echo "== ME =="
curl -s "$BASE/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "== CREATE CONVERSATION =="
CONV=$(curl -s -X POST "$BASE/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Demo Thread"}' | jq -r .id)
echo "CONV=$CONV"

echo "== SEND MESSAGE =="
curl -s -X POST "$BASE/api/v1/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"Hello threads via JWT\",\"conversation_id\":\"$CONV\"}" | jq .

echo "== HISTORY =="
curl -s "$BASE/api/v1/chat/history?conversation_id=$CONV&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "== LIST CONVERSATIONS =="
curl -s "$BASE/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" | jq .

