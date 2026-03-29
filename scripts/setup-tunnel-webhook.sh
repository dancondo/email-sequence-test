#!/usr/bin/env bash
set -euo pipefail

# Load .env vars (script runs on host, not in Docker)
set -a
source .env
set +a

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.tunnel.yml"

echo "Waiting for Cloudflare tunnel..."
TUNNEL_URL=""
for i in $(seq 1 30); do
  TUNNEL_URL=$(docker compose ${COMPOSE_FILES} logs tunnel 2>&1 | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | grep -v 'api\.trycloudflare' | head -1 || true)
  if [ -n "$TUNNEL_URL" ]; then
    break
  fi
  sleep 1
done

if [ -z "$TUNNEL_URL" ]; then
  echo "ERROR: Could not detect tunnel URL after 30s"
  echo "Tunnel logs:"
  docker compose ${COMPOSE_FILES} logs tunnel
  exit 1
fi

WEBHOOK_URL="${TUNNEL_URL}/api/webhooks/nylas"

echo ""
echo "==> Tunnel URL: ${TUNNEL_URL}"
echo "==> Webhook URL: ${WEBHOOK_URL}"
echo ""

# Wait until the tunnel URL is reachable
echo "Waiting for tunnel to be reachable..."
for i in $(seq 1 30); do
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' "${TUNNEL_URL}/api/health" || true)
  if [ "$STATUS" = "200" ]; then
    echo "Tunnel is live!"
    break
  fi
  if [ "$i" = "30" ]; then
    echo "ERROR: Tunnel URL not reachable after 30s"
    exit 2
  fi
  sleep 1
done

echo ""

# Create new webhook
echo "Creating Nylas webhook -> ${WEBHOOK_URL}"
RESPONSE=$(curl -s -X POST "https://api.us.nylas.com/v3/webhooks" \
  -H "Authorization: Bearer ${NYLAS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"trigger_types\": [\"message.created\", \"thread.replied\"],
    \"webhook_url\": \"${WEBHOOK_URL}\",
    \"description\": \"Local dev webhook (cloudflare tunnel)\",
    \"notification_email_addresses\": []
  }")

WEBHOOK_SECRET=$(echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'data' in data and data['data']:
    print(data['data'].get('webhook_secret', ''))
elif 'error' in data:
    print('ERROR: ' + json.dumps(data['error']), file=sys.stderr)
    sys.exit(1)
")

if [ -z "$WEBHOOK_SECRET" ]; then
  echo "ERROR: Failed to create webhook. Response:"
  echo "$RESPONSE"
  exit 1
fi

echo "==> Webhook secret obtained"
echo ""

# Restart only the backend with the new secret injected
echo "Restarting backend with new webhook secret..."
NYLAS_WEBHOOK_SECRET="$WEBHOOK_SECRET" docker compose ${COMPOSE_FILES} up -d --no-deps backend

echo ""
echo "Done! Webhook is active."
echo ""
