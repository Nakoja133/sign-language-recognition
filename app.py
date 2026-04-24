import cv2
import pickle
import numpy as np
import streamlit as st
import mediapipe as mp
import tensorflow as tf
from translator import get_twi_for_word, get_twi_translation, twi_to_phonetic
import time
import tempfile
import os
import urllib.request
from gtts import gTTS
from collections import Counter

# ── Auto-download hand landmarker ─────────────────────────────
if not os.path.exists("hand_landmarker.task"):
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        "hand_landmarker.task"
    )

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="SignTwi",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

:root {
    --gold:       #FFB800;
    --green:      #00C875;
    --red:        #FF3B5C;
    --bg:         #050508;
    --glass:      rgba(255,255,255,0.03);
    --glass-hov:  rgba(255,255,255,0.06);
    --border:     rgba(255,255,255,0.07);
    --border-hov: rgba(255,184,0,0.3);
    --text:       #F2F2F5;
    --muted:      #4A4A5A;
    --muted2:     #2A2A35;
}
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

.bg-mesh {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 10% 20%, rgba(255,184,0,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(0,200,117,0.04) 0%, transparent 60%);
}
.kente-bar {
    height: 5px;
    background: repeating-linear-gradient(
        90deg,
        #FFB800 0px,  #FFB800 20px,
        #DC143C 20px, #DC143C 40px,
        #00C875 40px, #00C875 60px,
        #FFB800 60px, #FFB800 80px,
        #050508 80px, #050508 100px
    );
    opacity: 0.8;
}
.kente-bar.thin {
    height: 2px; margin: 1.5rem 0; opacity: 0.3;
    background: repeating-linear-gradient(
        90deg,
        #FFB800 0px,  #FFB800 20px,
        #DC143C 20px, #DC143C 40px,
        #00C875 40px, #00C875 60px,
        #050508 60px, #050508 80px
    );
}
.app-wrapper {
    padding: 0 2.5rem 3rem;
    position: relative; z-index: 1;
    max-width: 1300px; margin: 0 auto;
}
.hero-section {
    padding: 1.5rem 0 1rem;
    display: flex; align-items: center;
    justify-content: space-between; gap: 2rem;
}
.hero-eyebrow {
    display: inline-flex; align-items: center;
    background: rgba(255,184,0,0.08);
    border: 1px solid rgba(255,184,0,0.2);
    border-radius: 100px; padding: 5px 14px;
    font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--gold); margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Unbounded', sans-serif;
    font-size: 3.5rem; font-weight: 900;
    line-height: 1.0; margin: 0 0 0.8rem;
}
.hero-title .twi {
    background: linear-gradient(135deg, #FFB800 0%, #FF8C00 50%, #00C875 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    color: var(--muted); font-size: 0.9rem;
    font-weight: 300; max-width: 420px; line-height: 1.6;
}
.hero-right { display: flex; flex-direction: column; gap: 0.6rem; }
.stat-pill {
    display: flex; align-items: center; gap: 0.8rem;
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 12px; padding: 0.8rem 1.2rem;
    transition: all 0.3s ease;
}
.stat-pill:hover {
    background: var(--glass-hov); border-color: var(--border-hov);
    transform: translateX(-4px);
}
.stat-icon { font-size: 1.3rem; }
.stat-val {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.1rem; font-weight: 700;
    color: var(--gold); line-height: 1.1;
}
.stat-desc { font-size: 0.7rem; color: var(--muted); }

.stTabs [data-baseweb="tab-list"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important; padding: 5px !important; gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 10px !important;
    color: var(--muted) !important; font-weight: 500 !important;
    font-size: 0.9rem !important; padding: 0.6rem 1.8rem !important;
    border: none !important; transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important; background: var(--glass-hov) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FFB800, #FF8C00) !important;
    color: #000 !important; font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(255,184,0,0.3) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

.gcard {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 18px; padding: 1.4rem 1.6rem; margin-bottom: 0.8rem;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.gcard::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,184,0,0.2), transparent);
}
.gcard:hover {
    background: var(--glass-hov); border-color: rgba(255,184,0,0.15);
    transform: translateY(-2px);
}
.gcard.gold-accent  { border-left: 3px solid var(--gold); }
.gcard.green-accent { border-left: 3px solid var(--green); }

