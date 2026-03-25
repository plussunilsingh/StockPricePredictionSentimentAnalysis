import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class DataPreprocessor:
    """
    Preprocesses data before feeding to the model.
    """
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def cleanData(self, data: pd.DataFrame) -> pd.DataFrame:
        # Handle missing values by dropping them for simplicity
        cleanDf = data.dropna().copy()
        return cleanDf

    def normalize(self, data: pd.DataFrame, columns: list) -> pd.DataFrame:
        # Scale specific columns
        if not data.empty:
            data.loc[:, columns] = self.scaler.fit_transform(data[columns])
        return data

    def inverseTransform(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(self.scaler.inverse_transform(data))
