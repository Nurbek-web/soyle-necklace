# audio.py

import subprocess
import os
import shutil

# --- Configuration ---
SOYLE_LANG = "ru-RU" # Pico TTS uses a different language code format

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
