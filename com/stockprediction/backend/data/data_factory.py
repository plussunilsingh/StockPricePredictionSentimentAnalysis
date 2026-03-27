from enum import Enum
from .data_strategy import (
    DataCollectionStrategy, 
    StockDataCollector, 
    NewsDataCollector,
    CsvStockDataCollector,
    CsvNewsDataCollector
)

class DataType(Enum):
    STOCK = 1
    NEWS = 2
    CSV_STOCK = 3
    CSV_NEWS = 4

class DataCollectorFactory:
    """
    Factory to retrieve the appropriate DataCollectionStrategy.
    """
    @staticmethod
    def getCollector(dataType: DataType) -> DataCollectionStrategy:
        if dataType == DataType.STOCK:
            return StockDataCollector()
        elif dataType == DataType.NEWS:
            # using dummy key for now
            return NewsDataCollector(apiKey="dummy_key")
        elif dataType == DataType.CSV_STOCK:
            return CsvStockDataCollector()
        elif dataType == DataType.CSV_NEWS:
            return CsvNewsDataCollector()
        else:
            raise ValueError(f"Unsupported DataType format: {dataType}")
