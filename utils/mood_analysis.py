import spacy
import nltk
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("punkt")
nltk.download("vader_lexicon")
nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()

def analyze_mood_with_audio(text, tempo=0, avg_pitch=0):
    sentiment = sia.polarity_scores(text)
    compound = sentiment["compound"]
    doc = nlp(text)
    if any(tok.dep_ == "neg" for tok in doc):
        compound *= -1

    norm_tempo = min(max((tempo - 40) / (200 - 40), 0), 1)
    norm_pitch = min(max((avg_pitch - 50) / (500 - 50), 0), 1)
    norm_sentiment = (compound + 1) / 2

    lower = text.lower()
    if "love" in lower:
        return "love"
    if any(w in lower for w in ["angry", "furious", "rage"]):
        return "angry"
    if any(w in lower for w in ["sad", "cry", "depressed"]):
        return "sad"

    score = 0.3 * norm_tempo + 0.3 * norm_pitch + 0.4 * norm_sentiment
    if compound <= -0.4:
        return "sad"
    if avg_pitch > 250 and tempo > 120:
        return "angry"
    if score >= 0.7:
        return "happy"
    elif score <= 0.3:
        return "sad"
    elif norm_pitch > 0.75 and compound < 0:
        return "angry"
    else:
        return "neutral"
