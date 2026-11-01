import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",
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
    load_dotenv(override=True)
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
        audio_context = f"Detected vocal audio features: Tempo ~ {tempo:.1f} BPM, Pitch ~ {pitch:.1f} Hz, Vocal Energy ~ {energy:.2f}."

    prompt = f"""You are Moodify's empathetic AI Emotion & Music Intelligence Engine.
Analyze the following user statement and determine their emotional state and tailored musical vibe.

User text / speech transcript: "{text}"
Preferred music language: {language}
{audio_context}

Return a STRICT JSON object (no markdown, no code fences, only valid JSON) with these exact keys:
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

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        for model in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                raw_text = (response.text or "").strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]

                parsed = json.loads(raw_text.strip())
                if "primary_mood" in parsed:
                    parsed["provider"] = f"Google Gemini ({model})"
                    return parsed
            except Exception as model_err:
                print(f"[Moodify AI] Gemini model {model} attempt error: {model_err}")
                continue

    except Exception as e:
        print(f"[Moodify AI] Gemini client error: {e}")

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
