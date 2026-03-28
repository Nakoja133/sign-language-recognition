import cv2
import pickle
import numpy as np
import streamlit as st
import mediapipe as mp
import tensorflow as tf
from translator import get_twi_for_word, get_twi_for_sign, get_twi_translation, TWI_DICTIONARY
from audio_output import speak_twi, save_audio_file
import time
import tempfile
import os
from gtts import gTTS
import urllib.request

# Auto-download hand landmarker model if not present
if not os.path.exists("hand_landmarker.task"):
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        "hand_landmarker.task"
    )

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="SignTwi — ASL to Twi Translator",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --gold:    #FFB800;
    --green:   #00A86B;
    --red:     #DC143C;
    --bg:      #080808;
    --surface: #111111;
    --card:    #161616;
    --border:  #242424;
    --text:    #F0F0F0;
    --muted:   #666666;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

.hero { text-align: center; padding: 3rem 0 2rem; position: relative; }
.hero::before {
    content: ''; position: absolute; top: 0; left: 50%;
    transform: translateX(-50%); width: 600px; height: 300px;
    background: radial-gradient(ellipse, rgba(255,184,0,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(255,184,0,0.15), rgba(0,168,107,0.15));
    border: 1px solid rgba(255,184,0,0.3); border-radius: 100px;
    padding: 6px 20px; font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--gold); margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 4rem; font-weight: 800;
    line-height: 1.05; margin: 0 0 1rem;
    background: linear-gradient(135deg, #FFB800 0%, #FFD966 40%, #00A86B 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    font-size: 1.1rem; font-weight: 300; color: var(--muted);
    max-width: 560px; margin: 0 auto 2rem; line-height: 1.7;
}
.hero-stats { display: flex; justify-content: center; gap: 3rem; margin-top: 1.5rem; }
.stat { text-align: center; }
.stat-num { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--gold); }
.stat-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }

.kente-divider {
    height: 4px; border-radius: 2px; margin: 2rem 0;
    background: linear-gradient(90deg, var(--bg) 0%, var(--red) 20%, var(--gold) 40%, var(--green) 60%, var(--gold) 80%, var(--bg) 100%);
}
.result-card {
    background: linear-gradient(135deg, #161616, #111111);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 1.2rem 1.5rem; margin-bottom: 0.75rem;
    position: relative; overflow: hidden;
}
.result-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 4px; height: 100%; background: var(--gold);
    border-radius: 4px 0 0 4px;
}
.result-card.green::before { background: var(--green); }
.result-card.red::before   { background: var(--red); }
.result-label {
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.15em; color: var(--muted); margin-bottom: 0.4rem;
}
.result-value { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: var(--text); }
.result-value.gold  { color: var(--gold); }
.result-value.green { color: var(--green); }
.result-value.small { font-size: 1.2rem; }

