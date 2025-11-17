"""Main service orchestrating the deepfake detection pipeline."""

import sys
import os
from typing import Dict, Optional, Callable
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.quality_gate import assess_quality
from core.watermark_ocr_v2 import detect_watermark_in_video, detect_watermark_in_image
from core.forensics import analyze_forensics
from core.face_detect import analyze_faces_in_video
from core.fusion import DeepfakeFusion, generate_reasons
from core.artifact_detector import (
    analyze_visual_artifacts,
    analyze_visual_artifacts_image
)
from core.face_dynamics import analyze_face_dynamics
from core.feedback_store import store_detection
from core.scene_logic import detect_logic_breaks
from app.config import DECISION
from core.provenance import check_provenance
from core.temporal import optical_flow_oddity, rppg_coherence


def analyze_audio_visual_simple(video_path: str) -> Dict:
    """Simple audio-visual sync analysis.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with A/V analysis results
    """
    # Placeholder: would use SyncNet-like model
    # For now, return neutral score
    return {
        'sync_score': 0.5,
        'mis_sync_ms': 0,
        'has_audio': False
    }


def analyze_scene_logic_simple(video_path: str) -> Dict:
    """Simple scene logic and continuity analysis.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with scene analysis results
    """
    # Placeholder: would do shot detection and object persistence
    # For now, return neutral score
    return {
        'incoherence_score': 0.5,
        'num_shots': 1,
        'object_persistence_score': 0.5
    }


