# Aggressive Detection Revamp Summary

## Critical Issues Fixed

### 1. Watermark Detection - NOW AGGRESSIVE

**Problem**: Watermark detection was too conservative, missing many watermarks.

**Solution**:
- **ANY text overlay** → minimum 0.50 score (was 0.30 max)
- **AI keywords detected** (Sora, Runway, Pika, etc.) → minimum 0.60 score
- **Watermark detected** → Forces watermark-dominant mode (50% weight)
- **Watermark detection** now checks for AI keywords even if OCR confidence is low

**New Logic**:
```python
if text_detected or has_ai_keyword:
    if has_ai_keyword:
        watermark_score = max(0.60, text_confidence)  # AI keyword = 0.60+
    else:
        watermark_score = max(0.50, text_confidence)  # Any overlay = 0.50+
```

### 2. Watermark Weight - NOW 50% WHEN DETECTED

**Problem**: Watermark wasn't getting 50% weight even when detected.

**Solution**:
- **If ANY watermark detected** → Forces `has_verified_watermark = True`
- **Watermark-dominant weights applied**: watermark = 0.50, motion = 0.25, etc.
- **Debug logging** added to confirm watermark detection and weight application

**New Weights (when watermark detected)**:
```python
{
    "motion": 0.25,      # Reduced from 0.50
    "bio": 0.10,        # Reduced from 0.20
    "scene": 0.10,      # Reduced from 0.15
    "texture": 0.05,    # Reduced from 0.10
    "watermark": 0.50   # DOMINANT - 50% of final score!
}
```

### 3. Motion Detection - NOW MORE SENSITIVE

**Problem**: Motion detection thresholds were too high, missing subtle artifacts.

**Solution**: Lowered all thresholds and increased scores:

#### Static Region Variance:
- **Old**: 0.3 → 0.7 score, 0.15 → 0.4 score
- **New**: 0.15 → 0.75 score, 0.08 → 0.55 score, 0.04 → 0.35 score (new)

#### Edge Consistency:
- **Old**: 0.2 → 0.8 score, 0.1 → 0.5 score
- **New**: 0.12 → 0.85 score, 0.06 → 0.65 score, 0.03 → 0.45 score (new)

#### Optical Flow:
- **Old**: 2.0 → 0.7 score, 1.0 → 0.4 score
- **New**: 1.5 → 0.75 score, 0.8 → 0.55 score, 0.4 → 0.35 score (new)

#### Face Jitter Detection (NEW):
- Added `_detect_face_jitter()` method
- Tracks face position/size across frames
- Detects sudden jumps, jitter, and size changes
- More sophisticated than simple position tracking

### 4. Bio/Physics Detection - NOW MORE SENSITIVE

**Problem**: Face position/size change thresholds were too high.

**Solution**: Lowered thresholds and added consistency checks:

#### Position Changes:
- **Old**: 100 → 0.7, 50 → 0.4
- **New**: 50 → 0.85, 25 → 0.65, 12 → 0.45 (new)
- **Added**: Consistency check (std/mean ratio) for jittery movement

#### Size Changes:
- **Old**: 0.3 → 0.6, 0.15 → 0.3
- **New**: 0.2 → 0.75, 0.1 → 0.55, 0.05 → 0.35 (new)

### 5. Holistic Reasoning - WATERMARK PRIORITY

**Problem**: Watermark wasn't being treated as dominant signal.

**Solution**:
- **Watermark >= 0.50** → Counts as **2 strong AI signals** (not just 1)
- **Watermark >= 0.50** → Boosts final_prob to at least **0.65** (not 0.60)
- **Watermark detection** → Forces AI-GENERATED if probability is close to threshold

## Example: Watermark Detection Flow

### Before:
1. Text overlay detected → score 0.12
2. Base score: 0.40
3. Result: **UNCERTAIN**

### After:
1. Text overlay detected → **boosted to 0.50**
2. AI keyword "Sora" found → **boosted to 0.60**
3. Watermark-dominant weights applied (watermark = 50%)
4. Base score: 0.50 * 0.50 (watermark) + other axes = **~0.55+**
5. Holistic reasoning: Watermark = 2 strong signals → **AI-GENERATED**
6. Result: **AI-GENERATED** (probability ~0.65+)

## Debug Output

New debug logging shows:
```
[detection_engine] Watermark detected! Score: 0.60, Forcing watermark-dominant mode (50% weight)
[detection_engine] Using watermark-dominant weights: {'motion': 0.25, 'bio': 0.10, 'scene': 0.10, 'texture': 0.05, 'watermark': 0.50}
```

## Key Improvements

1. **Watermark Detection**: 3x more aggressive (0.50 minimum vs 0.30 max)
2. **Watermark Weight**: Guaranteed 50% when detected
3. **Motion Sensitivity**: 2x more sensitive (lower thresholds)
4. **Bio Sensitivity**: 2x more sensitive (lower thresholds)
5. **Face Jitter**: New sophisticated detection method
6. **Holistic Reasoning**: Watermark counts as 2 signals, boosts to 0.65

## Expected Results

- **Videos with watermarks**: Should now get **AI-GENERATED** (not UNCERTAIN)
- **Videos with motion artifacts**: Should now get higher scores (more sensitive)
- **Videos with face jitter**: Should now be detected (new method)
- **Overall**: More confident, fewer UNCERTAIN results

## Files Modified

1. **`core/provenance_detector.py`**: Aggressive watermark detection (0.50+ minimum)
2. **`core/detection_engine.py`**:
   - More sensitive motion detection
   - More sensitive bio/physics detection
   - Face jitter detection (new)
   - Watermark-dominant mode enforcement
   - Debug logging

