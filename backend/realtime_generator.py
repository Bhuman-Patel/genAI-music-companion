import threading
import time
import json
import random
import fluidsynth

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

THAAT_DICT = {
    "Major": [0, 2, 4, 5, 7, 9, 11],
    "Minor": [0, 2, 3, 5, 7, 8, 10],
    "Kalyan": [0, 2, 4, 6, 7, 9, 11],
    "Khamaj": [0, 2, 4, 5, 7, 9, 10],
    "Bhairav": [0, 1, 4, 5, 7, 8, 11],
    "Bhairavi": [0, 1, 3, 5, 7, 8, 10],
    "Todi": [0, 1, 3, 6, 7, 8, 11],
    "Purvi": [0, 1, 4, 6, 7, 8, 11],
    "Marwa": [0, 1, 4, 6, 7, 9, 11],
    "Kaafi": [0, 2, 3, 5, 7, 9, 10],
}

should_generate = False
generation_thread = None
fs = None

current_states = {}
current_volumes = {}

def is_channel_enabled(name):
    states = current_states
    if not states:
        return True
    if any(cfg.get('solo') for cfg in states.values()):
        return states.get(name, {}).get('solo', False)
    return not states.get(name, {}).get('mute', False)


def fade_in(fs, target_volumes, channels, duration_sec=4.0):
    steps = 20
    interval = duration_sec / steps
    for step in range(steps + 1):
        for ch, name in channels.items():
            target = int(target_volumes.get(name, 0.8) * 127)
            fs.cc(ch, 7, int(target * step / steps))
        time.sleep(interval)


def fade_out_and_stop(fs, channels, duration_sec=4.0):
    global should_generate
    steps = 20
    interval = duration_sec / steps
    for step in range(steps + 1):
        for ch in channels:
            fs.cc(ch, 7, int(127 * (1 - step / steps)))
        time.sleep(interval)
    fs.system_reset()
    fs.delete()
    should_generate = False


def start_infinite_generation(features_json, instrument_states, instrument_volumes):
    global should_generate, generation_thread, fs, current_states, current_volumes
    if generation_thread and generation_thread.is_alive():
        return
    should_generate = True
    current_states = instrument_states
    current_volumes = instrument_volumes

    def generator():
        features = json.loads(features_json)
        key = features.get("key", "C")
        scale = features.get("scale_mode", "Major")
        tempo = float(features.get("tempo_bpm", 90))
        beat_duration = 60.0 / tempo

        root_index = NOTE_NAMES.index(key)
        scale_degrees = THAAT_DICT.get(scale, THAAT_DICT["Major"])
        scale_notes = [(root_index + interval) % 12 for interval in scale_degrees]

        melody_notes = [12 * o + n for o in range(5, 7) for n in scale_notes]
        bass_note = 12 * 2 + scale_notes[0]
        pad_chord = [12 * 4 + scale_notes[i % len(scale_notes)] for i in (0, 2, 4)]
        guitar_arpeggio = [12 * 4 + n for n in scale_notes[:4]]
        choir_notes = [12 * 5 + scale_notes[0]]

        fs = fluidsynth.Synth()
        fs.start(driver="coreaudio")
        sfid = fs.sfload("/Users/bhuman/soundfonts/GeneralUser.sf2")
        fs.program_select(0, sfid, 0, 0)     # Piano
        fs.program_select(1, sfid, 0, 32)    # Bass
        fs.program_select(2, sfid, 0, 89)    # Pad
        fs.program_select(3, sfid, 0, 24)    # Nylon Guitar
        fs.program_select(4, sfid, 0, 52)    # Choir

        print("🎻 Multi-instrument generation started")

        channels = {0: "Keys", 1: "Bass", 2: "Pad", 3: "Guitar", 4: "Flute"}
        for ch in channels:
            fs.cc(ch, 7, 0)  # initial silent

        threading.Thread(target=fade_in, args=(fs, current_volumes, channels)).start()

        i = 0
        pad_counter = bass_counter = guitar_counter = choir_counter = 0

        while should_generate:
            note = random.choice(melody_notes)
            vel = random.randint(85, 115)
            dur = beat_duration * random.choice([0.25, 0.5, 0.75, 1])

            if is_channel_enabled("Keys"):
                fs.noteon(0, note, vel)
                time.sleep(dur)
                fs.noteoff(0, note)
            else:
                time.sleep(dur)

            bass_counter += dur
            if bass_counter >= beat_duration * 4 and is_channel_enabled("Bass"):
                fs.noteon(1, bass_note, random.randint(90, 110))
                time.sleep(beat_duration * 0.9)
                fs.noteoff(1, bass_note)
                bass_counter = 0

            pad_counter += dur
            if pad_counter >= beat_duration * 8 and is_channel_enabled("Pad"):
                for n in pad_chord:
                    fs.noteon(2, n, random.randint(55, 75))
                time.sleep(beat_duration * 3)
                for n in pad_chord:
                    fs.noteoff(2, n)
                pad_counter = 0

            guitar_counter += dur
            if guitar_counter >= beat_duration * 2 and is_channel_enabled("Guitar"):
                for gn in guitar_arpeggio:
                    fs.noteon(3, gn, random.randint(70, 90))
                    time.sleep(beat_duration * 0.3)
                    fs.noteoff(3, gn)
                guitar_counter = 0

            choir_counter += dur
            if choir_counter >= beat_duration * 16 and is_channel_enabled("Flute"):
                for cn in choir_notes:
                    fs.noteon(4, cn, random.randint(40, 60))
                time.sleep(beat_duration * 5)
                for cn in choir_notes:
                    fs.noteoff(4, cn)
                choir_counter = 0


    generation_thread = threading.Thread(target=generator)
    generation_thread.start()


def stop_infinite_generation():
    global fs
    channels = {0: "Keys", 1: "Bass", 2: "Pad", 3: "Guitar", 4: "Flute"}
    if fs:
        fade_out_and_stop(fs, channels)
    else:
        global should_generate
        should_generate = False
