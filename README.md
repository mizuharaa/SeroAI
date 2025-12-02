# SeroAI — Real-Time Deepfake Defense System

> **Advanced AI-powered deepfake detection with 5-axis forensic analysis, visual watermark verification, and holistic reasoning**

SeroAI is a production-ready deepfake detection system that analyzes videos and images using multiple detection axes, combining motion analysis, biological realism checks, scene logic verification, texture/frequency artifact detection, and advanced watermark/provenance verification. The system provides detailed, explainable results with configurable thresholds and weights.

---

## 🌟 Key Features

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

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Detection Methods](#detection-methods)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+** (3.10+ recommended)
- **Node.js 18+** and npm
- **FFmpeg** (for video processing)
- **Tesseract OCR** (optional, for text-based watermark detection)

### System Dependencies

#### Windows (PowerShell)
```powershell
# Install FFmpeg
winget install ffmpeg

# Install Tesseract OCR (optional)
winget install tesseract
```

#### macOS
```bash
# Install FFmpeg
brew install ffmpeg

# Install Tesseract OCR (optional)
brew install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
# Install FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg

# Install Tesseract OCR (optional)
sudo apt-get install tesseract-ocr
```

### Python Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install Python dependencies
python -m pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to webui directory
cd webui

# Install Node.js dependencies
npm ci

# Build production bundle
npm run build

# Return to project root
cd ..
```

---

## ⚡ Quick Start

### Start the Server

```bash
# From project root
python app.py
```

The server will start on `http://localhost:5000`

### Access the Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Click on the "Detect" section or navigate to `http://localhost:5000/#detect`
3. Upload a video or image file
4. Wait for analysis to complete (typically 8-12 seconds)
5. View detailed results with explanations

### Development Mode

For frontend development with hot-reload:

```bash
# Terminal 1: Start backend
python app.py

# Terminal 2: Start frontend dev server
cd webui
npm run dev
```

Frontend dev server runs on `http://localhost:5173` and proxies API requests to the backend.

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
│   ├── fusion.py           # Result fusion
│   └── ...
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
├── scripts/                 # Utility scripts
├── app.py                   # Flask entry point
└── requirements.txt        # Python dependencies
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

**Scoring**:
- `0.0` = Perfect temporal consistency (strongly authentic)
- `1.0` = Severe temporal artifacts (strongly AI-generated)

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

**Scoring**:
- `0.0` = Natural biological patterns (strongly authentic)
- `1.0` = Severe biological inconsistencies (strongly AI-generated)

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

**Scoring**:
- `0.0` = Physically consistent scene (strongly authentic)
- `1.0` = Severe scene/logic inconsistencies (strongly AI-generated)

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

**Scoring**:
- `0.0` = Natural textures and frequencies (strongly authentic)
- `1.0` = Severe texture/frequency artifacts (strongly AI-generated)

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

**Supported Providers**:
- Sora (OpenAI)
- Gemini (Google)
- Pika / Pika Labs
- Luma / Luma AI
- Runway
- HeyGen
- D-ID

**Scoring**:
- `0.0` = No watermark detected (neutral)
- `1.0` = Verified AI model watermark (strongly AI-generated)

**Weight Adjustment**:
- **Default**: 5% weight (no verified watermark)
- **Watermark-Dominant**: 50% weight (verified logo detected with ≥80% confidence)

**Key Indicators**:
- Verified AI model logo in video
- Consistent watermark across frames
- Text overlays (lower confidence, not verified)

---

## 📡 API Reference

### Endpoints

#### `POST /upload`
Upload a media file for analysis.

**Request**:
- Content-Type: `multipart/form-data`
- Body: `file` (video or image file)

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

**Response** (in progress):
```json
{
  "status": "processing",
  "progress": 45.5,
  "stage": "temporal",
  "completedStages": ["forensics", "artifact"]
}
```

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
    "overallScore": 40,
    "results": [...]
  }
}
```

#### `GET /uploads/<filename>`
Serve uploaded media file.

#### `GET /`
Serve web interface (redirects to `webui/dist/index.html`).

### CLI Usage

```bash
# Analyze a video file
python -m core.debug_infer --input path/to/video.mp4

# Extract features for training
python -m scripts.extract_features

# Train fusion model
python -m scripts.train_fusion

