"""Watermark detection features for deepfake detection.

Detects visible AI generator watermarks, logos, and text overlays.
Uses the efficient detect_watermarks.py script for detection.
"""

import sys
import os
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the efficient watermark detection script
try:
    from scripts.detect_watermarks import detect_watermarks_in_video
    HAS_WATERMARK_DETECTOR = True
except ImportError:
    HAS_WATERMARK_DETECTOR = False
    print("[watermark_features] Warning: detect_watermarks script not available")


def extract_watermark_features(video_path: str) -> Dict[str, float]:
    """
    Extract watermark detection features using the efficient detection script.
    
    Detects:
    - Visible AI generator watermarks/logos/text overlays (SoraAI, Veo, Runway, etc.)
    - Persistent text patterns across frames
    - Generator-style marks in corners/edges
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with:
        - watermark_detected: float (1.0 if detected, 0.0 otherwise)
        - watermark_confidence: float [0, 1] - confidence of detection
        - watermark_type: float - encoded type (0=text, 1=logo, 2=pattern)
        - watermark_persistence: float [0, 1] - how persistent across frames
        - watermark_corner_score: float [0, 1] - strength in corner regions
    """
    if not HAS_WATERMARK_DETECTOR:
        return _default_watermark_features()
    
    try:
        # Use the improved watermark detection script
        # Sample every 1 second, analyze 5-30 frames
        watermark_result = detect_watermarks_in_video(
            video_path,
            sample_interval=1.0,
            min_frames=5,
            max_frames=30,
        )
        
        # Extract features from result
        detected = watermark_result.get('watermark_detected', False)
        confidence = watermark_result.get('watermark_confidence', 0.0)
        watermark_type = watermark_result.get('watermark_type', 'unknown')
        
        # Encode type: 0=text, 1=logo, 2=pattern/unknown
        type_encoded = 0.0
        if watermark_type == 'logo':
            type_encoded = 1.0
        elif watermark_type == 'text_logo':
            type_encoded = 0.5  # Mixed
        elif watermark_type == 'text':
            type_encoded = 0.0
        else:
            type_encoded = 2.0  # Pattern/unknown
        
        # Get detection details (new simplified format)
        detection_details = watermark_result.get('detection_details', {})
        
        # Persistence: use ratio from detection_details if available
        # The new script returns ratio = frames_with_watermark / frames_checked
        ratio = detection_details.get('ratio', 0.0)
        persistence = float(ratio) if detected else 0.0
        
        # Location score - check if watermark is in corner regions or other common locations
        locations = watermark_result.get('watermark_location', [])
        corner_regions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
        edge_regions = ['left_edge_top', 'left_edge_mid', 'left_edge_bottom', 
                       'right_edge_top', 'right_edge_mid', 'right_edge_bottom']
        
        # Calculate location score based on where watermark was found
        if any(loc in corner_regions for loc in locations):
            corner_score = 1.0  # Strong indicator in corners
        elif any(loc in edge_regions for loc in locations):
            corner_score = 0.7  # Good indicator on edges
        else:
            corner_score = 0.5  # Unknown location (or overlay)
        
        return {
            'watermark_detected': 1.0 if detected else 0.0,
            'watermark_confidence': float(confidence),
            'watermark_type': type_encoded,
            'watermark_persistence': float(persistence),
            'watermark_corner_score': float(corner_score),
            'watermark_tracking_confidence': 0.0,  # Not used in new simplified approach
        }
        
    except Exception as e:
        print(f"[watermark_features] Error detecting watermark: {e}")
        import traceback
        traceback.print_exc()
        return _default_watermark_features()


def _default_watermark_features() -> Dict[str, float]:
    """Return default watermark features when detection fails."""
    return {
        'watermark_detected': 0.0,
        'watermark_confidence': 0.0,
        'watermark_type': 0.0,
        'watermark_persistence': 0.0,
        'watermark_corner_score': 0.0,
    }

