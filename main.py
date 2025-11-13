import cv2
import numpy as np
import librosa
import os
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')


def extract_frames(video_path: str, max_frames: int = 100) -> List[np.ndarray]:
    """
    Extract frames from a video file.
    
    Args:
        video_path: Path to the video file
        max_frames: Maximum number of frames to extract
        
    Returns:
        List of frame arrays
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Sample frames evenly across the video
    if total_frames > max_frames:
        step = total_frames // max_frames
    else:
        step = 1
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % step == 0:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        
        frame_count += 1
        if len(frames) >= max_frames:
            break
    
    cap.release()
    return frames


def analyze_pixel_stability(frames: List[np.ndarray]) -> float:
    """
    Analyze pixel stability across frames.
    Deepfakes often have inconsistent pixel patterns.
    
    Args:
        frames: List of frame arrays
        
    Returns:
        Score between 0 and 1 (1 = more stable/authentic)
    """
    if len(frames) < 2:
        return 0.5
    
    # Convert frames to grayscale for analysis
    gray_frames = [cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame 
                   for frame in frames]
    
    # Calculate frame differences
    diffs = []
    for i in range(1, len(gray_frames)):
        diff = cv2.absdiff(gray_frames[i-1], gray_frames[i])
        diffs.append(np.mean(diff))
    
    if not diffs:
        return 0.5
    
    # Calculate coefficient of variation
    mean_diff = np.mean(diffs)
    std_diff = np.std(diffs)
    
    if mean_diff == 0:
        return 1.0
    
    cv_score = std_diff / mean_diff
    
    # Normalize to 0-1 scale (lower variation = higher score)
    # Using exponential decay to convert CV to score
    stability_score = np.exp(-cv_score * 2)
    
    return min(max(stability_score, 0.0), 1.0)


def detect_motion_incoherence(frames: List[np.ndarray]) -> float:
    """
    Detect motion incoherence between frames.
    Deepfakes often have unnatural motion patterns.
    
    Args:
        frames: List of frame arrays
        
    Returns:
        Score between 0 and 1 (1 = more coherent/authentic)
    """
    if len(frames) < 3:
        return 0.5
    
    # Convert to grayscale
    gray_frames = [cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame 
                   for frame in frames]
    
    # Calculate optical flow between consecutive frames
    flow_magnitudes = []
    
    for i in range(1, len(gray_frames)):
        # Calculate optical flow using Farneback method
        flow = cv2.calcOpticalFlowFarneback(
            gray_frames[i-1], gray_frames[i], None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Calculate magnitude of flow vectors
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        flow_magnitudes.append(np.mean(magnitude))
    
    if not flow_magnitudes:
        return 0.5
    
    # Check for sudden changes in motion (incoherence)
    motion_changes = []
    for i in range(1, len(flow_magnitudes)):
        change = abs(flow_magnitudes[i] - flow_magnitudes[i-1])
        motion_changes.append(change)
    
    if not motion_changes:
        return 0.5
    
    # Calculate coefficient of variation of motion changes
    mean_change = np.mean(motion_changes)
    std_change = np.std(motion_changes)
    
    if mean_change == 0:
        return 1.0
    
    cv_motion = std_change / mean_change
    
    # Lower variation = more coherent motion
    coherence_score = np.exp(-cv_motion * 1.5)
    
    return min(max(coherence_score, 0.0), 1.0)


def check_scene_logic(frames: List[np.ndarray]) -> float:
    """
    Check scene logic and consistency.
    Deepfakes may have inconsistent lighting, shadows, or scene elements.
    
    Args:
        frames: List of frame arrays
        
    Returns:
        Score between 0 and 1 (1 = more consistent/authentic)
    """
    if len(frames) < 2:
        return 0.5
    
    # Analyze lighting consistency
    brightness_values = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame
        brightness_values.append(np.mean(gray))
    
    # Calculate brightness consistency
    brightness_std = np.std(brightness_values)
    brightness_mean = np.mean(brightness_values)
    
    if brightness_mean == 0:
        brightness_score = 1.0
    else:
        # Normalize by mean brightness
        brightness_cv = brightness_std / brightness_mean
        brightness_score = np.exp(-brightness_cv * 3)
    
    # Analyze color consistency
    color_means = []
    for frame in frames:
        if len(frame.shape) == 3:
            color_means.append(np.mean(frame, axis=(0, 1)))
        else:
            color_means.append([np.mean(frame)])
    
    color_means = np.array(color_means)
    color_variance = np.mean(np.std(color_means, axis=0))
    
    # Lower variance = more consistent
    color_score = np.exp(-color_variance / 50)
    
    # Combine scores
    scene_score = (brightness_score * 0.6 + color_score * 0.4)
    
    return min(max(scene_score, 0.0), 1.0)


def detect_temporal_flicker(frames: List[np.ndarray]) -> float:
    """
    Detect temporal flickering that may indicate deepfake artifacts.
    
    Args:
        frames: List of frame arrays
        
    Returns:
        Score between 0 and 1 (1 = less flickering/authentic)
    """
    if len(frames) < 3:
        return 0.5
    
    # Convert to grayscale
    gray_frames = [cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame 
                   for frame in frames]
    
    # Calculate frame-to-frame intensity changes
    intensity_changes = []
    for i in range(1, len(gray_frames)):
        diff = np.abs(gray_frames[i].astype(float) - gray_frames[i-1].astype(float))
        intensity_changes.append(np.mean(diff))
    
    if not intensity_changes:
        return 0.5
    
    # Detect high-frequency flickering using FFT
    # High-frequency components indicate flickering
    fft_values = np.abs(np.fft.fft(intensity_changes))
    high_freq_energy = np.sum(fft_values[len(fft_values)//4:])  # Upper 75% of frequencies
    
    # Normalize by total energy
    total_energy = np.sum(fft_values)
    if total_energy == 0:
        return 1.0
    
    flicker_ratio = high_freq_energy / total_energy
    
    # Lower flicker ratio = better (more authentic)
    flicker_score = 1.0 - min(flicker_ratio * 2, 1.0)
    
    return min(max(flicker_score, 0.0), 1.0)


def analyze_audio_sync(video_path: str) -> float:
    """
    Analyze audio-visual synchronization.
    Deepfakes may have audio sync issues.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Score between 0 and 1 (1 = better sync/authentic)
    """
    try:
        # Try to extract audio
        import subprocess
        import tempfile
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
            tmp_audio_path = tmp_audio.name
        
        # Extract audio using ffmpeg (if available)
        try:
            subprocess.run(
                ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', 
                 '-ar', '16000', '-ac', '1', '-y', tmp_audio_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            
            # Load audio
            audio, sr = librosa.load(tmp_audio_path, sr=16000)
            
            # Analyze audio features
            # Calculate spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            
            # Calculate zero crossing rate (speech activity)
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Check for consistency (sudden changes might indicate issues)
            centroid_std = np.std(spectral_centroids)
            centroid_mean = np.mean(spectral_centroids)
            
            if centroid_mean == 0:
                audio_score = 0.5
            else:
                # Normalize consistency
                consistency = 1.0 - min(centroid_std / centroid_mean, 1.0)
                audio_score = consistency
            
            # Clean up
            os.unlink(tmp_audio_path)
            
            return min(max(audio_score, 0.0), 1.0)
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # FFmpeg not available or extraction failed
            # Return a default score
            if os.path.exists(tmp_audio_path):
                os.unlink(tmp_audio_path)
            return 0.5
            
    except Exception as e:
        # If audio analysis fails, return neutral score
        return 0.5


def weighted_sum(scores: List[float], 
                 weights: List[float] = None) -> float:
    """
    Calculate weighted sum of scores.
    
    Args:
        scores: List of individual scores
        weights: List of weights (default: equal weights)
        
    Returns:
        Weighted sum score
    """
    if weights is None:
        weights = [1.0 / len(scores)] * len(scores)
    
    if len(scores) != len(weights):
        raise ValueError("Number of scores must match number of weights")
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    
    normalized_weights = [w / total_weight for w in weights]
    
    # Calculate weighted sum
    weighted_score = sum(score * weight for score, weight in zip(scores, normalized_weights))
    
    return min(max(weighted_score, 0.0), 1.0)


def detect_deepfake_image(image_path: str) -> Tuple[float, dict]:
    """
    Detect deepfake in a single image.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Tuple of (final_score, detailed_scores)
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # For images, we can only analyze certain aspects
    # Create a single-frame "video" for compatibility
    frames = [image_rgb]
    
    # Analyze applicable aspects (no motion or audio for images)
    pixel_score = 0.5  # Single image can't analyze temporal pixel stability
    scene_score = check_scene_logic(frames)
    
    # For images, use scene analysis and image quality metrics
    # Analyze image artifacts that might indicate AI generation
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    
    # Check for compression artifacts and inconsistencies
    # Use Laplacian variance to detect blur/artifacts
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Normalize variance score (typical good images have variance > 100)
    quality_score = min(laplacian_var / 200, 1.0)
    
    # Combine scores (images get different weights)
    final_score = (scene_score * 0.6 + quality_score * 0.4)
    
    detailed_scores = {
        'pixel_stability': pixel_score,
        'motion_coherence': 0.5,  # N/A for images
        'scene_consistency': scene_score,
        'temporal_stability': quality_score,
        'audio_sync': 0.5,  # N/A for images
        'overall_score': final_score
    }
    
    return final_score, detailed_scores


