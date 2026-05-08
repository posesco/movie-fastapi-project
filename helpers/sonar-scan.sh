#!/usr/bin/env bash
set -euo pipefail

# Get absolute paths regardless of where script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
TOKEN_KEY="SONAR_TOKEN"

# Read or prompt for token
if [ -f "$ENV_FILE" ] && grep -q "^${TOKEN_KEY}=" "$ENV_FILE" 2>/dev/null; then
  # Extract token and strip potential quotes
  SONAR_TOKEN=$(grep "^${TOKEN_KEY}=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
  echo "[sonar] Using token from $ENV_FILE"
else
  read -rsp "SonarQube token: " SONAR_TOKEN
  echo
  echo "${TOKEN_KEY}=${SONAR_TOKEN}" >> "$ENV_FILE"
  echo "[sonar] Token saved to $ENV_FILE"
fi

# Run tests inside the app container (isolated)
# Use project name 'fastapi_stack' as defined in compose.yml
APP_CONTAINER=$(docker compose -f "$PROJECT_ROOT/compose.yml" ps -q app | head -1)
if [ -n "$APP_CONTAINER" ]; then
  echo "[sonar] Running tests inside container ${APP_CONTAINER}..."
  # Use /tmp for coverage files to avoid permission issues in /app/tests
  docker exec "$APP_CONTAINER" \
    env PYTHONPATH=/app COVERAGE_FILE=/tmp/.coverage \
    pytest --cov=src --cov-report=xml:/tmp/coverage.xml tests/ -q
  
  # Copy coverage.xml to helpers/ so sonar-scanner finds it (as per sonar-project.properties)
  docker cp "${APP_CONTAINER}:/tmp/coverage.xml" "$SCRIPT_DIR/coverage.xml"
  
  # Rewrite container paths (/app) to match sonar-scanner mount (/usr/src)
  # Linux sed -i works fine here
  sed -i 's|/app/|/usr/src/|g' "$SCRIPT_DIR/coverage.xml"
else
  echo "[sonar] WARN: app container not running, skipping coverage"
fi

# Run scanner from project root
echo "[sonar] Starting analysis..."
docker run --rm \
  --network fastapi_net \
  -v "$PROJECT_ROOT:/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.token="${SONAR_TOKEN}"

echo "[sonar] Done. Results at http://localhost:9100"
