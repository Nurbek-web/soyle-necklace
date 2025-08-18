# audio.py

import subprocess
import os
import shutil

# --- Configuration ---
SOYLE_LANG = "ru-RU" # Pico TTS uses a different language code format

# --- Phrase Maps ---
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

GESTURE_TO_PHRASE = {**RU_DESCRIPTIVE, **RU_BASIC}

def set_pi_volume(level="100%"):
    """Set the system volume on a Raspberry Pi."""
    if shutil.which("amixer"):
        try:
            # Use 'PCM' as the control name, which is correct for this device.
            subprocess.run(["amixer", "set", "PCM", level], check=True)
            print(f"System volume set to {level}.")
        except Exception as e:
            print(f"Could not set volume: {e}")

def speak_phrase(phrase: str):
    """Speak a short phrase using the offline Pico TTS engine."""
    try:
        # 1. Check if the pico2wave command exists
        if not shutil.which("pico2wave"):
            print("Pico TTS (pico2wave) not found. Please install with 'sudo apt install libttspico-utils'")
            return

        # 2. Create a temporary WAV file
        temp_audio_file = "/tmp/soyle_speech.wav"
        
        # 3. Generate the audio file from text
        subprocess.run([
            "pico2wave",
            f"--lang={SOYLE_LANG}",
            f"--wave={temp_audio_file}",
            phrase
        ], check=True)

        # 4. Play the audio file using the reliable aplay command
        subprocess.run(["aplay", temp_audio_file], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except Exception as e:
        print(f"Error speaking phrase with Pico TTS: {e}")
