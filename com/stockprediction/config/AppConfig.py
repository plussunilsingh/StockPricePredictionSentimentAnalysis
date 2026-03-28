import json
import os
import logging

"""Application configuration and logging helper.

This module exposes a simple singleton AppConfig instance that loads a
project-level JSON configuration (if present) and sets up a basic logging
configuration. The API intentionally remains small: use `config.get(...)`
for nested config keys and `config.getLogger(name)` to obtain a logger.
"""

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
        # Look for a config.json next to this file. Non-fatal if not present.
        configPath = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(configPath):
            try:
                with open(configPath, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except Exception as e:
                # Keep default empty config but surface the problem via logging
                logging.warning("Failed to parse config.json (%s): %s", configPath, e)
        else:
            logging.warning("Configuration file not found at %s", configPath)

    def _setupLogging(self):
        # Allow config to override where logs are written. Default to a local
        # `logs` directory so logs are visible in the repo while developing.
        default_log_dir = os.path.join(os.path.dirname(__file__), os.pardir, "..", "logs")
        default_log_dir = os.path.abspath(default_log_dir)
        try:
            os.makedirs(default_log_dir, exist_ok=True)
        except Exception:
            # If directory creation fails, fall back to current working dir
            default_log_dir = os.getcwd()

        logFile = self.get("system", "logFile", default=os.path.join(default_log_dir, "backend.log"))

        # Basic logging configuration suitable for a small project. Keep it
        # simple and human-friendly so maintainers can quickly read files.
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logFile),
                logging.StreamHandler()
            ]
        )

    def get(self, *keys, default=None):
        """Retrieve a nested configuration value.

        Usage:
            config.get('section', 'subsection', default=123)

        If any key in the chain is missing, `default` is returned.
        """
        val = self._config
        try:
            for key in keys:
                val = val[key]
            return val
        except (KeyError, TypeError):
            return default

    @staticmethod
    def getLogger(name):
        """Convenience wrapper around logging.getLogger to keep call sites concise."""
        return logging.getLogger(name)


# Global configuration instance used throughout the project
config = AppConfig()
