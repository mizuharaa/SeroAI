"""Evaluation script for ensemble classifier on a dataset."""

import sys
import os
import argparse
import csv
from typing import List, Tuple, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.feature_extractor import extract_all_features
from models.ensemble_classifier import EnsembleClassifier


def load_dataset(data_dir: str) -> List[Tuple[str, int, str]]:
    """
    Load dataset from directory structure.
    
    Returns:
        List of (video_path, label, filename) tuples where label=0 for real, 1 for fake
    """
    dataset = []
    
    real_dir = os.path.join(data_dir, 'real')
    fake_dir = os.path.join(data_dir, 'fake')
    
    if os.path.exists(real_dir):
        for filename in os.listdir(real_dir):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(real_dir, filename)
                dataset.append((video_path, 0, filename))
    
    if os.path.exists(fake_dir):
        for filename in os.listdir(fake_dir):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(fake_dir, filename)
                dataset.append((video_path, 1, filename))
    
    return dataset


def evaluate_dataset(dataset: List[Tuple[str, int, str]], 
                    model_path: str,
                    config_path: str,
                    output_csv: str) -> Dict:
    """Evaluate classifier on dataset."""
    classifier = EnsembleClassifier(config_path=config_path)
    if os.path.exists(model_path):
        classifier.load(model_path)
    else:
        print(f"Warning: Model not found at {model_path}, using rule-based classifier")
    
    results = []
    correct = 0
    total = 0
    
    for i, (video_path, true_label, filename) in enumerate(dataset):
        print(f"Processing {i+1}/{len(dataset)}: {filename}")
        
        try:
            # Extract features
            features = extract_all_features(video_path, enable_hand_analysis=True)
            
            # Predict
            result = classifier.predict(features)
            pred_score = result['score']
            pred_label = result['label']
            
            # Map label to 0/1
            pred_label_int = 1 if pred_label == 'DEEPFAKE' else (0 if pred_label == 'REAL' else 0.5)
            
            # Check correctness
            is_correct = (pred_label_int == true_label) if pred_label_int != 0.5 else False
            if is_correct:
                correct += 1
            total += 1
            
            results.append({
                'filename': filename,
                'true_label': 'real' if true_label == 0 else 'fake',
                'pred_score': pred_score,
                'pred_label': pred_label,
                'correct': is_correct,
                'explanations': '; '.join(result.get('explanations', []))
            })
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            results.append({
                'filename': filename,
                'true_label': 'real' if true_label == 0 else 'fake',
                'pred_score': 0.5,
                'pred_label': 'ERROR',
                'correct': False,
                'explanations': str(e)
            })
    
    # Compute metrics
    accuracy = correct / total if total > 0 else 0.0
    
    # Confusion matrix
    tp = sum(1 for r in results if r['true_label'] == 'fake' and r['pred_label'] == 'DEEPFAKE')
    tn = sum(1 for r in results if r['true_label'] == 'real' and r['pred_label'] == 'REAL')
    fp = sum(1 for r in results if r['true_label'] == 'real' and r['pred_label'] == 'DEEPFAKE')
    fn = sum(1 for r in results if r['true_label'] == 'fake' and r['pred_label'] == 'REAL')
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Save results to CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'true_label', 'pred_score', 'pred_label', 'correct', 'explanations'])
        writer.writeheader()
        writer.writerows(results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    print(f"Total videos: {total}")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"\nConfusion Matrix:")
    print(f"  True Positives (fake->DEEPFAKE):  {tp}")
    print(f"  True Negatives (real->REAL):       {tn}")
    print(f"  False Positives (real->DEEPFAKE):  {fp}")
    print(f"  False Negatives (fake->REAL):     {fn}")
    print(f"\nMetrics:")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1 Score:  {f1:.3f}")
    print(f"\nResults saved to {output_csv}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate ensemble classifier on dataset')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Directory containing real/ and fake/ subdirectories')
    parser.add_argument('--model_path', type=str, default='models/ensemble_classifier.pkl',
                       help='Path to trained model')
    parser.add_argument('--config_path', type=str, default='models/ensemble_config.json',
                       help='Path to configuration file')
    parser.add_argument('--output_csv', type=str, default='evaluation_results.csv',
                       help='Path to save evaluation results CSV')
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.data_dir}...")
    dataset = load_dataset(args.data_dir)
    print(f"Found {len(dataset)} videos\n")
    
    if len(dataset) == 0:
        print("Error: No videos found in dataset")
        return
    
    # Evaluate
    evaluate_dataset(dataset, args.model_path, args.config_path, args.output_csv)


if __name__ == '__main__':
    main()

