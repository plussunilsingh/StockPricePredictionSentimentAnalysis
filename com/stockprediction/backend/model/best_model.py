import joblib
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
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
        """Load a joblib model if `loadPath` exists, otherwise leave unset.

        This method logs what it does to aid debugging during development.
        """
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
        """Return predicted class probabilities for the provided input array.

        Accepts either 2D arrays (n_samples, n_features) or 3D arrays where
        the last two dims are flattened into a feature vector (n_samples, -1).
        Raises ValueError if the model is not loaded.
        """
        if self._model is None:
            raise ValueError("RF Model not loaded. Train the model first.")

        x = np.asarray(xTest)

        if x.ndim == 3:
            # Flatten sequences/features into a single feature vector per sample
            x = x.reshape(x.shape[0], -1)
        elif x.ndim != 2:
            raise ValueError(f"Unexpected input array shape: {x.shape}")

        return self._model.predict_proba(x)

    def trainAndSave(self, xTrain: np.ndarray, yTrain: np.ndarray, savePath: str):
        """Train a RandomForestClassifier on (xTrain, yTrain) and persist it.

        Returns the trained estimator to make testing easier.
        """
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
            os.makedirs(os.path.dirname(savePath), exist_ok=True)
            joblib.dump(self._model, savePath)
            logger.info(f"RF Model saved to {savePath}")
        else:
            logger.warning("No savePath provided; model trained but not saved.")

        return self._model

    @classmethod
    def load_default(cls):
        """Convenience: attempt to load a model from a sensible default path.

        The default path is looked up from the application config if present,
        otherwise a `data/rf_model.joblib` path is used. Returns the singleton
        instance (possibly without a loaded model if the file didn't exist).
        """
        default_path = config.get("models", "rf_model_path", default=os.path.join("data", "rf_model.joblib"))
        return cls(loadPath=default_path)


class RFModelTrainer:
    """Small utility to convert a pandas DataFrame into training arrays.

    The method here is intentionally explicit: it computes a one-step-ahead
    binary target indicating whether the `targetColumn` increases on the
    next row. It returns (x, y, feature_columns) where `x` is a numpy array
    suitable for scikit-learn estimators.
    """

    def prepareData(self, data: pd.DataFrame, targetColumn: str = 'Close'):
        logger.info("Preparing data for RF Training")
        # Exclude obvious non-feature columns; keep all others as features.
        featureCols = [col for col in data.columns if col not in ['Date', 'Headline', targetColumn, 'Target', 'Next_Close']]

        data = data.copy()
        data['Next_Close'] = data[targetColumn].shift(-1)
        data['Target'] = (data['Next_Close'] > data[targetColumn]).astype(int)

        # Drop rows where the target or any selected feature is NaN
        data = data.dropna(subset=['Target'] + featureCols)

        x = data[featureCols].values
        y = data['Target'].values
        return x, y, featureCols
