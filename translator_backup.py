from googletrans import Translator

translator = Translator()

# ══════════════════════════════════════════════════════════════
# TWI PHONETIC CONVERTER
# Based on official Twi (Akan) phonetics:
# ɛ = "eh" (like air), ɔ = "aw" (like law)
# ky = "ch", gy = "j", hw = "sh", tw = "ch"
# ny = "ny", dw = "j", kw = "kw", hy = "hy"
# ══════════════════════════════════════════════════════════════
def twi_to_phonetic(text):
    """Convert Twi text to English phonetics for gTTS pronunciation"""
    t = text.lower()

    # Step 1: Digraphs first (order matters — do these before single letters)
    t = t.replace("ky", "ch")       # ky → ch (palatal)
    t = t.replace("gy", "j")        # gy → soft j
    t = t.replace("hw", "sh")       # hw → sh
    t = t.replace("tw", "chwi")     # tw → ch sound
    t = t.replace("dw", "j")        # dw → j sound
    t = t.replace("ny", "ny")       # ny → ny (Spanish ñ)
    t = t.replace("kw", "kw")       # kw → kw (queen)
    t = t.replace("hy", "hy")       # hy → hy

    # Step 2: Special Twi vowels
    t = t.replace("ɛ", "eh")        # ɛ → eh (open e, like "air")
    t = t.replace("ɔ", "aw")        # ɔ → aw (open o, like "law")

    # Step 3: Regular vowels — guide pronunciation
    # (leave as is, they're close enough for gTTS)

    return t


from googletrans import Translator

translator = Translator()

# ══════════════════════════════════════════════════════════════
# TWI PHONETIC CONVERTER
# Based on official Twi (Akan) phonetics:
# ɛ = "eh" (like air), ɔ = "aw" (like law)
# ky = "ch", gy = "j", hw = "sh", tw = "ch"
# ny = "ny", dw = "j", kw = "kw", hy = "hy"
# ══════════════════════════════════════════════════════════════
def twi_to_phonetic(text):
    """Convert Twi text to English phonetics for gTTS pronunciation"""
    t = text.lower()

    # Step 1: Digraphs first (order matters — do these before single letters)
    t = t.replace("ky", "ch")       # ky → ch (palatal)
    t = t.replace("gy", "j")        # gy → soft j
    t = t.replace("hw", "sh")       # hw → sh
    t = t.replace("tw", "chwi")     # tw → ch sound
    t = t.replace("dw", "j")        # dw → j sound
    t = t.replace("ny", "ny")       # ny → ny (Spanish ñ)
    t = t.replace("kw", "kw")       # kw → kw (queen)
    t = t.replace("hy", "hy")       # hy → hy

    # Step 2: Special Twi vowels
    t = t.replace("ɛ", "eh")        # ɛ → eh (open e, like "air")
    t = t.replace("ɔ", "aw")        # ɔ → aw (open o, like "law")

    # Step 3: Regular vowels — guide pronunciation
    # (leave as is, they're close enough for gTTS)

    return t


