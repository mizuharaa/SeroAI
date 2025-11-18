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
        self.use_interactions = False  # Flag for interaction features
        self.load_models()
    
    def load_models(self):
        """Load pre-trained fusion model, calibration, and threshold config."""
        # Try to load improved model first (if available)
        improved_model_path = "models/fusion_improved.pkl"
        if os.path.exists(improved_model_path):
            try:
                if joblib is not None:
                    self.model = joblib.load(improved_model_path)
                    self.use_interactions = True  # Flag to create interaction features
                    print(f"[fusion] Loaded improved ensemble fusion model: {improved_model_path}")
                    # Try to load improved thresholds
                    improved_thresholds_path = "models/fusion_thresholds_improved.json"
                    if os.path.exists(improved_thresholds_path):
                        with open(improved_thresholds_path, 'r') as f:
                            self.thresholds = json.load(f)
                            print(f"[fusion] Loaded improved thresholds: AI={self.thresholds.get('ai_threshold_conservative', 0.85):.3f}")
                    return
            except Exception as e:  # pragma: no cover
                print(f"[fusion] Failed to load improved model ({e}); trying standard model...")
                self.use_interactions = False
        
        # Try to load standard trained model
        if os.path.exists(FUSION_MODEL_PATH):
            try:
                if joblib is not None:
                    self.model = joblib.load(FUSION_MODEL_PATH)
                    self.use_interactions = False
                    # One-line log so users can confirm the model is active
                    print(f"[fusion] Loaded supervised fusion model: {FUSION_MODEL_PATH}")
            except Exception as e:  # pragma: no cover
                print(f"[fusion] Failed to load supervised model ({e}); falling back to rule-based.")
                self.model = None
                self.use_interactions = False
        
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
        df = pd.DataFrame(data)
        
        # Create interaction features if using improved model
        if self.use_interactions:
            interactions = [
                ("forensics.flicker", "temp.flow_oddity"),
                ("art.edge", "art.texture"),
                ("face.mouth_exag", "face.eye_blink"),
                ("forensics.prnu", "quality.blur"),
                ("temp.rppg", "face.mouth_exag"),
            ]
            
            for feat1, feat2 in interactions:
                if feat1 in df.columns and feat2 in df.columns:
                    # Create interaction if both features are present
                    val1 = df[feat1].iloc[0]
                    val2 = df[feat2].iloc[0]
                    if pd.notna(val1) and pd.notna(val2):
                        df[f"{feat1}_x_{feat2}"] = [val1 * val2]
                    else:
                        df[f"{feat1}_x_{feat2}"] = [np.nan]
        
        return df
    
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
        # NOTE: Generator watermarks are now handled BEFORE model prediction in predict()
        # This section handles other hard evidence (scene logic, anatomy) but NOT watermarks
        # Watermarks are handled in predict() before model runs, so we skip watermark checks here
        wm = analysis_results.get('watermark', {}) or {}
        
        # Skip watermark checks here - already handled in predict()
        # Only check for other hard evidence (scene logic breaks, anatomy)
        has_generator_wm = False  # Watermarks already handled, don't check again
        has_wm = False  # Don't apply regular watermark boosts here
        
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
        # ========== CRITICAL: Check for hard AI evidence FIRST ==========
        # If we have a generator watermark (Sora, Runway, etc.), ALWAYS return high AI probability
        # This MUST happen before model prediction to prevent the model from overriding it
        # BUT: Must be strict to avoid false positives
        wm = analysis_results.get('watermark', {}) or {}
        
        # Only check if watermark is actually detected AND has valid data
        # Safeguard: Don't trigger on empty/default values
        if not wm.get('detected', False) or not wm:
            # No watermark detected, proceed with normal model prediction
            pass
        elif wm.get('watermark') is None and wm.get('text') is None and not wm.get('generator_hint', False):
            # Watermark "detected" but no actual text or hint - likely false positive
            # Proceed with normal model prediction
            pass
        else:
            # Watermark detected - check if it's a generator watermark
            # Use STRICT criteria to avoid false positives
            has_generator_wm = False
            wm_text = str(wm.get('watermark', '') or '').upper().strip()
            raw_text = str(wm.get('text', '') or '').upper().strip()
            
            # STRICT generator keywords - only actual generator names/brands
            # Removed generic terms like "STABLE", "DIFFUSION", "AI GENERATED" that cause false positives
            strict_generator_keywords = [
                'SORA', 'SORA AI', 'SORA.AI', 'SORA-AI',
                'RUNWAY', 'RUNWAYML', 'RUNWAY ML', 'GEN-2', 'GEN-3',
                'VEO', 'IMAGEN',
                'MIDJOURNEY',
                'PIKA', 'SYNTHESIA', 'D-ID', 'HEYGEN',
                'DALL-E', 'DALLE'
            ]
            
            # Check 1: generator_hint flag MUST be True AND confidence must be high
            # This is the most reliable indicator
            # CRITICAL: Also verify text is not empty and matches a generator keyword
            if wm.get('generator_hint', False):
                conf = wm.get('confidence', 0.0)
                # Require high confidence (0.75+) AND persistence for generator_hint
                if conf >= 0.75 and wm.get('persistent', False):
                    # Also verify the text matches a generator keyword (MUST have text)
                    check_text = wm_text or raw_text
                    if check_text and len(check_text.strip()) > 0:
                        for keyword in strict_generator_keywords:
                            if keyword in check_text:
                                has_generator_wm = True
                                print(f"[fusion] Generator watermark confirmed: '{check_text}' (generator_hint=True, conf={conf:.2f}, persistent=True)")
                                break
                    else:
                        # generator_hint is True but no text - likely false positive, skip
                        print(f"[fusion] WARNING: generator_hint=True but no watermark text found. Skipping to avoid false positive.")
            
            # Check 2: If generator_hint is True but confidence is lower, require:
            # - High confidence (≥0.8) OR
            # - Persistent + corner + confidence ≥0.7
            if not has_generator_wm and wm.get('generator_hint', False):
                conf = wm.get('confidence', 0.0)
                is_persistent = wm.get('persistent', False)
                is_corner = wm.get('corner', False)
                
                if conf >= 0.8:
                    # Very high confidence, trust it
                    check_text = wm_text or raw_text
                    if check_text:
                        for keyword in strict_generator_keywords:
                            if keyword in check_text:
                                has_generator_wm = True
                                print(f"[fusion] Generator watermark confirmed: '{check_text}' (high confidence={conf:.2f})")
                                break
                elif is_persistent and is_corner and conf >= 0.7:
                    # Persistent corner watermark with decent confidence
                    check_text = wm_text or raw_text
                    if check_text:
                        for keyword in strict_generator_keywords:
                            if keyword in check_text:
                                has_generator_wm = True
                                print(f"[fusion] Generator watermark confirmed: '{check_text}' (persistent corner, conf={conf:.2f})")
                                break
            
            # Check 3: Even without generator_hint, if we have very high confidence persistent watermark
            # with matching text, trust it (but require higher confidence)
            if not has_generator_wm:
                conf = wm.get('confidence', 0.0)
                is_persistent = wm.get('persistent', False)
                is_corner = wm.get('corner', False)
                
                if is_persistent and is_corner and conf >= 0.85:
                    # Very high confidence persistent corner watermark
                    check_text = wm_text or raw_text
                    if check_text:
                        for keyword in strict_generator_keywords:
                            if keyword in check_text:
                                has_generator_wm = True
                                print(f"[fusion] Generator watermark confirmed: '{check_text}' (very high confidence persistent corner, conf={conf:.2f})")
                                break
            
            # If we have a confirmed generator watermark, IMMEDIATELY return high AI probability
            # FINAL SAFEGUARD: Only trigger if we have confirmed text match or very high confidence
            if has_generator_wm:
                # Double-check: ensure we have either matching text OR very high confidence with generator_hint
                final_check = False
                if wm_text or raw_text:
                    # We have text that matched a keyword - this is definitive
                    final_check = True
                elif wm.get('generator_hint', False) and wm.get('confidence', 0.0) >= 0.85:
                    # Very high confidence generator_hint without text - still trust it
                    final_check = True
                
                if final_check:
                    prob = DECISION["HARD_AI_MIN_PROB"]  # 0.95 minimum
                    analysis_results['_hard_ai_evidence'] = {
                        'applied': True,
                        'details': [f"Generator watermark confirmed: {wm_text or raw_text or 'via generator_hint'}"],
                        'min_prob_enforced': DECISION["HARD_AI_MIN_PROB"],
                        'source': 'watermark_override',
                        'watermark_text': wm_text or raw_text,
                        'confidence': wm.get('confidence', 0.0),
                        'generator_hint': wm.get('generator_hint', False),
                        'persistent': wm.get('persistent', False),
                        'corner': wm.get('corner', False)
                    }
                    print(f"[fusion] HARD AI EVIDENCE: Generator watermark confirmed. Overriding model prediction with prob={prob:.3f}")
                    # Skip all other processing - watermark is definitive
                    return prob
                else:
                    # Has generator_wm flag but failed final check - likely false positive
                    print(f"[fusion] WARNING: Potential generator watermark but failed final validation. Proceeding with normal prediction.")
        
        # No generator watermark detected - proceed with normal model prediction
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
                # Debug: Log model prediction
                if prob > 0.9:
                    print(f"[fusion] Model predicted high AI probability: {prob:.3f} (checking for false positive)")
        
        # Apply calibration if available
        if self.calibration:
            # Temperature scaling
            temp = self.calibration.get('temperature', 1.0)
            eps = 1e-6
            p = float(np.clip(prob, eps, 1.0 - eps))
            logit = np.log(p / (1.0 - p))
            prob = 1.0 / (1.0 + np.exp(-logit / max(temp, eps)))
        
        # Hard-evidence overrides (logit boosts) - but watermark already handled above
        prob = self._apply_hard_evidence_boosts(prob, analysis_results)

        # Check if hard AI evidence was applied (watermark override or other hard evidence)
        has_hard_ai = analysis_results.get('_hard_ai_evidence', {}).get('applied', False)
        
        # If watermark was detected and overridden, skip all other rules
        if has_hard_ai and analysis_results.get('_hard_ai_evidence', {}).get('source') == 'watermark_override':
            return prob  # Already set to HARD_AI_MIN_PROB (0.95)
        
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

