"""Ensemble-based deepfake detector using feature extraction modules."""

import sys
import os
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.feature_extractor import extract_all_features
from models.ensemble_classifier import EnsembleClassifier
from core.config import FUSION_MODEL_PATH


def detect_with_ensemble(
    video_path: str,
    model_path: Optional[str] = None,
    config_path: Optional[str] = None,
    enable_hand_analysis: bool = True
) -> Dict:
    """
    Detect deepfake using feature-based ensemble.
    
    Args:
        video_path: Path to video file
        model_path: Path to trained ensemble model (optional)
        config_path: Path to configuration file (optional)
        enable_hand_analysis: Whether to analyze hands
        
    Returns:
        Dictionary with:
        - score: Deepfake probability [0, 1]
        - label: 'REAL', 'DEEPFAKE', or 'UNCERTAIN'
        - explanations: List of explanation strings
        - features: Extracted features dictionary
    """
    # Extract all features
    features = extract_all_features(
        video_path,
        enable_motion=True,
        enable_anatomy=True,
        enable_frequency=True,
        enable_audio_sync=True,
        enable_hand_analysis=enable_hand_analysis
    )
    
    # Initialize classifier
    if model_path is None:
        model_path = 'models/ensemble_classifier.pkl'
    
    if config_path is None:
        config_path = 'models/ensemble_config.json'
    
    classifier = EnsembleClassifier(model_type='logistic', config_path=config_path)
    
    # Load model if it exists
    if os.path.exists(model_path):
        classifier.load(model_path)
    
    # Predict
    result = classifier.predict(features)
    
    # Add features to result
    result['features'] = features
    
    return result