# ══════════════════════════════════════════════════════════════
# EXPANDED TWI DICTIONARY — 200+ words
# ══════════════════════════════════════════════════════════════
TWI_DICTIONARY = {

    # ── Greetings ─────────────────────────────────────────────
    "hello":           "agoo",
    "hi":              "agoo",
    "goodbye":         "nante yie",
    "bye":             "nante yie",
    "goodmorning":     "maakye",
    "good morning":    "maakye",
    "goodafternoon":   "maaha",
    "good afternoon":  "maaha",
    "goodevening":     "maadwo",
    "good evening":    "maadwo",
    "goodnight":       "daa",
    "good night":      "daa",
    "welcome":         "akwaaba",
    "howareyou":       "ete sen",
    "how are you":     "ete sen",
    "iamfine":         "me ho ye",
    "i am fine":       "me ho ye",
    "imfine":          "me ho ye",
    "seeyou":          "yɛbɛhyia",
    "see you":         "yɛbɛhyia",

    # ── Courtesies ────────────────────────────────────────────
    "please":          "mepawokyew",
    "thankyou":        "medaase",
    "thank you":       "medaase",
    "thanks":          "medaase",
    "thankyouverymuch":"medaase paa",
    "sorry":           "kafra",
    "excuse":          "kafra",
    "excuseme":        "kafra",
    "excuse me":       "kafra",
    "yes":             "aane",
    "no":              "daabi",
    "okay":            "yoo",
    "ok":              "yoo",
    "alright":         "yoo",
    "help":            "boa me",
    "please help me":  "mepawokyew boa me",
    "pleasehelpme":    "mepawokyew boa me",

    # ── People & Family ───────────────────────────────────────
    "name":            "din",
    "myname":          "me din",
    "my name":         "me din",
    "whatisyourname":  "wo din de sen",
    "what is your name": "wo din de sen",
    "mynameis":        "me din de",
    "my name is":      "me din de",
    "i":               "me",
    "you":             "wo",
    "me":              "me",
    "we":              "yɛn",
    "they":            "wɔn",
    "he":              "ɔno",
    "she":             "ɔno",
    "it":              "ɛno",
    "friend":          "adamfo",
    "friends":         "nnaafo",
    "family":          "abusua",
    "mother":          "maame",
    "father":          "agya",
    "sister":          "nuabaa",
    "brother":         "nua barima",
    "child":           "abofra",
    "baby":            "abofra",
    "children":        "mmofra",
    "man":             "barima",
    "woman":           "obaa",
    "boy":             "abarimaa",
    "girl":            "abaa",
    "person":          "onipa",
    "people":          "nnipa",
    "husband":         "kunu",
    "wife":            "yere",
    "son":             "babarima",
    "daughter":        "babaa",
    "grandfather":     "nana barima",
    "grandmother":     "nana",
    "uncle":           "wofa",
    "aunt":            "na",
    "king":            "ohene",
    "queen":           "ohemaa",
    "chief":           "odikro",

    # ── Basic Needs ───────────────────────────────────────────
    "food":            "aduane",
    "water":           "nsuo",
    "eat":             "didi",
    "drink":           "nom",
    "sleep":           "daa",
    "rest":            "home",
    "hungry":          "kɔm de me",
    "thirsty":         "nsukɔm de me",
    "sick":            "yare",
    "pain":            "yaw",
    "medicine":        "ɔduro",
    "hospital":        "asramuro",
    "doctor":          "ɔdɔkono",
    "nurse":           "nɔse",
    "toilet":          "tɔlet",
    "bathroom":        "adwenguare",
    "shower":          "guare",
    "money":           "sika",
    "market":          "dwa",
    "shop":            "tienda",
    "buy":             "tɔ",
    "sell":            "tɔn",
    "price":           "bo",
    "cheap":           "ɛhia",
    "expensive":       "ɛdɔɔso",

    # ── Emotions & Feelings ───────────────────────────────────
    "love":            "ɔdɔ",
    "i love you":      "me dɔ wo",
    "happy":           "anigye",
    "happiness":       "anigye",
    "sad":             "awerehow",
    "angry":           "abufuw",
    "scared":          "suro",
    "fear":            "suro",
    "hope":            "anidaso",
    "peace":           "asomdwoe",
    "joy":             "ahosɛpɛ",
    "pain":            "yaw",
    "tired":           "ahoɔden",
    "bored":           "anikɔ",
    "surprised":       "nwanwa",
    "confused":        "amanehunu",
    "proud":           "ahoɔfɛ",
    "lonely":          "ɔhohoo",
    "excited":         "anigye",

    # ── Descriptions (Adjectives) ─────────────────────────────
    "good":            "papa",
    "bad":             "bone",
    "big":             "kɛse",
    "large":           "kɛse",
    "small":           "ketewa",
    "little":          "ketewa",
    "hot":             "hyew",
    "cold":            "fre",
    "fast":            "ntɛm",
    "quick":           "ntɛm",
    "slow":            "brɛ brɛ",
    "strong":          "chɔkɔ",
    "weak":            "mmerɛw",
    "beautiful":       "ɛfɛ",
    "ugly":            "ɛfɛ da",
    "clean":           "fitaa",
    "dirty":           "fifiw",
    "old":             "ɛdaa",
    "new":             "foforo",
    "young":           "akokoraa",
    "rich":            "adefo",
    "poor":            "ohiani",
    "tall":            "tenten",
    "short":           "tiaa",
    "long":            "tenten",
    "hard":            "den",
    "soft":            "mmerɛw",
    "sweet":           "dɛ",
    "bitter":          "yaw",
    "sour":            "berɛ",
    "full":            "boro",
    "empty":           "hunu",
    "true":            "nokware",
    "false":           "atorɔ",
    "right":           "nyim",
    "wrong":           "tia",
    "easy":            "mmerɛw",
    "difficult":       "den",
    "important":       "ɛho hia",
    "free":            "kwa",

    # ── Places ────────────────────────────────────────────────
    "home":            "fie",
    "house":           "ofi",
    "school":          "sukuu",
    "church":          "asore",
    "mosque":          "mɔske",
    "hospital":        "asramuro",
    "market":          "dwa",
    "office":          "ofesi",
    "road":            "kwan",
    "street":          "ɛkwan",
    "city":            "kuropɔn",
    "town":            "kuro",
    "village":         "akuraa",
    "country":         "ɔman",
    "ghana":           "ghana",
    "accra":           "nkran",
    "kumasi":          "kumase",
    "africa":          "africa",
    "sea":             "po",
    "river":           "nsuo",
    "mountain":        "bepɔw",
    "forest":          "wuram",
    "farm":            "afuo",
    "field":           "mpoano",

    # ── Actions (Verbs) ───────────────────────────────────────
    "come":            "bra",
    "go":              "kɔ",
    "stop":            "gyae",
    "wait":            "twen",
    "run":             "tu mmirika",
    "walk":            "nante",
    "sit":             "tena",
    "stand":           "gyina",
    "look":            "hwɛ",
    "see":             "hunu",
    "listen":          "tie",
    "hear":            "tie",
    "speak":           "kasa",
    "say":             "ka",
    "ask":             "bisa",
    "answer":          "bua",
    "read":            "kenkan",
    "write":           "kyerɛw",
    "give":            "ma",
    "take":            "gye",
    "open":            "bue",
    "close":           "tɔ mu",
    "bring":           "fa bra",
    "send":            "soma",
    "call":            "frɛ",
    "work":            "dwuma",
    "play":            "agoru",
    "learn":           "sua",
    "teach":           "kyerɛ",
    "know":            "nim",
    "think":           "dwen",
    "want":            "pɛ",
    "need":            "hia",
    "have":            "wɔ",
    "like":            "pɛ",
    "hate":            "tan",
    "pray":            "bɔ mpae",
    "sing":            "to dwom",
    "dance":           "sa",
    "cry":             "su",
    "laugh":           "sere",
    "smile":           "sere ketewa",
    "cook":            "noa",
    "clean":           "sɔ ho",
    "wash":            "hohoro",
    "build":           "si",
    "grow":            "so",
    "die":             "wu",
    "born":            "wo",
    "live":            "tena ase",
    "fight":           "ko",
    "win":             "di nkonim",
    "lose":            "thua",
    "try":             "sɔ hwɛ",
    "start":           "hyɛ ase",
    "finish":          "wie",
    "return":          "san bra",
    "pay":             "tua",
    "count":           "kan",

    # ── Time ──────────────────────────────────────────────────
    "today":           "ɛnnɛ",
    "tomorrow":        "ɔkyena",
    "yesterday":       "ɛnnɛ twam",
    "morning":         "anɔpa",
    "afternoon":       "awia",
    "evening":         "anwummerɛ",
    "night":           "anadwo",
    "now":             "seesei",
    "time":            "bere",
    "soon":            "ntɛm",
    "late":            "ɛnkyɛ",
    "early":           "ntɛm",
    "always":          "daadaa",
    "never":           "da mmo",
    "week":            "nnawɔtwe",
    "month":           "bosome",
    "year":            "afe",
    "today":           "ɛnnɛ",

    # ── Numbers ───────────────────────────────────────────────
    "one":             "baako",
    "two":             "abien",
    "three":           "abiɛsa",
    "four":            "anan",
    "five":            "enum",
    "six":             "asia",
    "seven":           "ason",
    "eight":           "awɔtwe",
    "nine":            "akron",
    "ten":             "edu",
    "hundred":         "ɔha",
    "thousand":        "apem",

    # ── Questions ─────────────────────────────────────────────
    "what":            "dɛn",
    "where":           "hɔ",
    "when":            "bere bɛn",
    "who":             "hwan",
    "why":             "adɛn",
    "how":             "sɛn",
    "which":           "bɛn",
    "howmuch":         "sɛn",
    "how much":        "sɛn",

    # ── Colors ────────────────────────────────────────────────
    "red":             "kɔkɔɔ",
    "blue":            "bluu",
    "green":           "ahabammono",
    "white":           "fitaa",
    "black":           "tuntum",
    "yellow":          "akokɔsrade",
    "orange":          "ɔrens",
    "purple":          "purpol",
    "brown":           "aborɔnoma",
    "pink":            "pinki",

    # ── Body Parts ────────────────────────────────────────────
    "head":            "ti",
    "eye":             "ani",
    "ear":             "aso",
    "nose":            "hwene",
    "mouth":           "ɛnu",
    "hand":            "nsa",
    "foot":            "nan",
    "leg":             "nan",
    "heart":           "koma",
    "body":            "honam",
    "hair":            "owu",
    "face":            "anim",
    "back":            "akyi",
    "stomach":         "yafunu",
    "finger":          "nsateaa",

    # ── Nature ────────────────────────────────────────────────
    "sun":             "owia",
    "moon":            "osrane",
    "star":            "nsoromma",
    "rain":            "nsuo",
    "wind":            "mframa",
    "fire":            "ogya",
    "water":           "nsuo",
    "earth":           "asase",
    "sky":             "ɔsoro",
    "tree":            "dua",
    "flower":          "abɔdwese",
    "grass":           "mɔnkɔ",
    "animal":          "mmoa",
    "bird":            "anomaa",
    "fish":            "ɛnam",
    "dog":             "ɔkraman",
    "cat":             "ɔkra",
    "cow":             "nantwie",
    "goat":            "aponkye",
    "chicken":         "akokɔ",

    # ── Common Phrases ────────────────────────────────────────
    "idonotunderstand": "mente aseɛ",
    "i do not understand": "mente aseɛ",
    "idontunderstand": "mente aseɛ",
    "pleasespeakslowly": "mepawokyew kasa brɛ brɛ",
    "please speak slowly": "mepawokyew kasa brɛ brɛ",
    "whereisthebathroom": "adwenguare no wɔ hɔ",
    "ineedhelp":       "mhia mmoa",
    "i need help":     "mhia mmoa",
    "callpolice":      "frɛ polisi",
    "call police":     "frɛ polisi",
    "iamhungry":       "kɔm de me",
    "i am hungry":     "kɔm de me",
    "iamthirsty":      "nsukɔm de me",
    "i am thirsty":    "nsukɔm de me",
    "iamsick":         "me yare",
    "i am sick":       "me yare",
    "congratulations": "ayekoo",
    "wellcome":        "akwaaba",
    "blessed":         "nhyira",
    "amen":            "amen",
    "god":             "nyame",
    "church":          "asore",
    "pray":            "bɔ mpae",
    "worship":         "som",

    # ── Education & Work ──────────────────────────────────────
    "school":          "sukuu",
    "university":      "sukuu tenten",
    "teacher":         "ɔkyerɛkyerɛfo",
    "student":         "osuani",
    "book":            "nhoma",
    "pen":             "ɛpɛn",
    "pencil":          "pensɛl",
    "paper":           "krataa",
    "class":           "klass",
    "exam":            "nhwɛsoɔ",
    "work":            "adwuma",
    "job":             "adwuma",
    "office":          "ofesi",
    "business":        "adwumayɛ",
    "money":           "sika",
    "phone":           "fɔn",
    "computer":        "komputa",
    "internet":        "intanet",

    # ── Food & Drinks ─────────────────────────────────────────
    "rice":            "ɔmo",
    "bread":           "bɔrodo",
    "meat":            "ɛnam",
    "fish":            "ɛnam nsuo",
    "soup":            "nkwan",
    "fufu":            "fufu",
    "banku":           "banku",
    "kenkey":          "kɛnkɛ",
    "plantain":        "ɔpɛtɛ",
    "yam":             "ɛde",
    "pepper":          "mako",
    "salt":            "nkyene",
    "oil":             "ngo",
    "sugar":           "sikre",
    "milk":            "nufusuo",
    "tea":             "atɛ",
    "coffee":          "kofi",
    "juice":           "nsuo",
}


