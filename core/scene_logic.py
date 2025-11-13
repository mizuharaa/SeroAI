"""Lightweight scene logic checks: shot changes and background consistency."""

from __future__ import annotations

import cv2
import numpy as np
from typing import Dict, List

from core.media_io import extract_frames
from app.config import SCENE as SCN
import time


def _hist_diff(a: np.ndarray, b: np.ndarray) -> float:
    hist_size = 32
    hist_a = cv2.calcHist([a], [0], None, [hist_size], [0, 256])
    hist_b = cv2.calcHist([b], [0], None, [hist_size], [0, 256])
    cv2.normalize(hist_a, hist_a)
    cv2.normalize(hist_b, hist_b)
    return float(cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_BHATTACHARYYA))


def _stabilized_bg_diff(prev: np.ndarray, cur: np.ndarray) -> float:
    orb = cv2.ORB_create(200)
    kp1, des1 = orb.detectAndCompute(prev, None)
    kp2, des2 = orb.detectAndCompute(cur, None)
    if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
        return 0.0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)[:80]
    if len(matches) < 10:
        return 0.0
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 3.0)
    if H is None:
        return 0.0
    h, w = prev.shape[:2]
    warped = cv2.warpPerspective(cur, np.linalg.inv(H), (w, h))
    gray_a = cv2.cvtColor(prev, cv2.COLOR_RGB2GRAY)
    gray_b = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(gray_a, gray_b)
    return float(np.mean(diff) / 255.0)


def detect_logic_breaks(video_path: str, max_frames: int = None, target_fps: int = 15) -> Dict:
    """Detect scene logic issues such as abrupt object/material changes."""
    if max_frames is None:
        max_frames = SCN["MAX_FRAMES"]
    t0 = time.time()
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps)
    if len(frames) < 6:
        return {'flag': False, 'reasons': [], 'confidence': 0.0}

    # Shot detection via histogram differences on downsampled grayscale
    gray_frames = []
    for f in frames:
        # Downscale for speed
        h, w = f.shape[:2]
        scale_w = SCN["RESIZE_WIDTH"]
        if w > scale_w:
            f = cv2.resize(f, (scale_w, int(h * (scale_w / w))), interpolation=cv2.INTER_AREA)
        gray_frames.append(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY))
    shot_boundaries: List[int] = [0]
    for i in range(1, len(gray_frames)):
        diff = _hist_diff(gray_frames[i - 1], gray_frames[i])
        if diff > SCN["HIST_DIFF_THR"]:
            shot_boundaries.append(i)
    if shot_boundaries[-1] != len(frames) - 1:
        shot_boundaries.append(len(frames) - 1)

    # Compare background consistency within shots
    reasons: List[str] = []
    logic_score = 0.0
    for i in range(1, len(shot_boundaries)):
        # Timeout guard
        if time.time() - t0 > SCN["MAX_SECONDS"]:
            break
        start = shot_boundaries[i - 1]
        end = shot_boundaries[i]
        if end - start < 3:
            continue
        mid = (start + end) // 2
        prev = frames[mid - 1]
        cur = frames[mid + 1] if mid + 1 < len(frames) else frames[mid]
        bg_jump = _stabilized_bg_diff(prev, cur)
        # If background is stable (low jump) but colors/textures shift strongly → suspicious
        if bg_jump < 0.05:
            color_jump = _hist_diff(cv2.cvtColor(prev, cv2.COLOR_RGB2GRAY),
                                    cv2.cvtColor(cur, cv2.COLOR_RGB2GRAY))
            if color_jump > SCN["COLOR_JUMP_THR"]:
                logic_score = max(logic_score, min(1.0, (color_jump - 0.40) * 2.5 + 0.7))
                reasons.append(f"Background stable but color/texture flips within shot {i}")

    flag = logic_score >= 0.8
    confidence = float(min(1.0, logic_score))
    return {'flag': bool(flag), 'reasons': reasons, 'confidence': confidence}


