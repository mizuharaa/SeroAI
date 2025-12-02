# 🔗 SeroAI — Real-Time Deepfake Defense System

> **Advanced AI-powered deepfake detection with 5-axis forensic analysis, visual watermark verification, and holistic reasoning**

---

## 🎯 Featuring Advanced Deepfake Detection Technology

A production-ready deepfake detection system that analyzes videos and images using multiple detection axes, combining motion analysis, biological realism checks, scene logic verification, texture/frequency artifact detection, and advanced watermark/provenance verification. Built for trust & safety teams, journalists, and AI researchers who need explainable, accurate results.

---

## 🌐 Available in

**English** (current) • [**한국어**](README.ko.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md) • [**Español**](README.es.md) • [**Tiếng Việt**](README.vi.md) • [**Français**](README.fr.md)

---

## ✨ Key Features

### 🎯 **5-Axis Detection System**
- **Motion/Temporal Stability** (50% weight): Detects frame-to-frame inconsistencies, optical flow anomalies, and temporal artifacts
- **Biological/Physical Realism** (20% weight): Analyzes facial landmarks, blinking patterns, anatomical consistency, and body movements
- **Scene & Lighting Logic** (15% weight): Validates object persistence, physics consistency, lighting coherence, and shot boundaries
- **Texture & Frequency Artifacts** (10% weight): Identifies GAN fingerprints, spectral patterns, compression artifacts, and texture inconsistencies
- **Watermarks & Provenance** (5-50% weight): Visual logo matching for verified AI model watermarks (Sora, Gemini, Pika, Luma, Runway, HeyGen, D-ID)

### 🔍 **Advanced Detection Capabilities**
- **Visual Logo Matching**: Template matching, ORB feature matching, histogram comparison, and SSIM for verified watermark detection
- **Holistic Reasoning**: Combines multiple weak signals intelligently to reduce false positives and increase confidence
- **Semantic Impossibility Detection**: Flags logically impossible scenarios (e.g., deceased celebrities in new footage)
- **Dynamic Weight Adjustment**: Automatically switches to watermark-dominant weights (50%) when verified AI logos are detected
- **Quality Gate**: Pre-filters low-quality media to prevent false positives

### 🎨 **Modern Web Interface**
- **React + TypeScript + Vite**: Fast, responsive, and production-ready
- **Framer Motion Animations**: Smooth transitions and micro-interactions
- **Dark/Light Mode**: Automatic theme switching with system preference detection
- **Real-time Progress Tracking**: Live updates during analysis with per-method status indicators
- **Detailed Results Dashboard**: Comprehensive analysis breakdown with explanations

### 🛡️ **Production-Ready**
- **Local-First**: All processing happens on your device; no cloud uploads
- **Fast Processing**: 8-12 seconds typical runtime for standard videos
- **Configurable Thresholds**: Adjustable decision boundaries via JSON config
- **Structured Logging**: JSON logs with detailed analysis records
- **Terminal Output**: Real-time analysis results printed to console

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (3.10+ recommended)
- **Node.js 18+** and npm
- **FFmpeg** (for video processing)
- **Tesseract OCR** (optional, for text-based watermark detection)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. Create and activate virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Install Python dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Install frontend dependencies
cd webui
npm ci
npm run build
cd ..

# 5. Start the server
python app.py
```

The server will start on `http://localhost:5000`

### System Dependencies

**Windows (PowerShell)**:
```powershell
winget install ffmpeg
winget install tesseract  # Optional
```

