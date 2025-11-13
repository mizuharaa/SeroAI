"""Media I/O utilities for frame and audio extraction."""

import cv2
import numpy as np
from typing import List, Optional, Tuple
import os

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import MAX_FRAMES_TO_ANALYZE, TARGET_FPS, FRAME_SAMPLE_RATE


def extract_frames(video_path: str, max_frames: Optional[int] = None, 
                   target_fps: Optional[float] = None,
                   max_dim: int = 640) -> List[np.ndarray]:
    """Extract frames from video with optional downsampling.
    
    Args:
        video_path: Path to video file
        max_frames: Maximum number of frames to extract
        target_fps: Target FPS (if None, use original)
        
    Returns:
        List of frames (RGB format)
    """
    if max_frames is None:
        max_frames = MAX_FRAMES_TO_ANALYZE
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    original_fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    # Decide sampling indices to avoid decoding every frame
    indices: List[int] = []
    if total_frames > 0:
        # If target_fps provided, approximate stride by fps ratio
        if target_fps and original_fps and original_fps > target_fps:
            stride = max(1, int(round(original_fps / target_fps)))
            # Spread samples up to max_frames
            idx = 0
            while len(indices) < max_frames and idx < total_frames:
                indices.append(idx)
                idx += stride
        else:
            # Evenly spaced indices across the clip
            step = max(1, total_frames // max_frames)
            indices = list(range(0, min(total_frames, step * max_frames), step))[:max_frames]
    else:
        # Fallback: sequential read
        indices = list(range(0, max_frames))

    frames: List[np.ndarray] = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Optional downscale to speed-up downstream stages
        if max_dim and max(frame_rgb.shape[:2]) > max_dim:
            h, w = frame_rgb.shape[:2]
            if h >= w:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            else:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            frame_rgb = cv2.resize(frame_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        frames.append(frame_rgb)
        if len(frames) >= max_frames:
            break

    cap.release()
    return frames


def extract_faces_from_frame(frame: np.ndarray, face_detector) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
    """Extract face crops from a frame.
    
    Args:
        frame: Input frame (RGB or BGR)
        face_detector: Face detection function/callable
        
    Returns:
        List of (face_crop, bbox) tuples
    """
    # This will be implemented with MediaPipe or RetinaFace
    # For now, return empty list
    return []


def load_image(image_path: str) -> Optional[np.ndarray]:
    """Load image and convert to RGB.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image array in RGB format, or None if loading fails
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

