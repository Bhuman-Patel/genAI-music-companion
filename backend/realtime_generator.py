import threading
import time
import mido
import json
import librosa

should_generate = False
generation_thread = None

def start_infinite_generation(features_json):
    global should_generate, generation_thread
    if generation_thread and generation_thread.is_alive():
        return  # already running
    should_generate = True

    def generator():
        features = json.loads(features_json)
        pitch = features["pitch_contour"]
        velocity = features["velocity_rms"]
        time_axis = features["time_axis"]

        # 💡 Replace with the exact name from mido.get_output_names()
        output_port_name = "FluidSynth virtual port"

        try:
            port = mido.open_output(output_port_name)
            print(f"🎹 Sending MIDI to: {output_port_name}")
        except IOError:
            print("❌ Could not find FluidSynth output port. Check port name with mido.get_output_names()")
            return

        i = 0
        while should_generate:
            idx = i % len(pitch)
            if pitch[idx] is None:
                i += 1
                continue

            midi_note = int(librosa.hz_to_midi(pitch[idx]))
            vel = min(max(int(velocity[idx] * 200), 30), 127)
            start = time_axis[idx]
            duration = 0.25  # or use time_axis[i+1] - time_axis[i] for real timing

            port.send(mido.Message('note_on', note=midi_note, velocity=vel))
            time.sleep(duration)
            port.send(mido.Message('note_off', note=midi_note))

            i += 1

    generation_thread = threading.Thread(target=generator)
    generation_thread.start()

def stop_infinite_generation():
    global should_generate
    should_generate = False
