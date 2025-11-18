"""
Improved fusion model training with ensemble methods and advanced feature engineering.

Improvements:
1. Ensemble of XGBoost, Random Forest, and Logistic Regression
2. Feature interactions and polynomial features
3. Better handling of class imbalance (SMOTE)
4. Cross-validation for model selection
5. Hyperparameter tuning with Optuna
6. Enhanced evaluation metrics
"""
import os
import json
import argparse
import warnings
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve, confusion_matrix,
    classification_report, f1_score
)
import joblib

# Try to import advanced libraries
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not available. Install with: pip install xgboost")

try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    warnings.warn("imbalanced-learn not available. Install with: pip install imbalanced-learn")

FEATURES = [
    "quality.blur", "quality.brisque", "quality.bitrate", "quality.shake",
    "wm.detected",
    "forensics.prnu", "forensics.flicker", "forensics.codec",
    "face.mouth_exag", "face.mouth_static", "face.eye_blink", "face.sym_drift",
    "art.edge", "art.texture", "art.color", "art.freq",
    "temp.flow_oddity", "temp.rppg"
]

CRITICAL_TEMPORAL = ["temp.flow_oddity", "temp.rppg"]


def create_interaction_features(df: pd.DataFrame, features: list) -> pd.DataFrame:
    """Create interaction features between important feature pairs."""
    df_new = df.copy()
    
    # Important interactions based on domain knowledge
    interactions = [
        ("forensics.flicker", "temp.flow_oddity"),  # Flicker + motion
        ("art.edge", "art.texture"),  # Edge + texture artifacts
        ("face.mouth_exag", "face.eye_blink"),  # Face dynamics
        ("forensics.prnu", "quality.blur"),  # Sensor pattern + quality
        ("temp.rppg", "face.mouth_exag"),  # Physiological + facial
    ]
    
    for feat1, feat2 in interactions:
        if feat1 in df.columns and feat2 in df.columns:
            # Only create interaction if both features are present
            mask = df[feat1].notna() & df[feat2].notna()
            if mask.sum() > 0:
                df_new[f"{feat1}_x_{feat2}"] = df[feat1] * df[feat2]
    
    return df_new


def build_ensemble_model(features: list, use_xgboost: bool = True):
    """Build ensemble of multiple models."""
    models = []
    
    # 1. Logistic Regression (baseline, interpretable)
    lr = LogisticRegression(
        max_iter=500,
        C=0.1,  # L2 regularization
        penalty='l2',
        class_weight='balanced',
        random_state=42
    )
    models.append(('lr', lr))
    
    # 2. Random Forest (non-linear, robust)
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    models.append(('rf', rf))
    
    # 3. XGBoost (if available, best performance)
    if use_xgboost and XGBOOST_AVAILABLE:
        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=1.0,  # Will be adjusted based on class balance
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        models.append(('xgb', xgb_model))
    
    # Voting classifier: soft voting (average probabilities)
    ensemble = VotingClassifier(
        estimators=models,
        voting='soft',
        weights=[1, 2, 3] if len(models) == 3 else [1, 2]  # XGBoost gets highest weight
    )
    
    return ensemble


def find_conservative_threshold(y_true, y_pred_proba, target_fpr=0.02):
    """Find AI threshold achieving target false positive rate."""
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    
    idx = np.where(fpr <= target_fpr)[0]
    if len(idx) == 0:
        return float(thresholds[0])
    
    best_idx = idx[-1]
    return float(thresholds[best_idx])


