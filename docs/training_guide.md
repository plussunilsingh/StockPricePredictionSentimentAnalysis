# 🧠 Training & Data Management Guide

This guide explains how to maintain the Stock Prediction System by updating datasets and retraining the predictive models.

## 📅 1. Updating Data (Mock Mode)
To update the system with the latest market prices up to today, use the `generate_data.py` utility.

### Step-by-Step:
1.  **Configure Date Range**: Edit `scripts/generate_data.py` to set the `end_date` to the current date.
2.  **Add Symbols**: Add any new Indian or US symbols to the `if __name__ == "__main__":` block at the bottom of the script.
3.  **Execute**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    ./test_env_311/bin/python3 scripts/generate_data.py
    ```

---

## 🏗 2. Training Predictive Models
The system uses **Random Forest (RF)** and **LSTM** models. While RF trains instantly, LSTM requires a historical dataset.

### Retraining Workflow:
1.  Ensure your `data/*.csv` files are updated.
2.  Run the centralized training script:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    ./test_env_311/bin/python3 scripts/train_models.py
    ```
3.  **Outputs**:
    *   `data/rf_model.joblib`: The serialized Random Forest classifier.
    *   `data/model.h5`: The SavedModel for LSTM (requires TensorFlow).

---

## 🔄 3. Production Deployment (Live Mode)
In **Live Mode**, neither manual data generation nor manual training is required for basic drift detection, as the backend fetches 180 days of rolling data from Yahoo Finance and performs on-the-fly feature engineering.

### To Enable Live Mode:
1.  Open the **Stock Sentinel** dashboard.
2.  Toggle **"Enable Live Market Data"** in the sidebar.
3.  Click **"Generate Intelligence Report"**.

---

## 🛠 4. Standardizing New Securities
If adding a new stock from the Indian market (NSE), ensure it follows the `.NS` suffix convention (e.g., `TCS.NS`) to allow the yfinance strategy to resolve it correctly.
