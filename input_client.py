import cv2
import socket
import numpy as np
import time

# --- Connection Settings ---
PI_ADDRESS = "172.20.10.2" # The IP address of your Raspberry Pi
PORT = 8485

# --- Key to Gesture Mapping ---
KEY_TO_GESTURE = {
    ord('1'): "ONE",       ord('2'): "PEACE",
    ord('3'): "THREE",     ord('4'): "FOUR",
    ord('5'): "PALM",      ord('f'): "FIST",
    ord('o'): "OK",        ord('p'): "POINT",
    ord('l'): "L",         ord('r'): "ROCK",
    ord('i'): "ILY",       ord('c'): "CALL_ME",
    ord('t'): "THUMB_UP",  ord('d'): "THUMB_DOWN",
}

def send_gesture_command(sock, gesture_label):
    """Sends a gesture command to the server."""
    if not gesture_label:
        return
    try:
        label_bytes = gesture_label.encode('utf-8')
        size_bytes = len(label_bytes).to_bytes(1, 'big')
        sock.sendall(size_bytes)
        sock.sendall(label_bytes)
        print(f"Sent command: '{gesture_label}'")
    except (BrokenPipeError, ConnectionResetError):
        print("Connection lost. Could not send command.")
        return False
    return True

def main():
    print(f"Attempting to connect to Raspberry Pi Audio Server at {PI_ADDRESS}:{PORT}...")
    
    try:
        with socket.socket() as client_socket:
            client_socket.connect((PI_ADDRESS, PORT))
            print("Connection successful! Press keys to send gestures. Press 'q' to quit.")

            # Create a simple UI window
            window_name = "Soyle | Keyboard Controller"
            ui_image = np.zeros((200, 400, 3), dtype=np.uint8)
            cv2.putText(ui_image, "Keyboard Controller Active", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(ui_image, "Press keys to trigger sounds.", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(ui_image, "Press 'q' to quit.", (110, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            last_key = -1
            
            while True:
                cv2.imshow(window_name, ui_image)
                key = cv2.waitKey(1) & 0xFF

                if key != 255 and key != last_key: # New key pressed
                    if key in KEY_TO_GESTURE:
                        if not send_gesture_command(client_socket, KEY_TO_GESTURE[key]):
                            break # Connection failed, exit loop
                    elif key == ord('q'):
                        break
                
                last_key = key
                
                # Check if the window was closed
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break

    except ConnectionRefusedError:
        print(f"Connection refused. Is the stream_server.py script running on the Pi?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cv2.destroyAllWindows()
        print("Client shut down.")

if __name__ == "__main__":
    main()
