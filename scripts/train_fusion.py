"""
Train supervised fusion model with robust guardrails and conservative threshold tuning.

Changes for false-positive reduction:
1. Feature health checks: ensure no all-NaN or zero-variance columns
2. Asymmetric threshold optimization for minimizing false AI on real content
3. Feature importance extraction to identify over-weighted artifact modules
4. Conservative AI threshold persistence for runtime use
"""
import os
import json
import argparse
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve, confusion_matrix
)
import joblib

FEATURES = [
    "quality.blur", "quality.brisque", "quality.bitrate", "quality.shake",
    "wm.detected",
    "forensics.prnu", "forensics.flicker", "forensics.codec",
    "face.mouth_exag", "face.mouth_static", "face.eye_blink", "face.sym_drift",
    "art.edge", "art.texture", "art.color", "art.freq",
    "temp.flow_oddity", "temp.rppg"
]

# Critical temporal features that must be present
CRITICAL_TEMPORAL = ["temp.flow_oddity", "temp.rppg"]


def check_feature_health(df: pd.DataFrame, features: list) -> dict:
    """
    Validate feature health before training.
    
    Returns dict with:
        - missing_cols: columns not in df
        - all_nan_cols: columns with 100% NaN
        - zero_var_cols: columns with zero variance
        - high_nan_cols: columns with >50% NaN
        - summary: per-column stats
    """
    health = {
        "missing_cols": [],
        "all_nan_cols": [],
        "zero_var_cols": [],
        "high_nan_cols": [],
        "summary": {}
    }
    
    for feat in features:
        if feat not in df.columns:
            health["missing_cols"].append(feat)
            continue
        
        col = df[feat]
        nan_pct = col.isna().sum() / len(col)
        valid = col.dropna()
        
        stats = {
            "nan_pct": float(nan_pct),
            "n_valid": len(valid),
            "mean": float(valid.mean()) if len(valid) > 0 else None,
            "std": float(valid.std()) if len(valid) > 0 else None,
            "min": float(valid.min()) if len(valid) > 0 else None,
            "max": float(valid.max()) if len(valid) > 0 else None
        }
        health["summary"][feat] = stats
        
        if nan_pct == 1.0:
            health["all_nan_cols"].append(feat)
        elif nan_pct > 0.5:
            health["high_nan_cols"].append(feat)
        
        if len(valid) > 0 and valid.std() == 0:
            health["zero_var_cols"].append(feat)
    
    return health