.section-title {
    font-family: 'Syne', sans-serif; font-size: 0.85rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.2em; color: var(--muted);
    margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
}
.section-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.word-chip {
    display: inline-block; background: var(--surface);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 4px 12px; margin: 3px; font-size: 0.9rem;
    font-family: 'Syne', sans-serif;
}
.word-chip.translated {
    border-color: var(--green); color: var(--green);
}
.word-chip.current {
    border-color: var(--gold); color: var(--gold);
    animation: pulse 1s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.sentence-box {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.75rem;
    font-family: 'Syne', sans-serif; font-size: 1.3rem; min-height: 3rem;
    color: var(--text); line-height: 1.6;
}
.sentence-box.twi { color: var(--green); border-color: rgba(0,168,107,0.3); }

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important; border-radius: 12px !important;
    padding: 4px !important; border: 1px solid var(--border) !important; gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 8px !important;
    color: var(--muted) !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; padding: 0.5rem 1.5rem !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: var(--gold) !important; color: #000 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

.stButton > button {
    background: linear-gradient(135deg, var(--gold), #FFC933) !important;
    color: #000 !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; border: none !important; border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important; transition: all 0.2s ease !important; width: 100% !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(255,184,0,0.35) !important; }
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--green), #00C47D) !important;
    color: #fff !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; border: none !important;
    border-radius: 10px !important; width: 100% !important;
}
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--gold), var(--green)) !important; }
audio { width: 100%; border-radius: 10px; }
.log-entry {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.6rem 1rem; margin-bottom: 0.4rem;
    font-size: 0.9rem; display: flex; align-items: center; gap: 0.75rem;
}
.log-sign  { color: var(--gold);  font-weight: 700; font-family: 'Syne', sans-serif; }
.log-twi   { color: var(--green); font-style: italic; }
.log-arrow { color: var(--muted); }
</style>
""", unsafe_allow_html=True)


# ── Load resources ─────────────────────────────────────────────
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
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.3
    )
    return HandLandmarker.create_from_options(options)

def draw_landmarks_manual(frame, hand_landmarks):
    h, w, _ = frame.shape
    connections = [
        (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)
    ]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
    for s, e in connections:
        cv2.line(frame, pts[s], pts[e], (0, 168, 107), 2)
    for pt in pts:
        cv2.circle(frame, pt, 5, (255, 184, 0), -1)
    return frame

def predict_from_frame(frame, model, classes, landmarker, threshold):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    results   = landmarker.detect(mp_image)
    if results.hand_landmarks:
        lms = []
        for lm in results.hand_landmarks[0]:
            lms.extend([lm.x, lm.y, lm.z])
        preds = model.predict(np.array(lms).reshape(1, -1), verbose=0)
        conf  = float(np.max(preds))
        cls   = np.argmax(preds)
        if conf >= threshold:
            return classes[cls], conf, results.hand_landmarks[0]
    return None, 0.0, None

def build_words_and_sentence(signs):
    """Convert list of signs into words and full sentence with Twi translations"""
    words        = []
    current      = ""
    translations = []

    for sign in signs:
        if sign == "space":
            if current:
                words.append(current)
                _, twi = get_twi_for_word(current)
                translations.append(twi)
                current = ""
        elif sign == "del":
            current = current[:-1]
        elif sign != "nothing":
            current += sign

    # Add last word
    if current:
        words.append(current)
        _, twi = get_twi_for_word(current)
        translations.append(twi)

    english_sentence = " ".join(words)
    twi_sentence     = " ".join(translations)
    return words, translations, english_sentence, twi_sentence

def process_video(video_path, model, classes, landmarker, threshold):
    """Process video extracting one clean sign per sign held"""
    cap          = cv2.VideoCapture(video_path)
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = max(1, int(total_frames / fps))

    signs        = []
    last_added   = None
    progress_bar = st.progress(0, text="Analysing video...")
    preview      = st.empty()

    # Sample every 1.5 seconds, offset by 0.75s to land mid-sign
    step    = 1.5
    samples = int(duration_sec / step)

    for i in range(samples):
        sec = i * step + 0.75
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if not ret:
            break

        sign, conf, lms = predict_from_frame(frame, model, classes, landmarker, threshold)

        if sign and sign != "nothing" and sign != last_added:
            signs.append(sign)
            last_added = sign
            if lms:
                frame = draw_landmarks_manual(frame, lms)
            cv2.putText(frame, f"{sign} ({conf:.0%})",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 184, 0), 2)

        preview.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            channels="RGB", use_container_width=True,
            caption=f"Analysing second {sec:.1f} of {duration_sec}")

        progress_value = min((i + 1) / samples, 1.0)
        progress_bar.progress(progress_value,
            text=f"Processing {i+1}/{samples} frames...")

    cap.release()
    progress_bar.progress(1.0, text="✅ Analysis complete!")
    return signs


# ══════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">🇬🇭 Ghana · ASL · Twi · AI</div>
    <div class="hero-title">SignTwi</div>
    <div class="hero-sub">
        Real-time ASL sign language recognition that speaks back to you
        in Twi — bridging communication for the deaf community in Ghana.
    </div>
    <div class="hero-stats">
        <div class="stat"><div class="stat-num">98.4%</div><div class="stat-label">Model Accuracy</div></div>
        <div class="stat"><div class="stat-num">29</div><div class="stat-label">ASL Signs</div></div>
        <div class="stat"><div class="stat-num">100+</div><div class="stat-label">Twi Words</div></div>
        <div class="stat"><div class="stat-num">Live</div><div class="stat-label">Real-Time</div></div>
    </div>
</div>
<div class="kente-divider"></div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
    color:#FFB800;margin-bottom:0.2rem;">⚙️ Settings</div>
    <div style="color:#666;font-size:0.8rem;margin-bottom:1.5rem;">Configure recognition</div>
    """, unsafe_allow_html=True)

    confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.8, 0.05)
    show_landmarks = st.checkbox("🖐️ Show Hand Skeleton", value=True)
    speak_audio    = st.checkbox("🔊 Speak Twi Audio", value=True)

    st.markdown("<div class='kente-divider'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:0.9rem;
    font-weight:700;color:#FFB800;margin-bottom:0.8rem;">📖 ASL Reference</div>""",
    unsafe_allow_html=True)
    st.image("https://www.nidcd.nih.gov/sites/default/files/2022-08/asl-alphabet.jpg",
        caption="ASL Alphabet")

    st.markdown("<div class='kente-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#444;font-size:0.75rem;line-height:1.8;">
    <b style="color:#FFB800;">How to sign words:</b><br>
    Sign letters one by one to spell a word.<br>
    ✋ <b style="color:#FFB800;">SPACE</b> → completes word, speaks Twi<br>
    🗑️ <b style="color:#DC143C;">DEL</b> → deletes last letter<br><br>
    <b style="color:#FFB800;">Example — say "HELLO":</b><br>
    Sign H → E → L → L → O → SPACE<br>
    App says: <i style="color:#00A86B;">"Agoo"</i> 🔊
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='kente-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:0.85rem;font-weight:700;
    color:#FFB800;margin-bottom:0.5rem;">📚 Known Twi Words</div>
    """, unsafe_allow_html=True)

    # Show dictionary sample
    sample_words = list(TWI_DICTIONARY.items())[:15]
    dict_html = ""
    for eng, twi in sample_words:
        dict_html += f"""<div style="display:flex;justify-content:space-between;
        padding:3px 0;border-bottom:1px solid #1a1a1a;font-size:0.75rem;">
        <span style="color:#888;">{eng}</span>
        <span style="color:#00A86B;">{twi}</span></div>"""
    st.markdown(dict_html, unsafe_allow_html=True)


# ── Load model ─────────────────────────────────────────────────
model, classes = load_model_and_classes()
landmarker     = load_landmarker()

tab1, tab2 = st.tabs(["📹  Video Upload", "📷  Live Camera"])


# ══════════════════════════════════════════════════════════════
# TAB 1 — VIDEO UPLOAD
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Upload Sign Language Video</div>',
        unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111;border:1px solid #222;border-radius:12px;
    padding:1rem 1.2rem;margin-bottom:1.2rem;color:#888;font-size:0.9rem;line-height:1.7;">
    Upload a video of ASL signing. SignTwi extracts each letter, builds words and sentences,
    translates everything to <b style="color:#FFB800;">Twi</b>, and generates a
    <b style="color:#00A86B;">downloadable voice note</b>.<br><br>
    💡 <b style="color:#666;">Tip:</b> Hold each sign for 2-3 seconds with good lighting for best results.
    </div>
    """, unsafe_allow_html=True)

    uploaded_video = st.file_uploader(
        "Drop video here", type=["mp4","avi","mov","mkv"],
        label_visibility="collapsed"
    )

    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(uploaded_video.read())
            video_path = tmp.name

        col_vid, col_btn = st.columns([3, 1])
        with col_vid:
            st.video(uploaded_video)
        with col_btn:
            st.markdown("<br><br>", unsafe_allow_html=True)
            process_btn = st.button("🚀 Analyse & Translate")

        if process_btn:
            st.markdown('<div class="kente-divider"></div>', unsafe_allow_html=True)
            signs = process_video(video_path, model, classes, landmarker, confidence_threshold)
            st.markdown('<div class="kente-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Recognition Results</div>',
                unsafe_allow_html=True)

            if not signs:
                st.error("⚠️ No signs detected. Make sure the hand is clearly visible and well-lit.")
            else:
                # Raw signs
                signs_display = " → ".join(signs)
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Letters Detected</div>
                    <div style="font-family:'Syne',sans-serif;font-size:1rem;
                    color:#FFB800;letter-spacing:0.1em;">{signs_display}</div>
                </div>
                """, unsafe_allow_html=True)

                # Build words and sentence
                words, translations, english_sentence, twi_sentence = \
                    build_words_and_sentence(signs)

                if words:
                    # Word by word breakdown
                    st.markdown('<div class="section-title">Word by Word Translation</div>',
                        unsafe_allow_html=True)

                    cols = st.columns(min(len(words), 4))
                    for idx, (word, twi) in enumerate(zip(words, translations)):
                        with cols[idx % 4]:
                            st.markdown(f"""
                            <div class="result-card">
                                <div class="result-label">Word {idx+1}</div>
                                <div class="result-value" style="font-size:1.2rem;">{word}</div>
                                <div style="color:#00A86B;font-family:'Syne',sans-serif;
                                font-size:1rem;margin-top:0.3rem;">{twi}</div>
                            </div>
                            """, unsafe_allow_html=True)

                # Full sentence
                st.markdown('<div class="section-title" style="margin-top:1rem;">Full Translation</div>',
                    unsafe_allow_html=True)

                col_en, col_tw = st.columns(2)
                with col_en:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">🇺🇸 English Sentence</div>
                        <div class="result-value small">{english_sentence or "—"}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_tw:
                    st.markdown(f"""
                    <div class="result-card green">
                        <div class="result-label">🇬🇭 Twi Translation</div>
                        <div class="result-value green small">{twi_sentence or "—"}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Audio
                if twi_sentence:
                    st.markdown('<div class="section-title" style="margin-top:1rem;">Twi Voice Note</div>',
                        unsafe_allow_html=True)
                    audio_path = save_audio_file(twi_sentence, "twi_output.mp3")
                    if audio_path and os.path.exists(audio_path):
                        with open(audio_path, "rb") as af:
                            audio_bytes = af.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button(
                            label="⬇️  Download Twi Voice Note (.mp3)",
                            data=audio_bytes,
                            file_name="signtwi_translation.mp3",
                            mime="audio/mp3"
                        )
                        if speak_audio:
                            speak_twi(twi_sentence)
                    else:
                        st.warning("Audio generation failed. Check internet connection.")

        try:
            os.unlink(video_path)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
