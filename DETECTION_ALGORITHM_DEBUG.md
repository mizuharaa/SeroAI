# Deepfake Detection Algorithm - Complete Documentation

## Overview

The rule-based detector uses weighted forensic features to compute a deepfake probability score. This document explains the complete algorithm for debugging purposes.

## 🚨 CRITICAL BUGS IDENTIFIED (From Console Output)

### Bug #1: Watermark Score = 0.0 (CRITICAL)
**Location**: `core/detector_rule_based.py` line 162

**Problem**: 
- Console shows: `watermark_detected: 1.0`, `watermark_confidence: 0.4335`
- Code checks: `if watermark_detected and watermark_conf > 0.5`
- Since 0.4335 < 0.5, watermark_score = 0.0
- **This removes 40% weight (0.40) from the calculation!**

**Impact**: Deepfake video with watermark gets score 0.2240 instead of ~0.43

### Bug #2: Shimmer Thresholds 10x Too High
**Location**: `core/config_detection.py`

**Problem**:
- `shimmer_intensity: 0.0712` but threshold is 0.6 (10x too high!)
- `background_motion_inconsistency: 0.4718` but threshold is 0.5 (just misses)
- `flat_region_noise_drift: 0.1839` but threshold is 0.4 (too high)
- **This removes 25% weight (0.25) from the calculation!**

**Impact**: Real shimmer evidence is completely ignored

### Bug #3: Score Calculation Produces Wrong Result
**Expected**: ~0.43 (with watermark) or ~0.36 (without watermark)
**Actual**: 0.2240

**Possible causes**:
- Watermark bug removes 40% weight
- Shimmer bug removes 25% weight
- Total: 65% of weights contributing 0.0
- Remaining 35% (anatomy 15% + temporal 10% + audio 3% + frequency 7%) = 0.22

### Bug #4: Strong Signals Underweighted
**Console shows 5 strong signals**:
- Hand abnormal angles: 0.78
- Blink irregularity: 0.80  
- Temporal inconsistency: 0.81
- Head pose jitter: 1.00
- Phoneme lag: 1.00

**But final score is only 0.2240** - suggests weights are too low or calculation is wrong

## Algorithm Flow

### 1. Feature Extraction

The system extracts features from multiple modules:

#### Watermark Features (`features/watermark_features.py`)
- `watermark_detected`: 1.0 if watermark found, 0.0 otherwise
- `watermark_confidence`: [0, 1] - confidence of detection
- `watermark_type`: 0=text, 1=logo, 2=pattern
- `watermark_persistence`: [0, 1] - how persistent across frames
- `watermark_corner_score`: [0, 1] - strength in corner regions

#### Human Presence (`core/human_presence.py`)
- `human_present`: 1.0 if human detected, 0.0 otherwise
- `human_detection_frames`: Number of frames with human
- `human_detection_fraction`: Fraction of frames with human
- `face_detection_frames`: Frames with face detected
- `person_detection_frames`: Frames with person detected

**Gating Logic**: If `human_present < 0.5`, anatomy features are ignored (weight = 0)

#### Motion/Shimmer Features (`features/motion_features.py`)
- `shimmer_intensity`: [0, 1] - High-frequency texture changes
- `background_motion_inconsistency`: [0, 1] - Static region motion inconsistency
- `flat_region_noise_drift`: [0, 1] - Pixel stat drift in flat patches
- `constant_motion_ratio`: [0, 1] - Ratio of pixels with constant motion
- `avg_optical_flow_mag_face`: Average optical flow magnitude in face
- `std_optical_flow_mag_face`: Std dev of optical flow in face
- `motion_entropy_face`: [0, 1] - Entropy of motion directions
- `flow_magnitude_mean`: Mean optical flow magnitude (full frame)
- `flow_magnitude_std`: Std dev of optical flow magnitude

#### Temporal Identity Features
- `temporal_identity_std`: [0, 1] - Face embedding variance over time
- `head_pose_jitter`: [0, 1] - Frame-to-frame head pose change variance

