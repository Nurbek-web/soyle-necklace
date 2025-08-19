# gestures.py

import math
import numpy as np

# --- Detection Thresholds ---
# These values were previously in config.py and are now here.
# You can tune these to make detection more or less strict.
EXT_ANGLE_DEG = 155   # finger extended if PIP angle >= this
CURL_ANGLE_DEG = 140  # finger curled if PIP angle <= this
OK_PINCH_THRESH = 0.32
L_ANGLE_MIN = 60
L_ANGLE_MAX = 120
L_INDEX_LEN_MIN = 0.48
L_THUMB_LEN_MIN = 0.40

# ---------- Landmark processing and geometry utils ----------

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def finger_is_extended(lm, tip, pip, mcp, wrist):
    return dist(lm[tip], lm[wrist]) > dist(lm[pip], lm[wrist]) > dist(lm[mcp], lm[wrist])

def angle_deg(a, b, c):
    ab = np.array(a) - np.array(b)
    cb = np.array(c) - np.array(b)
    denom = (np.linalg.norm(ab) * np.linalg.norm(cb)) + 1e-6
    cosang = np.dot(ab, cb) / denom
    cosang = max(-1.0, min(1.0, cosang))
    return math.degrees(math.acos(cosang))

def angle_between_points(a1, a0, b1, b0):
    v1 = np.array(a1) - np.array(a0)
    v2 = np.array(b1) - np.array(b0)
    denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-6
    cosang = np.dot(v1, v2) / denom
    cosang = max(-1.0, min(1.0, cosang))
    return math.degrees(math.acos(cosang))

def palm_scale(lm):
    WRIST = 0
    IX_MCP, MD_MCP, RG_MCP = 5, 9, 13
    s1 = dist(lm[WRIST], lm[IX_MCP])
    s2 = dist(lm[WRIST], lm[MD_MCP])
    s3 = dist(lm[WRIST], lm[RG_MCP])
    scale = np.median([s1, s2, s3])
    return max(scale, 1e-3)

def norm_dist(lm, i, j):
    return dist(lm[i], lm[j]) / palm_scale(lm)

# ---------- Gesture Classification Engine ----------

def classify_gesture(lm):
    WRIST = 0
    TH_TIP, TH_IP, TH_MCP = 4, 3, 2
    IX_TIP, IX_PIP, IX_MCP = 8, 6, 5
    MD_TIP, MD_PIP, MD_MCP = 12, 10, 9
    RG_TIP, RG_PIP, RG_MCP = 16, 14, 13
    PK_TIP, PK_PIP, PK_MCP = 20, 18, 17

    debug_info = {}

    def finger_state(tip, pip, mcp, ext_th=EXT_ANGLE_DEG, curl_th=CURL_ANGLE_DEG):
        ang = angle_deg(lm[tip], lm[pip], lm[mcp])
        state = "unknown"
        if ang >= ext_th: state = "extended"
        if ang <= curl_th: state = "curled"
        return state, ang

    def thumb_state():
        ang = angle_deg(lm[TH_TIP], lm[TH_IP], lm[TH_MCP])
        wrist_to_tip = dist(lm[WRIST], lm[TH_TIP])
        wrist_to_mcp = dist(lm[WRIST], lm[TH_MCP])
        state = "unknown"
        if ang >= 150 and wrist_to_tip > wrist_to_mcp * 0.85: state = "extended"
        if ang <= 120 and wrist_to_tip < wrist_to_mcp * 0.95: state = "curled"
        return state, ang

    th_s, th_a = thumb_state()
    ix_s, ix_a = finger_state(IX_TIP, IX_PIP, IX_MCP)
    md_s, md_a = finger_state(MD_TIP, MD_PIP, MD_MCP)
    rg_s, rg_a = finger_state(RG_TIP, RG_PIP, RG_MCP)
    pk_s, pk_a = finger_state(PK_TIP, PK_PIP, PK_MCP)

    debug_info['states'] = {'TH': th_s, 'IX': ix_s, 'MD': md_s, 'RG': rg_s, 'PK': pk_s}
    debug_info['angles'] = {'TH': th_a, 'IX': ix_a, 'MD': md_a, 'RG': rg_a, 'PK': pk_a}

    thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext = (s == "extended" for s in [th_s, ix_s, md_s, rg_s, pk_s])
    thumb_curled, index_curled, middle_curled, ring_curled, pinky_curled = (s == "curled" for s in [th_s, ix_s, md_s, rg_s, pk_s])

    thumb_index_tip = norm_dist(lm, TH_TIP, IX_TIP)

    if thumb_ext and index_ext and pinky_ext and middle_curled and ring_curled: return "ILY", debug_info
    if index_ext and pinky_ext and middle_curled and ring_curled: return "ROCK", debug_info
    if index_ext and middle_ext and ring_ext and pinky_ext: return "FOUR", debug_info
    if thumb_index_tip < OK_PINCH_THRESH and (middle_ext or ring_ext or pinky_ext): return "OK", debug_info
    if thumb_index_tip < OK_PINCH_THRESH and not (middle_ext or ring_ext or pinky_ext): return "PINCH", debug_info
    if thumb_ext and pinky_ext and index_curled and middle_curled and ring_curled: return "CALL_ME", debug_info
    if index_ext and thumb_ext and middle_curled and ring_curled:
        ang_t_i = angle_between_points(lm[IX_TIP], lm[IX_MCP], lm[TH_TIP], lm[TH_MCP])
        idx_len = norm_dist(lm, IX_TIP, IX_MCP)
        th_len = norm_dist(lm, TH_TIP, TH_MCP)
        if L_ANGLE_MIN <= ang_t_i <= L_ANGLE_MAX and idx_len > L_INDEX_LEN_MIN and th_len > L_THUMB_LEN_MIN:
            return "L", debug_info
    if thumb_ext and index_ext and middle_ext and ring_curled and pinky_curled: return "THREE", debug_info
    if index_ext and not thumb_ext and not middle_ext and not ring_ext and not pinky_ext: return "ONE", debug_info

    ext_count = sum([thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext])
    if ext_count <= 1 and not index_ext: return "FIST", debug_info
    if index_ext and middle_ext and ring_ext and pinky_ext and not (middle_curled or ring_curled): return "PALM", debug_info
    if index_ext and middle_ext and not (ring_ext or pinky_ext): return "PEACE", debug_info
    if thumb_ext and index_curled and middle_curled and ring_curled and pinky_curled:
        margin = max(12, palm_scale(lm) * 0.15)
        if lm[TH_TIP][1] < lm[WRIST][1] - margin: return "THUMB_UP", debug_info
        if lm[TH_TIP][1] > lm[WRIST][1] + margin: return "THUMB_DOWN", debug_info
    if index_ext and not (middle_ext or ring_ext or pinky_ext): return "POINT", debug_info

    return "UNKNOWN", debug_info
