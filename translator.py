from googletrans import Translator

translator = Translator()

# Comprehensive English → Twi dictionary
TWI_DICTIONARY = {
    # Greetings
    "hello": "agoo",
    "hi": "agoo",
    "goodbye": "nante yie",
    "bye": "nante yie",
    "goodmorning": "maakye",
    "goodafternoon": "maaha",
    "goodevening": "maadwo",
    "goodnight": "daa",
    "welcome": "akwaaba",

    # Courtesies
    "please": "mepawokyew",
    "thankyou": "medaase",
    "thanks": "medaase",
    "sorry": "kafra",
    "excuse": "kafra",
    "yes": "aane",
    "no": "daabi",
    "okay": "yoo",
    "help": "boa me",

    # People
    "name": "din",
    "myname": "me din",
    "you": "wo",
    "me": "me",
    "we": "yen",
    "they": "won",
    "friend": "adamfo",
    "family": "abusua",
    "mother": "maame",
    "father": "agya",
    "sister": "nuabaa",
    "brother": "nua",
    "child": "abofra",
    "baby": "abofra",
    "man": "barima",
    "woman": "obaa",
    "boy": "abarimaa",
    "girl": "abaa",

    # Basic needs
    "food": "aduane",
    "water": "nsuo",
    "eat": "didi",
    "drink": "nom",
    "sleep": "daa",
    "rest": "hometew",
    "hungry": "kɔm de me",
    "thirsty": "sукоm de me",
    "sick": "yare",
    "pain": "yaw",
    "hospital": "asramuro",
    "doctor": "ɔdɔkono",

    # Emotions
    "love": "odo",
    "happy": "anigye",
    "sad": "awerchow",
    "angry": "abufuw",
    "scared": "suro",
    "good": "papa",
    "bad": "bone",
    "beautiful": "ɛfɛ",

    # Places
    "home": "fie",
    "school": "sukuu",
    "church": "asore",
    "market": "dwam",
    "hospital": "asramuro",
    "work": "adwuma",
    "ghana": "ghana",
    "accra": "nkran",

    # Common words
    "come": "bra",
    "go": "ko",
    "stop": "gyae",
    "wait": "twen",
    "run": "tu mmirika",
    "walk": "nante",
    "sit": "tena",
    "stand": "gyina",
    "look": "hwɛ",
    "listen": "tie",
    "speak": "kasa",
    "read": "kenkan",
    "write": "kyerɛw",
    "buy": "tɔ",
    "sell": "tɔn",
    "give": "ma",
    "take": "gye",
    "open": "bue",
    "close": "to mu",

    # Time
    "today": "ɛnnɛ",
    "tomorrow": "ɔkyena",
    "yesterday": "ɛnnɛ",
    "morning": "anɔpa",
    "afternoon": "awia",
    "evening": "anadwo",
    "now": "seesei",
    "time": "bere",

    # Numbers
    "one": "baako",
    "two": "abien",
    "three": "abiesa",
    "four": "anan",
    "five": "enum",
    "six": "asia",
    "seven": "ason",
    "eight": "awotwe",
    "nine": "akron",
    "ten": "edu",

    # Questions
    "what": "dɛn",
    "where": "hen",
    "when": "katekyi",
    "who": "hwan",
    "why": "adɛn",
    "how": "sɛn",

    # Colors
    "red": "kɔkɔɔ",
    "blue": "bruu",
    "green": "ahabammono",
    "white": "fitaa",
    "black": "tuntum",
    "yellow": "akokɔsrade",
}

def get_twi_translation(text):
    """Get Twi translation for any text"""
    if not text:
        return text, ""

    # Clean and lowercase
    clean = text.lower().strip().replace(" ", "")

    # Check dictionary first (fastest and most accurate)
    if clean in TWI_DICTIONARY:
        return text, TWI_DICTIONARY[clean]

    # Try with spaces too
    spaced = text.lower().strip()
    if spaced in TWI_DICTIONARY:
        return text, TWI_DICTIONARY[spaced]

    # Try Google Translate as fallback
    try:
        result = translator.translate(text, src='en', dest='ak')
        if result and result.text:
            return text, result.text
    except Exception as e:
        print(f"Translation error: {e}")

    # Last resort — return original
    return text, text

def get_twi_for_word(word):
    """Translate a complete word to Twi"""
    return get_twi_translation(word)

def get_twi_for_sign(sign_label):
    """Get Twi for a single sign label"""
    mapping = {
        'del': 'delete', 'nothing': '', 'space': 'space'
    }
    english = mapping.get(sign_label, sign_label)
    return get_twi_translation(english)

if __name__ == "__main__":
    tests = ["hello", "food", "water", "love", "ghana", "help"]
    for word in tests:
        eng, twi = get_twi_for_word(word)
        print(f"{eng} → {twi}")