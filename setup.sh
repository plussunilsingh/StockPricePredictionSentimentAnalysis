#!/usr/bin/env bash
# File: setup.sh
# Usage: ./setup.sh
set -euo pipefail

PROJECT_ROOT="$(pwd)"
PYPROJECT="$PROJECT_ROOT/pyproject.toml"
GEN_SCRIPT="$PROJECT_ROOT/scripts/generate_model.py"
MODEL_DIR="$PROJECT_ROOT/models"
MODEL_PATH="$MODEL_DIR/stock_model.pkl"

echo "Setting up project with Poetry and generating a dummy model..."

# Ensure python3 is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install Python 3.11+ and retry."
    exit 1
fi

# Ensure poetry is available; try to install locally if missing
if ! command -v poetry >/dev/null 2>&1; then
    echo "Poetry not found. Installing poetry (user install)..."
    python3 -m pip install --user "poetry>=1.5" >/dev/null
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v poetry >/dev/null 2>&1; then
        echo "Failed to install poetry. Install it manually and re-run."
        exit 1
    fi
fi

# Create pyproject.toml if missing
if [ ! -f "$PYPROJECT" ]; then
    cat > "$PYPROJECT" <<'PYPROJECT'
[tool.poetry]
name = "stock-prediction-enterprise"
version = "0.1.0"
description = "Stock prediction system"
authors = ["Your Name <you@example.com>"]
license = "MIT"

[tool.poetry.dependencies]
python = "^3.11"
streamlit = "^1.30"
pandas = "^2.0"
scikit-learn = "^1.2"
joblib = "^1.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
PYPROJECT
    echo "Created $PYPROJECT"
else
    echo "$PYPROJECT already exists; skipping creation."
fi

# Ensure scripts directory and generator exist
mkdir -p "$(dirname "$GEN_SCRIPT")"
if [ ! -f "$GEN_SCRIPT" ]; then
    cat > "$GEN_SCRIPT" <<'PYGEN'
#!/usr/bin/env python3
"""
Simple model generator for development.
Creates a toy regression model and saves to models/stock_model.pkl
"""
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
import joblib

os.makedirs("models", exist_ok=True)
X, y = make_regression(n_samples=300, n_features=10, noise=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=50, random_state=42)
model.fit(X, y)
joblib.dump(model, "models/stock_model.pkl")
print("Saved model to models/stock_model.pkl")
PYGEN
    chmod +x "$GEN_SCRIPT"
    echo "Created $GEN_SCRIPT"
else
    echo "$GEN_SCRIPT already exists; skipping creation."
fi

# Install dependencies via poetry (creates isolated venv)
echo "Running poetry install (this may take a few minutes)..."
poetry install --no-interaction --no-ansi

# Generate model using poetry environment
echo "Generating model..."
poetry run python "$GEN_SCRIPT"

# Verify model created
if [ -f "$MODEL_PATH" ]; then
    echo "Model generated at $MODEL_PATH"
else
    echo "Model generation failed: $MODEL_PATH not found"
    exit 1
fi

echo "Setup complete. Use ./manage.sh start to run the system (or adjust to use poetry run as needed)."
