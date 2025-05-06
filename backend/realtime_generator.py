import threading
import time
import json
import random
import fluidsynth
import atexit
from thaat_key import THAAT_DICT
from thaat_key import NOTE_NAMES

should_generate = False
generation_thread = None
fs = None
current_states = {}
current_volumes = {}

def is_channel_enabled(name):
    if not current_states:
        return True
    if any(cfg.get('solo') for cfg in current_states.values()):
        return current_states.get(name, {}).get('solo', False)
    return not current_states.get(name, {}).get('mute', False)


def fs_grace_note(fs, channel, note, velocity=90, duration=0.1):
    grace = note - 1
    fs.noteon(channel, grace, velocity)
    time.sleep(duration)
    fs.noteoff(channel, grace)

def fs_mordent(fs, channel, note, velocity=90, duration=0.1):
    upper = note + 1
    fs.noteon(channel, note, velocity)
    time.sleep(duration)
    fs.noteon(channel, upper, velocity)
    time.sleep(duration)
    fs.noteoff(channel, upper)
    time.sleep(duration)
    fs.noteoff(channel, note)

def fs_andolan(fs, channel, note, velocity=90, duration=0.4, oscillations=3):
    fs.noteon(channel, note, velocity)
    for _ in range(oscillations):
        fs.noteoff(channel, note)
        time.sleep(duration / (oscillations * 2))
        fs.noteon(channel, note, velocity)
        time.sleep(duration / (oscillations * 2))
    fs.noteoff(channel, note)

def fs_meend(fs, channel, note1, note2, steps=4, velocity=90, duration=0.4):
    interval = (note2 - note1) / steps
    for i in range(steps):
        n = int(note1 + i * interval)
        fs.noteon(channel, n, velocity)
        time.sleep(duration / steps)
        fs.noteoff(channel, n)

def fs_gamak(fs, channel, note, velocity=90, duration=0.3, oscillations=4):
    lower = note - 1
    for _ in range(oscillations):
        fs.noteon(channel, note, velocity)
        time.sleep(duration / (oscillations * 2))
        fs.noteoff(channel, note)
        fs.noteon(channel, lower, velocity)
        time.sleep(duration / (oscillations * 2))
        fs.noteoff(channel, lower)
    


def play_expressive_melody(fs, melody_notes, beat_duration, phrase_position, previous_note=None):
    note = random.choice(melody_notes)
    velocity = 90
    channel = 0

    # Ornament rules
    ornament = None

    # 1. Sustained note → Vibrato (Andolan)
    if phrase_position % 4 == 3:
        ornament = fs_andolan

    # 2. Phrase start → Grace note
    elif phrase_position % 4 == 0:
        ornament = fs_grace_note

    # 3. Repeated note → Mordent
    elif previous_note is not None and abs(note - previous_note) <= 1:
        ornament = fs_mordent

    # 4. Large jump → Meend
    elif previous_note is not None and abs(note - previous_note) >= 4:
        ornament = lambda fs, ch, n: fs_meend(fs, ch, previous_note, n)

    # 5. Phrase end → Gamak
    elif phrase_position % 8 == 7:
        ornament = fs_gamak

    # Play with selected ornament
    if ornament:
        ornament(fs, channel, note)
    else:
        fs.noteon(channel, note, velocity)
        time.sleep(beat_duration * 0.9)
        fs.noteoff(channel, note)

    return note
  # track for next round


