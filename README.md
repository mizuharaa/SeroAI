# SeroAI
# SeroAI

AI-powered deepfake detection that restores trust in digital media.  
Local-first (no cloud uploads), modern UI, and a fused multi-signal pipeline for accurate, fast results.

- Backend: Python + Flask
- Frontend: React + Vite + TypeScript
- OS: Windows-first (works cross‑platform with Python 3.10–3.11 and Node 18+)

## Features

- Multiple detection signals fused for a calibrated verdict:
  - Quality gate (blur, compression, bitrate, camera shake)
  - Watermark OCR (e.g., Sora, VEO, Runway) with robust corner-zone focus
  - Forensics (PRNU proxy, flicker, codec artifacts)
  - Face detection/tracking and face dynamics (mouth/eyes symmetry heuristics)
  - Temporal cues (optical-flow oddity, rPPG coherence)
  - Scene logic checks (shot-breaks, background consistency vs. color jumps)
- Modern web UI with warm gradients, scroll re-triggered animations, and dark/light theme with persisted preference
- Local processing only; files never leave your machine
- Practical performance:
  - Smart frame sampling and downscaling for speed
  - Progress reporting that advances smoothly to 100%

## Quick start (Windows PowerShell)
hell
# 1) Clone your repo
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Install backend dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4) (Optional) Install FFmpeg (for audio-related features)
# winget install ffmpeg    or    choco install ffmpeg

# 5) (Optional) Install Tesseract OCR (for watermark detection)
# winget install tesseract    or download from https://github.com/UB-Mannheim/tesseract/wiki

# 6) Install frontend deps and build the UI
cd webui
npm ci
npm run build
cd ..

# 7) Start the server
python app.py

# 8) Open in your browser
# http://localhost:5000Tip: For frontend development with hot reload, run `npm run dev` in `webui` and keep `python app.py` running; the Flask app serves the built UI when `webui/dist` exists.

## Project structure

Tip: For frontend development with hot reload, run `npm run dev` in `webui` and keep `python app.py` running; the Flask app serves the built UI when `webui/dist` exists.

## API (JSON)

- POST `/upload`
  - Form-data: `file`
  - Returns: `{ filename, original_name }`
- POST `/analyze/start`
  - Body: `{ filename, originalName? }`
  - Returns: `{ success, jobId }`
- GET `/analyze/status/<jobId>`
  - Returns: `{ progress, currentStage, details, completed? }` plus interim results or final payload
- GET `/uploads/<filename>`
  - Serves your uploaded file (local temp storage)

The Flask root `/` serves `webui/dist/index.html` when built; otherwise it falls back to a minimal legacy template.

## Configuration

- Core thresholds: `core/config.py`
  - Quality thresholds (BLUR_MIN, BRISQUE_MAX, BITRATE_MIN, SHAKE_MAX)
  - Frame budgets: `MAX_FRAMES_TO_ANALYZE`, `TARGET_FPS`
- Pipeline thresholds & policy: `app/config.py`
  - Decision bands, scene logic time caps, watermark lexicon/policy
- Theme & UI animation are handled in `webui/src/App.tsx`

## Performance & accuracy

- Optimized frame sampling (indexed seeks) and downscaling to ~512–640 px
- Reduced per-stage frame budgets while preserving signal quality
- Monotonic progress reporting avoids the perceived “stall” around 82%
- You can further tune speed/accuracy:
  - Decrease frame budgets in `core/*` modules
  - Increase `SCENE["MAX_SECONDS"]` (or lower it) in `app/config.py`
  - Skip certain branches when quality is low (already applied to some)

## Troubleshooting

- “Theme toggle doesn’t stick”: the app persists theme in `localStorage` and applies class on first paint. Hard-refresh if needed.
- Tesseract not found: install it and ensure `pytesseract` can locate the binary (Windows paths are auto-checked).
- FFmpeg missing: install FFmpeg for audio-related features.
- Mediapipe errors: ensure Python 3.10–3.11 and a clean venv.
- Still slow on large videos: lower frame budgets or resolution caps in `core/*`.

## Development

- Type check (frontend):
 
  cd webui && npx tsc --noEmit
  - Build (frontend):
 
  cd webui && npm run build
  - Run backend:
 
  .\.venv\Scripts\Activate.ps1
  python app.py
  ## Roadmap

- Optional GPU-accelerated models for face/scene branches
- Better per-video adaptive sampling & time budgeting
- Expanded watermark lexicon and confidence model

## License

MIT © 2025 SeroAI Contributors
