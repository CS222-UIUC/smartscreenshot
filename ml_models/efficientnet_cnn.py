"""
ml_models/cnn_model.py

Define + train a CNN classifier w/ EfficientNetB0.
saving to `trained_model.h5`.
"""

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def build_model(num_classes=5):
    base_model = EfficientNetB0(include_top=False, input_shape=(224, 224, 3), weights='imagenet')
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation='relu')(x)
    output = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(train_dir, val_dir, model_save_path="trained_model.h5", num_classes=5, epochs=3):
    datagen = ImageDataGenerator(rescale=1./255)
    train_gen = datagen.flow_from_directory(train_dir, target_size=(224, 224), class_mode='categorical')
    val_gen = datagen.flow_from_directory(val_dir, target_size=(224, 224), class_mode='categorical')

    model = build_model(num_classes)
    model.fit(train_gen, validation_data=val_gen, epochs=epochs)
    model.save(model_save_path)
    return model