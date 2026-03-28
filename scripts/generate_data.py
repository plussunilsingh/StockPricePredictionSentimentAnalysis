import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_stock_data(symbol, start_price, days=60):
    dates = [datetime(2026, 1, 1) + timedelta(days=i) for i in range(days)]
    prices = [start_price]
    for _ in range(days - 1):
        change = np.random.normal(0, 2)
        prices.append(prices[-1] + change)
    
    df = pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Open': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
        'High': [p * (1 + abs(np.random.normal(0.02, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0.02, 0.01))) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, days)
    })
    df.to_csv(f'data/{symbol}.csv', index=False)
    print(f"Generated data/{symbol}.csv")

def generate_news_data(symbol, days=60):
    dates = [datetime(2026, 1, 1) + timedelta(days=i) for i in range(days)]
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
    generate_stock_data('RELIANCE', 2900, days=days_long)
    generate_news_data('RELIANCE', days=days_long)
    generate_stock_data('TCS', 3800, days=days_long)
    generate_news_data('TCS', days=days_long)
    generate_stock_data('INFY', 1500, days=days_long)
    generate_news_data('INFY', days=days_long)
    generate_stock_data('HDFCBANK', 1450, days=days_long)
    generate_news_data('HDFCBANK', days=days_long)
    generate_stock_data('ICICIBANK', 1050, days=days_long)
    generate_news_data('ICICIBANK', days=days_long)
    generate_stock_data('SBIN', 750, days=days_long)
    generate_news_data('SBIN', days=days_long)
