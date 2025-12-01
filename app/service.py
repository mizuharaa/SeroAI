"""Main service orchestrating the deepfake detection pipeline.

Uses the new 5-axis detection engine following expert forensic analyst specification.
"""

import sys
import os
from typing import Dict, Optional, Callable
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detection_engine import DeepfakeDetectionEngine
from core.fusion import generate_reasons
from core.feedback_store import store_detection
from app.config import DECISION


def analyze_media(media_path: str, progress_callback: Optional[Callable[[float, Optional[str], str, bool], None]] = None) -> Dict:
    """
    Main function to analyze media for deepfake detection using new 5-axis engine.
    
    Args:
        media_path: Path to video or image file
        progress_callback: Optional callback for progress updates
        
    Returns:
        Dictionary with analysis results:
        {
            'verdict': 'AI'|'REAL'|'UNSURE'|'ABSTAIN',
            'prob_ai': float,
            'reasons': [{'name': str, 'weight': float, 'detail': str}, ...],
            'quality': {...},
            'debug': {...},
            'scores': {
                'motion_score': float,
                'bio_physics_score': float,
                'scene_logic_score': float,
                'texture_freq_score': float,
                'watermark_score': float
            }
        }
    """
    start_time = time.time()
    
    def emit(progress: float, stage: Optional[str], message: str, completed: bool = False):
        if progress_callback:
            try:
                progress_callback(progress, stage, message, completed)
            except Exception:
                pass
    
    # Check if file exists
    if not os.path.exists(media_path):
        return {
            'verdict': 'ABSTAIN',
            'prob_ai': 0.5,
            'reasons': [{'name': 'error', 'weight': 1.0, 'detail': 'File not found'}],
            'quality': {},
            'error': 'File not found',
            'scores': {}
        }
    
    # Initialize detection engine
    engine = DeepfakeDetectionEngine()
    
    # Run analysis
    emit(5.0, 'initializing', 'Initializing detection engine', False)
    result = engine.analyze(media_path, progress_callback=emit)
    
    # Extract results
    prob_ai = result['deepfake_probability']
    final_label = result['final_label']
    
    # Map label to verdict format
    if final_label == "AI-GENERATED":
        verdict = "AI"
    elif final_label == "AUTHENTIC":
        verdict = "REAL"
    else:  # UNCERTAIN
        verdict = "UNSURE"
    
    # Check for quality-based abstention
    quality = result.get('quality', {})
    if DECISION.get("ALLOW_ABSTAIN_ON_LOW_QUALITY", False) and quality.get('status') == 'low':
        if 0.15 < prob_ai < 0.85:  # In uncertain range
            verdict = "ABSTAIN"
    
    # Generate reasons from explanation
    reasons = generate_reasons(result, prob_ai)
    
    # Processing time
    processing_time = time.time() - start_time
    
    # Store detection
    detection_id = str(uuid.uuid4())
    store_detection(
        detection_id=detection_id,
        filename=os.path.basename(media_path),
        verdict=verdict,
        prob_ai=prob_ai,
        features=result,
    )
    
    return {
        'verdict': verdict,
        'prob_ai': prob_ai,
        'reasons': reasons,
        'quality': quality,
        'feedback_id': detection_id,
        'scores': {
            'motion_score': result['motion_score'],
            'bio_physics_score': result['bio_physics_score'],
            'scene_logic_score': result['scene_logic_score'],
            'texture_freq_score': result['texture_freq_score'],
            'watermark_score': result['watermark_score']
        },
        'explanation': result.get('explanation', {}),
        'debug': {
            'processing_time': processing_time,
            'final_label': final_label,
            'video_info': result.get('video_info')
        }
    }
