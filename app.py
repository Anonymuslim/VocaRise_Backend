import os
import uuid
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from TTS.api import TTS

# Config
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

# Initialisation Flask
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

tts = None  # Initialisation différée

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file("index.html")  # Utilisé pour servir ton front déployé avec les fichiers statiques

@app.route('/api/clone-voice', methods=['POST'])
def clone_voice():
    global tts
    try:
        if 'audio' not in request.files or 'text' not in request.form:
            return jsonify({'error': 'Fichier audio ou texte manquant'}), 400

        file = request.files['audio']
        text = request.form['text'].strip()

        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Format de fichier non autorisé'}), 400

        # Chargement unique du modèle
        if tts is None:
            print("🔁 Chargement XTTS v2...")
            tts = TTS(
                config_path="xtts_model/config.json",
                model_path="xtts_model/model.pth",
                progress_bar=False,
                gpu=False
            )

        # Gestion des noms
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        ext = os.path.splitext(file.filename)[1]
        filename = f"upload_{timestamp}{ext}"
        wav_filename = f"converted_{timestamp}.wav"
        output_name = f"voice_clone_{timestamp}.mp3"

        raw_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

        file.save(raw_path)
        audio = AudioSegment.from_file(raw_path).set_channels(1).set_frame_rate(16000).normalize()
        audio.export(wav_path, format="wav")

        tts.tts_to_file(
            text=text + ".",
            speaker_wav=wav_path,
            language="fr",
            file_path=output_path
        )

        # Ajouter un peu de silence pour plus de naturel
        final_audio = AudioSegment.from_file(output_path)
        final_audio += AudioSegment.silent(duration=1000)
        final_audio.export(output_path, format="mp3")

        return jsonify({'success': True, 'audio_url': f'/api/audio/{output_name}'})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur serveur : {str(e)}'}), 500

@app.route('/api/audio/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Lancer l'app
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Flask running on port {port}")
    app.run(host='0.0.0.0', port=port)
