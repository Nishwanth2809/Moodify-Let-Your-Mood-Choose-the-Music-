from flask import Blueprint, request, jsonify, render_template
from utils.mood_analysis import analyze_mood_with_audio
from utils.audio_features import extract_audio_features
from utils.spotify_helper import get_songs_by_mood_and_language
import base64
import io
from pydub import AudioSegment
import whisper
import os

main_bp = Blueprint("main", __name__)
whisper_model = whisper.load_model("tiny")

@main_bp.route("/")
def home():
    return render_template("front.html")

@main_bp.route("/text", methods=["POST"])
def text_input():
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "english").lower()
    mood = analyze_mood_with_audio(text)
    songs = get_songs_by_mood_and_language(mood, language)
    return jsonify({"text": text, "mood": mood, "songs": songs})

@main_bp.route("/voice", methods=["POST"])
def voice_input():
    data = request.get_json()
    audio_base64 = data.get("file")
    language = data.get("language", "english").lower()
    
    audio_data = base64.b64decode(audio_base64)
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
    file_path = "temp_audio.wav"
    audio.export(file_path, format="wav")

    tempo, pitch = extract_audio_features(file_path)
    text = whisper_model.transcribe(file_path)["text"]
    mood = analyze_mood_with_audio(text, tempo, pitch)
    songs = get_songs_by_mood_and_language(mood, language)

    if os.path.exists(file_path):
        os.remove(file_path)

    return jsonify({"text": text, "mood": mood, "songs": songs})
