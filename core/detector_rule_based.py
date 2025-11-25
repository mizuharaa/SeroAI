"""Rule-based deepfake detector using forensic features.

This detector uses a dual-score system (real_score, fake_score) with confidence
to properly handle missing features and avoid false positives.
"""

import numpy as np
import math
from typing import Dict, List, Optional, Tuple, NamedTuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_detection import (
    USE_LEGACY_MODEL,
    LEGACY_MODEL_WEIGHT,
    WEIGHTS,
    HUMAN_PRESENCE_MIN_FRAMES,
    HUMAN_PRESENCE_MIN_FRACTION,
    HUMAN_DETECTION_FRACTION_THRESHOLD,
    WATERMARK_CONFIDENCE_THRESHOLD,
    WATERMARK_STRONG_THRESHOLD,
    DEEPFAKE_PROB_REAL_THRESHOLD,
    DEEPFAKE_PROB_UNCERTAIN_LOW,
    DEEPFAKE_PROB_UNCERTAIN_HIGH,
    DEEPFAKE_PROB_DEEPFAKE_THRESHOLD,
    EVIDENCE_SIGMOID_SLOPE,
    SHIMMER_INTENSITY_THRESHOLD,
    SHIMMER_INTENSITY_HIGH,
    BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD,
    BACKGROUND_MOTION_INCONSISTENCY_HIGH,
    FLAT_REGION_NOISE_DRIFT_THRESHOLD,
    FLAT_REGION_NOISE_DRIFT_HIGH,
    CONSTANT_MOTION_RATIO_LOW,
    CONSTANT_MOTION_RATIO_HIGH,
    MOTION_ENTROPY_LOW,
    MOTION_ENTROPY_HIGH,
    HAND_MISSING_FINGER_LOW,
    HAND_MISSING_FINGER_HIGH,
    HAND_ABNORMAL_ANGLE_LOW,
    HAND_ABNORMAL_ANGLE_HIGH,
    EXTREME_MOUTH_OPEN_LOW,
    EXTREME_MOUTH_OPEN_HIGH,
    BLINK_IRREGULARITY_LOW,
    BLINK_IRREGULARITY_HIGH,
    TEMPORAL_IDENTITY_STD_LOW,
    TEMPORAL_IDENTITY_STD_HIGH,
    HEAD_POSE_JITTER_LOW,
    HEAD_POSE_JITTER_HIGH,
    BOUNDARY_ARTIFACT_THRESHOLD,
    FREQ_ENERGY_RATIO_THRESHOLD,
    LIP_AUDIO_CORRELATION_THRESHOLD,
    AUDIO_SUSPICION_THRESHOLD,
    PHONEME_LAG_THRESHOLD,
    FACE_BODY_MOTION_COHERENCE_THRESHOLD,
    FACE_BODY_MOTION_COHERENCE_LOW,
    FACE_BODY_MOTION_COHERENCE_HIGH,
)

from features.feature_extractor import extract_all_features
from features.watermark_features import extract_watermark_features
from core.human_presence import detect_human_presence
from core.fusion import DeepfakeFusion  # For legacy model if enabled


class FeatureScores(NamedTuple):
    """Represents scores for a single forensic category."""
    real_score: float    # Evidence it is REAL (0-1)
    fake_score: float    # Evidence it is FAKE (0-1)
    confidence: float    # How reliable this feature is (0-1)
    weight: float        # Importance of this category


def soft_score(value: float, low: float, high: float) -> float:
    """
    Soft scoring function: maps [low, high] -> [0, 1], clamps outside.
    """
    if value <= low:
        return 0.0
    if value >= high:
        return 1.0
    return (value - low) / (high - low)


