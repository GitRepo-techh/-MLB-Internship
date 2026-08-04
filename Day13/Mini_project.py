import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras import layers, models
from sklearn.metrics import confusion_matrix

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# -------------------- Load & preproces --------------------
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0
x_train = x_train.reshape(-1, 28, 28, 1)
x_test = x_test.reshape(-1, 28, 28, 1)

print("Train shape:", x_train.shape, "Test shape:", x_test.shape)

# -------------------- Display sample images --------------------
plt.figure(figsize=(10, 5))
for i in range(10):
    plt.subplot(2, 5, i + 1)
    plt.imshow(x_train[i].reshape(28, 28), cmap='gray')
    plt.title(class_names[y_train[i]])
    plt.axis('off')
plt.tight_layout()
plt.savefig('mp_sample_images.png')
plt.close()

# -------------------- Build the CNN --------------------
model = models.Sequential([
    layers.Input(shape=(28, 28, 1)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# -------------------- Train --------------------
history = model.fit(
    x_train, y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2
)

model.save('mp_fashion_mnist_cnn.keras')

# -------------------- Evaluate --------------------
train_loss, train_acc = model.evaluate(x_train, y_train, verbose=0)
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\nTraining Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")
print(f"Test Loss: {test_loss:.4f}")

# -------------------- Training/validation accuracy curves --------------------
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training vs Validation Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training vs Validation Loss')
plt.legend()

plt.tight_layout()
plt.savefig('mp_accuracy_loss_curves.png')
plt.close()

# -------------------- Predictions on full test set --------------------
predictions = model.predict(x_test)
predicted_labels = np.argmax(predictions, axis=1)

# -------------------- Confusion matrix --------------------
cm = confusion_matrix(y_test, predicted_labels)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.savefig('mp_confusion_matrix.png')
plt.close()

# -------------------- Correct vs incorrect predictions --------------------
correct_idx = np.where(predicted_labels == y_test)[0]
incorrect_idx = np.where(predicted_labels != y_test)[0]

# 10 correctly classified images
plt.figure(figsize=(12, 6))
for i, idx in enumerate(correct_idx[:10]):
    plt.subplot(2, 5, i + 1)
    plt.imshow(x_test[idx].reshape(28, 28), cmap='gray')
    plt.title(f"Pred: {class_names[predicted_labels[idx]]}\nTrue: {class_names[y_test[idx]]}",
               color='green', fontsize=8)
    plt.axis('off')
plt.tight_layout()
plt.savefig('mp_correct_predictions.png')
plt.close()

# 10 incorrectly classified images
plt.figure(figsize=(12, 6))
for i, idx in enumerate(incorrect_idx[:10]):
    plt.subplot(2, 5, i + 1)
    plt.imshow(x_test[idx].reshape(28, 28), cmap='gray')
    plt.title(f"Pred: {class_names[predicted_labels[idx]]}\nTrue: {class_names[y_test[idx]]}",
               color='red', fontsize=8)
    plt.axis('off')
plt.tight_layout()
plt.savefig('mp_incorrect_predictions.png')
plt.close()

print(f"\nCorrectly classified: {len(correct_idx)} / {len(y_test)}")
print(f"Incorrectly classified: {len(incorrect_idx)} / {len(y_test)}")
print("\nAll plots saved: mp_sample_images.png, mp_accuracy_loss_curves.png,")
print("mp_confusion_matrix.png, mp_correct_predictions.png, mp_incorrect_predictions.png")