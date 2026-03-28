from pydantic import BaseModel, Field
from typing import Optional, List

class PredictionRequestDTO(BaseModel):
    symbol: str = Field(..., example="RELIANCE.NS")
    startDate: str = Field(..., example="2026-01-01")
    endDate: str = Field(..., example="2026-03-28")
    useMock: bool = Field(True, example=True)
    modelType: str = Field("RF", example="RF")

class PredictionResponseDTO(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    decision: str
    modelUsed: str
    lastClose: Optional[float] = None
    changePercent: Optional[float] = None

class TrainRequestDTO(BaseModel):
    symbol: str = Field(..., example="RELIANCE.NS")
    startDate: str = Field(..., example="2026-01-01")
    endDate: str = Field(..., example="2026-03-28")
    useMock: bool = Field(True, example=True)
    modelType: str = Field("RF", example="RF")

class TrainResponseDTO(BaseModel):
    status: str
    message: str
    modelPath: str
