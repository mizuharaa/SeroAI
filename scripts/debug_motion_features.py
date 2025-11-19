"""Debug script for motion features."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.motion_features import extract_motion_features


def main():
    parser = argparse.ArgumentParser(description='Debug motion features')
    parser.add_argument('--video', type=str, required=True,
                       help='Path to video file')
    parser.add_argument('--target_fps', type=float, default=12.0,
                       help='Target FPS for frame sampling')
    parser.add_argument('--max_frames', type=int, default=50,
                       help='Maximum number of frames to process')
    
    args = parser.parse_args()
    
    print(f"Extracting motion features from {args.video}...")
    print(f"Target FPS: {args.target_fps}, Max frames: {args.max_frames}\n")
    
    try:
        features = extract_motion_features(
            args.video,
            target_fps=args.target_fps,
            max_frames=args.max_frames
        )
        
        print("Motion Features:")
        print("=" * 50)
        for key, value in features.items():
            print(f"{key:30s}: {value:8.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

