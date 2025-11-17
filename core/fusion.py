"""Fusion model for combining multiple detection signals."""

import numpy as np
from typing import Dict, List
import json
import os
import math

# Pandas is only needed when a trained model is present
try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore
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


class DeepfakeFusion:
    """Fusion model for deepfake detection."""
    
    def __init__(self):
        self.model = None
        self.calibration = None
        self.thresholds = None  # Conservative threshold config
        self.metric_weights = get_metric_weights()
        self.load_models()
    
    def load_models(self):
        """Load pre-trained fusion model, calibration, and threshold config."""
        # Try to load trained model
        if os.path.exists(FUSION_MODEL_PATH):
            try:
                if joblib is not None:
                    self.model = joblib.load(FUSION_MODEL_PATH)
                    # One-line log so users can confirm the model is active
                    print(f"[fusion] Loaded supervised fusion model: {FUSION_MODEL_PATH}")
            except Exception as e:  # pragma: no cover
                print(f"[fusion] Failed to load supervised model ({e}); falling back to rule-based.")
                self.model = None
        
        # Try to load calibration
        if os.path.exists(CALIBRATION_PATH):
            try:
                with open(CALIBRATION_PATH, 'r') as f:
                    self.calibration = json.load(f)
            except Exception:  # pragma: no cover
                self.calibration = None
        
        # Try to load conservative thresholds
        thresholds_path = "models/fusion_thresholds.json"
        if os.path.exists(thresholds_path):
            try:
                with open(thresholds_path, 'r') as f:
                    self.thresholds = json.load(f)
                    print(f"[fusion] Loaded conservative thresholds: AI={self.thresholds.get('ai_threshold_conservative', 0.85):.3f}")
            except Exception:  # pragma: no cover
                self.thresholds = None
        
        # If no model loaded, use default rule-based fusion
        if self.model is None:
            self.model = 'rule_based'
            print("[fusion] No trained fusion model found; using rule-based fusion.")
    
    # Columns used by the supervised fusion model (must match training)
    TRAIN_FEATURE_COLUMNS: List[str] = [
        "quality.blur", "quality.brisque", "quality.bitrate", "quality.shake",
        "wm.detected",
        "forensics.prnu", "forensics.flicker", "forensics.codec",
        "face.mouth_exag", "face.mouth_static", "face.eye_blink", "face.sym_drift",
        "art.edge", "art.texture", "art.color", "art.freq",
        "temp.flow_oddity", "temp.rppg",
    ]

    def _to_float(self, value) -> float:
        """Convert value to float; return NaN when not numeric."""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            # Some booleans may sneak in; treat as 1.0/0.0
            if isinstance(value, bool):
                return 1.0 if value else 0.0
        except Exception:
            pass
        return float("nan")
    
    def _get_artifact_scale(self, flow_oddity: float) -> float:
        """
        Get artifact down-weighting scale based on optical flow oddity.
        
        When motion is smooth and natural (low flow_oddity), we trust that signal
        over artifact/frequency heuristics, which can false-positive on compressed
        or edited real content (talk shows, sports with overlays, etc.).
        
        Args:
            flow_oddity: Optical flow oddity score [0-1]
        
        Returns:
            Scale factor for artifact features [0.2-1.0]
        """
        if flow_oddity <= 0.15:
            return 0.2  # 80% reduction for very smooth motion
        elif flow_oddity <= 0.25:
            return 0.4  # 60% reduction for smooth motion
        elif flow_oddity <= 0.35:
            return 0.7  # 30% reduction for moderately smooth motion
        else:
            return 1.0  # No reduction for irregular motion

    def _extract_features_row(self, analysis_results: Dict) -> Dict[str, float]:
        """Extract a single-row dict matching TRAIN_FEATURE_COLUMNS."""
        quality = analysis_results.get("quality", {}) or {}
        watermark = analysis_results.get("watermark", {}) or {}
        forensics = analysis_results.get("forensics", {}) or {}
        artifacts = analysis_results.get("artifact_analysis", {}) or {}
        face_dyn = analysis_results.get("face_dynamics", {}) or {}
        temporal = (analysis_results.get("temporal", {}) or {})
        flow = (temporal.get("flow", {}) or {})
        rppg = (temporal.get("rppg", {}) or {})

        row: Dict[str, float] = {
            "quality.blur": self._to_float(quality.get("blur")),
            "quality.brisque": self._to_float(quality.get("brisque")),
            "quality.bitrate": self._to_float(quality.get("bitrate")),
            "quality.shake": self._to_float(quality.get("shake")),
            "wm.detected": 1.0 if watermark.get("detected") else 0.0,
            "forensics.prnu": self._to_float(forensics.get("prnu_score")),
            "forensics.flicker": self._to_float(forensics.get("flicker_score")),
            "forensics.codec": self._to_float(forensics.get("codec_score")),
            "face.mouth_exag": self._to_float(face_dyn.get("mouth_exaggeration_score")),
            "face.mouth_static": self._to_float(face_dyn.get("mouth_static_score")),
            "face.eye_blink": self._to_float(face_dyn.get("eye_blink_anomaly")),
            "face.sym_drift": self._to_float(face_dyn.get("face_symmetry_drift")),
            "art.edge": self._to_float(artifacts.get("edge_artifact_score")),
            "art.texture": self._to_float(artifacts.get("texture_inconsistency")),
            "art.color": self._to_float(artifacts.get("color_anomaly_score")),
            "art.freq": self._to_float(artifacts.get("freq_artifact_score")),
            "temp.flow_oddity": self._to_float(flow.get("oddity_score")),
            "temp.rppg": self._to_float(rppg.get("rppg_score")),
        }
        return row

    def extract_features_df(self, analysis_results: Dict):
        """Return a pandas DataFrame with one row and named columns for the model."""
        # If pandas unavailable (very minimal env), fall back to rule-based
        if pd is None:  # pragma: no cover
            return None
        row = self._extract_features_row(analysis_results)
        # Ensure column order matches training
        data = {col: [row.get(col)] for col in self.TRAIN_FEATURE_COLUMNS}
        return pd.DataFrame(data)
    
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
        
        # Get flow oddity early for forensics scaling
        temporal = analysis_results.get('temporal', {}) or {}
        flow = (temporal.get('flow', {}) or {})
        oddity = float(flow.get('oddity_score', 0.5))
        forensics_scale = self._get_artifact_scale(oddity) if oddity <= 0.30 else 1.0
        
        # PRNU: lower = more likely AI (don't scale - this is a strong real signal)
        scores.append(1.0 - prnu)
        weights.append(weighted('forensics_prnu', 0.2))
        
        # Flicker: higher = more likely AI (scale down for smooth motion)
        scores.append(flicker)
        weights.append(weighted('forensics_flicker', 0.18 * forensics_scale))
        
        # Codec: higher = more likely AI (scale down for smooth motion)
        scores.append(codec)
        weights.append(weighted('forensics_codec', 0.15 * forensics_scale))
        
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
        freq_score = artifacts.get('freq_artifact_score', 0.5)

        # Smooth artifact down-weighting based on optical flow oddity (already extracted above)
        # When motion is natural, artifact heuristics often false-positive on compression/overlays
        artifact_scale = self._get_artifact_scale(oddity)

        scores.append(edge_score)
        weights.append(weighted('edge_artifacts', 0.16 * artifact_scale))
        scores.append(texture_score)
        weights.append(weighted('texture_inconsistency', 0.14 * artifact_scale))
        scores.append(color_score)
        weights.append(weighted('color_anomaly', 0.1 * artifact_scale))
        scores.append(freq_score)
        weights.append(weighted('freq_artifacts', 0.14 * artifact_scale))

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
            # Down-weight fragile features slightly if quality is low
            # Reduced from 0.7 to 0.85 (more lenient - quality matters less)
            weights = [w * 0.85 for w in weights]
        
        # Weighted average
        if weights:
            prob_ai = np.average(scores, weights=weights)
        else:
            prob_ai = 0.5
        
        return float(np.clip(prob_ai, 0.0, 1.0))
    
    def _apply_hard_evidence_boosts(self, prob_ai: float, analysis_results: Dict) -> float:
        """
        Apply logit-space boosts for hard evidence and real-evidence calming.
        
        This is the critical function for reducing false positives on normal content.
        """
        def to_logit(p: float) -> float:
            p = float(np.clip(p, 1e-6, 1.0 - 1e-6))
            return float(np.log(p / (1.0 - p)))
        def to_prob(z: float) -> float:
            return float(1.0 / (1.0 + math.exp(-z)))
        
        z = to_logit(prob_ai)
        
        # ========== REAL-EVIDENCE CALMING (counter false positives) ==========
        # Apply logit adjustments for strong real-world signals
        real_evidence_count = 0
        real_evidence_details = []
        
        try:
            forensics = analysis_results.get('forensics', {}) or {}
            av = analysis_results.get('av_analysis', {}) or {}
            temporal = (analysis_results.get('temporal', {}) or {})
            flow = (temporal.get('flow', {}) or {})
            rppg = (temporal.get('rppg', {}) or {})
            scene_logic = analysis_results.get('scene_logic', {}) or {}
            quality = analysis_results.get('quality', {}) or {}

            prnu = float(forensics.get('prnu_score', 0.5))
            sync = float(av.get('sync_score', 0.5))
            rppg_score = float(rppg.get('rppg_score', 0.5))
            oddity = float(flow.get('oddity_score', 0.5))
            incoh = float(scene_logic.get('incoherence_score', 0.5))
            qual_status = quality.get('status', 'unknown')  # Don't default to 'high'

            # Strong sensor pattern → likely real camera
            # Relaxed back to 0.70 - too strict at 0.75
            if prnu >= 0.70:
                z -= 0.6  # Reduced from 0.8 - less aggressive
                real_evidence_count += 1
                real_evidence_details.append('strong_prnu')
            
            # Good A/V sync → real
            # Relaxed back to 0.80 - too strict at 0.90
            if sync >= 0.80:
                z -= 0.3  # Reduced from 0.5 - less aggressive
                real_evidence_count += 1
                real_evidence_details.append('good_sync')
            
            # Strong physiological coherence (clear pulse) → real
            # Relaxed to 0.25 - too strict at 0.20
            if rppg_score <= 0.25:
                z -= 0.3  # Reduced from 0.5 - less aggressive
                real_evidence_count += 1
                real_evidence_details.append('strong_rppg')
            
            # Smooth camera motion → real
            # Relaxed to 0.20 - too strict at 0.15
            if oddity <= 0.20:
                z -= 0.3  # Reduced from 0.4 - less aggressive
                real_evidence_count += 1
                real_evidence_details.append('smooth_motion')
            
            # Scene consistent → gentle calm
            # Relaxed to 0.35 - too strict at 0.30
            if incoh <= 0.35 and not scene_logic.get('flag'):
                z -= 0.15  # Reduced from 0.2 - less aggressive
                real_evidence_count += 1
                real_evidence_details.append('scene_coherent')
            
            # Don't count quality as evidence - it's not a deepfake signal
        
        except Exception:
            pass

        # ========== HARD AI EVIDENCE (boosts AI probability) ==========
        wm = analysis_results.get('watermark', {})
        has_wm = bool(wm.get('detected') and wm.get('confidence', 0.0) >= 0.8)
        
        # NEW: Check for AI generator watermark (Sora, Runway, etc.)
        has_generator_wm = bool(
            wm.get('generator_hint', False) and
            wm.get('confidence', 0.0) >= 0.8 and
            wm.get('persistent', False)
        )
        
        scene_logic = analysis_results.get('scene_logic', {})
        has_logic_break = bool(scene_logic.get('flag') and scene_logic.get('confidence', 0.0) >= 0.8)
        
        # Strong logic break (very high incoherence)
        has_strong_logic_break = bool(
            scene_logic.get('flag') and
            scene_logic.get('incoherence_score', 0.0) >= 0.8 and
            scene_logic.get('confidence', 0.0) >= 0.8
        )
        
        face_dyn = analysis_results.get('face_dynamics', {})
        anatomy_max = max(
            face_dyn.get('mouth_exaggeration_score', 0.0),
            face_dyn.get('mouth_static_score', 0.0),
            face_dyn.get('eye_blink_anomaly', 0.0),
            face_dyn.get('face_symmetry_drift', 0.0),
        )
        has_anatomy = bool(anatomy_max >= 0.90)
        
        # Apply logit boosts
        if has_generator_wm:
            # STRONG boost for AI generator watermarks
            z += DECISION["WATERMARK_GENERATOR_LOGIT_BONUS"]
        elif has_wm:
            # Regular watermark boost
            z += DECISION["WATERMARK_LOGIT_BONUS"]
        
        if has_strong_logic_break:
            # Strong scene logic break
            z += DECISION["LOGIC_BREAK_STRONG_LOGIT_BONUS"]
        elif has_logic_break:
            # Regular logic break
            z += DECISION["LOGIC_BREAK_LOGIT_BONUS"]
        
        if has_anatomy:
            z += DECISION["ANATOMY_LOGIT_BONUS"]
        
        # Convert back to probability
        prob_after_boosts = to_prob(z)
        
        # Track hard AI evidence for later use
        hard_ai_evidence = has_generator_wm or has_strong_logic_break
        hard_ai_details = []
        if has_generator_wm:
            hard_ai_details.append(f"AI generator watermark: {wm.get('watermark', 'UNKNOWN')}")
        if has_strong_logic_break:
            hard_ai_details.append(f"Strong scene logic break (incoherence={scene_logic.get('incoherence_score', 0):.2f})")
        
        # ========== HARD AI EVIDENCE ENFORCEMENT ==========
        # When we have hard AI evidence (generator watermark or strong logic break),
        # enforce minimum AI probability and cap real probability
        if hard_ai_evidence:
            # Enforce minimum AI probability
            prob_after_boosts = max(prob_after_boosts, DECISION["HARD_AI_MIN_PROB"])
            
            # Store hard AI evidence info for explanation
            analysis_results['_hard_ai_evidence'] = {
                'applied': True,
                'details': hard_ai_details,
                'min_prob_enforced': DECISION["HARD_AI_MIN_PROB"],
            }
            
            # Skip real-evidence override when hard AI evidence present
            return prob_after_boosts
        
        # ========== REAL-EVIDENCE OVERRIDE ==========
        # ONLY trigger if we have VERY strong real evidence (≥4 criteria) 
        # AND the probability is suspiciously high (>0.75)
        # AND there's NO hard AI evidence
        
        # Only apply override if:
        # 1. We have 4+ strong real signals (very rare)
        # 2. Model is predicting high AI probability (>0.75)
        # 3. No hard AI evidence
        if real_evidence_count >= 4 and prob_after_boosts > 0.75:
            # Conservative cap to prevent false positives on heavily compressed real content
            override_cap = 0.65
            # Store override info for explanation layer
            analysis_results['_real_evidence_override'] = {
                'applied': True,
                'count': real_evidence_count,
                'details': real_evidence_details,
                'original_prob': prob_after_boosts,
                'capped_prob': override_cap
            }
            return override_cap
        
        return prob_after_boosts
    
    def predict(self, analysis_results: Dict) -> float:
        """Predict probability of AI generation.
        
        Args:
            analysis_results: Dictionary with all analysis results
            
        Returns:
            Calibrated probability of AI generation
        """
        # Refresh adaptive weights in case new feedback has arrived
        self.metric_weights = get_metric_weights()
        if isinstance(self.model, str) or self.model is None:
            prob = self.fuse_rule_based(analysis_results)
        else:
            # Use trained model
            df = self.extract_features_df(analysis_results)
            if df is None:  # Safety: pandas missing → fallback
                prob = self.fuse_rule_based(analysis_results)
            else:
                prob = float(self.model.predict_proba(df)[0, 1])
        
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

        # Check if hard AI evidence was applied
        has_hard_ai = analysis_results.get('_hard_ai_evidence', {}).get('applied', False)
        
        # Independence rule: require two strong independent branches to exceed 0.90
        # SKIP this rule if hard AI evidence present
        if not has_hard_ai:
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
            # SKIP this cap if hard AI evidence present
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
    
    # ========== HARD AI EVIDENCE (highest priority - shows AI generator detection) ==========
    hard_ai_info = analysis_results.get('_hard_ai_evidence', {})
    if hard_ai_info.get('applied'):
        details_str = '; '.join(hard_ai_info.get('details', []))
        reasons.append({
            'name': 'hard_ai_evidence',
            'weight': 1.0,
            'detail': f"🚨 HARD AI EVIDENCE DETECTED: {details_str} → enforcing minimum AI probability ({hard_ai_info.get('min_prob_enforced', 0.95):.0%})",
            'confidence': 0.98
        })
    
    # ========== REAL-EVIDENCE OVERRIDE (only applies when NO hard AI evidence) ==========
    override_info = analysis_results.get('_real_evidence_override', {})
    if override_info.get('applied'):
        details_str = ', '.join(override_info.get('details', []))
        reasons.append({
            'name': 'real_evidence_override',
            'weight': 1.0,
            'detail': f"Multiple strong real-world cues detected ({details_str}) → lowering AI probability to avoid false positives on normal footage",
            'confidence': 0.95
        })
    
    # ========== ARTIFACT DOWN-WEIGHTING (explain when applied) ==========
    temporal = analysis_results.get('temporal', {}) or {}
    flow = temporal.get('flow', {}) or {}
    oddity = float(flow.get('oddity_score', 0.5))
    if oddity <= 0.30:
        scale = 0.2 if oddity <= 0.15 else (0.4 if oddity <= 0.25 else 0.7)
        reasons.append({
            'name': 'artifact_downweight',
            'weight': 0.5,
            'detail': f"Smooth natural motion detected (oddity={oddity:.2f}) → artifact/frequency heuristics down-weighted by {int((1-scale)*100)}% to avoid false positives",
            'confidence': 0.85
        })
    
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

