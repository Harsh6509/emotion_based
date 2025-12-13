# backend_flask.py (example)
import base64
from flask import Flask, render_template, request, jsonify
import numpy as np
import socket
import cv2
import io
from PIL import Image
from keras.models import load_model
YOUTUBE_API_KEY = "fill the yt api here"

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


# Example route that runs a function
@app.route('/process', methods=['POST'])
def process():
    user_input = request.form['text']  # take input from HTML form
    result = user_input.upper()        # example function logic
    return render_template('index.html', output=result)

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.get_json()
    image_data = data['image']

    # Decode base64 image
    img_bytes = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(img_bytes))
    image = image.resize((48, 48)).convert('L')  # grayscale
    img_array = np.array(image)
    img_array = np.expand_dims(img_array, axis=(0, -1)) / 255.0

    prediction = model.predict(img_array)
    emotion_label = labels[np.argmax(prediction)]

    return jsonify({'emotion': emotion_label})

@app.route("/recommend_songs", methods=["POST"])
def recommend_songs():
    import requests

    data = request.get_json()
    emotion = data.get("emotion", "").lower()
    lang = data.get("lang", "")
    singer = data.get("singer", "")
    mood = data.get("mood", "")

    # Build dynamic YouTube search query
    search_query = f"{emotion} {lang} {mood} {singer} songs"
    search_query = search_query.strip()

    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={search_query}"
        "&type=video&maxResults=15"
        f"&key={YOUTUBE_API_KEY}"
    )

    yt_response = requests.get(url).json()

    results = []

    if "items" in yt_response:
        for item in yt_response["items"]:
            video_id = item["id"]["videoId"]
            embed_url = f"https://www.youtube.com/embed/{video_id}"

            results.append({
                "embed_url": embed_url
            })

    return jsonify({"results": results})




model = load_model("model.h5")
labels = np.load("labels.npy")

# Add your mediapipe feature extraction here (same steps as your Streamlit code)
import mediapipe as mp
mp_holistic = mp.solutions.holistic
mp_hands = mp.solutions.hands
holis = mp_holistic.Holistic()
drawing = mp.solutions.drawing_utils

def preprocess_image_to_features(image_np):
    """
    image_np: RGB numpy array (H,W,3)
    returns: feature vector shaped (1, N) same as your Streamlit code
    """
    # replicate the landmark extraction that you used in the Streamlit app
    res = holis.process(cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
    lst = []
    if res.face_landmarks:
        for i in res.face_landmarks.landmark:
            lst.append(i.x - res.face_landmarks.landmark[1].x)
            lst.append(i.y - res.face_landmarks.landmark[1].y)

        if res.left_hand_landmarks:
            for i in res.left_hand_landmarks.landmark:
                lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
        else:
            lst.extend([0.0]*42)

        if res.right_hand_landmarks:
            for i in res.right_hand_landmarks.landmark:
                lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
        else:
            lst.extend([0.0]*42)

    else:
        # if face not found, return None
        return None

    return np.array(lst).reshape(1,-1)


@app.route("/predict", methods=["POST"])
def predict():
    print("📸 Received image for prediction")
    if "image" not in request.files:
        print("❌ No image found in request")
        return jsonify({"error": "no_image"}), 400

    file = request.files["image"]
    img = Image.open(io.BytesIO(file.read())).convert("RGB")
    image_np = np.array(img)
    print("✅ Image converted to numpy")

    features = preprocess_image_to_features(image_np)
    if features is None:
        print("⚠️ No face or landmarks detected")
        return jsonify({"error": "no_face_detected"}), 200

    preds = model.predict(features)
    label = labels[np.argmax(preds)]
    print(f"🎯 Predicted emotion: {label}")

    return jsonify({"emotion": str(label)})


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    free_port = s.getsockname()[1]
    s.close()
    print(f"Running on port {free_port}")
    app.run(debug=True, port=free_port)
