import os
import random
import time
from urllib.parse import quote_plus

from dotenv import load_dotenv
import requests

load_dotenv()

_access_token = None
_token_expires_at = 0
_missing_credentials_warned = False


def get_spotify_access_token():
    global _access_token, _token_expires_at, _missing_credentials_warned

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        if not _missing_credentials_warned:
            print("Spotify credentials are missing. Song recommendations will be empty.")
            _missing_credentials_warned = True
        return None

    if _access_token and time.time() < _token_expires_at - 60:
        return _access_token

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=12
    )

    if response.status_code != 200:
        raise RuntimeError(format_spotify_error(response))

    token_data = response.json()
    _access_token = token_data["access_token"]
    _token_expires_at = time.time() + token_data.get("expires_in", 3600)
    return _access_token


def format_spotify_error(response):
    try:
        data = response.json()
    except ValueError:
        data = {}

    error = data.get("error")
    if isinstance(error, dict):
        message = error.get("message") or response.text
    elif isinstance(error, str):
        message = data.get("error_description") or error
    else:
        message = response.text

    return f"Spotify Web API {response.status_code}: {message}"

# ----------------------------------------
#  MOOD TO PLAYLIST MAPPING
# ----------------------------------------
MOOD_PLAYLISTS = {
    "happy": {
        "english": "4Ml5FIY5qJ1qoSzjpgszx5",
        "hindi": "3D6sC3UYQUvTDuRE5hCqY4",
        "telugu": "293UF8TMOQFFtNwhctlKwU"
    },
    "sad": {
        "english": "0wZ03RU2rEOQ62qPpRghKV",
        "hindi": "7taJQO4qe6RlPAGimE9qRC",
        "telugu": "2BCsnZdPuiPV19hNulkQgT"
    },
    "neutral": {
        "english": "1YTrQChc67rZoNfG1YoTch",
        "hindi": "1YTrQChc67rZoNfG1YoTch",
        "telugu": "1YTrQChc67rZoNfG1YoTch"
    },
    "love": {
        "english": "46FwKzf5zAc7LnWJ8Gb0Ua",
        "hindi": "00tMG0oI6eqLUP0MsUxz12",
        "telugu": "5yFLeTOySZFQ9K1kFfmE6x"
    },
    "angry": {
        "english": "5I57hzwg68PIr0Xu0nX0pE",
        "hindi": "62QYDyNWB18qN0IjG6PVH8",
        "telugu": "6IY6M71r9yLzsOslKD7BzH"
    }
}

TELUGU_FALLBACK_TRACKS = {
    "happy": [
        ("Butta Bomma", "Armaan Malik", "Ala Vaikunthapurramuloo"),
        ("Naatu Naatu", "Rahul Sipligunj, Kaala Bhairava", "RRR"),
        ("Samajavaragamana", "Sid Sriram", "Ala Vaikunthapurramuloo"),
        ("Choosi Chudangane", "Anurag Kulkarni, Mahati Swara Sagar", "Chalo"),
        ("Ramuloo Ramulaa", "Anurag Kulkarni, Mangli", "Ala Vaikunthapurramuloo")
    ],
    "sad": [
        ("Adiga Adiga", "Sid Sriram", "Ninnu Kori"),
        ("Priyathama Priyathama", "Chinmayi", "Majili"),
        ("Kanulanu Thaake", "Arijit Singh", "Manam"),
        ("Oosupodu", "Hemachandra", "Fidaa"),
        ("Yenti Yenti", "Chinmayi", "Geetha Govindam")
    ],
    "neutral": [
        ("Inkem Inkem Inkem Kaavaale", "Sid Sriram", "Geetha Govindam"),
        ("Vachindamma", "Sid Sriram", "Geetha Govindam"),
        ("Undiporaadhey", "Sid Sriram", "Hushaaru"),
        ("Nee Kannu Neeli Samudram", "Javed Ali", "Uppena"),
        ("Mellaga Tellarindoi", "Anurag Kulkarni, Ramya Behara", "Shatamanam Bhavati")
    ],
    "love": [
        ("Inkem Inkem Inkem Kaavaale", "Sid Sriram", "Geetha Govindam"),
        ("Vellipomaakey", "Sid Sriram", "Sahasam Swasaga Sagipo"),
        ("Undiporaadhey", "Sid Sriram", "Hushaaru"),
        ("Em Sandeham Ledu", "Kalyani Koduri, Sunitha", "Oohalu Gusagusalade"),
        ("Nuvvunte Naa Jathaga", "Sid Sriram, Isshrathquadhre", "I")
    ],
    "angry": [
        ("Dimaak Kharaab", "Keerthana Sharma, Saketh", "iSmart Shankar"),
        ("Blockbuster", "Shreya Ghoshal, Nakash Aziz, Simha", "Sarrainodu"),
        ("Top Lesi Poddi", "Sagar, Geetha Madhuri", "Iddarammayilatho"),
        ("Pakka Local", "Geetha Madhuri, Sagar", "Janatha Garage"),
        ("Jigelu Rani", "Rela Kumar, Ganta Venkata Lakshmi", "Rangasthalam")
    ]
}

