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
from drawing import draw_ui, draw_landmarks, DebugDashboard

# Import picamera2 if on Raspberry Pi
if config.IS_RASPBERRY_PI:
    from picamera2 import Picamera2
    from libcamera import controls

class PiCameraStream:
    def __init__(self, width=640, height=480):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(
            main={"size": (width, height)},
            controls={"FrameDurationLimits": (33333, 33333)} # Lock framerate to 30fps
        ))
        self.picam2.start()
        # Initial camera settings
        self.controls = {
            "AwbMode": controls.AwbModeEnum.Tungsten,
            "ExposureTime": 10000,
            "AnalogueGain": 1.0
        }
        self.picam2.set_controls(self.controls)
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
        
    def set_exposure(self, value):
        self.controls["ExposureTime"] = int(value)
        self.picam2.set_controls(self.controls)

    def set_gain(self, value):
        self.controls["AnalogueGain"] = float(value)
        self.picam2.set_controls(self.controls)


def main(headless=False):
    absl_logging.set_verbosity(absl_logging.ERROR)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1, # Single hand for clarity in debug
        model_complexity=config.MODEL_COMPLEXITY,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    if config.IS_RASPBERRY_PI:
        stream = PiCameraStream(width=config.CAPTURE_WIDTH, height=config.CAPTURE_HEIGHT).start()
        time.sleep(1.0)
    else:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)

    # State and dashboard setup
    stable_label = "NO_HAND"
    dashboard = DebugDashboard()
    gesture_debug_info = {}

    print("Soyle Gesture Recognition running...")
    print("Camera Controls (Pi Only): [U/J] Exposure, [I/K] Gain")
    
    try:
        while True:
            if config.IS_RASPBERRY_PI:
                frame = stream.read()
            else:
                ok, frame = cap.read()
                if not ok: break

            frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            res = hands.process(frame_rgb)
            
            h, w = frame_rgb.shape[:2]
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            if res and res.multi_hand_landmarks:
                lm = [(int(p.x * w), int(p.y * h)) for p in res.multi_hand_landmarks[0].landmark]
                stable_label, gesture_debug_info = classify_gesture(lm)
            else:
                stable_label = "NO_HAND"
                gesture_debug_info = {}
            
            draw_ui(frame_bgr, stable_label)
            draw_landmarks(frame_bgr, res.multi_hand_landmarks)
            dashboard.render(frame_bgr, res, gesture_debug_info)

            cv2.imshow("Soyle | Gesture Diagnostic", frame_bgr)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            
            if config.IS_RASPBERRY_PI:
                if key == ord('u'): stream.set_exposure(stream.controls['ExposureTime'] + 1000)
                if key == ord('j'): stream.set_exposure(max(1000, stream.controls['ExposureTime'] - 1000))
                if key == ord('i'): stream.set_gain(stream.controls['AnalogueGain'] + 0.5)
                if key == ord('k'): stream.set_gain(max(1.0, stream.controls['AnalogueGain'] - 0.5))
            
    finally:
        print("\nShutting down...")
        if config.IS_RASPBERRY_PI:
            stream.stop()
        else:
            cap.release()
        hands.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