.card-label {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.18em; color: var(--muted); margin-bottom: 0.4rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.card-label::before {
    content: ''; display: inline-block;
    width: 6px; height: 6px; border-radius: 50%; background: var(--gold);
}
.card-label.green::before { background: var(--green); }
.card-label.muted::before { background: var(--muted); }

.translation-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 1rem; margin: 1rem 0;
}
.trans-box {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.4rem; transition: all 0.3s;
}
.trans-box:hover { transform: translateY(-3px); }
.trans-box.english { border-top: 2px solid rgba(255,184,0,0.4); }
.trans-box.twi     {
    border-top: 2px solid rgba(0,200,117,0.4);
    background: rgba(0,200,117,0.03);
}
.trans-flag { font-size: 1.5rem; margin-bottom: 0.4rem; }
.trans-lang {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.15em; color: var(--muted); margin-bottom: 0.5rem;
}
.trans-text {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    color: var(--text); line-height: 1.3;
}
.trans-text.twi-text { color: var(--green); }

.audio-section {
    background: linear-gradient(135deg, rgba(255,184,0,0.05), rgba(0,200,117,0.05));
    border: 1px solid rgba(255,184,0,0.15); border-radius: 16px;
    padding: 1.2rem 1.5rem; margin-top: 1rem;
}
.audio-title {
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.15em; color: var(--gold); margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.audio-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(255,184,0,0.2), transparent);
}
audio { width: 100%; border-radius: 10px; }

