from tensorflow import keras
from tensorflow.keras import layers

activations = ['relu', 'sigmoid', 'tanh']

for act in activations:

    print(f"Activation: {act}")

    
    model = keras.Sequential([
        layers.Input(shape=(784,)),
        layers.Dense(128, activation=act),
        layers.Dense(10, activation='softmax')
    ])
    model.summary()