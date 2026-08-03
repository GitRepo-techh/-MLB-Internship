import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.datasets import fashion_mnist

# Step 1: Load the dataset
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

# Step 2: Explore the dataset
print("Training data shape:", x_train.shape)
print("Training labels shape:", y_train.shape)
print("Test data shape:", x_test.shape)
print("Test labels shape:", y_test.shape)
print("Unique labels:", np.unique(y_train))

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat','Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# Step 3: Show a few sample images
plt.figure(figsize=(10, 5))
for i in range(10):
    plt.subplot(2, 5, i+1)
    plt.imshow(x_train[i], cmap='gray')
    plt.title(class_names[y_train[i]])
    plt.axis('off')
plt.tight_layout()
plt.savefig('sample_images.png')
plt.show()




# Step 4: Normalize pixel values (0-255 -> 0-1)
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# Step 5: Build the ANN
model = keras.Sequential([
    layers.Input(shape=(28, 28)),
    layers.Flatten(),                          # Flatten 28x28 image into 784-length vector
    layers.Dense(128, activation='relu'),       # Hidden layer
    layers.Dense(10, activation='softmax')      # Output layer: 10 classes
])

model.summary()

# Step 6: Compile the model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)


# Step 7: Train the model
history = model.fit(
    x_train, y_train,
    epochs=10,
    validation_split=0.2,
    verbose=1
)

# Step 8: Evaluate on test data
test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
print(f"\nTest Accuracy: {test_accuracy:.4f}")
print(f"Test Loss: {test_loss:.4f}")