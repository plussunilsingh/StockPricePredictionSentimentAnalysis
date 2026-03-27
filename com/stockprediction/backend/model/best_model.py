import joblib
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from com.stockprediction.config.AppConfig import config

logger = config.getLogger("RandomForestModel")

class RandomForestModelPredictor:
    _instance = None
    _model = None

    def __new__(cls, loadPath: str = None):
        if cls._instance is None:
            cls._instance = super(RandomForestModelPredictor, cls).__new__(cls)
            cls._instance._loadModel(loadPath)
        return cls._instance

    def _loadModel(self, loadPath: str):
        if loadPath and os.path.exists(loadPath):
            logger.info(f"Loading RF Model from {loadPath}")
            self._model = joblib.load(loadPath)
        else:
            logger.warning(f"RF Model not found or path not provided. Model will require training.")

    def predict(self, xTest: np.ndarray):
        if self._model is None:
            raise ValueError("RF Model not loaded. Train the model first.")
        
        # Flatten xTest if it's 3D (samples, sequence, features)
        if len(xTest.shape) == 3:
            xTest = xTest.reshape(xTest.shape[0], -1)
            
        return self._model.predict_proba(xTest)

    def trainAndSave(self, xTrain, yTrain, savePath: str):
        logger.info("Training and Saving RF Model")
        if len(xTrain.shape) == 3:
            xTrain = xTrain.reshape(xTrain.shape[0], -1)
            
        if self._model is None:
            self._model = RandomForestClassifier(n_estimators=100, random_state=42)
            
        self._model.fit(xTrain, yTrain)
        os.makedirs(os.path.dirname(savePath), exist_ok=True)
        joblib.dump(self._model, savePath)
        logger.info(f"RF Model saved to {savePath}")

class RFModelTrainer:
    def prepareData(self, data: pd.DataFrame, targetColumn: str = 'Close'):
        logger.info("Preparing data for RF Training")
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', targetColumn, 'Target', 'Next_Close']]
        
        data = data.copy()
        data['Next_Close'] = data[targetColumn].shift(-1)
        data['Target'] = (data['Next_Close'] > data[targetColumn]).astype(int)
        data = data.dropna(subset=['Target'] + featureCols)

        x = data[featureCols].values
        y = data['Target'].values
        return x, y, featureCols
