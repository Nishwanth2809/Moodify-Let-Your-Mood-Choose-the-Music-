import wave
import numpy as np

def extract_audio_features(file_path):
    with wave.open(file_path, "rb") as wav_file:
        n_channels = wav_file.getnchannels()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        audio_frames = wav_file.readframes(n_frames)

    audio = np.frombuffer(audio_frames, dtype=np.int16)
    if audio.size == 0:
        return 0, 0

    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)

    audio = audio.astype(np.float32)
    peak_amplitude = np.max(np.abs(audio))
    if peak_amplitude < 1e-6:
        return 0, 0

    audio /= peak_amplitude

    amplitude = np.abs(audio)
    peaks = np.where(amplitude > max(amplitude.mean() * 2.0, 0.08))[0]
    duration = len(audio) / framerate
    tempo = len(peaks) / duration if duration > 0 else 0

    windowed = audio * np.hanning(len(audio))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1 / framerate)
    peak_idx = np.argmax(np.abs(fft))
    peak_freq = abs(freqs[peak_idx])

    return round(tempo, 2), round(peak_freq, 2)
