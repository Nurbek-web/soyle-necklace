# config.py

import os

# -----------------
# Auto-detect Raspberry Pi
# -----------------
def is_raspberry_pi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception:
        pass
    return False

IS_RASPBERRY_PI = is_raspberry_pi()

# -----------------
# Performance/behavior knobs
# -----------------
MODEL_COMPLEXITY = int(os.environ.get("SOYLE_MODEL_COMPLEXITY", "0"))  # 0 = fast, 1 = balanced
PROCESS_EVERY_N_FRAMES = int(os.environ.get("SOYLE_PROCESS_EVERY_N_FRAMES", "3" if IS_RASPBERRY_PI else "1"))
DWELL_MS = int(os.environ.get("SOYLE_DWELL_MS", "450"))  # Time gesture must be stable to be recognized

# -----------------
# Camera settings
# -----------------
CAPTURE_WIDTH = int(os.environ.get("SOYLE_CAPTURE_WIDTH", "640"))
CAPTURE_HEIGHT = int(os.environ.get("SOYLE_CAPTURE_HEIGHT", "480"))
OPENCV_THREADS = int(os.environ.get("SOYLE_OPENCV_THREADS", "2"))

# -----------------
# Language and Speech settings
# -----------------
PHRASE_PROFILE = os.environ.get("SOYLE_PHRASE_PROFILE", "basic")  # basic | descriptive
SOYLE_LANG = os.environ.get("SOYLE_LANG", "ru")  # ru | en
SOYLE_TTS_VOICE = os.environ.get("SOYLE_TTS_VOICE", "")  # macOS specific optional voice name
TTS_RATE_WPM = int(os.environ.get("SOYLE_TTS_RATE_WPM", "170"))

# -----------------
# Detection thresholds (tune if gestures are not detected reliably)
# -----------------
EXT_ANGLE_DEG = float(os.environ.get("SOYLE_EXT_ANGLE_DEG", "155"))   # finger extended if PIP angle >= this
CURL_ANGLE_DEG = float(os.environ.get("SOYLE_CURL_ANGLE_DEG", "140"))  # finger curled if PIP angle <= this
OK_PINCH_THRESH = float(os.environ.get("SOYLE_OK_PINCH_THRESH", "0.32"))
L_ANGLE_MIN = float(os.environ.get("SOYLE_L_ANGLE_MIN", "60"))
L_ANGLE_MAX = float(os.environ.get("SOYLE_L_ANGLE_MAX", "120"))
L_INDEX_LEN_MIN = float(os.environ.get("SOYLE_L_INDEX_LEN_MIN", "0.48"))
L_THUMB_LEN_MIN = float(os.environ.get("SOYLE_L_THUMB_LEN_MIN", "0.40"))

# -----------------
# UI and Debug
# -----------------
# Note: Debug overlay is only visible when not in headless mode.
DEBUG_OVERLAY = os.environ.get("SOYLE_DEBUG_OVERLAY", "true" if IS_RASPBERRY_PI else "false").lower() == "true"
