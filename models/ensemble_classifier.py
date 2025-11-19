"""Ensemble classifier for combining feature-based detection signals."""

import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import ML libraries
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        confusion_matrix, roc_auc_score, roc_curve,
        precision_score, recall_score, f1_score, classification_report
    )
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("[ensemble_classifier] scikit-learn not available; using simple rule-based classifier")

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False


class EnsembleClassifier:
    """Ensemble classifier that combines multiple feature types."""
    
    def __init__(self, model_type: str = 'logistic', config_path: Optional[str] = None):
        """
        Initialize ensemble classifier.
        
        Args:
            model_type: Type of model ('logistic', 'random_forest', 'gradient_boosting')
            config_path: Path to configuration file with thresholds
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler() if HAS_SKLEARN else None
        self.calibration = None
        self.thresholds = {
            'real_threshold': 0.25,
            'uncertain_low': 0.25,
            'uncertain_high': 0.75,
            'deepfake_threshold': 0.75
        }
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        
        # Feature names (must match order in feature extraction)
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self) -> List[str]:
        """Get list of feature names in order."""
        return [
            # Motion features
            'avg_optical_flow_mag_face',
            'std_optical_flow_mag_face',
            'motion_entropy_face',
            'constant_motion_ratio',
            'temporal_identity_std',
            'head_pose_jitter',
            'flow_magnitude_mean',
            'flow_magnitude_std',
            # Anatomy features
            'hand_missing_finger_ratio',
            'hand_abnormal_angle_ratio',
            'avg_hand_landmark_confidence',
            'mouth_open_ratio_mean',
            'mouth_open_ratio_std',
            'extreme_mouth_open_frequency',
            'lip_sync_smoothness',
            'eye_blink_rate',
            'eye_blink_irregularity',
            # Frequency features
            'high_freq_energy_face',
            'low_freq_energy_face',
            'freq_energy_ratio',
            'boundary_artifact_score',
            # Audio sync features
            'lip_audio_correlation',
            'avg_phoneme_lag',
            'sync_consistency',
            'has_audio',
        ]
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'thresholds' in config:
                    self.thresholds.update(config['thresholds'])
        except Exception as e:
            print(f"[ensemble_classifier] Error loading config: {e}")
    
    def save_config(self, config_path: str):
        """Save configuration to JSON file."""
        try:
            config = {
                'thresholds': self.thresholds,
                'model_type': self.model_type
            }
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[ensemble_classifier] Error saving config: {e}")
    
    def train(self, features: np.ndarray, labels: np.ndarray, 
              test_size: float = 0.2, calibrate: bool = True):
        """
        Train the ensemble classifier.
        
        Args:
            features: Feature matrix (n_samples, n_features)
            labels: Binary labels (0=real, 1=deepfake)
            test_size: Fraction of data to use for validation
            calibrate: Whether to apply calibration
        """
        if not HAS_SKLEARN:
            print("[ensemble_classifier] scikit-learn not available; cannot train")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Scale features
        if self.scaler is None:
            raise RuntimeError("Scaler not initialized. scikit-learn required for training.")
        assert self.scaler is not None  # Type narrowing for linter
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create model
        if self.model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        elif self.model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        
        # Calibrate if requested
        if calibrate:
            self.calibration = CalibratedClassifierCV(self.model, method='isotonic', cv=3)
            self.calibration.fit(X_train_scaled, y_train)
        
        # Evaluate
        if self.model is None:
            raise RuntimeError("Model not trained.")
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)[:, 1]  # type: ignore[index]
        
        print("\n=== Training Results ===")
        print(f"Accuracy: {np.mean(y_pred == y_test):.3f}")
        print(f"AUC: {roc_auc_score(y_test, y_proba):.3f}")
        print(f"Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"Recall: {recall_score(y_test, y_pred):.3f}")
        print(f"F1: {f1_score(y_test, y_pred):.3f}")
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
    
    def predict(self, features: Dict[str, float]) -> Dict[str, any]:  # type: ignore[type-arg]
        """
        Predict deepfake probability from features.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            Dictionary with:
            - score: Deepfake probability [0, 1]
            - label: 'REAL', 'DEEPFAKE', or 'UNCERTAIN'
            - explanations: List of explanation strings
        """
        # Convert features to array
        feature_vector = self._features_to_vector(features)
        
        # Predict
        if self.model is not None and HAS_SKLEARN and self.scaler is not None:
            # Scale features
            assert self.scaler is not None  # Type narrowing for linter
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Predict probability
            if self.calibration is not None:
                prob = self.calibration.predict_proba(feature_vector_scaled)[0, 1]  # type: ignore[index]
            else:
                prob = self.model.predict_proba(feature_vector_scaled)[0, 1]  # type: ignore[index]
        else:
            # Fallback: simple rule-based prediction
            prob = self._rule_based_predict(features)
        
        # Get verdict
        label = self._get_verdict(prob)
        
        # Generate explanations
        explanations = self._generate_explanations(features, prob)
        
        return {
            'score': float(prob),
            'label': label,
            'explanations': explanations
        }
    
    def _features_to_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary to vector."""
        vector = []
        for name in self.feature_names:
            value = features.get(name, 0.0)
            if isinstance(value, (int, float)):
                vector.append(float(value))
            else:
                vector.append(0.0)
        return np.array(vector)
    
    def _rule_based_predict(self, features: Dict[str, float]) -> float:
        """
        Conservative rule-based prediction that requires STRONG evidence.
        Designed to avoid false positives - defaults to REAL (low score) unless
        multiple strong signals indicate deepfake.
        """
        # Start with a REAL bias (low score) - require strong evidence to increase
        base_score = 0.2  # Start assuming real content
        
        # Collect STRONG evidence from different feature categories
        # Use higher thresholds to avoid false positives
        strong_evidence_count = 0
        moderate_evidence_count = 0
        
        # ========== REAL-WORLD EVIDENCE (REDUCES score) ==========
        # Smooth motion indicates real content
        constant_motion = features.get('constant_motion_ratio', 0.5)
        if constant_motion < 0.4:  # Low constant motion = natural movement
            base_score -= 0.1
        
        # Low temporal identity variance = consistent face (real)
        temporal_identity = features.get('temporal_identity_std', 0.5)
        if temporal_identity < 0.3:
            base_score -= 0.1
        
        # Low head jitter = smooth head movement (real)
        head_jitter = features.get('head_pose_jitter', 0.5)
        if head_jitter < 0.4:
            base_score -= 0.1
        
        # Good lip smoothness = natural speech (real)
        lip_smooth = features.get('lip_sync_smoothness', 0.5)
        if lip_smooth > 0.6:
            base_score -= 0.1
        
        # Good audio sync = real content
        has_audio = features.get('has_audio', 0.0) > 0.5
        if has_audio:
            lip_audio_corr = features.get('lip_audio_correlation', 0.5)
            if lip_audio_corr > 0.6:  # Good correlation
                base_score -= 0.15
        
        # ========== DEEPFAKE EVIDENCE (INCREASES score) ==========
        # Require STRONG thresholds to avoid false positives
        
        # Motion anomalies (require very high values)
        if constant_motion > 0.75:  # Very high = suspicious
            strong_evidence_count += 1
        elif constant_motion > 0.65:
            moderate_evidence_count += 1
        
        if temporal_identity > 0.7:  # Very high variance
            strong_evidence_count += 1
        elif temporal_identity > 0.6:
            moderate_evidence_count += 1
        
        if head_jitter > 0.75:  # Very high jitter
            strong_evidence_count += 1
        elif head_jitter > 0.65:
            moderate_evidence_count += 1
        
        # Anatomy anomalies (require actual detections, not defaults)
        hand_missing = features.get('hand_missing_finger_ratio', 0.0)
        if hand_missing > 0.5:  # High threshold - actual missing fingers
            strong_evidence_count += 1
        elif hand_missing > 0.3:
            moderate_evidence_count += 1
        
        hand_abnormal = features.get('hand_abnormal_angle_ratio', 0.0)
        if hand_abnormal > 0.5:
            strong_evidence_count += 1
        elif hand_abnormal > 0.3:
            moderate_evidence_count += 1
        
        mouth_extreme = features.get('extreme_mouth_open_frequency', 0.0)
        if mouth_extreme > 0.5:  # Very frequent extreme openings
            strong_evidence_count += 1
        elif mouth_extreme > 0.3:
            moderate_evidence_count += 1
        
        blink_irregular = features.get('eye_blink_irregularity', 0.5)
        if blink_irregular > 0.8:  # Very irregular
            strong_evidence_count += 1
        elif blink_irregular > 0.7:
            moderate_evidence_count += 1
        
        if lip_smooth < 0.2:  # Very low smoothness
            strong_evidence_count += 1
        elif lip_smooth < 0.3:
            moderate_evidence_count += 1
        
        # Frequency artifacts (require high values)
        boundary_artifacts = features.get('boundary_artifact_score', 0.0)
        if boundary_artifacts > 0.7:  # Very high artifacts
            strong_evidence_count += 1
        elif boundary_artifacts > 0.6:
            moderate_evidence_count += 1
        
        freq_ratio = features.get('freq_energy_ratio', 0.5)
        if freq_ratio > 0.8:  # Very abnormal ratio
            strong_evidence_count += 1
        elif freq_ratio > 0.7:
            moderate_evidence_count += 1
        
        # Audio sync issues (only if audio present)
        if has_audio:
            lip_audio_corr = features.get('lip_audio_correlation', 0.5)
            if lip_audio_corr < 0.2:  # Very poor correlation
                strong_evidence_count += 1
            elif lip_audio_corr < 0.3:
                moderate_evidence_count += 1
            
            phoneme_lag = features.get('avg_phoneme_lag', 0.0)
            if phoneme_lag > 0.7:  # Very high lag
                strong_evidence_count += 1
            elif phoneme_lag > 0.5:
                moderate_evidence_count += 1
        
        # ========== CALCULATE FINAL SCORE ==========
        # Require multiple strong signals to increase score significantly
        # Conservative approach: need 3+ strong signals OR 5+ moderate signals
        
        if strong_evidence_count >= 3:
            # Multiple strong signals - likely deepfake
            base_score += 0.5
        elif strong_evidence_count >= 2:
            # Some strong signals
            base_score += 0.3
        elif strong_evidence_count >= 1:
            # One strong signal - be cautious
            base_score += 0.15
        
        if moderate_evidence_count >= 5:
            # Many moderate signals
            base_score += 0.3
        elif moderate_evidence_count >= 3:
            # Several moderate signals
            base_score += 0.15
        elif moderate_evidence_count >= 2:
            # A few moderate signals
            base_score += 0.08
        
        # Ensure score stays in [0, 1] range
        final_score = float(np.clip(base_score, 0.0, 1.0))
        
        # If no evidence at all, return low score (assume real)
        if strong_evidence_count == 0 and moderate_evidence_count == 0:
            return 0.15  # Low score - assume real content
        
        # Cap the maximum score unless we have overwhelming evidence
        # Require 4+ strong signals OR 6+ moderate signals to exceed 0.7
        if final_score > 0.7:
            if strong_evidence_count < 4 and moderate_evidence_count < 6:
                final_score = 0.65  # Cap at uncertain range
        
        # Additional safety: never return 1.0 unless we have 5+ strong signals
        if final_score >= 0.95 and strong_evidence_count < 5:
            final_score = 0.85
        
        return float(np.clip(final_score, 0.0, 1.0))
    
    def _get_verdict(self, prob: float) -> str:
        """Get verdict from probability."""
        if prob < self.thresholds['real_threshold']:
            return 'REAL'
        elif prob > self.thresholds['deepfake_threshold']:
            return 'DEEPFAKE'
        else:
            return 'UNCERTAIN'
    
    def _generate_explanations(self, features: Dict[str, float], prob: float) -> List[str]:
        """Generate human-readable explanations."""
        explanations = []
        
        # Motion explanations
        if features.get('constant_motion_ratio', 0.5) > 0.7:
            explanations.append("Constant motion pixels detected (rubbery/overly uniform motion)")
        if features.get('temporal_identity_std', 0.5) > 0.6:
            explanations.append("Temporal identity inconsistency (face embedding fluctuates)")
        if features.get('head_pose_jitter', 0.5) > 0.7:
            explanations.append("Head pose jitter detected (unnatural pose changes)")
        
        # Anatomy explanations
        if features.get('hand_missing_finger_ratio', 0.0) > 0.3:
            explanations.append("Hand skeleton inconsistencies (missing/merged fingers)")
        if features.get('hand_abnormal_angle_ratio', 0.0) > 0.3:
            explanations.append("Abnormal hand joint angles detected")
        if features.get('extreme_mouth_open_frequency', 0.0) > 0.3:
            explanations.append("Mouth opens unrealistically wide or often")
        if features.get('eye_blink_irregularity', 0.5) > 0.7:
            explanations.append("Irregular eye blink pattern")
        if features.get('lip_sync_smoothness', 0.5) < 0.3:
            explanations.append("Lip movement lacks temporal smoothness")
        
        # Frequency explanations
        if features.get('boundary_artifact_score', 0.0) > 0.6:
            explanations.append("Boundary artifacts detected near face edges")
        if features.get('freq_energy_ratio', 0.5) > 0.7:
            explanations.append("Abnormal frequency energy ratio (high-frequency artifacts)")
        
        # Audio sync explanations
        if features.get('has_audio', 0.0) > 0.5:
            if features.get('lip_audio_correlation', 0.0) < 0.3:
                explanations.append("Poor lip-audio correlation (mouth movement doesn't match speech)")
            if features.get('avg_phoneme_lag', 0.0) > 0.5:
                explanations.append("Audio-visual lag detected (phoneme-mouth misalignment)")
        
        # If no specific explanations, add generic ones
        if len(explanations) == 0:
            if prob > 0.7:
                explanations.append("Multiple subtle anomalies detected")
            elif prob < 0.3:
                explanations.append("No significant anomalies detected")
            else:
                explanations.append("Mixed signals detected")
        
        return explanations[:5]  # Limit to top 5
    
    def save(self, model_path: str):
        """Save model to disk."""
        if not HAS_JOBLIB:
            print("[ensemble_classifier] joblib not available; cannot save model")
            return
        
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'calibration': self.calibration,
                'model_type': self.model_type,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, model_path)
            print(f"[ensemble_classifier] Model saved to {model_path}")
        except Exception as e:
            print(f"[ensemble_classifier] Error saving model: {e}")
    
    def load(self, model_path: str):
        """Load model from disk."""
        if not HAS_JOBLIB:
            print("[ensemble_classifier] joblib not available; cannot load model")
            return
        
        try:
            model_data = joblib.load(model_path)
            self.model = model_data.get('model')
            self.scaler = model_data.get('scaler')
            self.calibration = model_data.get('calibration')
            self.model_type = model_data.get('model_type', 'logistic')
            self.feature_names = model_data.get('feature_names', self._get_feature_names())
            print(f"[ensemble_classifier] Model loaded from {model_path}")
        except Exception as e:
            print(f"[ensemble_classifier] Error loading model: {e}")

