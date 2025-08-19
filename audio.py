import subprocess
import os
import shutil

# --- Configuration ---
AUDIO_DIR = "audio_files"

def speak_phrase(gesture_label: str):
    """Plays a pre-recorded WAV file for the given gesture label using aplay."""
    # Do not play sounds for non-gestures.
    if gesture_label in ["NO_HAND", "UNKNOWN", "CONNECTING"]:
        return

    try:
        if not shutil.which("aplay"):
            print("Player (aplay) not found. This is unexpected on a Pi.")
            return
            
        file_path = os.path.join(AUDIO_DIR, f"{gesture_label}.wav")

        if os.path.exists(file_path):
            # aplay will now use the system's default device, which we
            # have configured to be the USB sound card.
            subprocess.run(["aplay", file_path], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"Warning: Audio file not found for gesture '{gesture_label}' at {file_path}")

    except Exception as e:
        print(f"Error playing audio file with aplay: {e}")
