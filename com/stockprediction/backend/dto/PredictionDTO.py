from pydantic import BaseModel
from typing import Optional, List

class PredictionRequestDTO(BaseModel):
    symbol: str
    startDate: str
    endDate: str
    useMock: bool = True
    modelType: str = "RF"

class PredictionResponseDTO(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    decision: str
    modelUsed: str
    lastClose: Optional[float] = None
    changePercent: Optional[float] = None

class TrainRequestDTO(BaseModel):
    symbol: str
    startDate: str
    endDate: str
    useMock: bool = True
    modelType: str = "RF"

class TrainResponseDTO(BaseModel):
    status: str
    message: str
    modelPath: str
