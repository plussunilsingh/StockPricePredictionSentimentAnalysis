import json
import os
import logging

class AppConfig:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._loadConfig()
            cls._instance._setupLogging()
        return cls._instance

    def _loadConfig(self):
        configPath = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(configPath):
            with open(configPath, "r") as f:
                self._config = json.load(f)
        else:
            print(f"Warning: Configuration file not found at {configPath}")

    def _setupLogging(self):
        logFile = self.get("system", "logFile", default="backend.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logFile),
                logging.StreamHandler()
            ]
        )

    def get(self, *keys, default=None):
        val = self._config
        try:
            for key in keys:
                val = val[key]
            return val
        except (KeyError, TypeError):
            return default

    @staticmethod
    def getLogger(name):
        return logging.getLogger(name)

# Global configuration instance
config = AppConfig()
