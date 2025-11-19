"""Frequency and texture artifact detection for deepfake detection.

This module analyzes:
- High/low frequency energy ratios
- Boundary artifacts near face edges
- Texture inconsistencies
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
from core.face_detect import FaceDetector


def extract_frequency_features(
    video_path: str,
    target_fps: float = 10.0,
    max_frames: int = 20,
    face_detector: Optional[FaceDetector] = None
) -> Dict[str, float]:
    """
    Extract frequency-based features from face regions.
    
    Args:
        video_path: Path to video file
        target_fps: Target FPS for frame sampling
        max_frames: Maximum number of frames to process
        face_detector: Optional face detector instance
        
    Returns:
        Dictionary of scalar features:
        - high_freq_energy_face: High-frequency energy in face region
        - low_freq_energy_face: Low-frequency energy in face region
        - freq_energy_ratio: Ratio of high to low frequency energy
        - boundary_artifact_score: Artifact score near face boundaries
    """
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
    
    if len(frames) < 1:
        return _default_frequency_features()
    
    # Initialize face detector if not provided
    if face_detector is None:
        face_detector = FaceDetector()
    
    # Process frames
    freq_ratios = []
    boundary_scores = []
    
    for frame in frames:
        # Detect face
        detections = face_detector.detect_faces(frame)
        if not detections:
            continue
        
        # Use largest face
        largest = max(detections, key=lambda d: (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1]))
        x1, y1, x2, y2 = largest['bbox']
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            continue
        
        # Extract face crop
        face_crop = frame[y1:y2, x1:x2]
        
        # Convert to grayscale
        gray_face = cv2.cvtColor(face_crop, cv2.COLOR_RGB2GRAY) if len(face_crop.shape) == 3 else face_crop
        
        # Compute frequency features
        freq_ratio = _compute_frequency_ratio(gray_face)
        if freq_ratio is not None:
            freq_ratios.append(freq_ratio)
        
        # Compute boundary artifacts
        boundary_score = _compute_boundary_artifacts(gray_face)
        if boundary_score is not None:
            boundary_scores.append(boundary_score)
    
    # Aggregate features
    if freq_ratios:
        # Split into high and low frequency components
        # For simplicity, use mean ratio as proxy
        mean_ratio = np.mean(freq_ratios)
        # Heuristic: high ratio = more high-freq energy (could indicate artifacts)
        high_freq_energy_face = float(np.clip(mean_ratio * 0.5, 0.0, 1.0))
        low_freq_energy_face = float(np.clip((1.0 - mean_ratio) * 0.5, 0.0, 1.0))
        freq_energy_ratio = float(mean_ratio)
    else:
        high_freq_energy_face = 0.0
        low_freq_energy_face = 0.0
        freq_energy_ratio = 0.5
    
    if boundary_scores:
        boundary_artifact_score = float(np.mean(boundary_scores))
    else:
        boundary_artifact_score = 0.0
    
    return {
        'high_freq_energy_face': high_freq_energy_face,
        'low_freq_energy_face': low_freq_energy_face,
        'freq_energy_ratio': freq_energy_ratio,
        'boundary_artifact_score': boundary_artifact_score,
    }


def _compute_frequency_ratio(face_patch: np.ndarray) -> Optional[float]:
    """Compute ratio of high to low frequency energy using DCT."""
    if face_patch.size == 0:
        return None
    
    # Resize to standard size for DCT
    patch_size = 64
    if face_patch.shape[0] < patch_size or face_patch.shape[1] < patch_size:
        return None
    
    # Crop center patch
    h, w = face_patch.shape
    y1 = (h - patch_size) // 2
    x1 = (w - patch_size) // 2
    patch = face_patch[y1:y1+patch_size, x1:x1+patch_size].astype(np.float32)
    
    # Apply DCT
    dct = cv2.dct(patch)
    
    # Split into low and high frequency regions
    # Low frequency: top-left quadrant
    # High frequency: rest
    mid = patch_size // 2
    low_freq = dct[0:mid, 0:mid]
    high_freq = np.concatenate([
        dct[mid:, :].flatten(),
        dct[0:mid, mid:].flatten()
    ])
    
    # Compute energy
    low_energy = np.sum(np.abs(low_freq))
    high_energy = np.sum(np.abs(high_freq))
    
    if low_energy < 1e-6:
        return None
    
    ratio = high_energy / (low_energy + high_energy)
    return float(ratio)


def _compute_boundary_artifacts(face_patch: np.ndarray) -> Optional[float]:
    """Detect artifacts near face boundaries (edges)."""
    if face_patch.size == 0:
        return None
    
    h, w = face_patch.shape
    
    # Extract boundary regions (edges)
    boundary_width = min(5, h // 10, w // 10)
    if boundary_width < 1:
        return None
    
    # Top, bottom, left, right boundaries
    top_boundary = face_patch[0:boundary_width, :]
    bottom_boundary = face_patch[h-boundary_width:h, :]
    left_boundary = face_patch[:, 0:boundary_width]
    right_boundary = face_patch[:, w-boundary_width:w]
    
    # Compute gradient magnitude at boundaries (artifacts show as high gradients)
    def gradient_magnitude(region):
        if region.size == 0:
            return 0.0
        grad_x = cv2.Sobel(region, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(region, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(grad_x**2 + grad_y**2)
        return np.mean(mag)
    
    boundary_gradients = [
        gradient_magnitude(top_boundary),
        gradient_magnitude(bottom_boundary),
        gradient_magnitude(left_boundary),
        gradient_magnitude(right_boundary)
    ]
    
    # Compare to center region gradient
    center_y1, center_y2 = h // 4, 3 * h // 4
    center_x1, center_x2 = w // 4, 3 * w // 4
    center_region = face_patch[center_y1:center_y2, center_x1:center_x2]
    center_gradient = gradient_magnitude(center_region)
    
    if center_gradient < 1e-6:
        return 0.0
    
    # Artifact score: ratio of boundary to center gradient
    # High ratio suggests boundary artifacts
    mean_boundary_gradient = np.mean(boundary_gradients)
    artifact_score = mean_boundary_gradient / (center_gradient + 1e-6)
    
    # Normalize to [0, 1]
    artifact_score = np.clip(artifact_score / 2.0, 0.0, 1.0)
    return float(artifact_score)


def _default_frequency_features() -> Dict[str, float]:
    """Return default feature values when insufficient frames."""
    return {
        'high_freq_energy_face': 0.0,
        'low_freq_energy_face': 0.0,
        'freq_energy_ratio': 0.5,
        'boundary_artifact_score': 0.0,
    }

