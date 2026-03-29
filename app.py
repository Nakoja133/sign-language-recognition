import cv2
import pickle
import numpy as np
import streamlit as st
import mediapipe as mp
import tensorflow as tf
from translator import get_twi_for_word, get_twi_translation
import time
import tempfile
import os
import urllib.request
from gtts import gTTS

# ── Auto-download hand landmarker ─────────────────────────────
if not os.path.exists("hand_landmarker.task"):
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        "hand_landmarker.task"
    )

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="SignTwi — ASL to Twi",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
# PREMIUM CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

/* ── Variables ── */
:root {
    --gold:       #FFB800;
    --gold-dim:   #CC9200;
    --gold-glow:  rgba(255,184,0,0.15);
    --green:      #00C875;
    --green-glow: rgba(0,200,117,0.12);
    --red:        #FF3B5C;
    --bg:         #050508;
    --bg2:        #0A0A10;
    --glass:      rgba(255,255,255,0.03);
    --glass-hov:  rgba(255,255,255,0.06);
    --border:     rgba(255,255,255,0.07);
    --border-hov: rgba(255,184,0,0.3);
    --text:       #F2F2F5;
    --muted:      #4A4A5A;
    --muted2:     #2A2A35;
}

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] { display: none; }

/* ── Animated Background ── */
.bg-mesh {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 10% 20%, rgba(255,184,0,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(0,200,117,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 50% 50%, rgba(255,59,92,0.02) 0%, transparent 70%);
}

/* ── Kente Pattern ── */
.kente-bar {
    height: 5px;
    background: repeating-linear-gradient(
        90deg,
        #FFB800 0px, #FFB800 20px,
        #DC143C 20px, #DC143C 40px,
        #00C875 40px, #00C875 60px,
        #FFB800 60px, #FFB800 80px,
        #050508 80px, #050508 100px
    );
    opacity: 0.8;
}
.kente-bar.thin {
    height: 2px;
    margin: 1.5rem 0;
    opacity: 0.3;
}

/* ── Main Wrapper ── */
.app-wrapper {
    padding: 0 2.5rem 3rem;
    position: relative; z-index: 1;
    max-width: 1300px; margin: 0 auto;
}

/* ── Hero Section ── */
.hero-section {
    padding: 1.5rem 0 1rem;
    display: flex; align-items: center;
    justify-content: space-between;
    gap: 2rem;
}
.hero-left {}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(255,184,0,0.08);
    border: 1px solid rgba(255,184,0,0.2);
    border-radius: 100px; padding: 5px 14px;
    font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--gold); margin-bottom: 1rem;
    animation: fadeSlideUp 0.6s ease both;
}
.hero-title {
    font-family: 'Unbounded', sans-serif;
    font-size: 3.8rem; font-weight: 900;
    line-height: 1.0; margin: 0 0 0.8rem;
    animation: fadeSlideUp 0.7s ease both;
}
.hero-title .sign { color: var(--text); }
.hero-title .twi  {
    background: linear-gradient(135deg, #FFB800 0%, #FF8C00 50%, #00C875 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    color: var(--muted); font-size: 0.9rem; font-weight: 300;
    max-width: 420px; line-height: 1.6;
    animation: fadeSlideUp 0.8s ease both;
}
.hero-right {
    display: flex; flex-direction: column; gap: 0.6rem;
    animation: fadeSlideUp 0.9s ease both;
}
.stat-pill {
    display: flex; align-items: center; gap: 0.8rem;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 0.8rem 1.2rem;
    transition: all 0.3s ease;
}
.stat-pill:hover {
    background: var(--glass-hov);
    border-color: var(--border-hov);
    transform: translateX(-4px);
}
.stat-icon { font-size: 1.3rem; }
.stat-info {}
.stat-val {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.1rem; font-weight: 700;
    color: var(--gold); line-height: 1.1;
}
.stat-desc { font-size: 0.7rem; color: var(--muted); }

/* ── Settings Strip ── */
.settings-strip {
    display: flex; align-items: center; gap: 2rem;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 14px; padding: 0.8rem 1.5rem;
    margin-bottom: 1.5rem;
    animation: fadeSlideUp 1s ease both;
}
.settings-label {
    font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: var(--muted); white-space: nowrap;
}

/* ── Tab Styles ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 5px !important; gap: 4px !important;
    margin-bottom: 0 !important;
    animation: fadeSlideUp 1s ease both;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: var(--muted) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 0.9rem !important;
    padding: 0.6rem 1.8rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: var(--glass-hov) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FFB800, #FF8C00) !important;
    color: #000 !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(255,184,0,0.3) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem !important;
}

/* ── Glass Cards ── */
.gcard {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 18px; padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
    transition: all 0.3s ease;
    position: relative; overflow: hidden;
}
.gcard::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,184,0,0.2), transparent);
}
.gcard:hover {
    background: var(--glass-hov);
    border-color: rgba(255,184,0,0.15);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}
