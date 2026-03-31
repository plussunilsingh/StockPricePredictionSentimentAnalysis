import os
import numpy as np

# Optional heavy imports: allow the module to be imported in environments
# where these packages aren't installed (e.g., static analysis). Callers
# that actually use the functionality will encounter helpful runtime errors.
try:
    import joblib
except Exception:
    joblib = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    from sklearn.ensemble import RandomForestClassifier
except Exception:
    RandomForestClassifier = None

from com.stockprediction.config.AppConfig import config

logger = config.getLogger("RandomForestModel")

"""Simple random-forest based predictor used as a fallback / baseline model.

This module exposes two cooperating classes:
- RandomForestModelPredictor: a lightweight singleton wrapper around a
  scikit-learn RandomForestClassifier instance that supports loading,
  predicting and saving models.
- RFModelTrainer: small helper to prepare tabular training data and return
  numpy arrays that are ready for model training.

The design is intentionally pragmatic: clear, documented, and easy to test.
"""


class RandomForestModelPredictor:
    """Singleton wrapper around a RandomForestClassifier.

    The class ensures a single in-memory instance and provides convenience
    methods to train, save and load a model. The `predict` method returns
    predict_proba outputs to give downstream code probability estimates.
    """

    _instance = None
    _model = None

    def __new__(cls, loadPath: str = None):
        if cls._instance is None:
            cls._instance = super(RandomForestModelPredictor, cls).__new__(cls)
            cls._instance._loadModel(loadPath)
        return cls._instance

    def _loadModel(self, loadPath: str):
        if joblib is None:
            logger.warning("joblib not available: model loading disabled.")
            return

        if loadPath and os.path.exists(loadPath):
            logger.info(f"Loading RF Model from {loadPath}")
            try:
                self._model = joblib.load(loadPath)
            except Exception as e:
                logger.error("Failed to load RF model: %s", e)
                self._model = None
        else:
            logger.warning("RF Model not found or path not provided. Model will require training.")

    def predict(self, xTest: np.ndarray) -> np.ndarray:
        if self._model is None:
            raise ValueError("RF Model not loaded. Train the model first.")

        x = np.asarray(xTest)

        if x.ndim == 3:
            x = x.reshape(x.shape[0], -1)
        elif x.ndim != 2:
            raise ValueError(f"Unexpected input array shape: {x.shape}")

        return self._model.predict_proba(x)

    def trainAndSave(self, xTrain: np.ndarray, yTrain: np.ndarray, savePath: str):
        if RandomForestClassifier is None:
            raise RuntimeError("scikit-learn not available: cannot train RF model")

        logger.info("Training RF Model")

        x = np.asarray(xTrain)
        y = np.asarray(yTrain)

        if x.ndim == 3:
            x = x.reshape(x.shape[0], -1)
        elif x.ndim != 2:
            raise ValueError(f"Unexpected training array shape: {x.shape}")

        if self._model is None:
            self._model = RandomForestClassifier(n_estimators=100, random_state=42)

        self._model.fit(x, y)

        # Ensure directory exists before saving
        if savePath:
            if joblib is None:
                logger.warning("joblib not available: trained model will not be saved to disk")
            else:
                os.makedirs(os.path.dirname(savePath), exist_ok=True)
                joblib.dump(self._model, savePath)
                logger.info(f"RF Model saved to {savePath}")
        else:
            logger.warning("No savePath provided; model trained but not saved.")

        return self._model

    @classmethod
    def load_default(cls):
        default_path = config.get("models", "rf_model_path", default=os.path.join("data", "rf_model.joblib"))
        return cls(loadPath=default_path)


class RFModelTrainer:
    """Small utility to convert a pandas DataFrame into training arrays.

    The method here is intentionally explicit: it computes a one-step-ahead
    binary target indicating whether the `targetColumn` increases on the
    next row. It returns (x, y, feature_columns) where `x` is a numpy array
    suitable for scikit-learn estimators.
    """

    def prepareData(self, data, targetColumn: str = 'Close'):
        if pd is None:
            raise RuntimeError("pandas is required to prepare training data")

        logger.info("Preparing data for RF Training")
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', targetColumn, 'Target', 'Next_Close']]

        data = data.copy()
        data['Next_Close'] = data[targetColumn].shift(-1)
        data['Target'] = (data['Next_Close'] > data[targetColumn]).astype(int)

        data = data.dropna(subset=['Target'] + featureCols)

        x = data[featureCols].values
        y = data['Target'].values
        return x, y, featureCols
