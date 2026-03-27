import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from com.stockprediction.config.AppConfig import config

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
st.title("📈 Stock Sentinel")
st.markdown("### *Enterprise-Grade Market Intelligence & Predictive Analysis*")

# Sidebar - User Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Live Data Toggle
    isLiveData = st.toggle("Enable Live Market Data", value=(config.get("system", "dataMode") == "LIVE"))
    
    # Model Selection
    modelType = st.radio("Predictive Model", ["RF", "LSTM"], index=0, help="Random Forest is faster; LSTM identifies long-term patterns.")
    
    st.divider()
    
    # Market Selection
    allSymbols = config.get("symbols", "indices") + config.get("symbols", "stocks")
    symbolLabels = [s['label'] for s in allSymbols]
    symbolValues = [s['value'] for s in allSymbols]
    
    selectedLabel = st.selectbox("Market Security", symbolLabels)
    selectedSymbol = symbolValues[symbolLabels.index(selectedLabel)]
    
    manualSymbol = st.text_input("Or search symbol manually", value="", placeholder="e.g. RELIANCE.NS")
    finalSymbol = manualSymbol if manualSymbol else selectedSymbol
    
    histDays = config.get("data", "historicalDays")
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
        else:
            st.error(f"Engine Error: {response.text}")
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
                    st.metric("Last Traded Price", f"{result['lastClose']:.2f}", delta=None)
            
            with col2:
                st.subheader("📊 Price Momentum")
                # Load historical data for charting
                mockDir = config.get("data", "mockDir")
                filePath = os.path.join(mockDir, f"{finalSymbol}.csv")
                
                if os.path.exists(filePath):
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
    st.image("https://images.unsplash.com/photo-1611974717482-1da3de121010?auto=format&fit=crop&q=80&w=1470&ixlib=rb-4.0.3", caption="Enterprise Market Surveillance System")
