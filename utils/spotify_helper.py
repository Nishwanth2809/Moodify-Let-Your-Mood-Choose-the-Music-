import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import random

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

mood_playlists = {
    "happy": {"english": "4Ml5FIY5qJ1qoSzjpgszx5", "hindi": "3D6sC3UYQUvTDuRE5hCqY4", "telugu": "293UF8TMOQFFtNwhctlKwU"},
    "sad": {"english": "0wZ03RU2rEOQ62qPpRghKV", "hindi": "7taJQO4qe6RlPAGimE9qRC", "telugu": "2BCsnZdPuiPV19hNulkQgT"},
    "neutral": {"english": "1YTrQChc67rZoNfG1YoTch", "hindi": "1YTrQChc67rZoNfG1YoTch", "telugu": "1YTrQChc67rZoNfG1YoTch"},
    "love": {"english": "46FwKzf5zAc7LnWJ8Gb0Ua", "hindi": "00tMG0oI6eqLUP0MsUxz12", "telugu": "5yFLeTOySZFQ9K1kFfmE6x"},
    "angry": {"english": "5I57hzwg68PIr0Xu0nX0pE", "hindi": "62QYDyNWB18qN0IjG6PVH8", "telugu": "6IY6M71r9yLzsOslKD7BzH"}
}

def get_songs_by_mood_and_language(mood, language="english"):
    playlist_id = mood_playlists.get(mood, {}).get(language)
    if not playlist_id:
        return []

    try:
        results = sp.playlist_items(playlist_id)
        songs = [{
            "name": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"],
            "cover": item["track"]["album"]["images"][0]["url"],
            "spotify_uri": item["track"]["uri"],
            "spotify_url": item["track"]["external_urls"]["spotify"]
        } for item in results["items"] if "track" in item]
        return random.sample(songs, min(3, len(songs))) if songs else []
    except:
        return []
