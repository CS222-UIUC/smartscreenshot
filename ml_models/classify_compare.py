import os
import numpy as np
from tensorflow.keras.models import load_model
from ml_utils.preprocessing import load_and_preprocess_image
from vision import get_image_labels

CLASS_NAMES = ["UI", "Ad", "Game", "Error", "Text"]

def classify_with_model(image_path, model_path='trained_model.h5'):
    model = load_model(model_path)
    image = load_and_preprocess_image(image_path)
    image = np.expand_dims(image, axis=0)
    preds = model.predict(image)
    predicted_class = np.argmax(preds, axis=1)[0]
    return CLASS_NAMES[predicted_class]

def classify_with_vision_api(image_path):
    try:
        labels = get_image_labels(image_path)
        return labels  # returns top 5 labels, less if fewer found
    except Exception as e:
        return [f"Error: {str(e)}"]

def compare_outputs(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(folder_path, filename)
            cnn_label = classify_with_model(path)
            vision_labels = classify_with_vision_api(path)
            print(f"\n📷 {filename}")
            print(f"CNN Prediction: {cnn_label}")
            print(f"Vision API Labels: {vision_labels}")

if __name__ == "__main__":
    compare_outputs("test")
    # compare_outputs("uploaded_screenshots")