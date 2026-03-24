#!/bin/bash

# Configuration and Paths
ROOT_DIR="$(pwd)"

start_services() {
    echo "🚀 Starting Data-Driven Stock Price Prediction System..."
    
    # Start ML Service
    echo "➡ Starting ML Service (Port 8000)..."
    cd "$ROOT_DIR/ml_service" || exit
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "$ROOT_DIR/ml_service.log" 2>&1 &
    
    # Start Backend Service
    echo "➡ Starting Backend Service (Port 8080)..."
    cd "$ROOT_DIR/backend" || exit
    nohup mvn spring-boot:run > "$ROOT_DIR/backend.log" 2>&1 &
    
    # Start Frontend Service
    echo "➡ Starting Frontend Service (Port 8501)..."
    cd "$ROOT_DIR/frontend" || exit
    nohup streamlit run app.py > "$ROOT_DIR/frontend.log" 2>&1 &
    
    cd "$ROOT_DIR" || exit
    echo "✅ All services have been started in the background."
    echo "📜 Logs are being written to ml_service.log, backend.log, and frontend.log"
}

stop_services() {
    echo "🛑 Stopping all services..."
    
    echo "➡ Stopping ML Service (Port 8000)..."
    # Find processes listening on port 8000 and kill them
    lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   (ML Service was not running)"

    echo "➡ Stopping Backend Service (Port 8080)..."
    # Find processes listening on port 8080 and kill them
    lsof -ti:8080 | xargs kill -9 2>/dev/null || echo "   (Backend Service was not running)"

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
