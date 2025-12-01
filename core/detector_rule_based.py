"""
Refactored rule-based deepfake detector with modular feature pipeline.

This detector uses:
- FeatureExtractor for modular feature extraction
- ScoreCalibrator for config-based normalization and scoring
- AnalysisLogger for structured logging
- VideoAnalysisResult dataclass for structured results

The public API analyze_video() is maintained for compatibility.
"""

import numpy as np
import sys
import os
from typing import Dict, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.types_analysis import VideoAnalysisResult, FeatureReason, FrameRecord
from core.feature_extractor import FeatureExtractor
from core.score_calibrator import ScoreCalibrator
from core.logger_analysis import AnalysisLogger
from core.media_io import extract_frames
from core.face_detect import FaceDetector


class SeroRuleBasedDetector:
    """
    Refactored rule-based detector with modular architecture.
    
    Maintains compatibility with existing API while using new
    feature extraction and scoring pipeline.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize detector.
        
        Args:
            config_path: Optional path to feature_stats.json config file
        """
        self.feature_extractor = FeatureExtractor()
        self.calibrator = ScoreCalibrator(config_path)
        self.logger = AnalysisLogger()
        self.face_detector = FaceDetector()
    
    def analyze_video(
        self,
        video_path: str,
        max_frames: int = 50,
        frame_sample_rate: int = 1,
        enable_logging: bool = True
    ) -> VideoAnalysisResult:
        """
        Analyze video and return structured result.
        
        This is the main public API method.
        
        Args:
            video_path: Path to video file
            max_frames: Maximum frames to extract
            frame_sample_rate: Sample every Nth frame
            enable_logging: Whether to write log file
        
        Returns:
            VideoAnalysisResult with all analysis data
        """
        # Initialize result
        result = VideoAnalysisResult(
            video_path=video_path,
            parameters={
                'max_frames': max_frames,
                'frame_sample_rate': frame_sample_rate,
                'decision_threshold': self.calibrator.decision_threshold
            }
        )
        
        # Extract features
        features = self.feature_extractor.extract_all_features(
            video_path,
            max_frames=max_frames,
            frame_sample_rate=frame_sample_rate
        )
        result.features = features
        
        # Normalize features
        normalized_features = self.calibrator.normalize_features(features)
        result.normalized_features = normalized_features
        
        # Compute deepfake score
        deepfake_score = self.calibrator.compute_deepfake_score(normalized_features)
        result.deepfake_score = deepfake_score
        
        # Get label
        label = self.calibrator.get_label(deepfake_score)
        result.label = label
        
        # Generate reasons (top contributing features)
        reasons = self._generate_reasons(features, normalized_features)
        result.reasons = reasons
        
        # Extract sample frame records for debugging
        frame_records = self._extract_frame_records(
            video_path,
            max_frames=min(10, max_frames)
        )
        result.frame_records = frame_records
        
        # Generate summary and log (always print to terminal)
        summary = self.logger.generate_summary(result)
        result.summary = summary
        
        # Always print to terminal
        if enable_logging:
            log_path, _ = self.logger.log_and_summarize(result)
        else:
            # Still print to terminal even if not saving to file
            log_path = "N/A (logging disabled)"
            self.logger.print_analysis(result, log_path)
        
        return result
    
    def detect(self, video_path: str) -> Dict:
        """
        Legacy API method for compatibility.
        
        Converts VideoAnalysisResult to old dictionary format.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with: score, label, explanations, features
        """
        # Always enable logging for terminal output
        result = self.analyze_video(video_path, enable_logging=True)
        
        # Convert to legacy format
        explanations = []
        for reason in result.reasons[:5]:  # Top 5 reasons
            direction = "increased" if reason.contribution > 0 else "decreased"
            explanations.append(
                f"{reason.name}: {direction} probability by {abs(reason.contribution):.3f}"
            )
        
        # Map label
        if result.label == "deepfake":
            legacy_label = "DEEPFAKE"
        elif result.label == "authentic":
            legacy_label = "REAL"
        else:
            legacy_label = "UNCERTAIN"
        
        return {
            'score': result.deepfake_score,
            'label': legacy_label,
            'explanations': explanations,
            'features': result.features
        }
    
    def _generate_reasons(
        self,
        features: Dict[str, float],
        normalized_features: Dict[str, float]
    ) -> List[FeatureReason]:
        """
        Generate list of contributing features (reasons).
        
        Args:
            features: Raw feature values
            normalized_features: Normalized feature values
        
        Returns:
            List of FeatureReason objects, sorted by contribution magnitude
        """
        reasons = []
        
        for feature_name, z_score in normalized_features.items():
            if feature_name in self.calibrator.weights:
                weight = self.calibrator.weights[feature_name]
                raw_value = features.get(feature_name, 0.0)
                
                # Contribution = weight * normalized_value
                contribution = weight * z_score
                
                reasons.append(FeatureReason(
                    name=feature_name,
                    contribution=contribution,
                    normalized_value=z_score,
                    raw_value=raw_value,
                    weight=weight
                ))
        
        # Sort by absolute contribution (most impactful first)
        reasons.sort(key=lambda r: abs(r.contribution), reverse=True)
        
        return reasons
    
    def _extract_frame_records(
        self,
        video_path: str,
        max_frames: int = 10
    ) -> List[FrameRecord]:
        """
        Extract sample per-frame records for debugging.
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to sample
            
        Returns:
            List of FrameRecord objects
        """
        frames = extract_frames(video_path, max_frames=max_frames)
        if not frames:
            return []
        
        frame_records = []
        
        # Get video FPS for timestamp calculation
        import cv2
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        cap.release()
        
        for i, frame in enumerate(frames):
            # Detect face
            faces = self.face_detector.detect_faces(frame)
            face_detected = len(faces) > 0
            
            # Extract basic features (simplified - would use full feature extraction)
            # Initialize with required fields
            mouth_open_ratio = None
            eye_aspect_ratio = None
            landmark_jitter = None
            
            # Add more detailed features if face detected
            if face_detected:
                # These would be extracted from full feature pipeline
                # For now, use placeholders
                mouth_open_ratio = 0.5  # Placeholder
                eye_aspect_ratio = 0.25  # Placeholder
                landmark_jitter = 0.1  # Placeholder
            
            record = FrameRecord(
                timestamp=i / fps,
                frame_idx=i,
                face_detected=face_detected,
                mouth_open_ratio=mouth_open_ratio,
                eye_aspect_ratio=eye_aspect_ratio,
                landmark_jitter=landmark_jitter,
                raw_values={}
            )
            
            frame_records.append(record)
        
        return frame_records
