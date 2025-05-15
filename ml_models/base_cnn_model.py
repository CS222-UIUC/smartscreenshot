"""
ml_models/base_cnn_model.py

Define + train a basic CNN classifier from scratch (w/o any pretrained skeleton).
We save the trained weights to `baseline_model.h5`.
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def build_baseline_model(num_classes=5):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),

        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),

        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),

        Flatten(),
        Dropout(0.5),
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_baseline_model(train_dir, val_dir, model_save_path="baseline_model.h5", num_classes=5, epochs=5):
    datagen = ImageDataGenerator(rescale=1./255)
    train_gen = datagen.flow_from_directory(train_dir, target_size=(224, 224), class_mode='categorical')
    val_gen = datagen.flow_from_directory(val_dir, target_size=(224, 224), class_mode='categorical')

    model = build_baseline_model(num_classes)
    model.fit(train_gen, validation_data=val_gen, epochs=epochs)
    model.save(model_save_path)
    return model

if __name__ == "__main__":
    print("In order to train this baseline CNN, call train_baseline_model(train_dir, val_dir)")
