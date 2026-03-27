import pandas as pd
import numpy as np
import os
from com.stockprediction.config.AppConfig import config
from com.stockprediction.backend.data.data_strategy import DataScannerFactory
from com.stockprediction.backend.model.best_model import RandomForestModelPredictor, RFModelTrainer
from com.stockprediction.backend.model.lstm_model import LSTMModelPredictor, LSTMModelTrainer

# Re-use the technical indicator logic from main.py (or centralize it)
def applyTechnicalIndicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 20: return df
    df = df.copy()
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['Std_20'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['Std_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['Std_20'] * 2)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df.dropna()

def train():
    symbol = "AAPL" # Use AAPL for base training
    scanner = DataScannerFactory.getStockScanner("MOCK")
    df = scanner.collectData(symbol, "2020-01-01", "2026-03-27")
    
    if df.empty:
        print("No training data found!")
        return

    df = applyTechnicalIndicators(df)
    df['Sentiment'] = 0.0 # Placeholder
    
    # Train RF
    rf_trainer = RFModelTrainer()
    x_rf, y_rf, _ = rf_trainer.prepareData(df)
    rf_predictor = RandomForestModelPredictor()
    rf_predictor.trainAndSave(x_rf, y_rf, config.get("models", "rfPath"))
    print(f"RF Model trained with {x_rf.shape[1]} features.")

    # Train LSTM
    lstm_trainer = LSTMModelTrainer(sequenceLength=config.get("models", "sequenceLength"))
    x_lstm, y_lstm, _ = lstm_trainer.prepareData(df)
    lstm_predictor = LSTMModelPredictor()
    lstm_predictor.trainAndSave(x_lstm, y_lstm, config.get("models", "lstmPath"), epochs=5)
    print(f"LSTM Model trained with shape {x_lstm.shape}.")

if __name__ == "__main__":
    train()
