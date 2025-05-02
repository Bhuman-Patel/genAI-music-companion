from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Placeholder: return filename or trigger processing
    return jsonify({"message": "File uploaded successfully", "filename": file.filename})

@app.route("/play", methods=["POST"])
def play_music():
    data = request.json
    print("Received control config:", data)

    # TODO: Hook to your real-time generation engine
    return jsonify({"message": "Playback started with config"})

@app.route("/stop", methods=["POST"])
def stop_music():
    # TODO: Hook to your real-time engine to stop
    return jsonify({"message": "Playback stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

