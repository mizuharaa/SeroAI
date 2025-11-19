# Ensemble Detection Fix - Summary

## Problem
Every video was being flagged as 100% deepfake confidence, causing false positives.

## Root Cause
The rule-based prediction in `ensemble_classifier.py` was:
1. Using thresholds that were too low (triggering on neutral/default values)
2. Starting from a neutral score (0.5) instead of assuming real content
3. Not requiring strong enough evidence before increasing the score
4. Not capping maximum scores appropriately

## Fixes Applied

### 1. Conservative Rule-Based Prediction (`SeroAI/models/ensemble_classifier.py`)
- **Changed base score**: Now starts at 0.2 (assumes real content) instead of 0.5
- **Raised all thresholds**: 
  - Strong evidence now requires values > 0.75 (was 0.6)
  - Moderate evidence requires values > 0.65 (was 0.5)
  - Anatomy features require > 0.5 (was 0.2)
- **Added real-world evidence checks**: Good features (smooth motion, good sync) now REDUCE the score
- **Requires multiple signals**: Need 3+ strong signals OR 5+ moderate signals to significantly increase score
- **Score capping**: 
  - Scores > 0.7 require 4+ strong signals OR 6+ moderate signals
  - Scores > 0.95 require 5+ strong signals
- **Default behavior**: When no evidence, returns 0.15 (low score, assumes real)

### 2. Updated Thresholds (`SeroAI/models/ensemble_config.json`)
- `real_threshold`: 0.25 (was 0.35)
- `uncertain_low`: 0.25 (was 0.35)
- `uncertain_high`: 0.75 (was 0.65)
- `deepfake_threshold`: 0.75 (was 0.65)

### 3. Debug Logging (`SeroAI/core/ensemble_detector.py`)
- Added logging to track predictions and feature values
- Warns when high scores are detected and shows top contributing features

## Long-Term Solution Architecture

The system now uses a **feature-based ensemble** that combines:

### Feature Modules
1. **Motion Features** (`features/motion_features.py`)
   - Optical flow analysis
   - Temporal identity consistency
   - Head pose jitter
   - Constant motion pixel detection

2. **Anatomy Features** (`features/anatomy_features.py`)
   - MediaPipe Hands analysis (missing fingers, abnormal angles)
   - MediaPipe Face Mesh (mouth opening, eye blinks)
   - Lip sync smoothness

3. **Frequency Features** (`features/frequency_features.py`)
   - DCT/FFT analysis on face crops
   - High/low frequency energy ratios
   - Boundary artifact detection

4. **Audio Sync Features** (`features/audio_sync_features.py`)
   - MFCC extraction
   - Lip-audio correlation
   - Phoneme lag detection

### Ensemble Classifier (`models/ensemble_classifier.py`)
- **Primary**: Trained ML model (Logistic Regression, Random Forest, XGBoost, etc.)
- **Fallback**: Conservative rule-based prediction (when no trained model exists)
- **Calibration**: Platt scaling/isotonic regression for probability calibration
- **Thresholds**: Configurable via `ensemble_config.json`

### Integration (`core/ensemble_detector.py` + `app/service.py`)
- Ensemble is used as PRIMARY method for videos
- Falls back to standard fusion if ensemble fails
- Explanations are merged with existing reasons

## Testing Recommendations

1. **Test with known real videos**: Should return scores < 0.3 (REAL)
2. **Test with known deepfakes**: Should return scores > 0.75 (DEEPFAKE) only if multiple strong signals present
3. **Monitor debug logs**: Check which features are contributing to high scores
4. **Tune thresholds**: Adjust `ensemble_config.json` based on your dataset

## Next Steps for Improvement

1. **Train a model**: Use `train_ensemble.py` to train on labeled data
2. **Calibrate probabilities**: Use calibration to improve probability estimates
3. **Feature engineering**: Refine feature extraction based on false positive/negative analysis
4. **Threshold tuning**: Adjust thresholds based on your specific use case and acceptable false positive rate

## Configuration

Edit `SeroAI/models/ensemble_config.json` to adjust thresholds:
```json
{
  "thresholds": {
    "real_threshold": 0.25,      // Below this = REAL
    "uncertain_low": 0.25,       // Start of uncertain range
    "uncertain_high": 0.75,      // End of uncertain range
    "deepfake_threshold": 0.75   // Above this = DEEPFAKE
  }
}
```

## Notes

- The system is now **conservative by default** - it assumes content is real unless strong evidence suggests otherwise
- This reduces false positives but may increase false negatives
- For production use, train a model on your specific dataset for best results
- The rule-based fallback is designed to be safe but may not be as accurate as a trained model

