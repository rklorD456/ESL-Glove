# 🧤 ESL Gesture Translation Glove

This project is a real-time Egyptien Sign Language (ASL) to speech and text translator. It uses a custom-built glove with flex and motion sensors to capture hand gestures. A deep learning model predicts the gesture, and a web application displays the results, builds sentences, and translates them into different languages.

---

## ✨ Features

- **Real-Time Gesture Prediction**  
  Captures sensor data from an ESP32 and predicts the corresponding ASL gesture in real-time.

- **Sentence Building**  
  Automatically constructs sentences from a sequence of gestures.

- **Live Translation**  
  Translates the constructed sentences into multiple languages (Arabic, French, Spanish, German) using a free translation API.

- **Text-to-Speech**  
  Speaks the predicted words and translations out loud.

- **Modern Web Interface**  
  A clean, responsive user interface built with Flask and JavaScript.

- **Feature-Rich UI**  
  Includes a prediction history, visual confidence bar, live status indicator, and a dark mode toggle.

- **Optimized AI Model**  
  Uses TensorFlow Lite (.tflite) for faster, more efficient predictions.

---

## 📂 Project Structure

```

asl-glove-translator/
├── static/
│   ├── css/
│   │   └── style.css         # Styles for the webpage
│   ├── js/
│   │   └── script.js         # JavaScript for frontend logic
│   └── images/
│       ├── dog.png, ok.png, etc...
│       └── speaker.png
├── templates/
│   └── index.html            # Main HTML file for the UI
├── app.py                    # The main Flask web server
├── mock\_esp32.py             # Script to test the server with CSV files
├── model.tflite              # The final, optimized TFLite model
├── scaler.joblib             # The scaler for normalizing sensor data
└── README.md                 # This file

````

---

## 🚀 How to Use

Follow these steps to set up and run the project on your local machine.

### ✅ Prerequisites

- Python 3.8+
- An ESP32 board and the Arduino IDE
- A custom glove with 5 flex sensors and an IMU (like MPU6050)

---

### 1. Clone the Repository

```bash
git clone https://github.com/rklorD456/ESL-Glove.git
cd ESL-Glove
````

---

### 2. Install Python Libraries

```bash
pip install -r requirements.txt
```

> **Note on `requirements.txt`:**
> To create this file:
>
> ```bash
> pip freeze > requirements.txt
> ```
>
> Your file should contain:
> `flask`, `flask-socketio`, `eventlet`, `requests`, `tensorflow`, `numpy`, `joblib`, `scikit-learn`

---

### 3. Train Your Own Model (Optional)

* Place your gesture `.csv` files inside a `data/` folder.
* Run the training script from Google Colab to generate:

  * `asl_glove_model.h5`
  * `scaler.joblib`
* Move both files to the main project directory.

---

### 4. Convert the Model to TFLite

```bash
python convert_model.py
```

---

### 5. Run the Web Application

```bash
python app.py
```

* Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🤖 Hardware Setup (ESP32)

> ⚠️ `esp32_client.ino` sketch is not included in this repo.

### Configuration

* **Configure Wi-Fi**
  Update the `ssid` and `password` variables with your Wi-Fi network details.

* **Set Server IP**
  Update the `serverUrl` to your computer’s IP address, e.g.
  `http://192.168.1.10:5000/predict`

* **Implement Sensor Logic**
  Replace the `read_sensor_values()` function with logic to read 9 sensor values:

  * 5 from flex sensors
  * 4 from IMU

* **Upload**
  Upload the sketch to your ESP32. Once powered, it will stream data to the server.

---

## 🛠️ Technology Stack

* **Backend**: Python, Flask, Flask-SocketIO
* **AI Model**: TensorFlow, Keras, Scikit-learn
* **Frontend**: HTML5, CSS3, JavaScript
* **Hardware**: ESP32, Flex Sensors, MPU6050
* **Translation API**: [MyMemory](https://mymemory.translated.net/)

---

## 📄 License

This project is licensed under the **MIT License**.
See the [LICENSE](./LICENSE) file for details.
