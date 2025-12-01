"""
Fusion module - Updated to use new 5-axis detection engine.

This module now wraps the new detection engine and provides compatibility
with the existing service interface.
"""

from typing import Dict
from core.detection_engine import DeepfakeDetectionEngine


class DeepfakeFusion:
    """Wrapper for the new 5-axis detection engine."""
    
    def __init__(self):
        """Initialize the detection engine."""
        self.engine = DeepfakeDetectionEngine()
        self.model = 'rule_based'  # For compatibility
        self.thresholds = None
        self.calibration = None
        self.metric_weights = {}
        self.use_interactions = False
        print("[fusion] Using new 5-axis detection engine (algorithmic only, no trained models).")
    
    def load_models(self):
        """No-op: models are disabled."""
        pass
    
    def predict(self, analysis_results: Dict) -> float:
        """
        Predict probability of AI generation.
        
        Note: This method is kept for compatibility but the actual analysis
        should be done through the detection engine's analyze() method.
        
        Args:
            analysis_results: Dictionary with analysis results (legacy format)
            
        Returns:
            Probability of AI generation (0-1)
        """
        # For backward compatibility, extract probability if available
        if 'deepfake_probability' in analysis_results:
            return float(analysis_results['deepfake_probability'])
        
        # Fallback: compute from individual scores if available
        motion = analysis_results.get('motion_score', 0.5)
        bio = analysis_results.get('bio_physics_score', 0.5)
        scene = analysis_results.get('scene_logic_score', 0.5)
        texture = analysis_results.get('texture_freq_score', 0.5)
        watermark = analysis_results.get('watermark_score', 0.0)
        
        prob = (
            motion * 0.50 +
            bio * 0.20 +
            scene * 0.15 +
            texture * 0.10 +
            watermark * 0.05
        )
        
        return float(prob)
    
    def get_verdict(self, prob_ai: float, quality_status: str) -> str:
        """
        Get final verdict based on probability.
        
        Args:
            prob_ai: Probability of AI generation
            quality_status: Quality status (unused in new system)
            
        Returns:
            Verdict: 'AI', 'REAL', or 'UNSURE'
        """
        if prob_ai >= 0.85:
            return 'AI'
        elif prob_ai <= 0.15:
            return 'REAL'
        else:
            return 'UNSURE'
        

def generate_reasons(analysis_results: Dict, prob_ai: float) -> list:
    """
    Generate human-readable reasons for the decision.
    
    Args:
        analysis_results: Dictionary with analysis results
        prob_ai: Probability of AI generation
        
    Returns:
        List of reason dictionaries
    """
    reasons = []
    
    # Extract scores from new format
    motion_score = analysis_results.get('motion_score', 0.5)
    bio_score = analysis_results.get('bio_physics_score', 0.5)
    scene_score = analysis_results.get('scene_logic_score', 0.5)
    texture_score = analysis_results.get('texture_freq_score', 0.5)
    watermark_score = analysis_results.get('watermark_score', 0.0)
    
    # Get explanations if available
    explanation = analysis_results.get('explanation', {})
    
    # Motion (weight: 0.50)
    reasons.append({
        'name': 'motion_temporal_stability',
        'weight': 0.50,
        'detail': explanation.get('motion', f"Motion score: {motion_score:.3f}"),
        'confidence': abs(motion_score - 0.5) * 2  # Distance from neutral
    })
    
    # Biological/Physics (weight: 0.20)
    reasons.append({
        'name': 'biological_physical_realism',
        'weight': 0.20,
        'detail': explanation.get('bio_physics', f"Biological score: {bio_score:.3f}"),
        'confidence': abs(bio_score - 0.5) * 2
    })
    
    # Scene Logic (weight: 0.15)
    reasons.append({
        'name': 'scene_lighting_logic',
        'weight': 0.15,
        'detail': explanation.get('scene_logic', f"Scene logic score: {scene_score:.3f}"),
        'confidence': abs(scene_score - 0.5) * 2
    })
    
    # Texture/Frequency (weight: 0.10)
    reasons.append({
        'name': 'texture_frequency_artifacts',
        'weight': 0.10,
        'detail': explanation.get('texture_freq', f"Texture score: {texture_score:.3f}"),
        'confidence': abs(texture_score - 0.5) * 2
    })
    
    # Watermark (weight: 0.05)
    if watermark_score > 0:
        reasons.append({
            'name': 'watermark_provenance',
            'weight': 0.05,
            'detail': explanation.get('watermark', f"Watermark detected: {watermark_score:.3f}"),
            'confidence': watermark_score
        })
    
    # Summary
    reasons.append({
        'name': 'final_decision',
        'weight': 1.0,
        'detail': explanation.get('summary', f"Final probability: {prob_ai:.3f}"),
        'confidence': abs(prob_ai - 0.5) * 2
    })
    
    return reasons