def start_infinite_generation(features_json, instrument_states, instrument_volumes):
    global should_generate, generation_thread, fs, current_states, current_volumes

    if generation_thread and generation_thread.is_alive():
        return

    should_generate = True
    current_states = instrument_states
    current_volumes = instrument_volumes

    def generator() :
        features = json.loads(features_json)
        key = features.get("key", "C")
        scale = features.get("scale_mode", "Major")
        tempo = float(features.get("tempo_bpm", 80))
        beat_duration = 60.0 / tempo

        root_index = NOTE_NAMES.index(key)
        scale_degrees = THAAT_DICT.get(scale, THAAT_DICT["Major"])
        scale_notes = [(root_index + interval) % 12 for interval in scale_degrees]

        # Expanded note ranges for expressive phrasing
        melody_notes = [12 * o + n for o in range(5, 7) for n in scale_notes]
        bass_notes = [12 * 2 + n for n in scale_notes[:3]]
        pad_chords = [[12 * 4 + scale_notes[i % len(scale_notes)] for i in (0, 2, 4)] for _ in range(4)]
        guitar_patterns = [[12 * 4 + n for n in scale_notes[i:i+3]] for i in range(0, len(scale_notes)-2, 3)]

        phrase_length = 16  # beats per phrase (e.g., 4 bars of 4/4)
        phrase_position = 0
        previous_note = None

        fs = fluidsynth.Synth()
        fs.start(driver="coreaudio")
        sfid = fs.sfload("/Users/bhuman/soundfonts/GeneralUser.sf2")
        fs.program_select(0, sfid, 0, 73)  # Flute
        fs.program_select(1, sfid, 0, 48)  # Strings / Pad
        fs.program_select(2, sfid, 0, 25)  # Guitar
        fs.program_select(3, sfid, 0, 32)  # Bass

        while should_generate:
            phrase_stage = (phrase_position // 4) % 4  # 0 to 3 (intro, build, climax, resolve)
            melody_intensity = [0.3, 0.6, 1.0, 0.5][phrase_stage]

            # Melody - richer during climax
            if is_channel_enabled("melody"):
                note = play_expressive_melody(fs, melody_notes, beat_duration, phrase_position, previous_note)
                previous_note = note

            # Chord Pad - slower rate
            if phrase_position % 8 == 0 and is_channel_enabled("pad"):
                chord = random.choice(pad_chords)
                for note in chord:
                    fs.noteon(1, note, int(40 + melody_intensity * 40))

            # Guitar - moderate rhythm
            if phrase_position % 4 == 0 and is_channel_enabled("guitar"):
                notes = random.choice(guitar_patterns)
                for note in notes:
                    fs.noteon(2, note, int(50 + melody_intensity * 40))

            # Bass - simple root motion
            if phrase_position % 4 == 0 and is_channel_enabled("bass"):
                note = random.choice(bass_notes)
                fs.noteon(3, note, int(40 + melody_intensity * 30))

            time.sleep(beat_duration)
            phrase_position += 1

            features = json.loads(features_json)
            key = features.get("key", "C")
            scale = features.get("scale_mode", "Major")
            tempo = float(features.get("tempo_bpm", 80))
            beat_duration = 60.0 / tempo

            root_index = NOTE_NAMES.index(key)
            from thaat_key import tonal_values

        melody_base = tonal_values(key, scale)
        melody_notes = []
        for octave in range(5, 7):
            melody_notes += [note + 12 * (octave - 5) for note in melody_base]
            bass_note = 12 * 2 + scale_notes[0]
            pad_chord = [12 * 4 + scale_notes[i % len(scale_notes)] for i in (0, 2, 4)]
            guitar_notes = [12 * 4 + n for n in scale_notes[:4]]
            flute_note = 12 * 5 + scale_notes[0]

            fs = fluidsynth.Synth()
            fs.start(driver="coreaudio")
            sfid = fs.sfload("/Users/bhuman/soundfonts/GeneralUser.sf2")
            fs.program_select(0, sfid, 0, 0)     # Piano / Keys
            fs.program_select(1, sfid, 0, 32)    # Bass
            fs.program_select(2, sfid, 0, 89)    # Pad
            fs.program_select(3, sfid, 0, 24)    # Guitar
            fs.program_select(4, sfid, 0, 52)    # Flute/Choir

            next_melody = time.time() + 0.2
            next_bass = time.time() + 2.0
            next_pad = time.time() + 4.0
            next_guitar = time.time() + 3.0
            next_flute = time.time() + 6.0

            print("🎶 Smooth generation started")

            while should_generate:
                now = time.time()

                if now >= next_melody and is_channel_enabled("Keys"):
                    previous_note = play_expressive_melody(fs, melody_notes, beat_duration, phrase_position, previous_note)
                    vel = random.randint(85, 115)
                    dur = random.uniform(0.3, 0.6)
                    fs.noteon(0, note, vel)
                    threading.Timer(dur, lambda: fs.noteoff(0, note)).start()
                    next_melody = now + random.uniform(0.4, 1.0)

                if now >= next_bass and is_channel_enabled("Bass"):
                    vel = random.randint(70, 100)
                    fs.noteon(1, bass_note, vel)
                    threading.Timer(0.8, lambda: fs.noteoff(1, bass_note)).start()
                    next_bass = now + random.uniform(2.0, 4.0)

                if now >= next_pad and is_channel_enabled("Pad"):
                    for n in pad_chord:
                        fs.noteon(2, n, random.randint(40, 70))
                    threading.Timer(2.5, lambda: [fs.noteoff(2, n) for n in pad_chord]).start()
                    next_pad = now + random.uniform(6.0, 10.0)

                if now >= next_guitar and is_channel_enabled("Guitar"):
                    for gn in guitar_notes:
                        fs.noteon(3, gn, random.randint(60, 90))
                        threading.Timer(0.3, lambda n=gn: fs.noteoff(3, n)).start()
                        time.sleep(0.2)
                    next_guitar = now + random.uniform(4.0, 6.0)

                if now >= next_flute and is_channel_enabled("Flute"):
                    fs.noteon(4, flute_note, random.randint(50, 75))
                    threading.Timer(2.0, lambda: fs.noteoff(4, flute_note)).start()
                    next_flute = now + random.uniform(10.0, 15.0)

                time.sleep(0.05)

            fs.system_reset()
            fs.delete()
            print("🛑 Generation stopped")

    generation_thread = threading.Thread(target=generator)
    generation_thread.start()

def stop_infinite_generation():
    global should_generate, fs, generation_thread

    should_generate = False

    # Safely stop thread
    if generation_thread and generation_thread.is_alive():
        generation_thread.join(timeout=1.0)

    # Turn off all notes and stop audio
    if fs:
        try:
            for chan in range(16):
                fs.cc(chan, 123, 0)  # All notes off
            fs.delete()
        except Exception as e:
            print(f"Error during FluidSynth cleanup: {e}")
        fs = None

    print("✅ Generation stopped. All notes off.")

def cleanup_fluidsynth():
    global fs
    if fs:
        try:
            for chan in range(16):
                fs.cc(chan, 123, 0)
            fs.delete()
        except Exception as e:
            print(f"Error cleaning up fluidsynth: {e}")
        fs = None

atexit.register(cleanup_fluidsynth)