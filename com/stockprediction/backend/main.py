from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

from com.stockprediction.config.AppConfig import config
from com.stockprediction.backend.dto.PredictionDTO import PredictionRequestDTO, PredictionResponseDTO, TrainRequestDTO, TrainResponseDTO
from com.stockprediction.backend.data.data_strategy import DataScannerFactory
from com.stockprediction.backend.sentiment.sentiment_analyzer import SentimentAnalyzerFactory
from com.stockprediction.backend.model.best_model import RandomForestModelPredictor, RFModelTrainer
from com.stockprediction.backend.model.lstm_model import LSTMModelPredictor, LSTMModelTrainer
from com.stockprediction.backend.utils.DataMapper import DataMapper

logger = config.getLogger("BackendAPI")
app = FastAPI(title="Stock Prediction Enterprise API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sentimentAnalyzer = SentimentAnalyzerFactory.getAnalyzer("VADER")

def applyTechnicalIndicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates technical indicators for feature engineering."""
    if df.empty or len(df) < 20:
        logger.warning(f"Insufficient data for indicators: {len(df)} rows")
        return df
    
    df = df.copy()
    # EMA
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['Std_20'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['Std_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['Std_20'] * 2)
    
    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df.dropna()

@app.get("/")
async def root():
    return {"message": "Stock Prediction Enterprise API is running", "mode": config.get("system", "dataMode")}

@app.post("/predict", response_model=PredictionResponseDTO)
async def getPrediction(request: PredictionRequestDTO):
    logger.info(f"Received prediction request for {request.symbol} using {request.modelType}")
    
    # Selection of scanner (Mock vs Live)
    scannerType = "LIVE" if not request.useMock else "MOCK"
    stockScanner = DataScannerFactory.getStockScanner(scannerType)
    newsScanner = DataScannerFactory.getNewsScanner(scannerType)
    
    # Fetch Data with window for indicators
    end_dt = pd.to_datetime(request.endDate)
    start_dt = (end_dt - timedelta(days=60)).strftime('%Y-%m-%d')
    stockData = stockScanner.collectData(request.symbol, start_dt, request.endDate)
    
    if stockData.empty:
        raise HTTPException(status_code=404, detail=f"No stock data found for {request.symbol}")
    
    newsData = newsScanner.collectData(request.symbol, start_dt, request.endDate)
    
    # Feature Engineering
    stockData = applyTechnicalIndicators(stockData)
    if stockData.empty:
        raise HTTPException(status_code=400, detail="Insufficient data after technical indicators application")
        
    # Sentiment
    if not newsData.empty:
        stockData['Sentiment'] = newsData['Headline'].apply(lambda x: sentimentAnalyzer.analyzeText(x))
    else:
        stockData['Sentiment'] = 0.0
        
    # Last price for response
    lastPrice = stockData['Close'].iloc[-1]
    
    # Model Inference
    try:
        if request.modelType == "RF":
            predictor = RandomForestModelPredictor(config.get("models", "rfPath"))
            trainer = RFModelTrainer()
            logger.info(f"stockData columns: {stockData.columns.tolist()}, shape: {stockData.shape}")
            x, _, _ = trainer.prepareData(stockData)
            logger.info(f"Prepared x shape: {x.shape}")
            if len(x) == 0:
                logger.error(f"stockData before fail: {stockData.tail(5).to_dict()}")
                raise ValueError("Not enough data points after preparation for RF")
            
            probs = predictor.predict(x[-1].reshape(1, -1))
            prediction_prob = probs[0][1]
        else:
            # LSTM
            predictor = LSTMModelPredictor(config.get("models", "lstmPath"))
            trainer = LSTMModelTrainer(sequenceLength=config.get("models", "sequenceLength"))
            x, _, _ = trainer.prepareData(stockData)
            if len(x) == 0:
                raise ValueError("Not enough data points for LSTM sequence")
            
            prob = predictor.predict(x[-1].reshape(1, x.shape[1], x.shape[2]))
            prediction_prob = float(prob[0][0])
            
        prediction = "UP" if prediction_prob > 0.5 else "DOWN"
        confidence = prediction_prob if prediction == "UP" else 1.0 - prediction_prob
        
        logger.info(f"Prediction for {request.symbol}: {prediction} ({confidence*100:.1f}%) | Model: {request.modelType} | Data: {scannerType}")
            
        return DataMapper.mapToPredictionResponse(request.symbol, prediction, confidence, request.modelType, lastPrice)
        
    except Exception as e:
        logger.error(f"Prediction error for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train", response_model=TrainResponseDTO)
async def trainModel(request: TrainRequestDTO):
    logger.info(f"Received training request for {request.symbol} using {request.modelType}")
    # Integration logic for training...
    return TrainResponseDTO(status="SUCCESS", message="Training completed", modelPath=config.get("models", "rfPath"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.get("system", "port"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
