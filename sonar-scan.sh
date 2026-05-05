#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".env"
TOKEN_KEY="SONAR_TOKEN"

# Read or prompt for token
if grep -q "^${TOKEN_KEY}=" "$ENV_FILE" 2>/dev/null; then
  SONAR_TOKEN=$(grep "^${TOKEN_KEY}=" "$ENV_FILE" | cut -d'=' -f2)
  echo "[sonar] Using token from $ENV_FILE"
else
  read -rsp "SonarQube token: " SONAR_TOKEN
  echo
  echo "${TOKEN_KEY}=${SONAR_TOKEN}" >> "$ENV_FILE"
  echo "[sonar] Token saved to $ENV_FILE"
fi

# Run tests inside the app container (isolated)
APP_CONTAINER=$(docker compose -f compose.yml ps -q app | head -1)
if [ -n "$APP_CONTAINER" ]; then
  echo "[sonar] Running tests inside container ${APP_CONTAINER}..."
  docker exec "$APP_CONTAINER" \
    env PYTHONPATH=/app COVERAGE_FILE=/tmp/.coverage \
    pytest --cov=src --cov-report=xml:/tmp/coverage.xml tests/ -q
  # Copy coverage.xml to host so sonar-scanner can read it
  docker cp "${APP_CONTAINER}:/tmp/coverage.xml" ./coverage.xml
  # Rewrite container paths (/app) to match sonar-scanner mount (/usr/src)
  sed -i 's|/app/|/usr/src/|g' ./coverage.xml
else
  echo "[sonar] WARN: app container not running, skipping coverage"
fi

# Run scanner
echo "[sonar] Starting analysis..."
docker run --rm \
  --network fastapi_net \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.token="${SONAR_TOKEN}"

echo "[sonar] Done. Results at http://localhost:9100"
