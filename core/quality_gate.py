"""Quality gate for routing media to appropriate detection pipelines."""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
import subprocess
import json
import os
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import BLUR_MIN, BRISQUE_MAX, BITRATE_MIN, SHAKE_MAX


def compute_blur_score(frame: np.ndarray) -> float:
    """Compute blur score using Laplacian variance.
    
    Args:
        frame: Input frame (BGR or grayscale)
        
    Returns:
        Blur score (higher = less blur)
    """
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame
    
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(laplacian_var)


def compute_brisque_score(frame: np.ndarray) -> Optional[float]:
    """Compute BRISQUE (Blind/Referenceless Image Spatial Quality Evaluator) score.
    
    Simplified implementation using statistical features.
    Higher score = worse quality.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        BRISQUE score or None if computation fails
    """
    try:
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Normalize
        gray = gray.astype(np.float64) / 255.0
        
        # Compute basic statistics (simplified BRISQUE)
        mean = np.mean(gray)
        std = np.std(gray)
        
        # Compute gradient statistics
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        grad_mean = np.mean(gradient_magnitude)
        grad_std = np.std(gradient_magnitude)
        
        # Simplified BRISQUE-like score (higher = worse)
        # Real BRISQUE uses more complex features, this is an approximation
        score = 100 - (mean * 50 + std * 30 + grad_mean * 15 + grad_std * 5)
        score = max(0, min(100, score))
        
        return float(score)
    except Exception:
        return None


def get_video_bitrate(video_path: str) -> Optional[float]:
    """Get video bitrate using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Bitrate in bits per second, or None if unavailable
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=bit_rate', '-of', 'json', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            bitrate = data.get('format', {}).get('bit_rate')
            if bitrate:
                return float(bitrate)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
            json.JSONDecodeError, FileNotFoundError, KeyError):
        pass
    return None


def compute_shake_score(video_path: str, max_frames: int = 30) -> Optional[float]:
    """Compute camera shake score using optical flow.
    
    Args:
        video_path: Path to video file
        max_frames: Maximum frames to analyze
        
    Returns:
        Average shake magnitude in pixels per frame, or None
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        shake_magnitudes = []
        prev_frame = None
        frame_count = 0
        
        # Create ORB detector for feature matching
        orb = cv2.ORB_create()
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Find features and match
                kp1, des1 = orb.detectAndCompute(prev_frame, None)
                kp2, des2 = orb.detectAndCompute(gray, None)
                
                if des1 is not None and des2 is not None and len(des1) > 10 and len(des2) > 10:
                    matches = matcher.match(des1, des2)
                    matches = sorted(matches, key=lambda x: x.distance)[:50]
                    
                    if len(matches) > 10:
                        # Extract matched points
                        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                        
                        # Compute homography to compensate for camera movement
                        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                        
                        if M is not None:
                            # Compute translation from homography
                            tx = M[0, 2]
                            ty = M[1, 2]
                            shake_mag = np.sqrt(tx**2 + ty**2)
                            shake_magnitudes.append(shake_mag)
            
            prev_frame = gray
            frame_count += 1
        
        cap.release()
        
        if shake_magnitudes:
            return float(np.mean(shake_magnitudes))
        return None
    except Exception:
        return None


def assess_quality(video_path: str, sample_frames: int = 10) -> Dict:
    """Assess overall quality of video.
    
    Args:
        video_path: Path to video file
        sample_frames: Number of frames to sample for quality assessment
        
    Returns:
        Dictionary with quality metrics and status
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            'status': 'error',
            'blur': None,
            'brisque': None,
            'bitrate': None,
            'shake': None,
            'message': 'Could not open video'
        }
    
    # Sample frames for blur and BRISQUE
    blur_scores = []
    brisque_scores = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, total_frames // sample_frames)
    frame_idx = 0
    
    while len(blur_scores) < sample_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % step == 0:
            blur = compute_blur_score(frame)
            blur_scores.append(blur)
            
            brisque = compute_brisque_score(frame)
            if brisque is not None:
                brisque_scores.append(brisque)
        
        frame_idx += 1
    
    cap.release()
    
    # Compute averages
    avg_blur = np.mean(blur_scores) if blur_scores else None
    avg_brisque = np.mean(brisque_scores) if brisque_scores else None
    
    # Get bitrate
    bitrate = get_video_bitrate(video_path)
    
    # Get shake (compute separately as it requires more processing)
    shake = compute_shake_score(video_path, max_frames=30)
    
    # Determine quality status
    quality_issues = []
    if avg_blur is not None and avg_blur < BLUR_MIN:
        quality_issues.append('blur')
    if avg_brisque is not None and avg_brisque > BRISQUE_MAX:
        quality_issues.append('compression')
    if bitrate is not None and bitrate < BITRATE_MIN:
        quality_issues.append('low_bitrate')
    if shake is not None and shake > SHAKE_MAX:
        quality_issues.append('shake')
    
    status = 'low' if quality_issues else 'good'
    
    return {
        'status': status,
        'issues': quality_issues,
        'blur': avg_blur,
        'brisque': avg_brisque,
        'bitrate': bitrate,
        'shake': shake,
        'message': f'Quality issues: {", ".join(quality_issues)}' if quality_issues else 'Quality acceptable'
    }

