#!/bin/sh
# Checks a running Compose stack (docker compose up -d --wait) end to end.
set -eu
BASE=${BASE:-http://localhost:8080}

curl -fsS "$BASE/api/health/" | grep -q '"ok"'
curl -fsS "$BASE/" | grep -q '<div id="root">'
curl -fsSI "$BASE/" | grep -qi '^content-security-policy:'
curl -fsS "$BASE/api/schema/" | grep -q 'openapi:'
# the snapshot was loaded: every topic has patents
curl -fsS "$BASE/api/datasets/" | python3 -c 'import json, sys; d = json.load(sys.stdin); assert len(d) >= 3 and all(x["patent_count"] > 0 for x in d), d'
curl -fsS "$BASE/admin/login/" | grep -q 'Django'
echo "smoke test passed: $BASE"
