import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
]

EMOTION_VIBES = {
    "happy": {
        "nuance": "Uplifting & Energized",
        "empathy": "Your energy is contagious! Enjoy this positive rhythm and keep radiating good vibes.",
        "vibe": "Upbeat tempos, lively rhythms, and feel-good melodies."
    },
    "sad": {
        "nuance": "Reflective & Tender",
        "empathy": "It's completely okay to feel down sometimes. Music can hold space for healing and peace.",
        "vibe": "Gentle acoustic strings, mellow melodies, and comforting vocals."
    },
    "angry": {
        "nuance": "Intense & Cathartic",
        "empathy": "Frustration is valid. Channel that powerful intensity into music that lets you vent and reset.",
        "vibe": "High-octane bass, driving beats, and expressive guitar riffs."
    },
    "love": {
        "nuance": "Warm & Affectionate",
        "empathy": "Love and warmth make everything brighter. Let these soulful tracks celebrate your heart.",
        "vibe": "Romantic ballads, smooth harmonies, and sweet melodies."
    },
    "neutral": {
        "nuance": "Calm & Centered",
        "empathy": "A balanced, peaceful state of mind. Perfect for staying focused, relaxed, and present.",
        "vibe": "Lo-Fi beats, chilled instrumental grooves, and ambient tunes."
    }
}


def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY", "").strip()


def query_gemini_emotion(text: str, language: str = "english", audio_features: dict = None) -> dict:
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    audio_context = ""
    if audio_features:
        tempo = audio_features.get("tempo", 0)
        pitch = audio_features.get("pitch", 0)
        energy = audio_features.get("energy", 0)
        audio_context = f"Detected vocal audio features: Tempo ~ {tempo:.1f} BPM, Average Pitch ~ {pitch:.1f} Hz, Vocal Energy ~ {energy:.2f}."

    prompt = f"""You are Moodify's empathetic AI Emotion & Music Intelligence Engine.
Analyze the following user statement and determine their emotional state and tailored musical vibe.

User text / speech transcript: "{text}"
Preferred music language: {language}
{audio_context}

Return a STRICT JSON response (no markdown fences, just pure JSON) with the following exact keys:
{{
  "primary_mood": "happy" | "sad" | "neutral" | "love" | "angry",
  "nuanced_emotion": "1-3 words describing exact emotional nuance (e.g. 'Bittersweet Nostalgia', 'Determined & Fierce', 'Euphoric Joy')",
  "empathy_note": "A compassionate, insightful 1-2 sentence reflection validating their feelings and explaining the emotional vibe",
  "music_vibe": "A brief description of the musical style and instruments that best match this moment",
  "confidence": float between 0.50 and 0.99,
  "scores": {{
    "happy": float 0.0-1.0,
    "sad": float 0.0-1.0,
    "neutral": float 0.0-1.0,
    "love": float 0.0-1.0,
    "angry": float 0.0-1.0
  }},
  "suggested_query": "3-5 search words for music recommendations in {language} for this mood"
}}
"""

    for model in GEMINI_API_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=7)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        raw_text = parts[0].get("text", "").strip()
                        # Clean markdown json fences if any
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        if raw_text.startswith("```"):
                            raw_text = raw_text[3:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]
                        parsed = json.loads(raw_text.strip())
                        if "primary_mood" in parsed:
                            parsed["provider"] = f"gemini ({model})"
                            return parsed
            else:
                print(f"[Moodify AI] Gemini model {model} returned status {response.status_code}: {response.text[:120]}")
        except Exception as e:
            print(f"[Moodify AI] Gemini request error with {model}: {e}")

    return None


def generate_heuristic_insight(text: str, mood: str, compound: float, matched_keywords: list = None) -> dict:
    """Fallback high-quality AI reflection synthesized from linguistic and sentiment signals."""
    base = EMOTION_VIBES.get(mood, EMOTION_VIBES["neutral"])

    nuance = base["nuance"]
    empathy = base["empathy"]
    vibe = base["vibe"]

    if mood == "sad" and compound < -0.6:
        nuance = "Deep Heartache & Longing"
        empathy = "You seem to be going through something heavy right now. Take a deep breath; gentle melodies are here to soothe you."
    elif mood == "happy" and compound > 0.6:
        nuance = "Pure Radiance & Joy"
        empathy = "Such vibrant positive momentum! Let these rhythmic beats amplify your celebration."
    elif mood == "angry" and compound < -0.5:
        nuance = "Intense Release & Power"
        empathy = "There's powerful tension in your words. Music with raw energy can help give voice to that fire and release it."
    elif mood == "love":
        nuance = "Deep Romantic Warmth"
        empathy = "Feelings of deep connection and fondness are shining through your words."
    elif mood == "neutral":
        if abs(compound) < 0.1:
            nuance = "Quiet Focus & Tranquility"
            empathy = "You're in a steady, tranquil headspace. Ambient sounds and chilled beats will keep your flow going."

    return {
        "provider": "smart_heuristic",
        "primary_mood": mood,
        "nuanced_emotion": nuance,
        "empathy_note": empathy,
        "music_vibe": vibe,
        "suggested_query": f"{mood} chilled {vibe.split(',')[0]}"
    }
