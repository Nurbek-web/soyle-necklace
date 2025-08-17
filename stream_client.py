# stream_client.py
import cv2
import socket
import numpy as np
import simplejpeg
import mediapipe as mp
import time

# Local Mac module imports (assuming they are in the same folder)
from gestures import classify_gesture
from drawing import draw_ui, draw_landmarks, DebugDashboard

# --- Connection Settings ---
PI_ADDRESS = "172.20.10.2" # The IP address of your Raspberry Pi
PORT = 8485

def main():
    # --- MediaPipe Hands setup ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # --- Dashboard and State ---
    dashboard = DebugDashboard()
    stable_label = "CONNECTING"
    gesture_debug_info = {}

    print(f"Attempting to connect to Raspberry Pi at {PI_ADDRESS}:{PORT}...")
    
    try:
        with socket.socket() as client_socket:
            client_socket.connect((PI_ADDRESS, PORT))
            print("Connection successful!")
            
            while True:
                # 1. Receive the size of the incoming frame
                size_bytes = client_socket.recv(4)
                if not size_bytes:
                    break
                frame_size = int.from_bytes(size_bytes, 'big')

                # 2. Receive the full jpeg frame
                jpeg_buffer = b''
                while len(jpeg_buffer) < frame_size:
                    chunk = client_socket.recv(frame_size - len(jpeg_buffer))
                    if not chunk:
                        break
                    jpeg_buffer += chunk
                
                if not jpeg_buffer:
                    break

                # 3. Decode the JPEG frame
                frame = simplejpeg.decode_jpeg(jpeg_buffer, colorspace='BGR')

                # 4. Process the frame for gesture recognition
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb.flags.writeable = False
                res = hands.process(frame_rgb)
                
                h, w = frame_rgb.shape[:2]
                
                if res and res.multi_hand_landmarks:
                    lm = [(int(p.x * w), int(p.y * h)) for p in res.multi_hand_landmarks[0].landmark]
                    stable_label, gesture_debug_info = classify_gesture(lm)
                else:
                    stable_label = "NO_HAND"
                    gesture_debug_info = {}

                # 5. Draw UI and display
                draw_ui(frame, stable_label)
                draw_landmarks(frame, res.multi_hand_landmarks)
                dashboard.render(frame, res, gesture_debug_info)

                cv2.imshow("Soyle | Pi Stream Client", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except ConnectionRefusedError:
        print(f"Connection refused. Is the stream_server.py script running on the Pi?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cv2.destroyAllWindows()
        hands.close()
        print("Client shut down.")

if __name__ == "__main__":
    main()
