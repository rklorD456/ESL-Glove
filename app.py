from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import numpy as np
import tensorflow as tf # Use tensorflow for the interpreter
import joblib
import logging
import requests

# Initialize the Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
socketio = SocketIO(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# --- Load TFLite model and allocate tensors ---
try:
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    # Get input and output tensor details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    app.logger.info("✅ TFLite model loaded successfully.")
except Exception as e:
    app.logger.error(f"❌ Error loading TFLite model: {e}")
    interpreter = None

# Load the scaler
try:
    scaler = joblib.load("scaler.joblib")
    app.logger.info("✅ Scaler loaded successfully.")
except Exception as e:
    app.logger.error(f"❌ Error loading scaler: {e}")
    scaler = None


gesture_classes = ["dog", "ok", "bye", "love", "mother", "grandmother"] 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not interpreter or not scaler:
        return jsonify({'error': 'Model or scaler is not loaded'}), 500
    try:
        data = request.get_json()
        sensor_data = data.get('sensor_data', [])
        sensor_array = np.array(sensor_data)

        if sensor_array.shape != (750, 9):
            return jsonify({'error': f'Wrong shape {sensor_array.shape}'}), 400

        # --- Prediction using TFLite Interpreter ---
        
        # 1. Scale and prepare the input data
        scaled_data = scaler.transform(sensor_array)
        # Reshape and ensure the data type matches the model's input
        input_data = scaled_data.reshape(1, 750, 9).astype(np.float32)

        # 2. Set the input tensor
        interpreter.set_tensor(input_details[0]['index'], input_data)

        # 3. Run inference
        interpreter.invoke()

        # 4. Get the output tensor
        prediction = interpreter.get_tensor(output_details[0]['index'])[0]
        # --- End of TFLite Prediction ---

        gesture_index = int(np.argmax(prediction))
        gesture = gesture_classes[gesture_index]
        confidence = float(prediction[gesture_index])

        app.logger.info(f"🧠 Prediction: {gesture}, Confidence: {confidence:.2f}")

        socketio.emit('new_prediction', {'gesture': gesture, 'confidence': round(confidence * 100, 2)})
        
        return jsonify({"status": "success", "predicted_gesture": gesture})

    except Exception as e:
        app.logger.error(f"❌ An error occurred during prediction: {e}")
        return jsonify({"error": str(e)}), 500

# The /translate route remains exactly the same
@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text_to_translate = data.get('text')
    target_lang = data.get('target_lang')

    if not text_to_translate or not target_lang:
        return jsonify({'error': 'Missing text or target language'}), 400

    api_url = f"https://api.mymemory.translated.net/get?q={text_to_translate}&langpair=en|{target_lang}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        translation_data = response.json()
        translated_text = translation_data['responseData']['translatedText']
        return jsonify({'translated_text': translated_text})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.logger.info("Starting server... Open http://127.0.0.1:5000 in your browser.")
    # We remove debug=True for measuring speed, as it slows the server down.
    socketio.run(app, host='0.0.0.0', port=5000, debug= True, use_reloader=False)