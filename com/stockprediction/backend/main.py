from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from com.stockprediction.backend.data.data_factory import DataCollectorFactory, DataType
from com.stockprediction.backend.sentiment.sentiment_analyzer import SentimentAnalyzerFactory
from com.stockprediction.backend.pipeline.features import FeatureEngineer
from com.stockprediction.backend.model.lstm_model import LSTMModelPredictor
from com.stockprediction.backend.model.trainer import ModelTrainer
from com.stockprediction.backend.model.best_model import RandomForestModelPredictor, RFModelTrainer
import pandas as pd
import numpy as np

app = FastAPI(title="Stock Prediction ML API")

# Initialize components
featureEngineer = FeatureEngineer()
sentimentAnalyzer = SentimentAnalyzerFactory.getAnalyzer("VADER")
modelTrainer = ModelTrainer(sequenceLength=5)
rfTrainer = RFModelTrainer()
model_path = "data/model.h5"
rf_model_path = "data/rf_model.joblib"

class PredictionRequest(BaseModel):
    symbol: str = "AAPL"
    startDate: str = "2026-01-01"
    endDate: str = "2026-03-31"
    useMock: bool = True
    modelType: str = "RF" # "RF" or "LSTM"

class PredictionResponse(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    decision: str
    modelUsed: str

@app.get("/")
def readRoot():
    return {"message": "Stock Prediction ML API is running!"}

def apply_features(df: pd.DataFrame, newsData: pd.DataFrame):
    print(f"Applying features to {len(df)} rows of stock data and {len(newsData)} news items.")
    data = featureEngineer.mergeSentiment(df, newsData, sentimentAnalyzer)
    data = featureEngineer.addMovingAverage(data, 'Close', 5)
    data = featureEngineer.addEMA(data, 'Close', 5)
    data = featureEngineer.addRSI(data, 'Close', 14)
    data = featureEngineer.addMACD(data, 'Close')
    data = featureEngineer.addBollingerBands(data, 'Close')
    print(f"Data after features (before dropna): {len(data)}")
    data = data.dropna()
    print(f"Data after dropna: {len(data)}")
    return data

@app.post("/train")
def trainModel(req: PredictionRequest):
    # Fetch data
    stockCollector = DataCollectorFactory.getCollector(DataType.CSV_STOCK if req.useMock else DataType.STOCK)
    newsCollector = DataCollectorFactory.getCollector(DataType.CSV_NEWS if req.useMock else DataType.NEWS)
    
    stockData = stockCollector.collectData(req.symbol, req.startDate, req.endDate)
    newsData = newsCollector.collectData(req.symbol, req.startDate, req.endDate)
    
    if stockData.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
        
    # Feature Engineering
    data = apply_features(stockData, newsData)
    
    if len(data) <= 15:
        raise HTTPException(status_code=400, detail="Not enough data for training")
        
    if req.modelType == "LSTM":
        # Prepare data for LSTM
        x, y, featureCols = modelTrainer.createSequences(data)
        inputShape = (x.shape[1], x.shape[2])
        predictor = LSTMModelPredictor(inputShape=inputShape)
        predictor.train(x, y, epochs=10, batchSize=4)
        predictor.saveModel(model_path)
        return {"message": "LSTM Model trained successfully", "features": featureCols}
    else:
        # Prepare data for Random Forest
        x, y, featureCols = rfTrainer.prepareData(data)
        predictor = RandomForestModelPredictor()
        predictor.train(x, y)
        predictor.saveModel(rf_model_path)
        return {"message": "Random Forest Model trained successfully", "features": featureCols}

@app.post("/predict", response_model=PredictionResponse)
def getPrediction(req: PredictionRequest):
    # Fetch data for prediction
    stockCollector = DataCollectorFactory.getCollector(DataType.CSV_STOCK if req.useMock else DataType.STOCK)
    newsCollector = DataCollectorFactory.getCollector(DataType.CSV_NEWS if req.useMock else DataType.NEWS)
    
    # Take a slightly larger window to ensure all technical indicators have enough history
    start_dt = (pd.to_datetime(req.endDate) - pd.Timedelta(days=40)).strftime('%Y-%m-%d')
    stockData = stockCollector.collectData(req.symbol, start_dt, req.endDate)
    newsData = newsCollector.collectData(req.symbol, start_dt, req.endDate)
    
    if stockData.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
        
    # Feature Engineering
    data = apply_features(stockData, newsData)
    
    if data.empty:
        raise HTTPException(status_code=400, detail="Not enough data after feature engineering")

    if req.modelType == "LSTM":
        if not os.path.exists(model_path):
            trainModel(req)
        predictor = LSTMModelPredictor(loadPath=model_path)
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', 'Target', 'Next_Close', 'Close']]
        last_sequence = data[featureCols].values[-modelTrainer.sequenceLength:]
        last_sequence = np.expand_dims(last_sequence, axis=0)
        prediction_prob = predictor.predict(last_sequence)[0][0]
    else:
        if not os.path.exists(rf_model_path):
            trainModel(req)
        predictor = RandomForestModelPredictor(loadPath=rf_model_path)
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', 'Target', 'Next_Close', 'Close']]
        print(f"Prediction feature count: {len(featureCols)}. Features: {featureCols}")
        last_features = data[featureCols].values[-1:]
        prediction_prob = predictor.predict(last_features)[0][1] # Probability of UP(1)
    
    prediction = "UP" if prediction_prob > 0.5 else "DOWN"
    confidence = float(prediction_prob if prediction_prob > 0.5 else 1 - prediction_prob)
    decision = "BUY" if (prediction == "UP" and confidence > 0.55) else "SELL" if (prediction == "DOWN" and confidence > 0.55) else "HOLD"
    
    return PredictionResponse(
        symbol=req.symbol,
        prediction=prediction,
        confidence=confidence,
        decision=decision,
        modelUsed=req.modelType
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
