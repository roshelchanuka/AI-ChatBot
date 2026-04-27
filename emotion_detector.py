import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

class EmotionDetector:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def get_emotion(self, text):
        """
        Analyzes text sentiment and returns a tuple:
        (emoji, emotion_name, color_hex)
        """
        scores = self.sia.polarity_scores(text)
        compound = scores['compound']

        if compound >= 0.5:
            return "😊", "Happy", "#4CAF50"  # Green
        elif compound > 0.1:
            return "🙂", "Positive", "#8BC34A" # Light Green
        elif compound <= -0.5:
            return "😤", "Annoyed", "#F44336"  # Red
        elif compound < -0.1:
            return "😔", "Sad", "#2196F3"     # Blue
        else:
            # Check for surprise words
            surprise_words = ["wow", "incredible", "really", "omg", "what"]
            if any(word in text.lower() for word in surprise_words):
                return "😮", "Surprised", "#FFC107" # Amber
            return "😐", "Neutral", "#9E9E9E"   # Grey

# Singleton
detector = EmotionDetector()

def detect_emotion(text):
    return detector.get_emotion(text)