def get_twi_translation(text):
    """Get Twi translation for any text"""
    if not text:
        return text, ""

    # Single letter — return letter name (Twi alphabet only)
    if len(text) == 1 and text.upper().isalpha():
        '''letter_names = {
            'A':'Ah', 'B':'Bi', 'D':'Di', 'E':'Ii',
            'F':'Ef', 'G':'Gi', 'H':'He', 'I':'me',
            'K':'Kei', 'L':'El', 'M':'Em', 'N':'En',
            'O':'Oh', 'P':'Pi', 'R':'Ar', 'S':'Es',
            'T':'Ti', 'U':'U', 'W':'We', 'Y':'Wai'
        }
        return text, letter_names.get(text.upper(), text)
'''
    clean  = text.lower().strip().replace(" ", "")
    spaced = text.lower().strip()



    # Check dictionary (no spaces first, then with spaces)
    if clean in TWI_DICTIONARY:
        return text, TWI_DICTIONARY[clean]
    if spaced in TWI_DICTIONARY:
        return text, TWI_DICTIONARY[spaced]

    # Google Translate fallback
    try:
        result = translator.translate(text, src='en', dest='ak')
        if result and result.text and result.text.lower() != text.lower():
            return text, result.text
    except Exception as e:
        print(f"Translation error: {e}")

    return text, text


