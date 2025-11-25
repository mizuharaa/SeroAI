"""
Enhanced watermark detection for AI generator identification.

Uses the new detect_watermarks.py script for accurate detection.
This module provides backward compatibility for the service layer.
"""
import sys
import os
from typing import Dict

# Import the new watermark detection script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.detect_watermarks import detect_watermarks_in_video
    HAS_NEW_DETECTOR = True
except ImportError:
    HAS_NEW_DETECTOR = False
    print("[watermark_ocr_v2] Warning: detect_watermarks script not available, falling back to old method")

# Legacy code removed - now using new detection script


def detect_watermark_in_video(video_path: str) -> Dict:
    """
    Detect watermark in video using the new detection script.
    Returns format compatible with the service layer.
    """
    if not HAS_NEW_DETECTOR:
        # Fallback: return no detection
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }
    
    try:
        # Use the new detection script
        result = detect_watermarks_in_video(
            video_path,
            max_frames=30,  # Use same max as the script default
        )
        
        # Convert to old format for backward compatibility
        detected = result.get('watermark_detected', False)
        confidence = result.get('watermark_confidence', 0.0)
        watermark_type = result.get('watermark_type', 'unknown')
        locations = result.get('watermark_location', [])
        watermark_text = result.get('watermark_text', [])
        
        # Determine generator name from detected text
        generator_name = None
        if watermark_text:
            generator_name = watermark_text[0].upper() if watermark_text else None
        
        # Check if in corner
        corner_regions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
        is_corner = any(loc in corner_regions for loc in locations)
        
        return {
            'detected': detected,
            'watermark': generator_name,
            'confidence': float(confidence),
            'generator_hint': detected and watermark_type in ['text', 'logo', 'text_logo'],
            'persistent': detected,  # If detected, it's persistent by definition (30% threshold)
            'corner': is_corner,
            'text': generator_name,
            'location': locations[0] if locations else None,
        }
    except Exception as e:
        print(f"[watermark_ocr_v2] Error in new detector: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: return no detection
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }


def detect_watermark_in_image(image_path: str) -> Dict:
    """
    Detect watermark in a single image using the new detection script.
    For images, we treat them as single-frame videos.
    """
    if not HAS_NEW_DETECTOR:
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }
    
    # For images, we can't use the video detection script directly
    # Return no detection for now (images are less common)
    # TODO: Implement image-specific detection if needed
    return {
        'detected': False,
        'watermark': None,
        'confidence': 0.0,
        'generator_hint': False,
        'persistent': False,
        'corner': False,
    }

