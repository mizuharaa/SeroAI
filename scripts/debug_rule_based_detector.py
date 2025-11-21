"""Debug script for rule-based detector.

Tests the rule-based detector on a video and prints detailed
feature values and explanations.
"""

import sys
import os
import argparse
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detector_rule_based import SeroRuleBasedDetector


def print_features_by_category(features: Dict[str, float]):
    """Print features grouped by category."""
    categories = {
        'Watermark': ['watermark_detected', 'watermark_confidence', 'watermark_type', 
                     'watermark_persistence', 'watermark_corner_score'],
        'Human Presence': ['human_present', 'human_detection_frames', 'human_detection_fraction',
                          'face_detection_frames', 'person_detection_frames'],
        'Motion/Shimmer': ['shimmer_intensity', 'background_motion_inconsistency', 
                          'flat_region_noise_drift', 'constant_motion_ratio',
                          'avg_optical_flow_mag_face', 'std_optical_flow_mag_face',
                          'motion_entropy_face', 'flow_magnitude_mean', 'flow_magnitude_std'],
        'Temporal Identity': ['temporal_identity_std', 'head_pose_jitter'],
        'Anatomy': ['hand_missing_finger_ratio', 'hand_abnormal_angle_ratio',
                   'avg_hand_landmark_confidence', 'mouth_open_ratio_mean',
                   'mouth_open_ratio_std', 'extreme_mouth_open_frequency',
                   'lip_sync_smoothness', 'eye_blink_rate', 'eye_blink_irregularity'],
        'Frequency': ['high_freq_energy_face', 'low_freq_energy_face',
                     'freq_energy_ratio', 'boundary_artifact_score'],
        'Audio Sync': ['has_audio', 'lip_audio_correlation', 'avg_phoneme_lag',
                      'sync_consistency'],
    }
    
    for category, feature_names in categories.items():
        print(f"\n{category}:")
        print("-" * 60)
        found_any = False
        for name in feature_names:
            if name in features:
                value = features[name]
                print(f"  {name:40s}: {value:8.4f}")
                found_any = True
        if not found_any:
            print("  (no features found)")


def main():
    parser = argparse.ArgumentParser(description='Debug rule-based detector')
    parser.add_argument('--video', type=str, required=True,
                       help='Path to video file')
    parser.add_argument('--verbose', action='store_true',
                       help='Print all feature values')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        return
    
    print(f"Testing rule-based detector on: {args.video}")
    print("=" * 60)
    
    try:
        detector = SeroRuleBasedDetector()
        result = detector.detect(args.video)
        
        print("\n" + "=" * 60)
        print("=== DETECTION RESULT ===")
        print(f"Score: {result['score']:.4f}")
        print(f"Label: {result['label']}")
        
        print("\n=== EXPLANATIONS ===")
        explanations = result.get('explanations', [])
        if explanations:
            for i, exp in enumerate(explanations, 1):
                print(f"{i}. {exp}")
        else:
            print("(no explanations)")
        
        # Always print features (not just verbose)
        print("\n=== ALL FEATURES ===")
        features = result.get('features', {})
        print_features_by_category(features)
        
        # Print category scores if available in debug output
        print("\n" + "=" * 60)
        print("Analysis complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