def aggregate_scores(feature_scores: Dict[str, FeatureScores]) -> Tuple[float, float, float]:
    """
    Aggregate per-category scores into final deepfake probability.
    
    Args:
        feature_scores: Dictionary mapping category names to FeatureScores
        
    Returns:
        Tuple of (deepfake_prob, real_evidence, fake_evidence)
    """
    # Compute weighted, confidence-adjusted evidence
    real_num = sum(f.real_score * f.confidence * f.weight for f in feature_scores.values())
    fake_num = sum(f.fake_score * f.confidence * f.weight for f in feature_scores.values())
    denom = sum(f.confidence * f.weight for f in feature_scores.values()) + 1e-6
    
    real_evidence = real_num / denom
    fake_evidence = fake_num / denom
    
    # Safeguard: if fake_evidence is very high (>0.7), don't let weak real_evidence dilute it
    if fake_evidence > 0.7 and real_evidence < 0.3:
        # Strong fake evidence should dominate
        fake_evidence = min(fake_evidence * 1.1, 1.0)
        real_evidence = real_evidence * 0.8  # Reduce weak real evidence
    
    # Convert evidence difference to deepfake probability using sigmoid
    x = fake_evidence - real_evidence
    
    # If fake evidence is much stronger, make it more decisive
    if fake_evidence > 0.5 and fake_evidence > real_evidence * 1.5:
        x = x * 1.3  # Boost the difference
    
    deepfake_prob = 1.0 / (1.0 + math.exp(-EVIDENCE_SIGMOID_SLOPE * x))
    
    return (deepfake_prob, real_evidence, fake_evidence)