# Evaluate detector on dataset
python tools/evaluate_detector.py --dataset path/to/dataset
```

---

## ⚙️ Configuration

### Decision Thresholds

Edit `config/detector_thresholds.json`:

```json
{
  "ai_threshold": 0.50,
  "auth_threshold": 0.40,
  "version": "2.0.0",
  "notes": ">= 0.50 = AI-GENERATED, <= 0.40 = AUTHENTIC, else = UNCERTAIN"
}
```

**Thresholds**:
- `ai_threshold`: Probability ≥ this value → "AI-GENERATED"
- `auth_threshold`: Probability ≤ this value → "AUTHENTIC"
- Between thresholds → "UNCERTAIN"

### Axis Weights

Weights are defined in `core/detection_engine.py` and `core/provenance_detector.py`:

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

### Quality Gate Settings

Edit `app/config.py`:

```python
MIN_QUALITY_SCORE = 0.3  # Minimum quality threshold
MIN_BITRATE = 1000       # Minimum bitrate (kbps)
MAX_BLUR = 0.5           # Maximum blur threshold
```

### Reference Logos

Place transparent PNG logos in `assets/reference_logos/`:
- `sora.png`
- `gemini.png`
- `pika.png`
- `luma.png`
- `runway.png`
- `heygen.png`
- `did.png`

See `assets/reference_logos/README.md` for details.

---

## 🛠️ Development

### Project Setup

1. **Clone and install** (see [Installation](#installation))

2. **Set up development environment**:
```bash
# Install pre-commit hooks (if available)
pre-commit install

# Run type checking
pyright

# Run linting
pylint core/ app/
```

### Code Structure

- **`core/detection_engine.py`**: Main 5-axis detection engine
- **`core/provenance_detector.py`**: Watermark/provenance detection
- **`core/logo_matcher.py`**: Visual logo matching implementation
- **`app/service.py`**: Service layer for analysis
- **`webui/src/App.tsx`**: React frontend application

### Adding New Detection Methods

1. Create new module in `core/` (e.g., `core/my_detector.py`)
2. Implement detection logic returning score `[0, 1]`
3. Integrate into `core/detection_engine.py`
4. Add to 5-axis system or create new axis
5. Update weights in `core/provenance_detector.py`

### Testing

```bash
# Run unit tests (if available)
pytest tests/

# Test specific module
python -m core.debug_infer --input test_video.mp4

# Evaluate on dataset
python tools/evaluate_detector.py --dataset data/test/
```

### Building Frontend

```bash
cd webui
npm run build
```

Production build outputs to `webui/dist/`.

---

## 🐛 Troubleshooting

### Common Issues

#### Analysis Stuck at 10%
**Symptom**: Progress bar stops at 10% during analysis.

**Solution**:
- Check terminal for error messages
- Verify video file is valid and not corrupted
- Ensure FFmpeg is installed and accessible
- Check `logs/analysis/` for detailed error logs

#### "No fusion model found"
**Symptom**: Warning about missing fusion model.

**Solution**:
- This is normal; system uses rule-based detection by default
- To train a fusion model: `python -m scripts.train_fusion`
- Model is optional; rule-based detection works standalone

#### OCR Slow Performance
**Symptom**: Watermark detection takes too long.

**Solution**:
- Verify Tesseract OCR is installed
- Reduce frame sampling in `core/watermark_ocr_v2.py`
- Disable OCR if not needed (edit `core/provenance_detector.py`)

#### Theme Toggle Flashes
**Symptom**: Dark/light mode toggle causes flashing.

**Solution**:
- Clear browser cache
- Ensure `webui/index.html` inline script runs before bundle
- Check browser console for errors

#### Import Errors
**Symptom**: Module import errors when running.

**Solution**:
- Ensure virtual environment is activated
- Run `python -m pip install -r requirements.txt` again
- Check Python path includes project root

### Debug Mode

Enable verbose logging:

```python
# In app.py, set logging level
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Logs Location

- **Analysis Logs**: `logs/analysis/*.json`
- **Application Logs**: Check terminal output
- **Error Logs**: Terminal stderr

---

## 📊 Performance

### Typical Runtime

- **Short video (10-30s)**: 8-12 seconds
- **Medium video (1-2min)**: 15-25 seconds
- **Long video (5+ min)**: 30-60 seconds

### Optimization Tips

1. **Reduce Frame Budget**: Edit `core/media_io.py` to sample fewer frames
2. **Disable Optional Features**: Comment out unused detection methods
3. **Use GPU**: Install CUDA-enabled OpenCV for faster processing
4. **Parallel Processing**: Enable multiprocessing in `core/detection_engine.py`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes** with tests
4. **Commit**: `git commit -m "Add my feature"`
5. **Push**: `git push origin feature/my-feature`
6. **Open a Pull Request**

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow ESLint rules, use TypeScript strict mode
- **Commits**: Use conventional commit messages

### Areas for Contribution

- Additional AI model logo references
- New detection methods
- Performance optimizations
- Documentation improvements
- UI/UX enhancements
- Test coverage

---

## 📄 License

MIT © 2025 SeroAI Contributors

See `LICENSE` file for details.

---

## 🙏 Acknowledgments

- **MediaPipe**: Facial landmark detection
- **OpenCV**: Computer vision operations
- **React + Vite**: Frontend framework
- **Framer Motion**: Animation library
- **Flask**: Backend framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/<your-org-or-user>/SeroAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/<your-org-or-user>/SeroAI/discussions)
- **Email**: [Your email or support contact]

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

**Made with ❤️ for trust and safety teams, journalists, and AI researchers**
