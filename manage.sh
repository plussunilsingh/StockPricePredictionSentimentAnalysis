#!/bin/bash

# Enterprise Management Script for Stock Prediction System
# Usage: ./manage.sh [start|stop|status|restart|logs]

PROJECT_ROOT=$(pwd)
BACKEND_LOG="logs/backend_enterprise.log"
FRONTEND_LOG="logs/frontend_enterprise.log"
PID_FILE="logs/.app.pids"

function start() {
    echo "Starting Stock Prediction System..."
    
    # Create logs directory if it does not exist
    if [ ! -d "logs" ]; then
        mkdir logs
    fi
    
    # Start Backend
    export PYTHONPATH=$PYTHONPATH:.
    nohup python3 com/stockprediction/backend/main.py > $BACKEND_LOG 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > $PID_FILE
    echo "Backend started with PID: $BACKEND_PID (Logs: $BACKEND_LOG)"
    
    # Start Frontend
    nohup python3 -m streamlit run com/stockprediction/frontend/app.py --server.port=5001 > $FRONTEND_LOG 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID >> $PID_FILE
    echo "Frontend started with PID: $FRONTEND_PID (Logs: $FRONTEND_LOG)"
    
    echo "System is warming up. Access dashboard at http://localhost:5001"
}

function stop() {
    echo "Stopping Stock Prediction System..."
    # Kill backend on 5000
    BACKEND_PID=$(lsof -ti:5000)
    if [ ! -z "$BACKEND_PID" ]; then
        kill -9 $BACKEND_PID
        echo "Stopped backend process $BACKEND_PID"
    fi
    
    # Kill frontend on 5001
    FRONTEND_PID=$(lsof -ti:5001 2>/dev/null || lsof -ti:8503 2>/dev/null)
    if [ ! -z "$FRONTEND_PID" ]; then
        kill -9 $FRONTEND_PID
        echo "Stopped frontend process $FRONTEND_PID"
    fi
    
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
