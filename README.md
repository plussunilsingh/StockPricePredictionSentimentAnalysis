---
title: "Institutional Options Decision Engine"
emoji: "📈"
colorFrom: "blue"
colorTo: "green"
sdk: docker
sdk_version: "docker"
python_version: "3.11"
app_file: "com/stockprediction/dashboard/app.py"
pinned: false
---

# Institutional-Style Market Intelligence & Options Decision Engine

This system is an **AI-assisted institutional-grade trading intelligence platform** for real-time options analysis. It combines derivatives data, market structure, sentiment analysis, and predictive modeling to generate explainable, risk-aware trading insights for intraday and short-term traders.

## 🚀 The TRUE Project Goal
The real goal is NOT to randomly "predict stock prices". 
The real goal is to build a real-time AI-assisted market decision system that helps identify high-probability options trading opportunities using live market structure, derivatives flow, sentiment, volatility, and AI-driven contextual reasoning.

The system acts as a **Market Analyst, Quant Assistant, and Trade Confidence Evaluator**.

---

## 🏛 The 6 Pillars of the Platform

### Pillar 1 — Reliability & Market Data Infrastructure
- **Purpose**: Low-latency, crash-proof reliable market ingestion.
- **Includes**: **AngelOne WebSocket** with auto-reconnect and tick deduplication.
- **Data Stack**: **Redis** for tick caching, **PostgreSQL (TimescaleDB)** for fast OHLC aggregation.

### Pillar 2 — Market Intelligence Engine
- **Purpose**: Convert raw data into trading intelligence.
- **Includes**: Black-Scholes Greeks Engine (Delta, Gamma, Theta, Vega, IV), OI buildup detection, PCR calculation, and Max Pain strike analysis.

### Pillar 3 — Risk Management Layer
- **Purpose**: Hard stop for capital protection.
- **Includes**: Spread limit filters, low-volume liquidity blocks, and maximum daily drawdown limits to prevent the AI from executing in hostile conditions.

### Pillar 4 — AI Prediction & Reasoning Layer
- **Purpose**: AI-enhanced probabilistic forecasting predicting probability, NOT certainty.
- **Includes**: Engineered datasets specifically mathematically labeled for options success. Models used: **XGBoost** (for structured tabular rules), LSTM (sequence), FinBERT (sentiment).

### Pillar 5 — Decision & Signal Engine
- **Purpose**: Convert intelligence into actionable setups.
- **Outputs**: BUY CE, BUY PE, HOLD, with exact Confidence Probabilities.
- **Labeling Logic**: `Label = 1 IF NIFTY moves +40 points in 15 mins AND premium increases > 20% AND move occurs before stop-loss.`

### Pillar 6 — Trader Interface Layer
- **Purpose**: Human-readable command center.
- **Includes**: Live **Streamlit** dashboard showing real-time charts, options chains, PCR heatmaps, and transparent AI signal reasoning.

---

## 🚀 How to Run

1. **Start Infrastructure**: `docker compose up -d` (requires Docker running)
2. **Launch Streamlit UI**: `streamlit run com/stockprediction/dashboard/app.py`
3. **Start Websocket**: `python -m com.stockprediction.backend.angelone_websocket`
4. **Start Aggregator**: `python -m com.stockprediction.backend.ohlc_aggregator`

## 📂 Project Documentation

All system documentation and project requirements are maintained in the `docs/` directory:
- `docs/requirements.md` - Core project requirements and trading goals.
- `docs/implementation_plan.md` - Technical roadmap and actionable tasks.
- `walkthrough.md` - Architectural summary and execution validation.
