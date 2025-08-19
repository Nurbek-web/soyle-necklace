# stream_client.py
import cv2
import socket
import numpy as np
import simplejpeg
import mediapipe as mp
import time

# --- Connection Settings ---
PI_ADDRESS = "172.20.10.2"
AUDIO_PORT = 8485
VIDEO_PORT = 8486

# --- Manual Gesture Override ---
KEY_TO_GESTURE = {
    ord('1'): "ONE",       ord('2'): "PEACE",
    ord('3'): "THREE",     ord('4'): "FOUR",
    ord('5'): "PALM",      ord('f'): "FIST",
    ord('o'): "OK",        ord('p'): "POINT",
    ord('l'): "L",         ord('r'): "ROCK",
    ord('i'): "ILY",       ord('c'): "CALL_ME",
    ord('t'): "THUMB_UP",  ord('d'): "THUMB_DOWN",
    ord('s'): "PINCH",
}

# --- Local Mac module imports ---
from gestures import classify_gesture
from drawing import draw_ui, draw_landmarks, DebugDashboard

def send_audio_command(sock, gesture_label):
    """Sends a gesture label to the audio server."""
    if not gesture_label: return
    try:
        label_bytes = gesture_label.encode('utf-8')
        size_bytes = len(label_bytes).to_bytes(1, 'big')
        sock.sendall(size_bytes)
        sock.sendall(label_bytes)
    except (BrokenPipeError, ConnectionResetError):
        print("Audio server connection lost.")

def main():
    # --- MediaPipe Hands setup ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False, max_num_hands=1,
        min_detection_confidence=0.6, min_tracking_confidence=0.6
    )

    # --- State and Dashboard ---
    dashboard = DebugDashboard()
    stable_label = "CONNECTING"
    gesture_debug_info = {}
    last_sent_label = None

    print(f"Attempting to connect to Pi Servers at {PI_ADDRESS}...")
    
    try:
        # Establish two separate connections
        audio_socket = socket.socket()
        audio_socket.connect((PI_ADDRESS, AUDIO_PORT))
        print(f"Audio connection on port {AUDIO_PORT} successful!")
        
        video_socket = socket.socket()
        video_socket.connect((PI_ADDRESS, VIDEO_PORT))
        print(f"Video connection on port {VIDEO_PORT} successful!")
        
        with audio_socket, video_socket:
            while True:
                # 1. Handle keyboard input for manual override
                key = cv2.waitKey(1) & 0xFF
                manual_gesture = KEY_TO_GESTURE.get(key)
                
                if manual_gesture:
                    send_audio_command(audio_socket, manual_gesture)
                    last_sent_label = manual_gesture
                    print(f"MANUAL OVERRIDE: Sent '{manual_gesture}'")
                elif key == ord('q'):
                    break

                # 2. Receive and decode video frame
                size_bytes = video_socket.recv(4)
                if not size_bytes: break
                frame_size = int.from_bytes(size_bytes, 'big')

                jpeg_buffer = b''
                while len(jpeg_buffer) < frame_size:
                    chunk = video_socket.recv(frame_size - len(jpeg_buffer))
                    if not chunk: break
                    jpeg_buffer += chunk
                
                if not jpeg_buffer: break
                frame = simplejpeg.decode_jpeg(jpeg_buffer, colorspace='BGR')

                # 3. Process the frame for gesture recognition
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = hands.process(frame_rgb)
                
                h, w = frame.shape[:2]
                if res.multi_hand_landmarks:
                    lm = [(int(p.x * w), int(p.y * h)) for p in res.multi_hand_landmarks[0].landmark]
                    stable_label, gesture_debug_info = classify_gesture(lm)
                else:
                    stable_label = "NO_HAND"
                    gesture_debug_info = {}

                # 4. Send auto-detected gesture if it's new and not overridden
                if stable_label != last_sent_label and stable_label != "UNKNOWN" and not manual_gesture:
                    send_audio_command(audio_socket, stable_label)
                    last_sent_label = stable_label

                # 5. Draw UI and display
                # Show the last *sent* label for consistency
                display_label = manual_gesture if manual_gesture else stable_label
                draw_ui(frame, display_label)
                draw_landmarks(frame, res.multi_hand_landmarks)
                dashboard.render(frame, res, gesture_debug_info)
                cv2.imshow("Soyle | Pi Stream Client", frame)

    except ConnectionRefusedError as e:
        print(f"Connection refused. Are both servers running on the Pi? Port: {e.args[1]}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cv2.destroyAllWindows()
        hands.close()
        print("Client shut down.")

if __name__ == "__main__":
    main()
