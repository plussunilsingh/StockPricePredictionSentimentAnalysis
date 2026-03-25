import numpy as np
import pandas as pd
from .lstm_model import LSTMModelPredictor

class ModelTrainer:
    """
    Handles preparation of sequences and training the model.
    """
    def __init__(self, sequenceLength: int = 10):
        self.sequenceLength = sequenceLength

    def createSequences(self, data: pd.DataFrame, targetColumn: str = 'Close'):
        """
        Creates sequences of length `sequenceLength` to predict UP(1) or DOWN(0) of `targetColumn`.
        """
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', targetColumn, 'Target', 'Next_Close']]
        # Re-insert targetColumn as part of features
        featureCols.append(targetColumn)
        
        # Shift target column by -1 to get "next day's" price difference
        data = data.copy()
        data['Next_Close'] = data[targetColumn].shift(-1)
        data['Target'] = (data['Next_Close'] > data[targetColumn]).astype(int)
        
        # Drop rows with NaN (especially the last one)
        data = data.dropna(subset=['Target'] + featureCols)

        dataset = data[featureCols].values
        target = data['Target'].values

        x, y = [], []
        for i in range(self.sequenceLength, len(dataset)):
            x.append(dataset[i-self.sequenceLength:i, :])
            y.append(target[i])
            
        return np.array(x), np.array(y), featureCols
