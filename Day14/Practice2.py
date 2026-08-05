import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# Image settings
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Load training dataset
train_dataset = tf.keras.utils.image_dataset_from_directory(
    "archive/training_set/training_set",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True
)

# Load validation dataset
validation_dataset = tf.keras.utils.image_dataset_from_directory(
    "archive/test_set/test_set",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

# Preprocessing function
def preprocess(image, label):
    image = preprocess_input(image)
    return image, label

# Improve performance
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

# Check one batch
for images, labels in train_dataset.take(1):
    print("Image Batch Shape:", images.shape)
    print("Label Batch Shape:", labels.shape)