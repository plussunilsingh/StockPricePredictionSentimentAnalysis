# Project Vision & Requirements: Institutional-Style Options Decision Engine

## Step 1 — The TRUE Project Goal
**Primary Goal:** Build a real-time AI-powered options trading intelligence system capable of analyzing live market data, options flow, volatility, sentiment, and historical market behavior to generate high-confidence trading insights, trade setups, and risk-aware entry/exit signals for intraday and short-term options trading.

## Step 2 — What This System Actually Does
The system acts as a:
- Market analyst
- Quant assistant
- Options flow analyzer
- AI reasoning engine
- Signal assistant
- Trade confidence evaluator

*(It is NOT a magical "future predictor")*

## Step 3 — Core System Mission
The mission of this project is to combine institutional-grade market data, options analytics, historical context, real-time sentiment, and AI forecasting models into a unified trading intelligence platform that assists traders in making fast, informed, and risk-aware decisions during live market hours.

## Step 4 — The 6 Pillars of the Platform
1. **Pillar 1: Reliability & Market Data Infrastructure** - Low-latency crash-proof ingestion via **AngelOne WebSocket**. Uses **Redis** for tick caching and **PostgreSQL (TimescaleDB)** for aggregate historical candles.
2. **Pillar 2: Market Intelligence Engine** - Convert raw data into trading intelligence (Black-Scholes Greeks Engine, OI buildup detection, PCR calculation, Max Pain Analysis).
3. **Pillar 3: Risk Management Layer** - Protect capital with pre-trade filters (Bid-Ask spread limits, Volume liquidity requirements, Max Daily Loss circuits).
4. **Pillar 4: AI Prediction Layer** - AI-enhanced probabilistic forecasting predicting probability (XGBoost, LSTM, FinBERT) trained strictly on mathematically labeled options data.
5. **Pillar 5: Decision & Signal Engine** - Convert intelligence into actionable setups with explainable reasoning based on the exact label: `Label = 1 IF NIFTY moves +40 points in 15 mins AND premium increases > 20% AND move occurs before stop-loss.`
6. **Pillar 6: Trader Interface Layer** - Human-readable command center (Streamlit) showing live charts, options chains, PCR heatmaps, and AI Confidence scores.

## Step 5 — Architectural Directives
- **Avoid Overengineering History**: Focus on the last 3 months, last 30 days, intraday structure, and volatility regimes rather than pure 100-year deep historical modeling. Intraday options depend on live liquidity and order flow.
- **Rule-Based Before AI**: Establish rule-based signals (breakouts, OI shifts, VWAP logic) before layering on complex AI. AI should *enhance* signal quality, not replace core logic.
- **Explainability**: The system must explain *WHY* a signal was generated. Institutional systems require explainability.
