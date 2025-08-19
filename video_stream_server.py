# video_stream_server.py
import socket
import time
from picamera2 import Picamera2
from libcamera import controls
import simplejpeg
import cv2

def main():
    """
    This server captures video from the Pi's camera, applies corrections,
    and streams it over the network to the gesture recognition client.
    """
    print("Initializing camera...")
    picam2 = Picamera2()
    
    # Configure for a wide field of view
    config = picam2.create_video_configuration(
        main={"size": (1640, 1232)},
        lores={"size": (640, 480), "format": "YUV420"}
    )
    picam2.configure(config)
    picam2.set_controls({"AwbEnable": 1, "AwbMode": controls.AwbModeEnum.Auto})
    picam2.start()
    time.sleep(2.0)
    print("Camera initialized.")

    HOST = '0.0.0.0'
    PORT = 8486 # Using a different port to not conflict with the audio server
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(0)
        print(f"Video Stream Server started on {HOST}:{PORT}. Waiting for connection...")

        try:
            while True:
                conn, addr = server_socket.accept()
                with conn:
                    print(f"Video connection from: {addr}")
                    try:
                        while True:
                            frame_bgra = picam2.capture_array("lores")
                            frame_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
                            
                            jpeg_buffer = simplejpeg.encode_jpeg(frame_bgr, quality=80, colorspace='BGR', fastdct=True)
                            
                            size_bytes = len(jpeg_buffer).to_bytes(4, 'big')
                            conn.sendall(size_bytes)
                            conn.sendall(jpeg_buffer)
                    
                    except (BrokenPipeError, ConnectionResetError):
                        print(f"Client {addr} disconnected.")
                    finally:
                        print("Waiting for a new video connection...")

        except KeyboardInterrupt:
            print("\nShutting down video server.")
        finally:
            picam2.stop()
            print("Video server has been shut down.")

if __name__ == "__main__":
    main()
