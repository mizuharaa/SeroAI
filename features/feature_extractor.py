"""Main feature extraction orchestrator that combines all feature modules."""

import sys
import os
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.motion_features import extract_motion_features
from features.anatomy_features import extract_anatomy_features
from features.frequency_features import extract_frequency_features
from features.audio_sync_features import extract_audio_sync_features
from core.face_detect import FaceDetector


def extract_all_features(
    video_path: str,
    enable_motion: bool = True,
    enable_anatomy: bool = True,
    enable_frequency: bool = True,
    enable_audio_sync: bool = True,
    enable_hand_analysis: bool = True
) -> Dict[str, float]:
    """
    Extract all features from video.
    
    Args:
        video_path: Path to video file
        enable_motion: Whether to extract motion features
        enable_anatomy: Whether to extract anatomy features
        enable_frequency: Whether to extract frequency features
        enable_audio_sync: Whether to extract audio-sync features
        enable_hand_analysis: Whether to analyze hands (can be disabled if no hands expected)
        
    Returns:
        Combined dictionary of all features
    """
    all_features = {}
    
    # Initialize face detector once (shared across modules)
    face_detector = FaceDetector()
    
    # Motion features
    if enable_motion:
        try:
            motion_features = extract_motion_features(
                video_path,
                target_fps=12.0,
                max_frames=50,
                face_detector=face_detector
            )
            all_features.update(motion_features)
        except Exception as e:
            print(f"[feature_extractor] Error extracting motion features: {e}")
            # Add default motion features
            all_features.update({
                'avg_optical_flow_mag_face': 0.0,
                'std_optical_flow_mag_face': 0.0,
                'motion_entropy_face': 0.5,
                'constant_motion_ratio': 0.5,
                'temporal_identity_std': 0.5,
                'head_pose_jitter': 0.5,
                'flow_magnitude_mean': 0.0,
                'flow_magnitude_std': 0.0,
            })
    
    # Anatomy features
    if enable_anatomy:
        try:
            anatomy_features = extract_anatomy_features(
                video_path,
                target_fps=8.0,
                max_frames=30,
                enable_hand_analysis=enable_hand_analysis
            )
            all_features.update(anatomy_features)
        except Exception as e:
            print(f"[feature_extractor] Error extracting anatomy features: {e}")
            # Add default anatomy features
            all_features.update({
                'hand_missing_finger_ratio': 0.0,
                'hand_abnormal_angle_ratio': 0.0,
                'avg_hand_landmark_confidence': 0.0,
                'mouth_open_ratio_mean': 0.0,
                'mouth_open_ratio_std': 0.0,
                'extreme_mouth_open_frequency': 0.0,
                'lip_sync_smoothness': 0.5,
                'eye_blink_rate': 0.0,
                'eye_blink_irregularity': 0.5,
            })
    
    # Frequency features
    if enable_frequency:
        try:
            frequency_features = extract_frequency_features(
                video_path,
                target_fps=10.0,
                max_frames=20,
                face_detector=face_detector
            )
            all_features.update(frequency_features)
        except Exception as e:
            print(f"[feature_extractor] Error extracting frequency features: {e}")
            # Add default frequency features
            all_features.update({
                'high_freq_energy_face': 0.0,
                'low_freq_energy_face': 0.0,
                'freq_energy_ratio': 0.5,
                'boundary_artifact_score': 0.0,
            })
    
    # Audio sync features
    if enable_audio_sync:
        try:
            audio_sync_features = extract_audio_sync_features(
                video_path,
                target_fps=12.0,
                max_frames=50
            )
            all_features.update(audio_sync_features)
        except Exception as e:
            print(f"[feature_extractor] Error extracting audio-sync features: {e}")
            # Add default audio sync features
            all_features.update({
                'lip_audio_correlation': 0.0,
                'avg_phoneme_lag': 0.0,
                'sync_consistency': 0.5,
                'has_audio': 0.0,
            })
    
    return all_features

