# generate_audio.py
from gtts import gTTS
import os
import subprocess

# --- This script should be run on a machine with a working internet connection ---
# --- It requires 'ffmpeg' to be installed for audio conversion ---

# --- Phrase Maps ---
PHRASES = {
    "en": {
        "FIST": "Help",
        "PALM": "Stop",
        "PEACE": "Goodbye",
        "OK": "Okay",
        "THUMB_UP": "Yes",
        "THUMB_DOWN": "No",
        "POINT": "You",
        "L": "Loser",
        "THREE": "Three",
        "FOUR": "I want to eat",
        "ROCK": "Rock on",
        "PINCH": "Sorry",
        "ILY": "I love you",
        "CALL_ME": "Call me",
        "ONE": "One"
    },
    "ru": {
        "FIST": "Помогите",
        "PALM": "Стоп",
        "PEACE": "Спасибо",
        "THUMB_UP": "Да",
        "THUMB_DOWN": "Нет",
        "POINT": "Пожалуйста",
        "OK": "Окей",
        "PINCH": "Извините",
        "ILY": "Я люблю тебя",
        "CALL_ME": "Позвони мне",
        "L": "Пойдём",
        "ROCK": "Мне нужна вода",
        "THREE": "Я хочу пить",
        "FOUR": "Я хочу есть",
        "ONE": "Один"
    }
}

# --- Audio Generation ---
output_dir = "audio_files"
os.makedirs(output_dir, exist_ok=True)
lang = "ru"

print("Generating and converting audio files to WAV...")
for gesture, phrase in PHRASES[lang].items():
    mp3_path = os.path.join(output_dir, f"{gesture}.mp3")
    wav_path = os.path.join(output_dir, f"{gesture}.wav")
    
    print(f"Creating {wav_path} for phrase: '{phrase}'")
    
    # 1. Generate MP3
    tts = gTTS(text=phrase, lang=lang, slow=False)
    tts.save(mp3_path)
    
    # 2. Convert MP3 to WAV using ffmpeg
    subprocess.run([
        "ffmpeg", "-i", mp3_path, "-acodec", "pcm_s16le", "-ac", "2", "-ar", "44100", wav_path, 
        "-y", "-hide_banner", "-loglevel", "error"
    ], check=True)
    
    # 3. Clean up the MP3 file
    os.remove(mp3_path)

print("\nAudio file generation complete.")
print(f"WAV files are saved in the '{output_dir}' directory.")
print("Please transfer this entire directory to your Raspberry Pi.")
