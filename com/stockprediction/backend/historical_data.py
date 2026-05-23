import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Define ticker symbols for requested indices
# Note: For SENSEX and NIFTY, Yahoo Finance uses specific tickers
INDICES = {
    "DJIA": "^DJI",
    "SP500": "^GSPC",
    "NIFTY_50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANKNIFTY": "^NSEBANK"
}

def fetch_historical_data(data_dir: str):
    """
    Fetches the maximum available historical data for all target indices 
    and saves them as CSV files.
    """
    os.makedirs(data_dir, exist_ok=True)
    
    for name, ticker in INDICES.items():
        print(f"Fetching historical data for {name} ({ticker})...")
        try:
            # period="max" will pull as far back as yfinance has data (often to 1920s for DJI/SP500)
            stock = yf.Ticker(ticker)
            df = stock.history(period="max")
            
            if df.empty:
                print(f"  -> No data found for {name}.")
                continue
                
            file_path = os.path.join(data_dir, f"{name}_historical.csv")
            df.to_csv(file_path)
            
            start_date = df.index.min().strftime('%Y-%m-%d')
            end_date = df.index.max().strftime('%Y-%m-%d')
            total_years = (df.index.max() - df.index.min()).days / 365.25
            
            print(f"  -> Saved to {file_path}")
            print(f"  -> Data span: {start_date} to {end_date} (Approx {total_years:.1f} years)")
            
        except Exception as e:
            print(f"  -> Error fetching data for {name}: {e}")

if __name__ == "__main__":
    PROJECT_ROOT = "/Users/suniltomar/Desktop/workspace/StockPricePredictionSentimentAnalysis"
    DATA_DIR = os.path.join(PROJECT_ROOT, "data", "historical")
    fetch_historical_data(DATA_DIR)
