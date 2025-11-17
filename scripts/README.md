# SeroAI Training Scripts

This directory contains scripts for training and retraining the deepfake detection fusion model.

## Overview

SeroAI uses a hybrid approach:
1. **Feature extraction**: Multiple detection signals (forensics, artifacts, face dynamics, temporal cues, etc.) are computed for each video
2. **Supervised fusion**: A calibrated Logistic Regression model combines these signals into a final AI probability
3. **Rule-based fallback**: If no trained model exists, a weighted average with adaptive weights is used
4. **Real-evidence override**: Strong real-world cues can cap the AI probability to prevent false positives

## Quick Start

### 1. Organize Training Data

Place labeled videos in:
- `data/raw/real/` - Real, authentic videos (label=0)
- `data/raw/fake/` - AI-generated or deepfake videos (label=1)

**Data quality tips**:
- Use diverse sources (different cameras, lighting, compression)
- Include edge cases: talk shows, sports, interviews, vlogs, news clips
- Ensure temporal features can be computed (videos should be >2 seconds, >15 fps)
- Remove temporary/incomplete files (`.tmp`, `.crdownload`, etc.)

### 2. Extract Features

```bash
python scripts/extract_features.py \
  --out data/training/features.csv \
  --flush_every 1
```

**Options**:
- `--out`: Output CSV path (default: `data/training/features.csv`)
- `--limit`: Process only N files (for testing)
- `--no-resume`: Overwrite existing CSV instead of resuming
- `--flush_every`: Flush to disk every N rows (default: 1 for safety)

**What it does**:
- Iterates through `data/raw/real` and `data/raw/fake`
- Calls the full analysis pipeline for each video
- Extracts 18 features (quality, watermark, forensics, face dynamics, artifacts, temporal)
- Appends to CSV row-by-row (safe to interrupt and resume)
- Skips files already processed (checks `id` column)

**Features extracted**:
```
quality.blur, quality.brisque, quality.bitrate, quality.shake
wm.detected
forensics.prnu, forensics.flicker, forensics.codec
face.mouth_exag, face.mouth_static, face.eye_blink, face.sym_drift
art.edge, art.texture, art.color, art.freq
temp.flow_oddity, temp.rppg
```

**Expected runtime**: ~30-60 seconds per video (depends on length and resolution)

### 3. Train the Fusion Model

```bash
python -m scripts.train_fusion \
  --in_csv data/training/features.csv \
  --target_fpr 0.05
```

**Options**:
- `--in_csv`: Input features CSV (default: `data/training/features.csv`)
- `--out_model`: Output model path (default: `models/fusion.pkl`)
- `--metrics`: Metrics JSON path (default: `models/fusion_metrics.json`)
- `--feature_health`: Feature health report (default: `models/feature_health.json`)
- `--thresholds`: Threshold config (default: `models/fusion_thresholds.json`)
- `--test_size`: Test set fraction (default: 0.2)
- `--val_size`: Validation set fraction (default: 0.1)
- `--target_fpr`: Target false positive rate for conservative threshold (default: 0.05)
- `--seed`: Random seed (default: 42)

**What it does**:
1. **Feature health checks**: Validates no missing/all-NaN/zero-variance columns
2. **Data splitting**: Train/val/test with stratification
3. **Model training**: LogisticRegression + CalibratedClassifierCV (3-fold sigmoid calibration)
4. **Threshold optimization**: Finds conservative AI threshold achieving target FPR on validation set
5. **Feature importance extraction**: Identifies which features dominate (warns if artifacts >50%)
6. **Saves outputs**:
   - `models/fusion.pkl` - trained model pipeline
   - `models/fusion_metrics.json` - ROC-AUC, PR-AUC, Brier score, feature importances
   - `models/feature_health.json` - per-feature statistics and warnings
   - `models/fusion_thresholds.json` - default and conservative AI thresholds

**Expected metrics** (on balanced dataset):
- ROC-AUC: >0.90
- PR-AUC: >0.85
- Brier score: <0.15

### 4. Deploy and Test

The model is automatically loaded on server start. Check the console for:
```
[fusion] Loaded supervised fusion model: models/fusion.pkl
[fusion] Loaded conservative thresholds: AI=0.850
```

Test on known false positive cases:
- Upload a talk show clip (e.g., Jimmy Fallon)
- Upload a sports video with smooth pans
- Verify prob_ai < 0.40 with real-evidence override message

Test on known deepfakes:
- Upload a Sora/Runway/FaceSwap video
- Verify prob_ai > conservative_threshold

