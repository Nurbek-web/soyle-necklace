import cv2
import socket
import numpy as np

# --- Configuration ---
PI_ADDRESS = "172.20.10.2"
PORT = 8485

# --- Key to Gesture Mapping ---
# Organized for a 2-column layout in the UI
KEY_MAP = [
    ("f", "FIST", "Call my family"),
    ("5", "PALM", "I need help"),
    ("4", "FOUR", "I'm in pain"),
    ("3", "THREE", "I can't breathe"),
    ("2", "PEACE", "Where is the bathroom?"),
]
KEY_TO_GESTURE = {ord(k[0]): k[1] for k in KEY_MAP}

def send_gesture_command(sock, gesture_label):
    """Sends a gesture command to the server."""
    if not gesture_label: return False
    try:
        label_bytes = gesture_label.encode('utf-8')
        size_bytes = len(label_bytes).to_bytes(1, 'big')
        sock.sendall(size_bytes)
        sock.sendall(label_bytes)
        return True
    except (BrokenPipeError, ConnectionResetError):
        return False

def draw_control_panel(status, last_sent_label):
    """Creates a visually appealing UI for the keyboard client."""
    width, height = 700, 480
    panel = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Title
    cv2.putText(panel, "Demo Control Panel", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Status
    status_color = (0, 255, 0) if "Connected" in status else (0, 0, 255)
    cv2.putText(panel, f"Status: {status}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # Last Sent Command
    if last_sent_label:
        cv2.putText(panel, f"Last Command: {last_sent_label}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Instructions
    start_y = 160
    col1_x, col2_x = 30, 380
    for i, (key, _, desc) in enumerate(KEY_MAP):
        x = col1_x if i < (len(KEY_MAP) + 1) // 2 else col2_x
        y = start_y + (i % ((len(KEY_MAP) + 1) // 2)) * 30
        text = f"Press '{key.upper()}': {desc}"
        cv2.putText(panel, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
    cv2.putText(panel, "Press 'Q' to Quit", (width - 180, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
    return panel

def main():
    window_name = "Soyle | Demo Control Panel"
    status = "Connecting..."
    last_sent_label = ""
    
    try:
        with socket.socket() as client_socket:
            client_socket.connect((PI_ADDRESS, PORT))
            status = f"Connected to {PI_ADDRESS}"
            
            while True:
                panel = draw_control_panel(status, last_sent_label)
                cv2.imshow(window_name, panel)
                key = cv2.waitKey(1) & 0xFF

                if key != 255: # A key was pressed
                    if key in KEY_TO_GESTURE:
                        gesture = KEY_TO_GESTURE[key]
                        if send_gesture_command(client_socket, gesture):
                            print(f"Sent command: '{gesture}'")
                            last_sent_label = gesture
                        else:
                            status = "Connection Lost"
                            break
                    elif key == ord('q'):
                        break
                
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break

    except ConnectionRefusedError:
        status = "Connection Refused (Is server running?)"
        print(status)
    except Exception as e:
        status = f"Error: {e}"
        print(status)
    finally:
        cv2.destroyAllWindows()
        print("Client shut down.")
        
        # Display final status if connection failed
        if "Connected" not in status:
            panel = draw_control_panel(status, "")
            cv2.imshow(window_name, panel)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
