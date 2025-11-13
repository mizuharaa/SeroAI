"""Lightweight temporal cues: optical-flow oddity and rudimentary rPPG coherence."""
from __future__ import annotations

import cv2
import numpy as np
from typing import Dict, List, Tuple

from core.media_io import extract_frames


def optical_flow_oddity(video_path: str, max_pairs: int = 12) -> Dict:
    """Compute simple statistics over dense flow to flag temporal oddities.
    Returns {'oddity_score': float, 'mean_mag': float, 'var_mag': float}.
    """
    frames = extract_frames(video_path, max_frames=max_pairs + 1, target_fps=12, max_dim=512)
    if len(frames) < 2:
        return {'oddity_score': 0.5, 'mean_mag': 0.0, 'var_mag': 0.0}
    try:
        # TV-L1 may live in cv2.optflow or cv2 depending on build; method is `calc`, not `compute`
        tvl1 = None
        if hasattr(cv2, 'optflow') and hasattr(cv2.optflow, 'DualTVL1OpticalFlow_create'):  # type: ignore
            tvl1 = cv2.optflow.DualTVL1OpticalFlow_create()  # type: ignore
        elif hasattr(cv2, 'DualTVL1OpticalFlow_create'):
            tvl1 = cv2.DualTVL1OpticalFlow_create()  # type: ignore
        use_tvl1 = tvl1 is not None
    except Exception:
        tvl1 = None
        use_tvl1 = False
    mags: List[float] = []
    for i in range(1, len(frames)):
        a = cv2.cvtColor(frames[i - 1], cv2.COLOR_RGB2GRAY)
        b = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
        if use_tvl1 and tvl1 is not None:
            flow = tvl1.calc(a, b, None)  # TV-L1 API
        else:
            flow = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        mags.append(float(np.mean(mag)))
    mean_mag = float(np.mean(mags))
    var_mag = float(np.var(mags))
    # Heuristic: very high variance while mean remains low suggests flicker/temporal inconsistency
    oddity_score = float(np.clip((var_mag / (mean_mag + 1e-3)) * 0.5, 0.0, 1.0))
    return {'oddity_score': oddity_score, 'mean_mag': mean_mag, 'var_mag': var_mag}


def rppg_coherence(video_path: str, max_frames: int = 90) -> Dict:
    """Rudimentary rPPG proxy over full frame (face ROI unavailable here).
    This is a low-cost placeholder: returns {'rppg_score': float} where lower is more 'real'.
    """
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=20, max_dim=512)
    if len(frames) < 16:
        return {'rppg_score': 0.5}
    # Average green channel over center patch to build a signal
    greens: List[float] = []
    for f in frames:
        h, w = f.shape[:2]
        y1 = h // 4
        y2 = 3 * h // 4
        x1 = w // 4
        x2 = 3 * w // 4
        patch = f[y1:y2, x1:x2]
        greens.append(float(np.mean(patch[..., 1])))
    sig = np.array(greens, dtype=np.float32)
    sig = sig - np.mean(sig)
    if np.std(sig) < 1e-6:
        return {'rppg_score': 0.7}
    sig = sig / (np.std(sig) + 1e-6)
    # FFT power in plausible heart-band 0.7–4 Hz relative to total
    fft = np.abs(np.fft.rfft(sig))
    freqs = np.fft.rfftfreq(len(sig), d=1 / 20.0)
    band = (freqs >= 0.7) & (freqs <= 4.0)
    power_band = float(np.sum(fft[band]))
    power_total = float(np.sum(fft) + 1e-6)
    coherence = power_band / power_total  # higher coherence => more 'real'
    # Map to anomaly score where higher = more likely AI
    rppg_score = float(np.clip(1.0 - coherence * 2.0, 0.0, 1.0))
    return {'rppg_score': rppg_score}


