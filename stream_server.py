# stream_server.py
import socket
import time
from picamera2 import Picamera2
from libcamera import controls
import simplejpeg
import cv2

# 1. Initialize Picamera2
print("Initializing camera...")
picam2 = Picamera2()
# Use a standard, fast resolution for streaming
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
# Set white balance for indoor lighting BEFORE starting
picam2.set_controls({"AwbEnable": 1, "AwbMode": controls.AwbModeEnum.Tungsten})
picam2.start()
time.sleep(1) # Allow camera to warm up
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

try:
    while True:
        # 3. Capture, encode, and send frame
        frame = picam2.capture_array()
        
        # Convert from BGRA to BGR for standard JPEG encoding
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        jpeg_buffer = simplejpeg.encode_jpeg(frame_bgr, quality=70, colorspace='BGR', fastdct=True)
        
        # 4. Send the size of the jpeg buffer first
        size_bytes = len(jpeg_buffer).to_bytes(4, 'big')
        conn.sendall(size_bytes)
        
        # 5. Send the jpeg buffer
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
