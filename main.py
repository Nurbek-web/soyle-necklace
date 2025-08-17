import cv2
import time
import numpy as np
import mediapipe as mp
import os
from absl import logging as absl_logging

# Local module imports
import config
from gestures import classify_gesture
from audio import GESTURE_TO_PHRASE, speak_phrase
from drawing import draw_ui, draw_landmarks, draw_debug_overlay

def main():
    # Suppress verbose logs and force CPU
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("MEDIAPIPE_DISABLE_GPU", "1")
    absl_logging.set_verbosity(absl_logging.ERROR)

    # OpenCV optimizations
    cv2.setUseOptimized(True)
    try:
        cv2.setNumThreads(config.OPENCV_THREADS)
    except:
        pass

    # MediaPipe Hands setup
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=config.MODEL_COMPLEXITY,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Standard camera capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Application state
    stable_label = "NO_HAND"
    candidate_label = None
    candidate_since = 0.0
    frame_count = 0
    last_drawn_landmarks = None
    debug_mode = config.DEBUG_OVERLAY
    
    audio_state = {
        "last_spoken_time": 0.0,
        "last_spoken_label": None
    }
    
    print("Soyle Gesture Recognition running (single-threaded mode)...")
    print("Press 'd' to toggle debug overlay, 'q' to quit.")
    
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Warning: Could not read frame from camera. Exiting.")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            res = None
            # Always process frames in this simplified mode for debugging
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False # Performance hint
            res = hands.process(rgb)
            rgb.flags.writeable = True

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
            if res and res.multi_hand_landmarks:
                draw_landmarks(frame, res.multi_hand_landmarks)
            elif last_drawn_landmarks:
                draw_landmarks(frame, last_drawn_landmarks)
            
            if debug_mode:
                draw_debug_overlay(frame, res)

            cv2.imshow("Soyle | Gesture Demo", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            if key == ord('d'):
                debug_mode = not debug_mode

            frame_count += 1
            
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down...")
        cap.release()
        hands.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