FALLBACK_TRACKS = {
    "telugu": TELUGU_FALLBACK_TRACKS,
    "hindi": {
        "happy": [
            ("Gallan Goodiyaan", "Yashita Sharma, Manish Kumar Tipu, Farhan Akhtar", "Dil Dhadakne Do"),
            ("Badtameez Dil", "Benny Dayal, Shefali Alvares", "Yeh Jawaani Hai Deewani"),
            ("Kar Gayi Chull", "Badshah, Fazilpuria, Sukriti Kakar, Neha Kakkar", "Kapoor & Sons"),
            ("London Thumakda", "Labh Janjua, Sonu Kakkar, Neha Kakkar", "Queen"),
            ("Nashe Si Chadh Gayi", "Arijit Singh", "Befikre")
        ],
        "sad": [
            ("Channa Mereya", "Arijit Singh", "Ae Dil Hai Mushkil"),
            ("Agar Tum Saath Ho", "Alka Yagnik, Arijit Singh", "Tamasha"),
            ("Phir Bhi Tumko Chaahunga", "Arijit Singh, Shashaa Tirupati", "Half Girlfriend"),
            ("Tujhe Bhula Diya", "Mohit Chauhan, Shekhar Ravjiani, Shruti Pathak", "Anjaana Anjaani"),
            ("Kabira", "Tochi Raina, Rekha Bhardwaj", "Yeh Jawaani Hai Deewani")
        ],
        "neutral": [
            ("Ilahi", "Arijit Singh", "Yeh Jawaani Hai Deewani"),
            ("Safarnama", "Lucky Ali", "Tamasha"),
            ("Khaabon Ke Parinday", "Alyssa Mendonsa, Mohit Chauhan", "Zindagi Na Milegi Dobara"),
            ("Iktara", "Kavita Seth, Amit Trivedi", "Wake Up Sid"),
            ("Sham", "Amit Trivedi, Nikhil D'Souza, Neuman Pinto", "Aisha")
        ],
        "love": [
            ("Tum Hi Ho", "Arijit Singh", "Aashiqui 2"),
            ("Raabta", "Arijit Singh", "Agent Vinod"),
            ("Pee Loon", "Mohit Chauhan", "Once Upon A Time In Mumbaai"),
            ("Tera Ban Jaunga", "Akhil Sachdeva, Tulsi Kumar", "Kabir Singh"),
            ("Kesariya", "Arijit Singh", "Brahmastra")
        ],
        "angry": [
            ("Sultan", "Sukhwinder Singh, Shadab Faridi", "Sultan"),
            ("Malhari", "Vishal Dadlani", "Bajirao Mastani"),
            ("Zinda", "Siddharth Mahadevan", "Bhaag Milkha Bhaag"),
            ("Brothers Anthem", "Vishal Dadlani", "Brothers"),
            ("Dangal", "Daler Mehndi", "Dangal")
        ]
    },
    "english": {
        "happy": [
            ("Happy", "Pharrell Williams", "G I R L"),
            ("Can't Stop the Feeling!", "Justin Timberlake", "Trolls"),
            ("Uptown Funk", "Mark Ronson, Bruno Mars", "Uptown Special"),
            ("Good as Hell", "Lizzo", "Coconut Oil"),
            ("Shut Up and Dance", "WALK THE MOON", "Talking Is Hard")
        ],
        "sad": [
            ("Someone Like You", "Adele", "21"),
            ("Let Her Go", "Passenger", "All the Little Lights"),
            ("Fix You", "Coldplay", "X&Y"),
            ("Say Something", "A Great Big World, Christina Aguilera", "Is There Anybody Out There?"),
            ("All I Want", "Kodaline", "In a Perfect World")
        ],
        "neutral": [
            ("Yellow", "Coldplay", "Parachutes"),
            ("Sunday Morning", "Maroon 5", "Songs About Jane"),
            ("Riptide", "Vance Joy", "Dream Your Life Away"),
            ("Put Your Records On", "Corinne Bailey Rae", "Corinne Bailey Rae"),
            ("Banana Pancakes", "Jack Johnson", "In Between Dreams")
        ],
        "love": [
            ("Perfect", "Ed Sheeran", "Divide"),
            ("All of Me", "John Legend", "Love in the Future"),
            ("Just the Way You Are", "Bruno Mars", "Doo-Wops & Hooligans"),
            ("Adore You", "Harry Styles", "Fine Line"),
            ("Lover", "Taylor Swift", "Lover")
        ],
        "angry": [
            ("Numb", "Linkin Park", "Meteora"),
            ("Believer", "Imagine Dragons", "Evolve"),
            ("Stronger", "Kanye West", "Graduation"),
            ("Seven Nation Army", "The White Stripes", "Elephant"),
            ("Smells Like Teen Spirit", "Nirvana", "Nevermind")
        ]
    }
}