def get_twi_for_word(word):
    """Translate a complete word to Twi"""
    return get_twi_translation(word)


def get_twi_for_sign(sign_label):
    """Get Twi for a single sign label"""
    mapping = {'del': 'delete', 'nothing': '', 'space': 'space'}
    english = mapping.get(sign_label, sign_label)
    return get_twi_translation(english)


if __name__ == "__main__":
    tests = ["hello", "food", "water", "love", "ghana",
             "good morning", "i love you", "thank you",
             "medaase", "akwaaba"]
    for word in tests:
        eng, twi = get_twi_for_word(word)
        phonetic = twi_to_phonetic(twi)
        print(f"{eng:20} → {twi:20} → [{phonetic}]")



def get_twi_translation(text):
    """Get Twi translation for any text"""
    if not text:
        return text, ""

    # Single letter — return letter name (Twi alphabet only)
    if len(text) == 1 and text.upper().isalpha():
        '''letter_names = {
            'A':'Ah', 'B':'Bi', 'D':'Di', 'E':'Ii',
            'F':'Ef', 'G':'Gi', 'H':'He', 'I':'me',
            'K':'Kei', 'L':'El', 'M':'Em', 'N':'En',
            'O':'Oh', 'P':'Pi', 'R':'Ar', 'S':'Es',
            'T':'Ti', 'U':'U', 'W':'We', 'Y':'Wai'
        }
        return text, letter_names.get(text.upper(), text)
'''
    clean  = text.lower().strip().replace(" ", "")
    spaced = text.lower().strip()



    # Check dictionary (no spaces first, then with spaces)
    if clean in TWI_DICTIONARY:
        return text, TWI_DICTIONARY[clean]
    if spaced in TWI_DICTIONARY:
        return text, TWI_DICTIONARY[spaced]

    # Google Translate fallback
    try:
        result = translator.translate(text, src='en', dest='ak')
        if result and result.text and result.text.lower() != text.lower():
            return text, result.text
    except Exception as e:
        print(f"Translation error: {e}")

    return text, text


def get_twi_for_word(word):
    """Translate a complete word to Twi"""
    return get_twi_translation(word)


def get_twi_for_sign(sign_label):
    """Get Twi for a single sign label"""
    mapping = {'del': 'delete', 'nothing': '', 'space': 'space'}
    english = mapping.get(sign_label, sign_label)
    return get_twi_translation(english)


if __name__ == "__main__":
    tests = ["hello", "food", "water", "love", "ghana",
             "good morning", "i love you", "thank you",
             "medaase", "akwaaba"]
    for word in tests:
        eng, twi = get_twi_for_word(word)
        phonetic = twi_to_phonetic(twi)
        print(f"{eng:20} → {twi:20} → [{phonetic}]")
