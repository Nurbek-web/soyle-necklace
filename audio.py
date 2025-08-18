# audio.py

import subprocess
import os
import shutil

# --- Configuration ---
AUDIO_DIR = "audio_files"

def set_pi_volume(level="100%"):
    """Set the system volume on a Raspberry Pi."""
    if shutil.which("amixer"):
        try:
            subprocess.run(["amixer", "set", "PCM", level], check=True)
            print(f"System volume set to {level}")
        except Exception as e:
            print(f"Could not set volume: {e}")

def speak_phrase(gesture_label: str):
    """Plays a pre-recorded audio file for the given gesture label."""
    try:
        # 1. Check if the mpg123 player exists
        if not shutil.which("mpg123"):
            print("Player (mpg123) not found. Please install with 'sudo apt install mpg123'")
            return
            
        # 2. Construct the file path
        file_path = os.path.join(AUDIO_DIR, f"{gesture_label}.mp3")

        # 3. Play the audio file if it exists
        if os.path.exists(file_path):
            subprocess.run(["mpg123", file_path], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"Warning: Audio file not found for gesture '{gesture_label}' at {file_path}")

    except Exception as e:
        print(f"Error playing audio file: {e}")