def get_playlist_id(mood: str, language: str):
    mood = (mood or "neutral").lower().strip()
    language = (language or "english").lower().strip()

    if mood not in MOOD_PLAYLISTS:
        mood = "neutral"

    playlists = MOOD_PLAYLISTS[mood]
    playlist_id = playlists.get(language) or playlists.get("english")
    return mood, language, playlist_id


def friendly_spotify_error(error: str):
    if not error:
        return None

    lower = error.lower()
    if "active premium subscription required" in lower:
        return "Spotify rejected this app token while loading public playlist metadata."
    if "credentials" in lower:
        return "Spotify credentials are missing or invalid."
    if "403" in lower:
        return "Spotify refused access to this playlist for the current app credentials."
    if "404" in lower:
        return "Spotify could not find this playlist. Check the playlist ID."
    if "failed to establish a new connection" in lower or "max retries exceeded" in lower:
        return "Spotify could not be reached. Check your internet connection or deployment network access."

    return "Spotify could not load tracks from this playlist."


# Simple in-process cache: query → {cover, spotify_url, name}
_search_cache: dict = {}


def search_itunes_track(name: str, artist: str):
    """
    Fetch album artwork and track link via the free iTunes Search API.
    Returns (cover_url, spotify_search_url).
    """
    cache_key = f"{name}|||{artist}"
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    spotify_url = f"https://open.spotify.com/search/{quote_plus(f'{name} {artist}')}"
    default = ("", spotify_url)

    try:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={"term": f"{name} {artist}", "media": "music", "limit": 1},
            timeout=8
        )
        if response.status_code != 200:
            print(f"[Moodify] iTunes search failed for '{name}': {response.status_code}")
            _search_cache[cache_key] = default
            return default

        results = response.json().get("results") or []
        if not results:
            print(f"[Moodify] iTunes: no results for '{name} {artist}'")
            _search_cache[cache_key] = default
            return default

        track = results[0]
        # Upgrade artwork to 600×600 for banner quality
        cover = (track.get("artworkUrl100") or "").replace("100x100bb", "600x600bb")
        result = (cover, spotify_url)
        _search_cache[cache_key] = result
        print(f"[Moodify] iTunes art found for '{name}': {cover[:70]}...")
        return result

    except Exception as exc:
        print(f"[Moodify] iTunes search exception for '{name}': {exc}")
        _search_cache[cache_key] = default
        return default


