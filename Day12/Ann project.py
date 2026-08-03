from tensorflow import keras
from tensorflow.keras import layers

model = keras.Sequential([
    layers.Input(shape=(784,)),             # Input layer: e.g. 28x28 flattened image = 784 features
    layers.Dense(128, activation='sigmoid'),   # Hidden layer: 128 neurons
    layers.Dense(10, activation='softmax')  # Output layer: 10 classes 
])

model.summary()
