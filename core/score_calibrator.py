"""
Score calibration and normalization module.

This module handles feature normalization and logistic scoring using
config-based parameters.
"""

import numpy as np
import json
import os
from typing import Dict, Optional
from math import exp


class ScoreCalibrator:
    """
    Calibrates and scores features using config-based normalization and weights.
    
    Features are normalized using z-score: z = (x - mean_real) / std_real
    Final score uses logistic combination: sigmoid(sum(weights * z) + bias)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize calibrator with config file.
        
        Args:
            config_path: Path to feature_stats.json config file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config', 'feature_stats.json'
            )
        
        self.config_path = config_path
        self.feature_stats: Dict[str, Dict[str, float]] = {}
        self.weights: Dict[str, float] = {}
        self.bias: float = 0.0
        self.decision_threshold: float = 0.6
        
        self._load_config()
    
    def _load_config(self):
        """Load feature statistics and weights from config file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.feature_stats = config.get('feature_stats', {})
                    self.weights = config.get('weights', {})
                    self.bias = config.get('bias', 0.0)
                    self.decision_threshold = config.get('decision_threshold', 0.6)
            except Exception as e:
                print(f"[score_calibrator] Error loading config: {e}, using defaults")
                self._set_defaults()
        else:
            print(f"[score_calibrator] Config file not found: {self.config_path}, using defaults")
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default values if config file is missing."""
        # Default feature statistics (mean_real, std_real)
        self.feature_stats = {
            'blink_anomaly_score': {'mean_real': 0.2, 'std_real': 0.15},
            'landmark_jitter_score': {'mean_real': 0.1, 'std_real': 0.08},
            'lip_sync_error': {'mean_real': 0.3, 'std_real': 0.2},
            'texture_artifact_score': {'mean_real': 0.15, 'std_real': 0.12},
            'pose_background_inconsistency': {'mean_real': 0.2, 'std_real': 0.15},
            'watermark_prob': {'mean_real': 0.0, 'std_real': 0.1}
        }
        
        # Default weights (should sum to ~1.0 for interpretability)
        self.weights = {
            'blink_anomaly_score': 0.20,
            'landmark_jitter_score': 0.25,
            'lip_sync_error': 0.15,
            'texture_artifact_score': 0.20,
            'pose_background_inconsistency': 0.15,
            'watermark_prob': 0.05
        }
        
        self.bias = 0.0
        self.decision_threshold = 0.6
    
    def normalize_feature(self, feature_name: str, value: float) -> float:
        """
        Normalize a feature value using z-score: z = (x - mean) / std
        
        Args:
            feature_name: Name of the feature
            value: Raw feature value
            
        Returns:
            Normalized z-score
        """
        if feature_name not in self.feature_stats:
            # Unknown feature - return as-is (no normalization)
            return value
        
        stats = self.feature_stats[feature_name]
        mean_real = stats.get('mean_real', 0.0)
        std_real = stats.get('std_real', 1.0)
        
        if std_real < 1e-6:
            return 0.0
        
        z_score = (value - mean_real) / std_real
        return float(z_score)
    
    def normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize all features in a dictionary.
        
        Args:
            features: Dictionary of feature_name -> raw_value
            
        Returns:
            Dictionary of feature_name -> normalized_value
        """
        normalized = {}
        for name, value in features.items():
            normalized[name] = self.normalize_feature(name, value)
        return normalized
    
    def compute_deepfake_score(
        self,
        normalized_features: Dict[str, float]
    ) -> float:
        """
        Compute deepfake score using logistic combination.
        
        Formula: sigmoid(sum(weights * z) + bias)
        
        Args:
            normalized_features: Dictionary of normalized feature values
            
        Returns:
            Deepfake probability [0, 1]
        """
        weighted_sum = self.bias
        
        for feature_name, z_score in normalized_features.items():
            if feature_name in self.weights:
                weight = self.weights[feature_name]
                weighted_sum += weight * z_score
        
        # Apply sigmoid
        deepfake_score = 1.0 / (1.0 + exp(-weighted_sum))
        
        return float(np.clip(deepfake_score, 0.0, 1.0))
    
    def get_label(self, deepfake_score: float) -> str:
        """
        Get decision label from deepfake score.
        
        Args:
            deepfake_score: Deepfake probability [0, 1]
            
        Returns:
            "deepfake" if score >= threshold, else "authentic"
        """
        if deepfake_score >= self.decision_threshold:
            return "deepfake"
        else:
            return "authentic"

