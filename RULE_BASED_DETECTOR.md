# Rule-Based Detector System

## Overview

The new rule-based detector system replaces the biased supervised model with a forensic feature-driven approach. It prioritizes explicit detection signals over learned patterns from a biased training dataset.

## Key Changes

### 1. Legacy Model Disabled by Default

The old supervised model (`DeepfakeFusion`) was trained on a biased dataset:
- **Deepfakes**: Mainly talking-head clips (static, exaggerated faces, grainy/noisy)
- **Real**: Wide variety of normal clips

This caused the model to learn: "If it doesn't look like a talking deepfake → mark as REAL"

**Solution**: Legacy model is disabled by default (`USE_LEGACY_MODEL = False` in `core/config_detection.py`)

### 2. Feature-Based Detection

The new detector uses weighted forensic features:

1. **Watermark Evidence** (weight: 0.40) - Highest priority
   - Detects visible AI generator watermarks/logos/text
   - Forces minimum score if high confidence watermark detected

2. **Noise/Shimmer** (weight: 0.25) - High priority
   - Shimmer intensity (high-frequency texture changes)
   - Background motion inconsistency
   - Flat region noise drift

3. **Anatomy** (weight: 0.15) - Only if human present
   - Hand skeleton anomalies
   - Mouth abnormalities
   - Eye blink patterns

4. **Temporal Identity** (weight: 0.10)
   - Face embedding consistency
   - Head pose jitter

5. **Frequency Artifacts** (weight: 0.07)
   - DCT/FFT boundary artifacts
   - Frequency energy ratios

6. **Audio Sync** (weight: 0.03)
   - Lip-audio correlation
   - Phoneme lag

### 3. Human Presence Gating

Anatomy features are only used when humans are detected:
- Minimum 10 frames with face/person detected
- Minimum 30% of frames with human presence
- If no human detected, anatomy features are ignored (weight = 0)

### 4. Watermark Forcing

If watermark detected with confidence >= 0.7:
- Forces score >= 0.5
- Never outputs "REAL" label (at best "UNCERTAIN")

## Files Created/Modified

### New Files

1. **`core/config_detection.py`**
   - Configuration for weights, thresholds, and settings
   - Easy to tune without touching core logic

2. **`core/detector_rule_based.py`**
   - Main rule-based detector class
   - Weighted feature combination
   - Explanation generation

3. **`features/watermark_features.py`**
   - Watermark detection features
   - Uses existing watermark OCR system

4. **`core/human_presence.py`**
   - Human detection for gating anatomy features
   - Uses face detection + MediaPipe pose detection

5. **`scripts/debug_rule_based_detector.py`**
   - Debug script for testing detector
   - Prints all features and explanations

### Modified Files

1. **`features/motion_features.py`**
   - Added shimmer detection features:
     - `shimmer_intensity`
     - `background_motion_inconsistency`
     - `flat_region_noise_drift`

2. **`features/feature_extractor.py`**
   - Added watermark feature extraction
   - Updated default features to include shimmer

3. **`app/service.py`**
   - Uses rule-based detector as primary method
   - Falls back to standard fusion only if rule-based fails

## Usage

### Running Detection

The detector is automatically used in the main service:

```python
from core.detector_rule_based import SeroRuleBasedDetector

detector = SeroRuleBasedDetector()
result = detector.detect(video_path)

print(f"Score: {result['score']}")
print(f"Label: {result['label']}")
print(f"Explanations: {result['explanations']}")
```

### Debug Script

Test the detector on a video:

```bash
python scripts/debug_rule_based_detector.py --video path/to/video.mp4 --verbose
```

This prints:
- Final score and label
- All explanations
- All feature values (grouped by category)

### Configuration

Edit `core/config_detection.py` to adjust:

- **Weights**: Change feature importance
- **Thresholds**: Adjust detection sensitivity
- **Legacy Model**: Enable/disable and set weight
- **Human Presence**: Minimum frames/fraction required

## Example Output

```
Score: 0.7234
Label: DEEPFAKE
Explanations:
1. Watermark detected (confidence=0.85)
2. Strong shimmer detected (intensity=0.68)
3. Background motion inconsistency (score=0.52)
4. Hand skeleton anomalies: missing/merged fingers (ratio=0.35)
5. Temporal identity inconsistency (std=0.61)
```

## Future Improvements

Placeholder hooks for advanced methods (not yet implemented):

- **PRNU consistency**: Real cameras have stable sensor noise patterns
- **Compression regularity**: AI videos may show inconsistent GOP structure
- **Physics consistency**: Shadow directions vs light sources, motion blur

These can be added as additional features in the weighted system.

## Notes

- The system is conservative by default (assumes real unless strong evidence)
- All thresholds are configurable in `config_detection.py`
- Explanations help understand why a video was flagged
- Human presence gating prevents false positives on non-human content

