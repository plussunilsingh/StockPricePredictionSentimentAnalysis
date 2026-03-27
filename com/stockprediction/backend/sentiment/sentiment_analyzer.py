from abc import ABC, abstractmethod

# NLTK imports required for VADER
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import os

class SentimentStrategy(ABC):
    @abstractmethod
    def analyzeText(self, text: str) -> float:
        pass

class VaderSentimentAnalyzer(SentimentStrategy):
    def __init__(self):
        # Set local nltk_data path
        local_nltk_data = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(local_nltk_data, exist_ok=True)
        if local_nltk_data not in nltk.data.path:
            nltk.data.path.append(local_nltk_data)
            
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            print(f"Downloading vader_lexicon to {local_nltk_data}...")
            nltk.download('vader_lexicon', download_dir=local_nltk_data)
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
