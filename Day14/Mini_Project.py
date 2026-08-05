import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import matplotlib.pyplot as plt
import numpy as np


IMG_SIZE = (224, 224)
BATCH_SIZE = 32



train_dataset = tf.keras.utils.image_dataset_from_directory(
    "archive/training_set/training_set",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    "archive/test_set/test_set",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = train_dataset.class_names

# -----------------------------
# Preprocessing
# -----------------------------

def preprocess(image, label):
    image = preprocess_input(image)
    return image, label

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = (
    train_dataset
    .map(preprocess)
    .prefetch(AUTOTUNE)
)

validation_dataset = (
    validation_dataset
    .map(preprocess)
    .prefetch(AUTOTUNE)
)

# -----------------------------
# Data Augmentation
# -----------------------------

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
])

# -----------------------------
# Load MobileNetV2
# -----------------------------

base_model = MobileNetV2(
    input_shape=(224,224,3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False

# -----------------------------
# Build Model
# -----------------------------

model = models.Sequential([

    data_augmentation,

    base_model,

    layers.GlobalAveragePooling2D(),

    layers.Dropout(0.3),

    layers.Dense(128, activation="relu"),

    layers.Dropout(0.3),

    layers.Dense(1, activation="sigmoid")

])

# -----------------------------
# Compile Model
# -----------------------------

model.compile(

    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),

    loss="binary_crossentropy",

    metrics=["accuracy"]

)

model.summary()

# -----------------------------
# Train Model
# -----------------------------

history = model.fit(

    train_dataset,

    validation_data=validation_dataset,

    epochs=10

)

# -----------------------------
# Evaluate
# -----------------------------

loss, accuracy = model.evaluate(validation_dataset)

print(f"\nValidation Accuracy : {accuracy*100:.2f}%")
print(f"Validation Loss     : {loss:.4f}")

# -----------------------------
# Plot Accuracy
# -----------------------------

plt.figure(figsize=(8,5))

plt.plot(history.history["accuracy"], label="Training Accuracy")

plt.plot(history.history["val_accuracy"], label="Validation Accuracy")

plt.xlabel("Epoch")

plt.ylabel("Accuracy")

plt.legend()

plt.grid(True)

plt.savefig("accuracy.png")

plt.show()

# -----------------------------
# Plot Loss
# -----------------------------

plt.figure(figsize=(8,5))

plt.plot(history.history["loss"], label="Training Loss")

plt.plot(history.history["val_loss"], label="Validation Loss")

plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.legend()

plt.grid(True)

plt.savefig("loss.png")

plt.show()

# -----------------------------
# Sample Predictions
# -----------------------------

plt.figure(figsize=(12,8))

for images, labels in validation_dataset.take(1):

    predictions = model.predict(images)

    predictions = (predictions > 0.5).astype(int)

    for i in range(6):

        plt.subplot(2,3,i+1)

        image = (images[i] + 1) / 2

        plt.imshow(image)

        predicted = class_names[int(predictions[i][0])]

        actual = class_names[int(labels[i])]

        plt.title(f"P:{predicted}\nA:{actual}")

        plt.axis("off")

plt.tight_layout()

plt.savefig("sample_predictions.png")

plt.show()