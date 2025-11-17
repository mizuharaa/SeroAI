"""
Debug inference mode for detailed per-branch analysis.

Usage:
    python -m core.debug_infer --input path/to/video.mp4 --out data/debug/video_debug.json
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.service import analyze_media
from core.fusion import DeepfakeFusion


def safe_float(value: Any) -> float:
    """Convert value to float, return 0.0 if not possible."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def debug_inference(video_path: str) -> Dict:
    """
    Run inference with detailed debug output.
    
    Returns dict with:
        - raw_features: All extracted features
        - branch_contributions: Per-branch logit contributions
        - fusion_details: Before/after probabilities, overrides
        - final_decision: Verdict and reasons
    """
    print(f"Analyzing: {video_path}")
    
    # Run full analysis
    result = analyze_media(video_path)
    
    # Extract raw features
    quality = result.get('quality', {}) or {}
    watermark = result.get('watermark', {}) or {}
    forensics = result.get('forensics', {}) or {}
    face_analysis = result.get('face_analysis', {}) or {}
    face_dynamics = result.get('face_dynamics', {}) or {}
    artifacts = result.get('artifact_analysis', {}) or {}
    temporal = result.get('temporal', {}) or {}
    flow = temporal.get('flow', {}) or {}
    rppg = temporal.get('rppg', {}) or {}
    scene_logic = result.get('scene_logic', {}) or {}
    av_analysis = result.get('av_analysis', {}) or {}
    
    raw_features = {
        # Quality
        'quality.blur': safe_float(quality.get('blur')),
        'quality.brisque': safe_float(quality.get('brisque')),
        'quality.bitrate': safe_float(quality.get('bitrate')),
        'quality.shake': safe_float(quality.get('shake')),
        'quality.status': quality.get('status', 'unknown'),
        
        # Watermark
        'wm.detected': bool(watermark.get('detected')),
        'wm.confidence': safe_float(watermark.get('confidence')),
        'wm.label': watermark.get('watermark', ''),
        'wm.persistent': bool(watermark.get('persistent')),
        'wm.corner': bool(watermark.get('corner')),
        'wm.generator_hint': bool(watermark.get('generator_hint', False)),
        
        # Forensics
        'forensics.prnu': safe_float(forensics.get('prnu_score')),
        'forensics.flicker': safe_float(forensics.get('flicker_score')),
        'forensics.codec': safe_float(forensics.get('codec_score')),
        
        # Face
        'face.detected': bool(face_analysis.get('face_detected')),
        'face.num_faces': int(face_analysis.get('num_faces', 0)),
        'face.mouth_exag': safe_float(face_dynamics.get('mouth_exaggeration_score')),
        'face.mouth_static': safe_float(face_dynamics.get('mouth_static_score')),
        'face.eye_blink': safe_float(face_dynamics.get('eye_blink_anomaly')),
        'face.sym_drift': safe_float(face_dynamics.get('face_symmetry_drift')),
        
        # Artifacts
        'art.edge': safe_float(artifacts.get('edge_artifact_score')),
        'art.texture': safe_float(artifacts.get('texture_inconsistency')),
        'art.color': safe_float(artifacts.get('color_anomaly_score')),
        'art.freq': safe_float(artifacts.get('freq_artifact_score')),
        
        # Temporal
        'temp.flow_oddity': safe_float(flow.get('oddity_score')),
        'temp.rppg': safe_float(rppg.get('rppg_score')),
        
        # Scene logic
        'scene.incoherence_score': safe_float(scene_logic.get('incoherence_score')),
        'scene.flag': bool(scene_logic.get('flag')),
        'scene.confidence': safe_float(scene_logic.get('confidence')),
        'scene.reasons': scene_logic.get('reasons', []),
        
        # A/V sync
        'av.sync_score': safe_float(av_analysis.get('sync_score')),
        'av.has_audio': bool(av_analysis.get('has_audio')),
    }
    
    # Compute branch contributions (approximate from rule-based fusion)
    branch_contributions = compute_branch_contributions(raw_features)
    
    # Get fusion details
    fusion = DeepfakeFusion()
    prob_ai = result.get('prob_ai', 0.5)
    
    # Check for overrides
    override_info = result.get('_real_evidence_override', {})
    hard_ai_info = result.get('_hard_ai_evidence', {})
    
    fusion_details = {
        'prob_ai_final': float(prob_ai),
        'verdict': result.get('verdict', 'UNKNOWN'),
        'real_evidence_override': override_info,
        'hard_ai_evidence': hard_ai_info,
        'reasons': result.get('reasons', []),
    }
    
    debug_output = {
        'video_path': video_path,
        'raw_features': raw_features,
        'branch_contributions': branch_contributions,
        'fusion_details': fusion_details,
        'full_result': {
            'verdict': result.get('verdict'),
            'prob_ai': result.get('prob_ai'),
            'processing_time': result.get('debug', {}).get('processing_time', 0),
        }
    }
    
    return debug_output