**macOS**:
```bash
brew install ffmpeg
brew install tesseract  # Optional
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr  # Optional
```

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Detection Methods](#detection-methods)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🏗️ Architecture

### Project Structure

```
SeroAI/
├── app/                    # Flask application
│   ├── config.py          # Configuration settings
│   ├── service.py          # Analysis service layer
│   ├── analysis_manager.py # Job queue management
│   └── result_formatter.py # Result formatting
├── core/                   # Core detection modules
│   ├── detection_engine.py # Main 5-axis detection engine
│   ├── provenance_detector.py # Watermark/provenance detection
│   ├── logo_matcher.py     # Visual logo matching
│   ├── forensics.py        # Forensic analysis
│   ├── face_dynamics.py    # Facial analysis
│   ├── temporal.py         # Motion/temporal analysis
│   ├── scene_logic.py      # Scene consistency
│   └── fusion.py           # Result fusion
├── config/                  # Configuration files
│   ├── detector_thresholds.json # Decision thresholds
│   └── feature_stats.json  # Feature normalization stats
├── webui/                   # React frontend
│   ├── src/
│   │   ├── App.tsx         # Main application
│   │   ├── components/     # React components
│   │   └── styles/         # CSS styles
│   └── package.json
├── assets/                   # Static assets
│   └── reference_logos/    # AI model logo references
├── logs/                    # Analysis logs
│   └── analysis/           # JSON analysis logs
├── uploads/                 # Uploaded media files
├── models/                  # Trained models (optional)
└── scripts/                 # Utility scripts
```

### Detection Pipeline

```
1. Quality Gate
   └─> Assesses video quality, bitrate, compression
   
2. Frame Extraction
   └─> Samples frames for analysis
   
3. 5-Axis Analysis (Parallel)
   ├─> Motion/Temporal Stability
   ├─> Biological/Physical Realism
   ├─> Scene & Lighting Logic
   ├─> Texture & Frequency Artifacts
   └─> Watermarks & Provenance
   
4. Holistic Reasoning
   └─> Combines signals intelligently
   
5. Final Decision
   └─> AI-GENERATED / AUTHENTIC / UNCERTAIN
```

---

## 🔬 Detection Methods

### 1. Motion/Temporal Stability (Weight: 50%)

**Purpose**: Detects temporal inconsistencies and motion anomalies that indicate AI generation.

**Techniques**:
- **Optical Flow Analysis**: Tracks motion vectors between frames to detect unnatural movement patterns
- **Static Region Stability**: Monitors variance in static background regions for unexpected changes
- **Edge Consistency**: Checks for flickering or inconsistent edges across frames
- **Temporal Coherence**: Validates smooth transitions between frames

**Scoring**: `0.0` = Perfect temporal consistency → `1.0` = Severe temporal artifacts

**Key Indicators**:
- Face warping or "swimming" effects
- Background flickering while subject is static
- Inconsistent motion vectors
- Sudden jumps in pixel values

### 2. Biological/Physical Realism (Weight: 20%)

**Purpose**: Analyzes anatomical and biological consistency in faces and bodies.

**Techniques**:
- **Facial Landmark Detection**: Uses MediaPipe to track facial features
- **Blink Pattern Analysis**: Detects abnormal blinking frequency or patterns
- **Face Position Consistency**: Monitors face position and size stability
- **Symmetry Analysis**: Checks for unnatural facial asymmetry
- **Anatomical Proportions**: Validates realistic body/face proportions

**Scoring**: `0.0` = Natural biological patterns → `1.0` = Severe biological inconsistencies

**Key Indicators**:
- Uncanny smoothness or rubbery appearance
- Weird jawlines or off proportions
- Lifeless stare or abnormal blinking
- Stiff lips or unnatural expressions

### 3. Scene & Lighting Logic (Weight: 15%)

**Purpose**: Validates physical consistency of scenes, objects, and lighting.

**Techniques**:
- **Object Persistence**: Tracks objects across frames for consistency
- **Lighting Coherence**: Analyzes shadow and reflection consistency
- **Physics Validation**: Checks for physically impossible movements
- **Shot Boundary Detection**: Identifies scene cuts and transitions
- **Background Consistency**: Monitors static background elements

**Scoring**: `0.0` = Physically consistent scene → `1.0` = Severe scene/logic inconsistencies

**Key Indicators**:
- Inconsistent lighting or shadows
- Objects appearing/disappearing unnaturally
- Background static while subject moves
- Physically impossible movements

### 4. Texture & Frequency Artifacts (Weight: 10%)

**Purpose**: Detects GAN fingerprints and frequency-domain artifacts.

**Techniques**:
- **Frequency Domain Analysis**: FFT analysis to detect GAN signatures
- **Texture Consistency**: Monitors texture patterns across frames
- **Compression Artifact Detection**: Identifies unusual compression patterns
- **Spectral Analysis**: Analyzes frequency distributions

**Scoring**: `0.0` = Natural textures and frequencies → `1.0` = Severe texture/frequency artifacts

**Key Indicators**:
- Over-smooth skin or smeared textures
- Too-clean frames without natural noise
- AI struggles with hands, fingers, teeth, hairlines
- Unusual frequency patterns

### 5. Watermarks & Provenance (Weight: 5-50%)

**Purpose**: Detects AI model watermarks and verifies content provenance.

**Techniques**:
- **Visual Logo Matching**: Template matching, ORB features, histogram comparison, SSIM
- **OCR Text Detection**: Fallback for text-based overlays
- **Consistency Checking**: Validates watermark presence across frames
- **Provider Classification**: Identifies specific AI model (Sora, Gemini, Pika, etc.)

**Supported Providers**: Sora (OpenAI) • Gemini (Google) • Pika / Pika Labs • Luma / Luma AI • Runway • HeyGen • D-ID

**Scoring**: `0.0` = No watermark → `1.0` = Verified AI model watermark

**Weight Adjustment**:
- **Default**: 5% weight (no verified watermark)
- **Watermark-Dominant**: 50% weight (verified logo detected with ≥80% confidence)

---

## 📡 API Reference

### Endpoints

#### `POST /upload`
Upload a media file for analysis.

**Request**: `multipart/form-data` with `file` field

**Response**:
```json
{
  "filename": "uploaded_file.mp4",
  "original_name": "my_video.mp4"
}
```

#### `POST /analyze/start`
Start analysis job for uploaded file.

**Request**:
```json
{
  "filename": "uploaded_file.mp4",
  "originalName": "my_video.mp4"
}
```

**Response**:
```json
{
  "jobId": "uuid-string"
}
```

#### `GET /analyze/status/<jobId>`
Get analysis job status and results.

**Response** (completed):
```json
{
  "status": "completed",
  "progress": 100.0,
  "result": {
    "motion_score": 0.42,
    "bio_physics_score": 0.65,
    "scene_logic_score": 0.16,
    "texture_freq_score": 0.37,
    "watermark_score": 0.00,
    "deepfake_probability": 0.40,
    "final_label": "UNCERTAIN",
    "overallScore": 40
  }
}
```

### CLI Usage

```bash
# Analyze a video file
python -m core.debug_infer --input path/to/video.mp4

# Extract features for training
python -m scripts.extract_features

# Train fusion model
python -m scripts.train_fusion
```

---

## ⚙️ Configuration

### Decision Thresholds

Edit `config/detector_thresholds.json`:

```json
{
  "ai_threshold": 0.50,
  "auth_threshold": 0.40,
  "version": "2.0.0"
}
```

**Thresholds**:
- `ai_threshold`: Probability ≥ this value → "AI-GENERATED"
- `auth_threshold`: Probability ≤ this value → "AUTHENTIC"
- Between thresholds → "UNCERTAIN"

### Axis Weights

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
    "watermark": 0.50
}
```

---

## 🛠️ Development

### Project Setup

```bash
# Install dependencies
python -m pip install -r requirements.txt
cd webui && npm ci && cd ..

