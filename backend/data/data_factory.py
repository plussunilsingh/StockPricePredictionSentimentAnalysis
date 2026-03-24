from enum import Enum
from .data_strategy import DataCollectionStrategy, StockDataCollector, NewsDataCollector

class DataType(Enum):
    STOCK = 1
    NEWS = 2

class DataCollectorFactory:
    \"\"\"
    Factory to retrieve the appropriate DataCollectionStrategy.
    \"\"\"
    @staticmethod
    def getCollector(dataType: DataType) -> DataCollectionStrategy:
        if dataType == DataType.STOCK:
            return StockDataCollector()
        elif dataType == DataType.NEWS:
            # using dummy key for now
            return NewsDataCollector(apiKey="dummy_key")
        else:
            raise ValueError(f"Unsupported DataType format: {dataType}")
