# SeroAI — Real-Time Deepfake Defense Copilot

Pull signal-level evidence out of video files, fuse it with a supervised model, and ship trustworthy verdicts without ever leaving your device.

> 🌐 Available in: English (default) • 한국어 • 日本語 • 中文 • Español • Tiếng Việt • Français  
> 🛡️ Local-first • 🧠 ML-guided fusion • ⚡ 8–12s typical runtime

SeroAI watches every pixel, waveform, and watermark so AI agents, journalists, and trust & safety teams can act with confidence.

---

## Why Sero feels different

### 🚀 End-to-end verdict intelligence
- Quality gate, watermark OCR, forensic cues, facial dynamics, motion oddities, scene logic, and A/V sync—stitched together by a calibrated fusion model.
- Hard-evidence overrides (e.g., generator watermarks) prevent obvious AI clips from slipping through.
- Adaptive “real evidence” calming stops false alarms on talk shows, sports, and vlogs.

### 🧩 Component intelligence for detection teams
- Debug mode exposes per-branch logits so you can understand *why* a clip was flagged.
- Feedback loop assigns small, bounded weights based on analyst input—useful but never dominant.
- Hard AI test suite ensures watermark/scene logic regressions are caught before release.

### 🎨 Frontend built for humans and agents
- Responsive React + Vite UI with light/dark modes, progress choreography, and a Stripe-style globe.
- Detect marquee, schools carousel, and animated dashboard hero convince stakeholders instantly.
- Zero cloud upload: you keep the source files; Sero only serves results on localhost.

---

## Quick start (Windows PowerShell)
```powershell
# 1) Clone
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2) Python env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3) Optional system deps
# winget install ffmpeg
# winget install tesseract

# 4) Frontend build
cd webui
npm ci
npm run build
cd ..

# 5) Run everything
python app.py
# http://localhost:5000
```
💡 Frontend dev workflow: `npm run dev` inside `webui` while `python app.py` continues to serve the API.

---

## Pipeline anatomy
| Stage | What it checks | Module |
| --- | --- | --- |
| Quality Gate | Blur, bitrate, compression, shake | `core/media_io.py`, `app/config.py` |
| Watermark OCR | Sora / Runway / Imagen / custom lexicon | `core/watermark_ocr_v2.py` |
| Forensics | PRNU proxy, flicker, codec residue | `core/forensics.py` |
| Face Dynamics | Landmarks, blinking, symmetry | `core/face_dynamics.py` |
| Temporal | Optical flow oddity, rPPG drift | `core/temporal.py` |
| Scene Logic | Shot boundaries, object persistence | `core/scene_logic.py` |
| Audio-Visual Sync | Lip-to-audio alignment | `core/audio_visual.py` |
| Fusion | Rule-based + logistic regression blend | `core/fusion.py` |

Progress events map to the UI so the six-step card stack always fills from top to bottom.

---

## What the UI gives you
- **Live Analysis card**: looping progress rail, per-branch tiles, authenticity score, CTA footer.
- **Dashboard hero**: verdict gauge, branch evidence chips, stat tiles (detections, accuracy, runtime).
- **Global reach**: Stripe-inspired globe with orbits, ripple nodes, and marquee partners.
- **Feedback module**: analysts mark “Real / AI” and leave notes; keywords influence metric weights cautiously.

---

## Core commands & API
| Purpose | Endpoint / Command |
| --- | --- |
| Upload media | `POST /upload` (form-data `file`) |
| Start analysis | `POST /analyze/start` → `{ jobId }` |
| Poll status | `GET /analyze/status/<jobId>` |
| Serve UI | Flask root → `webui/dist/index.html` |
| Local file | `GET /uploads/<filename>` |

CLI helpers:
```bash
python -m scripts.extract_features        # build training CSVs
python -m scripts.patch_temporal_features # repair flow/rPPG columns
python -m scripts.train_fusion            # train + calibrate fusion model
python -m core.debug_infer --input path/to/video.mp4
```

---

## Configuration & tuning
- `app/config.py`: quality thresholds, hard-evidence logits, progress milestones.
- `core/*`: frame budgets, sampling strategies, heuristics per branch.
- `webui/src/App.tsx`: theme logic, hero animation, marquee content.
- `tailwind.config.js`: custom gradients + dark-mode class setup.

Tips:
- Lower frame budgets for speed-sensitive deployments.
- Relax or tighten real-evidence calming thresholds in `core/fusion.py` depending on your false-positive appetite.
- Extend the watermark lexicon dictionary when new generators ship.

---

## Troubleshooting cheat-sheet
| Symptom | Fix |
| --- | --- |
| Theme toggle flashes | Ensure `webui/index.html` inline script runs before bundle; clear cache. |
| OCR slow | Verify Tesseract path; reduce frame/crop count in `watermark_ocr_v2`. |
| Stuck progress | Flask auto-reloader cleared in-memory jobs—restart server after edits. |
| “No fusion model found” | Train via `python -m scripts.train_fusion` or rename fallback `.pkl`. |
| RPPG NaNs | Run `scripts.patch_temporal_features.py` to backfill missing temporal columns. |

---

## Roadmap
- GPU-accelerated face/scene models for heavier deployments.
- Streaming mode for live cameras.
- Expanded watermark OCR (Gemini, Pika, KLING) + tamper-evident overlays.
- Signed verdict payloads for audit trails.

---

## License
MIT © 2025 SeroAI Contributors  
📝 Need help or want to contribute? Open an issue or drop feedback through the in-app button. SeroAI stays sharp thanks to you. 💡
