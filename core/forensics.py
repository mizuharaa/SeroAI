"""Forensic analysis: PRNU, flicker, codec artifacts."""

import cv2
import numpy as np
from typing import List, Dict
from scipy import signal
from scipy.fft import fft, fftfreq

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames


def compute_prnu_score(frames: List[np.ndarray]) -> float:
    """Compute PRNU (Photo Response Non-Uniformity) score.
    
    Real cameras have sensor-specific noise patterns. GAN videos show weaker PRNU.
    
    Args:
        frames: List of frames (RGB)
        
    Returns:
        PRNU score (higher = more likely real camera)
    """
    if len(frames) < 5:
        return 0.5
    
    # Convert to grayscale
    gray_frames = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) if len(f.shape) == 3 else f 
                   for f in frames]
    
    # Compute noise residuals using wavelet denoising
    residuals = []
    for gray in gray_frames[:20]:  # Sample first 20 frames
        # Simple high-pass filter to extract noise
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]])
        residual = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        residuals.append(residual)
    
    if not residuals:
        return 0.5
    
    # Compute cross-correlation between residuals (real cameras show consistent patterns)
    correlations = []
    for i in range(len(residuals) - 1):
        corr = np.corrcoef(residuals[i].flatten(), residuals[i+1].flatten())[0, 1]
        if not np.isnan(corr):
            correlations.append(abs(corr))
    
    if correlations:
        avg_correlation = np.mean(correlations)
        # Normalize to 0-1 scale
        prnu_score = min(avg_correlation * 2, 1.0)
        return float(prnu_score)
    
    return 0.5


def compute_flicker_score(frames: List[np.ndarray]) -> float:
    """Compute temporal flicker score using FFT.
    
    GAN videos often show periodic flickering artifacts.
    
    Args:
        frames: List of frames (RGB)
        
    Returns:
        Flicker score (higher = more flickering = more likely AI)
    """
    if len(frames) < 10:
        return 0.5
    
    # Convert to grayscale
    gray_frames = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) if len(f.shape) == 3 else f 
                   for f in frames]
    
    # Compute frame-to-frame intensity changes
    intensity_changes = []
    for i in range(1, len(gray_frames)):
        diff = np.abs(gray_frames[i].astype(float) - gray_frames[i-1].astype(float))
        intensity_changes.append(np.mean(diff))
    
    if len(intensity_changes) < 5:
        return 0.5
    
    # FFT to detect periodic flickering
    fft_values = np.abs(fft(intensity_changes))
    freqs = fftfreq(len(intensity_changes))
    
    # High-frequency components indicate flickering
    high_freq_mask = np.abs(freqs) > 0.1  # Frequencies > 10% of Nyquist
    high_freq_energy = np.sum(fft_values[high_freq_mask])
    total_energy = np.sum(fft_values)
    
    if total_energy == 0:
        return 0.5
    
    flicker_ratio = high_freq_energy / total_energy
    
    # Higher flicker = more likely AI
    flicker_score = min(flicker_ratio * 3, 1.0)
    return float(flicker_score)


def compute_codec_artifacts(frames: List[np.ndarray]) -> float:
    """Detect codec compression artifacts.
    
    GAN videos may show inconsistent compression patterns.
    
    Args:
        frames: List of frames (RGB)
        
    Returns:
        Codec artifact score (higher = more artifacts = more likely AI)
    """
    if len(frames) < 5:
        return 0.5
    
    # Convert to grayscale
    gray_frames = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) if len(f.shape) == 3 else f 
                   for f in frames]
    
    # Analyze DCT block artifacts (JPEG/MPEG compression)
    block_scores = []
    block_size = 8
    
    for gray in gray_frames[:20]:  # Sample frames
        h, w = gray.shape
        h_blocks = h // block_size
        w_blocks = w // block_size
        
        # Compute variance within each block (compression creates uniform blocks)
        block_variances = []
        for i in range(h_blocks):
            for j in range(w_blocks):
                block = gray[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size]
                block_var = np.var(block)
                block_variances.append(block_var)
        
        if block_variances:
            # Low variance blocks indicate compression artifacts
            low_var_ratio = sum(1 for v in block_variances if v < 10) / len(block_variances)
            block_scores.append(low_var_ratio)
    
    if block_scores:
        avg_block_score = np.mean(block_scores)
        # Higher score = more compression artifacts = possibly AI
        return float(avg_block_score)
    
    return 0.5


def analyze_forensics(video_path: str) -> Dict:
    """Run all forensic analyses.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with forensic scores
    """
    # Extract frames
    frames = extract_frames(video_path, max_frames=60, target_fps=15, max_dim=512)
    
    if not frames:
        return {
            'prnu_score': 0.5,
            'flicker_score': 0.5,
            'codec_score': 0.5,
            'error': 'Could not extract frames'
        }
    
    prnu = compute_prnu_score(frames)
    flicker = compute_flicker_score(frames)
    codec = compute_codec_artifacts(frames)
    
    return {
        'prnu_score': prnu,
        'flicker_score': flicker,
        'codec_score': codec
    }

