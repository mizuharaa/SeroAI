"""Training script for ensemble classifier."""

import sys
import os
import argparse
import numpy as np
from typing import List, Tuple, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.feature_extractor import extract_all_features
from models.ensemble_classifier import EnsembleClassifier


def load_dataset(data_dir: str) -> List[Tuple[str, int]]:
    """
    Load dataset from directory structure.
    
    Expected structure:
    data_dir/
        real/
            video1.mp4
            video2.mp4
            ...
        fake/
            video1.mp4
            video2.mp4
            ...
    
    Returns:
        List of (video_path, label) tuples where label=0 for real, 1 for fake
    """
    dataset = []
    
    real_dir = os.path.join(data_dir, 'real')
    fake_dir = os.path.join(data_dir, 'fake')
    
    if os.path.exists(real_dir):
        for filename in os.listdir(real_dir):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(real_dir, filename)
                dataset.append((video_path, 0))
    
    if os.path.exists(fake_dir):
        for filename in os.listdir(fake_dir):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(fake_dir, filename)
                dataset.append((video_path, 1))
    
    return dataset


def extract_features_from_dataset(dataset: List[Tuple[str, int]], 
                                   max_samples: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract features from all videos in dataset.
    
    Args:
        dataset: List of (video_path, label) tuples
        max_samples: Maximum number of samples to process (None = all)
        
    Returns:
        Tuple of (features_matrix, labels_array)
    """
    features_list = []
    labels_list = []
    
    dataset_subset = dataset[:max_samples] if max_samples else dataset
    
    for i, (video_path, label) in enumerate(dataset_subset):
        print(f"Processing {i+1}/{len(dataset_subset)}: {os.path.basename(video_path)} (label={label})")
        
        try:
            features = extract_all_features(video_path, enable_hand_analysis=True)
            
            # Convert to vector (using feature names from classifier)
            classifier = EnsembleClassifier()
            feature_vector = classifier._features_to_vector(features)
            
            features_list.append(feature_vector)
            labels_list.append(label)
            
        except Exception as e:
            print(f"Error processing {video_path}: {e}")
            continue
    
    if len(features_list) == 0:
        raise ValueError("No features extracted from dataset")
    
    features_matrix = np.array(features_list)
    labels_array = np.array(labels_list)
    
    return features_matrix, labels_array


def main():
    parser = argparse.ArgumentParser(description='Train ensemble classifier')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Directory containing real/ and fake/ subdirectories')
    parser.add_argument('--model_path', type=str, default='models/ensemble_classifier.pkl',
                       help='Path to save trained model')
    parser.add_argument('--config_path', type=str, default='models/ensemble_config.json',
                       help='Path to save configuration')
    parser.add_argument('--model_type', type=str, default='logistic',
                       choices=['logistic', 'random_forest', 'gradient_boosting'],
                       help='Type of model to train')
    parser.add_argument('--max_samples', type=int, default=None,
                       help='Maximum number of samples to process')
    parser.add_argument('--test_size', type=float, default=0.2,
                       help='Fraction of data to use for testing')
    parser.add_argument('--calibrate', action='store_true',
                       help='Apply calibration to model')
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.data_dir}...")
    dataset = load_dataset(args.data_dir)
    print(f"Found {len(dataset)} videos ({sum(1 for _, l in dataset if l == 0)} real, {sum(1 for _, l in dataset if l == 1)} fake)")
    
    if len(dataset) == 0:
        print("Error: No videos found in dataset")
        return
    
    # Extract features
    print("\nExtracting features...")
    features, labels = extract_features_from_dataset(dataset, max_samples=args.max_samples)
    print(f"Extracted features from {len(features)} videos")
    print(f"Feature shape: {features.shape}")
    
    # Train classifier
    print("\nTraining classifier...")
    classifier = EnsembleClassifier(model_type=args.model_type, config_path=args.config_path)
    classifier.train(features, labels, test_size=args.test_size, calibrate=args.calibrate)
    
    # Save model and config
    os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
    classifier.save(args.model_path)
    classifier.save_config(args.config_path)
    
    print(f"\nModel saved to {args.model_path}")
    print(f"Config saved to {args.config_path}")


if __name__ == '__main__':
    main()