# Run type checking
pyright

# Start development servers
python app.py  # Terminal 1
cd webui && npm run dev  # Terminal 2
```

### Code Structure

- **`core/detection_engine.py`**: Main 5-axis detection engine
- **`core/provenance_detector.py`**: Watermark/provenance detection
- **`core/logo_matcher.py`**: Visual logo matching implementation
- **`app/service.py`**: Service layer for analysis
- **`webui/src/App.tsx`**: React frontend application

### Building Frontend

```bash
cd webui
npm run build
```

Production build outputs to `webui/dist/`.

---

## 🐛 Troubleshooting

### Common Issues

| Symptom | Solution |
|---------|----------|
| Analysis stuck at 10% | Check terminal for errors, verify video file is valid, ensure FFmpeg is installed |
| "No fusion model found" | Normal; system uses rule-based detection by default. Train with `python -m scripts.train_fusion` |
| OCR slow performance | Verify Tesseract OCR is installed, reduce frame sampling |
| Theme toggle flashes | Clear browser cache, check browser console for errors |
| Import errors | Ensure virtual environment is activated, reinstall requirements |

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Performance

**Typical Runtime**:
- Short video (10-30s): **8-12 seconds**
- Medium video (1-2min): **15-25 seconds**
- Long video (5+ min): **30-60 seconds**

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with tests
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Open a Pull Request

### Areas for Contribution

- Additional AI model logo references
- New detection methods
- Performance optimizations
- Documentation improvements
- UI/UX enhancements
- Test coverage

---

## 📄 License

**MIT** © 2025 SeroAI Contributors

See `LICENSE` file for details.

---

## 🗺️ Roadmap

- [ ] GPU-accelerated face/scene models
- [ ] Streaming mode for live cameras
- [ ] Expanded watermark OCR (Gemini, Pika, KLING)
- [ ] Tamper-evident overlay detection
- [ ] Signed verdict payloads for audit trails
- [ ] API rate limiting and authentication
- [ ] Batch processing support
- [ ] Real-time video stream analysis

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/<your-org-or-user>/SeroAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/<your-org-or-user>/SeroAI/discussions)

---

**Made with ❤️ for trust and safety teams, journalists, and AI researchers**

---

## 🏷️ Tags

**Python** • **3.9+** • **Deepfake Detection** • **Computer Vision** • **AI/ML** • **React** • **TypeScript** • **Flask** • **License** • **MIT**
