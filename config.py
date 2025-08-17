# config.py

import os

# -----------------
# Performance/behavior knobs
# -----------------
MODEL_COMPLEXITY = int(os.environ.get("SOYLE_MODEL_COMPLEXITY", "0"))  # 0 = fast, 1 = balanced
PROCESS_EVERY_N_FRAMES = int(os.environ.get("SOYLE_PROCESS_EVERY_N_FRAMES", "2")) # 1 = realtime, 2-3 = good for Pi
DWELL_MS = int(os.environ.get("SOYLE_DWELL_MS", "450"))  # Time gesture must be stable to be recognized

# -----------------
# Camera settings
# -----------------
# Resolution; smaller is faster. 320x240 is a good starting point for Pi 4.
CAPTURE_WIDTH = int(os.environ.get("SOYLE_CAPTURE_WIDTH", "480"))
CAPTURE_HEIGHT = int(os.environ.get("SOYLE_CAPTURE_HEIGHT", "360"))
OPENCV_THREADS = int(os.environ.get("SOYLE_OPENCV_THREADS", "2")) # Threads for OpenCV processing

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
EXT_ANGLE_DEG = float(os.environ.get("SOYLE_EXT_ANGLE_DEG", "158"))   # finger extended if PIP angle >= this
CURL_ANGLE_DEG = float(os.environ.get("SOYLE_CURL_ANGLE_DEG", "135"))  # finger curled if PIP angle <= this
OK_PINCH_THRESH = float(os.environ.get("SOYLE_OK_PINCH_THRESH", "0.30"))
L_ANGLE_MIN = float(os.environ.get("SOYLE_L_ANGLE_MIN", "65"))
L_ANGLE_MAX = float(os.environ.get("SOYLE_L_ANGLE_MAX", "115"))
L_INDEX_LEN_MIN = float(os.environ.get("SOYLE_L_INDEX_LEN_MIN", "0.50"))
L_THUMB_LEN_MIN = float(os.environ.get("SOYLE_L_THUMB_LEN_MIN", "0.42"))

# -----------------
# UI and Debug
# -----------------
DEBUG_OVERLAY = os.environ.get("SOYLE_DEBUG_OVERLAY", "false").lower() == "true"
