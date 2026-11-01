# Moodify — Let Your Mood Choose the Music 🎵

[![Live Demo](https://img.shields.io/badge/Demo-Live%20on%20Render-brightgreen?style=flat-square)](https://moodify-8g0x.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=flat-square&logo=google)](https://ai.google.dev/)
[![Spotify](https://img.shields.io/badge/Music-Spotify%20API-1DB954?style=flat-square&logo=spotify)](https://developer.spotify.com/)

> **Live Deployment:** [https://moodify-8g0x.onrender.com/](https://moodify-8g0x.onrender.com/)

Moodify is an intelligent, multi-modal music curation web application. It detects emotional states from typed thoughts or spoken voice notes using **Google Gemini** and browser **Web Audio analysis**, delivers empathetic AI reflections, and recommends curated Spotify tracks tailored for English, Hindi, and Telugu listeners.

---

## ✨ Features

- **🤖 Google Gemini AI Emotion Engine**: Integrates Google Gemini (`gemini-3.5-flash-lite` / `gemini-3.8-flash`) for deep, nuanced emotional reflection, empathetic feedback notes, and tailored musical vibe descriptions.
- **🎙️ Multimodal Voice & Audio Intelligence**:
  - In-browser microphone recording with real-time Web Audio API signal processing (tempo, pitch, and vocal energy estimation).
  - Independent **Spoken Language** selection (`English`, `Telugu`, `Hindi`) decoupled from the song recommendation language.
- **📊 Emotion Breakdown & Metrics**:
  - Real-time confidence score and 5-dimensional mood distribution meters (*Happy*, *Sad*, *Neutral*, *Love*, *Angry*).
  - Sentiment compound ratings and vocal audio diagnostics.
- **🎶 Adaptive Spotify Recommendations**:
  - Connects directly to the Spotify Web API.
  - Automatic fallback to iTunes Search API metadata and artwork when Spotify credentials are unavailable or rate-limited.
- **📱 Responsive Modern Interface**:
  - Interactive mood orb, dynamic gradient palettes, audio feedback preview, and glassmorphic aesthetic.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3.11, Flask, Flask-Session, Gunicorn
- **AI & NLP**: Google GenAI SDK (`google-genai`), NLTK (VADER Sentiment Intensity Analyzer)
- **Audio Processing**: Web Audio API (real-time channel decoders, autocorrelation pitch detection, RMS energy)
- **External APIs**: Spotify Web API, iTunes Search API, Google Generative Language API
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3 Glassmorphism

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Nishwanth2809/Moodify-Let-Your-Mood-Choose-the-Music-.git
cd moodify
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root directory:

```env
# Spotify Developer API (https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Flask Secret Key
FLASK_SECRET=your_random_flask_secret_key

# Optional: Google Gemini API Key (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key
```

> **Note**: If `GEMINI_API_KEY` is not provided, Moodify automatically operates with its built-in linguistic heuristic engine without interruption.

### 4. Run the Application
```bash
python app.py
```
Open **[http://localhost:5050](http://localhost:5050)** in your browser.

---

## 💡 Browser Tips for Voice Input

- **Chrome / Edge**: Recommended for native Web Speech API support. Allow microphone access when prompted.
- **Brave Browser**: Brave's privacy shields block Google speech-to-text servers by default. To enable:
  1. Go to `brave://settings/privacy`
  2. Search for `speech`
  3. Turn ON **"Use Google services for push messaging and speech recognition"**
  4. Ensure `http://localhost:5050` is allowed under `brave://settings/content/speechRecognition`
- *Alternatively, type your thoughts into the **Mood Input** text box and click **Analyze**.*

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
