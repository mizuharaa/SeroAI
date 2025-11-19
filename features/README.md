# Feature-Based Ensemble Detection

This directory contains the modular feature extraction system for SeroAI's deepfake detection.

## Architecture

The system is organized into four main feature modules:

### 1. Motion Features (`motion_features.py`)
Extracts temporal consistency and motion-based features:
- **Constant motion pixels**: Detects rubbery/overly uniform motion patterns
- **Temporal identity consistency**: Measures face embedding stability over time
- **Optical flow statistics**: Mean/std of flow magnitude in face region
- **Head pose jitter**: Frame-to-frame pose change variance

### 2. Anatomy Features (`anatomy_features.py`)
Uses MediaPipe to check for anatomical inconsistencies:
- **Hand skeleton**: Missing/merged fingers, abnormal joint angles
- **Mouth abnormalities**: Unrealistic opening, extreme mouth shapes
- **Eye blink patterns**: Blink rate and irregularity
- **Lip movement smoothness**: Temporal consistency of lip motion

### 3. Frequency Features (`frequency_features.py`)
Analyzes frequency and texture artifacts:
- **High/low frequency energy**: DCT-based frequency analysis
- **Boundary artifacts**: Artifacts near face edges
- **Frequency energy ratio**: Ratio of high to low frequency components

### 4. Audio Sync Features (`audio_sync_features.py`)
Checks audio-visual synchronization (if audio present):
- **Lip-audio correlation**: Correlation between mouth opening and audio energy
- **Phoneme lag**: Average lag between audio phonemes and mouth movement
- **Sync consistency**: Consistency of sync over time

## Usage

### Extract All Features

```python
from features.feature_extractor import extract_all_features

features = extract_all_features(
    video_path='path/to/video.mp4',
    enable_motion=True,
    enable_anatomy=True,
    enable_frequency=True,
    enable_audio_sync=True,
    enable_hand_analysis=True
)
```

### Use Individual Modules

```python
from features.motion_features import extract_motion_features
from features.anatomy_features import extract_anatomy_features

motion_features = extract_motion_features('video.mp4')
anatomy_features = extract_anatomy_features('video.mp4', enable_hand_analysis=True)
```

## Integration

The feature extractor is integrated into the main detection pipeline in `app/service.py`. If a trained ensemble model exists at `models/ensemble_classifier.pkl`, it will be used automatically. Otherwise, the system falls back to the existing fusion model.

## Training

See `scripts/train_ensemble.py` for training the ensemble classifier on your dataset.

## Debugging

Use the debug scripts to test individual feature modules:
- `scripts/debug_motion_features.py`
- `scripts/debug_anatomy_features.py`