class SeroRuleBasedDetector:
    """
    Rule-based detector using dual-score system (real_score, fake_score) with confidence.
    """
    
    def __init__(self):
        """Initialize the rule-based detector."""
        self.legacy_model = None
        if USE_LEGACY_MODEL:
            try:
                self.legacy_model = DeepfakeFusion()
                print("[rule_based] Legacy model enabled (weight={:.2f})".format(LEGACY_MODEL_WEIGHT))
            except Exception as e:
                print(f"[rule_based] Legacy model failed to load: {e}")
                self.legacy_model = None
    
    def detect(self, video_path: str) -> Dict:
        """
        Detect deepfake in video using rule-based forensic features.
        
        Returns:
            Dictionary with:
            - score: float [0, 1] - deepfake probability
            - label: str - "REAL", "DEEPFAKE", or "UNCERTAIN"
            - explanations: List[str] - human-readable explanations
            - features: Dict - raw feature values
        """
        # Extract all features
        features = extract_all_features(video_path)
        
        # Add watermark features
        watermark_features = extract_watermark_features(video_path)
        features.update(watermark_features)
        
        # Add human presence
        human_presence = detect_human_presence(video_path)
        features.update(human_presence)
        
        # Compute per-category scores
        category_scores = self._compute_category_scores(features)
        
        # Aggregate scores
        deepfake_prob, real_evidence, fake_evidence = aggregate_scores(category_scores)
        
        # Debug logging
        print("\n" + "=" * 60)
        print("[DEBUG] Per-Category Scores:")
        print("=" * 60)
        for category, scores in category_scores.items():
            print(f"  {category}:")
            print(f"    real_score={scores.real_score:.4f}, fake_score={scores.fake_score:.4f}")
            print(f"    confidence={scores.confidence:.4f}, weight={scores.weight:.4f}")
        print("=" * 60)
        print(f"[DEBUG] Aggregated Evidence:")
        print(f"  real_evidence={real_evidence:.4f}")
        print(f"  fake_evidence={fake_evidence:.4f}")
        print(f"  deepfake_prob={deepfake_prob:.4f}")
        print("=" * 60 + "\n")
        
        # Get label
        label = self._get_label(deepfake_prob, watermark_features)
        
        # Generate explanations
        explanations = self._generate_explanations(category_scores, real_evidence, fake_evidence, deepfake_prob)
        
        # Optionally blend with legacy model (disabled by default)
        if self.legacy_model is not None and USE_LEGACY_MODEL:
            try:
                legacy_score = 0.5  # Placeholder - would need to call legacy model
                blended_prob = (1.0 - LEGACY_MODEL_WEIGHT) * deepfake_prob + LEGACY_MODEL_WEIGHT * legacy_score
                deepfake_prob = blended_prob
                explanations.append(f"Legacy model blended (weight={LEGACY_MODEL_WEIGHT:.2f})")
            except Exception as e:
                print(f"[rule_based] Legacy model prediction failed: {e}")
        
        # Watermark forcing (if detected, ensure minimum score)
        watermark_detected_flag = watermark_features.get('watermark_detected', 0.0) > 0.5
        watermark_conf = watermark_features.get('watermark_confidence', 0.0)
        if (watermark_detected_flag or watermark_conf >= WATERMARK_CONFIDENCE_THRESHOLD) and deepfake_prob < 0.5:
            deepfake_prob = max(deepfake_prob, 0.5)
            explanations.append(
                f"⚠️ Generator watermark detected (conf={watermark_conf:.2f}); "
                f"forcing minimum probability to 0.5."
            )
            label = self._get_label(deepfake_prob, watermark_features)
        
        return {
            'score': float(np.clip(deepfake_prob, 0.0, 1.0)),
            'label': label,
            'explanations': explanations,
            'features': features,
        }
    
    def _compute_category_scores(self, features: Dict[str, float]) -> Dict[str, FeatureScores]:
        """
        Compute per-category scores using dual-score system.
        
        Returns:
            Dictionary mapping category names to FeatureScores
        """
        category_scores = {}
        
        # 1. Watermark
        watermark_detected = features.get('watermark_detected', 0.0) > 0.5
        watermark_conf = features.get('watermark_confidence', 0.0)
        
        if watermark_detected and watermark_conf >= WATERMARK_CONFIDENCE_THRESHOLD:
            # Watermark detected = fake evidence
            fake_score = min(watermark_conf * 1.2, 1.0) if watermark_conf >= WATERMARK_STRONG_THRESHOLD else watermark_conf
            category_scores['watermark'] = FeatureScores(
                real_score=0.0,
                fake_score=fake_score,
                confidence=watermark_conf,
                weight=WEIGHTS['watermark']
            )
        else:
            # No watermark = neutral (not evidence of real, just absence of fake marker)
            category_scores['watermark'] = FeatureScores(
                real_score=0.0,
                fake_score=0.0,
                confidence=0.0,  # Low confidence = neutral
                weight=WEIGHTS['watermark']
            )
        
        # 2. Noise/Shimmer
        shimmer_intensity = features.get('shimmer_intensity', 0.0)
        bg_inconsistency = features.get('background_motion_inconsistency', 0.0)
        noise_drift = features.get('flat_region_noise_drift', 0.0)
        constant_motion_ratio = features.get('constant_motion_ratio', 0.5)
        motion_entropy_face = features.get('motion_entropy_face', 0.5)
        
        # Compute fake evidence (suspicious values)
        fake_evidence_list = []
        real_evidence_list = []
        confidence_list = []
        
        si_fake = soft_score(shimmer_intensity, SHIMMER_INTENSITY_THRESHOLD, SHIMMER_INTENSITY_HIGH)
        if si_fake > 0:
            fake_evidence_list.append(si_fake)
            confidence_list.append(min(shimmer_intensity / SHIMMER_INTENSITY_HIGH, 1.0))
        
        bmi_fake = soft_score(bg_inconsistency, BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD, BACKGROUND_MOTION_INCONSISTENCY_HIGH)
        if bmi_fake > 0:
            fake_evidence_list.append(bmi_fake)
            confidence_list.append(min(bg_inconsistency / BACKGROUND_MOTION_INCONSISTENCY_HIGH, 1.0))
        
        frd_fake = soft_score(noise_drift, FLAT_REGION_NOISE_DRIFT_THRESHOLD, FLAT_REGION_NOISE_DRIFT_HIGH)
        if frd_fake > 0:
            fake_evidence_list.append(frd_fake)
            confidence_list.append(min(noise_drift / FLAT_REGION_NOISE_DRIFT_HIGH, 1.0))
        
        cmr_fake = soft_score(constant_motion_ratio, CONSTANT_MOTION_RATIO_LOW, CONSTANT_MOTION_RATIO_HIGH)
        if cmr_fake > 0:
            fake_evidence_list.append(cmr_fake)
            confidence_list.append(min(constant_motion_ratio / CONSTANT_MOTION_RATIO_HIGH, 1.0))
        
        mef_fake = soft_score(1.0 - motion_entropy_face, MOTION_ENTROPY_LOW, MOTION_ENTROPY_HIGH)
        if mef_fake > 0:
            fake_evidence_list.append(mef_fake)
            confidence_list.append(min((1.0 - motion_entropy_face) / MOTION_ENTROPY_HIGH, 1.0))
        
        # Real evidence: normal values (low shimmer, normal entropy, normal motion)
        if shimmer_intensity < SHIMMER_INTENSITY_THRESHOLD * 0.5:
            real_evidence_list.append(1.0 - (shimmer_intensity / (SHIMMER_INTENSITY_THRESHOLD * 0.5 + 1e-6)))
        if motion_entropy_face > 0.5:  # Normal entropy range
            real_evidence_list.append(min((motion_entropy_face - 0.5) / 0.3, 1.0))
        if constant_motion_ratio < CONSTANT_MOTION_RATIO_LOW * 0.7:
            real_evidence_list.append(1.0 - (constant_motion_ratio / (CONSTANT_MOTION_RATIO_LOW * 0.7 + 1e-6)))
        
        fake_score = float(np.mean(fake_evidence_list)) if fake_evidence_list else 0.0
        real_score = float(np.mean(real_evidence_list)) if real_evidence_list else 0.0
        
        # Confidence should reflect measurement quality and reliability
        # Be conservative: only high confidence if we have strong, multiple signals
        if fake_evidence_list or real_evidence_list:
            evidence_strength = max(fake_score, real_score)
            signal_count = len(fake_evidence_list) + len(real_evidence_list)
            
            # Confidence = evidence strength * signal reliability factor
            # Require multiple strong signals for high confidence
            if signal_count >= 3 and evidence_strength > 0.6:
                confidence = min(evidence_strength * 0.9, 0.85)  # Cap at 85% even for strong evidence
            elif signal_count >= 2 and evidence_strength > 0.5:
                confidence = min(evidence_strength * 0.8, 0.75)  # Cap at 75%
            elif signal_count >= 1 and evidence_strength > 0.4:
                confidence = min(evidence_strength * 0.7, 0.65)  # Cap at 65%
            else:
                confidence = evidence_strength * 0.5  # Weak evidence = low confidence
        else:
            confidence = 0.0  # No evidence = no confidence
        
        category_scores['noise_shimmer'] = FeatureScores(
            real_score=real_score,
            fake_score=fake_score,
            confidence=confidence,
            weight=WEIGHTS['noise_shimmer']
        )
        
        # 3. Anatomy (only if human present)
        human_detection_fraction = features.get('human_detection_fraction', 0.0)
        human_present = human_detection_fraction >= HUMAN_DETECTION_FRACTION_THRESHOLD
        
        if human_present:
            hand_missing = features.get('hand_missing_finger_ratio', 0.0)
            hand_abnormal = features.get('hand_abnormal_angle_ratio', 0.0)
            mouth_extreme = features.get('extreme_mouth_open_frequency', 0.0)
            blink_irregular = features.get('eye_blink_irregularity', 0.5)
            
            fake_evidence_list = []
            real_evidence_list = []
            confidence_list = []
            
            # Fake evidence: abnormal anatomy
            mf_fake = soft_score(hand_missing, HAND_MISSING_FINGER_LOW, HAND_MISSING_FINGER_HIGH)
            if mf_fake > 0:
                fake_evidence_list.append(mf_fake)
                confidence_list.append(min(hand_missing / HAND_MISSING_FINGER_HIGH, 1.0))
            
            aa_fake = soft_score(hand_abnormal, HAND_ABNORMAL_ANGLE_LOW, HAND_ABNORMAL_ANGLE_HIGH)
            if aa_fake > 0:
                fake_evidence_list.append(aa_fake)
                confidence_list.append(min(hand_abnormal / HAND_ABNORMAL_ANGLE_HIGH, 1.0))
            
            em_fake = soft_score(mouth_extreme, EXTREME_MOUTH_OPEN_LOW, EXTREME_MOUTH_OPEN_HIGH)
            if em_fake > 0:
                fake_evidence_list.append(em_fake)
                confidence_list.append(min(mouth_extreme / EXTREME_MOUTH_OPEN_HIGH, 1.0))
            
            bi_fake = soft_score(blink_irregular, BLINK_IRREGULARITY_LOW, BLINK_IRREGULARITY_HIGH)
            if bi_fake > 0:
                fake_evidence_list.append(bi_fake)
                confidence_list.append(min(blink_irregular / BLINK_IRREGULARITY_HIGH, 1.0))
            
            # Real evidence: normal anatomy (low abnormal ratios)
            if hand_missing < HAND_MISSING_FINGER_LOW * 0.5:
                real_evidence_list.append(1.0 - (hand_missing / (HAND_MISSING_FINGER_LOW * 0.5 + 1e-6)))
            if hand_abnormal < HAND_ABNORMAL_ANGLE_LOW * 0.5:
                real_evidence_list.append(1.0 - (hand_abnormal / (HAND_ABNORMAL_ANGLE_LOW * 0.5 + 1e-6)))
            if mouth_extreme < EXTREME_MOUTH_OPEN_LOW * 0.5:
                real_evidence_list.append(1.0 - (mouth_extreme / (EXTREME_MOUTH_OPEN_LOW * 0.5 + 1e-6)))
            if blink_irregular < BLINK_IRREGULARITY_LOW * 0.7:  # Normal blink patterns
                real_evidence_list.append(1.0 - (blink_irregular / (BLINK_IRREGULARITY_LOW * 0.7 + 1e-6)))
            
            fake_score = float(np.mean(fake_evidence_list)) if fake_evidence_list else 0.0
            real_score = float(np.mean(real_evidence_list)) if real_evidence_list else 0.0
            
            # Confidence based on evidence strength and signal count (conservative)
            if fake_evidence_list or real_evidence_list:
                evidence_strength = max(fake_score, real_score)
                signal_count = len(fake_evidence_list) + len(real_evidence_list)
                
                if signal_count >= 3 and evidence_strength > 0.6:
                    confidence = min(evidence_strength * 0.9, 0.85)
                elif signal_count >= 2 and evidence_strength > 0.5:
                    confidence = min(evidence_strength * 0.8, 0.75)
                elif signal_count >= 1 and evidence_strength > 0.4:
                    confidence = min(evidence_strength * 0.7, 0.65)
                else:
                    confidence = evidence_strength * 0.5
            else:
                confidence = 0.0
            
            category_scores['anatomy'] = FeatureScores(
                real_score=real_score,
                fake_score=fake_score,
                confidence=confidence,
                weight=WEIGHTS['anatomy']
            )
        else:
            # No human detected = neutral (confidence = 0)
            category_scores['anatomy'] = FeatureScores(
                real_score=0.0,
                fake_score=0.0,
                confidence=0.0,
                weight=WEIGHTS['anatomy']
            )
        
        # 4. Temporal identity
        temporal_std = features.get('temporal_identity_std', 0.5)
        head_jitter = features.get('head_pose_jitter', 0.5)
        face_body_coherence = features.get('face_body_motion_coherence', 1.0)
        
        fake_evidence_list = []
        real_evidence_list = []
        confidence_list = []
        
        # Fake evidence: high temporal inconsistency
        ti_fake = soft_score(temporal_std, TEMPORAL_IDENTITY_STD_LOW, TEMPORAL_IDENTITY_STD_HIGH)
        if ti_fake > 0:
            fake_evidence_list.append(ti_fake)
            confidence_list.append(min(temporal_std / TEMPORAL_IDENTITY_STD_HIGH, 1.0))
        
        hp_fake = soft_score(head_jitter, HEAD_POSE_JITTER_LOW, HEAD_POSE_JITTER_HIGH)
        if hp_fake > 0:
            fake_evidence_list.append(hp_fake)
            confidence_list.append(min(head_jitter / HEAD_POSE_JITTER_HIGH, 1.0))
        
        # Face-body coherence: low coherence = fake, high coherence = real
        fbc_drift = 1.0 - face_body_coherence
        fbc_fake = soft_score(fbc_drift, FACE_BODY_MOTION_COHERENCE_LOW, FACE_BODY_MOTION_COHERENCE_HIGH)
        if fbc_fake > 0:
            fake_evidence_list.append(fbc_fake)
            confidence_list.append(min(fbc_drift / FACE_BODY_MOTION_COHERENCE_HIGH, 1.0))
        
        # Real evidence: stable identity, low jitter, high coherence
        if temporal_std < TEMPORAL_IDENTITY_STD_LOW * 0.7:
            real_evidence_list.append(1.0 - (temporal_std / (TEMPORAL_IDENTITY_STD_LOW * 0.7 + 1e-6)))
        if head_jitter < HEAD_POSE_JITTER_LOW * 0.7:
            real_evidence_list.append(1.0 - (head_jitter / (HEAD_POSE_JITTER_LOW * 0.7 + 1e-6)))
        if face_body_coherence > 0.8:  # High coherence = strong real evidence
            real_evidence_list.append((face_body_coherence - 0.8) / 0.2)
        
        fake_score = float(np.mean(fake_evidence_list)) if fake_evidence_list else 0.0
        real_score = float(np.mean(real_evidence_list)) if real_evidence_list else 0.0
        
        # Confidence based on evidence strength and signal count
        if fake_evidence_list or real_evidence_list:
            evidence_strength = max(fake_score, real_score)
            signal_count = len(fake_evidence_list) + len(real_evidence_list)
            confidence = min(evidence_strength * (1.0 + signal_count * 0.1), 1.0)
        else:
            confidence = 0.0
        
        category_scores['temporal_identity'] = FeatureScores(
            real_score=real_score,
            fake_score=fake_score,
            confidence=confidence,
            weight=WEIGHTS['temporal_identity']
        )
        
        # 5. Frequency artifacts
        boundary_artifacts = features.get('boundary_artifact_score', 0.0)
        freq_ratio = features.get('freq_energy_ratio', 0.5)
        
        fake_evidence_list = []
        real_evidence_list = []
        confidence_list = []
        
        if boundary_artifacts >= BOUNDARY_ARTIFACT_THRESHOLD:
            fake_evidence_list.append(min((boundary_artifacts - BOUNDARY_ARTIFACT_THRESHOLD) / (1.0 - BOUNDARY_ARTIFACT_THRESHOLD + 1e-6), 1.0))
            confidence_list.append(min(boundary_artifacts, 1.0))
        
        if freq_ratio >= FREQ_ENERGY_RATIO_THRESHOLD:
            fake_evidence_list.append(min((freq_ratio - FREQ_ENERGY_RATIO_THRESHOLD) / (1.0 - FREQ_ENERGY_RATIO_THRESHOLD + 1e-6), 1.0))
            confidence_list.append(min(freq_ratio, 1.0))
        
        # Real evidence: low artifacts, normal frequency ratios
        if boundary_artifacts < BOUNDARY_ARTIFACT_THRESHOLD * 0.7:
            real_evidence_list.append(1.0 - (boundary_artifacts / (BOUNDARY_ARTIFACT_THRESHOLD * 0.7 + 1e-6)))
        if freq_ratio < FREQ_ENERGY_RATIO_THRESHOLD * 0.8:
            real_evidence_list.append(1.0 - ((freq_ratio - 0.5) / (FREQ_ENERGY_RATIO_THRESHOLD * 0.8 - 0.5 + 1e-6)))
        
        fake_score = float(np.mean(fake_evidence_list)) if fake_evidence_list else 0.0
        real_score = float(np.mean(real_evidence_list)) if real_evidence_list else 0.0
        
        # Confidence based on evidence strength and signal count
        if fake_evidence_list or real_evidence_list:
            evidence_strength = max(fake_score, real_score)
            signal_count = len(fake_evidence_list) + len(real_evidence_list)
            confidence = min(evidence_strength * (1.0 + signal_count * 0.1), 1.0)
        else:
            confidence = 0.0
        
        category_scores['frequency_artifacts'] = FeatureScores(
            real_score=real_score,
            fake_score=fake_score,
            confidence=confidence,
            weight=WEIGHTS['frequency_artifacts']
        )
        
        # 6. Audio sync
        has_audio = features.get('has_audio', 0.0) > 0.5
        if has_audio:
            lip_corr = features.get('lip_audio_correlation', 0.5)
            phoneme_lag = features.get('avg_phoneme_lag', 0.0)
            
            fake_evidence_list = []
            real_evidence_list = []
            confidence_list = []
            
            audio_suspicion = 1.0 - lip_corr
            if audio_suspicion > AUDIO_SUSPICION_THRESHOLD:
                fake_evidence_list.append(min((audio_suspicion - AUDIO_SUSPICION_THRESHOLD) / (1.0 - AUDIO_SUSPICION_THRESHOLD + 1e-6), 1.0))
                confidence_list.append(min(audio_suspicion, 1.0))
            
            if phoneme_lag >= PHONEME_LAG_THRESHOLD:
                fake_evidence_list.append(min((phoneme_lag - PHONEME_LAG_THRESHOLD) / (1.0 - PHONEME_LAG_THRESHOLD + 1e-6), 1.0))
                confidence_list.append(min(phoneme_lag, 1.0))
            
            # Real evidence: good correlation, low lag
            if lip_corr > 0.6:  # Good correlation
                real_evidence_list.append((lip_corr - 0.6) / 0.4)
            if phoneme_lag < PHONEME_LAG_THRESHOLD * 0.7:
                real_evidence_list.append(1.0 - (phoneme_lag / (PHONEME_LAG_THRESHOLD * 0.7 + 1e-6)))
            
            fake_score = float(np.mean(fake_evidence_list)) if fake_evidence_list else 0.0
            real_score = float(np.mean(real_evidence_list)) if real_evidence_list else 0.0
            
            # Confidence based on evidence strength and signal count (conservative)
            if fake_evidence_list or real_evidence_list:
                evidence_strength = max(fake_score, real_score)
                signal_count = len(fake_evidence_list) + len(real_evidence_list)
                
                if signal_count >= 3 and evidence_strength > 0.6:
                    confidence = min(evidence_strength * 0.9, 0.85)
                elif signal_count >= 2 and evidence_strength > 0.5:
                    confidence = min(evidence_strength * 0.8, 0.75)
                elif signal_count >= 1 and evidence_strength > 0.4:
                    confidence = min(evidence_strength * 0.7, 0.65)
                else:
                    confidence = evidence_strength * 0.5
            else:
                confidence = 0.0
            
            category_scores['audio_sync'] = FeatureScores(
                real_score=real_score,
                fake_score=fake_score,
                confidence=confidence,
                weight=WEIGHTS['audio_sync']
            )
        else:
            # No audio = neutral (confidence = 0)
            category_scores['audio_sync'] = FeatureScores(
                real_score=0.0,
                fake_score=0.0,
                confidence=0.0,
                weight=WEIGHTS['audio_sync']
            )
        
        return category_scores
    
    def _get_label(self, deepfake_prob: float, watermark_features: Dict) -> str:
        """Get label from deepfake probability."""
        if deepfake_prob < DEEPFAKE_PROB_REAL_THRESHOLD:
            return "REAL"
        elif deepfake_prob >= DEEPFAKE_PROB_DEEPFAKE_THRESHOLD:
            return "DEEPFAKE"
        else:
            return "UNCERTAIN"
    
    def _generate_explanations(
        self,
        category_scores: Dict[str, FeatureScores],
        real_evidence: float,
        fake_evidence: float,
        deepfake_prob: float
    ) -> List[str]:
        """Generate human-readable explanations."""
        explanations = []
        
        # Per-category explanations
        for category, scores in category_scores.items():
            if scores.confidence > 0.1:  # Only explain if confident
                if scores.fake_score > 0.3:
                    explanations.append(
                        f"{category}: Strong fake evidence (fake={scores.fake_score:.2f}, conf={scores.confidence:.2f})"
                    )
                elif scores.real_score > 0.3:
                    explanations.append(
                        f"{category}: Strong real evidence (real={scores.real_score:.2f}, conf={scores.confidence:.2f})"
                    )
        
        # Overall summary
        explanations.append(
            f"Overall: real_evidence={real_evidence:.3f}, fake_evidence={fake_evidence:.3f}, "
            f"deepfake_prob={deepfake_prob:.3f}"
        )
        
        return explanations