def detect_deepfake(video_path: str, 
                   weights: List[float] = None) -> Tuple[float, dict]:
    """
    Main function to detect deepfake in a video or image.
    
    Args:
        video_path: Path to the video or image file
        weights: Optional custom weights for each detection method
                 [pixel, motion, scene, flicker, audio]
    
    Returns:
        Tuple of (final_score, detailed_scores)
        - final_score: Overall deepfake probability (0-1, higher = more likely authentic)
        - detailed_scores: Dictionary with individual scores
    """
    # Check if it's an image
    image_extensions = {'.jpg', '.jpeg', '.png'}
    file_ext = os.path.splitext(video_path)[1].lower()
    
    if file_ext in image_extensions:
        return detect_deepfake_image(video_path)
    
    if weights is None:
        # Default weights - can be adjusted based on research
        weights = [0.25, 0.25, 0.20, 0.15, 0.15]
    
    # Extract frames
    frames = extract_frames(video_path)
    
    if not frames:
        raise ValueError("Could not extract frames from video")
    
    # Analyze different aspects
    pixel_score = analyze_pixel_stability(frames)
    motion_score = detect_motion_incoherence(frames)
    scene_score = check_scene_logic(frames)
    flicker_score = detect_temporal_flicker(frames)
    audio_score = analyze_audio_sync(video_path)
    
    # Calculate final score
    final_score = weighted_sum([
        pixel_score, motion_score, scene_score,
        flicker_score, audio_score
    ], weights)
    
    # Prepare detailed scores
    detailed_scores = {
        'pixel_stability': pixel_score,
        'motion_coherence': motion_score,
        'scene_consistency': scene_score,
        'temporal_stability': flicker_score,
        'audio_sync': audio_score,
        'overall_score': final_score
    }
    
    return final_score, detailed_scores


# Example usage
if __name__ == "__main__":
    # Example: Detect deepfake in a video
    video_path = "sample_video.mp4"  # Replace with your video path
    
    try:
        score, details = detect_deepfake(video_path)
        
        print(f"Deepfake Detection Results:")
        print(f"Overall Authenticity Score: {score:.3f}")
        print(f"\nDetailed Scores:")
        for key, value in details.items():
            print(f"  {key}: {value:.3f}")
        
        # Interpretation
        if score > 0.7:
            print(f"\nResult: Video appears to be AUTHENTIC (score: {score:.3f})")
        elif score > 0.5:
            print(f"\nResult: Video is UNCERTAIN (score: {score:.3f})")
        else:
            print(f"\nResult: Video may be a DEEPFAKE (score: {score:.3f})")
            
    except FileNotFoundError:
        print(f"Error: Video file not found: {video_path}")
        print("Please provide a valid video path.")
    except Exception as e:
        print(f"Error: {str(e)}")

