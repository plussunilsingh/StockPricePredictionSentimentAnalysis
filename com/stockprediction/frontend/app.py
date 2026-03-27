import streamlit as st
import requests
import pandas as pd
import os

# Configuration for Backend API Request
BACKEND_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Stock Prediction Dashboard", layout="wide")
st.title("📈 Data-Driven Stock Price Prediction")
st.markdown("Combining Technical Analysis and Market Sentiment for better insights.")

# Sidebar for User Input
st.sidebar.header("User Settings")

# Predefined common symbols for easy selection
market_options = {
    "NIFTY 50 (NSEI)": "NSEI",
    "SENSEX (BSESN)": "BSESN",
    "NIFTY BANK": "NSEBANK",
    "NIFTY IT": "CNXIT",
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
}

selected_label = st.sidebar.selectbox("Select Market/Security", list(market_options.keys()), index=0)
symbol = st.sidebar.text_input("Or type Symbol manually", value=market_options[selected_label])

model_type = st.sidebar.radio("Select Prediction Model", ["RF", "LSTM"], index=0)

if st.sidebar.button("Predict"):
    with st.spinner(f"Fetching predictions for {symbol} using {model_type}..."):
        try:
            response = requests.post(
                BACKEND_URL, 
                json={
                    "symbol": symbol, 
                    "startDate": "2026-01-01", 
                    "endDate": "2026-03-31", 
                    "useMock": True,
                    "modelType": model_type
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Results for {symbol} ({data.get('modelUsed')} Model)")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Movement", data.get("prediction"))
                col2.metric("Confidence", f"{data.get('confidence') * 100:.1f}%")
                
                decision = data.get("decision")
                color = "green" if decision == "BUY" else "red" if decision == "SELL" else "orange"
                col3.markdown(f"<h3 style='text-align: center; color: {color};'>Decision: {decision}</h3>", unsafe_allow_html=True)
                
                st.write("---")
                st.subheader("Price Trend (Mock Data)")
                csv_path = f"data/{symbol}.csv"
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    st.line_chart(df.set_index('Date')['Close'].tail(30))
                else:
                    st.warning(f"Mock data file {csv_path} not found for charting.")
            else:
                st.error(f"Backend Error: {response.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")
