# drawing.py

import cv2
import mediapipe as mp
from gestures import angle_deg
from config import EXT_ANGLE_DEG, CURL_ANGLE_DEG

mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def draw_ui(frame, stable_label):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(frame, f"Gesture: {stable_label}", (18, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 2)

def draw_landmarks(frame, landmarks):
    if landmarks:
        for hand_lms in landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

def draw_debug_overlay(frame, res):
    if res is None or not res.multi_hand_landmarks:
        return

    h, w = frame.shape[:2]
    hand_lms = res.multi_hand_landmarks[0]
    lm = [(int(p.x * w), int(p.y * h)) for p in hand_lms.landmark]

    WRIST = 0
    TH_TIP, TH_IP, TH_MCP = 4, 3, 2
    IX_TIP, IX_PIP, IX_MCP = 8, 6, 5
    MD_TIP, MD_PIP, MD_MCP = 12, 10, 9
    RG_TIP, RG_PIP, RG_MCP = 16, 14, 13
    PK_TIP, PK_PIP, PK_MCP = 20, 18, 17

    def fstate_name(tip, pip, mcp):
        ang = angle_deg(lm[tip], lm[pip], lm[mcp])
        if ang >= EXT_ANGLE_DEG: return f"ext {ang:.0f}"
        if ang <= CURL_ANGLE_DEG: return f"curl {ang:.0f}"
        return f"unk {ang:.0f}"

    lines = [
        f"TH: {fstate_name(TH_TIP, TH_IP, TH_MCP)}",
        f"IX: {fstate_name(IX_TIP, IX_PIP, IX_MCP)}",
        f"MD: {fstate_name(MD_TIP, MD_PIP, MD_MCP)}",
        f"RG: {fstate_name(RG_TIP, RG_PIP, RG_MCP)}",
        f"PK: {fstate_name(PK_TIP, PK_PIP, PK_MCP)}",
    ]

    y0 = 70
    for i, txt in enumerate(lines):
        cv2.putText(frame, txt, (10, y0 + i * 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
