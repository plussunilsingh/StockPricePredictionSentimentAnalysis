"""Data access strategies for stock and news data used across the backend.

This module exposes scanners for mock CSV data (`CsvStockScanner`,
`CsvNewsScanner`) and a `LiveStockScanner` that prefers `yfinance` but
falls back to a direct Yahoo API request or a synthetic mock-up when
required. The DataScannerFactory returns scanner instances for callers.
"""

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
        """Collect data between two date strings (YYYY-MM-DD)."""
        pass


class CsvStockScanner(DataScanner):
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        filePath = os.path.join(config.get("data", "mockDir"), f"{symbol}.csv")
        logger.info(f"Scanning mock stock data for {symbol} at {filePath}")
        if os.path.exists(filePath):
            df = pd.read_csv(filePath)
            # Ensure Date column is datetime for consistent filtering
            df['Date'] = pd.to_datetime(df['Date'])
            mask = (df['Date'] >= startDate) & (df['Date'] <= endDate)
            return df.loc[mask]
        logger.warning(f"Mock stock data file not found: {filePath}")
        return pd.DataFrame()


class LiveStockScanner(DataScanner):
    def collectData(self, symbol: str, startDate: str, endDate: str) -> pd.DataFrame:
        logger.info(f"Scanning live stock data for {symbol} from {startDate} to {endDate}")
        yfSymbol = symbol
        if symbol == "NSEI": yfSymbol = "^NSEI"
        if symbol == "BSESN": yfSymbol = "^BSESN"

        # Primary: use yfinance library if available
        if yf is not None:
            try:
                df = yf.download(yfSymbol, start=startDate, end=endDate)
                if not df.empty:
                    df = df.reset_index()
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                    return df
            except Exception as e:
                logger.error(f"Error fetching live stock data via yfinance: {e}")

        # Secondary: Yahoo chart API fallback using requests
        logger.info(f"Using requests API fallback for live data: {yfSymbol}")
        import requests
        import time
        from datetime import datetime
        import pandas as pd
        import os
        from com.stockprediction.config.AppConfig import config

        try:
            period1 = int(time.mktime(datetime.strptime(startDate, '%Y-%m-%d').timetuple()))
            period2 = int(time.mktime(datetime.strptime(endDate, '%Y-%m-%d').timetuple()))
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{yfSymbol}?period1={period1}&period2={period2}&interval=1d"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                result = data.get('chart', {}).get('result', [])
                if result:
                    timestamps = result[0].get('timestamp', [])
                    indicators = result[0].get('indicators', {}).get('quote', [{}])[0]
                    if timestamps and indicators:
                        df = pd.DataFrame({
                            'Date': pd.to_datetime(timestamps, unit='s'),
                            'Open': indicators.get('open', []),
                            'High': indicators.get('high', []),
                            'Low': indicators.get('low', []),
                            'Close': indicators.get('close', []),
                            'Volume': indicators.get('volume', [])
                        })
                        return df.dropna()
            else:
                logger.warning(f"Yahoo API Fallback returned status {resp.status_code}. Using Synthetic Live Fallback.")
        except Exception as e:
            logger.warning(f"Error in requests API fallback: {e}. Using Synthetic Live Fallback.")

        # Ultimate Synthetic Live Fallback (upsamples mock data to current date to ensure demo uptime)
        try:
            mockDir = config.get("data", "mockDir")
            filepath = os.path.join(mockDir, f"{symbol}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['Date'] = pd.to_datetime(df['Date'])
                date_diff = pd.to_datetime(endDate) - df['Date'].max()
                df['Date'] = df['Date'] + date_diff
                logger.info(f"Synthesized live data for {symbol} up to {endDate}")
                return df.tail(100)  # Return last 100 days
        except Exception as e:
            logger.error(f"Error during synthetic live fallback for {symbol}: {e}")

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
