#!/bin/sh
# Checks a running Compose stack (docker compose up -d --wait) end to end.
set -eu
BASE=${BASE:-http://localhost:8080}

curl -fsS "$BASE/api/health/" | grep -q '"ok"'
curl -fsS "$BASE/" | grep -q '<div id="root">'
curl -fsSI "$BASE/" | grep -qi '^content-security-policy:'
curl -fsS "$BASE/api/schema/" | grep -q 'openapi:'
curl -fsS "$BASE/admin/login/" | grep -q 'Django'
echo "smoke test passed: $BASE"
