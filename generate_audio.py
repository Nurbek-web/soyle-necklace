# generate_audio.py
import os
import subprocess
from gtts import gTTS
import argparse

# --- Configuration ---
# You can add more languages here if gTTS supports them.
# The key is the ISO 639-1 code that gTTS uses.
PHRASES = {
    "en": {
        "FIST": "Call my family",
        "PALM": "I need help", 
        "FOUR": "I'm in pain",
        "THREE": "I can't breathe",
        "PEACE": "Where is the bathroom?",
    },
    "ru": {
        "FIST": "Позвоните моей семье",
        "PALM": "Мне нужна помощь",
        "FOUR": "Мне больно", 
        "THREE": "Я не могу дышать",
        "PEACE": "Где туалет?",
    }
}

# --- Main execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate audio files for Soyle gestures.")
    parser.add_argument('--lang', type=str, default='ru', choices=PHRASES.keys(),
                        help='Language for the audio phrases.')
    args = parser.parse_args()

    lang = args.lang
    output_dir = "audio_files"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Selected language: {lang}")
    print("Generating and converting audio files to WAV...")
    
    for gesture, phrase in PHRASES[lang].items():
        try:
            # Step 1: Generate MP3 from text using gTTS
            mp3_path = os.path.join(output_dir, f"{gesture}.mp3")
            tts = gTTS(text=phrase, lang=lang)
            tts.save(mp3_path)

            # Step 2: Convert MP3 to WAV using ffmpeg
            # aplay on Pi works best with WAV files, 44100Hz, 16-bit, stereo.
            wav_path = os.path.join(output_dir, f"{gesture}.wav")
            command = [
                'ffmpeg', '-y', '-i', mp3_path, '-ar', '44100', 
                '-ac', '2', '-acodec', 'pcm_s16le', wav_path
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Step 3: Clean up the intermediate MP3 file
            os.remove(mp3_path)
            print(f"Successfully created {wav_path}")
            
        except Exception as e:
            print(f"Failed to process gesture '{gesture}': {e}")
            print("Please ensure you have an internet connection and 'ffmpeg' is installed.")

    print("\nAudio file generation complete.")
