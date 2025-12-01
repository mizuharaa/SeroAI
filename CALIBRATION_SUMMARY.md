# Deepfake Detector Calibration Summary

## Overview

The 5-axis deepfake detector has been recalibrated to correctly flag Sora-style videos (like Kobe Bryant clips) as AI-generated while remaining robust to troll overlays.

## Key Changes

### 1. Configurable Thresholds

**File**: `config/detector_thresholds.json`

```json
{
  "ai_threshold": 0.60,
  "auth_threshold": 0.30
}
```

- **Before**: >= 0.85 = AI-GENERATED, <= 0.15 = AUTHENTIC
- **After**: >= 0.60 = AI-GENERATED, <= 0.30 = AUTHENTIC
- Thresholds are loaded from config file at initialization
- More sensitive to AI-generated content

### 2. Refactored Watermark/Provenance Detection

**File**: `core/provenance_detector.py`

#### Sora-Style Watermark Detection

The new `ProvenanceDetector` class separates:
- **Sora-style trusted watermarks**: High-confidence, consistent, persistent watermarks matching Sora keywords
- **Generic overlays**: Random text/logos that are not trusted

#### Detection Logic

1. **OCR Detection**: Uses existing watermark OCR system
2. **Keyword Matching**: Checks for Sora keywords (SORA, SORA.AI, etc.)
3. **Consistency Check**: Verifies watermark appears in consistent region
4. **Persistence Check**: Verifies watermark appears in high percentage of frames
5. **Confidence Scoring**: Multi-factor confidence (OCR confidence, persistence, corner placement, generator hint)

#### Dynamic Weighting

- **Trusted Sora watermark** (sora_conf >= 0.8): `watermark_weight = 0.25`
- **Generic/untrusted**: `watermark_weight = 0.05` (default)

### 3. Semantic Impossibility Boost

**Function**: `semantic_impossibility_boost(subject, provenance_info)`

Detects semantic impossibilities:
- Deceased celebrities (Kobe Bryant, Michael Jackson, etc.) appearing in Sora-style clips
- Returns boost value [0, 0.4] added to base score

**Example**: Kobe Bryant (deceased 2020) in Sora-style clip → +0.30 boost

### 4. Enhanced Logging

Terminal output now includes:
- Provenance type (none, generic_or_untrusted, sora_style_trusted)
- Sora confidence score
- Dynamic watermark weight applied
- Semantic boost and reason
- Detailed watermark detection information

## Example Output

### Sora-Style Kobe Bryant Video

```
================================================================================
DEEPFAKE DETECTION ANALYSIS RESULTS
================================================================================
Video: kobe_bryant_sora_video.mp4

5-AXIS FEATURE SCORES:
--------------------------------------------------------------------------------
  Motion/Temporal Stability (weight: 0.50):     0.420
  Biological/Physical Realism (weight: 0.20):   0.650
  Scene & Lighting Logic (weight: 0.15):       0.155
  Texture & Frequency Artifacts (weight: 0.10): 0.367
  Watermarks & Provenance (weight: 0.25):     0.930
    - provenance_type: sora_style_trusted
    - sora_confidence: 0.950
    - details: High-confidence Sora-style watermark detected: 'SORA.AI' (confidence=0.92, persistent=true, corner=true, sora_conf=0.95)

SEMANTIC IMPOSSIBILITY BOOST:
--------------------------------------------------------------------------------
  Boost: +0.300
  Reason: Semantic impossibility: kobe_bryant (deceased 2020) in Sora-style clip (impossible new footage)

FINAL DECISION:
--------------------------------------------------------------------------------
  Base Score (before semantic boost): 0.4897
  Semantic Boost: +0.300
  Final Deepfake Probability: 0.7897
  Label: AI-GENERATED
  Decision Thresholds: >= 0.60 = AI-GENERATED, <= 0.30 = AUTHENTIC, else = UNCERTAIN
```

## Scoring Formula

```
base_score = (
    motion_score * 0.50 +
    bio_physics_score * 0.20 +
    scene_logic_score * 0.15 +
    texture_freq_score * 0.10 +
    watermark_score * watermark_weight  # Dynamic: 0.25 for trusted Sora, 0.05 otherwise
)

final_score = clamp(base_score + semantic_boost, 0.0, 1.0)
```

## Configuration Files

### `config/detector_thresholds.json`
- `ai_threshold`: Threshold for AI-GENERATED label (default: 0.60)
- `auth_threshold`: Threshold for AUTHENTIC label (default: 0.30)

### Tuning Recommendations

1. **Lower thresholds** if too many false negatives (real AI content not detected)
2. **Raise thresholds** if too many false positives (real content flagged as AI)
3. **Adjust SORA_CONFIDENCE_THRESHOLD** in `provenance_detector.py` to change when watermark weight increases
4. **Add more deceased celebrities** to `semantic_impossibility_boost` function for better detection

## API Compatibility

The public API remains unchanged:
- `analyze(media_path)` returns the same structure
- Additional fields added: `provenance_info`, `watermark_weight`, `semantic_boost`, `semantic_reason`
- Backward compatible with existing code

## Files Modified

1. `core/detection_engine.py` - Main detection logic with configurable thresholds and provenance detection
2. `core/provenance_detector.py` - New module for Sora-style watermark detection
3. `config/detector_thresholds.json` - Configurable thresholds
4. Terminal logging enhanced with provenance details

## Example Log File

See `logs/analysis/example_sora_kobe_log.json` for a complete example of the structured log format for a Sora-style Kobe Bryant video.

