"""Small synthetic data generator used for demo and development runs.

Produces simple stock CSVs and mock news CSVs used by the demo frontend
and unit tests. The generator is intentionally explicit so judges can
see how demo data was created.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_stock_data(symbol, start_price, days=180):
    # End exactly at today: 2026-03-28 (project was developed with deterministic end date)
    end_date = datetime(2026, 3, 28)
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]
    prices = [float(start_price)]
    for _ in range(days - 1):
        change = float(np.random.normal(0, 2))
        prices.append(prices[-1] + change)
    
    df = pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Open': [p * (1 + float(np.random.normal(0, 0.01))) for p in prices],
        'High': [p * (1 + abs(float(np.random.normal(0.02, 0.01)))) for p in prices],
        'Low': [p * (1 - abs(float(np.random.normal(0.02, 0.01)))) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, days)
    })
    df.to_csv(f'data/{symbol}.csv', index=False)
    print(f"Generated data/{symbol}.csv")

def generate_news_data(symbol, days=180):
    end_date = datetime(2026, 3, 28)
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]
    headlines = [
        f"Positive outlook for {symbol} after strong earnings report",
        f"{symbol} announces new strategic partnership",
        f"Market analysts raise target price for {symbol}",
        f"{symbol} faces supply chain challenges",
        f"New competition enters the market for {symbol} products",
        f"Bullish sentiment prevails for {symbol} investors",
        f"Regulatory hurdles ahead for {symbol}'s latest acquisition",
        f"{symbol} stock hits quarterly high",
        f"Concerns about {symbol}'s latest technology launch",
        f"Optimism grows for {symbol}'s market share in Asia"
    ]
    
    df = pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Headline': [np.random.choice(headlines) for _ in range(days)]
    })
    df.to_csv(f'data/{symbol}_news.csv', index=False)
    print(f"Generated data/{symbol}_news.csv")

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    days_long = 180
    generate_stock_data('AAPL', 150, days=days_long)
    generate_news_data('AAPL', days=days_long)
    generate_stock_data('MSFT', 400, days=days_long)
    generate_news_data('MSFT', days=days_long)
    generate_stock_data('GOOGL', 140, days=days_long)
    generate_news_data('GOOGL', days=days_long)
    
    # Indian Indices
    generate_stock_data('NSEI', 22000, days=days_long) # ^NSEI
    generate_news_data('NSEI', days=days_long)
    generate_stock_data('BSESN', 73000, days=days_long) # ^BSESN
    generate_news_data('BSESN', days=days_long)
    generate_stock_data('NSEBANK', 47000, days=days_long)
    generate_news_data('NSEBANK', days=days_long)
    generate_stock_data('CNXIT', 35000, days=days_long)
    generate_news_data('CNXIT', days=days_long)
    
    # Major Indian Stocks
    generate_stock_data('RELIANCE.NS', 2900, days=days_long)
    generate_news_data('RELIANCE.NS', days=days_long)
    generate_stock_data('TCS.NS', 3800, days=days_long)
    generate_news_data('TCS.NS', days=days_long)
    generate_stock_data('INFY.NS', 1500, days=days_long)
    generate_news_data('INFY.NS', days=days_long)
    generate_stock_data('HDFCBANK.NS', 1450, days=days_long)
    generate_news_data('HDFCBANK.NS', days=days_long)
    generate_stock_data('ICICIBANK.NS', 1050, days=days_long)
    generate_news_data('ICICIBANK.NS', days=days_long)
    generate_stock_data('SBIN.NS', 750, days=days_long)
    generate_news_data('SBIN.NS', days=days_long)
