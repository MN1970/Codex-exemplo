#!/bin/bash

# Test Webhook Script
# Send test webhooks to local webhook server

set -e

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:3000/webhooks/cowork}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:-test-secret-key-12345}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log functions
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to send webhook
send_webhook() {
  local event_type=$1
  local data=$2
  local description=$3

  log_info "Sending $description..."

  # Create payload
  local payload=$(cat <<EOF
{
  "event": "$event_type",
  "data": $data
}
EOF
)

  # Generate signature
  local signature=$(echo -n "$payload" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" -hex | cut -d' ' -f2)

  # Send webhook
  local response=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -H "X-Webhook-Signature: $signature" \
    -d "$payload" \
    -w "\n%{http_code}")

  local http_code=$(echo "$response" | tail -n1)
  local body=$(echo "$response" | head -n-1)

  if [ "$http_code" -eq 202 ] || [ "$http_code" -eq 200 ]; then
    log_info "✓ Success (HTTP $http_code)"
    local delivery_id=$(echo "$body" | grep -o '"deliveryId":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$delivery_id" ]; then
      log_info "  Delivery ID: $delivery_id"
    fi
  else
    log_error "✗ Failed (HTTP $http_code)"
    log_error "  Response: $body"
  fi

  echo ""
}

# Function to check status
check_status() {
  log_info "Checking webhook status..."

  local response=$(curl -s "$WEBHOOK_URL/../status")
  echo "$response" | jq '.' 2>/dev/null || echo "$response"

  echo ""
}

# Function to get audit log
get_audit_log() {
  local limit=${1:-10}
  log_info "Fetching audit log (last $limit entries)..."

  local response=$(curl -s "$WEBHOOK_URL/../audit-log?limit=$limit")
  echo "$response" | jq '.' 2>/dev/null || echo "$response"

  echo ""
}

# Function to check health
check_health() {
  log_info "Checking webhook health..."

  local response=$(curl -s "$WEBHOOK_URL/../health")
  echo "$response" | jq '.' 2>/dev/null || echo "$response"

  echo ""
}

# Main script

echo ""
log_info "Cowork Webhook Test Suite"
log_info "Webhook URL: $WEBHOOK_URL"
log_info "Secret: $WEBHOOK_SECRET (first 10 chars: ${WEBHOOK_SECRET:0:10}***)"
echo ""

# Check if server is running
log_info "Testing server connectivity..."
if ! curl -s -f "$WEBHOOK_URL/../status" > /dev/null 2>&1; then
  log_error "Cannot connect to webhook server at $WEBHOOK_URL"
  log_error "Make sure the server is running: npm run dev"
  exit 1
fi
log_info "✓ Server is running"
echo ""

# Test 1: PR_OPENED event
send_webhook "pr.opened" \
  '{"pr_id":"123","title":"Fix authentication bug","author":"alice","target_branch":"main"}' \
  "PR_OPENED event"

# Test 2: COMMIT event
send_webhook "commit" \
  '{"commit_sha":"abc123def456","message":"Fix auth validation","author":"bob","branch":"feature/auth"}' \
  "COMMIT event"

# Test 3: TASK_UPDATED event
send_webhook "task.updated" \
  '{"task_id":"task-001","status":"in_progress","assignee":"charlie","priority":"high"}' \
  "TASK_UPDATED event"

# Test 4: Multiple events (stress test light)
log_info "Sending 5 rapid webhooks..."
for i in {1..5}; do
  send_webhook "commit" \
    '{"commit_sha":"sha'$i'","message":"Test commit '$i'","author":"test","branch":"test"}' \
    "Rapid commit #$i" &
done
wait

# Wait for processing
sleep 1

# Check status
check_status

# Get audit log
get_audit_log 20

# Check health
check_health

log_info "✓ All tests completed"
