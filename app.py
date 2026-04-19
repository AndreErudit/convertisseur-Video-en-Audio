from flask import Flask, render_template, request, send_file, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os, subprocess, uuid

app = Flask(__name__)

# 🔒 limite 60MB
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024

# 🔒 rate limit
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/convert', methods=['POST'])
@limiter.limit("5 per minute")
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Fichier vide"}), 400

    # 🔒 validation type simple
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        return jsonify({"error": "Format non supporté"}), 400

    unique_name = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, unique_name + ".mp4")
    output_path = os.path.join(OUTPUT_FOLDER, unique_name + ".mp3")

    file.save(input_path)

    try:
        command = [
        "ffmpeg",
        "-i", input_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-b:a", "128k",
        "-threads", "2",
        "-preset", "ultrafast",
        "-y",
        output_path
    ]

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Erreur conversion"}), 500

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# 🔥 obligatoire pour Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)