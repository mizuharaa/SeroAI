"""Fusion model for combining multiple detection signals."""

import numpy as np
from typing import Dict, List
import json
import os
try:
    import joblib  # type: ignore
except Exception:  # pragma: no cover
    joblib = None  # type: ignore
try:
    # Optional; only required if a trained model is actually used
    from sklearn.linear_model import LogisticRegression  # type: ignore
    from sklearn.calibration import CalibratedClassifierCV  # type: ignore
except Exception:  # pragma: no cover
    LogisticRegression = None  # type: ignore
    CalibratedClassifierCV = None  # type: ignore

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import (
    WATERMARK_LOGIT_BONUS,
    AI_THRESHOLD,
    REAL_THRESHOLD,
    UNSURE_THRESHOLD_HIGH,
    UNSURE_THRESHOLD_LOW,
    FUSION_MODEL_PATH,
    CALIBRATION_PATH,
    ABSTAIN_ON_LOW_QUALITY,
)
from core.feedback_store import get_metric_weights
from app.config import DECISION
import math


class DeepfakeFusion:
    """Fusion model for deepfake detection."""
    
    def __init__(self):
        self.model = None
        self.calibration = None
        self.metric_weights = get_metric_weights()
        self.load_models()
    
    def load_models(self):
        """Load pre-trained fusion model and calibration."""
        # Try to load trained model
        if os.path.exists(FUSION_MODEL_PATH):
            try:
                if joblib is not None:
                    self.model = joblib.load(FUSION_MODEL_PATH)
            except:
                pass
        
        # Try to load calibration
        if os.path.exists(CALIBRATION_PATH):
            try:
                with open(CALIBRATION_PATH, 'r') as f:
                    self.calibration = json.load(f)
            except:
                pass
        
        # If no model loaded, use default rule-based fusion
        if self.model is None:
            self.model = 'rule_based'
    
    def extract_features(self, analysis_results: Dict) -> np.ndarray:
        """Extract feature vector from analysis results.
        
        Args:
            analysis_results: Dictionary with all analysis results
            
        Returns:
            Feature vector
        """
        # Extract features from different branches
        features = []
        
        # Face branch features
        face_analysis = analysis_results.get('face_analysis', {})
        if face_analysis.get('face_detected'):
            # Placeholder: would use face model predictions
            features.append(0.5)  # p_ai_face_mean
            features.append(0.5)  # p_ai_face_max
        else:
            features.append(0.5)
            features.append(0.5)
        
        # Scene branch features
        forensics = analysis_results.get('forensics', {})
        features.append(forensics.get('prnu_score', 0.5))
        features.append(forensics.get('flicker_score', 0.5))
        features.append(forensics.get('codec_score', 0.5))
        
        # Audio-visual features
        av_analysis = analysis_results.get('av_analysis', {})
        features.append(av_analysis.get('sync_score', 0.5))
        
        # Visual artifact heuristics
        artifacts = analysis_results.get('artifact_analysis', {})
        features.append(artifacts.get('edge_artifact_score', 0.5))
        features.append(artifacts.get('texture_inconsistency', 0.5))
        features.append(artifacts.get('color_anomaly_score', 0.5))
        features.append(artifacts.get('freq_artifact_score', 0.5))

        # Facial dynamics
        face_dyn = analysis_results.get('face_dynamics', {})
        features.append(face_dyn.get('mouth_exaggeration_score', 0.5))
        features.append(face_dyn.get('mouth_static_score', 0.5))
        features.append(face_dyn.get('eye_blink_anomaly', 0.5))
        features.append(face_dyn.get('face_symmetry_drift', 0.5))
        
        # Watermark features
        watermark = analysis_results.get('watermark', {})
        features.append(1.0 if watermark.get('detected') else 0.0)
        features.append(watermark.get('confidence', 0.0))
        
        # Quality features
        quality = analysis_results.get('quality', {})
        blur_value = quality.get('blur', 100.0)
        brisque_value = quality.get('brisque', 30.0)
        if not isinstance(blur_value, (int, float)):
            blur_value = 100.0
        if not isinstance(brisque_value, (int, float)):
            brisque_value = 30.0
        features.append(float(blur_value) / 100.0)  # Normalize
        features.append(float(brisque_value) / 100.0)  # Normalize
        features.append(1.0 if quality.get('status') == 'good' else 0.0)
        
        # Scene logic features
        scene_logic = analysis_results.get('scene_logic', {})
        features.append(scene_logic.get('incoherence_score', 0.5))
        
        return np.array(features).reshape(1, -1)
    
    def fuse_rule_based(self, analysis_results: Dict) -> float:
        """Rule-based fusion (fallback when no trained model).
        
        Args:
            analysis_results: Dictionary with all analysis results
            
        Returns:
            Probability of AI generation
        """
        scores = []
        weights = []
        
        metric_weights = getattr(self, "metric_weights", {}) or {}

        def weighted(metric: str, base: float) -> float:
            return base * metric_weights.get(metric, 1.0)

        # Watermark (strong signal but can be tuned)
        watermark = analysis_results.get('watermark', {})
        if watermark.get('detected'):
            wm_conf = watermark.get('confidence', 0.8)
            scores.append(0.75)
            weights.append(weighted('watermark', 0.4))
        
        # Face analysis
        face_analysis = analysis_results.get('face_analysis', {})
        if face_analysis.get('face_detected'):
            # Placeholder: would use face model score
            face_score = 0.5
            scores.append(face_score)
            weights.append(weighted('face_analysis', 0.25))
        
        # Forensics
        forensics = analysis_results.get('forensics', {})
        prnu = forensics.get('prnu_score', 0.5)
        flicker = forensics.get('flicker_score', 0.5)
        codec = forensics.get('codec_score', 0.5)
        
        # PRNU: lower = more likely AI
        scores.append(1.0 - prnu)
        weights.append(weighted('forensics_prnu', 0.2))
        
        # Flicker: higher = more likely AI
        scores.append(flicker)
        weights.append(weighted('forensics_flicker', 0.18))
        
        # Codec: higher = more likely AI
        scores.append(codec)
        weights.append(weighted('forensics_codec', 0.15))
        
        # Audio-visual
        av_analysis = analysis_results.get('av_analysis', {})
        av_score = av_analysis.get('sync_score', 0.5)
        # Lower sync = more likely AI
        scores.append(1.0 - av_score)
        weights.append(weighted('audio_sync', 0.12))
        
        # Artifact heuristics
        artifacts = analysis_results.get('artifact_analysis', {})
        edge_score = artifacts.get('edge_artifact_score', 0.5)
        texture_score = artifacts.get('texture_inconsistency', 0.5)
        color_score = artifacts.get('color_anomaly_score', 0.5)
        
        scores.append(edge_score)
        weights.append(weighted('edge_artifacts', 0.16))
        scores.append(texture_score)
        weights.append(weighted('texture_inconsistency', 0.14))
        scores.append(color_score)
        weights.append(weighted('color_anomaly', 0.1))
        freq_score = artifacts.get('freq_artifact_score', 0.5)
        scores.append(freq_score)
        weights.append(weighted('freq_artifacts', 0.14))

        # Face dynamics heuristics
        face_dyn = analysis_results.get('face_dynamics', {})
        mouth_ex = face_dyn.get('mouth_exaggeration_score', 0.5)
        mouth_static = face_dyn.get('mouth_static_score', 0.5)
        blink_anomaly = face_dyn.get('eye_blink_anomaly', 0.5)
        symmetry_drift = face_dyn.get('face_symmetry_drift', 0.5)

        scores.append(mouth_ex)
        weights.append(weighted('mouth_exaggeration', 0.16))
        scores.append(mouth_static)
        weights.append(weighted('mouth_static', 0.14))
        scores.append(blink_anomaly)
        weights.append(weighted('eye_blink', 0.12))
        scores.append(symmetry_drift)
        weights.append(weighted('face_symmetry', 0.1))
        
        # Scene logic
        scene_logic = analysis_results.get('scene_logic', {})
        scene_score = scene_logic.get('incoherence_score', 0.5)
        scores.append(scene_score)
        weights.append(weighted('scene_logic', 0.08))
        
        # Quality adjustment
        quality = analysis_results.get('quality', {})
        if quality.get('status') == 'low':
            # Down-weight all scores if quality is low
            weights = [w * 0.7 for w in weights]
        
        # Weighted average
        if weights:
            prob_ai = np.average(scores, weights=weights)
        else:
            prob_ai = 0.5
        
        return float(np.clip(prob_ai, 0.0, 1.0))
    
    def _apply_hard_evidence_boosts(self, prob_ai: float, analysis_results: Dict) -> float:
        """Apply logit-space boosts for hard evidence."""
        def to_logit(p: float) -> float:
            p = float(np.clip(p, 1e-6, 1.0 - 1e-6))
            return float(np.log(p / (1.0 - p)))
        def to_prob(z: float) -> float:
            return float(1.0 / (1.0 + math.exp(-z)))
        
        z = to_logit(prob_ai)
        
        # Evidence extraction
        wm = analysis_results.get('watermark', {})
        has_wm = bool(wm.get('detected') and wm.get('confidence', 0.0) >= 0.8)
        
        scene_logic = analysis_results.get('scene_logic', {})
        has_logic_break = bool(scene_logic.get('flag') and scene_logic.get('confidence', 0.0) >= 0.8)
        
        face_dyn = analysis_results.get('face_dynamics', {})
        anatomy_max = max(
            face_dyn.get('mouth_exaggeration_score', 0.0),
            face_dyn.get('mouth_static_score', 0.0),
            face_dyn.get('eye_blink_anomaly', 0.0),
            face_dyn.get('face_symmetry_drift', 0.0),
        )
        has_anatomy = bool(anatomy_max >= 0.85)
        
        if has_logic_break:
            z += DECISION["LOGIC_BREAK_LOGIT_BONUS"]
        if has_wm:
            z += DECISION["WATERMARK_LOGIT_BONUS"]
        if has_anatomy:
            z += DECISION["ANATOMY_LOGIT_BONUS"]
        
        return to_prob(z)
    
    def predict(self, analysis_results: Dict) -> float:
        """Predict probability of AI generation.
        
        Args:
            analysis_results: Dictionary with all analysis results
            
        Returns:
            Calibrated probability of AI generation
        """
        # Refresh adaptive weights in case new feedback has arrived
        self.metric_weights = get_metric_weights()
        if self.model == 'rule_based':
            prob = self.fuse_rule_based(analysis_results)
        else:
            # Use trained model
            features = self.extract_features(analysis_results)
            prob = self.model.predict_proba(features)[0, 1]
        
        # Apply calibration if available
        if self.calibration:
            # Temperature scaling
            temp = self.calibration.get('temperature', 1.0)
            eps = 1e-6
            p = float(np.clip(prob, eps, 1.0 - eps))
            logit = np.log(p / (1.0 - p))
            prob = 1.0 / (1.0 + np.exp(-logit / max(temp, eps)))
        
        # Hard-evidence overrides (logit boosts)
        prob = self._apply_hard_evidence_boosts(prob, analysis_results)

        # Independence rule: require two strong independent branches to exceed 0.90
        strong = 0
        wm = analysis_results.get('watermark', {})
        if wm.get('detected') and wm.get('persistent') and wm.get('corner') and wm.get('confidence', 0.0) >= 0.85:
            strong += 1
        scene_logic = analysis_results.get('scene_logic', {})
        if scene_logic.get('flag') and scene_logic.get('confidence', 0.0) >= 0.8:
            strong += 1
        artifacts = analysis_results.get('artifact_analysis', {})
        if artifacts.get('freq_artifact_score', 0.0) >= 0.8 or artifacts.get('edge_artifact_score', 0.0) >= 0.8:
            strong += 1
        face_dyn = analysis_results.get('face_dynamics', {})
        if max(
            face_dyn.get('mouth_exaggeration_score', 0.0),
            face_dyn.get('mouth_static_score', 0.0),
            face_dyn.get('eye_blink_anomaly', 0.0),
            face_dyn.get('face_symmetry_drift', 0.0),
        ) >= 0.85:
            strong += 1
        temporal = analysis_results.get('temporal', {})
        if temporal.get('flow', {}).get('oddity_score', 0.0) >= 0.8 or temporal.get('rppg', {}).get('rppg_score', 0.0) >= 0.8:
            strong += 1

        if prob > 0.90 and strong < 2:
            prob = 0.90

        # Low quality and only one strong branch → cap
        quality = analysis_results.get('quality', {})
        if quality.get('status') == 'low' and strong <= 1:
            prob = min(prob, 0.75)

        return float(np.clip(prob, 0.0, 1.0))
    
    def get_verdict(self, prob_ai: float, quality_status: str) -> str:
        """Get final verdict based on probability and quality.
        
        Args:
            prob_ai: Probability of AI generation
            quality_status: Quality status ('good' or 'low')
            
        Returns:
            Verdict: 'AI', 'REAL', 'UNSURE', or 'ABSTAIN'
        """
        # Abstain if quality is too low
        if DECISION["ALLOW_ABSTAIN_ON_LOW_QUALITY"] and quality_status == 'low':
            return 'ABSTAIN'
        
        # Decision thresholds (decisive policy)
        if prob_ai >= DECISION["AI_THRESHOLD"]:
            return 'AI'
        elif prob_ai <= DECISION["REAL_THRESHOLD"]:
            return 'REAL'
        
        if DECISION["UNSURE_LOW"] <= prob_ai <= DECISION["UNSURE_HIGH"]:
            return 'UNSURE'
        
        return 'AI' if prob_ai > 0.5 else 'REAL'


