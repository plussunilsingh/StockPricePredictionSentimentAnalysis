import sys
import os
# Add the project root to the python path so Streamlit can find the 'com' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import asyncio
import streamlit as st
import pandas as pd
from com.stockprediction.backend.db_client import LiveDBClient
from com.stockprediction.backend.oi_analyzer import OIAnalyzer

from datetime import datetime, timedelta

st.set_page_config(page_title="Institutional Options Engine", layout="wide")

# Add a manual refresh button as requested to save compute
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("⚡ Institutional Options Decision Engine")
with col_refresh:
    st.write("")
    if st.button("🔄 Fetch Live Market Data"):
        st.rerun()

st.sidebar.header("📊 Chart Filters")
time_filter = st.sidebar.selectbox(
    "Select Time Range", 
    ["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "Custom Range"]
)

start_date, end_date = None, None
if time_filter == "Custom Range":
    date_range = st.sidebar.date_input("Select Date Range", value=(datetime.now() - timedelta(days=7), datetime.now()))
    if len(date_range) == 2:
        start_date, end_date = date_range
        # Convert to datetime at midnight and 23:59:59
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
else:
    end_date = datetime.now()
    if time_filter == "1 Day":
        start_date = end_date - timedelta(days=1)
    elif time_filter == "1 Week":
        start_date = end_date - timedelta(weeks=1)
    elif time_filter == "1 Month":
        start_date = end_date - timedelta(days=30)
    elif time_filter == "3 Months":
        start_date = end_date - timedelta(days=90)
    elif time_filter == "6 Months":
        start_date = end_date - timedelta(days=180)
    elif time_filter == "1 Year":
        start_date = end_date - timedelta(days=365)

async def fetch_live_dashboard_data(start_time, end_time):
    client = LiveDBClient()
    await client.connect()
    
    # Fetch actual real-time data
    spot = await client.get_latest_spot("ANGELONE:26000")
    candles_df = await client.get_candles_by_timerange("ANGELONE:26000", start_time, end_time)
    health = await client.get_system_health()
    
    return spot, candles_df, health

# Fetch data via asyncio
spot_price, candles_df, sys_health = asyncio.run(fetch_live_dashboard_data(start_date, end_date))

st.markdown("---")

# Strict Live Data Guardrail
if sys_health.get("Redis") == "OFFLINE" and sys_health.get("TimescaleDB") == "OFFLINE":
    st.error("🚨 **SYSTEM OFFLINE: No Live Data Available.** The Docker infrastructure (Redis/TimescaleDB) is unreachable. Please start your Docker Daemon and ensure your AngelOne API Keys are valid.")
    st.stop()

# Top Metrics (Now Live)
col1, col2, col3, col4 = st.columns(4)
# If spot is 0, we haven't received a tick yet
col1.metric("NIFTY 50 (Live)", f"{spot_price:,.2f}" if spot_price > 0 else "Waiting for Tick...", "")

# We don't have real option chain DB fetching built yet, so PCR/MaxPain stay blank until data flows
col2.metric("Market PCR", "Awaiting Chain Data...", "") 
col3.metric("Max Pain Strike", "Awaiting Chain Data...", "")
col4.metric("Risk Status", "Evaluating..." if spot_price > 0 else "Offline", "")

st.markdown("---")

colA, colB = st.columns([2, 1])

with colA:
    st.subheader("Live Market Signals")
    if spot_price > 0:
        st.info("⏳ Analyzing market structure. Awaiting full 15-minute data buffer to generate probabilistic signal.")
    else:
        st.warning("No live ticks flowing. Signals suspended.")
    
    st.subheader(f"Live OHLC Chart ({time_filter})")
    if not candles_df.empty:
        # Streamlit line_chart can plot close prices easily
        chart_data = candles_df[['time', 'close']].set_index('time')
        st.line_chart(chart_data)
    else:
        st.info(f"No OHLC candles found in PostgreSQL for the selected range ({time_filter}). Make sure the OhlcAggregator is running and ingesting ticks.")

with colB:
    st.subheader("Options Chain Snapshot")
    st.info("Live Options Chain parsing will populate here once the WebSocket feed expands to NFO symbols.")
    
    st.subheader("System Health")
    st.code(f"""
Redis Cache: {sys_health.get("Redis")}
TimescaleDB: {sys_health.get("TimescaleDB")}
AngelOne WS: {"ONLINE" if spot_price > 0 else "WAITING FOR CONNECTION"}
AI Engine:   AWAITING TRAINING DATA
    """)

st.caption("Operating strictly on live market structure. Mock data is disabled.")
