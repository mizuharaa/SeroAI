"""Human presence detection for gating anatomy features.

Only use anatomy features (hands, mouth, eyes) when humans are
actually present in the video.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
from core.face_detect import FaceDetector

# Try to import MediaPipe for person detection
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False


def detect_human_presence(
    video_path: str,
    min_frames: int = 10,
    min_fraction: float = 0.3,
    target_fps: float = 5.0,
    max_frames: int = 30
) -> Dict[str, float]:
    """
    Detect if humans are present in the video.
    
    Uses face detection and optionally person detection to determine
    if humans are present in enough frames.
    
    Args:
        video_path: Path to video file
        min_frames: Minimum number of frames with detected human
        min_fraction: Minimum fraction of frames with detected human
        target_fps: FPS for frame sampling
        max_frames: Maximum frames to check
        
    Returns:
        Dictionary with:
        - human_present: bool (1.0 if present, 0.0 otherwise)
        - human_detection_frames: int - number of frames with human
        - human_detection_fraction: float [0, 1] - fraction of frames
        - face_detection_frames: int - frames with face detected
        - person_detection_frames: int - frames with person detected
    """
    try:
        frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
        
        if len(frames) < 1:
            return _default_human_presence()
        
        face_detector = FaceDetector()
        face_count = 0
        person_count = 0
        
        # Optional: MediaPipe person detection
        pose_detector = None
        if HAS_MEDIAPIPE:
            pose_detector = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5
            )
        
        for frame in frames:
            # Face detection
            detections = face_detector.detect_faces(frame)
            if detections:
                face_count += 1
            
            # Person detection (optional, more robust)
            if pose_detector:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose_detector.process(frame_rgb)
                if results.pose_landmarks:
                    person_count += 1
        
        total_frames = len(frames)
        face_fraction = face_count / total_frames if total_frames > 0 else 0.0
        person_fraction = person_count / total_frames if total_frames > 0 else 0.0
        
        # Human present if either face or person detected in enough frames
        human_detection_frames = max(face_count, person_count)
        human_detection_fraction = max(face_fraction, person_fraction)
        
        human_present = (
            human_detection_frames >= min_frames and
            human_detection_fraction >= min_fraction
        )
        
        if pose_detector:
            pose_detector.close()
        
        return {
            'human_present': 1.0 if human_present else 0.0,
            'human_detection_frames': float(human_detection_frames),
            'human_detection_fraction': float(human_detection_fraction),
            'face_detection_frames': float(face_count),
            'person_detection_frames': float(person_count),
        }
        
    except Exception as e:
        print(f"[human_presence] Error: {e}")
        return _default_human_presence()


def _default_human_presence() -> Dict[str, float]:
    """Return default human presence features when detection fails."""
    return {
        'human_present': 0.0,
        'human_detection_frames': 0.0,
        'human_detection_fraction': 0.0,
        'face_detection_frames': 0.0,
        'person_detection_frames': 0.0,
    }

