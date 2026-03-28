import os
import tempfile
import time
from gtts import gTTS

# Twi pronunciation guide for gTTS
# gTTS can't speak Twi but we can phonetically guide it
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
    "din": "deen",
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
}

def speak_twi(twi_text):
    """Speak Twi text using phonetic pronunciation"""
    try:
        # Get phonetic version if available
        phonetic = TWI_PHONETIC.get(twi_text.lower(), twi_text)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp_path = f.name

        # Use slow=True for clearer pronunciation
        tts = gTTS(text=phonetic, lang='en', slow=True)
        tts.save(tmp_path)

        # Play using Windows
        os.startfile(tmp_path)
        time.sleep(3)
        return True

    except Exception as e:
        print(f"Audio error: {e}")
        return False

def save_audio_file(twi_text, output_path="twi_output.mp3"):
    """Save Twi audio as downloadable file"""
    try:
        phonetic = TWI_PHONETIC.get(twi_text.lower(), twi_text)
        tts = gTTS(text=phonetic, lang='en', slow=True)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Save error: {e}")
        return None

def test_audio():
    print("Testing Twi audio...")
    words = ["agoo", "medaase", "akwaaba", "nsuo", "aduane"]
    for word in words:
        print(f"Speaking: {word}")
        speak_twi(word)
        time.sleep(1)
    print("Test complete! ✅")

if __name__ == "__main__":
    test_audio()