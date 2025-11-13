"""Facial dynamics heuristics using MediaPipe face mesh."""

from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List

from core.media_io import extract_frames


MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

FACE_LEFT = 234
FACE_RIGHT = 454


def _landmark_array(landmarks, image_shape):
    h, w = image_shape[:2]
    coords = []
    for landmark in landmarks:
        coords.append(np.array([landmark.x * w, landmark.y * h, landmark.z * max(w, h)]))
    return coords


def _aspect_ratio(points: List[np.ndarray], upper_idx: int, lower_idx: int, left_idx: int, right_idx: int) -> float:
    top = points[upper_idx]
    bottom = points[lower_idx]
    left = points[left_idx]
    right = points[right_idx]

    vertical = np.linalg.norm(top - bottom)
    horizontal = np.linalg.norm(left - right) + 1e-6
    return float(vertical / horizontal)


def _eye_aspect_ratio(points: List[np.ndarray], indices: List[int]) -> float:
    # Using standard EAR formula
    p2 = points[indices[1]]
    p3 = points[indices[2]]
    p4 = points[indices[3]]
    p5 = points[indices[4]]
    p6 = points[indices[5]]
    p1 = points[indices[0]]

    vertical1 = np.linalg.norm(p2 - p5)
    vertical2 = np.linalg.norm(p3 - p6)
    horizontal = np.linalg.norm(p1 - p4) + 1e-6

    return float((vertical1 + vertical2) / (2.0 * horizontal))


def analyze_face_dynamics(video_path: str, max_frames: int = 40, target_fps: int = 12) -> Dict:
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
    if not frames:
        return {
            'mouth_exaggeration_score': 0.5,
            'mouth_static_score': 0.5,
            'eye_blink_anomaly': 0.5,
            'face_symmetry_drift': 0.5,
            'frames_processed': 0
        }

    mouth_ratios: List[float] = []
    ear_values: List[float] = []
    symmetry_values: List[float] = []

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    try:
        for frame in frames:
            rgb_frame = frame
            results = face_mesh.process(rgb_frame)
            if not results.multi_face_landmarks:
                continue

            landmarks = results.multi_face_landmarks[0].landmark
            points = _landmark_array(landmarks, rgb_frame.shape)

            mouth_ratio = _aspect_ratio(points, MOUTH_TOP, MOUTH_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT)
            mouth_ratios.append(mouth_ratio)

            left_ear = _eye_aspect_ratio(points, LEFT_EYE)
            right_ear = _eye_aspect_ratio(points, RIGHT_EYE)
            ear_values.append((left_ear + right_ear) / 2.0)

            left_point = points[FACE_LEFT]
            right_point = points[FACE_RIGHT]
            symmetry = abs(left_point[0] - (rgb_frame.shape[1] - right_point[0])) / (rgb_frame.shape[1] + 1e-6)
            symmetry_values.append(symmetry)
    finally:
        face_mesh.close()

    if not mouth_ratios:
        return {
            'mouth_exaggeration_score': 0.5,
            'mouth_static_score': 0.5,
            'eye_blink_anomaly': 0.5,
            'face_symmetry_drift': 0.5,
            'frames_processed': 0
        }

    mouth_ratios = np.array(mouth_ratios)
    ear_values = np.array(ear_values) if ear_values else np.array([0.3])
    symmetry_values = np.array(symmetry_values) if symmetry_values else np.array([0.0])

    mouth_mean = float(np.mean(mouth_ratios))
    mouth_std = float(np.std(mouth_ratios))
    ear_mean = float(np.mean(ear_values))
    ear_std = float(np.std(ear_values))
    symmetry_mean = float(np.mean(symmetry_values))

    mouth_exaggeration_score = float(np.clip((mouth_mean - 0.38) * 3.0, 0.0, 1.0))
    mouth_static_score = float(np.clip((0.08 - mouth_std) * 12.0, 0.0, 1.0))
    eye_blink_anomaly = float(np.clip((0.18 - ear_std) * 10.0 + (0.25 - ear_mean) * 2.0, 0.0, 1.0))
    face_symmetry_drift = float(np.clip(symmetry_mean * 6.0, 0.0, 1.0))

    return {
        'mouth_exaggeration_score': mouth_exaggeration_score,
        'mouth_static_score': mouth_static_score,
        'eye_blink_anomaly': eye_blink_anomaly,
        'face_symmetry_drift': face_symmetry_drift,
        'frames_processed': len(mouth_ratios),
        'mouth_mean_ratio': mouth_mean,
        'mouth_std_ratio': mouth_std,
        'ear_mean': ear_mean,
        'ear_std': ear_std,
        'symmetry_mean': symmetry_mean,
    }

