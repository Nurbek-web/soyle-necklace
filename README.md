# Soyle Gesture Recognition Project

This project allows for real-time gesture recognition to trigger spoken phrases, designed to aid communication. It can be run in two modes for a presentation: a highly reliable keyboard-driven mode, and an impressive camera-driven mode.

## Project Structure

- **`keyboard_client.py`**: (Runs on Mac) A keyboard-based controller with a UI. The primary, reliable way to trigger sounds for the demo.
- **`stream_client.py`**: (Runs on Mac) A camera-based client that performs gesture recognition on a video stream. The secondary, "live demo" mode.
- **`stream_server.py`**: (Runs on Pi) A lightweight server that only listens for commands and plays the corresponding audio files.
- **`video_stream_server.py`**: (Runs on Pi) A dedicated server to stream video from the camera. Used only for the live camera demo.
- **`audio.py`**: (Runs on Pi) Helper module for playing audio.
- **`gestures.py`**: (Runs on Mac) The gesture classification logic.
- **`drawing.py`**: (Runs on Mac) UI drawing utilities.
- **`generate_audio.py`**: (Runs on Mac) A script to create the `.wav` audio files from text.
- **`audio_files/`**: (On Pi) The directory containing all the generated `.wav` sound files.

---

## Presentation Day Instructions

Follow these steps for a smooth and successful presentation.

### Mode 1: Keyboard-Only Demo (Primary & Reliable)

This mode is 100% reliable as it does not depend on computer vision.

**1. On the Raspberry Pi:**

First, ensure no old processes are running. Open a terminal and run:
```bash
pkill -f stream_server.py
pkill -f video_stream_server.py
```

Then, start the audio server:
```bash
python3 stream_server.py
```
You should see a message saying `Soyle Audio Server is running...`.

**2. On your Mac:**

Run the keyboard control panel client:
```bash
python3 keyboard_client.py
```
A control panel window will appear. Click on it to give it focus, then press the keys shown on the screen to trigger the audio on the Raspberry Pi.

---

### Mode 2: Live Camera Demo (Supplemental)

Use this mode to show the live computer vision capabilities if requested.

**1. On the Raspberry Pi:**

You need to run **two** servers for this mode. It is best to use two separate terminal windows/tabs connected to your Pi.

- **In Terminal 1**, start the audio server:
  ```bash
  python3 stream_server.py
  ```

- **In Terminal 2**, start the video server:
  ```bash
  python3 video_stream_server.py
  ```

**2. On your Mac:**

Run the main gesture recognition client:
```bash
python3 stream_client.py
```
The client will connect to both servers, and you will see the live video feed. It will play sounds based on the gestures it detects, but you can also use the keyboard keys at any time to override it and manually trigger a specific sound.

---
## Final Checklist

- [ ] Ensure the Raspberry Pi is powered on and connected to the same Wi-Fi network as your Mac.
- [ ] Ensure your USB audio device is plugged into the Pi.
- [ ] Verify the Pi's IP address in `keyboard_client.py` and `stream_client.py` is correct.
- [ ] Make sure the complete `audio_files` directory has been transferred to the `soyle-necklace` folder on the Pi.
- [ ] Practice switching between the two modes. Good luck!
