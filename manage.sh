#!/bin/bash

# Configuration and Paths
ROOT_DIR="$(pwd)"

start_services() {
    echo "🚀 Starting Python Full-Stack Data-Driven Stock Price Prediction System..."
    
    # Start Python Backend Service (FastAPI)
    echo "➡ Starting Backend Service (Port 8000)..."
    cd "$ROOT_DIR" || exit
    export PYTHONPATH="$ROOT_DIR"
    nohup "$ROOT_DIR/venv_new/bin/uvicorn" com.stockprediction.backend.main:app --host 0.0.0.0 --port 8000 > "$ROOT_DIR/backend.log" 2>&1 &
    
    # Start Frontend Service (Streamlit)
    echo "➡ Starting Frontend Service (Port 8501)..."
    cd "$ROOT_DIR/com/stockprediction/frontend" || exit
    nohup "$ROOT_DIR/venv_new/bin/streamlit" run app.py > "$ROOT_DIR/frontend.log" 2>&1 &
    
    cd "$ROOT_DIR" || exit
    echo "✅ All services have been started in the background."
    echo "📜 Logs are being written to backend.log and frontend.log"
}

stop_services() {
    echo "🛑 Stopping all services..."
    
    echo "➡ Stopping Backend Service (Port 8000)..."
    # Find processes listening on port 8000 and kill them
    lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   (Backend Service was not running)"

    echo "➡ Stopping Frontend Service (Port 8501)..."
    # Streamlit typically uses port 8501
    lsof -ti:8501 | xargs kill -9 2>/dev/null || echo "   (Frontend Service was not running)"

    echo "✅ All services stopped successfully."
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        echo "Waiting for 2 seconds..."
        sleep 2
        start_services
        ;;
    *)
        echo "Usage: ./manage.sh {start|stop|restart}"
        exit 1
        ;;
esac
