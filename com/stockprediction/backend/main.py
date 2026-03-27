print("Backend: Starting imports...")
from fastapi import FastAPI, HTTPException
print("Backend: FastAPI imported.")
from pydantic import BaseModel
print("Backend: Pydantic imported.")
import sys
import os
print("Backend: sys/os imported.")
from com.stockprediction.backend.data.data_factory import DataCollectorFactory, DataType
print("Backend: Data layers imported.")
from com.stockprediction.backend.sentiment.sentiment_analyzer import SentimentAnalyzerFactory
print("Backend: Sentiment analyzer imported.")
from com.stockprediction.backend.pipeline.features import FeatureEngineer
print("Backend: Feature engineer imported.")
from com.stockprediction.backend.model.lstm_model import LSTMModelPredictor
print("Backend: LSTM Model imported.")
from com.stockprediction.backend.model.trainer import ModelTrainer
print("Backend: Model trainer imported.")
import pandas as pd
print("Backend: Pandas imported.")
import numpy as np
print("Backend: Numpy imported.")

print("Backend: Imports completed.")
app = FastAPI(title="Stock Prediction ML API")
print("Backend: FastAPI app created.")

# Initialize components
featureEngineer = FeatureEngineer()
sentimentAnalyzer = SentimentAnalyzerFactory.getAnalyzer("VADER")
modelTrainer = ModelTrainer(sequenceLength=5) # use 5 for small sample data
model_path = "data/model.h5"

class PredictionRequest(BaseModel):
    symbol: str
    startDate: str = "2026-03-01"
    endDate: str = "2026-03-15"
    useMock: bool = True

class PredictionResponse(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    decision: str

@app.get("/")
def readRoot():
    return {"message": "Stock Prediction ML API is running!"}

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
    data = featureEngineer.mergeSentiment(stockData, newsData, sentimentAnalyzer)
    data = featureEngineer.addMovingAverage(data, 'Close', 3)
    data = featureEngineer.addRSI(data, 'Close', 3) # small window for sample
    data = data.dropna()
    
    if len(data) <= modelTrainer.sequenceLength:
        raise HTTPException(status_code=400, detail="Not enough data for the sequence length")
        
    # Prepare data for training
    x, y, featureCols = modelTrainer.createSequences(data)
    
    # Initialize and train model
    inputShape = (x.shape[1], x.shape[2])
    predictor = LSTMModelPredictor(inputShape=inputShape)
    predictor.train(x, y, epochs=5, batchSize=2)
    
    # Save model
    predictor.saveModel(model_path)
    
    return {"message": "Model trained and saved successfully", "features": featureCols}

@app.post("/predict", response_model=PredictionResponse)
def getPrediction(req: PredictionRequest):
    # Fetch data for prediction (last few days to form a sequence)
    stockCollector = DataCollectorFactory.getCollector(DataType.CSV_STOCK if req.useMock else DataType.STOCK)
    newsCollector = DataCollectorFactory.getCollector(DataType.CSV_NEWS if req.useMock else DataType.NEWS)
    
    stockData = stockCollector.collectData(req.symbol, req.startDate, req.endDate)
    newsData = newsCollector.collectData(req.symbol, req.startDate, req.endDate)
    
    if stockData.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
        
    # Feature Engineering
    data = featureEngineer.mergeSentiment(stockData, newsData, sentimentAnalyzer)
    data = featureEngineer.addMovingAverage(data, 'Close', 3)
    data = featureEngineer.addRSI(data, 'Close', 3)
    data = data.dropna()
    
    if len(data) < modelTrainer.sequenceLength:
        raise HTTPException(status_code=400, detail="Not enough data for sequence")

    # Load Model
    if not os.path.exists(model_path):
        # Fallback to training if model doesn't exist (for demo purposes)
        trainModel(req)
        
    predictor = LSTMModelPredictor(loadPath=model_path)
    
    # Prepare last sequence
    featureCols = [col for col in data.columns if col not in ['Date', 'Headline', 'Target', 'Next_Close']]
    last_sequence = data[featureCols].values[-modelTrainer.sequenceLength:]
    last_sequence = np.expand_dims(last_sequence, axis=0)
    
    prediction_prob = predictor.predict(last_sequence)[0][0]
    prediction = "UP" if prediction_prob > 0.5 else "DOWN"
    confidence = float(prediction_prob if prediction_prob > 0.5 else 1 - prediction_prob)
    decision = "BUY" if (prediction == "UP" and confidence > 0.6) else "SELL" if (prediction == "DOWN" and confidence > 0.6) else "HOLD"
    
    return PredictionResponse(
        symbol=req.symbol,
        prediction=prediction,
        confidence=confidence,
        decision=decision
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
