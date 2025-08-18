# audio.py

import subprocess
import platform
import shutil
import json
import os

# --- Configuration (previously in config.py) ---
# These are now set directly here for simplicity on the Pi.
SOYLE_LANG = "ru"
PHRASE_PROFILE = "basic"
TTS_RATE_WPM = 170

# Phrase profiles for EN and RU
EN_DESCRIPTIVE = {
    "FIST": "Fist", "PALM": "Open palm", "PEACE": "Peace", "THUMB_UP": "Thumbs up",
    "THUMB_DOWN": "Thumbs down", "POINT": "Pointing", "OK": "Okay", "PINCH": "Pinch",
    "ILY": "I love you", "CALL_ME": "Call me", "L": "L sign", "ROCK": "Rock",
    "THREE": "Three", "FOUR": "Four",
}

EN_BASIC = {
    "FIST": "Help", "PALM": "Hello", "PEACE": "Thank you", "THUMB_UP": "Yes",
    "THUMB_DOWN": "No", "POINT": "Please", "OK": "Okay", "PINCH": "Excuse me",
    "ILY": "I love you", "CALL_ME": "Call my family", "L": "Let's go",
    "ROCK": "I need water", "THREE": "I'm thirsty", "FOUR": "I'm hungry",
}

RU_DESCRIPTIVE = {
    "FIST": "Кулак", "PALM": "Ладонь", "PEACE": "Мир", "THUMB_UP": "Палец вверх",
    "THUMB_DOWN": "Палец вниз", "POINT": "Указание", "OK": "Окей", "PINCH": "Щепоть",
    "ILY": "Я тебя люблю", "CALL_ME": "Позвони мне", "L": "Жест L", "ROCK": "Рок",
    "THREE": "Три", "FOUR": "Четыре",
}

RU_BASIC = {
    "FIST": "Помогите", "PALM": "Здравствуйте", "PEACE": "Спасибо", "THUMB_UP": "Да",
    "THUMB_DOWN": "Нет", "POINT": "Пожалуйста", "OK": "Окей", "PINCH": "Извините",
    "ILY": "Я тебя люблю", "CALL_ME": "Позвоните моей семье", "L": "Пойдём",
    "ROCK": "Мне нужна вода", "THREE": "Я хочу пить", "FOUR": "Я хочу есть",
}

if SOYLE_LANG.lower().startswith("ru"):
    base_map = dict(RU_DESCRIPTIVE if PHRASE_PROFILE == "descriptive" else {**RU_DESCRIPTIVE, **RU_BASIC})
else:
    base_map = dict(EN_DESCRIPTIVE if PHRASE_PROFILE == "descriptive" else {**EN_DESCRIPTIVE, **EN_BASIC})

GESTURE_TO_PHRASE = base_map

# Optional external override via phrases.json in the same directory
try:
    cfg_path = os.path.join(os.path.dirname(__file__), "phrases.json")
    if os.path.isfile(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            user_map = json.load(f)
            if isinstance(user_map, dict):
                GESTURE_TO_PHRASE.update({str(k): str(v) for k, v in user_map.items()})
except Exception:
    pass

def set_pi_volume(level="100%"):
    """Set the system volume on a Raspberry Pi."""
    if shutil.which("amixer"):
        try:
            subprocess.run(["amixer", "set", "Master", level], check=True)
            print(f"System volume set to {level}.")
        except Exception as e:
            print(f"Could not set volume: {e}")

def speak_phrase(phrase: str):
    """Speak a short phrase. macOS: say; Linux: espeak/spd-say."""
    try:
        system = platform.system()
        if system == "Darwin":
            args = ["say"]
            if SOYLE_LANG.lower().startswith("ru"):
                args += ["-v", "Milena"]
            args += ["-r", str(TTS_RATE_WPM), phrase]
            subprocess.Popen(args)
        elif system == "Linux":
            # Use a more direct method for speech-dispatcher that is more robust.
            if shutil.which("spd-say"):
                subprocess.run(['spd-say', '-w', '-l', 'ru', phrase], check=True)
            elif shutil.which("espeak"):
                subprocess.run(['espeak', '-v', 'ru', '-s', str(TTS_RATE_WPM), phrase], check=True)
            else:
                print("No TTS engine found.")
    except Exception as e:
        print(f"Error speaking phrase: {e}")
