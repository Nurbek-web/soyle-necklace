import socket
import time
from picamera2 import Picamera2
from libcamera import controls
import simplejpeg
import cv2
import numpy as np
import threading

# Import audio components
from audio import speak_phrase

# --- Audio State ---
audio_state = {"last_spoken_label": "NO_HAND", "last_spoken_time": 0.0}

def handle_audio(conn):
    """This function runs in a separate thread to handle incoming gesture labels."""
    try:
        while True:
            size_bytes = conn.recv(1)
            if not size_bytes: break
            label_size = int.from_bytes(size_bytes, 'big')
            label = conn.recv(label_size).decode('utf-8')
            if not label: break

            now = time.time()
            if label != audio_state["last_spoken_label"]:
                if (now - audio_state["last_spoken_time"]) > 1.2:
                    print(f"Received gesture '{label}', playing audio...")
                    speak_phrase(label)
                    audio_state["last_spoken_label"] = label
                    audio_state["last_spoken_time"] = now

    except (BrokenPipeError, ConnectionResetError):
        print("Audio handler: Client disconnected.")
    except Exception as e:
        print(f"Audio handler error: {e}")
    finally:
        print("Audio handler thread stopped.")

# 1. Initialize Picamera2
print("Initializing camera...")
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
# Let the camera's ISP handle white balance automatically.
picam2.set_controls({"AwbEnable": 1, "AwbMode": controls.AwbModeEnum.Auto})
picam2.start()
time.sleep(2.0) # Give camera time to initialize and for AWB to settle.
print("Camera initialized.")

# 2. Set up the server socket
HOST = '0.0.0.0' # Listen on all network interfaces
PORT = 8485
server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen(0)

print(f"Server started on {HOST}:{PORT}. Waiting for connection...")
conn, addr = server_socket.accept()
print(f"Connection from: {addr}")

# Start the audio handler thread
audio_thread = threading.Thread(target=handle_audio, args=(conn,))
audio_thread.daemon = True
audio_thread.start()

try:
    while True:
        # 3. Capture frame
        frame_bgra = picam2.capture_array()
        
        # 4. Convert to 3-channel BGR for compatibility with Mediapipe & encoding
        frame_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
        
        # 5. Encode and send frame (manual color correction removed)
        jpeg_buffer = simplejpeg.encode_jpeg(frame_bgr, quality=75, colorspace='BGR', fastdct=True)
        
        size_bytes = len(jpeg_buffer).to_bytes(4, 'big')
        conn.sendall(size_bytes)
        conn.sendall(jpeg_buffer)

except (BrokenPipeError, ConnectionResetError):
    print("Client disconnected.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
    server_socket.close()
    picam2.stop()
    print("Server shut down.")
