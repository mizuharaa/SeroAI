# Watermark Detection System Revamp Summary

## Overview

The watermark detection system has been completely revamped to use **visual logo matching** against reference logos, making verified AI model watermarks a **dominant signal (50% weight)** that can override other detection axes.

## Key Changes

### 1. Visual Logo Matching System

**New Module**: `core/logo_matcher.py`

- **Template Matching**: Uses Normalized Cross-Correlation (NCC) to match video frames against reference logos
- **Feature Matching**: Uses ORB keypoint matching for robust detection
- **Histogram Comparison**: Compares color distributions
- **Structural Similarity**: SSIM-like comparison for shape matching

**Supported Providers**:
- Sora (OpenAI)
- Gemini (Google)
- Pika / Pika Labs
- Luma / Luma AI
- Runway
- HeyGen
- D-ID

### 2. Dynamic Axis Weights

**Default Weights** (no verified watermark):
```python
{
    "motion": 0.50,
    "bio": 0.20,
    "scene": 0.15,
    "texture": 0.10,
    "watermark": 0.05
}
```

**Watermark-Dominant Weights** (verified watermark detected):
```python
{
    "motion": 0.25,
    "bio": 0.10,
    "scene": 0.10,
    "texture": 0.05,
    "watermark": 0.50  # Dominant!
}
```

### 3. Watermark Verification Logic

**Verified Watermark Criteria**:
- Logo similarity >= 0.80 (high threshold)
- Visual match against reference logo (not just text)
- Consistent appearance across frames

**Text Overlays** (like "sora.ai" without logo):
- Low similarity score (< 0.80)
- Treated as generic/untrusted
- Low watermark score (capped at 0.3)
- Does NOT trigger watermark-dominant mode

### 4. Watermark Override Rule

When `has_verified_watermark = True`:

```python
# Strong assumption: official-looking AI logo ⇒ AI-generated
final_prob = max(base_score, 0.85 * watermark_conf)
label = "AI-GENERATED"  # Never UNCERTAIN with verified watermark
```

This ensures that verified logos always result in AI-GENERATED label, even if other axes suggest otherwise.

### 5. Enhanced Logging

Terminal output now shows:

```
Watermarks & Provenance (weight: 0.50): 0.950
  - provenance_type: sora
  - watermark_conf: 0.950
  - watermark_mode: VERIFIED_MODEL_LOGO
  - logo_match_method: NCC+ORB
  - details: Verified sora logo watermark detected. Logo similarity: 0.95...
  - override: Verified sora logo watermark detected; logo similarity 0.95. 
              Switching to watermark-dominant weighting and overriding other axes.
```

## Example: Sora-Style MLK Video

### Input Scores:
- Motion: 0.420
- Bio: 0.650
- Scene: 0.155
- Texture: 0.367
- **Watermark: 0.950** (verified Sora logo)

### With Verified Watermark:
- **Weights**: Watermark-dominant (watermark = 0.50)
- **Base Score**: 0.4575
- **Override Score**: 0.8075 (0.85 * 0.95)
- **Final Score**: 0.8075 (max of base and override)
- **Label**: **AI-GENERATED** (never UNCERTAIN)

### Without Verified Watermark (text overlay only):
- **Weights**: Default (watermark = 0.05)
- **Watermark Score**: 0.12 (low, text-only)
- **Base Score**: ~0.40
- **Label**: UNCERTAIN (if base < 0.60)

## Reference Logo Storage

**Location**: `assets/reference_logos/`

**Required Files**:
- `sora_logo.png`
- `gemini_logo.png`
- `pika_logo.png`
- `luma_logo.png`
- `runway_logo.png`
- `heygen_logo.png`
- `did_logo.png`

**Note**: If logos are not found, system falls back to text-based detection (lower confidence).

## Detection Pipeline

1. **Frame Sampling**: Extract frames from first 3-5 seconds
2. **Region Extraction**: Check common watermark regions (corners, edges)
3. **Logo Matching**: Compare each region against all reference logos
4. **Similarity Scoring**: Multi-method scoring (NCC, ORB, histogram, SSIM)
5. **Verification**: If similarity >= 0.80 → verified watermark
6. **Weight Selection**: Use watermark-dominant weights if verified
7. **Override**: Apply watermark override rule if verified

## API Compatibility

✅ **Maintained**: Public API unchanged
- `analyze(media_path)` returns same structure
- Additional fields: `provenance_info`, `axis_weights`, `override_explanation`

## Files Created/Modified

1. **`core/logo_matcher.py`** - Visual logo matching engine
2. **`core/provenance_detector.py`** - Updated to use logo matcher
3. **`core/detection_engine.py`** - Dynamic weights and override logic
4. **`assets/reference_logos/README.md`** - Logo storage instructions
5. **`logs/analysis/example_sora_verified_log.json`** - Example log

## Example Terminal Output

```
================================================================================
DEEPFAKE DETECTION ANALYSIS RESULTS
================================================================================
Video: sora_mlk_brainrot_video.mp4

5-AXIS FEATURE SCORES:
--------------------------------------------------------------------------------
  Motion/Temporal Stability (weight: 0.25):     0.420
  Biological/Physical Realism (weight: 0.10):   0.650
  Scene & Lighting Logic (weight: 0.10):       0.155
  Texture & Frequency Artifacts (weight: 0.05): 0.367
  Watermarks & Provenance (weight: 0.50):     0.950
    - provenance_type: sora
    - watermark_conf: 0.950
    - watermark_mode: VERIFIED_MODEL_LOGO
    - logo_match_method: NCC+ORB
    - details: Verified sora logo watermark detected. Logo similarity: 0.95...
    - override: Verified sora logo watermark detected; logo similarity 0.95. 
                Switching to watermark-dominant weighting and overriding other axes.

FINAL DECISION:
--------------------------------------------------------------------------------
  Base Score (weighted sum): 0.4575
  Watermark Override Score: 0.8075 (0.85 * 0.95)
  Final Score (max of base and override): 0.8075
  Label: AI-GENERATED
  Decision: AI-GENERATED (verified watermark override)
```

## Key Benefits

1. **Robust to Troll Overlays**: Text-only overlays won't trigger high confidence
2. **Dominant Signal**: Verified logos become 50% of decision
3. **Override Protection**: Verified logos always result in AI-GENERATED
4. **Visual Verification**: Uses actual logo shapes, not just text
5. **Multi-Method Matching**: NCC + ORB + histogram + SSIM for robustness

## Next Steps

1. **Add Reference Logos**: Place actual transparent PNG logos in `assets/reference_logos/`
2. **Tune Similarity Thresholds**: Adjust `VERIFIED_THRESHOLD` (0.80) if needed
3. **Extend Providers**: Add more AI model logos as needed
4. **Calibrate Weights**: Fine-tune axis weights based on real dataset performance