.gcard.gold-accent  { border-left: 3px solid var(--gold); }
.gcard.green-accent { border-left: 3px solid var(--green); }
.gcard.info-card    { background: rgba(255,184,0,0.04); border-color: rgba(255,184,0,0.1); }

.card-label {
    font-size: 0.65rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.18em;
    color: var(--muted); margin-bottom: 0.4rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.card-label::before {
    content: ''; display: inline-block;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--gold);
}
.card-label.green::before { background: var(--green); }
.card-label.muted::before { background: var(--muted); }

.card-value {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.7rem; font-weight: 700;
    color: var(--text); line-height: 1.2;
}
.card-value.gold  { color: var(--gold); }
.card-value.green { color: var(--green); }
.card-value.sm    { font-size: 1.1rem; }

/* ── Signs Flow ── */
.signs-flow {
    display: flex; flex-wrap: wrap; gap: 6px;
    margin-top: 0.5rem;
}
.sign-chip {
    background: rgba(255,184,0,0.08);
    border: 1px solid rgba(255,184,0,0.2);
    border-radius: 8px; padding: 4px 12px;
    font-family: 'Unbounded', sans-serif;
    font-size: 0.8rem; color: var(--gold);
    animation: chipPop 0.2s ease;
}
@keyframes chipPop {
    from { transform: scale(0.7); opacity: 0; }
    to   { transform: scale(1); opacity: 1; }
}

/* ── Translation Display ── */
.translation-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 1rem; margin: 1rem 0;
}
.trans-box {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 1.4rem;
    position: relative; overflow: hidden;
    transition: all 0.3s;
}
.trans-box:hover { transform: translateY(-3px); }
.trans-box.english {
    border-top: 2px solid rgba(255,184,0,0.4);
}
.trans-box.twi {
    border-top: 2px solid rgba(0,200,117,0.4);
    background: rgba(0,200,117,0.03);
}
.trans-flag { font-size: 1.5rem; margin-bottom: 0.4rem; }
.trans-lang {
    font-size: 0.65rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.15em;
    color: var(--muted); margin-bottom: 0.5rem;
}
.trans-text {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    color: var(--text); line-height: 1.3;
}
.trans-text.twi-text { color: var(--green); }

