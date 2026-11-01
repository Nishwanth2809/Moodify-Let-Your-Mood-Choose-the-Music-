from flask import Blueprint, request, jsonify, render_template

from utils.mood_analysis import analyze_mood_details
from utils.spotify_recommender import get_recommendation_result, get_spotify_access_token, fetch_playlist_tracks, MOOD_PLAYLISTS
from utils.ai_engine import get_gemini_api_key

main_bp = Blueprint("main_bp", __name__)
MAX_TEXT_LENGTH = 500

@main_bp.route("/")
def home():
    return render_template("front.html")


# --------------------------
#   AI STATUS ROUTE
# --------------------------
@main_bp.route("/api/ai-status")
def ai_status():
    has_key = bool(get_gemini_api_key())
    return jsonify({
        "gemini_configured": has_key,
        "engine": "Google Gemini 2.5 Flash" if has_key else "Smart Sentiment & Heuristic Engine"
    })


# --------------------------
#   TEXT INPUT ROUTE
# --------------------------
@main_bp.route("/text", methods=["POST"])
def analyze_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    language = data.get("language", "telugu")

    if not text:
        return jsonify({"error": "No text provided"}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"Text must be {MAX_TEXT_LENGTH} characters or fewer"}), 400

    analysis = analyze_mood_details(text, language=language)
    recommendation = get_recommendation_result(
        analysis["mood"],
        language,
        limit=3
    )

    return jsonify({
        "analysis": analysis,
        "mood": analysis["mood"],
        "recommendation": recommendation,
        "songs": recommendation["songs"]
    })


# --------------------------
#   VOICE INPUT ROUTE
# --------------------------
@main_bp.route("/voice", methods=["POST"])
def analyze_voice():
    data = request.get_json(silent=True) or {}

    # Text and lightweight voice features are produced in the browser.
    text = data.get("text", "").strip()
    language = data.get("language", "telugu")
    features = data.get("features") or {}

    try:
        tempo = float(features.get("tempo", 0) or 0)
        pitch = float(features.get("pitch", 0) or 0)
        energy = float(features.get("energy", 0) or 0)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid audio features"}), 400

    if not text:
        return jsonify({"error": "No transcript provided"}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"Transcript must be {MAX_TEXT_LENGTH} characters or fewer"}), 400

    try:
        analysis = analyze_mood_details(text, tempo, pitch, language=language)
        analysis["audio"]["browser_energy"] = round(max(0, min(energy, 1)), 2)
        recommendation = get_recommendation_result(
            analysis["mood"],
            language,
            limit=3
        )

        return jsonify({
            "text": text,
            "mood": analysis["mood"],
            "analysis": analysis,
            "tempo": tempo,
            "pitch": pitch,
            "recommendation": recommendation,
            "songs": recommendation["songs"]
        })

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


# --------------------------
#   DEBUG ROUTE
# --------------------------
@main_bp.route("/debug/spotify")
def debug_spotify():
    """Quick health-check: test token + fetch a few tracks from one playlist."""
    try:
        token = get_spotify_access_token()
        if not token:
            return jsonify({"ok": False, "error": "No Spotify token — credentials missing or invalid"}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": f"Token error: {e}"}), 500

    results = {}
    # Test one playlist per mood for the default language (telugu)
    for mood, langs in MOOD_PLAYLISTS.items():
        pid = langs.get("telugu") or langs.get("english")
        songs, error = fetch_playlist_tracks(pid, mood, "telugu")
        results[mood] = {
            "playlist_id": pid,
            "tracks_fetched": len(songs),
            "error": error,
            "sample": songs[:2] if songs else []
        }

    return jsonify({"ok": True, "token_ok": True, "playlists": results})
