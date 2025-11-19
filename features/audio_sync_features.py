"""Audio-visual synchronization features for deepfake detection.

This module analyzes:
- Correlation between audio energy and mouth movement
- Phoneme-mouth lag detection
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
import mediapipe as mp

# Try to import audio processing libraries
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("[audio_sync_features] librosa not available; audio features will be limited")

try:
    import subprocess
    import tempfile
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False


def extract_audio_sync_features(
    video_path: str,
    target_fps: float = 12.0,
    max_frames: int = 50
) -> Dict[str, float]:
    """
    Extract audio-visual synchronization features.
    
    Args:
        video_path: Path to video file
        target_fps: Target FPS for frame sampling
        max_frames: Maximum number of frames to process
        
    Returns:
        Dictionary of scalar features:
        - lip_audio_correlation: Correlation between mouth opening and audio energy
        - avg_phoneme_lag: Average lag between audio phonemes and mouth movement
        - sync_consistency: Consistency of sync over time
        - has_audio: Whether audio was detected
    """
    # Check if audio exists
    has_audio = _check_audio_exists(video_path)
    
    if not has_audio:
        return {
            'lip_audio_correlation': 0.0,
            'avg_phoneme_lag': 0.0,
            'sync_consistency': 0.5,
            'has_audio': 0.0,
        }
    
    # Extract frames and audio
    frames = extract_frames(video_path, max_frames=max_frames, target_fps=target_fps, max_dim=512)
    
    if len(frames) < 3:
        return {
            'lip_audio_correlation': 0.0,
            'avg_phoneme_lag': 0.0,
            'sync_consistency': 0.5,
            'has_audio': 1.0,
        }
    
    # Extract mouth opening ratios
    mouth_ratios = _extract_mouth_ratios(frames)
    
    # Extract audio features
    audio_features = _extract_audio_features(video_path, len(frames), target_fps)
    
    if audio_features is None or len(mouth_ratios) == 0:
        return {
            'lip_audio_correlation': 0.0,
            'avg_phoneme_lag': 0.0,
            'sync_consistency': 0.5,
            'has_audio': 1.0,
        }
    
    # Compute correlation
    lip_audio_correlation = _compute_correlation(mouth_ratios, audio_features['energy'])
    
    # Compute lag
    avg_phoneme_lag = _compute_phoneme_lag(mouth_ratios, audio_features['energy'], target_fps)
    
    # Compute consistency
    sync_consistency = _compute_sync_consistency(mouth_ratios, audio_features['energy'])
    
    return {
        'lip_audio_correlation': float(lip_audio_correlation),
        'avg_phoneme_lag': float(avg_phoneme_lag),
        'sync_consistency': float(sync_consistency),
        'has_audio': 1.0,
    }


def _check_audio_exists(video_path: str) -> bool:
    """Check if video has audio track."""
    if not HAS_FFMPEG:
        return False
    
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0 and b'audio' in result.stdout
    except Exception:
        return False


def _extract_mouth_ratios(frames: List[np.ndarray]) -> List[float]:
    """Extract mouth opening ratios from frames."""
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    mouth_ratios = []
    
    try:
        for frame in frames:
            results = face_mesh.process(frame)
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                h, w = frame.shape[:2]
                
                # Mouth landmarks
                MOUTH_TOP = 13
                MOUTH_BOTTOM = 14
                MOUTH_LEFT = 78
                MOUTH_RIGHT = 308
                
                try:
                    top = landmarks[MOUTH_TOP]
                    bottom = landmarks[MOUTH_BOTTOM]
                    left = landmarks[MOUTH_LEFT]
                    right = landmarks[MOUTH_RIGHT]
                    
                    vertical = abs(top.y - bottom.y) * h
                    horizontal = abs(left.x - right.x) * w
                    
                    if horizontal > 1e-6:
                        ratio = vertical / horizontal
                        mouth_ratios.append(ratio)
                except (IndexError, AttributeError):
                    continue
    finally:
        face_mesh.close()
    
    return mouth_ratios


def _extract_audio_features(video_path: str, num_frames: int, fps: float) -> Optional[Dict]:
    """Extract audio features (MFCCs, energy) aligned with frames."""
    if not HAS_LIBROSA or not HAS_FFMPEG:
        return None
    
    try:
        # Extract audio using ffmpeg
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
            tmp_audio_path = tmp_audio.name
        
        subprocess.run(
            ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
             '-ar', '16000', '-ac', '1', '-y', tmp_audio_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=30
        )
        
        # Load audio
        audio, sr = librosa.load(tmp_audio_path, sr=16000)
        
        # Clean up
        os.unlink(tmp_audio_path)
        
        # Compute frame-aligned features
        frame_duration = 1.0 / fps
        frame_length = int(sr * frame_duration)
        hop_length = frame_length
        
        # Energy per frame
        energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # MFCCs (for phoneme-like features)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, hop_length=hop_length)
        
        # Trim to match number of frames
        min_len = min(len(energy), num_frames)
        energy = energy[:min_len]
        mfccs = mfccs[:, :min_len]
        
        return {
            'energy': energy.tolist(),
            'mfccs': mfccs.tolist(),
            'sr': sr
        }
    
    except Exception as e:
        print(f"[audio_sync_features] Error extracting audio: {e}")
        return None


def _compute_correlation(mouth_ratios: List[float], audio_energy: List[float]) -> float:
    """Compute correlation between mouth opening and audio energy."""
    if len(mouth_ratios) < 3 or len(audio_energy) < 3:
        return 0.0
    
    # Align lengths
    min_len = min(len(mouth_ratios), len(audio_energy))
    mouth_ratios = mouth_ratios[:min_len]
    audio_energy = audio_energy[:min_len]
    
    # Normalize
    mouth_norm = (np.array(mouth_ratios) - np.mean(mouth_ratios)) / (np.std(mouth_ratios) + 1e-6)
    audio_norm = (np.array(audio_energy) - np.mean(audio_energy)) / (np.std(audio_energy) + 1e-6)
    
    # Compute correlation
    correlation = np.corrcoef(mouth_norm, audio_norm)[0, 1]
    
    # Normalize to [0, 1] (correlation is [-1, 1])
    normalized = (correlation + 1.0) / 2.0
    return float(np.clip(normalized, 0.0, 1.0))


def _compute_phoneme_lag(mouth_ratios: List[float], audio_energy: List[float], fps: float) -> float:
    """Compute average lag between audio phonemes and mouth movement."""
    if len(mouth_ratios) < 3 or len(audio_energy) < 3:
        return 0.0
    
    # Align lengths
    min_len = min(len(mouth_ratios), len(audio_energy))
    mouth_ratios = mouth_ratios[:min_len]
    audio_energy = audio_energy[:min_len]
    
    # Find peaks in audio energy (phoneme-like events)
    audio_peaks = []
    for i in range(1, len(audio_energy) - 1):
        if audio_energy[i] > audio_energy[i-1] and audio_energy[i] > audio_energy[i+1]:
            if audio_energy[i] > np.mean(audio_energy) + 0.5 * np.std(audio_energy):
                audio_peaks.append(i)
    
    # Find corresponding mouth opening peaks
    mouth_peaks = []
    for i in range(1, len(mouth_ratios) - 1):
        if mouth_ratios[i] > mouth_ratios[i-1] and mouth_ratios[i] > mouth_ratios[i+1]:
            if mouth_ratios[i] > np.mean(mouth_ratios) + 0.5 * np.std(mouth_ratios):
                mouth_peaks.append(i)
    
    if len(audio_peaks) == 0 or len(mouth_peaks) == 0:
        return 0.0
    
    # Compute lag: find closest mouth peak for each audio peak
    lags = []
    for audio_peak in audio_peaks[:5]:  # Limit to first 5 peaks
        closest_mouth = min(mouth_peaks, key=lambda x: abs(x - audio_peak))
        lag = (closest_mouth - audio_peak) / fps  # Lag in seconds
        lags.append(lag)
    
    if len(lags) == 0:
        return 0.0
    
    # Average lag (normalized)
    avg_lag = np.mean(np.abs(lags))
    # Normalize: typical lag is 0-200ms, so divide by 0.2
    normalized_lag = np.clip(avg_lag / 0.2, 0.0, 1.0)
    return float(normalized_lag)


def _compute_sync_consistency(mouth_ratios: List[float], audio_energy: List[float]) -> float:
    """Compute consistency of sync over time."""
    if len(mouth_ratios) < 3 or len(audio_energy) < 3:
        return 0.5
    
    # Align lengths
    min_len = min(len(mouth_ratios), len(audio_energy))
    mouth_ratios = mouth_ratios[:min_len]
    audio_energy = audio_energy[:min_len]
    
    # Compute local correlations in windows
    window_size = min(10, min_len // 3)
    if window_size < 3:
        return 0.5
    
    correlations = []
    for i in range(0, min_len - window_size, window_size // 2):
        window_mouth = mouth_ratios[i:i+window_size]
        window_audio = audio_energy[i:i+window_size]
        
        if len(window_mouth) >= 3 and len(window_audio) >= 3:
            mouth_norm = (np.array(window_mouth) - np.mean(window_mouth)) / (np.std(window_mouth) + 1e-6)
            audio_norm = (np.array(window_audio) - np.mean(window_audio)) / (np.std(window_audio) + 1e-6)
            
            corr = np.corrcoef(mouth_norm, audio_norm)[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
    
    if len(correlations) < 2:
        return 0.5
    
    # Consistency: low variance in correlations = consistent sync
    mean_corr = np.mean(correlations)
    std_corr = np.std(correlations)
    
    # Normalize: high mean and low std = consistent
    consistency = mean_corr * (1.0 - np.clip(std_corr, 0.0, 1.0))
    consistency = (consistency + 1.0) / 2.0  # Map from [-1, 1] to [0, 1]
    return float(np.clip(consistency, 0.0, 1.0))

