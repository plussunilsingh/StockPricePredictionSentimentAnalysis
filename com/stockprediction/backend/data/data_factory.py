"""Thin factory wrappers to obtain data collectors used across the project.

This module adapts the older "DataCollector" terminology to the current
`DataScannerFactory` implementation in `data_strategy.py`. It provides a
simple enum-based API that calling code can use without coupling to the
underlying scanner implementation.
"""

from enum import Enum
from com.stockprediction.backend.data.data_strategy import DataScannerFactory


class DataType(Enum):
    STOCK = 1
    NEWS = 2
    CSV_STOCK = 3
    CSV_NEWS = 4


class DataCollectorFactory:
    """
    Factory to retrieve the appropriate data scanner instance.

    getCollector returns an object implementing the same `collectData`
    signature used across the backend. The optional `scannerType` argument
    can be used to prefer live vs mock implementations when relevant.
    """

    @staticmethod
    def getCollector(dataType: DataType, scannerType: str = "MOCK"):
        if dataType == DataType.STOCK:
            return DataScannerFactory.getStockScanner(scannerType)
        elif dataType == DataType.NEWS:
            return DataScannerFactory.getNewsScanner(scannerType)
        elif dataType == DataType.CSV_STOCK:
            # Explicitly return a mock CSV stock scanner
            return DataScannerFactory.getStockScanner("MOCK")
        elif dataType == DataType.CSV_NEWS:
            return DataScannerFactory.getNewsScanner("MOCK")
        else:
            raise ValueError(f"Unsupported DataType format: {dataType}")
