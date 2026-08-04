# practice2_build_cnn.py

import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras import layers, models

# Load and normalize (same as Practice 1)
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# CNNs expect a channel dimension: (28, 28) -> (28, 28, 1)
x_train = x_train.reshape(-1, 28, 28, 1)
x_test = x_test.reshape(-1, 28, 28, 1)

print("Reshaped training data:", x_train.shape)

# Build the CNN model
model = models.Sequential([
    layers.Input(shape=(28, 28, 1)),

    # Convolution layer: 32 filters, 3x3 kernel, ReLU activation
    layers.Conv2D(32, (3, 3), activation='relu'),

    # Max pooling layer: shrinks feature maps by taking max in 2x2 windows
    layers.MaxPooling2D((2, 2)),

    # A second conv+pool block to learn deeper features
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    # Flatten layer: turns 2D feature maps into a 1D vector
    layers.Flatten(),

    # Dense (fully connected) layer
    layers.Dense(128, activation='relu'),

    # Output layer: 10 classes, softmax gives a probability per class
    layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',  # labels are integers, not one-hot
    metrics=['accuracy']
)

model.summary()

# Train the model
history = model.fit(
    x_train, y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2   # 20% of training data held out for validation
)

# Save the trained model so Practice 3 can load it without retraining
model.save('fashion_mnist_cnn.keras')
print("\nModel saved as fashion_mnist_cnn.keras")