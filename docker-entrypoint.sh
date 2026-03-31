#!/usr/bin/env bash
set -euo pipefail

# Entrypoint wrapper to start the app inside the container
# Usage: docker run <image> start

APP_ROOT="/app"
cd "$APP_ROOT"

# Ensure /app is on PYTHONPATH so imports like `from com...` work when running scripts
export PYTHONPATH="$APP_ROOT:${PYTHONPATH:-}"

# Default ports
PORT="${PORT:-8005}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

# Ensure logs directory exists so AppConfig can open files
mkdir -p "$APP_ROOT/logs"
chmod -R 755 "$APP_ROOT/logs" || true

# Create .venv in the container and activate it
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate

# Ensure pip is up-to-date and install requirements
python -m pip install --upgrade pip setuptools wheel || true
if [ -f requirements.txt ]; then
  pip install --no-cache-dir -r requirements.txt || true
fi

wait_for_port() {
  host=$1; port=$2; retries=${3:-15};
  i=0
  while ! (python - <<PY
import socket,sys
s=socket.socket()
try:
  s.connect(("$host", int($port)))
  s.close()
  sys.exit(0)
except Exception:
  sys.exit(1)
PY
  ); do
    i=$((i+1))
    if [ $i -ge $retries ]; then
      echo "Timed out waiting for $host:$port"
      return 1
    fi
    sleep 1
  done
  return 0
}

case "${1:-start}" in
  start)
    echo "Starting backend on 0.0.0.0:$BACKEND_PORT and frontend on 0.0.0.0:$PORT"

    # Start backend (uvicorn) bound to zero host so it's accessible locally and externally
    python -m uvicorn com.stockprediction.backend.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --log-level info &
    backend_pid=$!
    echo "Backend started with PID $backend_pid"

    # Wait briefly for backend
    if ! wait_for_port 127.0.0.1 $BACKEND_PORT 20; then
      echo "Backend failed to start or is not reachable on 127.0.0.1:$BACKEND_PORT"
      kill $backend_pid || true
      exit 1
    fi

    # Start streamlit on the port provided by the environment (Hugging Face uses $PORT)
    echo "Starting Streamlit on 0.0.0.0:$PORT"
    streamlit run com/stockprediction/frontend/app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless true &
    frontend_pid=$!

    # Wait briefly for frontend
    if ! wait_for_port 0.0.0.0 $PORT 30; then
      echo "Frontend failed to start or is not reachable on 0.0.0.0:$PORT"
      kill $backend_pid $frontend_pid || true
      exit 1
    fi

    echo "Container is 'ready'. Both backend and frontend services are responsive."

    # Wait for both processes to keep container alive
    wait $backend_pid $frontend_pid
    ;;
  *)
    exec "$@"
    ;;
esac
