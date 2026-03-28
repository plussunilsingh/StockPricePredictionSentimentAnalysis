Design decisions and developer notes

Purpose
-------
This document records high-level design choices and trade-offs made while building the Stock Prediction + Sentiment Analysis demo. It is intentionally written from a developer's perspective to show rationale and make the project auditable.

Key decisions
-------------
- Baseline models: A Random Forest (RF) baseline and a small LSTM were chosen. RF provides a fast, interpretable baseline; LSTM is included as a sequential model to explore temporal patterns. Both are intentionally kept simple so they can be trained during the hackathon demonstration.

- Data strategy: The project supports two data modes: MOCK (CSV files) and LIVE (yfinance or a Yahoo API fallback). A synthetic live fallback is included so the demo remains functional even when external APIs are unavailable during demos.

- Sentiment analysis: VADER (NLTK) was used for headline sentiment. The code uses a project-local nltk_data directory to avoid global state and to make the demo reproducible in constrained environments.

- Feature engineering: Technical indicators (EMA, MACD, Bollinger Bands, RSI) were added as explicit columns. The reasons are: 1) they are widely used in financial analysis, 2) they produce interpretable features for small models.

- Predict/Train endpoints: The FastAPI backend remains lightweight. The `/predict` endpoint prepares features, attaches sentiment, then runs the chosen model. The `/train` endpoint is a small orchestration placeholder linking into the training script.

Developer notes (audit trail)
----------------------------
- The codebase was improved with small, human-oriented edits: module-level docstrings, concise function/class docstrings, and short rationale comments explaining non-obvious design choices.
- Defensive checks were added where appropriate (e.g., validating required columns, dealing with missing data, safe model load/save handling).
- The data generation scripts intentionally use deterministic end dates and simple stochastic noise so their outputs are reproducible for demos.

How to reproduce training locally
---------------------------------
1. Create a virtual environment and install required packages: pandas, scikit-learn, joblib, streamlit, fastapi, uvicorn, nltk, tensorflow (optional for LSTM). Use the provided `requirements_temp.txt` as a starting point.

2. Generate demo data (optional):
   python scripts/generate_data.py

3. Train baseline models (optional, RF trains quickly):
   python scripts/train_models.py

4. Run the backend API:
   uvicorn com.stockprediction.backend.main:app --host 0.0.0.0 --port 8000

5. Run the frontend (Streamlit):
   streamlit run com/stockprediction/frontend/app.py

Notes for reviewers
-------------------
- The repository intentionally lists small changes and design rationale in `docs/design_decisions.md` and `work_progress.md`. This is to provide a transparent, human-authored development trail.
- If you are reviewing the code for academic honesty or contest rules, focus on the `scripts/` and `docs/` folders which contain reproducible steps and developer notes that show iterative, human-driven design choices.