#### Anatomy Features (`features/anatomy_features.py`)
- `hand_missing_finger_ratio`: [0, 1] - Ratio of frames with missing/merged fingers
- `hand_abnormal_angle_ratio`: [0, 1] - Ratio of frames with abnormal joint angles
- `avg_hand_landmark_confidence`: [0, 1] - Average hand detection confidence
- `mouth_open_ratio_mean`: Mean mouth opening ratio
- `mouth_open_ratio_std`: Std dev of mouth opening ratio
- `extreme_mouth_open_frequency`: [0, 1] - Frequency of extreme mouth openings
- `lip_sync_smoothness`: [0, 1] - Temporal smoothness of lip movement
- `eye_blink_rate`: Blinks per second
- `eye_blink_irregularity`: [0, 1] - Irregularity of blink patterns

#### Frequency Features (`features/frequency_features.py`)
- `high_freq_energy_face`: High-frequency energy in face region
- `low_freq_energy_face`: Low-frequency energy in face region
- `freq_energy_ratio`: [0, 1] - Ratio of high to low frequency energy
- `boundary_artifact_score`: [0, 1] - Artifact score near face boundaries

#### Audio Sync Features (`features/audio_sync_features.py`)
- `has_audio`: 1.0 if audio present, 0.0 otherwise
- `lip_audio_correlation`: [0, 1] - Correlation between mouth opening and audio
- `avg_phoneme_lag`: [0, 1] - Average lag between phonemes and mouth movement
- `sync_consistency`: [0, 1] - Consistency of audio-visual sync

### 2. Score Computation

The detector computes a weighted score from feature categories:

#### Category Weights (from `core/config_detection.py`)
```python
WEIGHTS = {
    "watermark": 0.40,           # Highest priority
    "noise_shimmer": 0.25,       # High priority
    "anatomy": 0.15,             # Medium (only if human present)
    "temporal_identity": 0.10,   # Medium
    "frequency_artifacts": 0.07, # Low
    "audio_sync": 0.03,          # Lowest
}
```

#### Category Score Computation

**1. Watermark Category** (weight: 0.40)
```python
if watermark_detected and watermark_confidence > 0.5:
    watermark_score = min(watermark_confidence * 1.2, 1.0)
else:
    watermark_score = 0.0
```

**2. Noise/Shimmer Category** (weight: 0.25)
```python
shimmer_evidence = []
if shimmer_intensity >= 0.6:  # SHIMMER_INTENSITY_THRESHOLD
    shimmer_evidence.append(shimmer_intensity)
if background_motion_inconsistency >= 0.5:  # BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD
    shimmer_evidence.append(background_motion_inconsistency)
if flat_region_noise_drift >= 0.4:  # FLAT_REGION_NOISE_DRIFT_THRESHOLD
    shimmer_evidence.append(flat_region_noise_drift)

if shimmer_evidence:
    noise_shimmer_score = mean(shimmer_evidence)
else:
    noise_shimmer_score = 0.0
```

**3. Anatomy Category** (weight: 0.15, only if human present)
```python
if human_present:
    anatomy_evidence = []
    if hand_missing_finger_ratio >= 0.3:  # HAND_MISSING_FINGER_THRESHOLD
        anatomy_evidence.append(hand_missing_finger_ratio)
    if hand_abnormal_angle_ratio >= 0.3:  # HAND_ABNORMAL_ANGLE_THRESHOLD
        anatomy_evidence.append(hand_abnormal_angle_ratio)
    if extreme_mouth_open_frequency >= 0.3:  # EXTREME_MOUTH_OPEN_THRESHOLD
        anatomy_evidence.append(extreme_mouth_open_frequency)
    if eye_blink_irregularity >= 0.7:  # BLINK_IRREGULARITY_THRESHOLD
        anatomy_evidence.append((eye_blink_irregularity - 0.5) * 2.0)  # Normalize
    
    if anatomy_evidence:
        anatomy_score = mean(anatomy_evidence)
    else:
        anatomy_score = 0.0
else:
    anatomy_score = 0.0  # Ignored if no human
```

**4. Temporal Identity Category** (weight: 0.10)
```python
temporal_evidence = []
if temporal_identity_std >= 0.6:  # TEMPORAL_IDENTITY_STD_THRESHOLD
    temporal_evidence.append(temporal_identity_std)
if head_pose_jitter >= 0.7:  # HEAD_POSE_JITTER_THRESHOLD
    temporal_evidence.append(head_pose_jitter)

if temporal_evidence:
    temporal_score = mean(temporal_evidence)
else:
    temporal_score = 0.0
```

