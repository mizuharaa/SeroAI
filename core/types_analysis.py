"""
Type definitions and dataclasses for video analysis results.

This module defines the structured data types used throughout the detection pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


@dataclass
class FrameRecord:
    """Per-frame analysis record for debugging."""
    timestamp: float  # Time in seconds from video start
    frame_idx: int
    face_detected: bool
    mouth_open_ratio: Optional[float] = None
    audio_energy: Optional[float] = None
    eye_aspect_ratio: Optional[float] = None  # EAR for blink detection
    head_pose_yaw: Optional[float] = None
    head_pose_pitch: Optional[float] = None
    landmark_jitter: Optional[float] = None
    texture_artifact: Optional[float] = None
    raw_values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureReason:
    """Represents a contributing feature with its contribution to the final score."""
    name: str
    contribution: float  # How much this feature contributed (can be negative)
    normalized_value: float  # Normalized feature value
    raw_value: float  # Original raw feature value
    weight: float  # Feature weight in scoring


@dataclass
class VideoAnalysisResult:
    """
    Complete analysis result for a video.
    
    This is the main return type from analyze_video().
    """
    # Video metadata
    video_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_path: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    # Aggregated feature values (scalars)
    features: Dict[str, float] = field(default_factory=dict)
    
    # Normalized feature values (z-scores)
    normalized_features: Dict[str, float] = field(default_factory=dict)
    
    # Final scores
    deepfake_score: float = 0.0  # [0, 1] - probability of being deepfake
    label: str = "uncertain"  # "deepfake", "authentic", or "uncertain"
    
    # Explanations
    reasons: List[FeatureReason] = field(default_factory=list)  # Top contributing features
    summary: str = ""  # Human-readable summary string
    
    # Debug data
    frame_records: List[FrameRecord] = field(default_factory=list)  # Sampled per-frame records
    
    # Analysis parameters
    parameters: Dict[str, Any] = field(default_factory=dict)  # Frame sample rate, threshold, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'metadata': {
                'video_id': self.video_id,
                'video_path': self.video_path,
                'analysis_timestamp': self.analysis_timestamp.isoformat(),
                'version': self.version
            },
            'features': self.features,
            'normalized_features': self.normalized_features,
            'deepfake_score': self.deepfake_score,
            'label': self.label,
            'reasons': [
                {
                    'name': r.name,
                    'contribution': r.contribution,
                    'normalized_value': r.normalized_value,
                    'raw_value': r.raw_value,
                    'weight': r.weight
                }
                for r in self.reasons
            ],
            'summary': self.summary,
            'frame_records': [
                {
                    'timestamp': fr.timestamp,
                    'frame_idx': fr.frame_idx,
                    'face_detected': fr.face_detected,
                    'mouth_open_ratio': fr.mouth_open_ratio,
                    'audio_energy': fr.audio_energy,
                    'eye_aspect_ratio': fr.eye_aspect_ratio,
                    'head_pose_yaw': fr.head_pose_yaw,
                    'head_pose_pitch': fr.head_pose_pitch,
                    'landmark_jitter': fr.landmark_jitter,
                    'texture_artifact': fr.texture_artifact,
                    'raw_values': fr.raw_values
                }
                for fr in self.frame_records
            ],
            'parameters': self.parameters
        }