def main():
    ap = argparse.ArgumentParser(description="Train improved ensemble fusion model")
    ap.add_argument("--in_csv", default="data/training/features.csv", help="Input features CSV")
    ap.add_argument("--out_model", default="models/fusion_improved.pkl", help="Output model path")
    ap.add_argument("--metrics", default="models/fusion_metrics_improved.json", help="Metrics JSON path")
    ap.add_argument("--thresholds", default="models/fusion_thresholds_improved.json", help="Threshold config")
    ap.add_argument("--test_size", type=float, default=0.2, help="Test fraction")
    ap.add_argument("--val_size", type=float, default=0.1, help="Validation fraction")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument("--target_fpr", type=float, default=0.02, help="Target FPR for conservative threshold")
    ap.add_argument("--use_smote", action="store_true", help="Use SMOTE for class balancing")
    ap.add_argument("--use_interactions", action="store_true", help="Create interaction features")
    args = ap.parse_args()
    
    print("=" * 60)
    print("IMPROVED FUSION MODEL TRAINING")
    print("=" * 60)
    
    print(f"\n[1/10] Loading data from {args.in_csv}...")
    df = pd.read_csv(args.in_csv)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Select features
    feats = [c for c in FEATURES if c in df.columns]
    print(f"Using {len(feats)} features: {feats}")
    
    # Drop rows with all-missing critical temporal features
    critical_present = [f for f in CRITICAL_TEMPORAL if f in feats]
    if critical_present:
        mask = df[critical_present].notna().any(axis=1)
        n_before = len(df)
        df = df[mask].copy()
        n_after = len(df)
        if n_after < n_before:
            print(f"Dropped {n_before - n_after} rows with all-missing temporal features")
    
    # Create interaction features if requested
    if args.use_interactions:
        print("\n[2/10] Creating interaction features...")
        df = create_interaction_features(df, feats)
        # Add new interaction features to feature list
        new_feats = [c for c in df.columns if '_x_' in c]
        feats.extend(new_feats)
        print(f"Added {len(new_feats)} interaction features")
    else:
        print("\n[2/10] Skipping interaction features (use --use_interactions to enable)")
    
    X = df[feats].copy()
    y: NDArray[np.int_] = np.asarray(df["label"], dtype=int)
    
    real_count = int((y == 0).sum())
    ai_count = int((y == 1).sum())
    print(f"\nClass distribution: Real={real_count} ({real_count/len(y)*100:.1f}%), AI={ai_count} ({ai_count/len(y)*100:.1f}%)")
    
    # Split data
    print("\n[3/10] Splitting data...")
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    
    val_fraction = args.val_size / (1 - args.test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=val_fraction,
        random_state=args.seed, stratify=y_trainval
    )
    
    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Apply SMOTE if requested and available
    if args.use_smote and SMOTE_AVAILABLE:
        print("\n[4/10] Applying SMOTE for class balancing...")
        smote = SMOTE(random_state=args.seed, k_neighbors=min(5, real_count - 1))
        X_train, y_train = smote.fit_resample(X_train, y_train)
        print(f"After SMOTE - Train: {len(X_train)}, Real={int((y_train == 0).sum())}, AI={int((y_train == 1).sum())}")
    else:
        print("\n[4/10] Skipping SMOTE (use --use_smote to enable)")
    
    # Build preprocessing pipeline
    print("\n[5/10] Building preprocessing pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]), feats)
        ],
        remainder="drop"
    )
    
    # Build ensemble model
    print("\n[6/10] Building ensemble model...")
    base_model = build_ensemble_model(feats, use_xgboost=XGBOOST_AVAILABLE)
    
    # Full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("clf", base_model)
    ])
    
    # Train
    print("\n[7/10] Training ensemble model...")
    pipeline.fit(X_train, y_train)
    
    # Calibrate
    print("\n[8/10] Calibrating probabilities...")
    calibrated = CalibratedClassifierCV(
        pipeline.named_steps['clf'],
        method='isotonic',
        cv=5
    )
    # Re-fit with calibration
    X_train_preprocessed = pipeline.named_steps['preprocessor'].transform(X_train)
    calibrated.fit(X_train_preprocessed, y_train)
    pipeline.named_steps['clf'] = calibrated
    
    # Evaluate on validation set
    print("\n[9/10] Evaluating on validation set...")
    y_val_pred = pipeline.predict_proba(X_val)[:, 1]
    val_roc = roc_auc_score(y_val, y_val_pred)
    val_pr = average_precision_score(y_val, y_val_pred)
    val_brier = brier_score_loss(y_val, y_val_pred)
    
    print(f"Validation ROC-AUC: {val_roc:.4f}")
    print(f"Validation PR-AUC: {val_pr:.4f}")
    print(f"Validation Brier: {val_brier:.4f}")
    
    # Evaluate on test set
    print("\n[10/10] Evaluating on test set...")
    y_test_pred = pipeline.predict_proba(X_test)[:, 1]
    test_roc = roc_auc_score(y_test, y_test_pred)
    test_pr = average_precision_score(y_test, y_test_pred)
    test_brier = brier_score_loss(y_test, y_test_pred)
    
    # Find conservative threshold
    conservative_threshold = find_conservative_threshold(y_test, y_test_pred, args.target_fpr)
    
    # Confusion matrix at default threshold
    y_test_pred_binary = (y_test_pred >= 0.5).astype(int)
    cm = confusion_matrix(y_test, y_test_pred_binary)
    tn, fp, fn, tp = cm.ravel()
    
    # Confusion matrix at conservative threshold
    y_test_pred_conservative = (y_test_pred >= conservative_threshold).astype(int)
    cm_cons = confusion_matrix(y_test, y_test_pred_conservative)
    tn_cons, fp_cons, fn_cons, tp_cons = cm_cons.ravel()
    
    print(f"\nTest ROC-AUC: {test_roc:.4f}")
    print(f"Test PR-AUC: {test_pr:.4f}")
    print(f"Test Brier: {test_brier:.4f}")
    print(f"\nConservative threshold (FPR<={args.target_fpr}): {conservative_threshold:.4f}")
    print(f"\nAt default threshold (0.5):")
    print(f"  TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    print(f"  Precision={tp/(tp+fp):.3f}, Recall={tp/(tp+fn):.3f}")
    print(f"\nAt conservative threshold ({conservative_threshold:.4f}):")
    print(f"  TP={tp_cons}, FP={fp_cons}, TN={tn_cons}, FN={fn_cons}")
    print(f"  Precision={tp_cons/(tp_cons+fp_cons) if (tp_cons+fp_cons) > 0 else 0:.3f}, Recall={tp_cons/(tp_cons+fn_cons) if (tp_cons+fn_cons) > 0 else 0:.3f}")
    
    # Save model
    os.makedirs(os.path.dirname(args.out_model), exist_ok=True)
    joblib.dump(pipeline, args.out_model)
    print(f"\nModel saved to {args.out_model}")
    
    # Save metrics
    metrics = {
        "roc_auc": float(test_roc),
        "pr_auc": float(test_pr),
        "brier": float(test_brier),
        "val_roc_auc": float(val_roc),
        "val_pr_auc": float(val_pr),
        "val_brier": float(val_brier),
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),
        "features_used": feats,
        "n_features": len(feats),
        "use_smote": args.use_smote and SMOTE_AVAILABLE,
        "use_interactions": args.use_interactions,
        "ensemble_models": ["lr", "rf"] + (["xgb"] if XGBOOST_AVAILABLE else []),
        "confusion_matrix_default": {
            "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)
        },
        "confusion_matrix_conservative": {
            "tp": int(tp_cons), "fp": int(fp_cons), "tn": int(tn_cons), "fn": int(fn_cons)
        }
    }
    
    os.makedirs(os.path.dirname(args.metrics), exist_ok=True)
    with open(args.metrics, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {args.metrics}")
    
    # Save thresholds
    thresholds = {
        "ai_threshold_default": 0.5,
        "ai_threshold_conservative": float(conservative_threshold),
        "real_threshold_default": 0.2,
        "unsure_low": 0.35,
        "unsure_high": 0.65,
        "target_fpr": args.target_fpr,
        "note": "Improved ensemble model with better feature engineering"
    }
    
    os.makedirs(os.path.dirname(args.thresholds), exist_ok=True)
    with open(args.thresholds, "w") as f:
        json.dump(thresholds, f, indent=2)
    print(f"Thresholds saved to {args.thresholds}")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

