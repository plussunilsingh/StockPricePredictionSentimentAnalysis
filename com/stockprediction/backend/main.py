from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

app = FastAPI(title="Stock Prediction ML API")

class PredictionRequest(BaseModel):
    symbol: str
    startDate: str
    endDate: str

class PredictionResponse(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    decision: str

@app.get("/")
def readRoot():
    return {"message": "Stock Prediction ML API is running!"}

@app.post("/predict", response_model=PredictionResponse)
def getPrediction(req: PredictionRequest):
    # This acts as an orchestrator for the strategy patterns.
    # In a real scenario, this would load the trained model and output a prediction based on live inputs.
    
    # Returning a dummy response to fulfill the API structure requirement
    return PredictionResponse(
        symbol=req.symbol,
        prediction="UP",
        confidence=0.82,
        decision="BUY"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
