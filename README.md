# Moodify

Moodify is an intelligent music curation app that detects a user's mood from typed text or a short voice note, provides empathetic emotional insights, and recommends Spotify tracks for English, Hindi, or Telugu listening.

## Highlights

- **AI-Powered Emotion Engine**: Integrates Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`) for deep, nuanced emotional reflection, empathetic feedback notes, and tailored musical vibe descriptions with seamless heuristic fallback.
- **Text & Voice Mood Detection**: Browser transcription with Web Audio analysis (tempo, pitch, energy) combined with NLTK VADER sentiment analysis and emotion keyword signals.
- **Emotional Breakdown & Metrics**: Confidence scores, multi-mood distribution meters (happy, sad, neutral, love, angry), sentiment metrics, and vocal audio features.
- **Adaptive Spotify Recommendations**: Spotify playlist recommendations with search fallbacks when credentials are unavailable.
- **Responsive Modern UI**: Sleek, accessible app-style interface for desktop and mobile.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5050`.

## Environment Configuration

Create a `.env` file in the root directory:

```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
FLASK_SECRET=your_flask_secret

# Optional: Google Gemini API Key for deep AI emotion analysis & empathy reflections
GEMINI_API_KEY=your_gemini_api_key
```

*Note: If `GEMINI_API_KEY` is omitted, Moodify automatically operates with its smart sentiment and linguistic emotion engine without interruption.*
