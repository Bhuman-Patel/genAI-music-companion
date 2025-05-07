# 🧠🎵 MindMelody

**Feel the Thought. Hear the Tune.**  
An AI-powered, real-time music generation system that analyzes user-uploaded audio and generates infinite, expressive melodies using multiple instruments.

## 🎯 Project Overview

MindMelody enables users to:
- Upload any audio file they enjoy.
- Analyze musical features like **tempo**, **key**, **scale**, and **time signature** in real time.
- Trigger AI-generated music that matches the mood and characteristics of the uploaded audio.
- Control each instrument (🎸 Guitar, 🎶 Flute, 🎻 Pad, 🎷 Bass, 🎺 Keys) with **Solo**, **Mute**, and **Volume** sliders.
- Enjoy continuous playback with dynamic layering and phrase-based expressiveness.

## 🧱 Project Structure

```
📁 backend/
├── app.py                  # Flask API server
├── feature_extractor.py    # Extracts BPM, key, scale, etc.
├── realtime_generator.py   # Starts live MIDI generation using FluidSynth
└── requirements.txt        # Python dependencies

📁 music_companion_ui/
└── lib/
    └── main.dart           # Flutter web app (UI + logic)
```

## 🚀 Getting Started

### Backend Setup (Python + Flask)

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure FluidSynth is installed:**
   ```bash
   brew install fluid-synth  # On macOS
   ```

4. **Run the backend:**
   ```bash
   python app.py
   ```

   By default, this runs on `http://0.0.0.0:5000/`

---

### Frontend Setup (Flutter Web)

1. **Ensure Flutter is installed with web support.**

2. **Navigate to the UI directory:**
   ```bash
   cd music_companion_ui
   ```

3. **Run the Flutter web app:**
   ```bash
   flutter run -d chrome
   ```

4. The app will open in your browser. Upload an audio file and hit **Generate Music**!

---

## 📡 API Endpoints

| Method | Endpoint               | Description                          |
|--------|------------------------|--------------------------------------|
| POST   | `/analyze-audio`       | Upload and analyze audio features    |
| POST   | `/start-generation`    | Start infinite music generation loop |

---

## 🛠️ Tech Stack

- **Flutter Web** – Responsive UI with instrument controls
- **Python (Flask)** – REST API backend
- **FluidSynth** – Real-time audio synthesis
- **Lottie** – Animations for interactive feedback
- **file_picker** – Cross-platform file selection in Flutter

---

## 🧠 Future Enhancements

- Add more instruments and layers (e.g. drums, arpeggios)
- Export generated music to WAV/MP3
- Host the entire system on AWS / Render for live demos
- Add adaptive phrasing and emotional modulation using LSTM or MusicVAE

---

## 📄 License

MIT License. Feel free to fork and extend!

---

## 🤝 Contributors

Bhuman Patel — [@bhumanpatel31](mailto:bhumanpatel31@gmail.com)
