"""
Provenance and watermark detection module.

This module handles:
- Visual logo matching against reference AI model logos
- Verified watermark detection using template/feature matching
- Generic overlay detection (text-based fallback)
- Provenance type classification
"""

import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
from core.watermark_ocr_v2 import detect_watermark_in_video, detect_watermark_in_image
from core.logo_matcher import LogoMatcher


class ProvenanceDetector:
    """Detects watermarks and classifies provenance type using visual logo matching."""
    
    def __init__(self):
        """Initialize provenance detector with logo matcher."""
        self.logo_matcher = LogoMatcher()
    
    def detect_verified_watermark(
        self,
        video_path: str,
        frames: Optional[List[np.ndarray]] = None
    ) -> Dict:
        """
        Detect verified AI model watermark using visual logo matching.
        
        Primary method: Visual logo matching against reference logos
        Fallback: Text-based OCR detection for generic overlays
        
        Args:
            video_path: Path to video file
            frames: Optional pre-extracted frames (for efficiency)
            
        Returns:
            Dictionary with:
            - best_provider: Provider name or None
            - watermark_conf: Confidence score [0, 1]
            - provenance_type: Provider name or "none"
            - watermark_detected: bool
            - has_verified_watermark: bool (logo similarity >= 0.80)
            - watermark_score: Final score [0, 1]
            - match_method: "NCC+ORB", "TEXT_FALLBACK", or "NONE"
            - details: Human-readable details
        """
        # Extract frames if not provided
        if frames is None:
            frames = extract_frames(video_path, max_frames=30)
        
        # Primary: Visual logo matching
        logo_result = self.logo_matcher.detect_verified_watermark(frames, max_frames=10)
        
        has_verified_watermark = logo_result['has_verified_watermark']
        watermark_conf = logo_result['watermark_conf']
        provenance_type = logo_result['provenance_type']
        match_method = logo_result['match_method']
        
        # If verified watermark found, use it
        if has_verified_watermark:
            watermark_score = watermark_conf
            details = (
                f"Verified {provenance_type} logo watermark detected. "
                f"Logo similarity: {watermark_conf:.2f} (method: {match_method}). "
                f"Region: {logo_result.get('best_region', 'unknown')})"
            )
        else:
            # Fallback: Text-based detection for generic overlays
            # AGGRESSIVE: Any text/overlay should trigger watermark detection
            try:
                text_result = detect_watermark_in_video(video_path)
                text_detected = text_result.get('detected', False)
                text_confidence = text_result.get('confidence', 0.0)
                
                # Check for any AI-related keywords in text
                text_content = str(text_result.get('watermark', '') or text_result.get('text', '') or '').upper()
                ai_keywords = ['SORA', 'RUNWAY', 'PIKA', 'LUMA', 'GEMINI', 'HEYGEN', 'D-ID', 'MIDJOURNEY', 'DALL-E', 'IMAGEN', 'VEO']
                has_ai_keyword = any(keyword in text_content for keyword in ai_keywords)
                
                if text_detected or has_ai_keyword:
                    # AGGRESSIVE: Any watermark/overlay gets at least 0.50
                    if has_ai_keyword:
                        # AI keyword found - high confidence
                        watermark_score = max(0.60, min(text_confidence, 1.0)) if text_confidence > 0 else 0.60
                        watermark_conf = max(0.60, text_confidence)
                    elif text_detected:
                        # Any text overlay - minimum 0.50
                        watermark_score = max(0.50, min(text_confidence, 1.0)) if text_confidence > 0 else 0.50
                        watermark_conf = max(0.50, text_confidence)
                    else:
                        watermark_score = 0.50
                        watermark_conf = 0.50
                    
                    match_method = "TEXT_FALLBACK"
                    details = (
                        f"Text overlay detected: '{text_content}' "
                        f"(confidence: {text_confidence:.2f}). "
                        f"AI keyword match: {has_ai_keyword}. "
                        f"Boosted to {watermark_score:.2f} (minimum watermark threshold)."
                    )
                else:
                    watermark_score = 0.0
                    watermark_conf = 0.0
                    match_method = "NONE"
                    details = "No watermark detected"
            except Exception as e:
                # Even on error, try to detect any visible overlays
                watermark_score = 0.0
                watermark_conf = 0.0
                match_method = "NONE"
                details = f"Watermark detection error: {str(e)}"
        
        return {
            'best_provider': logo_result.get('best_provider'),
            'watermark_conf': float(watermark_conf),
            'provenance_type': provenance_type,
            'watermark_detected': watermark_score > 0.0,  # Any watermark detected
            'has_verified_watermark': has_verified_watermark,
            'watermark_score': float(watermark_score),
            'match_method': match_method,
            'details': details,
            'best_region': logo_result.get('best_region')
        }
    
    def get_axis_weights(self, has_verified_watermark: bool) -> Dict[str, float]:
        """
        Get axis weights based on whether verified watermark is present.
        
        Args:
            has_verified_watermark: Whether a verified logo watermark was detected
            
        Returns:
            Dictionary of axis weights
        """
        if has_verified_watermark:
            # Watermark-dominant weights (50% for watermark)
            return {
                "motion": 0.25,
                "bio": 0.10,
                "scene": 0.10,
                "texture": 0.05,
                "watermark": 0.50
            }
        else:
            # Default weights
            return {
                "motion": 0.50,
                "bio": 0.20,
                "scene": 0.15,
                "texture": 0.10,
                "watermark": 0.05
            }


def semantic_impossibility_boost(
    subject: Optional[str],
    provenance_info: Dict
) -> Tuple[float, str]:
    """
    Returns an optional boost in [0, 0.4] if we detect a semantic impossibility.
    
    Examples:
    - Deceased celebrity (Kobe Bryant) appearing in Sora-style clip
    - Historical figure in modern context with AI watermark
    
    Args:
        subject: Subject identifier (e.g., "kobe_bryant", "michael_jackson")
        provenance_info: Provenance detection results
        
    Returns:
        Tuple of (boost_value [0, 0.4], reason_string)
    """
    # Known deceased celebrities (can be extended)
    DECEASED_CELEBRITIES = {
        'kobe_bryant': {'death_year': 2020, 'boost': 0.3},
        'michael_jackson': {'death_year': 2009, 'boost': 0.3},
        'princess_diana': {'death_year': 1997, 'boost': 0.3},
        'heath_ledger': {'death_year': 2008, 'boost': 0.3},
    }
    
    if not subject:
        return 0.0, ""
    
    subject_lower = subject.lower().replace(' ', '_')
    
    # Check if subject is a known deceased celebrity
    if subject_lower in DECEASED_CELEBRITIES:
        celeb_info = DECEASED_CELEBRITIES[subject_lower]
        
        # Check if we have trusted Sora-style watermark
        provenance_type = provenance_info.get('provenance_type', 'none')
        
        if provenance_type == 'sora_style_trusted':
            boost = celeb_info['boost']
            reason = (
                f"Semantic impossibility: {subject} (deceased {celeb_info['death_year']}) "
                f"in Sora-style clip (impossible new footage)"
            )
            return boost, reason
    
    return 0.0, ""

