"""MediaPipe-based anatomy checks for deepfake detection.

This module checks for:
- Hand skeleton inconsistencies (missing/merged fingers, abnormal joint angles)
- Mouth abnormalities (unnatural opening, odd textures)
- Eye blink patterns
- Facial landmark deformations
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames

# MediaPipe solutions
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


def extract_anatomy_features(
    video_path: str,
    target_fps: float = 8.0,
    max_frames: int = 30,
    enable_hand_analysis: bool = True
) -> Dict[str, float]:
    """
    Extract anatomy-based features using MediaPipe.
    
    Args:
        video_path: Path to video file
        target_fps: Target FPS for frame sampling (lower for faster processing)
        max_frames: Maximum number of frames to process
        enable_hand_analysis: Whether to analyze hands (can be disabled if no hands expected)
        
    Returns:
        Dictionary of scalar features:
        - hand_missing_finger_ratio: Ratio of frames with missing/merged fingers
        - hand_abnormal_angle_ratio: Ratio of frames with physically implausible joint angles
        - avg_hand_landmark_confidence: Average confidence of hand landmark detection
        - mouth_open_ratio_mean: Mean mouth opening ratio
        - mouth_open_ratio_std: Std dev of mouth opening ratio
        - extreme_mouth_open_frequency: Frequency of unrealistically wide mouth openings
        - lip_sync_smoothness: Temporal smoothness of lip movement
        - eye_blink_rate: Blinks per second
        - eye_blink_irregularity: Irregularity in blink timing
    """
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
    
    if len(frames) < 3:
        return _default_anatomy_features()
    
    # Initialize MediaPipe
    hands_detector = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) if enable_hand_analysis else None
    
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Process frames
    hand_features = []
    mouth_ratios = []
    eye_ear_values = []  # Eye Aspect Ratio values
    lip_landmark_sequences = []
    
    try:
        for frame in frames:
            rgb_frame = frame
            
            # Hand analysis
            if enable_hand_analysis and hands_detector is not None:
                hand_results = hands_detector.process(rgb_frame)
                if hand_results.multi_hand_landmarks:
                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        hand_feat = _analyze_hand(hand_landmarks, rgb_frame.shape)
                        if hand_feat:
                            hand_features.append(hand_feat)
            
            # Face mesh analysis
            face_results = face_mesh.process(rgb_frame)
            if face_results.multi_face_landmarks:
                landmarks = face_results.multi_face_landmarks[0].landmark
                
                # Mouth analysis
                mouth_ratio = _compute_mouth_open_ratio(landmarks, rgb_frame.shape)
                if mouth_ratio is not None:
                    mouth_ratios.append(mouth_ratio)
                
                # Eye blink analysis
                ear = _compute_eye_aspect_ratio(landmarks, rgb_frame.shape)
                if ear is not None:
                    eye_ear_values.append(ear)
                
                # Lip landmarks for smoothness
                lip_landmarks = _extract_lip_landmarks(landmarks, rgb_frame.shape)
                if lip_landmarks is not None:
                    lip_landmark_sequences.append(lip_landmarks)
    
    finally:
        if hands_detector is not None:
            hands_detector.close()
        face_mesh.close()
    
    # Aggregate hand features
    if hand_features:
        hand_missing_finger_ratio = np.mean([f['missing_finger'] for f in hand_features])
        hand_abnormal_angle_ratio = np.mean([f['abnormal_angle'] for f in hand_features])
        avg_hand_landmark_confidence = np.mean([f['confidence'] for f in hand_features])
    else:
        hand_missing_finger_ratio = 0.0
        hand_abnormal_angle_ratio = 0.0
        avg_hand_landmark_confidence = 0.0
    
    # Mouth features
    if mouth_ratios:
        mouth_open_ratio_mean = float(np.mean(mouth_ratios))
        mouth_open_ratio_std = float(np.std(mouth_ratios))
        # Extreme opening: ratio > 2x mean (unrealistic)
        extreme_threshold = mouth_open_ratio_mean * 2.0
        extreme_mouth_open_frequency = float(np.mean([r > extreme_threshold for r in mouth_ratios]))
    else:
        mouth_open_ratio_mean = 0.0
        mouth_open_ratio_std = 0.0
        extreme_mouth_open_frequency = 0.0
    
    # Lip sync smoothness (temporal consistency)
    lip_sync_smoothness = _compute_lip_smoothness(lip_landmark_sequences)
    
    # Eye blink features
    eye_blink_rate, eye_blink_irregularity = _analyze_blinks(eye_ear_values, target_fps)
    
    return {
        'hand_missing_finger_ratio': float(hand_missing_finger_ratio),
        'hand_abnormal_angle_ratio': float(hand_abnormal_angle_ratio),
        'avg_hand_landmark_confidence': float(avg_hand_landmark_confidence),
        'mouth_open_ratio_mean': float(mouth_open_ratio_mean),
        'mouth_open_ratio_std': float(mouth_open_ratio_std),
        'extreme_mouth_open_frequency': float(extreme_mouth_open_frequency),
        'lip_sync_smoothness': float(lip_sync_smoothness),
        'eye_blink_rate': float(eye_blink_rate),
        'eye_blink_irregularity': float(eye_blink_irregularity),
    }


def _analyze_hand(hand_landmarks, image_shape: Tuple[int, int, int]) -> Optional[Dict]:
    """Analyze a single hand for abnormalities."""
    h, w = image_shape[:2]
    
    # Convert landmarks to pixel coordinates
    landmarks_2d = []
    for landmark in hand_landmarks.landmark:
        landmarks_2d.append(np.array([landmark.x * w, landmark.y * h]))
    landmarks_2d = np.array(landmarks_2d)
    
    # MediaPipe hand landmarks: 21 points
    # Thumb: 0-4, Index: 5-8, Middle: 9-12, Ring: 13-16, Pinky: 17-20
    finger_indices = {
        'thumb': [0, 1, 2, 3, 4],
        'index': [5, 6, 7, 8],
        'middle': [9, 10, 11, 12],
        'ring': [13, 14, 15, 16],
        'pinky': [17, 18, 19, 20]
    }
    
    # Check for missing fingers (finger tip not visible or too close to base)
    missing_finger = False
    for finger_name, indices in finger_indices.items():
        if len(indices) >= 2:
            base = landmarks_2d[indices[0]]
            tip = landmarks_2d[indices[-1]]
            # If tip is very close to base, finger might be missing/merged
            dist = np.linalg.norm(tip - base)
            if dist < 10.0:  # Threshold in pixels
                missing_finger = True
                break
    
    # Check for abnormal joint angles
    abnormal_angle = False
    for finger_name, indices in finger_indices.items():
        if len(indices) >= 3:
            for i in range(len(indices) - 2):
                p1 = landmarks_2d[indices[i]]
                p2 = landmarks_2d[indices[i + 1]]
                p3 = landmarks_2d[indices[i + 2]]
                
                # Compute angle at joint
                v1 = p1 - p2
                v2 = p3 - p2
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
                
                # Normal finger joint angles are roughly 30-150 degrees
                # Angles < 20° or > 160° are physically implausible
                if angle < np.deg2rad(20) or angle > np.deg2rad(160):
                    abnormal_angle = True
                    break
            if abnormal_angle:
                break
    
    # Average confidence (MediaPipe doesn't provide per-landmark confidence, use 1.0 as proxy)
    confidence = 1.0
    
    return {
        'missing_finger': float(missing_finger),
        'abnormal_angle': float(abnormal_angle),
        'confidence': confidence
    }


def _compute_mouth_open_ratio(landmarks, image_shape: Tuple[int, int, int]) -> Optional[float]:
    """Compute mouth opening ratio (vertical/horizontal)."""
    # MediaPipe face mesh mouth landmarks
    # Upper lip: 13, Lower lip: 14, Left corner: 78, Right corner: 308
    MOUTH_TOP = 13
    MOUTH_BOTTOM = 14
    MOUTH_LEFT = 78
    MOUTH_RIGHT = 308
    
    h, w = image_shape[:2]
    
    try:
        top = landmarks[MOUTH_TOP]
        bottom = landmarks[MOUTH_BOTTOM]
        left = landmarks[MOUTH_LEFT]
        right = landmarks[MOUTH_RIGHT]
        
        vertical = abs(top.y - bottom.y) * h
        horizontal = abs(left.x - right.x) * w
        
        if horizontal < 1e-6:
            return None
        
        ratio = vertical / horizontal
        return float(ratio)
    except (IndexError, AttributeError):
        return None


def _compute_eye_aspect_ratio(landmarks, image_shape: Tuple[int, int, int]) -> Optional[float]:
    """Compute Eye Aspect Ratio (EAR) for blink detection."""
    # MediaPipe face mesh eye landmarks
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]
    
    h, w = image_shape[:2]
    
    try:
        # Compute EAR for left eye
        left_points = [landmarks[i] for i in LEFT_EYE]
        left_ear = _ear_from_points(left_points, h, w)
        
        # Compute EAR for right eye
        right_points = [landmarks[i] for i in RIGHT_EYE]
        right_ear = _ear_from_points(right_points, h, w)
        
        # Average EAR
        if left_ear is not None and right_ear is not None:
            return (left_ear + right_ear) / 2.0
        return None
    except (IndexError, AttributeError):
        return None


def _ear_from_points(points: List, h: int, w: int) -> Optional[float]:
    """Compute EAR from 6 eye landmark points."""
    if len(points) < 6:
        return None
    
    # Standard EAR formula: (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    p1 = np.array([points[0].x * w, points[0].y * h])
    p2 = np.array([points[1].x * w, points[1].y * h])
    p3 = np.array([points[2].x * w, points[2].y * h])
    p4 = np.array([points[3].x * w, points[3].y * h])
    p5 = np.array([points[4].x * w, points[4].y * h])
    p6 = np.array([points[5].x * w, points[5].y * h])
    
    vertical1 = np.linalg.norm(p2 - p6)
    vertical2 = np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)
    
    if horizontal < 1e-6:
        return None
    
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return float(ear)


def _extract_lip_landmarks(landmarks, image_shape: Tuple[int, int, int]) -> Optional[np.ndarray]:
    """Extract lip landmark coordinates for smoothness analysis."""
    # MediaPipe lip landmarks (outer lip contour)
    LIP_LANDMARKS = [61, 146, 91, 181, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
    
    h, w = image_shape[:2]
    
    try:
        lip_coords = []
        for idx in LIP_LANDMARKS:
            landmark = landmarks[idx]
            lip_coords.append([landmark.x * w, landmark.y * h])
        return np.array(lip_coords)
    except (IndexError, AttributeError):
        return None


def _compute_lip_smoothness(lip_sequences: List[np.ndarray]) -> float:
    """Compute temporal smoothness of lip movement."""
    if len(lip_sequences) < 2:
        return 0.5
    
    # Compute frame-to-frame changes in lip shape
    changes = []
    for i in range(1, len(lip_sequences)):
        seq1 = lip_sequences[i-1]
        seq2 = lip_sequences[i]
        if seq1.shape == seq2.shape:
            # Compute mean displacement
            displacement = np.mean(np.linalg.norm(seq2 - seq1, axis=1))
            changes.append(displacement)
    
    if len(changes) < 2:
        return 0.5
    
    # Smoothness: lower variance in changes = smoother
    mean_change = np.mean(changes)
    std_change = np.std(changes)
    if mean_change < 1e-6:
        return 1.0
    
    # Normalize: smooth = low std/mean ratio
    smoothness = 1.0 - np.clip(std_change / mean_change, 0.0, 1.0)
    return float(smoothness)


def _analyze_blinks(ear_values: List[float], fps: float) -> Tuple[float, float]:
    """Analyze blink rate and irregularity."""
    if len(ear_values) < 3:
        return 0.0, 0.5
    
    # EAR threshold for blink detection (typically 0.2-0.3)
    blink_threshold = 0.25
    
    # Detect blinks (EAR drops below threshold)
    blinks = []
    in_blink = False
    blink_start = None
    
    for i, ear in enumerate(ear_values):
        if ear < blink_threshold and not in_blink:
            in_blink = True
            blink_start = i
        elif ear >= blink_threshold and in_blink:
            in_blink = False
            if blink_start is not None:
                blinks.append((blink_start, i))
    
    # Compute blink rate (blinks per second)
    if len(ear_values) > 0:
        duration_seconds = len(ear_values) / fps
        blink_rate = len(blinks) / duration_seconds if duration_seconds > 0 else 0.0
    else:
        blink_rate = 0.0
    
    # Compute blink irregularity (variance in inter-blink intervals)
    if len(blinks) >= 2:
        intervals = []
        for i in range(1, len(blinks)):
            interval = (blinks[i][0] - blinks[i-1][1]) / fps
            intervals.append(interval)
        
        if len(intervals) > 1:
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            if mean_interval > 0:
                irregularity = std_interval / mean_interval
            else:
                irregularity = 0.5
        else:
            irregularity = 0.5
    else:
        # No blinks or only one blink - check if rate is abnormally low
        if blink_rate < 0.1:  # Less than 0.1 blinks/sec is suspicious
            irregularity = 0.8  # Flag as irregular
        else:
            irregularity = 0.5
    
    return float(blink_rate), float(np.clip(irregularity, 0.0, 1.0))


def _default_anatomy_features() -> Dict[str, float]:
    """Return default feature values when insufficient frames."""
    return {
        'hand_missing_finger_ratio': 0.0,
        'hand_abnormal_angle_ratio': 0.0,
        'avg_hand_landmark_confidence': 0.0,
        'mouth_open_ratio_mean': 0.0,
        'mouth_open_ratio_std': 0.0,
        'extreme_mouth_open_frequency': 0.0,
        'lip_sync_smoothness': 0.5,
        'eye_blink_rate': 0.0,
        'eye_blink_irregularity': 0.5,
    }

