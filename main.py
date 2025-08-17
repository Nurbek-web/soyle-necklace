import cv2
import time
import numpy as np
import mediapipe as mp
import os
import argparse
from absl import logging as absl_logging
from threading import Thread

# Local module imports
import config
from gestures import classify_gesture
from audio import GESTURE_TO_PHRASE, speak_phrase
from drawing import draw_ui, draw_landmarks, draw_debug_overlay

# Import picamera2 if on Raspberry Pi
if config.IS_RASPBERRY_PI:
    from picamera2 import Picamera2
    from libcamera import controls

class PiCameraStream:
    def __init__(self, width=640, height=480):
        self.picam2 = Picamera2()
        # Configure for full field of view, then scaled down.
        cam_props = self.picam2.camera_properties
        full_res = cam_props['PixelArraySize']
        self.picam2.configure(self.picam2.create_preview_configuration(
            main={"size": (width, height)},
            sensor={'output_size': full_res, 'bit_depth': 10}
        ))
        self.picam2.start()
        # Set white balance mode for indoor lighting
        self.picam2.set_controls({"AwbMode": controls.AwbModeEnum.Indoor})
        self.frame = None
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            self.frame = self.picam2.capture_array()
    
    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.picam2.stop()

def main(headless=False):
    # Suppress verbose logs and force CPU
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("MEDIAPIPE_DISABLE_GPU", "1")
    absl_logging.set_verbosity(absl_logging.ERROR)

    # MediaPipe Hands setup
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=config.MODEL_COMPLEXITY,
        min_detection_confidence=0.55, # Slightly higher confidence
        min_tracking_confidence=0.55
    )

    # --- Camera Initialization ---
    if config.IS_RASPBERRY_PI:
        print("Initializing Raspberry Pi camera (picamera2)...")
        stream = PiCameraStream(width=config.CAPTURE_WIDTH, height=config.CAPTURE_HEIGHT).start()
        time.sleep(1.0) # Allow camera to warm up
    else:
        # This part is now simplified as it's not the primary target
        print("Initializing USB camera (OpenCV)...")
        # For non-Pi, a simple capture is sufficient.
        # The original threaded capture can be re-added if needed.
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)

    # Application state
    stable_label = "NO_HAND"
    candidate_label = None
    candidate_since = 0.0
    last_drawn_landmarks = None
    debug_mode = config.DEBUG_OVERLAY
    audio_state = {"last_spoken_time": 0.0, "last_spoken_label": None}
    
    print("Soyle Gesture Recognition running...")
    if not headless:
        print("Press 'd' to toggle debug overlay, 'q' to quit.")
    
    try:
        while True:
            # --- Frame Capture ---
            if config.IS_RASPBERRY_PI:
                frame = stream.read()
            else:
                ok, frame = cap.read()
                if not ok: break

            # --- Gesture Recognition ---
            frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            res = hands.process(frame_rgb)
            
            h, w = frame_rgb.shape[:2]

            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            label = stable_label
            if res and res.multi_hand_landmarks:
                detected_labels = []
                for hand_lms in res.multi_hand_landmarks:
                    lm = [(int(p.x * w), int(p.y * h)) for p in hand_lms.landmark]
                    detected_labels.append(classify_gesture(lm))
                
                non_empty = [l for l in detected_labels if l not in ("UNKNOWN", "NO_HAND")]
                label = "UNKNOWN" if not non_empty else ("+".join(sorted(set(non_empty)))[:24] if len(set(non_empty)) > 1 else non_empty[0])
                last_drawn_landmarks = res.multi_hand_landmarks
            elif res:
                label = "NO_HAND"
            
            now = time.time()
            if label != candidate_label:
                candidate_label = label
                candidate_since = now
            elif (now - candidate_since) * 1000 >= config.DWELL_MS:
                stable_label = candidate_label
            
            # --- Audio & Terminal Output ---
            if headless:
                print(f"Detected: {label} -> Stable: {stable_label}", end='\r')

            if stable_label != audio_state["last_spoken_label"] and stable_label in GESTURE_TO_PHRASE:
                if (now - audio_state["last_spoken_time"]) > 1.2:
                    speak_phrase(GESTURE_TO_PHRASE[stable_label])
                    audio_state["last_spoken_time"] = now
                    audio_state["last_spoken_label"] = stable_label
                    if headless: print() # Newline after speaking
                    
            # --- Drawing ---
            draw_ui(frame_bgr, stable_label)
            draw_landmarks(frame_bgr, res.multi_hand_landmarks if res else last_drawn_landmarks)
            if debug_mode:
                draw_debug_overlay(frame_bgr, res)

            if not headless:
                cv2.imshow("Soyle | Gesture Demo", frame_bgr)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                if key == ord('d'):
                    debug_mode = not debug_mode
            
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        print("\nShutting down...")
        if config.IS_RASPBERRY_PI:
            stream.stop()
        else:
            cap.release()
        hands.close()
        if not headless:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Soyle Gesture Recognition")
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no GUI window)')
    args = parser.parse_args()

    main(headless=args.headless)
