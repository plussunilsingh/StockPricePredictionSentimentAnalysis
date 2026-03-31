#!/bin/bash

# Enterprise Management Script for Stock Prediction System
# Usage: ./manage.sh [start|stop|status|restart|logs]

PROJECT_ROOT=$(pwd)
BACKEND_LOG="logs/backend_enterprise.log"
FRONTEND_LOG="logs/frontend_enterprise.log"
PID_FILE="logs/.app.pids"

function start() {
    echo "Starting Stock Prediction System..."
    
    # Process cleanup
    stop
    
    # Create logs directory if it does not exist
    if [ ! -d "logs" ]; then
        mkdir logs
    fi
    
    # === PRE-FLIGHT PORT CHECK (Port 8000) ===
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "🚨 ERROR: PORT 8000 IS OCCUPIED 🚨"
        echo "System cannot start on Port 8000. Please run './manage.sh stop' or free current port."
        exit 1
    fi
    
    # Auto-activate valid virtual environment to ensure robust dependency loading
    PYTHON_BIN="python3"
    if [ -f "test_env_311/bin/python3" ]; then
        PYTHON_BIN="$(pwd)/test_env_311/bin/python3"
    elif [ -d "venv_new" ]; then
        PYTHON_BIN="$(pwd)/venv_new/bin/python3"
    elif [ -d "venv" ]; then
        PYTHON_BIN="$(pwd)/venv/bin/python3"
    elif [ -d ".venv" ]; then
        PYTHON_BIN="$(pwd)/.venv/bin/python3"
    fi
    echo "Using Python: $PYTHON_BIN"
    
    # Start Backend
    export PYTHONPATH=$PYTHONPATH:.
    nohup $PYTHON_BIN com/stockprediction/backend/main.py > $BACKEND_LOG 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > $PID_FILE
    
    # --- POST-START VERIFICATION ---
    sleep 2
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo "❌ BACKEND FAILED TO START (Check logs below)"
        echo "-------------------------------------------------------"
        tail -n 10 $BACKEND_LOG
        echo "-------------------------------------------------------"
        exit 1
    fi
    echo "Backend started with PID: $BACKEND_PID (Logs: $BACKEND_LOG)"
    
    # Start Frontend
    nohup $PYTHON_BIN -m streamlit run com/stockprediction/frontend/app.py --server.port=8005 > $FRONTEND_LOG 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID >> $PID_FILE
    
    sleep 1
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo "❌ FRONTEND FAILED TO START (Check logs below)"
        echo "-------------------------------------------------------"
        tail -n 10 $FRONTEND_LOG
        echo "-------------------------------------------------------"
        exit 1
    fi
    echo "Frontend started with PID: $FRONTEND_PID (Logs: $FRONTEND_LOG)"
    
    echo "System is warming up. Access dashboard at http://localhost:8005"
}

function stop() {
    echo "Stopping Stock Prediction System..."
    # Kill backend on 8000
    BACKEND_PID=$(lsof -ti:8000)
    if [ ! -z "$BACKEND_PID" ]; then
        kill -9 $BACKEND_PID 2>/dev/null
        echo "Stopped backend process $BACKEND_PID"
    fi
    
    # Kill frontend on 8005
    FRONTEND_PID=$(lsof -ti:8005 2>/dev/null)
    if [ ! -z "$FRONTEND_PID" ]; then
        kill -9 $FRONTEND_PID 2>/dev/null
        echo "Stopped frontend process $FRONTEND_PID"
    fi
    # Also blindly kill any hanging streamlit instances running independently
    pkill -f "streamlit run" 2>/dev/null
    
    # Clean up PID file if it exists
    [ -f $PID_FILE ] && rm $PID_FILE
    echo "Processes terminated."
}

function status() {
    echo "System Status:"
    if [ -f $PID_FILE ]; then
        while read pid; do
            if ps -p $pid > /dev/null; then
                echo "Process $pid is RUNNING."
            else
                echo "Process $pid is NOT running."
            fi
        done < $PID_FILE
    else
        echo "No PID file found. System might be offline."
    fi
}

function logs() {
    tail -f $BACKEND_LOG $FRONTEND_LOG
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|logs}"
        exit 1
esac