.stButton > button {
    background: linear-gradient(135deg, #FFB800 0%, #FF8C00 100%) !important;
    color: #000 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.6rem 1rem !important; width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(255,184,0,0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(255,184,0,0.4) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #00C875 0%, #00A85E 100%) !important;
    color: #fff !important; font-weight: 700 !important;
    border: none !important; border-radius: 12px !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(0,200,117,0.2) !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover { transform: translateY(-3px) !important; }

.stProgress > div > div > div {
    background: linear-gradient(90deg, #FFB800, #FF8C00, #00C875) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: var(--muted2) !important; border-radius: 100px !important;
}

[data-testid="stFileUploadDropzone"] {
    background: var(--glass) !important;
    border: 2px dashed var(--muted2) !important;
    border-radius: 16px !important; transition: all 0.3s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(255,184,0,0.3) !important;
}

.signs-flow { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 0.5rem; }
.sign-chip {
    background: rgba(255,184,0,0.08); border: 1px solid rgba(255,184,0,0.2);
    border-radius: 8px; padding: 4px 12px;
    font-family: 'Unbounded', sans-serif; font-size: 0.8rem; color: var(--gold);
}

.live-sign {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.2rem; margin-bottom: 0.6rem;
    text-align: center; transition: all 0.3s;
}
.live-sign.active {
    border-color: rgba(255,184,0,0.4);
    background: rgba(255,184,0,0.05);
    box-shadow: 0 0 20px rgba(255,184,0,0.1);
}
.live-sign-letter {
    font-family: 'Unbounded', sans-serif;
    font-size: 3rem; font-weight: 900;
    color: var(--gold); line-height: 1;
}
.live-sign-conf { font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem; }

.word-builder {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 16px; padding: 1rem 1.2rem; margin-bottom: 0.6rem;
    min-height: 60px; display: flex; align-items: center;
    gap: 0.5rem; flex-wrap: wrap;
}
.word-letter {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.2rem; font-weight: 700; color: var(--text);
    background: rgba(255,255,255,0.06); border: 1px solid var(--border);
    border-radius: 6px; padding: 2px 8px;
}
.word-cursor {
    width: 2px; height: 24px; background: var(--gold);
    border-radius: 2px; animation: blink 1s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.sentence-area {
    background: rgba(0,200,117,0.04); border: 1px solid rgba(0,200,117,0.15);
    border-radius: 14px; padding: 0.8rem 1.2rem; margin-bottom: 0.6rem;
    min-height: 48px; display: flex; align-items: center;
    gap: 0.5rem; flex-wrap: wrap;
}
.sentence-word {
    background: rgba(0,200,117,0.1); border: 1px solid rgba(0,200,117,0.2);
    border-radius: 8px; padding: 3px 10px;
    font-family: 'Unbounded', sans-serif; font-size: 0.85rem; color: var(--green);
}

.log-entry {
    display: flex; align-items: center; gap: 0.8rem;
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.6rem 1rem;
    margin-bottom: 0.3rem; font-size: 0.85rem;
}
.log-entry:hover { background: var(--glass-hov); }
.log-en  { color: var(--text); font-weight: 600; }
.log-arr { color: var(--muted); }
.log-twi { color: var(--green); font-style: italic; }

.cam-idle {
    background: var(--glass); border: 2px dashed var(--muted2);
    border-radius: 18px; padding: 6rem 2rem;
    text-align: center; transition: all 0.3s;
}
.cam-idle:hover { border-color: rgba(255,184,0,0.2); }
.cam-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
.cam-text { font-size: 0.95rem; color: var(--muted); font-weight: 300; }

.tip-box {
    background: rgba(255,184,0,0.04); border: 1px solid rgba(255,184,0,0.12);
    border-left: 3px solid var(--gold); border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem; margin-bottom: 1rem;
    font-size: 0.85rem; color: var(--muted); line-height: 1.8;
}
.tip-box b { color: var(--gold); }

.how-row { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.6rem; }
.how-step {
    width: 28px; height: 28px; background: rgba(255,184,0,0.1);
    border: 1px solid rgba(255,184,0,0.2); border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Unbounded', sans-serif; font-size: 0.7rem;
    font-weight: 700; color: var(--gold); flex-shrink: 0;
}
.how-text { font-size: 0.85rem; color: var(--muted); }
.how-text b { color: var(--text); }

.footer {
    text-align: center; padding: 2rem 0 1rem;
    color: var(--muted2); font-size: 0.8rem;
}
.footer span { color: var(--muted); }

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,184,0,0.2); }
    50%       { box-shadow: 0 0 0 8px rgba(255,184,0,0); }
}
.pulse { animation: pulse 2s infinite; }

@media (max-width: 768px) {
    .app-wrapper { padding: 0 1rem 2rem !important; }
    .hero-section { flex-direction: column !important; padding: 1rem 0 !important; }
    .hero-title { font-size: 2.2rem !important; }
    .hero-desc { max-width: 100% !important; }
    .hero-right {
        flex-direction: row !important;
        overflow-x: auto !important; width: 100% !important;
    }
    .stat-pill { min-width: 120px !important; }
    .translation-grid { grid-template-columns: 1fr !important; }
    .trans-text { font-size: 1.1rem !important; }
    .live-sign-letter { font-size: 2rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ── Audio ─────────────────────────────────────────────────────
def make_audio_bytes(text):
    try:
        phonetic = twi_to_phonetic(text)
        tts = gTTS(text=phonetic, lang='en', slow=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp = f.name
        tts.save(tmp)
        with open(tmp, 'rb') as f:
            data = f.read()
        os.unlink(tmp)
        return data
    except Exception as e:
        print(f"Audio error: {e}")
        return None

def play_local(text):
    try:
        phonetic = twi_to_phonetic(text)
        tts = gTTS(text=phonetic, lang='en', slow=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp = f.name
        tts.save(tmp)
        os.startfile(tmp)
    except Exception:
        pass


# ── Load model ─────────────────────────────────────────────────
@st.cache_resource
def load_model_and_classes():
    model = tf.keras.models.load_model("asl_model.keras")
    with open("classes.pkl", "rb") as f:
        classes = pickle.load(f)
    return model, classes

@st.cache_resource
def load_landmarker():
    BaseOptions           = mp.tasks.BaseOptions
    HandLandmarker        = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    VisionRunningMode     = mp.tasks.vision.RunningMode
    opts = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=1, min_hand_detection_confidence=0.3
    )
    return HandLandmarker.create_from_options(opts)

def draw_landmarks(frame, lms):
    h, w, _ = frame.shape
    conns = [
        (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)
    ]
    pts = [(int(lm.x*w), int(lm.y*h)) for lm in lms]
    for s, e in conns:
        cv2.line(frame, pts[s], pts[e], (0,200,117), 2)
    for pt in pts:
        cv2.circle(frame, pt, 6, (255,184,0), -1)
        cv2.circle(frame, pt, 6, (0,0,0), 1)
    return frame

def predict(frame, model, classes, landmarker, threshold):
    rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = landmarker.detect(mp_img)
    if results.hand_landmarks:
        lms = []
        for lm in results.hand_landmarks[0]:
            lms.extend([lm.x, lm.y, lm.z])
        preds = model.predict(np.array(lms).reshape(1,-1), verbose=0)
        conf  = float(np.max(preds))
        cls   = np.argmax(preds)
        if conf >= threshold:
            return classes[cls], conf, results.hand_landmarks[0]
    return None, 0.0, None

def process_video(path, model, classes, landmarker, threshold):
    cap      = cv2.VideoCapture(path)
    fps      = cap.get(cv2.CAP_PROP_FPS) or 30
    total    = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = max(1, int(total/fps))
    signs, last = [], None
    bar      = st.progress(0, text="🔍 Analysing signs...")
    preview  = st.empty()
    samples  = int(duration / 1.5)

    for i in range(samples):
        sec = i * 1.5 + 0.75
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if not ret: break
        sign, conf, lms = predict(frame, model, classes, landmarker, threshold)
        if sign and sign != "nothing" and sign != last:
            signs.append(sign); last = sign
            if lms: frame = draw_landmarks(frame, lms)
            cv2.putText(frame, f"{sign}  {conf:.0%}",
                (16,52), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255,184,0), 3)
            cv2.putText(frame, f"{sign}  {conf:.0%}",
                (16,52), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0,0,0), 1)
        frame_small = cv2.resize(frame, (320, 240))
        preview.image(cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB),
            channels="RGB", width=320,
            caption=f"Second {sec:.0f} of {duration}")
        bar.progress(min((i+1)/samples, 1.0),
            text=f"🔍 Frame {i+1} of {samples}...")

    cap.release()
    bar.progress(1.0, text="✅ Done!")
    return signs

def build_sentence(signs):
    if "space" not in signs:
        word = "".join([s for s in signs if s not in ["nothing","del","space"]])
        _, twi = get_twi_for_word(word)
        if "unavailable" in str(twi): twi = word
        return word, twi
    words, twis, cur = [], [], ""
    for s in signs:
        if s == "space":
            if cur:
                _, twi = get_twi_for_word(cur)
                if "unavailable" in str(twi): twi = cur
                words.append(cur); twis.append(twi); cur = ""
        elif s == "del": cur = cur[:-1]
        elif s != "nothing": cur += s
    if cur:
        _, twi = get_twi_for_word(cur)
        if "unavailable" in str(twi): twi = cur
        words.append(cur); twis.append(twi)
    return " ".join(words), " ".join(twis)


# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
defaults = {
    "log":            [],
    "word":           "",
    "sentence_words": [],
    "last_sign":      "",
    "last_time":      0.0,
    "pred_buffer":    [],
    "do_delete":      False,
    "do_clear":       False,
    "do_addword":     False,
    "do_translate":   False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="bg-mesh"></div>', unsafe_allow_html=True)
st.markdown('<div class="kente-bar"></div>', unsafe_allow_html=True)
st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <div class="hero-left">
    <div class="hero-eyebrow">🇬🇭 Ghana &nbsp;·&nbsp; ASL &nbsp;·&nbsp; Twi &nbsp;·&nbsp; AI</div>
    <div class="hero-title"><span>Sign</span><span class="twi">Twi</span></div>
    <div class="hero-desc">
        Real-time ASL recognition that translates to
        <b style="color:#FFB800;">Twi (Akan)</b> and speaks it aloud —
        bridging communication for Ghana's deaf community.
    </div>
  </div>
  <div class="hero-right">
    <div class="stat-pill">
        <div class="stat-icon">🎯</div>
        <div><div class="stat-val">98.4%</div><div class="stat-desc">Model Accuracy</div></div>
    </div>
    <div class="stat-pill">
        <div class="stat-icon">🤟</div>
        <div><div class="stat-val">29 Signs</div><div class="stat-desc">ASL Alphabet</div></div>
    </div>
    <div class="stat-pill">
        <div class="stat-icon">🗣️</div>
        <div><div class="stat-val">100+ Words</div><div class="stat-desc">Twi Dictionary</div></div>
    </div>
    <div class="stat-pill">
        <div class="stat-icon">⚡</div>
        <div><div class="stat-val">Real-Time</div><div class="stat-desc">Live Camera</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)

# Settings
sc1, sc2, sc3, sc4 = st.columns([3,1,1,1])
with sc1:
    threshold = st.slider("🎚️ Detection Confidence", 0.5, 1.0, 0.8, 0.05)
with sc2:
    st.markdown("<br>", unsafe_allow_html=True)
    show_lms = st.checkbox("🖐️ Skeleton", value=True)
with sc3:
    st.markdown("<br>", unsafe_allow_html=True)
    speak_audio = st.checkbox("🔊 Auto-Speak", value=True)
with sc4:
    st.markdown("""<br>
    <div style="background:rgba(255,184,0,0.08);border:1px solid rgba(255,184,0,0.2);
    border-radius:10px;padding:0.45rem 0.8rem;text-align:center;
    font-size:0.75rem;color:#FFB800;font-weight:600;">● LIVE</div>
    """, unsafe_allow_html=True)

st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)

