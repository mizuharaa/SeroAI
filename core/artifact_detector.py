"""Additional computer vision heuristics for artifact detection."""

from __future__ import annotations

import cv2
import numpy as np
from typing import Dict, List

from core.media_io import extract_frames


def _compute_edge_density(gray_frame: np.ndarray) -> float:
    edges = cv2.Canny(gray_frame, 100, 200)
    return float(np.count_nonzero(edges)) / float(edges.size)


def _compute_high_freq_energy(gray_frame: np.ndarray) -> float:
    return float(cv2.Laplacian(gray_frame, cv2.CV_64F).var())


def _compute_saturation(frame_rgb: np.ndarray) -> float:
    hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    # Explicit dtype for type checkers and stable casting
    return float(np.mean(saturation, dtype=np.float64)) / 255.0


def _compute_frequency_ratio(gray_frame: np.ndarray) -> float:
    resized = cv2.resize(gray_frame, (128, 128))
    norm = resized.astype(np.float32) / 255.0
    dct = cv2.dct(norm)
    low_freq = np.sum(np.abs(dct[:16, :16]))
    total_energy = np.sum(np.abs(dct))
    high_freq = total_energy - low_freq
    if total_energy <= 1e-6:
        return 0.0
    return float(high_freq / total_energy)


def analyze_visual_artifacts(
    video_path: str,
    max_frames: int = 45,
    target_fps: int = 12
) -> Dict:
    """Analyze video for edge and color inconsistencies indicative of deepfakes."""
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
    if not frames:
        return {
            'edge_artifact_score': 0.5,
            'texture_inconsistency': 0.5,
            'color_anomaly_score': 0.5,
            'frame_samples': 0
        }

    edge_densities: List[float] = []
    high_freq_energies: List[float] = []
    saturations: List[float] = []
    temporal_edge_diffs: List[float] = []
    freq_ratios: List[float] = []

    prev_edge_density: float | None = None

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        edge_density = _compute_edge_density(gray)
        high_freq = _compute_high_freq_energy(gray)
        saturation = _compute_saturation(frame)

        edge_densities.append(edge_density)
        high_freq_energies.append(high_freq)
        saturations.append(saturation)
        freq_ratios.append(_compute_frequency_ratio(gray))

        if prev_edge_density is not None:
            temporal_edge_diffs.append(abs(edge_density - prev_edge_density))
        prev_edge_density = edge_density

    edge_variability = float(np.std(edge_densities)) if len(edge_densities) > 1 else 0.0
    high_freq_std = float(np.std(high_freq_energies)) if len(high_freq_energies) > 1 else 0.0
    high_freq_mean = float(np.mean(high_freq_energies)) if high_freq_energies else 0.0
    saturation_std = float(np.std(saturations)) if len(saturations) > 1 else 0.0
    temporal_edge = float(np.mean(temporal_edge_diffs)) if temporal_edge_diffs else 0.0
    freq_mean = float(np.mean(freq_ratios)) if freq_ratios else 0.0
    freq_std = float(np.std(freq_ratios)) if len(freq_ratios) > 1 else 0.0

    # Normalize heuristics to 0-1 range
    edge_artifact_score = float(np.clip(edge_variability * 3.0 + temporal_edge * 2.0, 0.0, 1.0))
    texture_inconsistency = float(
        np.clip((high_freq_std / (high_freq_mean + 1e-6)) * 1.5, 0.0, 1.0)
    )
    color_anomaly_score = float(np.clip(saturation_std * 4.0, 0.0, 1.0))
    freq_artifact_score = float(np.clip((freq_mean * 1.5) + (freq_std * 4.0), 0.0, 1.0))

    return {
        'edge_artifact_score': edge_artifact_score,
        'texture_inconsistency': texture_inconsistency,
        'color_anomaly_score': color_anomaly_score,
        'freq_artifact_score': freq_artifact_score,
        'frame_samples': len(frames)
    }


def analyze_visual_artifacts_image(image_path: str) -> Dict:
    """Analyze a single image for edge and color artifacts."""
    image = cv2.imread(image_path)
    if image is None:
        return {
            'edge_artifact_score': 0.5,
            'texture_inconsistency': 0.5,
            'color_anomaly_score': 0.5,
            'frame_samples': 0
        }

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

    edge_density = _compute_edge_density(gray)
    high_freq = _compute_high_freq_energy(gray)
    saturation = _compute_saturation(image_rgb)
    freq_ratio = _compute_frequency_ratio(gray)

    # Heuristics tuned for single images
    edge_artifact_score = float(np.clip(edge_density * 1.8, 0.0, 1.0))
    texture_inconsistency = float(np.clip(high_freq / (high_freq + 50.0), 0.0, 1.0))
    color_anomaly_score = float(np.clip(abs(saturation - 0.35) * 2.0, 0.0, 1.0))
    freq_artifact_score = float(np.clip(freq_ratio * 2.0, 0.0, 1.0))

    return {
        'edge_artifact_score': edge_artifact_score,
        'texture_inconsistency': texture_inconsistency,
        'color_anomaly_score': color_anomaly_score,
        'freq_artifact_score': freq_artifact_score,
        'frame_samples': 1
    }

