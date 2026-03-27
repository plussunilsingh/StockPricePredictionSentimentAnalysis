#!/bin/bash

# Enterprise Management Script for Stock Prediction System
# Usage: ./manage.sh [start|stop|status|restart|logs]

PROJECT_ROOT=$(pwd)
BACKEND_LOG="backend.log"
FRONTEND_LOG="frontend.log"
PID_FILE=".app.pids"

function start() {
    echo "Starting Stock Prediction System..."
    
    # Start Backend
    export PYTHONPATH=$PYTHONPATH:.
    nohup python3 com/stockprediction/backend/main.py > $BACKEND_LOG 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > $PID_FILE
    echo "Backend started with PID: $BACKEND_PID (Logs: $BACKEND_LOG)"
    
    # Start Frontend
    nohup python3 -m streamlit run com/stockprediction/frontend/app.py > $FRONTEND_LOG 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID >> $PID_FILE
    echo "Frontend started with PID: $FRONTEND_PID (Logs: $FRONTEND_LOG)"
    
    echo "System is warming up. Access dashboard at http://localhost:8501"
}

function stop() {
    echo "Stopping Stock Prediction System..."
    if [ -f $PID_FILE ]; then
        while read pid; do
            if ps -p $pid > /dev/null; then
                kill $pid
                echo "Stopped process $pid"
            fi
        done < $PID_FILE
        rm $PID_FILE
    else
        # Fallback: kill by process name if pid file missing
        pkill -f "com/stockprediction/backend/main.py"
        pkill -f "streamlit run com/stockprediction/frontend/app.py"
        echo "Processes terminated via pkill."
    fi
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
