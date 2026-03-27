import pandas as pd
from com.stockprediction.backend.dto.PredictionDTO import PredictionResponseDTO
from typing import Dict, Any

class DataMapper:
    @staticmethod
    def mapToPredictionResponse(symbol: str, prediction: str, confidence: float, modelUsed: str, lastPrice: float = 0.0) -> PredictionResponseDTO:
        decision = "HOLD"
        if prediction == "UP" and confidence > 0.6:
            decision = "BUY"
        elif prediction == "DOWN" and confidence > 0.6:
            decision = "SELL"
            
        return PredictionResponseDTO(
            symbol=symbol,
            prediction=prediction,
            confidence=round(confidence, 2),
            decision=decision,
            modelUsed=modelUsed,
            lastClose=round(lastPrice, 2)
        )

    @staticmethod
    def mapDfToDict(df: pd.DataFrame) -> List[Dict[str, Any]]:
        return df.to_dict(orient='records')
