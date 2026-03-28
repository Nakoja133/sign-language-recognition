# 🤟 SignTwi — ASL Sign Language to Twi Translator

An AI-powered application that recognizes American Sign Language (ASL) 
and translates it into Twi (Akan) — one of Ghana's most spoken local languages.

## 🎯 Problem Statement
People with hearing disabilities in Ghana face communication barriers 
because most people don't know ASL. SignTwi bridges this gap by 
translating ASL signs into spoken Twi in real time.

## ✨ Features
- 📷 **Live Webcam Recognition** — Sign letters in real time
- 📹 **Video Upload** — Upload a sign language video for analysis  
- 🔤 **Word Building** — Spell words letter by letter
- 🇬🇭 **Twi Translation** — 100+ English words translated to Twi
- 🔊 **Audio Output** — Speaks the Twi translation aloud
- ⬇️ **Voice Note Download** — Download the Twi audio as MP3

## 🧠 How It Works
```
Webcam / Video Input
        ↓
MediaPipe Hand Landmark Detection
        ↓
Neural Network (98.4% accuracy)
        ↓
ASL Letter/Word Recognition
        ↓
English → Twi Dictionary Translation
        ↓
🔊 Twi Audio Output
```

## 🛠️ Tech Stack
| Tool | Purpose |
|---|---|
| Python 3.10 | Core language |
| MediaPipe | Hand landmark detection |
| TensorFlow / Keras | Sign recognition model |
| Streamlit | Web application UI |
| OpenCV | Webcam & video processing |
| gTTS | Text to speech audio |
| Google Translate API | Fallback translation |

## 📊 Model Performance
- **Test Accuracy:** 98.40%
- **Test Loss:** 0.0713
- **Dataset:** ASL Alphabet (87,000 images, 29 classes)
- **Architecture:** Dense Neural Network with BatchNormalization

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sign-language-recognition.git
cd sign-language-recognition
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download MediaPipe model
The hand landmarker model downloads automatically on first run.

### 5. Run the app
```bash
streamlit run app.py
```

## 📁 Project Structure
```
sign_language_app/
├── app.py                  # Main Streamlit application
├── train_model.py          # Model training script
├── data_preprocessing.py   # Dataset preprocessing
├── translator.py           # English → Twi translation
├── audio_output.py         # Text to speech
├── requirements.txt        # Dependencies
└── README.md
```

## 🎓 Limitations & Future Work
- Currently recognizes ASL alphabet (A-Z) — whole word signs require GPU training
- Twi TTS uses phonetic pronunciation (no native Twi TTS engine exists freely)
- Future: Train on WLASL dataset for whole-word recognition
- Future: Native Twi TTS model

## 🇬🇭 Made for Ghana
Built to help the deaf community in Ghana communicate with 
non-ASL speakers using their local language.