def compute_branch_contributions(features: Dict) -> Dict:
    """
    Approximate per-branch contributions to AI probability.
    
    Returns dict with estimated logit contributions.
    """
    contributions = {}
    
    # Watermark (strong signal)
    if features['wm.detected']:
        wm_logit = 2.0 * features['wm.confidence']
        if features['wm.generator_hint']:
            wm_logit += 3.0  # Strong boost for generator watermarks
        contributions['watermark'] = {
            'logit_contribution': wm_logit,
            'confidence': features['wm.confidence'],
            'generator_hint': features['wm.generator_hint']
        }
    else:
        contributions['watermark'] = {'logit_contribution': 0.0}
    
    # Forensics
    prnu_contrib = -0.8 if features['forensics.prnu'] >= 0.75 else 0.0
    flicker_contrib = 0.18 * features['forensics.flicker']
    codec_contrib = 0.15 * features['forensics.codec']
    contributions['forensics'] = {
        'prnu_logit': prnu_contrib,
        'flicker_logit': flicker_contrib,
        'codec_logit': codec_contrib,
        'total_logit': prnu_contrib + flicker_contrib + codec_contrib
    }
    
    # Artifacts
    edge_contrib = 0.16 * features['art.edge']
    texture_contrib = 0.14 * features['art.texture']
    color_contrib = 0.10 * features['art.color']
    freq_contrib = 0.14 * features['art.freq']
    contributions['artifacts'] = {
        'edge_logit': edge_contrib,
        'texture_logit': texture_contrib,
        'color_logit': color_contrib,
        'freq_logit': freq_contrib,
        'total_logit': edge_contrib + texture_contrib + color_contrib + freq_contrib
    }
    
    # Temporal
    flow_contrib = -0.4 if features['temp.flow_oddity'] <= 0.15 else 0.0
    rppg_contrib = -0.5 if features['temp.rppg'] <= 0.20 else 0.0
    contributions['temporal'] = {
        'flow_logit': flow_contrib,
        'rppg_logit': rppg_contrib,
        'total_logit': flow_contrib + rppg_contrib
    }
    
    # Scene logic
    if features['scene.flag'] and features['scene.confidence'] >= 0.8:
        scene_logit = 2.5
    else:
        scene_logit = 0.0
    contributions['scene_logic'] = {
        'logit_contribution': scene_logit,
        'flag': features['scene.flag'],
        'confidence': features['scene.confidence']
    }
    
    # A/V sync
    sync_contrib = -0.5 if features['av.sync_score'] >= 0.90 else 0.0
    contributions['av_sync'] = {
        'logit_contribution': sync_contrib
    }
    
    # Face dynamics
    face_max = max(
        features['face.mouth_exag'],
        features['face.mouth_static'],
        features['face.eye_blink'],
        features['face.sym_drift']
    )
    if face_max >= 0.90:
        face_logit = 1.5
    else:
        face_logit = 0.0
    contributions['face_dynamics'] = {
        'logit_contribution': face_logit,
        'max_anomaly': face_max
    }
    
    return contributions


def main():
    parser = argparse.ArgumentParser(description="Debug inference mode")
    parser.add_argument('--input', required=True, help="Path to video file")
    parser.add_argument('--out', required=True, help="Output JSON path")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)
    
    # Run debug inference
    debug_output = debug_inference(args.input)
    
    # Save to JSON
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(debug_output, f, indent=2)
    
    print(f"\n✓ Debug output saved to: {args.out}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    features = debug_output['raw_features']
    fusion = debug_output['fusion_details']
    
    print(f"\nVerdict: {fusion['verdict']}")
    print(f"AI Probability: {fusion['prob_ai_final']:.3f}")
    
    print("\n--- Key Features ---")
    print(f"Watermark: detected={features['wm.detected']}, "
          f"generator_hint={features['wm.generator_hint']}, "
          f"confidence={features['wm.confidence']:.2f}, "
          f"label='{features['wm.label']}'")
    print(f"Scene Logic: flag={features['scene.flag']}, "
          f"incoherence={features['scene.incoherence_score']:.2f}, "
          f"confidence={features['scene.confidence']:.2f}")
    print(f"Forensics: prnu={features['forensics.prnu']:.2f}, "
          f"flicker={features['forensics.flicker']:.2f}, "
          f"codec={features['forensics.codec']:.2f}")
    print(f"Temporal: flow_oddity={features['temp.flow_oddity']:.2f}, "
          f"rppg={features['temp.rppg']:.2f}")
    
    print("\n--- Top Reasons ---")
    for i, reason in enumerate(fusion['reasons'][:5], 1):
        print(f"{i}. {reason.get('name')}: {reason.get('detail')}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