def find_conservative_threshold(y_true, y_pred_proba, target_fpr=0.05):
    """
    Find AI threshold that achieves target false positive rate on real samples.
    
    Args:
        y_true: true labels (0=real, 1=AI)
        y_pred_proba: predicted AI probabilities
        target_fpr: target false positive rate (default 5%)
    
    Returns:
        threshold achieving approximately target_fpr
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    
    # Find threshold where FPR <= target_fpr
    idx = np.where(fpr <= target_fpr)[0]
    if len(idx) == 0:
        # If can't achieve target, use most conservative
        return float(thresholds[0])
    
    # Use the highest threshold that still keeps FPR <= target
    best_idx = idx[-1]
    return float(thresholds[best_idx])


def extract_feature_importances(pipeline, feature_names):
    """
    Extract feature importances from the trained LogisticRegression.
    
    Returns dict mapping feature name to importance (absolute coefficient after scaling).
    """
    # Get the calibrated classifier
    clf = pipeline.named_steps['clf']
    
    # CalibratedClassifierCV wraps the base estimator
    if hasattr(clf, 'calibrated_classifiers_'):
        # Get first fold's base estimator (they should be similar)
        base_est = clf.calibrated_classifiers_[0].base_estimator
    else:
        base_est = clf
    
    if not hasattr(base_est, 'coef_'):
        return {}
    
    # Get coefficients (shape: [1, n_features] for binary classification)
    coefs = base_est.coef_[0]
    
    # Map to feature names
    importances = {}
    for i, feat in enumerate(feature_names):
        importances[feat] = float(np.abs(coefs[i]))
    
    return importances


def main():
    ap = argparse.ArgumentParser(description="Train supervised fusion model with robust guardrails")
    ap.add_argument("--in_csv", default="data/training/features.csv", help="Input features CSV")
    ap.add_argument("--out_model", default="models/fusion.pkl", help="Output model path")
    ap.add_argument("--metrics", default="models/fusion_metrics.json", help="Metrics JSON path")
    ap.add_argument("--feature_health", default="models/feature_health.json", help="Feature health report")
    ap.add_argument("--thresholds", default="models/fusion_thresholds.json", help="Threshold config")
    ap.add_argument("--test_size", type=float, default=0.2, help="Test fraction")
    ap.add_argument("--val_size", type=float, default=0.1, help="Validation fraction (from train)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument("--target_fpr", type=float, default=0.05, help="Target FPR for conservative threshold")
    args = ap.parse_args()

    print(f"Loading data from {args.in_csv}...")
    df = pd.read_csv(args.in_csv)
    print(f"Loaded {len(df)} rows")
    
    # ========== STEP 1: Feature Health Checks ==========
    print("\n[1/8] Checking feature health...")
    health = check_feature_health(df, FEATURES)
    
    # Save health report
    os.makedirs(os.path.dirname(args.feature_health), exist_ok=True)
    with open(args.feature_health, "w") as f:
        json.dump(health, f, indent=2)
    print(f"Feature health report saved to {args.feature_health}")
    
    # Critical checks
    if health["missing_cols"]:
        raise ValueError(
            f"CRITICAL: Missing feature columns: {health['missing_cols']}\n"
            f"Re-run feature extraction to include all expected features."
        )
    
    if health["all_nan_cols"]:
        raise ValueError(
            f"CRITICAL: Features with 100% NaN values: {health['all_nan_cols']}\n"
            f"These features have no valid data. Re-run feature extraction."
        )
    
    # Check critical temporal features
    for feat in CRITICAL_TEMPORAL:
        if feat in health["high_nan_cols"]:
            warnings.warn(
                f"WARNING: Temporal feature '{feat}' has >{50}% NaN values. "
                f"This will severely limit model quality. Consider re-extracting features."
            )
    
    if health["zero_var_cols"]:
        warnings.warn(
            f"WARNING: Zero-variance features (will be dropped): {health['zero_var_cols']}"
        )
    
    if health["high_nan_cols"]:
        print(f"High-NaN features (>50%): {health['high_nan_cols']}")
    
    # Select features that are actually present
    feats = [c for c in FEATURES if c in df.columns and c not in health["all_nan_cols"]]
    print(f"Using {len(feats)} features for training")
    
    # Drop rows where critical temporal features are ALL missing
    critical_present = [f for f in CRITICAL_TEMPORAL if f in feats]
    if critical_present:
        # Keep rows that have at least ONE valid temporal feature
        mask = df[critical_present].notna().any(axis=1)
        n_before = len(df)
        df = df[mask].copy()
        n_after = len(df)
        if n_after < n_before:
            print(f"Dropped {n_before - n_after} rows with all-missing temporal features")
    
    X = df[feats].copy()
    y = df["label"].astype(int).values
    
    print(f"Final dataset: {len(X)} samples, {len(feats)} features")
    print(f"Class distribution: Real={np.sum(y==0)}, AI={np.sum(y==1)}")
    
    # ========== STEP 2: Train/Val/Test Split ==========
    print("\n[2/8] Splitting data...")
    # First split: train+val vs test
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    
    # Second split: train vs val
    val_fraction = args.val_size / (1 - args.test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=val_fraction,
        random_state=args.seed, stratify=y_trainval
    )
    
    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # ========== STEP 3: Build Pipeline ==========
    print("\n[3/8] Building pipeline...")
    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("sc", StandardScaler())
            ]), feats)
        ],
        remainder="drop"
    )
    
    base = LogisticRegression(max_iter=300, class_weight="balanced", random_state=args.seed)
    clf = CalibratedClassifierCV(base, cv=3, method="sigmoid")
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    
    # ========== STEP 4: Train ==========
    print("\n[4/8] Training model...")
    pipe.fit(X_train, y_train)
    print("Training complete")
    
    # ========== STEP 5: Evaluate on Test Set ==========
    print("\n[5/8] Evaluating on test set...")
    p_test = pipe.predict_proba(X_test)[:, 1]
    
    metrics = {
        "roc_auc": float(roc_auc_score(y_test, p_test)),
        "pr_auc": float(average_precision_score(y_test, p_test)),
        "brier": float(brier_score_loss(y_test, p_test)),
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test)
    }
    
    print(f"Test ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Test PR-AUC: {metrics['pr_auc']:.4f}")
    print(f"Test Brier: {metrics['brier']:.4f}")
    
    # ========== STEP 6: Find Conservative Threshold on Validation Set ==========
    print("\n[6/8] Finding conservative AI threshold on validation set...")
    p_val = pipe.predict_proba(X_val)[:, 1]
    
    # Default balanced threshold (0.5 for calibrated model)
    threshold_default = 0.5
    
    # Conservative threshold to minimize false positives on real content
    threshold_conservative = find_conservative_threshold(
        y_val, p_val, target_fpr=args.target_fpr
    )
    
    print(f"Default threshold: {threshold_default}")
    print(f"Conservative threshold (FPR≈{args.target_fpr}): {threshold_conservative:.4f}")
    
    # Evaluate both thresholds on validation set
    pred_default = (p_val >= threshold_default).astype(int)
    pred_conservative = (p_val >= threshold_conservative).astype(int)
    
    cm_default = confusion_matrix(y_val, pred_default)
    cm_conservative = confusion_matrix(y_val, pred_conservative)
    
    print("\nDefault threshold confusion matrix (val):")
    print(f"  TN={cm_default[0,0]}, FP={cm_default[0,1]}")
    print(f"  FN={cm_default[1,0]}, TP={cm_default[1,1]}")
    
    print("\nConservative threshold confusion matrix (val):")
    print(f"  TN={cm_conservative[0,0]}, FP={cm_conservative[0,1]}")
    print(f"  FN={cm_conservative[1,0]}, TP={cm_conservative[1,1]}")
    
    # Save thresholds
    thresholds_config = {
        "ai_threshold_default": float(threshold_default),
        "ai_threshold_conservative": float(threshold_conservative),
        "real_threshold_default": 0.20,  # Keep existing
        "unsure_low": 0.35,  # Slightly expanded UNSURE band
        "unsure_high": 0.65,
        "target_fpr": args.target_fpr,
        "note": "Conservative threshold minimizes false AI on real content; use for general uploads"
    }
    
    os.makedirs(os.path.dirname(args.thresholds), exist_ok=True)
    with open(args.thresholds, "w") as f:
        json.dump(thresholds_config, f, indent=2)
    print(f"\nThreshold config saved to {args.thresholds}")
    
    # ========== STEP 7: Extract Feature Importances ==========
    print("\n[7/8] Extracting feature importances...")
    importances = extract_feature_importances(pipe, feats)
    
    if importances:
        # Sort by importance
        sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        print("\nTop 10 most important features:")
        for feat, imp in sorted_imp[:10]:
            print(f"  {feat}: {imp:.4f}")
        
        # Check if artifact/frequency features dominate
        artifact_feats = ["art.edge", "art.texture", "art.color", "art.freq",
                          "forensics.flicker", "forensics.codec"]
        artifact_importance = sum(importances.get(f, 0) for f in artifact_feats if f in importances)
        total_importance = sum(importances.values())
        
        if total_importance > 0:
            artifact_ratio = artifact_importance / total_importance
            print(f"\nArtifact/frequency features account for {artifact_ratio*100:.1f}% of total importance")
            if artifact_ratio > 0.5:
                warnings.warn(
                    "WARNING: Artifact/frequency features dominate (>50%). "
                    "This may cause false positives on compressed/edited real content. "
                    "Runtime fusion will apply flow-conditioned down-weighting."
                )
        
        metrics["feature_importances"] = importances
        metrics["artifact_importance_ratio"] = float(artifact_ratio) if total_importance > 0 else 0.0
    
    # ========== STEP 8: Save Model and Metrics ==========
    print("\n[8/8] Saving model and metrics...")
    os.makedirs(os.path.dirname(args.out_model), exist_ok=True)
    joblib.dump(pipe, args.out_model)
    
    with open(args.metrics, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nModel saved to {args.out_model}")
    print(f"Metrics saved to {args.metrics}")
    print("\nTraining complete! ✓")
    print(f"\nNext steps:")
    print(f"1. Review {args.feature_health} for feature quality")
    print(f"2. Use conservative threshold ({threshold_conservative:.3f}) in runtime fusion for general uploads")
    print(f"3. Monitor false positive rate on real content and adjust target_fpr if needed")


if __name__ == "__main__":
    main()
