import os
import tempfile
from gtts import gTTS
from translator import twi_to_phonetic


def make_audio_bytes(text):
    """Generate audio bytes using Twi phonetic conversion"""
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


def speak_twi(text):
    """Speak Twi text using phonetic conversion — for local use"""
    try:
        phonetic = twi_to_phonetic(text)
        tts = gTTS(text=phonetic, lang='en', slow=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp = f.name
        tts.save(tmp)
        os.startfile(tmp)
        return True
    except Exception as e:
        print(f"Audio error: {e}")
        return False


def save_audio_file(text, output_path="twi_output.mp3"):
    """Save Twi speech as audio file"""
    try:
        phonetic = twi_to_phonetic(text)
        tts = gTTS(text=phonetic, lang='en', slow=True)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Save error: {e}")
        return None


def test_audio():
    """Test audio with Twi phonetics"""
    test_words = [
        ("akwaaba",     "Welcome"),
        ("medaase",     "Thank you"),
        ("maakye",      "Good morning"),
        ("me dɔ wo",    "I love you"),
        ("ɔdɔ",         "Love"),
        ("nsuo",        "Water"),
        ("aduane",      "Food"),
        ("gyina",       "Stand"),
        ("mepawokyew",  "Please"),
    ]
    print("Testing Twi phonetic audio...\n")
    for twi, english in test_words:
        phonetic = twi_to_phonetic(twi)
        print(f"  {english:15} | {twi:20} → [{phonetic}]")

    print("\nPlaying: 'Akwaaba' (Welcome)...")
    speak_twi("akwaaba")
    print("Done! ✅")


if __name__ == "__main__":
    test_audio()
