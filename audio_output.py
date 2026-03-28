import os
import tempfile
from gtts import gTTS

TWI_PHONETIC = {
    "agoo": "ah-goo",
    "nante yie": "nan-teh yee-eh",
    "maakye": "maa-cheh",
    "maaha": "maa-hah",
    "maadwo": "maa-jo",
    "akwaaba": "ah-kwaa-bah",
    "medaase": "meh-daa-seh",
    "mepawokyew": "meh-pah-wo-chew",
    "kafra": "kah-frah",
    "aane": "aa-neh",
    "daabi": "daa-bee",
    "boa me": "boh-ah meh",
    "adamfo": "ah-dam-fo",
    "abusua": "ah-boo-soo-ah",
    "maame": "maa-meh",
    "agya": "ah-jah",
    "aduane": "ah-joo-ah-neh",
    "nsuo": "n-soo-oh",
    "odo": "oh-doh",
    "anigye": "ah-nee-jeh",
    "papa": "pah-pah",
    "bone": "boh-neh",
    "fie": "fee-eh",
    "sukuu": "soo-koo",
    "adwuma": "ah-joo-mah",
    "ghana": "gah-nah",
    "nkran": "n-kran",
    "yoo": "yoh",
    "awerchow": "ah-wer-chow",
    "din": "deen",
    "odo": "oh-doh",
}

def generate_audio_bytes(twi_text):
    """Generate audio and return as bytes for st.audio()"""
    try:
        phonetic = TWI_PHONETIC.get(twi_text.lower(), twi_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp_path = f.name
        tts = gTTS(text=phonetic, lang='en', slow=True)
        tts.save(tmp_path)
        with open(tmp_path, 'rb') as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        return audio_bytes
    except Exception as e:
        print(f"Audio error: {e}")
        return None

def speak_twi(twi_text):
    """For local use — plays audio via Windows"""
    try:
        phonetic = TWI_PHONETIC.get(twi_text.lower(), twi_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp_path = f.name
        tts = gTTS(text=phonetic, lang='en', slow=True)
        tts.save(tmp_path)
        os.startfile(tmp_path)
        return True
    except Exception as e:
        print(f"Audio error: {e}")
        return False

def save_audio_file(twi_text, output_path="twi_output.mp3"):
    """Save audio as file"""
    try:
        phonetic = TWI_PHONETIC.get(twi_text.lower(), twi_text)
        tts = gTTS(text=phonetic, lang='en', slow=True)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Save error: {e}")
        return None