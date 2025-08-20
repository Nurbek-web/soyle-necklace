import socket
import time
from audio import speak_phrase

# --- Audio State ---
# We use a dictionary for debouncing, ensuring sounds don't repeat too rapidly.
audio_state = {"last_spoken_label": None, "last_spoken_time": 0.0}

def handle_connection(conn):
    """
    This function now runs in the main thread for a single client.
    It listens for gesture labels and triggers the audio playback.
    """
    try:
        while True:
            # Protocol: a single byte for the label's size, then the UTF-8 label.
            size_bytes = conn.recv(1)
            if not size_bytes:
                break # Client disconnected
            
            label_size = int.from_bytes(size_bytes, 'big')
            if label_size == 0:
                continue

            # Ensure we receive all the bytes for the label
            label_bytes = b''
            while len(label_bytes) < label_size:
                chunk = conn.recv(label_size - len(label_bytes))
                if not chunk:
                    break # Client disconnected
                label_bytes += chunk
            
            if not label_bytes:
                break # Client disconnected
                
            label = label_bytes.decode('utf-8')

            now = time.time()
            # Debounce: only speak if it's a new gesture or enough time has passed.
            if label != audio_state["last_spoken_label"] or (now - audio_state["last_spoken_time"]) > 1.0:
                print(f"Received command for '{label}', playing audio...")
                speak_phrase(label)
                audio_state["last_spoken_label"] = label
                audio_state["last_spoken_time"] = now

    except (BrokenPipeError, ConnectionResetError):
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred in the connection handler: {e}")
    finally:
        print("Connection closed.")
        conn.close()

def main():
    HOST = '0.0.0.0'  # Listen on all available network interfaces
    PORT = 8485
    
    server_socket = socket.socket()
    # This option allows the address to be reused immediately after the server is closed.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen(0)
    print(f"Soyle Audio Server is running on {HOST}:{PORT}")
    print("Waiting for a client to connect...")

    try:
        while True:
            # Accept a new connection. This is a blocking call.
            conn, addr = server_socket.accept()
            print(f"Connection established with: {addr}")
            # Handle this one client until they disconnect.
            handle_connection(conn)
            print("Client disconnected. Waiting for a new connection...")
            
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("Server has been shut down successfully.")

if __name__ == "__main__":
    main()
