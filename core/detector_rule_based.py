"""Rule-based deepfake detector using forensic features.

This detector prioritizes explicit forensic features over biased
supervised models. It uses weighted feature signals to compute
a deepfake probability.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
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
    WATERMARK_FORCE_MIN_SCORE,
    WATERMARK_FORCE_UNCERTAIN,
    SCORE_REAL_THRESHOLD,
    SCORE_UNCERTAIN_LOW,
    SCORE_UNCERTAIN_HIGH,
    SCORE_DEEPFAKE_THRESHOLD,
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
    CUMULATIVE_EVIDENCE_BOOST_3PLUS,
    CUMULATIVE_EVIDENCE_BOOST_2,
)

from features.feature_extractor import extract_all_features
from features.watermark_features import extract_watermark_features
from core.human_presence import detect_human_presence
from core.fusion import DeepfakeFusion  # For legacy model if enabled


def soft_score(value: float, low: float, high: float) -> float:
    """
    Soft scoring function: maps [low, high] -> [0, 1], clamps outside.
    
    Args:
        value: Input value to score
        low: Lower threshold (below this = 0.0)
        high: Upper threshold (above this = 1.0)
        
    Returns:
        Score in [0, 1]
    """
    if value <= low:
        return 0.0
    if value >= high:
        return 1.0
    return (value - low) / (high - low)


class SeroRuleBasedDetector:
    """
    Rule-based detector that uses weighted forensic features.
    
    This detector ignores or heavily down-weights the old biased
    supervised model and instead relies on explicit forensic signals.
    """
    
    def __init__(self):
        """Initialize the rule-based detector."""
        self.legacy_model = None
        if USE_LEGACY_MODEL:
            try:
                self.legacy_model = DeepfakeFusion()
                print("[rule_based] Legacy model enabled (weight={:.2f})".format(LEGACY_MODEL_WEIGHT))
            except Exception as e:
                print(f"[rule_based] Failed to load legacy model: {e}")
                self.legacy_model = None
    
    def detect(self, video_path: str) -> Dict:
        """
        Detect deepfake using rule-based forensic features.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with:
            - score: float [0, 1] - deepfake probability
            - label: str - "REAL", "DEEPFAKE", or "UNCERTAIN"
            - explanations: List[str] - human-readable explanations
            - features: Dict - all extracted features
        """
        # Extract all features
        features = extract_all_features(
            video_path,
            enable_motion=True,
            enable_anatomy=True,
            enable_frequency=True,
            enable_audio_sync=True,
            enable_hand_analysis=True
        )
        
        # Extract watermark features
        watermark_features = extract_watermark_features(video_path)
        features.update(watermark_features)
        
        # Detect human presence
        human_presence = detect_human_presence(
            video_path,
            min_frames=HUMAN_PRESENCE_MIN_FRAMES,
            min_fraction=HUMAN_PRESENCE_MIN_FRACTION
        )
        features.update(human_presence)
        
        # Compute rule-based score
        score, explanations = self._compute_score(features)
        
        # Apply watermark forcing
        if watermark_features.get('watermark_detected', 0.0) > 0.5:
            watermark_conf = watermark_features.get('watermark_confidence', 0.0)
            if watermark_conf >= WATERMARK_CONFIDENCE_THRESHOLD:
                score = max(score, WATERMARK_FORCE_MIN_SCORE)
                explanations.append(
                    f"Generator-like watermark detected (conf={watermark_conf:.2f}); "
                    f"forcing score >= {WATERMARK_FORCE_MIN_SCORE:.2f}"
                )
        
        # Get label
        label = self._get_label(score, watermark_features)
        
        # Optionally blend with legacy model (disabled by default due to biased training)
        # NOTE: The legacy supervised model was trained on a biased dataset:
        # - Deepfakes: mainly talking-head clips (static, exaggerated, grainy)
        # - Real: wide variety of normal clips
        # This caused it to learn "if it doesn't look like talking deepfake → mark as REAL"
        # We disable it by default (USE_LEGACY_MODEL = False) to avoid this bias.
        if self.legacy_model is not None and USE_LEGACY_MODEL:
            try:
                # Legacy model expects analysis_results format
                # For now, use a simplified approach
                legacy_score = 0.5  # Default if we can't compute
                # TODO: Convert features to legacy format if needed
                
                # Blend scores (legacy weight should be very low, e.g., 0.1)
                score = (1.0 - LEGACY_MODEL_WEIGHT) * score + LEGACY_MODEL_WEIGHT * legacy_score
                explanations.append(
                    f"Legacy model blended (weight={LEGACY_MODEL_WEIGHT:.2f})"
                )
            except Exception as e:
                print(f"[rule_based] Legacy model prediction failed: {e}")
        
        return {
            'score': float(np.clip(score, 0.0, 1.0)),
            'label': label,
            'explanations': explanations,
            'features': features,
        }
    
    def _compute_score(self, features: Dict[str, float]) -> Tuple[float, List[str]]:
        """
        Compute deepfake score from features using weighted rules.
        
        Returns:
            Tuple of (score, explanations)
        """
        explanations = []
        category_scores = {}
        
        # 1. Watermark evidence (highest weight)
        watermark_detected = features.get('watermark_detected', 0.0) > 0.5
        watermark_conf = features.get('watermark_confidence', 0.0)
        
        if watermark_detected:
            # Always give some positive score if we see a watermark
            # Use a low threshold for "strong" watermark, but still use the raw confidence below it
            if watermark_conf >= WATERMARK_STRONG_THRESHOLD:
                watermark_score = min(watermark_conf * 1.2, 1.0)
            else:
                # Weak confidence but still non-zero evidence
                watermark_score = watermark_conf
            category_scores['watermark'] = watermark_score
            explanations.append(
                f"Watermark detected (confidence={watermark_conf:.2f}, score={watermark_score:.2f})"
            )
        else:
            category_scores['watermark'] = 0.0
        
        # 2. Noise/Shimmer evidence (high weight) - using soft scoring
        shimmer_intensity = features.get('shimmer_intensity', 0.0)
        bg_inconsistency = features.get('background_motion_inconsistency', 0.0)
        noise_drift = features.get('flat_region_noise_drift', 0.0)
        constant_motion_ratio = features.get('constant_motion_ratio', 0.5)
        motion_entropy_face = features.get('motion_entropy_face', 0.5)
        
        shimmer_evidence = []
        
        # Soft scoring for shimmer features
        si = soft_score(shimmer_intensity, SHIMMER_INTENSITY_THRESHOLD, SHIMMER_INTENSITY_HIGH)
        if si > 0:
            shimmer_evidence.append(si)
            explanations.append(
                f"Shimmer detected (intensity={shimmer_intensity:.2f}, score={si:.2f})"
            )
        
        bmi = soft_score(bg_inconsistency, BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD, 
                        BACKGROUND_MOTION_INCONSISTENCY_HIGH)
        if bmi > 0:
            shimmer_evidence.append(bmi)
            explanations.append(
                f"Background motion inconsistency (raw={bg_inconsistency:.2f}, score={bmi:.2f})"
            )
        
        frd = soft_score(noise_drift, FLAT_REGION_NOISE_DRIFT_THRESHOLD, FLAT_REGION_NOISE_DRIFT_HIGH)
        if frd > 0:
            shimmer_evidence.append(frd)
            explanations.append(
                f"Flat region noise drift (raw={noise_drift:.2f}, score={frd:.2f})"
            )
        
        # Constant motion ratio (AI videos have overly coherent motion)
        cmr = soft_score(constant_motion_ratio, CONSTANT_MOTION_RATIO_LOW, CONSTANT_MOTION_RATIO_HIGH)
        if cmr > 0:
            shimmer_evidence.append(cmr)
            explanations.append(
                f"Constant motion pixels detected (ratio={constant_motion_ratio:.2f}, score={cmr:.2f})"
            )
        
        # Motion entropy (low entropy = suspicious, too coherent)
        mef = soft_score(1.0 - motion_entropy_face, MOTION_ENTROPY_LOW, MOTION_ENTROPY_HIGH)
        if mef > 0:
            shimmer_evidence.append(mef)
            explanations.append(
                f"Low motion entropy (entropy={motion_entropy_face:.2f}, suspicion={mef:.2f})"
            )
        
        if shimmer_evidence:
            category_scores['noise_shimmer'] = np.mean(shimmer_evidence)
            explanations.append(
                "Detected strong shimmer / crawling grain and constant-motion textures typical of AI-generated video."
            )
        else:
            category_scores['noise_shimmer'] = 0.0
        
        # 3. Anatomy features (only if human present)
        human_detection_fraction = features.get('human_detection_fraction', 0.0)
        human_present = human_detection_fraction >= HUMAN_DETECTION_FRACTION_THRESHOLD
        
        if human_present:
            anatomy_evidence = []
            
            # Hand features - using soft scoring
            hand_missing = features.get('hand_missing_finger_ratio', 0.0)
            mf = soft_score(hand_missing, HAND_MISSING_FINGER_LOW, HAND_MISSING_FINGER_HIGH)
            if mf > 0:
                anatomy_evidence.append(mf)
                explanations.append(
                    f"Hand skeleton anomalies: missing/merged fingers (ratio={hand_missing:.2f}, score={mf:.2f})"
                )
            
            hand_abnormal = features.get('hand_abnormal_angle_ratio', 0.0)
            aa = soft_score(hand_abnormal, HAND_ABNORMAL_ANGLE_LOW, HAND_ABNORMAL_ANGLE_HIGH)
            if aa > 0:
                anatomy_evidence.append(aa)
                explanations.append(
                    f"Hand abnormal joint angles (ratio={hand_abnormal:.2f}, score={aa:.2f})"
                )
            
            # Mouth features - using soft scoring
            mouth_extreme = features.get('extreme_mouth_open_frequency', 0.0)
            em = soft_score(mouth_extreme, EXTREME_MOUTH_OPEN_LOW, EXTREME_MOUTH_OPEN_HIGH)
            if em > 0:
                anatomy_evidence.append(em)
                explanations.append(
                    f"Extreme mouth openings detected (frequency={mouth_extreme:.2f}, score={em:.2f})"
                )
            
            # Eye features - using soft scoring
            blink_irregular = features.get('eye_blink_irregularity', 0.5)
            bi = soft_score(blink_irregular, BLINK_IRREGULARITY_LOW, BLINK_IRREGULARITY_HIGH)
            if bi > 0:
                anatomy_evidence.append(bi)
                explanations.append(
                    f"Irregular blink patterns (raw={blink_irregular:.2f}, score={bi:.2f})"
                )
            
            if anatomy_evidence:
                category_scores['anatomy'] = np.mean(anatomy_evidence)
                explanations.append(
                    "Detected unnatural anatomy: finger shapes/angles or mouth/blink patterns inconsistent with real humans."
                )
            else:
                category_scores['anatomy'] = 0.0
        else:
            category_scores['anatomy'] = 0.0
            explanations.append(
                f"No human detected in enough frames (fraction={human_detection_fraction:.2f} < {HUMAN_DETECTION_FRACTION_THRESHOLD:.2f}); anatomy-based cues ignored."
            )
        
        # 4. Temporal identity - using soft scoring
        temporal_std = features.get('temporal_identity_std', 0.5)
        head_jitter = features.get('head_pose_jitter', 0.5)
        
        temporal_evidence = []
        ti = soft_score(temporal_std, TEMPORAL_IDENTITY_STD_LOW, TEMPORAL_IDENTITY_STD_HIGH)
        if ti > 0:
            temporal_evidence.append(ti)
            explanations.append(
                f"Temporal identity inconsistency (std={temporal_std:.2f}, score={ti:.2f})"
            )
        
        hp = soft_score(head_jitter, HEAD_POSE_JITTER_LOW, HEAD_POSE_JITTER_HIGH)
        if hp > 0:
            temporal_evidence.append(hp)
            explanations.append(
                f"Head pose jitter detected (raw={head_jitter:.2f}, score={hp:.2f})"
            )
        
        if temporal_evidence:
            category_scores['temporal_identity'] = np.mean(temporal_evidence)
            explanations.append(
                "Detected unstable facial identity / head pose over time, suggesting temporal inconsistency."
            )
        else:
            category_scores['temporal_identity'] = 0.0
        
        # 5. Frequency artifacts
        boundary_artifacts = features.get('boundary_artifact_score', 0.0)
        freq_ratio = features.get('freq_energy_ratio', 0.5)
        
        freq_evidence = []
        if boundary_artifacts >= BOUNDARY_ARTIFACT_THRESHOLD:
            freq_evidence.append(boundary_artifacts)
            explanations.append(
                f"Boundary artifacts detected (score={boundary_artifacts:.2f})"
            )
        if freq_ratio >= FREQ_ENERGY_RATIO_THRESHOLD:
            freq_evidence.append((freq_ratio - 0.5) * 2.0)  # Normalize
            explanations.append(
                f"Abnormal frequency ratio (score={freq_ratio:.2f})"
            )
        
        if freq_evidence:
            category_scores['frequency_artifacts'] = np.mean(freq_evidence)
        else:
            category_scores['frequency_artifacts'] = 0.0
        
        # 6. Audio sync
        has_audio = features.get('has_audio', 0.0) > 0.5
        if has_audio:
            lip_corr = features.get('lip_audio_correlation', 0.5)
            phoneme_lag = features.get('avg_phoneme_lag', 0.0)
            
            audio_evidence = []
            audio_suspicion = 1.0 - lip_corr  # Invert: low corr = high suspicion
            
            # Treat correlation below ~0.45 as suspicious (equivalent to suspicion > 0.55)
            if audio_suspicion > AUDIO_SUSPICION_THRESHOLD:
                audio_evidence.append(audio_suspicion)
                explanations.append(
                    f"Poor lip-audio correlation (corr={lip_corr:.2f}, suspicion={audio_suspicion:.2f})"
                )
            
            if phoneme_lag >= PHONEME_LAG_THRESHOLD:
                audio_evidence.append(phoneme_lag)
                explanations.append(
                    f"Phoneme lag detected (lag={phoneme_lag:.2f})"
                )
            
            if audio_evidence:
                category_scores['audio_sync'] = np.mean(audio_evidence)
            else:
                category_scores['audio_sync'] = 0.0
        else:
            category_scores['audio_sync'] = 0.0
        
        # Compute weighted score with debug logging
        print(f"[DEBUG] Category scores: {category_scores}")
        total_score = 0.0
        total_weight = 0.0
        
        print("[DEBUG] Weighted contributions:")
        for category, weight in WEIGHTS.items():
            score = category_scores.get(category, 0.0)
            contrib = score * weight
            print(f"  {category}: score={score:.4f}, weight={weight:.2f}, contrib={contrib:.4f}")
            total_score += contrib
            total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.5  # Neutral if no evidence
        
        print(f"[DEBUG] Total_score={total_score:.4f}, Total_weight={total_weight:.4f}, Final_score={final_score:.4f}")
        
        # Cumulative evidence boost
        evidence_count = sum(1 for s in category_scores.values() if s > 0.0)
        
        if evidence_count >= 3:
            final_score = min(final_score * CUMULATIVE_EVIDENCE_BOOST_3PLUS, 1.0)
            explanations.append(
                f"Multiple independent evidence categories ({evidence_count}) indicate deepfake; boosting score by {CUMULATIVE_EVIDENCE_BOOST_3PLUS:.1f}x."
            )
            print(f"[DEBUG] Cumulative boost applied: {evidence_count} categories, multiplier={CUMULATIVE_EVIDENCE_BOOST_3PLUS:.1f}x")
        elif evidence_count == 2:
            final_score = min(final_score * CUMULATIVE_EVIDENCE_BOOST_2, 1.0)
            explanations.append(
                f"Two evidence categories indicate deepfake; slight boost applied ({CUMULATIVE_EVIDENCE_BOOST_2:.1f}x)."
            )
            print(f"[DEBUG] Cumulative boost applied: {evidence_count} categories, multiplier={CUMULATIVE_EVIDENCE_BOOST_2:.1f}x")
        
        print(f"[DEBUG] Final score after boost: {final_score:.4f}")
        
        return float(np.clip(final_score, 0.0, 1.0)), explanations
    
    def _get_label(self, score: float, watermark_features: Dict) -> str:
        """Get label from score."""
        # If watermark detected and forcing uncertain, never return REAL
        watermark_detected = watermark_features.get('watermark_detected', 0.0) > 0.5
        watermark_conf = watermark_features.get('watermark_confidence', 0.0)
        
        if watermark_detected and watermark_conf >= WATERMARK_CONFIDENCE_THRESHOLD and WATERMARK_FORCE_UNCERTAIN:
            if score < SCORE_DEEPFAKE_THRESHOLD:
                return "UNCERTAIN"
        
        if score < SCORE_REAL_THRESHOLD:
            return "REAL"
        elif score >= SCORE_DEEPFAKE_THRESHOLD:
            return "DEEPFAKE"
        else:
            return "UNCERTAIN"

