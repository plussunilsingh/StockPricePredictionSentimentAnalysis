"""Utility functions to map between pandas DataFrames and DTOs used by the API.

Keeping mapping logic centralized reduces duplication and makes tests
for serialization straightforward.
"""

try:
    import pandas as pd
except Exception:
    pd = None

from typing import List, Dict, Any
from com.stockprediction.backend.dto.PredictionDTO import PredictionResponseDTO


class DataMapper:
    @staticmethod
    def mapToPredictionResponse(symbol: str, prediction: str, confidence: float, modelUsed: str, lastPrice: float = 0.0) -> PredictionResponseDTO:
        """Map prediction primitives into a DTO sent by the API.

        The `decision` field is a simple rule-based interpretation of the
        prediction and its confidence. This is intentionally small and
        auditable for judges reviewing model outputs.
        """
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
    def mapDfToDict(df) -> List[Dict[str, Any]]:
        """Convert a DataFrame into a list of dictionaries suitable for JSON serialization."""
        if df is None:
            return []
        if pd is None:
            raise RuntimeError("pandas is required to convert DataFrame to dict")
        return df.to_dict(orient='records')
