"""Pydantic DTOs used by the backend API.

The DTOs below describe the JSON schemas accepted by the `/predict` and
`/train` endpoints and the shape of the responses. Keeping these schemas
explicit and documented makes the API self-describing and easier to audit.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class PredictionRequestDTO(BaseModel):
    """Request body for prediction endpoint.

    Attributes:
        symbol: Ticker symbol to request predictions for.
        startDate/endDate: ISO-formatted date strings bounding the historical window.
        useMock: Whether to use mock CSV data instead of live data.
        modelType: Model identifier string (e.g., 'RF' or 'LSTM').
    """
    symbol: str = Field(..., example="RELIANCE.NS")
    startDate: str = Field(..., example="2026-01-01")
    endDate: str = Field(..., example="2026-03-28")
    useMock: bool = Field(True, example=True)
    modelType: str = Field("RF", example="RF")


class PredictionResponseDTO(BaseModel):
    """Response payload returned by the prediction endpoint.

    Fields are deliberately compact: prediction is a simple UP/DOWN label,
    confidence is a [0,1] float, and `decision` is an operational action
    derived from prediction and confidence (BUY/HOLD/SELL).
    """
    symbol: str
    prediction: str
    confidence: float
    decision: str
    modelUsed: str
    lastClose: Optional[float] = None
    changePercent: Optional[float] = None


class TrainRequestDTO(BaseModel):
    """Request payload for triggering a training run (currently not fully wired)."""
    symbol: str = Field(..., example="RELIANCE.NS")
    startDate: str = Field(..., example="2026-01-01")
    endDate: str = Field(..., example="2026-03-28")
    useMock: bool = Field(True, example=True)
    modelType: str = Field("RF", example="RF")


class TrainResponseDTO(BaseModel):
    """Lightweight response indicating training status and saved model path."""
    status: str
    message: str
    modelPath: str
