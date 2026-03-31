#!/bin/bash

# Enterprise Management Script for Stock Prediction System
# Usage: ./manage.sh [start|stop|status|restart|logs]

PROJECT_ROOT=$(pwd)
BACKEND_LOG="logs/backend_enterprise.log"
FRONTEND_LOG="logs/frontend_enterprise.log"
PID_FILE="logs/.app.pids"

function setupEnv() {
    # Ensure python3 is available
    if ! command -v python3 >/dev/null 2>&1; then
        echo "ERROR: python3 is not installed. Please install Python 3.11+ and re-run."
        exit 1
    fi

    echo "Checking for existing virtual environments..."

    # Prefer existing envs in the project's conventional order
    if [ -f "$(pwd)/test_env_311/bin/python3" ]; then
        PYTHON_BIN="$(pwd)/test_env_311/bin/python3"
        echo "Using existing virtualenv: test_env_311"
    elif [ -f "$(pwd)/venv_new/bin/python3" ]; then
        PYTHON_BIN="$(pwd)/venv_new/bin/python3"
        echo "Using existing virtualenv: venv_new"
    elif [ -f "$(pwd)/venv/bin/python3" ]; then
        PYTHON_BIN="$(pwd)/venv/bin/python3"
        echo "Using existing virtualenv: venv"
    elif [ -f "$(pwd)/.venv/bin/python3" ]; then
        PYTHON_BIN="$(pwd)/.venv/bin/python3"
        echo "Using existing virtualenv: .venv"

        # Ensure required packages are installed in the existing venv (fast sanity check)
        if [ -f "requirements.txt" ]; then
            echo "Verifying required packages inside .venv..."
            # Always ensure pip and friends are reasonably up-to-date inside venv
            "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel || true

            # Install full requirements (visible) to satisfy dependencies
            echo "Installing/Updating packages from requirements.txt into .venv (this may take several minutes)..."
            if ! "$PYTHON_BIN" -m pip install -r requirements.txt; then
                echo "Warning: pip install -r requirements.txt returned non-zero. Will attempt to continue with best-effort installs."
            fi

            # Now sanity-check a few essential modules the app requires
            MISSING=()
            for mod in fastapi pandas scikit_learn streamlit uvicorn pydantic; do
                # Use import module names mapping for package names where pip vs import differs
                if [ "$mod" = "scikit_learn" ]; then
                    import_name="sklearn"
                else
                    import_name="$mod"
                fi
                if ! "$PYTHON_BIN" -c "import ${import_name}" >/dev/null 2>&1; then
                    MISSING+=("$mod")
                fi
            done

            if [ ${#MISSING[@]} -ne 0 ]; then
                echo "Detected missing modules in .venv: ${MISSING[*]}"
                echo "Attempting to install missing modules individually (best effort)..."
                for pkg in "${MISSING[@]}"; do
                    # map back to pip package names
                    case "$pkg" in
                        scikit_learn)
                            pip_pkg="scikit-learn";;
                        fastapi)
                            pip_pkg="fastapi";;
                        pandas)
                            pip_pkg="pandas";;
                        streamlit)
                            pip_pkg="streamlit";;
                        uvicorn)
                            pip_pkg="uvicorn";;
                        pydantic)
                            pip_pkg="pydantic";;
                        *)
                            pip_pkg="$pkg";;
                    esac

                    echo "Installing $pip_pkg into .venv..."
                    if ! "$PYTHON_BIN" -m pip install "$pip_pkg"; then
                        echo "Failed to install $pip_pkg into .venv"
                    fi
                done

                # Re-check imports after attempted installs
                STILL_MISSING=()
                for mod in fastapi pandas scikit_learn streamlit uvicorn pydantic; do
                    if [ "$mod" = "scikit_learn" ]; then
                        import_name="sklearn"
                    else
                        import_name="$mod"
                    fi
                    if ! "$PYTHON_BIN" -c "import ${import_name}" >/dev/null 2>&1; then
                        STILL_MISSING+=("$mod")
                    fi
                done

                if [ ${#STILL_MISSING[@]} -ne 0 ]; then
                    echo "ERROR: The following required packages are still missing in .venv: ${STILL_MISSING[*]}"
                    echo "Please inspect .venv logs or run '${PYTHON_BIN} -m pip install -r requirements.txt' manually. Exiting."
                    exit 1
                else
                    echo "All essential packages installed in .venv"
                fi
            else
                echo "All essential packages appear present in .venv"
            fi
        fi
    else
        # No env found -> create .venv
        echo "No virtualenv found. Creating .venv..."
        python3 -m venv .venv || { echo "Failed to create virtualenv"; exit 1; }

        # Activate in current shell so that subsequent pip installs go to the venv
        # shellcheck source=/dev/null
        source .venv/bin/activate || { echo "Failed to activate .venv"; exit 1; }

        # Upgrade pip and install project requirements if available
        echo "Upgrading pip and installing requirements (if present)..."
        pip install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt || echo "Warning: pip install -r requirements.txt failed"
        else
            echo "No requirements.txt found at project root; skipping pip installs."
        fi

        PYTHON_BIN="$(pwd)/.venv/bin/python3"
        echo "Created and activated .venv"
    fi

    export PYTHON_BIN
}

function start() {
    echo "Starting Stock Prediction System..."
    
    # Process cleanup
    stop
    
    # Create logs directory if it does not exist
    if [ ! -d "logs" ]; then
        mkdir logs
    fi
    
    BACKEND_PORT="${BACKEND_PORT:-8000}"
    # === PRE-FLIGHT PORT CHECK (Port $BACKEND_PORT) ===
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "🚨 ERROR: PORT $BACKEND_PORT IS OCCUPIED 🚨"
        echo "System cannot start on Port $BACKEND_PORT. Please free the port or set BACKEND_PORT=8001 ./manage.sh start"
        exit 1
    fi
    
    # Ensure / create and activate a valid virtual environment to ensure robust dependency loading
    setupEnv
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
    
    if [ -f $PID_FILE ]; then
        while read pid; do
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null
                echo "Stopped process $pid"
            fi
        done < $PID_FILE
        rm $PID_FILE
    else
        echo "No PID file found. Skipping clean up."
    fi
    
    # Also bluntly kill any hanging streamlit instances running independently
    pkill -f "streamlit run com/stockprediction/frontend/app.py" 2>/dev/null
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

function deploy_hf() {
    echo "Preparing Hugging Face Space deployment..."
    
    if [ ! -f "Dockerfile.slim" ]; then
        echo "ERROR: Dockerfile.slim not found."
        exit 1
    fi
    
    echo "Copying Dockerfile.slim -> Dockerfile for Hugging Face single container format..."
    cp Dockerfile.slim Dockerfile
    
    echo "Deployment preparation complete! You can now push this repository to your Hugging Face Space."
    echo "HuggingFace will automatically build using the updated Dockerfile."
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
    deploy-hf)
        deploy_hf
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|logs|deploy-hf}"
        exit 1
esac
