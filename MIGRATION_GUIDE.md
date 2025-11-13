# Migration Guide: New Deepfake Detection Pipeline

## Overview

The deepfake detection system has been completely rewritten to address the following issues:

1. **Blurry videos incorrectly flagged as AI-generated** - Fixed with quality gate
2. **Indecisive 40-60% scores** - Fixed with calibrated fusion model
3. **Missing watermark detection** - Now detects SORA, VEO, and other watermarks
4. **Poor accuracy on real vs synthetic content** - Improved with multiple forensic checks

## Key Changes

### 1. Quality Gate
- Detects blur, compression, low bitrate, and camera shake
- Routes low-quality media to robust detectors only
- Prevents false positives from blurry videos

### 2. Watermark Detection
- OCR-based detection of AI generator watermarks (SORA, VEO, RUNWAY, etc.)
- Strong signal when watermarks are detected
- Handles partial matches and variations

### 3. Forensic Analysis
- PRNU (sensor pattern noise) detection
- Temporal flicker analysis
- Codec artifact detection
- More robust than simple pixel stability

### 4. Calibrated Fusion
- Trained fusion model (or rule-based fallback)
- Calibrated probabilities for decisive outputs
- Verdict system: AI, REAL, UNSURE, ABSTAIN

### 5. Face Analysis
- MediaPipe-based face detection and tracking
- Face-specific deepfake detection (placeholder for future models)

## New API Response Format

```json
{
  "verdict": "AI" | "REAL" | "UNSURE" | "ABSTAIN",
  "probAi": 0.85,
  "overallScore": 85,
  "reasons": [
    {
      "name": "watermark",
      "weight": 0.4,
      "detail": "SORA watermark detected",
      "confidence": 0.95
    }
  ],
  "quality": {
    "status": "good" | "low",
    "issues": ["blur", "low_bitrate"]
  },
  "processingTime": 12.5
}
```

## Configuration

Thresholds can be adjusted in `core/config.py`:

- `AI_THRESHOLD = 0.80` - Probability above this = AI
- `REAL_THRESHOLD = 0.20` - Probability below this = REAL
- `BLUR_MIN = 60.0` - Minimum blur score for good quality
- `BRISQUE_MAX = 45.0` - Maximum BRISQUE score for good quality

## Installation

1. Install new dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR (for watermark detection):
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Or use: `winget install tesseract`

3. Install FFmpeg (for video analysis):
   - Windows: Download from https://ffmpeg.org/download.html
   - Or use: `winget install ffmpeg`

## Usage

The API remains the same:

```bash
python app.py
```

Navigate to `http://localhost:5000` and upload videos/images.

## Testing

Test with:
1. SORA watermarked video - should detect watermark and flag as AI
2. Blurry real video - should not falsely flag as AI
3. High-quality real video - should flag as REAL
4. High-quality AI video - should flag as AI

## Future Improvements

1. Train face deepfake models on DFDC, Celeb-DF datasets
2. Implement SyncNet-like audio-visual sync model
3. Add shot detection and object persistence tracking
4. Train fusion model on validation set
5. Add generator ID classification (SORA vs VEO vs etc.)

## Troubleshooting

### Import Errors
- Make sure all dependencies are installed
- Check that `core/` and `app/` directories exist

### OCR Not Working
- Install Tesseract OCR
- Set `TESSDATA_PREFIX` environment variable if needed

### MediaPipe Errors
- Install: `pip install mediapipe`
- May require Python 3.8-3.11

### FFmpeg Errors
- Install FFmpeg and add to PATH
- Audio analysis will default to neutral score if unavailable

