import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

_sia = None
_models_loaded = False

MOODS = ("happy", "sad", "neutral", "love", "angry")

KEYWORD_RULES = {
    "love": {
        "love", "romantic", "romance", "crush", "affection", "heart", "miss you",
        "pyaar", "pyar", "ishq", "premam"
    },
    "angry": {
        "angry", "mad", "furious", "rage", "annoyed", "irritated", "hate",
        "frustrated", "fight", "revenge"
    },
    "sad": {
        "sad", "cry", "tears", "tear", "depressed", "lonely", "heartbroken",
        "broken", "hurt", "down", "upset"
    },
    "happy": {
        "happy", "joy", "great", "excited", "smile", "party", "celebrate",
        "awesome", "amazing", "good"
    }
}


def _load_models():
    global _sia, _models_loaded
    if _models_loaded:
        return

    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        print("Warning: NLTK vader_lexicon is not installed. Falling back to keyword and audio signals.")
        _sia = None
        _models_loaded = True
        return

    try:
        _sia = SentimentIntensityAnalyzer()
    except Exception as exc:
        print(f"Warning: Could not load NLP models: {exc}")
        _sia = None
    finally:
        _models_loaded = True


def get_sia():
    _load_models()
    return _sia


def analyze_mood_with_audio(text, tempo=0, avg_pitch=0):
    return analyze_mood_details(text, tempo, avg_pitch)["mood"]


def analyze_mood_details(text, tempo=0, avg_pitch=0):
    text = (text or "").strip()

    try:
        sia = get_sia()
        sentiment = sia.polarity_scores(text) if sia and text else {
            "compound": 0,
            "pos": 0,
            "neu": 1,
            "neg": 0
        }
        compound = sentiment["compound"]
    except Exception:
        sentiment = {"compound": 0, "pos": 0, "neu": 1, "neg": 0}
        compound = 0

    tempo = float(tempo or 0)
    avg_pitch = float(avg_pitch or 0)
    norm_tempo = min(max((tempo - 40) / 160, 0), 1)
    norm_pitch = min(max((avg_pitch - 50) / 450, 0), 1)

    lower = text.lower()
    matched = {
        mood: sorted(keyword for keyword in keywords if keyword in lower)
        for mood, keywords in KEYWORD_RULES.items()
    }
    matched = {mood: words for mood, words in matched.items() if words}

    scores = {
        "happy": 0.30 + max(compound, 0) * 0.55 + norm_tempo * 0.25 + norm_pitch * 0.10,
        "sad": 0.25 + max(-compound, 0) * 0.65 + (1 - norm_tempo) * 0.25 + (1 - norm_pitch) * 0.10,
        "neutral": 0.55 - abs(compound) * 0.35 - abs(norm_tempo - 0.45) * 0.10,
        "love": 0.20 + max(compound, 0) * 0.35 + norm_pitch * 0.10,
        "angry": 0.15 + max(-compound, 0) * 0.25 + norm_tempo * 0.35 + norm_pitch * 0.35,
    }

    for mood, words in matched.items():
        scores[mood] += min(0.55, 0.25 + len(words) * 0.10)

    if avg_pitch > 250 and tempo > 120:
        scores["angry"] += 0.25

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    mood = ranked[0][0]
    top_score = ranked[0][1]
    second_score = ranked[1][1]
    confidence = min(max(0.45 + (top_score - second_score) * 0.55, 0.45), 0.96)

    signals = []
    for matched_mood, words in matched.items():
        signals.append(f"{matched_mood} keywords: {', '.join(words[:3])}")

    if compound >= 0.35:
        signals.append("positive language")
    elif compound <= -0.35:
        signals.append("negative language")
    else:
        signals.append("balanced sentiment")

    if tempo:
        signals.append("high vocal energy" if norm_tempo >= 0.55 else "calm vocal tempo")
    if avg_pitch:
        signals.append("intense pitch" if norm_pitch >= 0.55 else "steady pitch")

    return {
        "mood": mood,
        "confidence": round(confidence, 2),
        "scores": {name: round(min(max(value, 0), 1), 2) for name, value in scores.items()},
        "sentiment": {
            "compound": round(compound, 3),
            "positive": round(sentiment.get("pos", 0), 3),
            "neutral": round(sentiment.get("neu", 0), 3),
            "negative": round(sentiment.get("neg", 0), 3)
        },
        "audio": {
            "tempo": round(tempo, 2),
            "pitch": round(avg_pitch, 2),
            "energy": round(norm_tempo, 2),
            "intensity": round(norm_pitch, 2)
        },
        "signals": signals[:5]
    }
