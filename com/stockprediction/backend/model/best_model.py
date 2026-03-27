from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import pandas as pd
import numpy as np

class RandomForestModelPredictor:
    """
    Random Forest Classifier for Stock Price Prediction.
    """
    def __init__(self, loadPath=None):
        if loadPath and os.path.exists(loadPath):
            self.model = joblib.load(loadPath)
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def train(self, xTrain, yTrain):
        # Flatten xTrain if it's 3D (samples, sequence, features)
        if len(xTrain.shape) == 3:
            xTrain = xTrain.reshape(xTrain.shape[0], -1)
        self.model.fit(xTrain, yTrain)
        print("Random Forest Model trained.")

    def predict(self, xTest):
        # Flatten xTest if it's 3D
        if len(xTest.shape) == 3:
            xTest = xTest.reshape(xTest.shape[0], -1)
        return self.model.predict_proba(xTest)

    def saveModel(self, path: str):
        joblib.dump(self.model, path)
        print(f"Random Forest Model saved to {path}")

class RFModelTrainer:
    """
    Handles preparation of data for Random Forest.
    """
    def __init__(self):
        pass

    def prepareData(self, data: pd.DataFrame, targetColumn: str = 'Close'):
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', targetColumn, 'Target', 'Next_Close']]
        
        data = data.copy()
        data['Next_Close'] = data[targetColumn].shift(-1)
        data['Target'] = (data['Next_Close'] > data[targetColumn]).astype(int)
        data = data.dropna(subset=['Target'] + featureCols)

        x = data[featureCols].values
        y = data['Target'].values
            
        return x, y, featureCols
