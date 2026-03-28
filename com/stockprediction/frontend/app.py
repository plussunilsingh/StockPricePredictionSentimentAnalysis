"""Streamlit frontend application for the Stock Sentinel dashboard.

This module defines a small interactive UI used during the hackathon to
trigger predictions and visualize recent price history. Styling and
component choices are intentionally explicit and small so reviewers can
quickly understand the UX decisions.
"""

try:
    import streamlit as st
except Exception:
    st = None

try:
    import pandas as pd
except Exception:
    pd = None

import requests
import os
from datetime import datetime, timedelta
from com.stockprediction.config.AppConfig import config

if st is None:
    raise RuntimeError("streamlit is required to run the frontend app")

# Page Config
st.set_page_config(
    page_title="Stock Sentinel | Enterprise Market Intelligence",
    page_icon="📈",
    layout="wide"
)

# Premium Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b;
        border-color: #ff4b4b;
    }
    .prediction-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 0.9em; color: #a0a0a0; }
    .metric-value { font-size: 1.8em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("🛡️ Enterprise Market Surveillance")
st.markdown("### *Stock Sentinel | Advanced Predictive Analysis*")

# Sidebar - User Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Live Data Toggle: use checkbox for compatibility
    isLiveData = st.checkbox("Enable Live Market Data", value=(config.get("system", "dataMode") == "LIVE"))

    # Model Selection
    modelType = st.radio("Predictive Model", ["RF", "LSTM"], index=0, help="Random Forest is faster; LSTM identifies long-term patterns.")
    
    st.divider()
    # Use config value if exists, fallback to 8000
    port = config.get("system", "port") if config.get("system", "port") else 8000
    
    # Market Selection
    symbols_config = config.get("symbols", "indices") or []
    stocks_config = config.get("symbols", "stocks") or []
    allSymbols = symbols_config + stocks_config
    symbolLabels = [s['label'] for s in allSymbols]
    symbolValues = [s['value'] for s in allSymbols]
    
    # Defensive: handle missing symbol config
    if not symbolLabels:
        symbolLabels = ["RELIANCE.NS"]
        symbolValues = ["RELIANCE.NS"]

    selectedLabel = st.selectbox("Market Security", symbolLabels)
    selectedSymbol = symbolValues[symbolLabels.index(selectedLabel)]
    
    manualSymbol = st.text_input("Or search symbol manually", value="", placeholder="e.g. RELIANCE.NS")
    finalSymbol = manualSymbol if manualSymbol else selectedSymbol
    
    histDays = config.get("data", "historicalDays") or 90
    predictButton = st.button("Generate Intelligence Report")

# Backend Communication
BACKEND_URL = f"http://127.0.0.1:{config.get('system', 'port')}"

def getPrediction(symbol, model, useMock):
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            json={
                "symbol": symbol,
                "startDate": (datetime.now() - timedelta(days=histDays)).strftime('%Y-%m-%d'),
                "endDate": datetime.now().strftime('%Y-%m-%d'),
                "useMock": useMock,
                "modelType": model
            },
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.warning(f"Data not found for {symbol}. Try switching Data Mode.")
        else:
            st.error(f"Backend Error ({response.status_code}): {response.text}")
    except requests.exceptions.ConnectionError as e:
        port = config.get('system', 'port')
        if "Connection refused" in str(e):
            st.error(f"🚨 **Backend Offline**: Connection refused on Port {port}. Ensure the backend is running via `./manage.sh start`.")
        else:
            st.error(f"Backend Offline: Failed to connect to port {port}. Details: {e}")
    except Exception as e:
        st.error(f"Backend Offline: {e}")
    return None

# Main Dashboard
col1, col2 = st.columns([1, 2])

if predictButton:
    with st.spinner(f"Analyzing {finalSymbol} Market Dynamics..."):
        result = getPrediction(finalSymbol, modelType, not isLiveData)
        
        if result:
            with col1:
                st.subheader("🎯 Predictive Insights")
                color = "#00ff00" if result['prediction'] == "UP" else "#ff4b4b"
                
                st.markdown(f"""
                <div class="prediction-card" style="border-left-color: {color};">
                    <div class="metric-label">Signal Recommendation</div>
                    <div class="metric-value" style="color: {color};">{result['decision']}</div>
                    <hr style="opacity: 0.1; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <div class="metric-label">Prediction</div>
                            <div style="font-weight: bold;">{result['prediction']}</div>
                        </div>
                        <div>
                            <div class="metric-label">Confidence</div>
                            <div style="font-weight: bold;">{result['confidence']*100:.1f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if result.get('lastClose'):
                    st.markdown(f"""
                    <div style="background-color: #262730; padding: 15px; border-radius: 8px; border: 1px solid #444; margin-top: 20px;">
                        <div class="metric-label">Last Traded Price</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{result['lastClose']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.subheader("📊 Price Momentum")
                # Load historical data for charting
                mockDir = config.get("data", "mockDir")
                filePath = os.path.join(mockDir, f"{finalSymbol}.csv")
                
                if os.path.exists(filePath):
                    if pd is None:
                        st.info("pandas not available: cannot load historical chart data")
                    else:
                        df = pd.read_csv(filePath)
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.sort_values('Date').tail(histDays)

                        # Using st.line_chart for better compatibility
                        chart_data = df.set_index('Date')['Close']
                        st.line_chart(chart_data)
                else:
                    st.info("Live chart integration pending. Historical mock chart unavailable for this symbol.")
        else:
            st.warning("Intelligence Engine returned no results. Verify if data mode matches symbol availability.")
else:
    st.info("👈 Select a security and click 'Generate Intelligence Report' to start analysis.")
    st.markdown("""
    <div style="background-color: #1e1e2f; padding: 40px; border-radius: 15px; border: 1px solid #333; text-align: center;">
        <h2 style="color: #a0a0a0;">System Ready for Surveillance</h2>
        <p style="color: #666;">Awaiting command for technical and sentiment cross-analysis.</p>
    </div>
    """, unsafe_allow_html=True)
