"""
ml_utils/preprocessing.py

Image preprocessing for the CNN pipeline:
- Resizing
- Denoising
- Edge detection
- Normalization

call / apply script on both `test/` and `uploaded_screenshots/` folders depending on step -->
"""

import cv2
import numpy as np
import os

def resize_image(image, size=(224, 224)):
    return cv2.resize(image, size)

def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

def detect_edges(image):
    return cv2.Canny(image, 100, 200)

def normalize_image(image):
    return image.astype("float32") / 255.0

def load_and_preprocess_image(path):
    image = cv2.imread(path)
    image = resize_image(image)
    image = denoise_image(image)
    image = normalize_image(image)
    return image

def preprocess_folder(folder_path):
    print(f"processing the images in: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(folder_path, filename)
            image = cv2.imread(img_path)
            resized = resize_image(image)
            denoised = denoise_image(resized)
            edges = detect_edges(resized)
            print(f"processed image {filename}")
