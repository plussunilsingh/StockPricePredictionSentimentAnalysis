import os
import pandas as pd
import numpy as np
from com.stockprediction.config.AppConfig import config

logger = config.getLogger("LSTMModel")

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
except ImportError:
    tf = None

class LSTMModelPredictor:
    _instance = None
    _model = None

    def __new__(cls, loadPath: str = None):
        if cls._instance is None:
            cls._instance = super(LSTMModelPredictor, cls).__new__(cls)
            cls._instance._loadModel(loadPath)
        return cls._instance

    def _loadModel(self, loadPath: str):
        if tf is None:
            logger.error("TensorFlow not installed. LSTM predictor unavailable.")
            return

        if loadPath and os.path.exists(loadPath):
            logger.info(f"Loading LSTM Model from {loadPath}")
            self._model = load_model(loadPath)
        else:
            logger.warning(f"LSTM Model not found or path not provided: {loadPath}")

    def predict(self, xTest: np.ndarray):
        if self._model is None:
            raise ValueError("LSTM Model not loaded. Train the model first.")
        return self._model.predict(xTest)

    def trainAndSave(self, xTrain, yTrain, savePath: str, epochs: int = 5):
        if tf is None:
            logger.error("TensorFlow not installed. Cannot train LSTM.")
            return

        logger.info(f"Building and Training LSTM Model. Input shape: {xTrain.shape}")
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(xTrain.shape[1], xTrain.shape[2])),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25, activation='relu'),
            Dense(units=1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        model.fit(xTrain, yTrain, epochs=epochs, batch_size=32, verbose=0)
        os.makedirs(os.path.dirname(savePath), exist_ok=True)
        model.save(savePath)
        self._model = model
        logger.info(f"LSTM Model saved to {savePath}")

class LSTMModelTrainer:
    def __init__(self, sequenceLength: int = 10):
        self.sequenceLength = sequenceLength

    def prepareData(self, data: pd.DataFrame, targetColumn: str = 'Close'):
        logger.info("Preparing data for LSTM Training")
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', targetColumn, 'Target', 'Next_Close']]
        
        data = data.copy()
        data['Next_Close'] = data[targetColumn].shift(-1)
        data['Target'] = (data['Next_Close'] > data[targetColumn]).astype(int)
        data = data.dropna(subset=['Target'])

        x, y = [], []
        features = data[featureCols].values
        targets = data['Target'].values

        for i in range(self.sequenceLength, len(features)):
            x.append(features[i-self.sequenceLength:i])
            y.append(targets[i])

        return np.array(x), np.array(y), featureCols
