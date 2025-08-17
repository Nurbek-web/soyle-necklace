# drawing.py

import cv2
import mediapipe as mp

mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

class DebugDashboard:
    def __init__(self, x_offset=10, y_offset=70, font_size=0.5, font_color=(0, 255, 255)):
        self.x = x_offset
        self.y = y_offset
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_size = font_size
        self.color = font_color
        self.line_height = int(self.font_size * 35)

    def _put_text(self, frame, text, line_num):
        cv2.putText(frame, text, (self.x, self.y + line_num * self.line_height), 
                    self.font, self.font_size, self.color, 1)

    def render(self, frame, res, gesture_debug_info):
        if not res or not res.multi_hand_landmarks:
            self._put_text(frame, "No hand detected", 0)
            return

        # Handedness and Confidence
        handedness = res.multi_handedness[0].classification[0]
        hand = handedness.label
        confidence = handedness.score
        self._put_text(frame, f"Hand: {hand} ({confidence:.2f})", 0)
        
        # Finger States and Angles
        if gesture_debug_info and 'states' in gesture_debug_info:
            states = gesture_debug_info['states']
            angles = gesture_debug_info['angles']
            self._put_text(frame, "Finger States | Angles", 1)
            self._put_text(frame, f"- TH: {states['TH']:<10} | {angles['TH']:.1f}", 2)
            self._put_text(frame, f"- IX: {states['IX']:<10} | {angles['IX']:.1f}", 3)
            self._put_text(frame, f"- MD: {states['MD']:<10} | {angles['MD']:.1f}", 4)
            self._put_text(frame, f"- RG: {states['RG']:<10} | {angles['RG']:.1f}", 5)
            self._put_text(frame, f"- PK: {states['PK']:<10} | {angles['PK']:.1f}", 6)

def draw_ui(frame, stable_label):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(frame, f"Gesture: {stable_label}", (18, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 2)

def draw_landmarks(frame, landmarks):
    if landmarks:
        for hand_lms in landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
