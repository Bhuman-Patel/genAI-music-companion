# Thaat and keys

midi_mapping = {
        "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
        "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
    }

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

THAAT_DICT = {

        # "Bilawal": [0, 2, 4, 5, 7, 9, 11],   # Major Scale (Ionian)
        "Major": [0, 2, 4, 5, 7, 9, 11],   # Major Scale (Ionian)
        "Minor": [0, 2, 3, 5, 7, 8, 10],   # Natural Minor (Aeolian)/ Asavari
        "Kalyan": [0, 2, 4, 6, 7, 9, 11],    # Lydian
        "Khamaj": [0, 2, 4, 5, 7, 9, 10],    # Mixolydian
        "Bhairav": [0, 1, 4, 5, 7, 8, 11],   # Phrygian ♮4
        "Bhairavi": [0, 1, 3, 5, 7, 8, 10],  # Phrygian
        "Todi": [0, 1, 3, 6, 7, 8, 11],      # Augmented Phrygian
        "Purvi": [0, 1, 4, 6, 7, 8, 11],     # Similar to Todi but major third
        "Marwa": [0, 1, 4, 6, 7, 9, 11],     # Similar to Purvi but different Ni
        "Kaafi": [0, 2, 3, 5, 7, 9, 10]      # Dorian
    }

def tonal_values(key_name, scale_name):
    
    key_place = midi_mapping[key_name]
    return tonal_values[ key_place + THAAT_DICT[scale_name]]