def fallback_tracks(mood: str, language: str, playlist_id: str, limit: int):
    language_tracks = FALLBACK_TRACKS.get(language) or FALLBACK_TRACKS["telugu"]
    tracks = language_tracks.get(mood) or language_tracks["neutral"]
    picked = random.sample(tracks, min(limit, len(tracks)))

    result = []
    for name, artist, album in picked:
        cover, spotify_url = search_itunes_track(name, artist)
        result.append({
            "name": name,
            "artist": artist,
            "album": album,
            "cover": cover,
            "spotify_url": spotify_url,
            "playlist_id": playlist_id,
            "source": "fallback"
        })
    return result



# ----------------------------------------
#  FETCH SONGS FROM PLAYLIST
# ----------------------------------------
def fetch_playlist_tracks(playlist_id, mood, language):
    """Returns track info for a playlist."""
    try:
        access_token = get_spotify_access_token()
        if not access_token:
            return [], "Spotify credentials are missing."

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "limit": 50,
            "offset": 0,
            "market": "IN",
            "fields": "items(track(name,type,is_local,artists,album(name,images),external_urls)),next"
        }
        songs = []

        while url:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=12
            )
            if response.status_code != 200:
                error_msg = format_spotify_error(response)
                print(f"[Moodify] Spotify playlist fetch failed for {playlist_id}: {error_msg}")
                try:
                    print(f"[Moodify] Spotify response body: {response.json()}")
                except Exception:
                    print(f"[Moodify] Spotify response text: {response.text[:300]}")
                return [], error_msg

            data = response.json()
            items = data.get("items") or []
            print(f"[Moodify] Playlist {playlist_id}: fetched {len(items)} items from Spotify")

            for item in items:
                if not item:
                    continue
                track = item.get("track")

                if not track or track.get("type") != "track" or track.get("is_local"):
                    continue

                artists = track.get("artists") or []
                album = track.get("album") or {}
                images = album.get("images") or []
                external_urls = track.get("external_urls") or {}
                artist_names = [artist.get("name") for artist in artists if artist.get("name")]

                if not track.get("name") or not external_urls.get("spotify"):
                    continue

                songs.append({
                    "name": track["name"],
                    "artist": ", ".join(artist_names) if artist_names else "Unknown artist",
                    "album": album.get("name", ""),
                    "cover": images[0]["url"] if images else "",
                    "spotify_url": external_urls["spotify"],
                    "playlist_id": playlist_id,
                    "source": "playlist"
                })

            url = data.get("next")
            params = None  # next URL already has query params embedded

        print(f"[Moodify] Playlist {playlist_id}: total valid tracks collected = {len(songs)}")
        return songs, None

    except Exception as e:
        print(f"[Moodify] Spotify API exception for playlist {playlist_id}: {e}")
        return [], str(e)


# ----------------------------------------
#  MAIN RECOMMENDER FUNCTION
# ----------------------------------------
def get_recommendations(mood: str, language: str, limit: int = 3):
    return get_recommendation_result(mood, language, limit)["songs"]


def get_recommendation_result(mood: str, language: str, limit: int = 3):
    mood, language, playlist_id = get_playlist_id(mood, language)
    if not playlist_id:
        return {
            "songs": [],
            "playlist_id": "",
            "mood": mood,
            "language": language,
            "error": "No playlist is mapped for this mood and language."
        }

    songs, error = fetch_playlist_tracks(playlist_id, mood, language)
    picked = random.sample(songs, min(limit, len(songs))) if songs else []
    if not picked:
        picked = fallback_tracks(mood, language, playlist_id, limit)

    return {
        "songs": picked,
        "playlist_id": playlist_id,
        "mood": mood,
        "language": language,
        "error": None if picked else friendly_spotify_error(error),
        "total_tracks_found": len(songs)
    }
