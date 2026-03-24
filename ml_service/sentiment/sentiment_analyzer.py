from abc import ABC, abstractmethod

# NLTK imports required for VADER
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class SentimentStrategy(ABC):
    @abstractmethod
    def analyzeText(self, text: str) -> float:
        pass

class VaderSentimentAnalyzer(SentimentStrategy):
    def __init__(self):
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()

    def analyzeText(self, text: str) -> float:
        # returns compound score [-1, 1]
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']

class SentimentAnalyzerFactory:
    @staticmethod
    def getAnalyzer(analyzerType: str = "VADER") -> SentimentStrategy:
        if analyzerType.upper() == "VADER":
            return VaderSentimentAnalyzer()
        raise ValueError(f"Sentiment Analyzer {analyzerType} is not supported.")