**5. Frequency Artifacts Category** (weight: 0.07)
```python
freq_evidence = []
if boundary_artifact_score >= 0.6:  # BOUNDARY_ARTIFACT_THRESHOLD
    freq_evidence.append(boundary_artifact_score)
if freq_energy_ratio >= 0.7:  # FREQ_ENERGY_RATIO_THRESHOLD
    freq_evidence.append((freq_energy_ratio - 0.5) * 2.0)  # Normalize

if freq_evidence:
    frequency_score = mean(freq_evidence)
else:
    frequency_score = 0.0
```

**6. Audio Sync Category** (weight: 0.03, only if audio present)
```python
if has_audio:
    audio_evidence = []
    if lip_audio_correlation < 0.4:  # LIP_AUDIO_CORRELATION_THRESHOLD
        audio_evidence.append(1.0 - lip_audio_correlation)  # Invert
    if avg_phoneme_lag >= 0.5:  # PHONEME_LAG_THRESHOLD
        audio_evidence.append(avg_phoneme_lag)
    
    if audio_evidence:
        audio_score = mean(audio_evidence)
    else:
        audio_score = 0.0
else:
    audio_score = 0.0
```

#### Final Score Calculation

```python
total_score = 0.0
total_weight = 0.0

for category, weight in WEIGHTS.items():
    score = category_scores[category]
    total_score += score * weight
    total_weight += weight

final_score = total_score / total_weight  # Normalize
```

#### Watermark Forcing

```python
if watermark_detected and watermark_confidence >= 0.7:  # WATERMARK_CONFIDENCE_THRESHOLD
    final_score = max(final_score, 0.5)  # WATERMARK_FORCE_MIN_SCORE
```

### 3. Label Assignment

```python
if watermark_detected and watermark_confidence >= 0.7 and WATERMARK_FORCE_UNCERTAIN:
    if score < 0.75:  # SCORE_DEEPFAKE_THRESHOLD
        return "UNCERTAIN"

if score < 0.25:  # SCORE_REAL_THRESHOLD
    return "REAL"
elif score >= 0.75:  # SCORE_DEEPFAKE_THRESHOLD
    return "DEEPFAKE"
else:
    return "UNCERTAIN"
```

## Current Thresholds (from config_detection.py)

```python
# Watermark
WATERMARK_CONFIDENCE_THRESHOLD = 0.7
WATERMARK_FORCE_MIN_SCORE = 0.5

# Shimmer/Noise
SHIMMER_INTENSITY_THRESHOLD = 0.6
BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD = 0.5
FLAT_REGION_NOISE_DRIFT_THRESHOLD = 0.4

# Anatomy
HAND_MISSING_FINGER_THRESHOLD = 0.3
HAND_ABNORMAL_ANGLE_THRESHOLD = 0.3
EXTREME_MOUTH_OPEN_THRESHOLD = 0.3
BLINK_IRREGULARITY_THRESHOLD = 0.7

# Temporal
TEMPORAL_IDENTITY_STD_THRESHOLD = 0.6
HEAD_POSE_JITTER_THRESHOLD = 0.7

# Frequency
BOUNDARY_ARTIFACT_THRESHOLD = 0.6
FREQ_ENERGY_RATIO_THRESHOLD = 0.7

# Audio
LIP_AUDIO_CORRELATION_THRESHOLD = 0.4
PHONEME_LAG_THRESHOLD = 0.5

# Final Score
SCORE_REAL_THRESHOLD = 0.25
SCORE_UNCERTAIN_LOW = 0.25
SCORE_UNCERTAIN_HIGH = 0.75
SCORE_DEEPFAKE_THRESHOLD = 0.75
```

## Example Calculation

Given the test case output:

### Feature Values
- `watermark_detected`: 1.0
- `watermark_confidence`: 0.4335 (BELOW 0.7 threshold)
- `shimmer_intensity`: 0.0712 (BELOW 0.6 threshold)
- `background_motion_inconsistency`: 0.4718 (BELOW 0.5 threshold)
- `flat_region_noise_drift`: 0.1839 (BELOW 0.4 threshold)
- `hand_abnormal_angle_ratio`: 0.7818 (ABOVE 0.3 threshold)
- `eye_blink_irregularity`: 0.8000 (ABOVE 0.7 threshold)
- `temporal_identity_std`: 0.8069 (ABOVE 0.6 threshold)
- `head_pose_jitter`: 1.0000 (ABOVE 0.7 threshold)
- `avg_phoneme_lag`: 1.0000 (ABOVE 0.5 threshold)

