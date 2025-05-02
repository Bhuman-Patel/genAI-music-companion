from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from feature_extractor import extract_features_as_json
from realtime_generator import start_infinite_generation, stop_infinite_generation

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav','mp3'}

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Flask Music Generator API is running."
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

instrument_states = {}

# Global state to store last extracted features
latest_features_json = None


@app.route('/update-controls', methods=['POST'])
def update_controls():
    print("/update-controls here !!!")
    global instrument_states
    try:
        instrument_states = request.json.get('instrument_states', {})
        return jsonify({"status": "updated", "received": instrument_states})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


instrument_volumes = {}


@app.route('/update-volumes', methods=['POST'])
def update_volumes():
    print("/update-volumes here !!!")
    global instrument_volumes
    try:
        instrument_volumes = request.json.get('volumes', {})
        return jsonify({"status": "volume updated", "received": instrument_volumes})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(filepath)

        try:
            result_json = extract_features_as_json(filepath)
            global latest_features_json
            latest_features_json = result_json
            return jsonify(json_result=result_json)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(filepath)

    return jsonify({"error": "Invalid file format"}), 400

@app.route('/start-generation', methods=['POST'])
def start_gen():
    if not latest_features_json:
        return jsonify({"error": "Analyze audio first"}), 400
    start_infinite_generation(latest_features_json, instrument_states, instrument_volumes)
    return jsonify({"status": "generation_started"})


@app.route('/stop-generation', methods=['POST'])
def stop_gen():
    stop_infinite_generation()
    return jsonify({"status": "generation_stopped"})

if __name__ == '__main__':
    app.run(debug=True)