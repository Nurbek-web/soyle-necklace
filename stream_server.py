# stream_server.py
import socket
import time
from picamera2 import Picamera2
from libcamera import controls
import simplejpeg
import cv2
import numpy as np
import threading

# Import audio components
from audio import GESTURE_TO_PHRASE, speak_phrase

# --- Audio State ---
# We use a simple list to hold the last spoken label, making it mutable for threads
audio_state = {"last_spoken_label": "NO_HAND", "last_spoken_time": 0.0}

def handle_audio(conn):
    """This function runs in a separate thread to handle incoming gesture labels."""
    try:
        while True:
            # 1. Receive the size of the incoming label
            size_bytes = conn.recv(1)
            if not size_bytes:
                break
            label_size = int.from_bytes(size_bytes, 'big')

            # 2. Receive the label
            label = conn.recv(label_size).decode('utf-8')
            if not label:
                break

            # 3. Speak the phrase if it's a new, valid gesture
            now = time.time()
            if label != audio_state["last_spoken_label"] and label in GESTURE_TO_PHRASE:
                if (now - audio_state["last_spoken_time"]) > 1.2:
                    print(f"Received gesture '{label}', speaking phrase...")
                    speak_phrase(GESTURE_TO_PHRASE[label])
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
# Attempt to set a good starting white balance
picam2.set_controls({"AwbEnable": 1, "AwbMode": controls.AwbModeEnum.Tungsten})
picam2.start()
time.sleep(2.0) # Give camera extra time to initialize and adjust
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
        
        # 4. Manual Color Correction to fix blue tint
        frame_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
        
        # Convert to YUV color space to isolate brightness from color
        yuv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(yuv)
        
        # Lower the 'u' channel (blue-yellow axis) to reduce blue
        u = cv2.addWeighted(u, 0.9, np.zeros_like(u), 0.1, 0)
        
        # Merge and convert back to BGR
        corrected_yuv = cv2.merge([y, u, v])
        corrected_frame = cv2.cvtColor(corrected_yuv, cv2.COLOR_YUV2BGR)
        
        # 5. Encode and send corrected frame
        jpeg_buffer = simplejpeg.encode_jpeg(corrected_frame, quality=75, colorspace='BGR', fastdct=True)
        
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