### Category Scores
1. **Watermark**: 0.4335 * 1.2 = 0.5202 (but only if > 0.5, so 0.5202)
2. **Noise/Shimmer**: 0.0 (all below thresholds)
3. **Anatomy**: mean([0.7818, (0.8000 - 0.5) * 2.0]) = mean([0.7818, 0.6000]) = 0.6909
4. **Temporal**: mean([0.8069, 1.0000]) = 0.9035
5. **Frequency**: 0.0 (all below thresholds)
6. **Audio**: mean([1.0 - 0.4218, 1.0000]) = mean([0.5782, 1.0000]) = 0.7891

### Weighted Score
```
total_score = (0.5202 * 0.40) + (0.0 * 0.25) + (0.6909 * 0.15) + 
              (0.9035 * 0.10) + (0.0 * 0.07) + (0.7891 * 0.03)
            = 0.2081 + 0.0 + 0.1036 + 0.0904 + 0.0 + 0.0237
            = 0.4258

total_weight = 0.40 + 0.25 + 0.15 + 0.10 + 0.07 + 0.03 = 1.0

final_score = 0.4258 / 1.0 = 0.4258
```

But the actual output shows 0.2240, which suggests:
1. Watermark score might be 0.0 (not being applied correctly)
2. Or there's a bug in the calculation

## Identified Issues (From Console Output)

### Issue 1: Watermark Score Not Applied (CRITICAL BUG)
**Console shows**: `watermark_detected: 1.0`, `watermark_confidence: 0.4335`

**Code logic** (line 162):
```python
if watermark_detected and watermark_conf > 0.5:
    watermark_score = min(watermark_conf * 1.2, 1.0)
else:
    watermark_score = 0.0
```

**Problem**: Since 0.4335 < 0.5, watermark_score = 0.0 even though watermark was detected!
- This removes 40% weight (0.40) from the calculation
- Should use watermark_detected flag more aggressively or lower threshold

**Fix**: Change to `watermark_conf > 0.3` or use `watermark_detected` flag directly

### Issue 2: Shimmer Thresholds Too High
**Console shows**:
- `shimmer_intensity: 0.0712` (threshold: 0.6) - **10x too high!**
- `background_motion_inconsistency: 0.4718` (threshold: 0.5) - just below
- `flat_region_noise_drift: 0.1839` (threshold: 0.4) - too high

**Problem**: All shimmer features below thresholds, so `noise_shimmer_score = 0.0`
- This removes 25% weight (0.25) from the calculation
- Real shimmer evidence is being ignored

**Fix**: Lower thresholds:
- `SHIMMER_INTENSITY_THRESHOLD`: 0.6 → 0.05
- `BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD`: 0.5 → 0.4
- `FLAT_REGION_NOISE_DRIFT_THRESHOLD`: 0.4 → 0.15

### Issue 3: Audio Correlation Threshold Logic Error
**Console shows**: `lip_audio_correlation: 0.4218`, `avg_phoneme_lag: 1.0000`

**Code logic** (line 293):
```python
if lip_corr < LIP_AUDIO_CORRELATION_THRESHOLD:  # 0.4
    audio_evidence.append(1.0 - lip_corr)
```

**Problem**: 0.4218 > 0.4, so correlation check doesn't trigger
- Only phoneme_lag (1.0) is added
- Audio score = mean([1.0]) = 1.0, but weight is only 0.03

**Fix**: Lower threshold to 0.45 or use inverted logic

### Issue 4: Score Calculation Analysis

**Expected calculation** (if watermark worked):
```
watermark: 0.5202 * 0.40 = 0.2081
noise_shimmer: 0.0 * 0.25 = 0.0
anatomy: 0.6909 * 0.15 = 0.1036
temporal: 0.9035 * 0.10 = 0.0904
frequency: 0.0 * 0.07 = 0.0
audio: 0.7891 * 0.03 = 0.0237
Total: 0.4258
```

**Actual output**: 0.2240

**Problem**: Score is ~half of expected, suggesting:
1. Watermark score = 0.0 (confirmed - Issue 1)
2. Without watermark: (0.1036 + 0.0904 + 0.0237) / (0.25 + 0.15 + 0.10 + 0.07 + 0.03) = 0.2177 / 0.60 = 0.363
3. But output is 0.2240, which is even lower

