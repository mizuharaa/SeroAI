"""
Evaluation script for deepfake detector.

Takes a directory of labeled videos and computes confusion matrix,
precision, recall, F1 score, and optionally saves CSV for offline analysis.
"""

import os
import sys
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detector_rule_based import SeroRuleBasedDetector
from core.types_analysis import VideoAnalysisResult


def load_labeled_videos(dataset_dir: str) -> List[Tuple[str, str]]:
    """
    Load labeled videos from directory structure.
    
    Expected structure:
    dataset_dir/
        real/
            video1.mp4
            video2.mp4
        fake/
            video1.mp4
            video2.mp4
    
    Or from a CSV file with columns: path, label
    
    Args:
        dataset_dir: Path to dataset directory
        
    Returns:
        List of (video_path, label) tuples
    """
    videos = []
    
    # Check if it's a CSV file
    if dataset_dir.endswith('.csv'):
        with open(dataset_dir, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                video_path = row.get('path', '')
                label = row.get('label', '').lower()
                if os.path.exists(video_path) and label in ['real', 'fake', 'authentic', 'deepfake']:
                    # Normalize labels
                    if label in ['real', 'authentic']:
                        label = 'authentic'
                    else:
                        label = 'deepfake'
                    videos.append((video_path, label))
        return videos
    
    # Otherwise, assume directory structure
    real_dir = os.path.join(dataset_dir, 'real')
    fake_dir = os.path.join(dataset_dir, 'fake')
    
    if os.path.exists(real_dir):
        for video_file in os.listdir(real_dir):
            if video_file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                videos.append((os.path.join(real_dir, video_file), 'authentic'))
    
    if os.path.exists(fake_dir):
        for video_file in os.listdir(fake_dir):
            if video_file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                videos.append((os.path.join(fake_dir, video_file), 'deepfake'))
    
    return videos


def evaluate_detector(
    detector: SeroRuleBasedDetector,
    videos: List[Tuple[str, str]],
    save_csv: bool = False,
    csv_path: str = "evaluation_results.csv"
) -> Dict[str, float]:
    """
    Evaluate detector on labeled videos.
    
    Args:
        detector: SeroRuleBasedDetector instance
        videos: List of (video_path, true_label) tuples
        save_csv: Whether to save detailed CSV
        csv_path: Path to save CSV file
        
    Returns:
        Dictionary with metrics: precision, recall, f1, accuracy
    """
    true_labels = []
    pred_labels = []
    pred_scores = []
    all_features = []
    
    print(f"Evaluating on {len(videos)} videos...")
    
    for i, (video_path, true_label) in enumerate(videos):
        print(f"Processing {i+1}/{len(videos)}: {os.path.basename(video_path)}")
        
        try:
            result = detector.analyze_video(video_path, enable_logging=False)
            
            true_labels.append(true_label)
            pred_labels.append(result.label)
            pred_scores.append(result.deepfake_score)
            all_features.append(result.features)
            
        except Exception as e:
            print(f"  Error processing {video_path}: {e}")
            # Skip this video
            continue
    
    # Compute confusion matrix
    tp = sum(1 for t, p in zip(true_labels, pred_labels) if t == 'deepfake' and p == 'deepfake')
    tn = sum(1 for t, p in zip(true_labels, pred_labels) if t == 'authentic' and p == 'authentic')
    fp = sum(1 for t, p in zip(true_labels, pred_labels) if t == 'authentic' and p == 'deepfake')
    fn = sum(1 for t, p in zip(true_labels, pred_labels) if t == 'deepfake' and p == 'authentic')
    
    # Compute metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(true_labels) if len(true_labels) > 0 else 0.0
    
    # Print results
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total videos: {len(true_labels)}")
    print(f"\nConfusion Matrix:")
    print(f"  True Positive (TP):  {tp}")
    print(f"  True Negative (TN):  {tn}")
    print(f"  False Positive (FP): {fp}")
    print(f"  False Negative (FN): {fn}")
    print(f"\nMetrics:")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print("=" * 60)
    
    # Save CSV if requested
    if save_csv:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            feature_names = list(all_features[0].keys()) if all_features else []
            header = ['video_path', 'true_label', 'pred_label', 'pred_score'] + feature_names
            writer.writerow(header)
            
            # Rows
            for i, (video_path, true_label) in enumerate(videos):
                if i < len(pred_labels):
                    row = [
                        video_path,
                        true_label,
                        pred_labels[i],
                        pred_scores[i]
                    ] + [all_features[i].get(name, 0.0) for name in feature_names]
                    writer.writerow(row)
        
        print(f"\nDetailed results saved to: {csv_path}")
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Evaluate deepfake detector')
    parser.add_argument(
        'dataset',
        type=str,
        help='Path to dataset directory (with real/ and fake/ subdirs) or CSV file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to feature_stats.json config file'
    )
    parser.add_argument(
        '--csv',
        type=str,
        default='evaluation_results.csv',
        help='Path to save detailed CSV results'
    )
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Do not save CSV file'
    )
    
    args = parser.parse_args()
    
    # Load videos
    videos = load_labeled_videos(args.dataset)
    if not videos:
        print(f"Error: No videos found in {args.dataset}")
        return
    
    # Initialize detector
    detector = SeroRuleBasedDetector(config_path=args.config)
    
    # Evaluate
    metrics = evaluate_detector(
        detector,
        videos,
        save_csv=not args.no_csv,
        csv_path=args.csv
    )
    
    print(f"\nEvaluation complete!")


if __name__ == '__main__':
    main()

