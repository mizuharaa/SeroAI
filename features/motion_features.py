"""Motion-based and temporal consistency features for deepfake detection.

This module extracts features related to:
- Constant motion pixels (rubbery/overly uniform motion)
- Temporal identity consistency (face embedding stability)
- Optical flow statistics
- Head pose jitter
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
from core.face_detect import FaceDetector

# Try to import face embedding model
try:
    import torch
    from facenet_pytorch import MTCNN, InceptionResnetV1
    HAS_FACENET = True
except ImportError:
    HAS_FACENET = False
    # Silent - will use fallback method


def extract_motion_features(
    video_path: str,
    target_fps: float = 12.0,
    max_frames: int = 50,
    face_detector: Optional[FaceDetector] = None
) -> Dict[str, float]:
    """
    Extract motion-based and temporal consistency features.
    
    Args:
        video_path: Path to video file
        target_fps: Target FPS for frame sampling
        max_frames: Maximum number of frames to process
        face_detector: Optional face detector instance
        
    Returns:
        Dictionary of scalar features:
        - avg_optical_flow_mag_face: Average optical flow magnitude in face region
        - std_optical_flow_mag_face: Std dev of optical flow magnitude in face region
        - motion_entropy_face: Entropy of motion directions in face region
        - constant_motion_ratio: Ratio of pixels with constant motion over frames
        - temporal_identity_std: Std dev of face embedding distances over time
        - head_pose_jitter: Frame-to-frame head pose change variance
        - flow_magnitude_mean: Mean optical flow magnitude (full frame)
        - flow_magnitude_std: Std dev of optical flow magnitude (full frame)
    """
    # Extract frames
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
    
    if len(frames) < 3:
        return _default_motion_features()
    
    # Initialize face detector if not provided
    if face_detector is None:
        face_detector = FaceDetector()
    
    # Convert frames to grayscale for optical flow
    gray_frames = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames]
    
    # Compute optical flow between consecutive frames
    flows = []
    flow_magnitudes = []
    face_flow_magnitudes = []
    
    face_boxes = []
    for i, frame in enumerate(frames):
        detections = face_detector.detect_faces(frame)
        if detections:
            # Use largest face
            largest = max(detections, key=lambda d: (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1]))
            face_boxes.append(largest['bbox'])
        else:
            face_boxes.append(None)
    
    # Compute optical flow
    for i in range(1, len(gray_frames)):
        # Use Farneback optical flow
        flow = cv2.calcOpticalFlowFarneback(
            gray_frames[i-1], gray_frames[i], None,
            pyr_scale=0.5, levels=3, winsize=15, iterations=3,
            poly_n=5, poly_sigma=1.2, flags=0
        )
        flows.append(flow)
        
        # Compute flow magnitude
        mag = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        flow_magnitudes.append(mag)
        
        # Extract face region flow if face detected
        if face_boxes[i] is not None:
            x1, y1, x2, y2 = face_boxes[i]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            h, w = mag.shape
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 > x1 and y2 > y1:
                face_mag = mag[y1:y2, x1:x2]
                face_flow_magnitudes.append(face_mag)
    
    # Compute full-frame flow statistics
    if flow_magnitudes:
        all_mags = np.concatenate([m.flatten() for m in flow_magnitudes])
        flow_magnitude_mean = float(np.mean(all_mags))
        flow_magnitude_std = float(np.std(all_mags))
    else:
        flow_magnitude_mean = 0.0
        flow_magnitude_std = 0.0
    
    # Compute face region flow statistics
    if face_flow_magnitudes:
        face_all_mags = np.concatenate([m.flatten() for m in face_flow_magnitudes])
        avg_optical_flow_mag_face = float(np.mean(face_all_mags))
        std_optical_flow_mag_face = float(np.std(face_all_mags))
    else:
        avg_optical_flow_mag_face = 0.0
        std_optical_flow_mag_face = 0.0
    
    # Compute motion entropy in face region
    motion_entropy_face = _compute_motion_entropy(flows, face_boxes)
    
    # Compute constant motion ratio
    constant_motion_ratio = _compute_constant_motion_ratio(flows, face_boxes)
    
    # Compute temporal identity consistency
    temporal_identity_std = _compute_temporal_identity_std(frames, face_boxes)
    
    # Compute head pose jitter
    head_pose_jitter = _compute_head_pose_jitter(frames, face_boxes)
    
    return {
        'avg_optical_flow_mag_face': avg_optical_flow_mag_face,
        'std_optical_flow_mag_face': std_optical_flow_mag_face,
        'motion_entropy_face': motion_entropy_face,
        'constant_motion_ratio': constant_motion_ratio,
        'temporal_identity_std': temporal_identity_std,
        'head_pose_jitter': head_pose_jitter,
        'flow_magnitude_mean': flow_magnitude_mean,
        'flow_magnitude_std': flow_magnitude_std,
    }


def _compute_motion_entropy(flows: List[np.ndarray], face_boxes: List[Optional[Tuple[int, int, int, int]]]) -> float:
    """Compute entropy of motion directions in face region."""
    if not flows or not face_boxes:
        return 0.5
    
    # Collect motion directions from face regions
    directions = []
    for i, flow in enumerate(flows):
        if i + 1 < len(face_boxes) and face_boxes[i + 1] is not None:
            x1, y1, x2, y2 = face_boxes[i + 1]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            h, w = flow.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 > x1 and y2 > y1:
                face_flow = flow[y1:y2, x1:x2]
                # Compute angles (0-2π)
                angles = np.arctan2(face_flow[..., 1], face_flow[..., 0]) + np.pi
                # Filter out near-zero motion
                mags = np.sqrt(face_flow[..., 0]**2 + face_flow[..., 1]**2)
                angles = angles[mags > 0.1]
                directions.extend(angles.tolist())
    
    if len(directions) < 10:
        return 0.5
    
    # Discretize angles into bins
    n_bins = 16
    hist, _ = np.histogram(directions, bins=n_bins, range=(0, 2*np.pi))
    hist = hist + 1e-6  # Avoid log(0)
    probs = hist / np.sum(hist)
    entropy = -np.sum(probs * np.log2(probs))
    # Normalize to [0, 1] (max entropy = log2(n_bins))
    normalized_entropy = entropy / np.log2(n_bins)
    return float(normalized_entropy)


def _compute_constant_motion_ratio(flows: List[np.ndarray], face_boxes: List[Optional[Tuple[int, int, int, int]]]) -> float:
    """Compute ratio of pixels with constant motion over several frames."""
    if len(flows) < 3:
        return 0.5
    
    # Track motion vectors at each pixel location over frames
    constant_count = 0
    total_count = 0
    
    for i in range(1, len(flows)):
        if i + 1 < len(face_boxes) and face_boxes[i + 1] is not None:
            x1, y1, x2, y2 = face_boxes[i + 1]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            h, w = flows[i].shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 > x1 and y2 > y1:
                flow1 = flows[i-1][y1:y2, x1:x2]
                flow2 = flows[i][y1:y2, x1:x2]
                
                # Compute angle difference
                angle1 = np.arctan2(flow1[..., 1], flow1[..., 0])
                angle2 = np.arctan2(flow2[..., 1], flow2[..., 0])
                angle_diff = np.abs(angle1 - angle2)
                angle_diff = np.minimum(angle_diff, 2*np.pi - angle_diff)  # Wrap to [0, π]
                
                # Compute magnitude similarity
                mag1 = np.sqrt(flow1[..., 0]**2 + flow1[..., 1]**2)
                mag2 = np.sqrt(flow2[..., 0]**2 + flow2[..., 1]**2)
                mag_ratio = np.minimum(mag1, mag2) / (np.maximum(mag1, mag2) + 1e-6)
                
                # Constant motion: similar direction (within 15°) and similar magnitude (ratio > 0.8)
                constant_mask = (angle_diff < np.pi/12) & (mag_ratio > 0.8) & (mag1 > 0.5)
                constant_count += np.sum(constant_mask)
                total_count += np.sum(mag1 > 0.5)
    
    if total_count == 0:
        return 0.5
    
    ratio = constant_count / total_count
    return float(np.clip(ratio, 0.0, 1.0))


def _compute_temporal_identity_std(frames: List[np.ndarray], face_boxes: List[Optional[Tuple[int, int, int, int]]]) -> float:
    """Compute standard deviation of face embedding distances over time."""
    if not HAS_FACENET or len(frames) < 3:
        # Fallback: use face box size variance as proxy
        face_sizes = []
        for bbox in face_boxes:
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                size = (x2 - x1) * (y2 - y1)
                face_sizes.append(size)
        if len(face_sizes) > 1:
            return float(np.std(face_sizes) / (np.mean(face_sizes) + 1e-6))
        return 0.5
    
    try:
        # Load face embedding model
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        mtcnn = MTCNN(image_size=160, margin=0, device=device)
        resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        
        embeddings = []
        for i, frame in enumerate(frames):
            if face_boxes[i] is not None:
                x1, y1, x2, y2 = face_boxes[i]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                h, w = frame.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    face_crop = frame[y1:y2, x1:x2]
                    try:
                        face_tensor = mtcnn(face_crop)
                        if face_tensor is not None:
                            with torch.no_grad():
                                embedding = resnet(face_tensor.unsqueeze(0).to(device))
                                embeddings.append(embedding.cpu().numpy().flatten())
                    except Exception:
                        continue
        
        if len(embeddings) < 2:
            return 0.5
        
        # Compute pairwise distances
        embeddings = np.array(embeddings)
        distances = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                dist = np.linalg.norm(embeddings[i] - embeddings[j])
                distances.append(dist)
        
        if len(distances) == 0:
            return 0.5
        
        # Return normalized std dev
        mean_dist = np.mean(distances)
        std_dist = np.std(distances)
        if mean_dist == 0:
            return 0.5
        return float(np.clip(std_dist / mean_dist, 0.0, 1.0))
    
    except Exception as e:
        print(f"[motion_features] Error computing temporal identity: {e}")
        return 0.5


def _compute_head_pose_jitter(frames: List[np.ndarray], face_boxes: List[Optional[Tuple[int, int, int, int]]]) -> float:
    """Compute frame-to-frame head pose change variance."""
    if len(frames) < 3:
        return 0.5
    
    # Approximate head pose using face box center and size
    poses = []
    for bbox in face_boxes:
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            width = x2 - x1
            height = y2 - y1
            aspect = width / (height + 1e-6)
            poses.append([center_x, center_y, width, height, aspect])
        else:
            poses.append(None)
    
    # Compute frame-to-frame changes
    changes = []
    for i in range(1, len(poses)):
        if poses[i] is not None and poses[i-1] is not None:
            change = np.linalg.norm(np.array(poses[i]) - np.array(poses[i-1]))
            changes.append(change)
    
    if len(changes) < 2:
        return 0.5
    
    # Return normalized variance
    mean_change = np.mean(changes)
    std_change = np.std(changes)
    if mean_change == 0:
        return 0.5
    jitter = std_change / (mean_change + 1e-6)
    return float(np.clip(jitter, 0.0, 1.0))


def _default_motion_features() -> Dict[str, float]:
    """Return default feature values when insufficient frames."""
    return {
        'avg_optical_flow_mag_face': 0.0,
        'std_optical_flow_mag_face': 0.0,
        'motion_entropy_face': 0.5,
        'constant_motion_ratio': 0.5,
        'temporal_identity_std': 0.5,
        'head_pose_jitter': 0.5,
        'flow_magnitude_mean': 0.0,
        'flow_magnitude_std': 0.0,
    }

