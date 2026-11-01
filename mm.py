from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
from nltk.sentiment import SentimentIntensityAnalyzer
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

app = Flask(__name__, template_folder="templates")
sia = SentimentIntensityAnalyzer()

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("❌ Missing Spotify API credentials! Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Sentiment Analysis
def analyze_mood(text):
    text = text.lower()
    sentiment = sia.polarity_scores(text)

    love_keywords = ["love", "romantic", "passion", "heart", "valentine", "affection", "crush"]
    angry_keywords = ["angry", "mad", "furious", "rage", "annoyed", "irritated", "hate", "frustrated"]

    if any(word in text for word in love_keywords):
        return "love"
    elif any(word in text for word in angry_keywords) or sentiment['compound'] <= -0.5:
        return "angry"
    elif sentiment['compound'] >= 0.3:
        return "happy"
    elif sentiment['compound'] <= -0.2:
        return "sad"
    else:
        return "neutral"

# Fetch Songs by Mood
def get_songs_by_mood(mood):
    mood_playlist = {
        "happy": "5yFLeTOySZFQ9K1kFfmE6x",
        "sad": "2BCsnZdPuiPV19hNulkQgT",
        "neutral": "1YTrQChc67rZoNfG1YoTch",
        "love": "37i9dQZF1DXc3K4WsyHQwu",
        "angry": "37i9dQZF1DWYI3iCKn6UM3"
    }
    
    playlist_id = mood_playlist.get(mood, mood_playlist["neutral"])
    
    try:
        results = sp.playlist_items(playlist_id)
        songs = []
        for item in results.get("items", []):
            track = item.get("track")
            if not track:
                continue
            
            song_name = track.get("name", "Unknown Song")
            artist_list = track.get("artists", [])
            artist_name = artist_list[0].get("name", "Unknown Artist") if artist_list else "Unknown Artist"
            
            album_images = track.get("album", {}).get("images", [])
            album_cover = album_images[0]["url"] if album_images else None

            songs.append({
                "name": song_name,
                "artist": artist_name,
                "cover": album_cover
            })

        return songs[:3] if len(songs) >= 3 else songs
    except Exception as e:
        return [{"error": f"Failed to fetch songs: {str(e)}"}]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Input text is empty."}), 400

        mood = analyze_mood(text)
        songs = get_songs_by_mood(mood)

        return jsonify({
            "mood": mood,
            "songs": songs
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/voice", methods=["POST"])
def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust sensitivity
        audio = recognizer.listen(source)

    print("🔍 Processing voice...")
    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ Recognized: {text}")

        mood = analyze_mood(text)
        songs = get_songs_by_mood(mood)

        return jsonify({
            "text": text,
            "mood": mood,
            "songs": songs
        })
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service unavailable"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True, use_reloader=False)
