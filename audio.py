# audio.py

import subprocess
import os
import shutil

# --- Configuration ---
AUDIO_DIR = "audio_files"

def speak_phrase(gesture_label: str):
    """Plays a pre-recorded audio file at max volume for the given gesture label."""
    try:
        if not shutil.which("mpg123"):
            print("Player (mpg123) not found. Please install with 'sudo apt install mpg123'")
            return
            
        file_path = os.path.join(AUDIO_DIR, f"{gesture_label}.mp3")

        if os.path.exists(file_path):
            # The '-f 32768' flag sets the volume to 100%
            subprocess.run(["mpg123", "-f", "32768", file_path], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"Warning: Audio file not found for gesture '{gesture_label}' at {file_path}")

    except Exception as e:
        print(f"Error playing audio file: {e}")
