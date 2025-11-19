"""Debug script for anatomy features."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.anatomy_features import extract_anatomy_features


def main():
    parser = argparse.ArgumentParser(description='Debug anatomy features')
    parser.add_argument('--video', type=str, required=True,
                       help='Path to video file')
    parser.add_argument('--target_fps', type=float, default=8.0,
                       help='Target FPS for frame sampling')
    parser.add_argument('--max_frames', type=int, default=30,
                       help='Maximum number of frames to process')
    parser.add_argument('--no-hands', action='store_true',
                       help='Disable hand analysis')
    
    args = parser.parse_args()
    
    print(f"Extracting anatomy features from {args.video}...")
    print(f"Target FPS: {args.target_fps}, Max frames: {args.max_frames}")
    print(f"Hand analysis: {'disabled' if args.no_hands else 'enabled'}\n")
    
    try:
        features = extract_anatomy_features(
            args.video,
            target_fps=args.target_fps,
            max_frames=args.max_frames,
            enable_hand_analysis=not args.no_hands
        )
        
        print("Anatomy Features:")
        print("=" * 50)
        for key, value in features.items():
            print(f"{key:30s}: {value:8.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

