import cv2
import time
import numpy as np
import mediapipe as mp
import os
import argparse
from absl import logging as absl_logging

# Local module imports
import config
from gestures import classify_gesture
from audio import GESTURE_TO_PHRASE, speak_phrase
from drawing import draw_ui, draw_landmarks, draw_debug_overlay

# Import picamera2 if on Raspberry Pi
if config.IS_RASPBERRY_PI:
    from picamera2 import Picamera2

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
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # --- Camera Initialization ---
    if config.IS_RASPBERRY_PI:
        print("Initializing Raspberry Pi camera (picamera2)...")
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"size": (config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT)}))
        picam2.start()
    else:
        print("Initializing USB camera (OpenCV)...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open USB camera.")
            return
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
    print("Press 'd' to toggle debug overlay, 'q' to quit.")
    
    try:
        while True:
            # --- Frame Capture ---
            if config.IS_RASPBERRY_PI:
                frame = picam2.capture_array()
            else:
                ok, frame = cap.read()
                if not ok:
                    print("Warning: Could not read frame from USB camera. Exiting.")
                    break

            # --- Gesture Recognition ---
            # Flip the frame horizontally for a later selfie-view display
            # and convert the BGR image to RGB.
            frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            frame.flags.writeable = False
            res = hands.process(frame)
            frame.flags.writeable = True

            # Convert the color space from RGB to BGR for drawing
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

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
            
            # --- Audio ---
            if stable_label != audio_state["last_spoken_label"] and stable_label in GESTURE_TO_PHRASE:
                if (now - audio_state["last_spoken_time"]) > 1.2:
                    speak_phrase(GESTURE_TO_PHRASE[stable_label])
                    audio_state["last_spoken_time"] = now
                    audio_state["last_spoken_label"] = stable_label
                    
            # --- Drawing ---
            draw_ui(frame, stable_label)
            draw_landmarks(frame, res.multi_hand_landmarks if res else last_drawn_landmarks)
            if debug_mode:
                draw_debug_overlay(frame, res)

            if not headless:
                cv2.imshow("Soyle | Gesture Demo", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            if key == ord('d'):
                debug_mode = not debug_mode
            
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down...")
        if config.IS_RASPBERRY_PI:
            picam2.stop()
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
