"""Sentiment analysis strategies used by the backend.

Currently supports a VADER-based analyzer. The module documents why we
use a local `nltk_data` directory (to avoid global state) and gracefully
falls back to a no-op analyzer if NLTK is not available.
"""

from abc import ABC, abstractmethod
import logging
import os

# NLTK imports required for VADER
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except ImportError:
    nltk = None
    SentimentIntensityAnalyzer = None

from com.stockprediction.config.AppConfig import config
logger = config.getLogger("Sentiment")


class SentimentStrategy(ABC):
    @abstractmethod
    def analyzeText(self, text: str) -> float:
        """Return a float sentiment score in [-1, 1]."""
        pass


class VaderSentimentAnalyzer(SentimentStrategy):
    def __init__(self):
        # If NLTK isn't installed, provide a no-op analyzer (neutral score)
        if nltk is None:
            self.analyzer = None
            logger.warning("NLTK not available: sentiment analysis disabled.")
            return

        # Use a project-local nltk_data directory to avoid requiring system-wide data
        local_nltk_data = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(local_nltk_data, exist_ok=True)
        if local_nltk_data not in nltk.data.path:
            nltk.data.path.append(local_nltk_data)

        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            logger.info(f"Downloading vader_lexicon to {local_nltk_data}...")
            try:
                # Note: network access may be blocked in some environments
                nltk.download('vader_lexicon', download_dir=local_nltk_data)
            except Exception as e:
                logger.error("Failed to download vader_lexicon: %s. Sentiment analysis disabled.", e)
                self.analyzer = None
                return

        self.analyzer = SentimentIntensityAnalyzer()

    def analyzeText(self, text: str) -> float:
        if self.analyzer is None:
            return 0.0
        scores = self.analyzer.polarity_scores(text)
        return scores.get('compound', 0.0)


class SentimentAnalyzerFactory:
    @staticmethod
    def getAnalyzer(analyzerType: str = "VADER") -> SentimentStrategy:
        if analyzerType.upper() == "VADER":
            return VaderSentimentAnalyzer()
        raise ValueError(f"Sentiment Analyzer {analyzerType} is not supported.")