/* ── Audio Section ── */
.audio-section {
    background: linear-gradient(135deg, rgba(255,184,0,0.05), rgba(0,200,117,0.05));
    border: 1px solid rgba(255,184,0,0.15);
    border-radius: 16px; padding: 1.2rem 1.5rem;
    margin-top: 1rem;
}
.audio-title {
    font-size: 0.75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.15em;
    color: var(--gold); margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.audio-title::after {
    content: '';
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(255,184,0,0.2), transparent);
}
audio {
    width: 100%; border-radius: 10px;
    filter: invert(1) hue-rotate(200deg) saturate(0.5);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #FFB800 0%, #FF8C00 100%) !important;
    color: #000 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.9rem !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.7rem 1.8rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(255,184,0,0.2) !important;
    letter-spacing: 0.03em !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(255,184,0,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #00C875 0%, #00A85E 100%) !important;
    color: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    border: none !important; border-radius: 12px !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(0,200,117,0.2) !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(0,200,117,0.4) !important;
}

/* ── Progress Bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #FFB800, #FF8C00, #00C875) !important;
    border-radius: 100px !important;
    box-shadow: 0 0 10px rgba(255,184,0,0.4) !important;
}
.stProgress > div > div {
    background: var(--muted2) !important;
    border-radius: 100px !important;
}

/* ── Toggle ── */
.stToggle > label { color: var(--text) !important; font-weight: 500 !important; }

/* ── Slider ── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--gold) !important;
    box-shadow: 0 0 8px rgba(255,184,0,0.5) !important;
}
.stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
    color: var(--gold) !important;
}

/* ── Checkbox ── */
.stCheckbox label { color: var(--text) !important; font-weight: 400 !important; }

/* ── File Uploader ── */
[data-testid="stFileUploadDropzone"] {
    background: var(--glass) !important;
    border: 2px dashed var(--muted2) !important;
    border-radius: 16px !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(255,184,0,0.3) !important;
    background: var(--glass-hov) !important;
}

/* ── Live Result Cards ── */
.live-sign {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 1.2rem;
    margin-bottom: 0.6rem; text-align: center;
    transition: all 0.3s;
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
.live-sign-conf {
    font-size: 0.75rem; color: var(--muted);
    margin-top: 0.3rem;
}

/* ── Word Builder ── */
.word-builder {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem; min-height: 60px;
    display: flex; align-items: center; gap: 0.5rem;
    flex-wrap: wrap;
}
.word-letter {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.2rem; font-weight: 700;
    color: var(--text);
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--border);
    border-radius: 6px; padding: 2px 8px;
    animation: chipPop 0.15s ease;
}
.word-cursor {
    width: 2px; height: 24px;
    background: var(--gold);
    border-radius: 2px;
    animation: blink 1s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── Sentence Display ── */
.sentence-display {
    background: linear-gradient(135deg, rgba(255,184,0,0.04), rgba(0,200,117,0.04));
    border: 1px solid rgba(255,184,0,0.12);
    border-radius: 16px; padding: 1.2rem 1.4rem;
    margin-bottom: 0.6rem;
}
.sentence-en {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.1rem; font-weight: 600;
    color: var(--text); margin-bottom: 0.6rem;
}
.sentence-twi {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    color: var(--green);
}
.sentence-arrow {
    color: var(--muted); font-size: 0.8rem;
    margin: 0.3rem 0; display: block;
}

/* ── Log Entries ── */
.log-entry {
    display: flex; align-items: center; gap: 0.8rem;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 0.6rem 1rem;
    margin-bottom: 0.3rem; font-size: 0.85rem;
    animation: fadeSlideUp 0.3s ease;
    transition: all 0.2s;
}
.log-entry:hover {
    background: var(--glass-hov);
    border-color: rgba(255,184,0,0.1);
}
.log-en  { color: var(--text); font-weight: 600; }
.log-arr { color: var(--muted); }
.log-twi { color: var(--green); font-style: italic; }

/* ── Camera Idle State ── */
.cam-idle {
    background: var(--glass);
    border: 2px dashed var(--muted2);
    border-radius: 18px; padding: 6rem 2rem;
    text-align: center; transition: all 0.3s;
}
.cam-idle:hover { border-color: rgba(255,184,0,0.2); }
.cam-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
.cam-text {
    font-size: 0.95rem; color: var(--muted);
    font-weight: 300;
}

/* ── Tip Box ── */
.tip-box {
    background: rgba(255,184,0,0.04);
    border: 1px solid rgba(255,184,0,0.12);
    border-left: 3px solid var(--gold);
    border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.85rem; color: var(--muted);
    line-height: 1.6;
}
.tip-box b { color: var(--gold); }

/* ── How it works ── */
.how-row {
    display: flex; align-items: center;
    gap: 0.8rem; margin-bottom: 0.6rem;
}
.how-step {
    width: 28px; height: 28px;
    background: rgba(255,184,0,0.1);
    border: 1px solid rgba(255,184,0,0.2);
    border-radius: 50%; display: flex;
    align-items: center; justify-content: center;
    font-family: 'Unbounded', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    color: var(--gold); flex-shrink: 0;
}
.how-text { font-size: 0.85rem; color: var(--muted); }
.how-text b { color: var(--text); }

/* ── Footer ── */
.footer {
    text-align: center; padding: 2rem 0 1rem;
    color: var(--muted2); font-size: 0.8rem;
}
.footer span { color: var(--muted); }

/* ── Animations ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,184,0,0.2); }
    50%       { box-shadow: 0 0 0 8px rgba(255,184,0,0); }
}
.pulse { animation: pulse 2s infinite; }
</style>
""", unsafe_allow_html=True)


# ── Audio helpers ─────────────────────────────────────────────
def make_audio_bytes(text):
    try:
        tts = gTTS(text=text, lang='en', slow=True)
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
        tts = gTTS(text=text, lang='en', slow=True)
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
                # Resize frame to fixed width to avoid zoom out
        frame_small = cv2.resize(frame, (480, 360))
        preview.image(cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB),
            channels="RGB", width=480,
            caption=f"Analysing second {sec:.0f} of {duration}")

    cap.release()
    bar.progress(1.0, text="✅ Analysis complete!")
    return signs

def build_sentence(signs):
    if "space" not in signs:
        word = "".join([s for s in signs if s not in ["nothing","del","space"]])
        _, twi = get_twi_for_word(word)
        return word, twi
    words, twis, cur = [], [], ""
    for s in signs:
        if s == "space":
            if cur:
                _, twi = get_twi_for_word(cur)
                words.append(cur); twis.append(twi); cur = ""
        elif s == "del": cur = cur[:-1]
        elif s != "nothing": cur += s
    if cur:
        _, twi = get_twi_for_word(cur)
        words.append(cur); twis.append(twi)
    return " ".join(words), " ".join(twis)


# ══════════════════════════════════════════════════════════════
# RENDER APP
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="bg-mesh"></div>', unsafe_allow_html=True)
st.markdown('<div class="kente-bar"></div>', unsafe_allow_html=True)
st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <div class="hero-left">
    <div class="hero-eyebrow">🇬🇭 Ghana &nbsp;·&nbsp; ASL &nbsp;·&nbsp; Twi &nbsp;·&nbsp; AI</div>
    <div class="hero-title">
        <span class="sign">Sign</span><span class="twi">Twi</span>
    </div>
    <div class="hero-desc">
        Real-time American Sign Language recognition that translates to
        <b style="color:#FFB800;">Twi (Akan)</b> and speaks it aloud —
        bridging communication for Ghana's deaf community.
    </div>
  </div>
  <div class="hero-right">
    <div class="stat-pill">
        <div class="stat-icon">🎯</div>
        <div class="stat-info">
            <div class="stat-val">98.4%</div>
            <div class="stat-desc">Model Accuracy</div>
        </div>
    </div>
    <div class="stat-pill">
        <div class="stat-icon">🤟</div>
        <div class="stat-info">
            <div class="stat-val">29 Signs</div>
            <div class="stat-desc">ASL Alphabet + Special</div>
        </div>
    </div>
    <div class="stat-pill">
        <div class="stat-icon">🗣️</div>
        <div class="stat-info">
            <div class="stat-val">100+ Words</div>
            <div class="stat-desc">Twi Dictionary</div>
        </div>
    </div>
    <div class="stat-pill">
        <div class="stat-icon">⚡</div>
        <div class="stat-info">
            <div class="stat-val">Real-Time</div>
            <div class="stat-desc">Live Camera Detection</div>
        </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)

# ── Settings ──────────────────────────────────────────────────
sc1, sc2, sc3, sc4 = st.columns([3,1,1,1])
with sc1:
    threshold = st.slider(
        "🎚️ Detection Confidence",
        0.5, 1.0, 0.8, 0.05,
        help="Higher = stricter, Lower = more sensitive"
    )
with sc2:
    st.markdown("<br>", unsafe_allow_html=True)
    show_lms = st.checkbox("🖐️ Skeleton", value=True)
with sc3:
    st.markdown("<br>", unsafe_allow_html=True)
    speak_audio = st.checkbox("🔊 Auto-Speak", value=True)
with sc4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(255,184,0,0.08);border:1px solid rgba(255,184,0,0.2);
    border-radius:10px;padding:0.4rem 0.8rem;text-align:center;font-size:0.75rem;
    color:#FFB800;font-weight:600;">● LIVE</div>
    """, unsafe_allow_html=True)

st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)

# ── Load ───────────────────────────────────────────────────────
model, classes = load_model_and_classes()
landmarker     = load_landmarker()

# ── Tabs ──────────────────────────────────────────────────────
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
    <b>How video upload works:</b> Upload a video of someone performing ASL signs.
    SignTwi extracts each sign frame by frame, builds the word or sentence,
    translates it to <b>Twi</b>, and generates a downloadable voice note.
    Hold each sign for <b>2–3 seconds</b> with good lighting for best results.
    </div>
    """, unsafe_allow_html=True)

    video_file = st.file_uploader(
        "Drop your video here or click to browse — MP4, MOV, AVI supported",
        type=["mp4","avi","mov","mkv"],
        label_visibility="visible"
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
            go = st.button("🚀 Analyse & Translate", key="analyse_btn")

        if go:
            st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)
            st.markdown('<p style="color:#4A4A5A;font-size:0.85rem;">Processing your video...</p>',
                unsafe_allow_html=True)
            signs = process_video(vpath, model, classes, landmarker, threshold)
            st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)

            if not signs:
                st.markdown("""
                <div style="background:rgba(255,59,92,0.08);border:1px solid rgba(255,59,92,0.2);
                border-radius:14px;padding:1.2rem 1.5rem;color:#FF3B5C;font-size:0.9rem;">
                ⚠️ <b>No signs detected.</b> Make sure your hand is clearly visible,
                well-lit, and facing the camera directly.
                </div>
                """, unsafe_allow_html=True)
            else:
                # Signs chips
                chips = "".join([f'<span class="sign-chip">{s}</span>' for s in signs])
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
                            "⬇️  Download Twi Voice Note (.mp3)",
                            data=audio_bytes,
                            file_name="signtwi_output.mp3",
                            mime="audio/mp3"
                        )
                        if speak_audio:
                            try: play_local(twi)
                            except Exception: pass
                    else:
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.warning("Audio generation failed — check internet connection.")
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
    <b>Sign letters</b> one by one to spell words.
    Use the <b>SPACE</b> sign to complete a word — it will be translated and spoken in Twi.
    Use the <b>DEL</b> sign to delete the last letter.
    Build full sentences by spelling multiple words!
    </div>
    """, unsafe_allow_html=True)

    cam_col, res_col = st.columns([3, 2])

    with cam_col:
        run  = st.toggle("▶️  Start Camera", value=False)
        f_ph = st.empty()

    with res_col:
        # Current sign display
        st.markdown('<div class="card-label" style="margin-bottom:0.5rem;">Current Detection</div>',
            unsafe_allow_html=True)
        sign_ph = st.empty()

        # Word builder
        st.markdown('<div class="card-label" style="margin:0.5rem 0;">Building Word</div>',
            unsafe_allow_html=True)
        word_ph = st.empty()

        # Sentence
        st.markdown('<div class="card-label" style="margin:0.5rem 0;">Translation</div>',
            unsafe_allow_html=True)
        sent_ph = st.empty()

        # Confidence
        conf_ph = st.empty()

        # Log
        st.markdown('<div class="card-label" style="margin:0.8rem 0 0.4rem;">Session Log</div>',
            unsafe_allow_html=True)
        log_ph = st.empty()

    # Session state init
    for k, v in {
        "log":[], "word":"",
        "sent_en":[], "sent_tw":[],
        "last_sign":"", "last_time":0.0
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if run:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            st.error("❌ Could not access webcam. Please check your camera.")
        else:
            fc=0; ls=None; lc=0.0; ll=None

            while run:
                ret, frame = cap.read()
                if not ret: break

                frame = cv2.flip(frame, 1)
                fc   += 1

                if fc % 5 == 0:
                    ls, lc, ll = predict(frame, model, classes, landmarker, threshold)

                if ll and show_lms: frame = draw_landmarks(frame, ll)
                if ls:
                    cv2.putText(frame, f"{ls}  {lc:.0%}",
                        (16,52), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255,184,0), 3)
                    cv2.putText(frame, f"{ls}  {lc:.0%}",
                        (16,52), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0,0,0), 1)

                word_disp = st.session_state.word
                cv2.putText(frame, f"Word: {word_disp}",
                    (16,100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,200,117), 2)

                if st.session_state.sent_en:
                    cv2.putText(frame,
                        " ".join(st.session_state.sent_en),
                        (16,145), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180,180,180), 2)

                if fc % 5 == 0:
                    f_ph.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                        channels="RGB", use_container_width=True)

                now = time.time()
                if ls and ls != "nothing" and fc % 5 == 0:
                    if ls != st.session_state.last_sign or now - st.session_state.last_time > 1.5:
                        st.session_state.last_sign = ls
                        st.session_state.last_time = now

                        if ls == "del":
                            st.session_state.word = st.session_state.word[:-1]
                        elif ls == "space":
                            if st.session_state.word:
                                w = st.session_state.word
                                _, twi = get_twi_for_word(w)
                                st.session_state.sent_en.append(w)
                                st.session_state.sent_tw.append(twi)
                                st.session_state.log.append((w, twi))
                                st.session_state.word = ""
                                if speak_audio:
                                    try: play_local(twi)
                                    except Exception: pass
                        else:
                            st.session_state.word += ls

                if fc % 5 == 0:
                    # Current sign card
                    active = "active pulse" if ls else ""
                    sign_ph.markdown(f"""
                    <div class="live-sign {active}">
                        <div class="live-sign-letter">{ls or "·"}</div>
                        <div class="live-sign-conf">
                        {"Confidence: " + f"{lc:.0%}" if ls else "Show your hand to the camera"}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Word builder
                    letters = "".join([
                        f'<span class="word-letter">{c}</span>'
                        for c in st.session_state.word
                    ])
                    word_ph.markdown(f"""
                    <div class="word-builder">
                        {letters if letters else '<span style="color:#2A2A35;font-size:0.85rem;">Start signing to build a word...</span>'}
                        <div class="word-cursor"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Sentence
                    if st.session_state.sent_en:
                        en_sent = " ".join(st.session_state.sent_en)
                        tw_sent = " ".join(st.session_state.sent_tw)
                        sent_ph.markdown(f"""
                        <div class="sentence-display">
                            <div class="sentence-en">🇺🇸 {en_sent}</div>
                            <span class="sentence-arrow">↓ Twi Translation</span>
                            <div class="sentence-twi">🇬🇭 {tw_sent}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Confidence bar
                    conf_ph.markdown(f"""
                    <div class="gcard" style="padding:0.8rem 1.2rem;">
                        <div class="card-label muted">Detection Confidence</div>
                        <div style="display:flex;align-items:center;gap:1rem;margin-top:0.3rem;">
                            <div style="flex:1;background:#1A1A25;border-radius:100px;height:6px;">
                                <div style="width:{lc*100:.0f}%;background:linear-gradient(90deg,#FFB800,#00C875);
                                height:6px;border-radius:100px;transition:width 0.3s;"></div>
                            </div>
                            <span style="font-family:'Unbounded',sans-serif;
                            font-size:0.9rem;color:#FFB800;font-weight:700;min-width:40px;">
                            {lc:.0%}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Session log
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

            cap.release()
    else:
        f_ph.markdown("""
        <div class="cam-idle">
            <div class="cam-icon">📷</div>
            <div class="cam-text">Toggle <b style="color:#F2F2F5;">Start Camera</b> above to begin live recognition</div>
            <div style="margin-top:0.5rem;font-size:0.75rem;color:#2A2A35;">
            Make sure your webcam is connected and permitted</div>
        </div>
        """, unsafe_allow_html=True)

        # Show empty states
        sign_ph.markdown("""
        <div class="live-sign">
            <div class="live-sign-letter" style="color:#2A2A35;">·</div>
            <div class="live-sign-conf">Camera is off</div>
        </div>""", unsafe_allow_html=True)

        word_ph.markdown("""
        <div class="word-builder">
            <span style="color:#2A2A35;font-size:0.85rem;">Start camera to begin signing...</span>
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
                <div class="how-row">
                    <div class="how-step">1</div>
                    <div class="how-text">Click <b>Video Upload</b> tab and upload your video</div>
                </div>
                <div class="how-row">
                    <div class="how-step">2</div>
                    <div class="how-text">Click <b>Analyse & Translate</b> button</div>
                </div>
                <div class="how-row">
                    <div class="how-step">3</div>
                    <div class="how-text">View the detected signs and <b>English sentence</b></div>
                </div>
                <div class="how-row">
                    <div class="how-step">4</div>
                    <div class="how-text">Read the <b>Twi translation</b> and play the voice note</div>
                </div>
                <div class="how-row">
                    <div class="how-step">5</div>
                    <div class="how-text">Download the Twi audio as an <b>MP3 file</b></div>
                </div>
            </div>
        </div>

        <div class="gcard" style="margin-top:0.8rem;">
            <div class="card-label muted">💡 Tips for Best Results</div>
            <div style="margin-top:0.6rem;font-size:0.85rem;color:#4A4A5A;line-height:1.8;">
                ✓ &nbsp;Hold each sign for <b style="color:#F2F2F5;">2–3 seconds</b><br>
                ✓ &nbsp;Use <b style="color:#F2F2F5;">good lighting</b> — avoid shadows<br>
                ✓ &nbsp;<b style="color:#F2F2F5;">Plain background</b> works best<br>
                ✓ &nbsp;Keep hand <b style="color:#F2F2F5;">fully visible</b> in frame<br>
                ✓ &nbsp;Face camera <b style="color:#F2F2F5;">directly</b> — avoid angles
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="gcard green-accent">
            <div class="card-label green">📷 Live Camera</div>
            <div style="margin-top:0.8rem;">
                <div class="how-row">
                    <div class="how-step">1</div>
                    <div class="how-text">Toggle <b>Start Camera</b> to activate webcam</div>
                </div>
                <div class="how-row">
                    <div class="how-step">2</div>
                    <div class="how-text">Sign letters one by one to <b>spell a word</b></div>
                </div>
                <div class="how-row">
                    <div class="how-step">3</div>
                    <div class="how-text">Use <b>SPACE sign</b> to complete the word</div>
                </div>
                <div class="how-row">
                    <div class="how-step">4</div>
                    <div class="how-text">App translates to <b>Twi and speaks it</b> aloud</div>
                </div>
                <div class="how-row">
                    <div class="how-step">5</div>
                    <div class="how-text">Sign more words to build a <b>full sentence</b></div>
                </div>
            </div>
        </div>

        <div class="gcard" style="margin-top:0.8rem;">
            <div class="card-label muted">🤟 Special Signs</div>
            <div style="margin-top:0.6rem;font-size:0.85rem;color:#4A4A5A;line-height:1.8;">
                ✋ <b style="color:#FFB800;">SPACE sign</b> — completes current word,
                   triggers Twi translation and audio<br><br>
                🗑️ <b style="color:#FF3B5C;">DEL sign</b> — deletes the last letter
                   you signed<br><br>
                ⭕ <b style="color:#F2F2F5;">NOTHING sign</b> — rest position,
                   ignored by the app
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────
st.markdown('<div class="kente-bar thin"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <span style="font-family:'Unbounded',sans-serif;font-size:0.9rem;color:#FFB800;font-weight:700;">SignTwi</span>
    <br>
    <span>Built with MediaPipe &nbsp;·&nbsp; TensorFlow &nbsp;·&nbsp; Streamlit</span>
    <br>
    <span>🇬🇭 Made for Ghana &nbsp;·&nbsp; Bridging ASL and Twi for the deaf community</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)