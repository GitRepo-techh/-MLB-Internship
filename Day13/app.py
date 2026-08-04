import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist

st.set_page_config(page_title="Fashion MNIST Classifier", page_icon="👗", layout="centered")

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# -------------------- Custom CSS: fonts, colors, layout --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Space+Grotesk:wght@400;500;600&display=swap');

.stApp {
    background-color: #14141A;
    color: #F3F1EC;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #F3F1EC !important;
}

body, p, div, span, label {
    font-family: 'Space Grotesk', sans-serif;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 48px;
    font-weight: 700;
    color: #F3F1EC;
    margin-bottom: 0px;
}

.hero-sub {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    color: #C9A876;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 32px;
}

.result-card {
    background-color: #1E1E26;
    border: 1px solid #2E2E38;
    border-radius: 12px;
    padding: 28px;
    margin-top: 24px;
}

.prediction-label {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: #8B5CF6;
    margin-bottom: 4px;
}

.confidence-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    color: #C9A876;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.stButton>button {
    background-color: #8B5CF6;
    color: #14141A;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    border-radius: 8px;
    border: none;
    padding: 10px 24px;
    transition: background-color 0.2s ease, transform 0.15s ease;
}

.stButton>button:hover {
    background-color: #A78BFA;
    color: #14141A;
    transform: translateY(-2px);
}

@media (prefers-reduced-motion: no-preference) {

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    .hero-title, .hero-sub {
        animation: fadeIn 0.6s ease-out;
    }

    .result-card {
        animation: slideUp 0.5s ease-out;
    }

    .prediction-label {
        animation: pulse 2s ease-in-out infinite;
    }
}
</style>
""", unsafe_allow_html=True)

# -------------------- Header --------------------
st.markdown('<div class="hero-title">The Runway Recognizer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">CNN-powered fashion classification</div>', unsafe_allow_html=True)

# -------------------- Load model + data (cached) --------------------
@st.cache_resource
def load_trained_model():
    return tf.keras.models.load_model('mp_fashion_mnist_cnn.keras')

@st.cache_data
def load_test_data():
    (_, _), (x_test, y_test) = fashion_mnist.load_data()
    return x_test, y_test

model = load_trained_model()
x_test, y_test = load_test_data()

# -------------------- Image selection --------------------
st.write("Pick a test image index (0–9999) to classify:")
idx = st.slider("Image index", 0, len(x_test) - 1, 0)

image = x_test[idx]
true_label = class_names[y_test[idx]]

col1, col2 = st.columns([1, 1.5])

with col1:
    st.image(Image.fromarray(image).resize((150, 150)), caption=f"True label: {true_label}")

with col2:
    if st.button("Classify"):
        input_img = image.astype('float32') / 255.0
        input_img = input_img.reshape(1, 28, 28, 1)

        prediction = model.predict(input_img)
        predicted_label = class_names[np.argmax(prediction)]
        confidence = float(np.max(prediction)) * 100

        st.markdown(f"""
        <div class="result-card">
            <div class="confidence-text">Predicted class</div>
            <div class="prediction-label">{predicted_label}</div>
            <div class="confidence-text">Confidence: {confidence:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(int(confidence))