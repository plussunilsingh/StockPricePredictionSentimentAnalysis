#!/usr/bin/env bash
set -euo pipefail

# healthcheck.sh
# Return 0 when both backend and frontend are responding
# Backend: localhost:${BACKEND_PORT:-8000}
# Frontend: localhost:${PORT:-7860}

HOST=127.0.0.1
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${PORT:-7860}
TIMEOUT=${HC_TIMEOUT:-3}

check_url() {
  local url="$1"
  if curl -sf --max-time $TIMEOUT "$url" >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Check backend (try / or /docs)
if check_url "http://$HOST:$BACKEND_PORT/" || check_url "http://$HOST:$BACKEND_PORT/docs"; then
  backend_ok=1
else
  backend_ok=0
fi

# Check frontend (Streamlit serves some HTML at /)
if check_url "http://$HOST:$FRONTEND_PORT/"; then
  frontend_ok=1
else
  frontend_ok=0
fi

if [ $backend_ok -eq 1 ] && [ $frontend_ok -eq 1 ]; then
  exit 0
else
  echo "healthcheck failed: backend_ok=$backend_ok frontend_ok=$frontend_ok"
  exit 1
fi

