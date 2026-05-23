# Project Requirements: Real-Time Options Trading Setup

## Core Objective
Transform the system from a general stock price predictor into a **daily options trading setup** tailored specifically for analyzing the market and identifying optimal Call/Put entry and exit points (Buy/Sell).

## Key Requirements

1. **No Mock Data (100% Real Data)**:
   - All sentiment, pricing, and options data must be fetched from real sources. Mock data logic will be completely removed.

2. **Daily Options Trading Focus (Call vs Put)**:
   - The application must specialize in evaluating Options Contracts.
   - Must provide explicit Buy/Sell signals for Call and Put options based on deep technical and sentiment analysis.

3. **Real-Time Data Integration & Best-in-Class Sources**:
   - To achieve superior market control, we will prioritize the absolute best, low-latency data sources.
   - For Indian Markets (NSE): Integrate with **Upstox API** (for execution/retail feeds) and evaluate institutional-grade tick data providers like **TrueData** or **Global Datafeeds** if millisecond precision is required.
   - The system must act as a live "trader setup", continuously analyzing the market during trading hours without data lag.

4. **Predictive Analytics & Deep Analysis**:
   - Continue utilizing the 100-year historical data context and advanced LLMs (FinBERT, TimeGPT).
   - Merge long-term historical context with real-time options data to output high-confidence trade signals.
