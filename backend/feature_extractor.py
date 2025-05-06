import librosa
import numpy as np
import json

midi_mapping = {
    "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
    "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
}

NOTE_NAMES = list(midi_mapping.keys())

thaat_dict = {
    "Major": [0, 2, 4, 5, 7, 9, 11],     # Ionian
    "Minor": [0, 2, 3, 5, 7, 8, 10],     # Aeolian
    "Kalyan": [0, 2, 4, 6, 7, 9, 11],    # Lydian
    "Khamaj": [0, 2, 4, 5, 7, 9, 10],    # Mixolydian
    "Bhairav": [0, 1, 4, 5, 7, 8, 11],   # Phrygian ♮4
    "Bhairavi": [0, 1, 3, 5, 7, 8, 10],  # Phrygian
    "Todi": [0, 1, 3, 6, 7, 8, 11],      # Todi
    "Purvi": [0, 1, 4, 6, 7, 8, 11],     # Purvi
    "Marwa": [0, 1, 4, 6, 7, 9, 11],     # Marwa
    "Kaafi": [0, 2, 3, 5, 7, 9, 10]      # Dorian
}

def get_best_matching_thaat(chroma_vector, key_index):
    best_score = -np.inf
    best_thaat = None
    for name, intervals in thaat_dict.items():
        template = np.zeros(12)
        for interval in intervals:
            template[(key_index + interval) % 12] = 1
        score = np.dot(chroma_vector, template)
        if score > best_score:
            best_score = score
            best_thaat = name
    return best_thaat

def extract_features_as_json(file_path, save_to_file=True):  
    y, sr = librosa.load(file_path, sr=None)

    # Beat and tempo
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Onsets
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onsets = librosa.frames_to_time(onset_frames, sr=sr)

    # RMS energy
    rms = librosa.feature.rms(y=y)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)

    # Pitch tracking
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_contour = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        pitch_contour.append(pitch if pitch > 0 else None)

    # Harmonic for chroma
    y_harmonic, _ = librosa.effects.hpss(y)
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    key_index = chroma_mean.argmax()
    key = NOTE_NAMES[key_index]

    # Best thaat scale
    scale_mode = get_best_matching_thaat(chroma_mean, key_index)

    # Time signature estimation (basic)
    def guess_time_signature(bt):
        if len(bt) < 2: return "4/4"
        spacing = np.median(np.diff(bt))
        bpb = round(60 / spacing)
        return "3/4" if bpb == 3 else "4/4"

    # Timbre
    centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    bandwidth = float(librosa.feature.spectral_bandwidth(y=y, sr=sr).mean())

    # Estimate chord progression
    chords = estimate_chord_progression(y, sr, beat_times, chroma)

    # JSON output
    output = {
        "tempo_bpm": float(tempo[0]) if isinstance(tempo, (list, np.ndarray)) else float(tempo),
        "time_signature": guess_time_signature(beat_times),
        "key": key,
        "scale_mode": scale_mode,
        "beats": beat_times.tolist(),
        "onsets": onsets.tolist(),
        "spectral_centroid": centroid,
        "spectral_bandwidth": bandwidth,
        "pitch_contour": [float(p) if p else None for p in pitch_contour[:len(rms_times)]],
        "velocity_rms": [float(v) for v in rms[:len(rms_times)]],
        "time_axis": rms_times[:len(rms)].tolist(),
        "chord_progression": [{"time": t, "chord": c} for t, c in chords]
    }

    if save_to_file:
        with open("output_features.json", "w") as f:
            json.dump(output, f, indent=2)
    return json.dumps(output, indent=2)

def estimate_chord_progression(y, sr, beat_times, chroma):
    from collections import Counter

    chord_labels = []
    triads = {
        'C': [0, 4, 7], 'C#': [1, 5, 8], 'D': [2, 6, 9], 'D#': [3, 7, 10],
        'E': [4, 8, 11], 'F': [5, 9, 0], 'F#': [6, 10, 1], 'G': [7, 11, 2],
        'G#': [8, 0, 3], 'A': [9, 1, 4], 'A#': [10, 2, 5], 'B': [11, 3, 6]
    }

    labels = list(triads.keys())
    chords = []

    for i in range(len(beat_times) - 1):
        start = librosa.time_to_frames(beat_times[i], sr=sr)
        end = librosa.time_to_frames(beat_times[i + 1], sr=sr)
        segment = chroma[:, start:end]
        avg_chroma = np.mean(segment, axis=1)
        scores = {}
        for label in labels:
            indices = triads[label]
            scores[label] = sum(avg_chroma[i] for i in indices)
        best = max(scores, key=scores.get)
        chords.append((float(beat_times[i]), best))

    return chords

       
# Example usage
file_path = '/Users/bhuman/Desktop/`Perfect - Ed Sheeran.mp3'
extract_features_as_json(file_path)