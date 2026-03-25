import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# Configuration for Backend API Request
BACKEND_URL = "http://localhost:8000/predict"

st.set_page_config(page_title="Stock Prediction Dashboard", layout="wide")

st.title("📈 Data-Driven Stock Price Prediction using Sentiment Analysis")
st.markdown("This dashboard provides data-driven trading signals combining Technical Analysis and Market Sentiment.")

# Sidebar for User Input
st.sidebar.header("User Settings")
symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, RELIANCE.NS)", value="AAPL")

if st.sidebar.button("Predict"):
    with st.spinner(f"Fetching predictions for {symbol}..."):
        try:
            # Request to the Java Backend (which will call the Python ML Service)
            response = requests.get(BACKEND_URL, params={"symbol": symbol})
            
            if response.status_code == 200:
                data = response.json()
                
                prediction = data.get("prediction", "N/A")
                confidence = data.get("confidence", 0.0)
                decision = data.get("decision", "HOLD")
                
                # Display Layout
                st.subheader(f"Prediction Results for {symbol}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Predicted Movement", prediction)
                col2.metric("Model Confidence", f"{confidence * 100:.1f}%")
                
                decisionColor = "green" if decision == "BUY" else "red" if decision == "SELL" else "orange"
                col3.markdown(f"<h3 style='text-align: center; color: {decisionColor};'>Decision: {decision}</h3>", unsafe_allow_html=True)
                
                # Render chart using simple yfinance pull just for visualization
                st.write("---")
                st.subheader("Recent Price Trend (1 Month)")
                stockData = yf.download(symbol, period="1mo")
                st.line_chart(stockData['Close'])
            else:
                st.error(f"Failed to fetch prediction from backend API. Status code: {response.status_code}")
                
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            st.info("Make sure the Java Backend (port 8080) is running.")