def generate_reasons(analysis_results: Dict, prob_ai: float) -> List[Dict]:
    """Generate human-readable reasons for the decision.
    
    Args:
        analysis_results: Dictionary with all analysis results
        prob_ai: Probability of AI generation
        
    Returns:
        List of reason dictionaries
    """
    reasons = []
    
    # Watermark
    watermark = analysis_results.get('watermark', {})
    if watermark.get('detected'):
        reasons.append({
            'name': 'watermark',
            'weight': 0.4,
            'detail': f"{watermark.get('watermark', 'AI')} watermark detected",
            'confidence': watermark.get('confidence', 0.8)
        })
    
    # Face analysis
    face_analysis = analysis_results.get('face_analysis', {})
    if face_analysis.get('face_detected'):
        reasons.append({
            'name': 'face_analysis',
            'weight': 0.2,
            'detail': 'Face analysis indicates synthetic features',
            'confidence': 0.7
        })
    
    # Visual artifact heuristics
    artifacts = analysis_results.get('artifact_analysis', {})
    if artifacts.get('edge_artifact_score', 0.0) > 0.65:
        reasons.append({
            'name': 'edge_artifacts',
            'weight': 0.18,
            'detail': 'Edge activity inconsistent frame-to-frame (possible compositing)',
            'confidence': artifacts.get('edge_artifact_score', 0.6)
        })
    if artifacts.get('texture_inconsistency', 0.0) > 0.65:
        reasons.append({
            'name': 'texture_inconsistency',
            'weight': 0.15,
            'detail': 'Texture consistency varies abnormally across frames',
            'confidence': artifacts.get('texture_inconsistency', 0.6)
        })
    if artifacts.get('color_anomaly_score', 0.0) > 0.65:
        reasons.append({
            'name': 'color_anomaly',
            'weight': 0.12,
            'detail': 'Color saturation fluctuates unnaturally',
            'confidence': artifacts.get('color_anomaly_score', 0.6)
        })
    if artifacts.get('freq_artifact_score', 0.0) > 0.65:
        reasons.append({
            'name': 'frequency_artifact',
            'weight': 0.14,
            'detail': 'High-frequency spectral energy inconsistent with real footage',
            'confidence': artifacts.get('freq_artifact_score', 0.6)
        })

    # Face dynamics heuristics
    face_dyn = analysis_results.get('face_dynamics', {})
    if face_dyn.get('mouth_exaggeration_score', 0.0) > 0.65:
        reasons.append({
            'name': 'mouth_exaggeration',
            'weight': 0.17,
            'detail': 'Mouth opening appears exaggerated relative to facial structure',
            'confidence': face_dyn.get('mouth_exaggeration_score', 0.6)
        })
    if face_dyn.get('mouth_static_score', 0.0) > 0.65:
        reasons.append({
            'name': 'mouth_static',
            'weight': 0.14,
            'detail': 'Mouth shape remains unnaturally static over time',
            'confidence': face_dyn.get('mouth_static_score', 0.6)
        })
    if face_dyn.get('eye_blink_anomaly', 0.0) > 0.65:
        reasons.append({
            'name': 'eye_blink',
            'weight': 0.13,
            'detail': 'Eye blink pattern deviates from natural behavior',
            'confidence': face_dyn.get('eye_blink_anomaly', 0.6)
        })
    if face_dyn.get('face_symmetry_drift', 0.0) > 0.65:
        reasons.append({
            'name': 'face_symmetry',
            'weight': 0.1,
            'detail': 'Facial symmetry drifts across frames (possible face swap artifacts)',
            'confidence': face_dyn.get('face_symmetry_drift', 0.6)
        })
    
    # Forensics
    forensics = analysis_results.get('forensics', {})
    flicker = forensics.get('flicker_score', 0.5)
    if flicker > 0.7:
        reasons.append({
            'name': 'flicker',
            'weight': 0.15,
            'detail': 'Temporal flickering detected (GAN artifact)',
            'confidence': flicker
        })
    
    prnu = forensics.get('prnu_score', 0.5)
    if prnu < 0.3:
        reasons.append({
            'name': 'prnu',
            'weight': 0.15,
            'detail': 'Weak camera sensor pattern (synthetic content)',
            'confidence': 1.0 - prnu
        })
    
    # Audio-visual
    av_analysis = analysis_results.get('av_analysis', {})
    av_score = av_analysis.get('sync_score', 0.5)
    if av_score < 0.5:
        reasons.append({
            'name': 'audio_sync',
            'weight': 0.1,
            'detail': 'Audio-visual synchronization issues detected',
            'confidence': 1.0 - av_score
        })
    
    # Sort by weight
    reasons.sort(key=lambda x: x['weight'], reverse=True)
    
    return reasons[:5]  # Top 5 reasons

