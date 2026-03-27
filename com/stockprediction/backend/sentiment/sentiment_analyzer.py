from abc import ABC, abstractmethod

# NLTK imports required for VADER
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except ImportError:
    nltk = None
    SentimentIntensityAnalyzer = None

import os

class SentimentStrategy(ABC):
    @abstractmethod
    def analyzeText(self, text: str) -> float:
        pass

class VaderSentimentAnalyzer(SentimentStrategy):
    def __init__(self):
        if nltk is None:
            self.analyzer = None
            print("NLTK not found. Sentiment analysis will be disabled.")
            return

        # Set local nltk_data path
        local_nltk_data = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(local_nltk_data, exist_ok=True)
        if local_nltk_data not in nltk.data.path:
            nltk.data.path.append(local_nltk_data)
            
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            print(f"Downloading vader_lexicon to {local_nltk_data}...")
            try:
                nltk.download('vader_lexicon', download_dir=local_nltk_data)
            except Exception as e:
                print(f"Failed to download vader_lexicon: {e}. Sentiment analysis disabled.")
                self.analyzer = None
                return
        self.analyzer = SentimentIntensityAnalyzer()

    def analyzeText(self, text: str) -> float:
        if self.analyzer is None:
            return 0.0
        # returns compound score [-1, 1]
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']

class SentimentAnalyzerFactory:
    @staticmethod
    def getAnalyzer(analyzerType: str = "VADER") -> SentimentStrategy:
        if analyzerType.upper() == "VADER":
            return VaderSentimentAnalyzer()
        raise ValueError(f"Sentiment Analyzer {analyzerType} is not supported.")
