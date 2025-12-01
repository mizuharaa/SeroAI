# Deepfake Detection Pipeline Refactoring Summary

## Overview

The detection pipeline has been refactored into a modular, config-based architecture with structured logging and evaluation capabilities.

## New Architecture

### 1. Core Types (`core/types_analysis.py`)

- **`VideoAnalysisResult`**: Main dataclass storing complete analysis results
  - Aggregated feature values
  - Normalized features (z-scores)
  - Deepfake score and label
  - List of contributing reasons
  - Sample per-frame records
  - Human-readable summary

- **`FrameRecord`**: Per-frame debug records
- **`FeatureReason`**: Contributing feature with contribution score

### 2. Feature Extraction (`core/feature_extractor.py`)

Modular feature extractors:

- **`SpatialFeatures`**: Single-frame spatial analysis
  - `extract_texture_artifact_score()`: Compares face vs background frequency characteristics

- **`TemporalFeatures`**: Sequence-based temporal analysis
  - `extract_blink_anomaly_score()`: Blink rate and timing patterns
  - `extract_landmark_jitter_score()`: Landmark stability over time
  - `extract_pose_background_inconsistency()`: Head pose vs background motion

- **`AudioVisualFeatures`**: Audio-visual synchronization
  - `extract_lip_sync_error()`: Mouth movement vs audio correlation

- **`FeatureExtractor`**: Main orchestrator combining all modules

### 3. Score Calibration (`core/score_calibrator.py`)

- **`ScoreCalibrator`**: Config-based normalization and scoring
  - Z-score normalization: `z = (x - mean_real) / std_real`
  - Logistic combination: `sigmoid(sum(weights * z) + bias)`
  - Configurable weights and decision threshold
  - Reads from `config/feature_stats.json`

### 4. Logging (`core/logger_analysis.py`)

- **`AnalysisLogger`**: Structured JSON logging
  - Writes to `logs/analysis/<video_id>.json`
  - Generates human-readable summaries
  - Includes all metadata, features, reasons, and frame records

### 5. Refactored Detector (`core/detector_rule_based.py`)

- **`SeroRuleBasedDetector`**: Main detector class
  - `analyze_video()`: New API returning `VideoAnalysisResult`
  - `detect()`: Legacy API maintained for compatibility
  - Integrates all new modules

### 6. Evaluation Script (`tools/evaluate_detector.py`)

- Evaluates detector on labeled dataset
- Computes confusion matrix, precision, recall, F1, accuracy
- Optionally saves detailed CSV for offline analysis
- Supports directory structure (real/ and fake/ subdirs) or CSV input

### 7. Configuration (`config/feature_stats.json`)

- Feature statistics (mean_real, std_real) for normalization
- Feature weights for scoring
- Bias and decision threshold
- Default values provided, should be calibrated on real dataset

## Features Implemented

All required features are implemented:

1. ✅ **blink_anomaly_score**: From anatomy features (eye_blink_irregularity)
2. ✅ **landmark_jitter_score**: From motion features (temporal_identity_std + head_pose_jitter)
3. ✅ **lip_sync_error**: From audio sync features (1 - lip_audio_correlation)
4. ✅ **texture_artifact_score**: FFT-based face vs background frequency comparison
5. ✅ **pose_background_inconsistency**: Optical flow-based head pose vs background motion
6. ✅ **watermark_prob**: From existing watermark detection (strict matching)

## Usage Examples

### Basic Usage

```python
from core.detector_rule_based import SeroRuleBasedDetector

detector = SeroRuleBasedDetector()
result = detector.analyze_video("video.mp4")

print(f"Deepfake score: {result.deepfake_score:.3f}")
print(f"Label: {result.label}")
print(f"Summary: {result.summary}")

# Access features
print(f"Blink anomaly: {result.features['blink_anomaly_score']:.3f}")
print(f"Landmark jitter: {result.features['landmark_jitter_score']:.3f}")

# Top contributing reasons
for reason in result.reasons[:3]:
    print(f"{reason.name}: {reason.contribution:.3f}")
```

### Legacy API (Compatible)

```python
detector = SeroRuleBasedDetector()
result_dict = detector.detect("video.mp4")

print(f"Score: {result_dict['score']}")
print(f"Label: {result_dict['label']}")
print(f"Explanations: {result_dict['explanations']}")
```

### Evaluation

```bash
# Evaluate on directory structure
python tools/evaluate_detector.py dataset/ --csv results.csv

# Evaluate on CSV file
python tools/evaluate_detector.py dataset.csv --csv results.csv
```

## Example JSON Log

See `logs/analysis/example_log.json` for a complete example of the structured log format.

Key sections:
- **metadata**: Video ID, path, timestamp, version
- **features**: Raw feature values
- **normalized_features**: Z-score normalized values
- **deepfake_score**: Final probability [0, 1]
- **label**: "deepfake" or "authentic"
- **reasons**: Top contributing features with contributions
- **summary**: Human-readable summary
- **frame_records**: Sampled per-frame debug data
- **parameters**: Analysis parameters used

## Configuration

Edit `config/feature_stats.json` to:
- Calibrate feature statistics on your dataset
- Adjust feature weights
- Change decision threshold (default: 0.6)

## File Structure

```
SeroAI/
├── core/
│   ├── types_analysis.py          # Dataclasses and types
│   ├── feature_extractor.py        # Modular feature extraction
│   ├── score_calibrator.py         # Normalization and scoring
│   ├── logger_analysis.py          # Structured logging
│   └── detector_rule_based.py      # Refactored detector
├── config/
│   └── feature_stats.json          # Feature stats and weights
├── tools/
│   └── evaluate_detector.py        # Evaluation script
└── logs/
    └── analysis/                    # JSON log files
        └── example_log.json        # Example log
```

## Key Improvements

1. **Modularity**: Features organized by type (spatial, temporal, audio-visual)
2. **Config-based**: All thresholds and weights in JSON config
3. **Structured logging**: Rich JSON logs for debugging and analysis
4. **Transparency**: Clear reasons showing which features contributed
5. **Extensibility**: Easy to add new features
6. **Compatibility**: Legacy API maintained

## Next Steps

1. Calibrate `config/feature_stats.json` on your real dataset
2. Tune feature weights based on evaluation results
3. Add more sophisticated feature implementations as needed
4. Extend frame records with more detailed per-frame data

