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

## Step 4 — The 5 Pillars of the Platform
1. **Pillar 1: Market Data Infrastructure** - Low-latency reliable market ingestion (Upstox WebSocket, NSE option chain, Tick data, OHLC candles, Open Interest, Volume, India VIX, PCR).
2. **Pillar 2: Market Intelligence Engine** - Convert raw data into trading intelligence (Greeks analysis, OI buildup detection, Support/resistance zones, volatility spikes, gamma exposure).
3. **Pillar 3: AI Prediction & Reasoning Layer** - AI-enhanced probabilistic forecasting predicting probability, NOT certainty (LSTM, TimeGPT, FinBERT, XGBoost).
4. **Pillar 4: Decision & Signal Engine** - Convert intelligence into actionable setups with explainable reasoning (e.g., Signal: BUY NIFTY 22500 CE, Confidence: 81%, Reason: Strong OI buildup).
5. **Pillar 5: Trader Interface Layer** - Human-readable command center (Streamlit initially, React later) showing live charts, options chains, PCR heatmaps, and signal timelines.

## Step 5 — Architectural Directives
- **Avoid Overengineering History**: Focus on the last 3 months, last 30 days, intraday structure, and volatility regimes rather than pure 100-year deep historical modeling. Intraday options depend on live liquidity and order flow.
- **Rule-Based Before AI**: Establish rule-based signals (breakouts, OI shifts, VWAP logic) before layering on complex AI. AI should *enhance* signal quality, not replace core logic.
- **Explainability**: The system must explain *WHY* a signal was generated. Institutional systems require explainability.
