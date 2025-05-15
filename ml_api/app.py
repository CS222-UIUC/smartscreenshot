"""
ml_api/app.py

a Flask API for screenshot classification using a (our) trained CNN model
also: compare result with Google Vision API.

POST /predict
    - file: image
    - vision (optional; if): true → also return Google Vision API labels
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from tensorflow.keras.models import load_model
from ml_utils.preprocessing import load_and_preprocess_image

# the Vision API logic
try:
    from vision import get_image_labels
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
MODEL_PATH = "trained_model.h5"
CLASS_NAMES = ["UI", "Ad", "Game", "Error", "Text"]

# (Lazy-loading) model only once
model = None
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.before_first_request
def load_cnn_model():
    global model
    model = load_model(MODEL_PATH)
    print("[INFO] CNN model loaded.")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        image = load_and_preprocess_image(file_path)
        image = np.expand_dims(image, axis=0)
        preds = model.predict(image)
        predicted_index = int(np.argmax(preds, axis=1)[0])
        confidence = float(np.max(preds))

        result = {
            "filename": filename,
            "cnn_prediction": {
                "label": CLASS_NAMES[predicted_index],
                "confidence": round(confidence, 4)
            }
        }

        # when Vision API comparison is requested
        if request.args.get("vision") == "true":
            if VISION_AVAILABLE:
                vision_labels = get_image_labels(file_path)
                result["vision_labels"] = vision_labels
            else:
                result["vision_labels"] = "Vision API integration not available."

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "model_loaded": model is not None})

if __name__ == "__main__":
    app.run(debug=True)
