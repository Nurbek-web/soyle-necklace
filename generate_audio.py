# generate_audio.py
from gtts import gTTS
import os

# --- This script should be run on a machine with a working internet connection ---

# --- Phrase Maps (same as before) ---
RU_BASIC = {
    "FIST": "Помогите", "PALM": "Здравствуйте", "PEACE": "Спасибо", "THUMB_UP": "Да",
    "THUMB_DOWN": "Нет", "POINT": "Пожалуйста", "OK": "Окей", "PINCH": "Извините",
    "ILY": "Я тебя люблю", "CALL_ME": "Позвоните моей семье", "L": "Пойдём",
    "ROCK": "Мне нужна вода", "THREE": "Я хочу пить", "FOUR": "Я хочу есть",
}

# --- Audio Generation ---
output_dir = "audio_files"
os.makedirs(output_dir, exist_ok=True)
lang = "ru"

print("Generating audio files...")
for gesture, phrase in RU_BASIC.items():
    file_path = os.path.join(output_dir, f"{gesture}.mp3")
    print(f"Creating {file_path} for phrase: '{phrase}'")
    
    tts = gTTS(text=phrase, lang=lang, slow=False)
    tts.save(file_path)

print("\nAudio file generation complete.")
print(f"Files are saved in the '{output_dir}' directory.")
print("Please transfer this entire directory to your Raspberry Pi.")
