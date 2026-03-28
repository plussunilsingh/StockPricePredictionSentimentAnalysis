"""Data preprocessing utilities: cleaning and scaling helpers.

This module intentionally keeps preprocessing simple (drop NaNs,
min-max scaling) to make the pipeline auditable and deterministic.
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class DataPreprocessor:
    """
    Preprocesses data before feeding to the model.
    """
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def cleanData(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned DataFrame (currently drops NA rows)."""
        if data is None:
            return pd.DataFrame()
        cleanDf = data.dropna().copy()
        return cleanDf

    def normalize(self, data: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Scale the specified columns in-place using MinMaxScaler.

        This operation mutates a copy of the input DataFrame and returns it.
        """
        if data is None or data.empty:
            return data
        # Ensure columns exist
        cols = [c for c in columns if c in data.columns]
        if not cols:
            return data
        data = data.copy()
        data.loc[:, cols] = self.scaler.fit_transform(data[cols])
        return data

    def inverseTransform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform a scaled array back to original range.

        Caller is expected to pass only the scaled numeric array (2D) here.
        """
        if data is None or data.empty:
            return pd.DataFrame()
        return pd.DataFrame(self.scaler.inverse_transform(data))
