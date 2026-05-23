import streamlit as st
import pandas as pd
import numpy as np

# Pillar 6: Trader Interface Layer
st.set_page_config(page_title="Institutional Options Engine", layout="wide")

st.title("⚡ Institutional Options Decision Engine")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("NIFTY 50", "22,500.50", "+45.20")
col2.metric("Market PCR", "0.78", "-0.05", delta_color="inverse") # Low PCR is bullish
col3.metric("Max Pain Strike", "22,400", "0")
col4.metric("Risk Status", "PASS", "Safe")

st.markdown("---")

# Main Dashboard Layout
colA, colB = st.columns([2, 1])

with colA:
    st.subheader("Live Trading Signals")
    
    # Mock Live Signal from our Signal/AI Engines
    st.success("🟢 **BUY CE [NIFTY 22500 CE]**")
    st.markdown("""
    **Explainable AI Reasoning:**
    * 🎯 **AI Confidence Score:** 84.5% Probability of Success
    * 📈 **Trend:** Spot (22500.50) > VWAP (22480.00)
    * 🔥 **Options Flow:** PCR is Bullish (0.78), heavy Put writing observed at 22400.
    * 🛡️ **Risk Check:** Spread is 1.2% (Pass), Volume is 145,000 (Pass).
    """)
    
    st.subheader("Intraday Options Flow (Mock)")
    # Mock chart data
    chart_data = pd.DataFrame(
        np.random.randn(20, 2) * [1000, -1000] + [50000, 45000],
        columns=['Call OI', 'Put OI']
    )
    st.line_chart(chart_data)

with colB:
    st.subheader("Options Chain Snapshot")
    st.caption("Near ATM Strikes")
    
    # Mock Options Chain
    chain_data = pd.DataFrame({
        "CE OI": [120000, 80000, 50000, 30000],
        "CE LTP": [150.5, 100.2, 55.0, 25.5],
        "Strike": ["22400", "22500 (ATM)", "22600", "22700"],
        "PE LTP": [20.5, 45.0, 95.5, 140.2],
        "PE OI": [45000, 110000, 150000, 180000]
    })
    st.dataframe(chain_data, hide_index=True)
    
    st.subheader("System Health")
    st.code("""
Redis Cache: ONLINE
TimescaleDB: ONLINE
AngelOne WS: ONLINE (Latency: 12ms)
AI Engine:   TRAINED (XGBoost)
    """)

st.caption("Designed for Institutional-Grade Options Intelligence.")
