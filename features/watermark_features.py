"""Watermark detection features for deepfake detection.

Detects visible AI generator watermarks, logos, and text overlays.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
from core.watermark_ocr_v2 import detect_watermark_in_video

# Try to import OCR libraries
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    from Levenshtein import distance as levenshtein_distance
    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False


def extract_watermark_features(video_path: str) -> Dict[str, float]:
    """
    Extract watermark detection features.
    
    Detects:
    - Visible AI generator watermarks/logos/text overlays
    - Persistent text patterns across frames
    - Generator-style marks in corners/edges
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with:
        - watermark_detected: bool (1.0 if detected, 0.0 otherwise)
        - watermark_confidence: float [0, 1] - confidence of detection
        - watermark_type: float - encoded type (0=text, 1=logo, 2=pattern)
        - watermark_persistence: float [0, 1] - how persistent across frames
        - watermark_corner_score: float [0, 1] - strength in corner regions
    """
    try:
        # Use existing watermark detection
        watermark_result = detect_watermark_in_video(video_path)
        
        # Extract features from result
        detected = watermark_result.get('detected', False)
        confidence = watermark_result.get('confidence', 0.0)
        watermark_type = watermark_result.get('type', 'text')
        
        # Encode type: 0=text, 1=logo, 2=pattern
        type_encoded = 0.0
        if 'logo' in watermark_type.lower():
            type_encoded = 1.0
        elif 'pattern' in watermark_type.lower():
            type_encoded = 2.0
        
        # Calculate persistence (how many frames had watermark)
        persistence = watermark_result.get('persistence', 0.0)
        
        # Corner score (watermarks often in corners)
        corner_score = watermark_result.get('corner_score', 0.0)
        
        return {
            'watermark_detected': 1.0 if detected else 0.0,
            'watermark_confidence': float(confidence),
            'watermark_type': type_encoded,
            'watermark_persistence': float(persistence),
            'watermark_corner_score': float(corner_score),
        }
        
    except Exception as e:
        print(f"[watermark_features] Error: {e}")
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

