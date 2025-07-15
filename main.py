from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Phrase storage file
PHRASES_FILE = "phrases.json"

# Load phrases from file
def load_phrases():
    if os.path.exists(PHRASES_FILE):
        with open(PHRASES_FILE, "r") as f:
            return json.load(f)
    return []

# Save phrases to file
def save_phrases(phrases):
    with open(PHRASES_FILE, "w") as f:
        json.dump(phrases, f)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/phrases')
def get_phrases():
    phrases = load_phrases()
    phrases = sorted(phrases, key=lambda x: not x.get("pinned", False))  # Pinned first
    return jsonify(phrases)

@app.route('/save', methods=['POST'])
def save():
    text = request.form.get("text")
    file = request.files.get("image")
    image_url = None

    if file:
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
        image_url = f"/uploads/{filename}"

    phrases = load_phrases()

    # Prevent duplicates
    if any(p["text"] == text for p in phrases):
        return jsonify(success=False, message="Phrase already exists")

    phrases.append({
        "text": text,
        "pinned": False,
        "image": image_url
    })
    save_phrases(phrases)
    return jsonify(success=True)

@app.route('/toggle_pin', methods=['POST'])
def toggle_pin():
    text = request.json.get("text")
    phrases = load_phrases()
    for p in phrases:
        if p["text"] == text:
            p["pinned"] = not p.get("pinned", False)
    save_phrases(phrases)
    return jsonify(success=True)

@app.route('/delete', methods=['POST'])
def delete():
    text = request.json.get("text")
    phrases = load_phrases()
    phrases = [p for p in phrases if p["text"] != text]
    save_phrases(phrases)
    return jsonify(success=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)