# TAB 2 — LIVE CAMERA
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Live Camera Recognition</div>',
        unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111;border:1px solid #222;border-radius:12px;
    padding:0.8rem 1.2rem;margin-bottom:1rem;color:#888;font-size:0.85rem;">
    Sign letters to spell words. Use <b style="color:#FFB800;">SPACE</b> sign to complete
    a word and hear it in Twi. Use <b style="color:#DC143C;">DEL</b> to delete a letter.
    Build full sentences word by word!
    </div>
    """, unsafe_allow_html=True)

    cam_col, res_col = st.columns([3, 2])

    with cam_col:
        run               = st.toggle("▶️  Start Camera", value=False)
        frame_placeholder = st.empty()

    with res_col:
        st.markdown('<div class="section-title">Live Results</div>', unsafe_allow_html=True)
        sign_ph     = st.empty()
        word_ph     = st.empty()
        sentence_ph = st.empty()
        twi_ph      = st.empty()
        conf_ph     = st.empty()
        st.markdown('<div class="section-title" style="margin-top:0.5rem;">Session Log</div>',
            unsafe_allow_html=True)
        log_ph = st.empty()

    # Session state
    defaults = {
        "log": [],
        "current_word": "",
        "sentence_words": [],
        "sentence_twi": [],
        "last_sign": "",
        "last_sign_time": 0.0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    if run:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            st.error("❌ Could not access webcam.")
        else:
            frame_count = 0
            last_sign   = None
            last_conf   = 0.0
            last_lms    = None

            while run:
                ret, frame = cap.read()
                if not ret:
                    break

                frame        = cv2.flip(frame, 1)
                frame_count += 1

                if frame_count % 5 == 0:
                    last_sign, last_conf, last_lms = predict_from_frame(
                        frame, model, classes, landmarker, confidence_threshold
                    )

                if last_lms and show_landmarks:
                    frame = draw_landmarks_manual(frame, last_lms)
                if last_sign:
                    cv2.putText(frame, f"{last_sign}  {last_conf:.0%}",
                        (14, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 184, 0), 3)

                # Show current word and sentence on frame
                cv2.putText(frame,
                    f"Word: {st.session_state.current_word}",
                    (14, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 120), 2)

                sentence_so_far = " ".join(st.session_state.sentence_words)
                if sentence_so_far:
                    cv2.putText(frame,
                        f"Sentence: {sentence_so_far}",
                        (14, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

                if frame_count % 5 == 0:
                    frame_placeholder.image(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                        channels="RGB", use_container_width=True
                    )

                # Sign logic
                now = time.time()
                if last_sign and last_sign != "nothing" and frame_count % 5 == 0:
                    if (last_sign != st.session_state.last_sign or
                            now - st.session_state.last_sign_time > 1.5):
                        st.session_state.last_sign      = last_sign
                        st.session_state.last_sign_time = now

                        if last_sign == "del":
                            st.session_state.current_word = \
                                st.session_state.current_word[:-1]

                        elif last_sign == "space":
                            if st.session_state.current_word:
                                word = st.session_state.current_word
                                _, twi = get_twi_for_word(word)

                                # Add to sentence
                                st.session_state.sentence_words.append(word)
                                st.session_state.sentence_twi.append(twi)
                                st.session_state.current_word = ""

                                # Speak the Twi word
                                if speak_audio:
                                    speak_twi(twi)

                                # Log it
                                st.session_state.log.append((word, twi))
                        else:
                            st.session_state.current_word += last_sign

                # Update UI every 5th frame
                if frame_count % 5 == 0:
                    sign_ph.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">Current Sign</div>
                        <div class="result-value gold">{last_sign or "—"}</div>
                    </div>""", unsafe_allow_html=True)

                    word_ph.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">Word Being Built</div>
                        <div class="result-value">{st.session_state.current_word or "—"}</div>
                    </div>""", unsafe_allow_html=True)

                    # Full sentence display
                    if st.session_state.sentence_words:
                        eng_sent = " ".join(st.session_state.sentence_words)
                        twi_sent = " ".join(st.session_state.sentence_twi)

                        sentence_ph.markdown(f"""
                        <div class="result-card">
                            <div class="result-label">🇺🇸 English Sentence</div>
                            <div class="result-value small">{eng_sent}</div>
                        </div>""", unsafe_allow_html=True)

                        twi_ph.markdown(f"""
                        <div class="result-card green">
                            <div class="result-label">🇬🇭 Twi Sentence</div>
                            <div class="result-value green small">{twi_sent}</div>
                        </div>""", unsafe_allow_html=True)

                    conf_ph.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">Confidence</div>
                        <div class="result-value gold">{last_conf:.0%}</div>
                    </div>""", unsafe_allow_html=True)

                    # Session log
                    if st.session_state.log:
                        log_html = ""
                        for w, t in st.session_state.log[-8:][::-1]:
                            log_html += f"""
                            <div class="log-entry">
                                <span class="log-sign">{w}</span>
                                <span class="log-arrow">→</span>
                                <span class="log-twi">{t}</span>
                            </div>"""
                        log_ph.markdown(log_html, unsafe_allow_html=True)

            cap.release()
    else:
        frame_placeholder.markdown("""
        <div style="background:#0D0D0D;border:2px dashed #222;border-radius:16px;
        padding:5rem 2rem;text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">📷</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#444;font-weight:600;">
            Toggle Start Camera to begin</div>
            <div style="color:#333;font-size:0.85rem;margin-top:0.5rem;">
            Make sure your webcam is connected</div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────
st.markdown("""
<div class="kente-divider"></div>
<div style="text-align:center;padding:1.5rem 0 0.5rem;color:#333;font-size:0.8rem;">
    <span style="color:#FFB800;font-family:'Syne',sans-serif;font-weight:700;">SignTwi</span>
    &nbsp;·&nbsp; Built with MediaPipe · TensorFlow · Streamlit
    &nbsp;·&nbsp; 🇬🇭 Made for Ghana
</div>
""", unsafe_allow_html=True)
