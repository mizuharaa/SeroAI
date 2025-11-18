"""
Compare old and improved fusion models on test data.
"""
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, classification_report
)

def load_model(model_path):
    """Load a trained model."""
    try:
        return joblib.load(model_path)
    except Exception as e:
        print(f"Failed to load {model_path}: {e}")
        return None

def evaluate_model(model, X_test, y_test, threshold=0.5):
    """Evaluate model and return metrics."""
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    pr_auc = average_precision_score(y_test, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "brier": brier,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn)
    }

def main():
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    
    # Load test data
    print("\n[1/4] Loading test data...")
    df = pd.read_csv("data/training/features.csv")
    
    FEATURES = [
        "quality.blur", "quality.brisque", "quality.bitrate", "quality.shake",
        "wm.detected",
        "forensics.prnu", "forensics.flicker", "forensics.codec",
        "face.mouth_exag", "face.mouth_static", "face.eye_blink", "face.sym_drift",
        "art.edge", "art.texture", "art.color", "art.freq",
        "temp.flow_oddity", "temp.rppg"
    ]
    
    feats = [c for c in FEATURES if c in df.columns]
    
    # Create interaction features if needed (for improved model)
    interactions = [
        ("forensics.flicker", "temp.flow_oddity"),
        ("art.edge", "art.texture"),
        ("face.mouth_exag", "face.eye_blink"),
        ("forensics.prnu", "quality.blur"),
        ("temp.rppg", "face.mouth_exag"),
    ]
    
    for feat1, feat2 in interactions:
        if feat1 in df.columns and feat2 in df.columns:
            mask = df[feat1].notna() & df[feat2].notna()
            if mask.sum() > 0:
                df[f"{feat1}_x_{feat2}"] = df[feat1] * df[feat2]
    
    # Add interaction features to feature list
    interaction_feats = [c for c in df.columns if '_x_' in c]
    feats.extend(interaction_feats)
    
    X = df[feats].copy()
    y = np.asarray(df["label"], dtype=int)
    
    # Use same test split as training (20% test)
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Test set: {len(X_test)} samples")
    
    # Load models
    print("\n[2/4] Loading models...")
    old_model = load_model("models/fusion.pkl")
    new_model = load_model("models/fusion_improved.pkl")
    
    if old_model is None:
        print("WARNING: Old model not found. Skipping comparison.")
        return
    
    if new_model is None:
        print("WARNING: New model not found. Train it first with:")
        print("  python scripts/train_fusion_improved.py --use_smote --use_interactions")
        return
    
    # Load thresholds
    print("\n[3/4] Loading thresholds...")
    try:
        with open("models/fusion_thresholds.json", "r") as f:
            old_thresholds = json.load(f)
        old_cons_threshold = old_thresholds.get("ai_threshold_conservative", 0.5)
    except:
        old_cons_threshold = 0.5
    
    try:
        with open("models/fusion_thresholds_improved.json", "r") as f:
            new_thresholds = json.load(f)
        new_cons_threshold = new_thresholds.get("ai_threshold_conservative", 0.5)
    except:
        new_cons_threshold = 0.5
    
    # Evaluate
    print("\n[4/4] Evaluating models...")
    
    print("\n" + "-" * 60)
    print("OLD MODEL (Default Threshold = 0.5)")
    print("-" * 60)
    old_default = evaluate_model(old_model, X_test, y_test, 0.5)
    print(f"ROC-AUC:  {old_default['roc_auc']:.4f}")
    print(f"PR-AUC:   {old_default['pr_auc']:.4f}")
    print(f"Brier:    {old_default['brier']:.4f}")
    print(f"Precision: {old_default['precision']:.3f}")
    print(f"Recall:    {old_default['recall']:.3f}")
    print(f"F1:        {old_default['f1']:.3f}")
    print(f"TP={old_default['tp']}, FP={old_default['fp']}, TN={old_default['tn']}, FN={old_default['fn']}")
    
    print("\n" + "-" * 60)
    print(f"OLD MODEL (Conservative Threshold = {old_cons_threshold:.4f})")
    print("-" * 60)
    old_cons = evaluate_model(old_model, X_test, y_test, old_cons_threshold)
    print(f"ROC-AUC:  {old_cons['roc_auc']:.4f}")
    print(f"PR-AUC:   {old_cons['pr_auc']:.4f}")
    print(f"Brier:    {old_cons['brier']:.4f}")
    print(f"Precision: {old_cons['precision']:.3f}")
    print(f"Recall:    {old_cons['recall']:.3f}")
    print(f"F1:        {old_cons['f1']:.3f}")
    print(f"TP={old_cons['tp']}, FP={old_cons['fp']}, TN={old_cons['tn']}, FN={old_cons['fn']}")
    
    print("\n" + "-" * 60)
    print("NEW MODEL (Default Threshold = 0.5)")
    print("-" * 60)
    new_default = evaluate_model(new_model, X_test, y_test, 0.5)
    print(f"ROC-AUC:  {new_default['roc_auc']:.4f}")
    print(f"PR-AUC:   {new_default['pr_auc']:.4f}")
    print(f"Brier:    {new_default['brier']:.4f}")
    print(f"Precision: {new_default['precision']:.3f}")
    print(f"Recall:    {new_default['recall']:.3f}")
    print(f"F1:        {new_default['f1']:.3f}")
    print(f"TP={new_default['tp']}, FP={new_default['fp']}, TN={new_default['tn']}, FN={new_default['fn']}")
    
    print("\n" + "-" * 60)
    print(f"NEW MODEL (Conservative Threshold = {new_cons_threshold:.4f})")
    print("-" * 60)
    new_cons = evaluate_model(new_model, X_test, y_test, new_cons_threshold)
    print(f"ROC-AUC:  {new_cons['roc_auc']:.4f}")
    print(f"PR-AUC:   {new_cons['pr_auc']:.4f}")
    print(f"Brier:    {new_cons['brier']:.4f}")
    print(f"Precision: {new_cons['precision']:.3f}")
    print(f"Recall:    {new_cons['recall']:.3f}")
    print(f"F1:        {new_cons['f1']:.3f}")
    print(f"TP={new_cons['tp']}, FP={new_cons['fp']}, TN={new_cons['tn']}, FN={new_cons['fn']}")
    
    # Improvement summary
    print("\n" + "=" * 60)
    print("IMPROVEMENT SUMMARY")
    print("=" * 60)
    
    roc_improvement = new_default['roc_auc'] - old_default['roc_auc']
    pr_improvement = new_default['pr_auc'] - old_default['pr_auc']
    brier_improvement = old_default['brier'] - new_default['brier']  # Lower is better
    
    print(f"\nROC-AUC improvement: {roc_improvement:+.4f} ({roc_improvement/old_default['roc_auc']*100:+.1f}%)")
    print(f"PR-AUC improvement:  {pr_improvement:+.4f} ({pr_improvement/old_default['pr_auc']*100:+.1f}%)")
    print(f"Brier improvement:   {brier_improvement:+.4f} ({brier_improvement/old_default['brier']*100:+.1f}%)")
    print(f"F1 improvement:     {new_default['f1'] - old_default['f1']:+.4f}")
    
    # False positive reduction
    fp_reduction = old_default['fp'] - new_default['fp']
    fp_reduction_pct = (fp_reduction / old_default['fp'] * 100) if old_default['fp'] > 0 else 0
    print(f"\nFalse Positives: {old_default['fp']} -> {new_default['fp']} ({fp_reduction:+d}, {fp_reduction_pct:+.1f}%)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