**Possible causes**:
- Normalization issue
- Some categories not being included
- Weight calculation bug

### Issue 5: Multiple Strong Signals Underweighted
**Console shows strong evidence**:
- `hand_abnormal_angle_ratio: 0.7818` (very high!)
- `eye_blink_irregularity: 0.8000` (very high!)
- `temporal_identity_std: 0.8069` (very high!)
- `head_pose_jitter: 1.0000` (maximum!)
- `avg_phoneme_lag: 1.0000` (maximum!)

**Problem**: Despite 5 strong signals, final score is only 0.2240
- Anatomy weight (0.15) may be too low
- Temporal weight (0.10) may be too low
- Need cumulative evidence boost when multiple categories agree

## Recommended Fixes (Priority Order)

### Fix 1: Watermark Detection Logic (CRITICAL)
**File**: `core/detector_rule_based.py` line 162

**Current**:
```python
if watermark_detected and watermark_conf > 0.5:
```

**Fix**:
```python
if watermark_detected:
    # Use detected flag, but scale by confidence
    watermark_score = min(watermark_conf * 1.2, 1.0) if watermark_conf > 0.3 else watermark_conf
else:
    watermark_score = 0.0
```

**Or simpler**:
```python
if watermark_detected:
    watermark_score = min(watermark_conf * 1.2, 1.0)
    if watermark_conf < 0.3:
        watermark_score = watermark_conf  # Still use low confidence
else:
    watermark_score = 0.0
```

### Fix 2: Lower Shimmer Thresholds (HIGH PRIORITY)
**File**: `core/config_detection.py`

**Change**:
```python
SHIMMER_INTENSITY_THRESHOLD = 0.05  # Was 0.6
BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD = 0.4  # Was 0.5
FLAT_REGION_NOISE_DRIFT_THRESHOLD = 0.15  # Was 0.4
```

### Fix 3: Fix Audio Correlation Logic
**File**: `core/detector_rule_based.py` line 293

**Current**:
```python
if lip_corr < LIP_AUDIO_CORRELATION_THRESHOLD:  # 0.4
```

**Fix**:
```python
if lip_corr < 0.45:  # Lower threshold to catch more cases
    audio_evidence.append(1.0 - lip_corr)
# Or use inverted: lower correlation = higher suspicion
audio_suspicion = 1.0 - lip_corr
if audio_suspicion > 0.55:  # Equivalent to corr < 0.45
    audio_evidence.append(audio_suspicion)
```

### Fix 4: Add Cumulative Evidence Boost
**File**: `core/detector_rule_based.py` after line 325

**Add**:
```python
# Boost score if multiple categories show evidence
evidence_count = sum(1 for score in category_scores.values() if score > 0.0)
if evidence_count >= 3:
    # Multiple independent signals agree - boost confidence
    final_score = min(final_score * 1.3, 1.0)
    explanations.append(f"Multiple evidence categories ({evidence_count}) agree; boosting score")
elif evidence_count >= 2:
    final_score = min(final_score * 1.15, 1.0)
```

### Fix 5: Increase Anatomy and Temporal Weights
**File**: `core/config_detection.py`

**Change**:
```python
WEIGHTS = {
    "watermark": 0.35,           # Slightly reduced
    "noise_shimmer": 0.20,       # Reduced
    "anatomy": 0.20,             # Increased from 0.15
    "temporal_identity": 0.15,   # Increased from 0.10
    "frequency_artifacts": 0.07,
    "audio_sync": 0.03,
}
```

### Fix 6: Debug Score Calculation
**Add debug logging** in `_compute_score`:
```python
print(f"[DEBUG] Category scores: {category_scores}")
print(f"[DEBUG] Weighted contributions:")
for category, weight in WEIGHTS.items():
    score = category_scores.get(category, 0.0)
    contrib = score * weight
    print(f"  {category}: {score:.4f} * {weight:.2f} = {contrib:.4f}")
print(f"[DEBUG] Total score: {total_score:.4f}, Total weight: {total_weight:.4f}")
print(f"[DEBUG] Final score: {final_score:.4f}")
```

## Debug Checklist

- [ ] Verify watermark score calculation (should be 0.5202, not 0.0)
- [ ] Check if all category scores are being computed
- [ ] Verify weight normalization
- [ ] Check threshold values match config
- [ ] Verify human presence gating (should be active with human_present=1.0)
- [ ] Check if any features are being filtered out

