import pandas as pd
import os
from abc import ABC, abstractmethod
from typing import Optional
from com.stockprediction.config.AppConfig import config

logger = config.getLogger("DataStrategy")

try:
    import yfinance as yf
except ImportError:
    yf = None

class DataScanner(ABC):
    @abstractmethod
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        pass

class CsvStockScanner(DataScanner):
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        filePath = os.path.join(config.get("data", "mockDir"), f"{symbol}.csv")
        logger.info(f"Scanning mock stock data for {symbol} at {filePath}")
        if os.path.exists(filePath):
            df = pd.read_csv(filePath)
            df['Date'] = pd.to_datetime(df['Date'])
            mask = (df['Date'] >= startDate) & (df['Date'] <= endDate)
            return df.loc[mask]
        logger.warning(f"Mock stock data file not found: {filePath}")
        return pd.DataFrame()

class LiveStockScanner(DataScanner):
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        logger.info(f"Scanning live stock data for {symbol} from {startDate} to {endDate}")
        if yf is None:
            logger.error("yfinance not installed. Cannot fetch live data.")
            return pd.DataFrame()
        
        try:
            yfSymbol = symbol
            if symbol == "NSEI": yfSymbol = "^NSEI"
            if symbol == "BSESN": yfSymbol = "^BSESN"
            
            df = yf.download(yfSymbol, start=startDate, end=endDate)
            if not df.empty:
                df = df.reset_index()
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                return df
        except Exception as e:
            logger.error(f"Error fetching live stock data: {e}")
        return pd.DataFrame()

class CsvNewsScanner(DataScanner):
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        filePath = os.path.join(config.get("data", "mockDir"), f"{symbol}_news.csv")
        logger.info(f"Scanning mock news data for {symbol} at {filePath}")
        if os.path.exists(filePath):
            df = pd.read_csv(filePath)
            df['Date'] = pd.to_datetime(df['Date'])
            mask = (df['Date'] >= startDate) & (df['Date'] <= endDate)
            return df.loc[mask]
        logger.warning(f"Mock news data file not found: {filePath}")
        return pd.DataFrame()

class DataScannerFactory:
    @staticmethod
    def getStockScanner(scannerType: str = "MOCK") -> DataScanner:
        if scannerType == "LIVE":
            return LiveStockScanner()
        return CsvStockScanner()

    @staticmethod
    def getNewsScanner(scannerType: str = "MOCK") -> DataScanner:
        # Currently only Mock News is supported; Live News would integrate Twitter/NewsAPI
        return CsvNewsScanner()
