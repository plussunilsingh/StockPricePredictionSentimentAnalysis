import pandas as pd

class FeatureEngineer:
    """
    Generates technical and sentiment features for the model.
    """
    @staticmethod
    def addMovingAverage(data: pd.DataFrame, column: str, window: int) -> pd.DataFrame:
        data[f'MA_{window}'] = data[column].rolling(window=window).mean()
        return data

    @staticmethod
    def addRSI(data: pd.DataFrame, column: str, periods: int = 14) -> pd.DataFrame:
        delta = data[column].diff()
        gain = delta.where(delta > 0, 0.0).rolling(window=periods).mean()
        loss = -delta.where(delta < 0, 0.0).rolling(window=periods).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        return data
        
    @staticmethod
    def addEMA(data: pd.DataFrame, column: str, span: int) -> pd.DataFrame:
        data[f'EMA_{span}'] = data[column].ewm(span=span, adjust=False).mean()
        return data

    @staticmethod
    def addMACD(data: pd.DataFrame, column: str) -> pd.DataFrame:
        exp1 = data[column].ewm(span=12, adjust=False).mean()
        exp2 = data[column].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
        return data

    @staticmethod
    def addBollingerBands(data: pd.DataFrame, column: str, window: int = 20) -> pd.DataFrame:
        sma = data[column].rolling(window=window).mean()
        std = data[column].rolling(window=window).std()
        data['BB_Upper'] = sma + (std * 2)
        data['BB_Lower'] = sma - (std * 2)
        return data

    @staticmethod
    def mergeSentiment(stockData: pd.DataFrame, newsData: pd.DataFrame, sentimentAnalyzer) -> pd.DataFrame:
        """
        Analyzes news sentiment and merges it into the stock data based on date.
        """
        if not newsData.empty and 'Headline' in newsData.columns and 'Date' in newsData.columns:
            newsData['Sentiment_Score'] = newsData['Headline'].apply(lambda x: sentimentAnalyzer.analyzeText(str(x)))
            # Group by Date and average sentiment for the day
            dailySentiment = newsData.groupby('Date')['Sentiment_Score'].mean().reset_index()
            # Merge with stock data
            mergedData = pd.merge(stockData, dailySentiment, on='Date', how='left')
            # Fill NaN sentiment with 0 (Neutral)
            mergedData['Sentiment_Score'] = mergedData['Sentiment_Score'].fillna(0)
            return mergedData
        else:
            stockData['Sentiment_Score'] = 0.0
            return stockData
