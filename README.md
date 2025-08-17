# Soyle | Real-Time Gesture Recognition for Communication

This project is a real-time hand gesture recognition application designed to assist non-verbal communication. It uses a webcam to detect hand gestures, classifies them, and speaks the corresponding phrase in either English or Russian.

The application has been re-architected and optimized for performance on resource-constrained devices like the Raspberry Pi 4B.

## Features

- **Real-Time Performance:** Multi-threaded architecture to decouple camera I/O from ML inference, ensuring smooth video and low latency.
- **14+ Detectable Gestures:** Recognizes a wide range of single-hand gestures (Fist, Palm, Peace, Thumbs Up/Down, Point, OK, Pinch, ILY, Call Me, L, Rock, Three, Four).
- **Two-Hand Support:** Detects and classifies gestures on up to two hands simultaneously.
- **Bilingual TTS:** Speaks recognized gestures in **Russian** (default) or **English**.
- **Customizable Phrases:** Comes with two phrase profiles: `descriptive` (e.g., "Open Palm") and `basic` (e.g., "Hello"). Easily extendable with a `phrases.json` file.
- **Optimized for Raspberry Pi 4B:** Low CPU footprint, configurable resolution, and frame processing rate.
- **Debug Mode:** An on-screen overlay to visualize finger states and angles for easier tuning.

## Raspberry Pi 4B Setup Guide

### 1. Hardware Requirements

- Raspberry Pi 4B (2GB or more recommended)
- Raspberry Pi Camera Module or a USB Webcam
- Speaker connected to the Raspberry Pi (e.g., via 3.5mm jack or Bluetooth)
- MicroSD card with Raspberry Pi OS (64-bit recommended for better performance)

### 2. Software Installation

First, ensure your system is up-to-date:
```bash
sudo apt update && sudo apt upgrade -y
```

Install system dependencies, including the text-to-speech engine and libraries required by OpenCV:
```bash
sudo apt install -y python3-pip libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test
sudo apt install -y speech-dispatcher espeak-ng
```

Clone the repository and install the Python packages:
```bash
git clone <your-repo-url>
cd <your-repo-directory>
pip3 install -r requirements.txt
```
*Note: The `opencv-python-headless` package is used to avoid installing heavyweight GUI libraries on the Pi.*

### 3. Running the Application

To run the application with settings optimized for the Raspberry Pi, use the following command:

```bash
python3 main.py
```

The default configuration (`config.py`) is already tuned for the Pi. You can further optimize it using environment variables.

**Example: Running in Russian with the basic communication profile**
```bash
SOYLE_LANG=ru SOYLE_PHRASSE_PROFILE=basic python3 main.py
```

## Performance Tuning & Configuration

You can override the default settings in `config.py` using environment variables. This is the recommended way to tune the application without modifying the code.

| Environment Variable          | Default | Description                                                                 |
|-------------------------------|---------|-----------------------------------------------------------------------------|
| `SOYLE_MODEL_COMPLEXITY`      | `0`     | MediaPipe model complexity. `0` for fastest, `1` for more accurate.         |
| `SOYLE_PROCESS_EVERY_N_FRAMES`| `2`     | Process video every Nth frame. `2` or `3` is good for Pi.                     |
| `SOYLE_CAPTURE_WIDTH`         | `480`   | Camera capture width. Smaller is faster (e.g., 320).                        |
| `SOYLE_CAPTURE_HEIGHT`        | `360`   | Camera capture height. Smaller is faster (e.g., 240).                       |
| `SOYLE_LANG`                  | `ru`    | Language for TTS. `ru` or `en`.                                             |
| `SOYLE_PHRASE_PROFILE`        | `basic` | `basic` for communication phrases, `descriptive` for gesture names.           |
| `SOYLE_DEBUG_OVERLAY`         | `false` | Set to `true` to show the debug overlay by default.                           |

**Example of a highly optimized run command for an older Pi:**
```bash
SOYLE_PROCESS_EVERY_N_FRAMES=3 SOYLE_CAPTURE_WIDTH=320 SOYLE_CAPTURE_HEIGHT=240 python3 main.py
```

## User Controls

- **`d`**: Toggle the debug overlay on/off to see finger angles and states.
- **`q`** or **`ESC`**: Quit the application.
