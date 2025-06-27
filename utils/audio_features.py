import librosa
import numpy as np

def extract_audio_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=16000)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        f0 = librosa.yin(y, fmin=50, fmax=500)
        pitch = np.median(f0[f0 > 0]) if np.any(f0 > 0) else 0
        return round(float(tempo), 2), round(float(pitch), 2)
    except:
        return 0, 0
