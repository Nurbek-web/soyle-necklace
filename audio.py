# audio.py

import subprocess
import os
import shutil

# --- Configuration ---
AUDIO_DIR = "audio_files"

def speak_phrase(gesture_label: str):
    """Plays a pre-recorded WAV file for the given gesture label using aplay."""
    try:
        if not shutil.which("aplay"):
            print("Player (aplay) not found. This is unexpected on a Pi.")
            return
            
        file_path = os.path.join(AUDIO_DIR, f"{gesture_label}.wav")

        if os.path.exists(file_path):
            # aplay is the most basic and reliable player.
            # No volume control needed as the system default is used.
            subprocess.run(["aplay", file_path], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"Warning: Audio file not found for gesture '{gesture_label}' at {file_path}")

    except Exception as e:
        print(f"Error playing audio file with aplay: {e}")
