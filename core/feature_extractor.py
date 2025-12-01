"""
Modular feature extraction pipeline.

This module provides SpatialFeatures, TemporalFeatures, and AudioVisualFeatures
classes that extract specific feature sets from video frames and sequences.
"""

import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_io import extract_frames
from core.face_detect import FaceDetector
from features.anatomy_features import extract_anatomy_features
from features.motion_features import extract_motion_features
from features.frequency_features import extract_frequency_features
from features.audio_sync_features import extract_audio_sync_features
from features.watermark_features import extract_watermark_features


class SpatialFeatures:
    """Extract single-frame spatial features."""
    
    def __init__(self, face_detector: Optional[FaceDetector] = None):
        """Initialize with optional face detector."""
        self.face_detector = face_detector or FaceDetector()
    
    def extract_texture_artifact_score(
        self,
        frames: List[np.ndarray],
        face_regions: Optional[List[Tuple[int, int, int, int]]] = None
    ) -> float:
        """
        Compute texture artifact score by comparing high-frequency energy
        in face region vs surrounding background.
        
        Intuition: GAN/diffusion models often produce different frequency
        characteristics in face regions vs background, especially around edges.
        
        Computation:
        1. Extract face region and surrounding background region
        2. Compute 2D FFT for both regions
        3. Compare high-frequency energy (mid-to-high frequency bands)
        4. High ratio = suspicious (face has different texture characteristics)
        
        Returns: Score [0, 1] where higher = more artifacts
        """
        if len(frames) == 0:
            return 0.0
        
        scores = []
        
        for i, frame in enumerate(frames[:min(15, len(frames))]):
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            h, w = gray.shape
            
            # If face regions provided, use them; otherwise use center region
            if face_regions and i < len(face_regions) and face_regions[i]:
                fx, fy, fw, fh = face_regions[i]
                # Expand face region slightly
                fx = max(0, fx - fw // 4)
                fy = max(0, fy - fh // 4)
                fw = min(w - fx, int(fw * 1.5))
                fh = min(h - fy, int(fh * 1.5))
            else:
                # Default: center region
                fx, fy = w // 4, h // 4
                fw, fh = w // 2, h // 2
            
            # Extract face region
            face_region = gray[fy:fy+fh, fx:fx+fw]
            if face_region.size == 0:
                continue
            
            # Extract background region (surrounding area, avoiding face)
            bg_margin = 20
            bg_region = np.concatenate([
                gray[:fy-bg_margin, :].flatten() if fy > bg_margin else [],
                gray[fy+fh+bg_margin:, :].flatten() if fy+fh+bg_margin < h else [],
                gray[max(0, fy-bg_margin):min(h, fy+fh+bg_margin), :fx-bg_margin].flatten() if fx > bg_margin else [],
                gray[max(0, fy-bg_margin):min(h, fy+fh+bg_margin), fx+fw+bg_margin:].flatten() if fx+fw+bg_margin < w else []
            ])
            
            if len(bg_region) < 100:  # Not enough background
                continue
            
            # Reshape background to similar size as face for fair comparison
            bg_size = int(np.sqrt(len(bg_region)))
            bg_region_2d = bg_region[:bg_size*bg_size].reshape(bg_size, bg_size)
            bg_region_2d = cv2.resize(bg_region_2d, (fw, fh))
            
            # Compute 2D FFT
            face_fft = np.fft.fft2(face_region)
            face_fft_shift = np.fft.fftshift(face_fft)
            face_magnitude = np.abs(face_fft_shift)
            
            bg_fft = np.fft.fft2(bg_region_2d)
            bg_fft_shift = np.fft.fftshift(bg_fft)
            bg_magnitude = np.abs(bg_fft_shift)
            
            # Compute high-frequency energy (mid-to-high frequency bands)
            fh, fw = face_magnitude.shape
            center_h, center_w = fh // 2, fw // 2
            
            # High-frequency band: outer 30% of spectrum
            face_hf = face_magnitude[
                int(center_h - fh*0.15):int(center_h + fh*0.15),
                int(center_w - fw*0.15):int(center_w + fw*0.15)
            ]
            bg_hf = bg_magnitude[
                int(center_h - fh*0.15):int(center_h + fh*0.15),
                int(center_w - fw*0.15):int(center_w + fw*0.15)
            ]
            
            face_hf_energy = np.mean(face_hf)
            bg_hf_energy = np.mean(bg_hf)
            
            if bg_hf_energy > 0:
                # High ratio = face has different frequency characteristics (suspicious)
                ratio = face_hf_energy / (bg_hf_energy + 1e-6)
                # Normalize to [0, 1] - ratio > 2.0 is suspicious
                score = min(ratio / 2.0, 1.0)
                scores.append(score)
        
        return float(np.mean(scores)) if scores else 0.0


class TemporalFeatures:
    """Extract temporal/sequence features."""
    
    def __init__(self, face_detector: Optional[FaceDetector] = None):
        """Initialize with optional face detector."""
        self.face_detector = face_detector or FaceDetector()
    
    def extract_blink_anomaly_score(
        self,
        video_path: str,
        frames: Optional[List[np.ndarray]] = None
    ) -> float:
        """
        Compute blink anomaly score from blink rate and timing patterns.
        
        Intuition: Real humans blink at ~15-20 blinks/min with natural variation.
        AI-generated faces often have too few blinks, too regular patterns, or
        blinks that don't match speech/activity.
        
        Computation:
        1. Use existing anatomy features which include blink analysis
        2. Extract eye_blink_irregularity from anatomy features
        3. Normalize to [0, 1] score where higher = more anomalous
        
        Returns: Score [0, 1] where higher = more anomalous
        """
        try:
            # Use existing anatomy features
            anatomy_features = extract_anatomy_features(
                video_path,
                target_fps=8.0,
                max_frames=30
            )
            
            # Extract blink irregularity (already computed)
            blink_irregularity = anatomy_features.get('eye_blink_irregularity', 0.5)
            
            # Normalize to [0, 1] - typical real values are 0.2-0.4, higher is anomalous
            # Map: 0.0-0.3 = normal (0.0-0.2 score), 0.3-0.7 = moderate (0.2-0.7), >0.7 = high (0.7-1.0)
            if blink_irregularity < 0.3:
                score = blink_irregularity / 0.3 * 0.2
            elif blink_irregularity < 0.7:
                score = 0.2 + (blink_irregularity - 0.3) / 0.4 * 0.5
            else:
                score = 0.7 + min((blink_irregularity - 0.7) / 0.3, 1.0) * 0.3
            
            return float(np.clip(score, 0.0, 1.0))
        except Exception as e:
            print(f"[feature_extractor] Error computing blink anomaly: {e}")
            return 0.0
    
    def extract_landmark_jitter_score(
        self,
        video_path: str,
        frames: Optional[List[np.ndarray]] = None
    ) -> float:
        """
        Compute landmark jitter score from per-landmark standard deviation over time.
        
        Intuition: Facial landmarks should move smoothly. High jitter indicates
        frame-to-frame inconsistencies typical of AI generation.
        
        Computation:
        1. Use existing motion features which include temporal_identity_std
        2. Also use head_pose_jitter from motion features
        3. Combine these into a jitter score
        
        Returns: Score [0, 1] where higher = more jitter
        """
        try:
            # Use existing motion features
            motion_features = extract_motion_features(
                video_path,
                target_fps=12.0,
                max_frames=50,
                face_detector=self.face_detector
            )
            
            # Extract jitter-related features
            temporal_std = motion_features.get('temporal_identity_std', 0.5)
            head_jitter = motion_features.get('head_pose_jitter', 0.5)
            
            # Combine: average of both, normalized to [0, 1]
            # Typical real values: temporal_std ~0.1-0.3, head_jitter ~0.1-0.3
            # Higher values = more jitter
            combined_jitter = (temporal_std + head_jitter) / 2.0
            
            # Normalize: 0.0-0.2 = low (0.0-0.3 score), 0.2-0.5 = moderate (0.3-0.7), >0.5 = high (0.7-1.0)
            if combined_jitter < 0.2:
                score = combined_jitter / 0.2 * 0.3
            elif combined_jitter < 0.5:
                score = 0.3 + (combined_jitter - 0.2) / 0.3 * 0.4
            else:
                score = 0.7 + min((combined_jitter - 0.5) / 0.5, 1.0) * 0.3
            
            return float(np.clip(score, 0.0, 1.0))
        except Exception as e:
            print(f"[feature_extractor] Error computing landmark jitter: {e}")
            return 0.0
    
    def extract_pose_background_inconsistency(
        self,
        frames: List[np.ndarray],
        face_regions: Optional[List[Tuple[int, int, int, int]]] = None
    ) -> float:
        """
        Compute pose-background inconsistency by comparing head pose changes
        vs background motion.
        
        Intuition: When head rotates, background should shift accordingly.
        Inconsistent motion suggests the head was composited onto background.
        
        Computation:
        1. Track head pose (yaw, pitch, roll) over time
        2. Track background motion (optical flow in background regions)
        3. Compare head rotation direction with background motion direction
        4. High inconsistency = suspicious
        
        Returns: Score [0, 1] where higher = more inconsistent
        """
        if len(frames) < 3:
            return 0.0
        
        # Simplified implementation using optical flow
        # Full implementation would track head pose explicitly
        gray_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if len(f.shape) == 3 else f for f in frames[:min(20, len(frames))]]
        
        inconsistencies = []
        
        for i in range(len(gray_frames) - 1):
            # Compute optical flow
            h, w = gray_frames[i].shape
            flow = np.zeros((h, w, 2), dtype=np.float32)
            flow = cv2.calcOpticalFlowFarneback(
                gray_frames[i], gray_frames[i+1], flow, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Extract background region (assume corners are background)
            bg_regions = [
                flow[:h//4, :w//4],  # Top-left
                flow[:h//4, 3*w//4:],  # Top-right
                flow[3*h//4:, :w//4],  # Bottom-left
                flow[3*h//4:, 3*w//4:]  # Bottom-right
            ]
            
            # Compute average background motion direction
            bg_motions = []
            for bg_region in bg_regions:
                if bg_region.size > 0:
                    avg_motion = np.mean(bg_region, axis=(0, 1))
                    bg_motions.append(avg_motion)
            
            if len(bg_motions) > 0:
                avg_bg_motion = np.mean(bg_motions, axis=0)
                bg_magnitude = np.linalg.norm(avg_bg_motion)
                
                # High background motion with no corresponding head movement = suspicious
                # This is simplified - full version would track head pose
                if bg_magnitude > 5.0:  # Significant background motion
                    inconsistencies.append(0.5)  # Moderate inconsistency
                else:
                    inconsistencies.append(0.1)  # Low inconsistency
        
        return float(np.mean(inconsistencies)) if inconsistencies else 0.0


class AudioVisualFeatures:
    """Extract audio-visual synchronization features."""
    
    def extract_lip_sync_error(
        self,
        video_path: str,
        frames: List[np.ndarray],
        frame_timestamps: Optional[List[float]] = None
    ) -> float:
        """
        Compute lip-sync error from correlation between mouth-open ratio
        and audio energy over short windows.
        
        Intuition: Real speech has mouth movements synchronized with audio.
        AI-generated content often has misalignment.
        
        Computation:
        1. Extract audio energy in short windows (e.g., 100ms)
        2. Compute mouth-open ratio for corresponding frames
        3. Compute cross-correlation between audio energy and mouth-open ratio
        4. Low correlation = high sync error = suspicious
        
        Returns: Score [0, 1] where higher = more sync error
        """
        # Use existing audio sync features
        try:
            from features.audio_sync_features import extract_audio_sync_features
            audio_features = extract_audio_sync_features(video_path)
            
            # Extract lip sync correlation
            lip_corr = audio_features.get('lip_audio_correlation', 0.5)
            
            # Convert correlation to error score (low correlation = high error)
            sync_error = 1.0 - lip_corr
            
            return float(np.clip(sync_error, 0.0, 1.0))
        except Exception:
            return 0.0


class FeatureExtractor:
    """Main feature extractor that combines all feature modules."""
    
    def __init__(self):
        """Initialize feature extractors."""
        self.face_detector = FaceDetector()
        self.spatial = SpatialFeatures(self.face_detector)
        self.temporal = TemporalFeatures(self.face_detector)
        self.audio_visual = AudioVisualFeatures()
    
    def extract_all_features(
        self,
        video_path: str,
        max_frames: int = 50,
        frame_sample_rate: int = 1
    ) -> Dict[str, float]:
        """
        Extract all features from video.
        
        Returns dictionary with:
        - blink_anomaly_score
        - landmark_jitter_score
        - lip_sync_error
        - texture_artifact_score
        - pose_background_inconsistency
        - watermark_prob
        """
        # Extract frames
        frames = extract_frames(video_path, max_frames=max_frames)
        if not frames:
            return {}
        
        # Detect faces for each frame
        face_regions = []
        for frame in frames:
            faces = self.face_detector.detect_faces(frame)
            if len(faces) > 0:
                # Get largest face (bbox is (x, y, width, height))
                largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
                bbox = largest_face['bbox']
                face_regions.append((bbox[0], bbox[1], bbox[2], bbox[3]))
            else:
                face_regions.append(None)
        
        # Extract features
        features = {}
        
        # Spatial features
        features['texture_artifact_score'] = self.spatial.extract_texture_artifact_score(
            frames, face_regions
        )
        
        # Temporal features
        features['blink_anomaly_score'] = self.temporal.extract_blink_anomaly_score(
            video_path, frames
        )
        features['landmark_jitter_score'] = self.temporal.extract_landmark_jitter_score(
            video_path, frames
        )
        features['pose_background_inconsistency'] = self.temporal.extract_pose_background_inconsistency(
            frames, face_regions if face_regions else None
        )
        
        # Audio-visual features
        features['lip_sync_error'] = self.audio_visual.extract_lip_sync_error(
            video_path, frames
        )
        
        # Watermark (use existing watermark detection)
        try:
            watermark_features = extract_watermark_features(video_path)
            watermark_detected = watermark_features.get('watermark_detected', 0.0) > 0.5
            watermark_conf = watermark_features.get('watermark_confidence', 0.0)
            
            # Convert to probability score
            if watermark_detected and watermark_conf > 0.7:
                features['watermark_prob'] = min(watermark_conf, 1.0)
            else:
                features['watermark_prob'] = 0.0
        except Exception:
            features['watermark_prob'] = 0.0
        
        return features

