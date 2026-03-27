from abc import ABC, abstractmethod
import pandas as pd
try:
    import yfinance as yf
except ImportError:
    yf = None
import os

class DataCollectionStrategy(ABC):
    """
    Abstract Base Class for Data Collection Strategies.
    """
    @abstractmethod
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        pass

class StockDataCollector(DataCollectionStrategy):
    """
    Concrete Strategy for collecting historical stock data via yfinance.
    """
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        print(f"Collecting stock data for {symbol} from {startDate} to {endDate}")
        stockData = yf.download(symbol, start=startDate, end=endDate)
        
        # Ensure we have date as a column if it's the index
        if isinstance(stockData.index, pd.DatetimeIndex):
            stockData.reset_index(inplace=True)
            if 'Date' in stockData.columns:
                stockData['Date'] = pd.to_datetime(stockData['Date'])
        return stockData

class CsvStockDataCollector(DataCollectionStrategy):
    """
    Concrete Strategy for collecting historical stock data via CSV files (Mock).
    """
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        filePath = f"data/{symbol}.csv"
        print(f"Collecting stock data for {symbol} from {filePath}")
        if not os.path.exists(filePath):
            print(f"File {filePath} not found. Returning empty DataFrame.")
            return pd.DataFrame()
        
        stockData = pd.read_csv(filePath)
        if 'Date' in stockData.columns:
            stockData['Date'] = pd.to_datetime(stockData['Date'])
            # Filter by date range if needed
            mask = (stockData['Date'] >= startDate) & (stockData['Date'] <= endDate)
            stockData = stockData.loc[mask]
        return stockData

class NewsDataCollector(DataCollectionStrategy):
    """
    Concrete Strategy for collecting News data.
    """
    def __init__(self, apiKey: str = ""):
        self.apiKey = apiKey

    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        print(f"Collecting news data for {symbol}")
        # Placeholder for actual news API call
        # Mock format: Date, Headline
        dummyData = {
            'Date': pd.date_range(start=startDate, end=endDate),
            'Headline': [f"Dummy news headline for {symbol} on day {i}" for i in range((pd.to_datetime(endDate) - pd.to_datetime(startDate)).days + 1)]
        }
        return pd.DataFrame(dummyData)

class CsvNewsDataCollector(DataCollectionStrategy):
    """
    Concrete Strategy for collecting News data via CSV files (Mock).
    """
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        filePath = f"data/{symbol}_news.csv"
        print(f"Collecting news data for {symbol} from {filePath}")
        if not os.path.exists(filePath):
            print(f"File {filePath} not found. Returning empty DataFrame.")
            return pd.DataFrame()
        
        newsData = pd.read_csv(filePath)
        if 'Date' in newsData.columns:
            newsData['Date'] = pd.to_datetime(newsData['Date'])
            # Filter by date range if needed
            mask = (newsData['Date'] >= startDate) & (newsData['Date'] <= endDate)
            newsData = newsData.loc[mask]
        return newsData