## Retraining Loop

### When to Retrain

1. **New training data**: Added more labeled videos to `data/raw/`
2. **Feature drift**: User feedback indicates systematic errors
3. **Distribution shift**: Deploying to new domain (e.g., news → social media)
4. **Feature improvements**: Updated forensics/temporal modules

### Incremental Retraining

To add new data without re-processing everything:

```bash
# Extract features for new videos only (resume mode)
python scripts/extract_features.py --out data/training/features.csv

# Retrain with updated dataset
python -m scripts.train_fusion --in_csv data/training/features.csv
```

The extractor automatically skips videos already in the CSV (checks `id` column).

### Full Retraining

To start fresh (e.g., after major feature changes):

```bash
# Clear old features
rm data/training/features.csv

# Extract all features
python scripts/extract_features.py --out data/training/features.csv --no-resume

# Train new model
python -m scripts.train_fusion --in_csv data/training/features.csv
```

## Troubleshooting

### Feature Health Warnings

After training, check `models/feature_health.json`:

**Problem**: `"all_nan_cols": ["temp.flow_oddity"]`
- **Cause**: Temporal features failed to compute for all videos
- **Fix**: Check video quality (too short, corrupted, no motion)
- **Action**: Re-extract features after fixing videos

**Problem**: `"high_nan_cols": ["temp.rppg"]` (>50% NaN)
- **Cause**: rPPG requires faces; many videos have no faces or too short
- **Fix**: Acceptable if dataset is face-light; otherwise add more face videos
- **Action**: Monitor if model relies too heavily on other features

**Problem**: `"zero_var_cols": ["wm.detected"]`
- **Cause**: No watermarks detected in any training video
- **Fix**: Expected if training on real camera footage; model will learn from other signals
- **Action**: No action needed unless you specifically want watermark training

### Training Errors

**Error**: `CRITICAL: Missing feature columns: ['temp.flow_oddity']`
- **Cause**: Feature extraction script doesn't match training script's expected columns
- **Fix**: Re-run `extract_features.py` with latest version
- **Action**: Check that `FEATURES` list in both scripts matches

**Error**: `CRITICAL: Features with 100% NaN values: ['temp.rppg']`
- **Cause**: Feature computation failed for all videos
- **Fix**: Debug the rPPG module; check if videos have faces
- **Action**: Temporarily remove from `FEATURES` list if not critical

**Warning**: `Artifact/frequency features dominate (>50%)`
- **Cause**: Temporal features missing/weak, so model overfits to artifacts
- **Impact**: High false positive rate on compressed real content
- **Fix**: Ensure temporal features are present and diverse training data
- **Action**: Re-extract features, add more real videos with natural motion

### Low Performance

**ROC-AUC < 0.80**:
- Check class balance (should be roughly 50/50 real vs fake)
- Inspect feature health report for missing columns
- Verify training data quality (no mislabeled videos)
- Consider adding more diverse training data

**High false positive rate** (real videos flagged as AI):
- Check `artifact_importance_ratio` in metrics JSON
- If >0.5, temporal features are weak → re-extract with better videos
- Increase `target_fpr` to make conservative threshold more aggressive (e.g., 0.03)
- Review real-evidence override criteria in `core/fusion.py`

**High false negative rate** (deepfakes not detected):
- Check if training data includes modern generators (Sora, Runway, etc.)
- Verify watermark detection is working
- Inspect feature importances to see which signals are weak
- Consider adding more diverse deepfake examples

## Advanced: Feature Engineering

### Adding New Features

1. **Compute the feature** in the analysis pipeline (e.g., `core/forensics.py`)
2. **Add to extraction script** in `scripts/extract_features.py`:
   ```python
   FEATURES = [
       # ... existing features ...
       "new_module.new_score"
   ]
   
   def gather_one(video_path, label):
       # ... existing code ...
       feats["new_module.new_score"] = float(result.get("new_module", {}).get("new_score", 0.5))
   ```
3. **Add to training script** in `scripts/train_fusion.py`:
   ```python
   FEATURES = [
       # ... existing features ...
       "new_module.new_score"
   ]
   ```
4. **Re-extract and retrain**:
   ```bash
   rm data/training/features.csv
   python scripts/extract_features.py --out data/training/features.csv
   python -m scripts.train_fusion
   ```

### Tuning Real-Evidence Override

Edit `core/fusion.py` → `_apply_hard_evidence_boosts()`:

```python
# Adjust criteria thresholds
if prnu >= 0.75:  # was 0.70
    z -= 0.8
    real_evidence_count += 1

# Adjust override threshold
if real_evidence_count >= 4:  # was 3
    override_cap = 0.35  # was 0.40
```

### Tuning Artifact Down-Weighting

Edit `core/fusion.py` → `_get_artifact_scale()`:

```python
def _get_artifact_scale(self, flow_oddity: float) -> float:
    if flow_oddity <= 0.10:  # was 0.15
        return 0.1  # was 0.2 (more aggressive)
    elif flow_oddity <= 0.20:  # was 0.25
        return 0.3  # was 0.4
    # ...
```

## Monitoring Production

### Key Metrics

Track these over time (from user feedback and validation sets):

1. **False positive rate** on verified real content (target: <5%)
2. **True positive rate** on verified deepfakes (target: >90%)
3. **Real-evidence override frequency** (typical: 10-30% of real videos)
4. **Average artifact down-weighting factor** (typical: 0.4-0.7 for real videos)
5. **Feature importance drift** (from `models/fusion_metrics.json`)

### Feedback Integration

User feedback is stored in `data/feedback.db` and automatically adjusts metric weights:
- Correct detections → increase metric weight
- Incorrect detections → decrease metric weight
- Effect is small per feedback (~0.1-1.0 adjustment)
- Weights are Laplace-smoothed and clamped [0.3, 2.2]

To reset feedback weights:
```bash
rm data/feedback.db
```

### A/B Testing New Models

1. Train new model to `models/fusion_v2.pkl`
2. Update `core/config.py` → `FUSION_MODEL_PATH = "models/fusion_v2.pkl"`
3. Restart server
4. Monitor metrics for 24-48 hours
5. Roll back if performance degrades

## Dataset Recommendations

### Minimum Dataset Size
- **Small**: 100 real + 100 fake (baseline, expect overfitting)
- **Medium**: 500 real + 500 fake (good generalization)
- **Large**: 2000+ real + 2000+ fake (production-ready)

### Diversity Checklist
- [ ] Multiple video sources (YouTube, Vimeo, social media, camera footage)
- [ ] Various content types (interviews, vlogs, sports, news, presentations)
- [ ] Different quality levels (1080p, 720p, 480p, compressed)
- [ ] Multiple generators for fakes (Sora, Runway, FaceSwap, DeepFaceLab, etc.)
- [ ] Edge cases (overlays, subtitles, watermarks, filters)
- [ ] Temporal diversity (static shots, pans, zooms, cuts)

### Labeling Guidelines
- **Real (label=0)**: Authentic, unmodified video from real camera/screen recording
- **Fake (label=1)**: Any AI-generated or manipulated content
  - Full synthetic (Sora, Runway, Midjourney video)
  - Face swap (DeepFaceLab, FaceSwap)
  - Voice clone + face animation
  - Partial manipulation (background replacement, object insertion)

### Data Augmentation (Optional)
For small datasets, consider:
- Temporal cropping (use different segments of same video)
- Quality degradation (compress, add noise)
- **Warning**: Don't augment by adding artifacts - this will confuse the model

## Performance Benchmarks

### Hardware Requirements
- **CPU**: 4+ cores recommended for parallel feature extraction
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Optional (only used if face/temporal modules are GPU-accelerated)
- **Storage**: ~1GB per 1000 training videos (features + models)

### Processing Times (per video)
- **Feature extraction**: 30-60s (depends on length, resolution, complexity)
- **Training**: 1-5 minutes (depends on dataset size)
- **Inference**: 8-15s (with all modules enabled)

### Scaling
For large datasets (>10K videos):
- Use `--flush_every 10` to reduce I/O overhead
- Consider parallel extraction (split dataset, merge CSVs)
- Use Parquet instead of CSV for faster loading:
  ```python
  df = pd.read_csv("features.csv")
  df.to_parquet("features.parquet")
  ```
  Then update `train_fusion.py` to read Parquet

## References

- [Kaggle Deep Fake Detection Dataset](https://www.kaggle.com/datasets/sanikatiwarekar/deep-fake-detection-dfd-entire-original-dataset)
- [CalibratedClassifierCV Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)
- [Logistic Regression for Imbalanced Data](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

## Support

For issues or questions:
1. Check `models/feature_health.json` for warnings
2. Review `models/fusion_metrics.json` for performance
3. Inspect `IMPLEMENTATION_SUMMARY.md` for detailed algorithm explanations
4. Open an issue on GitHub with logs and metrics