def analyze_media(media_path: str, progress_callback: Optional[Callable[[float, Optional[str], str, bool], None]] = None) -> Dict:
    """Main function to analyze media for deepfake detection.
    
    Args:
        media_path: Path to video or image file
        
    Returns:
        Dictionary with analysis results:
        {
            'verdict': 'AI'|'REAL'|'UNSURE'|'ABSTAIN',
            'prob_ai': float,
            'reasons': [{'name': str, 'weight': float, 'detail': str}, ...],
            'quality': {...},
            'debug': {...}
        }
    """
    start_time = time.time()

    def emit(progress: float, stage: Optional[str], message: str, completed: bool = False):
        if progress_callback:
            try:
                progress_callback(progress, stage, message, completed)
            except Exception:
                pass
    
    emit(3.0, 'quality', 'Preparing media', False)

    # Provenance (non-blocking)
    provenance = check_provenance(media_path)
    
    # Check if file exists
    if not os.path.exists(media_path):
        return {
            'verdict': 'ABSTAIN',
            'prob_ai': 0.5,
            'reasons': [{'name': 'error', 'weight': 1.0, 'detail': 'File not found'}],
            'quality': {},
            'error': 'File not found'
        }
    
    # Determine if image or video
    ext = os.path.splitext(media_path)[1].lower()
    is_image = ext in ['.jpg', '.jpeg', '.png']
    
    # Quality gate
    emit(8.0, 'quality', 'Assessing quality', False)
    if is_image:
        # For images, use simpler quality assessment
        quality = {
            'status': 'good',
            'issues': [],
            'blur': None,
            'brisque': None,
            'bitrate': None,
            'shake': None
        }
    else:
        quality = assess_quality(media_path)
    emit(18.0, 'quality', 'Quality assessment complete', True)
    
    # Watermark detection
    emit(22.0, 'watermark', 'Scanning for watermarks', False)
    if is_image:
        watermark = detect_watermark_in_image(media_path)
    else:
        watermark = detect_watermark_in_video(media_path)
    emit(34.0, 'watermark', 'Watermark scan complete', True)
    
    # Forensics (for videos)
    emit(36.0, 'forensics', 'Running forensic checks', False)
    if is_image:
        forensics = {
            'prnu_score': 0.5,
            'flicker_score': 0.5,
            'codec_score': 0.5
        }
    else:
        forensics = analyze_forensics(media_path)
    emit(50.0, 'forensics', 'Forensic analysis complete', True)
    
    # Face analysis (for videos)
    if is_image:
        face_analysis = {
            'num_faces': 0,
            'face_detected': False
        }
    else:
        face_analysis = analyze_faces_in_video(media_path)
    emit(60.0, 'face_analysis', 'Face analysis complete', True)
    
    # Visual artifact heuristics
    emit(62.0, 'artifact', 'Analyzing visual artifacts', False)
    if is_image:
        artifact_analysis = analyze_visual_artifacts_image(media_path)
        face_dynamics = {
            'mouth_exaggeration_score': 0.5,
            'mouth_static_score': 0.5,
            'eye_blink_anomaly': 0.5,
            'face_symmetry_drift': 0.5,
            'frames_processed': 0
        }
        emit(68.0, 'face_dynamics', 'Facial dynamics (image baseline)', True)
    else:
        artifact_analysis = analyze_visual_artifacts(media_path)
        emit(70.0, 'artifact', 'Artifact analysis complete', True)
        emit(72.0, 'face_dynamics', 'Analyzing facial dynamics', False)
        face_dynamics = analyze_face_dynamics(media_path)
        emit(78.0, 'face_dynamics', 'Facial dynamics complete', True)
    if is_image:
        emit(70.0, 'artifact', 'Artifact analysis complete', True)
    
    # Additional temporal cues
    emit(82.0, 'temporal', 'Temporal consistency checks', False)
    flow = optical_flow_oddity(media_path)
    rppg = rppg_coherence(media_path) if not is_image else {'rppg_score': 0.5}
    emit(86.0, 'temporal', 'Temporal checks complete', True)

    # Scene logic (for videos) - place after temporal and keep progress monotonic
    emit(88.0, 'scene_logic', 'Evaluating scene logic', False)
    if is_image:
        scene_logic = {
            'incoherence_score': 0.5,
            'flag': False,
            'reasons': [],
            'confidence': 0.0
        }
    else:
        # If global quality is low, skip heavy scene logic to save time (keeps accuracy on blur)
        if quality.get('status') == 'low':
            scene_logic = {
                'incoherence_score': 0.5,
                'flag': False,
                'reasons': ['skipped_low_quality'],
                'confidence': 0.0
            }
        else:
            # Lightweight logic break detector
            logic = detect_logic_breaks(media_path)
            scene_logic = {
                'incoherence_score': 0.5,
                **logic
            }
    emit(91.0, 'scene_logic', 'Scene logic complete', True)
    
    # Audio-visual analysis (for videos only)
    emit(92.0, 'audio_visual', 'Analyzing audio-visual sync', False)
    if is_image:
        av_analysis = {
            'sync_score': 0.5,
            'has_audio': False
        }
    else:
        av_analysis = analyze_audio_visual_simple(media_path)
    emit(94.0, 'audio_visual', 'A/V analysis complete', True)
    
    # Combine all results
    analysis_results = {
        'provenance': provenance,
        'quality': quality,
        'watermark': watermark,
        'forensics': forensics,
        'face_analysis': face_analysis,
        'av_analysis': av_analysis,
        'scene_logic': scene_logic,
        'artifact_analysis': artifact_analysis,
        'face_dynamics': face_dynamics,
        'temporal': {'flow': flow, 'rppg': rppg}
    }
    
    # Fusion
    emit(96.0, 'fusion', 'Fusing signals', False)
    fusion = DeepfakeFusion()
    prob_ai = fusion.predict(analysis_results)

    def decide(prob_ai: float, quality_dict: Dict) -> str:
        blur = quality_dict.get('blur')
        brisque = quality_dict.get('brisque')
        bitrate = quality_dict.get('bitrate')

        def _lt(a, b):
            try:
                return a is not None and b is not None and float(a) < float(b)
            except Exception:
                return False
        def _gt(a, b):
            try:
                return a is not None and b is not None and float(a) > float(b)
            except Exception:
                return False

        qlow = (_lt(blur, DECISION["BLUR_MIN"]) or
                _gt(brisque, DECISION["BRISQUE_MAX"]) or
                _lt(bitrate, DECISION["BITRATE_MIN"]))

        if qlow and DECISION["ALLOW_ABSTAIN_ON_LOW_QUALITY"] and \
           DECISION["UNSURE_LOW"] <= prob_ai <= DECISION["UNSURE_HIGH"]:
            return "ABSTAIN"

        if prob_ai >= DECISION["AI_THRESHOLD"]:
            return "AI"
        if prob_ai <= DECISION["REAL_THRESHOLD"]:
            return "REAL"

        if DECISION["UNSURE_LOW"] <= prob_ai <= DECISION["UNSURE_HIGH"]:
            return "UNSURE"

        return "AI" if prob_ai > 0.5 else "REAL"

    verdict = decide(prob_ai, quality)
    
    # Generate reasons
    reasons = generate_reasons(analysis_results, prob_ai)
    
    # Processing time
    processing_time = time.time() - start_time
    emit(100.0, 'fusion', 'Fusion complete', True)
    
    detection_id = str(uuid.uuid4())
    store_detection(
        detection_id=detection_id,
        filename=os.path.basename(media_path),
        verdict=verdict,
        prob_ai=prob_ai,
        features=analysis_results,
    )

    return {
        'verdict': verdict,
        'prob_ai': prob_ai,
        'reasons': reasons,
        'quality': quality,
        'feedback_id': detection_id,
        'debug': {
            'processing_time': processing_time,
            'watermark_detected': watermark.get('detected', False),
            'face_detected': face_analysis.get('face_detected', False),
            'forensics': forensics,
            'artifacts': artifact_analysis,
            'face_dynamics': face_dynamics,
            'is_image': is_image
        }
    }