model, classes = load_model_and_classes()
landmarker     = load_landmarker()

tab1, tab2, tab3 = st.tabs([
    "📹  Video Upload",
    "📷  Live Camera",
    "📖  How To Use"
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — VIDEO UPLOAD
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="tip-box">
    <b>How it works:</b> Upload a video of ASL signing. The app reads each sign,
    builds the sentence, translates to <b>Twi</b>, and generates a voice note.
    Hold each sign for <b>2–3 seconds</b> with good lighting for best results.
    </div>
    """, unsafe_allow_html=True)

    video_file = st.file_uploader(
        "Drop your video here — MP4, MOV, AVI supported",
        type=["mp4","avi","mov","mkv"]
    )

    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(video_file.read())
            vpath = tmp.name

        vc, bc = st.columns([3,1])
        with vc:
            st.video(video_file)
        with bc:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            go = st.button("🚀 Analyse & Translate")

        if go:
            st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)
            signs = process_video(vpath, model, classes, landmarker, threshold)
            st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)

            if not signs:
                st.error("⚠️ No signs detected. Ensure hand is clearly visible.")
            else:
                chips = "".join([
                    f'<span class="sign-chip">{s}</span>' for s in signs
                ])
                st.markdown(f"""
                <div class="gcard">
                    <div class="card-label muted">Signs Detected ({len(signs)} total)</div>
                    <div class="signs-flow">{chips}</div>
                </div>
                """, unsafe_allow_html=True)

                english, twi = build_sentence(signs)
                st.markdown(f"""
                <div class="translation-grid">
                    <div class="trans-box english">
                        <div class="trans-flag">🇺🇸</div>
                        <div class="trans-lang">English</div>
                        <div class="trans-text">{english or "—"}</div>
                    </div>
                    <div class="trans-box twi">
                        <div class="trans-flag">🇬🇭</div>
                        <div class="trans-lang">Twi (Akan)</div>
                        <div class="trans-text twi-text">{twi or "—"}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if twi:
                    st.markdown("""
                    <div class="audio-section">
                        <div class="audio-title">🔊 Twi Voice Note</div>
                    """, unsafe_allow_html=True)
                    audio_bytes = make_audio_bytes(twi)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.download_button(
                            "⬇️ Download Twi Voice Note (.mp3)",
                            data=audio_bytes,
                            file_name="signtwi_output.mp3",
                            mime="audio/mp3"
                        )
                        if speak_audio:
                            try: play_local(twi)
                            except Exception: pass
                    else:
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.warning("Audio failed — check internet connection.")
        try:
            os.unlink(vpath)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
# TAB 2 — LIVE CAMERA
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="tip-box">
    <b>Step by step:</b><br>
    1️⃣ Click <b>▶ Start Camera</b> to turn on<br>
    2️⃣ Sign letters — auto-detected and added to word every 1.5 seconds<br>
    3️⃣ Click <b>← Delete</b> to remove a wrong letter<br>
    4️⃣ Click <b>+ Add Word</b> when you finish a word<br>
    5️⃣ Click <b>🇬🇭 Translate</b> to get Twi translation + audio<br>
    6️⃣ Click <b>⏹ Stop Camera</b> to turn off
    </div>
    """, unsafe_allow_html=True)

    cam_col, res_col = st.columns([3, 2])

    with cam_col:
        # Two buttons — Start and Stop (no toggle, no flicker)
        btn_start, btn_stop = st.columns(2)
        with btn_start:
            if st.button("▶ Start Camera", key="start_cam"):
                st.session_state.camera_on = True
        with btn_stop:
            if st.button("⏹ Stop Camera", key="stop_cam"):
                st.session_state.camera_on = False

        frame_placeholder = st.empty()

    with res_col:
        st.markdown(
            '<div class="card-label" style="margin-bottom:0.4rem;">Current Detection</div>',
            unsafe_allow_html=True
        )
        sign_ph = st.empty()

        st.markdown(
            '<div class="card-label" style="margin:0.6rem 0 0.4rem;">Word Being Built</div>',
            unsafe_allow_html=True
        )
        word_ph = st.empty()

        st.markdown(
            '<div class="card-label" style="margin:0.6rem 0 0.4rem;">Sentence So Far</div>',
            unsafe_allow_html=True
        )
        sent_ph = st.empty()

        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("← Delete",     key="del_btn"):
                st.session_state.do_delete    = True
        with b2:
            if st.button("✕ Clear All",  key="clr_btn"):
                st.session_state.do_clear     = True
        with b3:
            if st.button("+ Add Word",   key="add_btn"):
                st.session_state.do_addword   = True
        with b4:
            if st.button("🇬🇭 Translate", key="trans_btn"):
                st.session_state.do_translate = True

        st.markdown(
            '<div class="card-label" style="margin:0.6rem 0 0.4rem;">Translation Result</div>',
            unsafe_allow_html=True
        )
        result_ph = st.empty()

        st.markdown(
            '<div class="card-label" style="margin:0.6rem 0 0.4rem;">Session Log</div>',
            unsafe_allow_html=True
        )
        log_ph = st.empty()

    # Ensure camera_on exists
    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False

    # ── Show log always ────────────────────────────────────────
    def render_log():
        if st.session_state.log:
            html = ""
            for w, t in st.session_state.log[-5:][::-1]:
                html += f"""
                <div class="log-entry">
                    <span class="log-en">{w}</span>
                    <span class="log-arr">→</span>
                    <span class="log-twi">{t}</span>
                </div>"""
            log_ph.markdown(html, unsafe_allow_html=True)

    def render_word():
        letters = "".join([
            f'<span class="word-letter">{c}</span>'
            for c in st.session_state.word
        ])
        word_ph.markdown(f"""
        <div class="word-builder">
            {letters if letters else
            '<span style="color:#2A2A35;font-size:0.85rem;">Sign letters to build a word...</span>'}
            <div class="word-cursor"></div>
        </div>""", unsafe_allow_html=True)

    def render_sentence():
        if st.session_state.sentence_words:
            whtml = "".join([
                f'<span class="sentence-word">{w}</span>'
                for w in st.session_state.sentence_words
            ])
            sent_ph.markdown(
                f'<div class="sentence-area">{whtml}</div>',
                unsafe_allow_html=True
            )
        else:
            sent_ph.markdown("""
            <div class="sentence-area">
                <span style="color:#2A2A35;font-size:0.85rem;">
                Add words to build a sentence...</span>
            </div>""", unsafe_allow_html=True)

    # ── Process button flags ───────────────────────────────────
    if st.session_state.do_delete:
        st.session_state.word     = st.session_state.word[:-1]
        st.session_state.do_delete = False

    if st.session_state.do_clear:
        st.session_state.word           = ""
        st.session_state.sentence_words = []
        st.session_state.pred_buffer    = []
        st.session_state.do_clear       = False

    if st.session_state.do_addword and st.session_state.word:
        st.session_state.sentence_words.append(st.session_state.word)
        st.session_state.word        = ""
        st.session_state.pred_buffer = []
        st.session_state.do_addword  = False

    if st.session_state.do_translate:
        if st.session_state.word:
            st.session_state.sentence_words.append(st.session_state.word)
            st.session_state.word        = ""
            st.session_state.pred_buffer = []

        if st.session_state.sentence_words:
            full_english = " ".join(st.session_state.sentence_words)
            
            # Try to translate the full sentence as a phrase first
            _, full_twi = get_twi_translation(full_english)
            
            # If full translation returns the same text (not found in dictionary), do word-by-word
            if full_twi == full_english:
                twi_words = []
                for w in st.session_state.sentence_words:
                    _, tw = get_twi_for_word(w)
                    if "unavailable" in str(tw): tw = w
                    twi_words.append(tw)
                full_twi = " ".join(twi_words)

            result_ph.markdown(f"""
            <div class="translation-grid">
                <div class="trans-box english">
                    <div class="trans-flag">🇺🇸</div>
                    <div class="trans-lang">English</div>
                    <div class="trans-text">{full_english}</div>
                </div>
                <div class="trans-box twi">
                    <div class="trans-flag">🇬🇭</div>
                    <div class="trans-lang">Twi (Akan)</div>
                    <div class="trans-text twi-text">{full_twi}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            audio_bytes = make_audio_bytes(full_twi)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                if speak_audio:
                    try: play_local(full_twi)
                    except Exception: pass

            st.session_state.log.append((full_english, full_twi))
            st.session_state.sentence_words = []

        st.session_state.do_translate = False

    render_log()
    render_word()
    render_sentence()

    # ── CAMERA LOOP ───────────────────────────────────────────
    if st.session_state.camera_on:
        # Try camera index 0, if fails try index 1
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            st.error("❌ Could not open webcam. Please check your camera connection.")
            st.session_state.camera_on = False
        else:
            fc = 0
            ls = None; lc = 0.0; ll = None

            while st.session_state.camera_on:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                fc   += 1

                # Predict every 5th frame
                if fc % 5 == 0:
                    raw, lc, ll = predict(
                        frame, model, classes, landmarker, threshold
                    )
                    if raw:
                        st.session_state.pred_buffer.append(raw)
                        st.session_state.pred_buffer = \
                            st.session_state.pred_buffer[-7:]
                        ls = Counter(
                            st.session_state.pred_buffer
                        ).most_common(1)[0][0]
                    else:
                        st.session_state.pred_buffer = []
                        ls = None

                # Draw
                if ll and show_lms:
                    frame = draw_landmarks(frame, ll)
                if ls:
                    cv2.putText(frame, f"{ls}  {lc:.0%}",
                        (16,52), cv2.FONT_HERSHEY_SIMPLEX,
                        1.4, (255,184,0), 3)
                    cv2.putText(frame, f"{ls}  {lc:.0%}",
                        (16,52), cv2.FONT_HERSHEY_SIMPLEX,
                        1.4, (0,0,0), 1)

                cv2.putText(frame,
                    f"Word: {st.session_state.word}",
                    (16,100), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0,200,117), 2)

                if st.session_state.sentence_words:
                    cv2.putText(frame,
                        " ".join(st.session_state.sentence_words),
                        (16,145), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (180,180,180), 2)

                # Show frame every 5th
                if fc % 5 == 0:
                    frame_placeholder.image(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                        channels="RGB", use_container_width=True
                    )

                # Auto-add letter every 1.5s
                now = time.time()
                if ls and fc % 5 == 0:
                    if ls == "space":
                        # Space sign: add current word to sentence (creates space between words)
                        if st.session_state.word:
                            st.session_state.sentence_words.append(st.session_state.word)
                            st.session_state.word = ""
                            st.session_state.pred_buffer = []
                            st.session_state.last_sign = ls
                            st.session_state.last_time = now
                    elif ls == "del":
                        # Delete sign: remove last letter from current word
                        if st.session_state.word:
                            st.session_state.word = st.session_state.word[:-1]
                            st.session_state.last_sign = ls
                            st.session_state.last_time = now
                    elif ls != "nothing":
                        # Regular letter: add to current word
                        if (ls != st.session_state.last_sign or
                                now - st.session_state.last_time > 1.5):
                            st.session_state.last_sign = ls
                            st.session_state.last_time = now
                            st.session_state.word += ls

                # Update result panels every 5th frame
                if fc % 5 == 0:
                    active = "active pulse" if ls else ""
                    sign_ph.markdown(f"""
                    <div class="live-sign {active}">
                        <div class="live-sign-letter">{ls or "·"}</div>
                        <div class="live-sign-conf">
                        {"Confidence: " + f"{lc:.0%}" if ls else "Show your hand to the camera"}
                        </div>
                    </div>""", unsafe_allow_html=True)

                    render_word()
                    render_sentence()

            cap.release()

    else:
        frame_placeholder.markdown("""
        <div class="cam-idle">
            <div class="cam-icon">📷</div>
            <div class="cam-text">Click <b style="color:#F2F2F5;">▶ Start Camera</b> to begin</div>
            <div style="margin-top:0.5rem;font-size:0.75rem;color:#2A2A35;">
            Make sure your webcam is connected</div>
        </div>""", unsafe_allow_html=True)
        sign_ph.markdown("""
        <div class="live-sign">
            <div class="live-sign-letter" style="color:#2A2A35;">·</div>
            <div class="live-sign-conf">Camera is off</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — HOW TO USE
# ══════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="gcard gold-accent">
            <div class="card-label">📹 Video Upload</div>
            <div style="margin-top:0.8rem;">
                <div class="how-row"><div class="how-step">1</div>
                    <div class="how-text">Upload a video of ASL signing</div></div>
                <div class="how-row"><div class="how-step">2</div>
                    <div class="how-text">Click <b>Analyse & Translate</b></div></div>
                <div class="how-row"><div class="how-step">3</div>
                    <div class="how-text">View detected signs and <b>English sentence</b></div></div>
                <div class="how-row"><div class="how-step">4</div>
                    <div class="how-text">Read the <b>Twi translation</b> and play audio</div></div>
                <div class="how-row"><div class="how-step">5</div>
                    <div class="how-text">Download the <b>MP3 voice note</b></div></div>
            </div>
        </div>
        <div class="gcard" style="margin-top:0.8rem;">
            <div class="card-label muted">💡 Tips for Best Results</div>
            <div style="margin-top:0.6rem;font-size:0.85rem;color:#4A4A5A;line-height:1.9;">
                ✓ &nbsp;Hold each sign for <b style="color:#F2F2F5;">2–3 seconds</b><br>
                ✓ &nbsp;Use <b style="color:#F2F2F5;">good lighting</b><br>
                ✓ &nbsp;<b style="color:#F2F2F5;">Plain background</b> works best<br>
                ✓ &nbsp;Keep hand <b style="color:#F2F2F5;">fully visible</b><br>
                ✓ &nbsp;Face camera <b style="color:#F2F2F5;">directly</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="gcard green-accent">
            <div class="card-label green">📷 Live Camera — Sentence Builder</div>
            <div style="margin-top:0.8rem;">
                <div class="how-row"><div class="how-step">1</div>
                    <div class="how-text">Click <b>▶ Start Camera</b></div></div>
                <div class="how-row"><div class="how-step">2</div>
                    <div class="how-text">Sign letters — auto-added every 1.5s</div></div>
                <div class="how-row"><div class="how-step">3</div>
                    <div class="how-text">Click <b>← Delete</b> for wrong letters</div></div>
                <div class="how-row"><div class="how-step">4</div>
                    <div class="how-text">Click <b>+ Add Word</b> to add to sentence</div></div>
                <div class="how-row"><div class="how-step">5</div>
                    <div class="how-text">Click <b>🇬🇭 Translate</b> for Twi + audio</div></div>
            </div>
        </div>
        <div class="gcard" style="margin-top:0.8rem;">
            <div class="card-label muted">🔤 Example — Building a Sentence</div>
            <div style="margin-top:0.6rem;font-size:0.85rem;color:#4A4A5A;line-height:2;">
                Sign <b style="color:#FFB800;">G-O-O-D</b>
                → click <b style="color:#F2F2F5;">+ Add Word</b><br>
                Sign <b style="color:#FFB800;">M-O-R-N-I-N-G</b>
                → click <b style="color:#F2F2F5;">+ Add Word</b><br>
                Click <b style="color:#00C875;">🇬🇭 Translate</b><br>
                Result: <b style="color:#00C875;">"GOOD MORNING" → "Maakye"</b> 🔊
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────
st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <span style="font-family:'Unbounded',sans-serif;font-size:0.9rem;
    color:#FFB800;font-weight:700;">SignTwi</span><br>
    <span>Built with MediaPipe &nbsp;·&nbsp; TensorFlow &nbsp;·&nbsp; Streamlit</span><br>
    <span>🇬🇭 Made for Ghana &nbsp;·&nbsp; Bridging ASL and Twi for the deaf community</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
