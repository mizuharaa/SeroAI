"""Face detection and tracking for deepfake analysis."""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import mediapipe as mp

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import FACE_CONFIDENCE_THRESHOLD, MIN_FACE_SIZE, FACE_TRACK_MIN_LENGTH
from core.media_io import extract_frames


class FaceDetector:
    """Face detector using MediaPipe."""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # Full range model
            min_detection_confidence=FACE_CONFIDENCE_THRESHOLD
        )
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces in a frame.
        
        Args:
            frame: Input frame (RGB)
            
        Returns:
            List of face detections with bboxes and confidence
        """
        # MediaPipe expects RGB
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            rgb_frame = frame
        else:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.face_detection.process(rgb_frame)
        
        detections = []
        h, w = frame.shape[:2]
        
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                
                # Convert to absolute coordinates
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Filter by minimum size
                if width >= MIN_FACE_SIZE and height >= MIN_FACE_SIZE:
                    detections.append({
                        'bbox': (x, y, width, height),
                        'confidence': detection.score[0],
                        'center': (x + width // 2, y + height // 2)
                    })
        
        return detections
    
    def extract_face_crop(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                         padding: int = 20) -> Optional[np.ndarray]:
        """Extract face crop from frame.
        
        Args:
            frame: Input frame (RGB)
            bbox: Bounding box (x, y, width, height)
            padding: Padding around face
            
        Returns:
            Face crop or None
        """
        x, y, w, h = bbox
        h_img, w_img = frame.shape[:2]
        
        # Add padding
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w_img, x + w + padding)
        y2 = min(h_img, y + h + padding)
        
        crop = frame[y1:y2, x1:x2]
        
        if crop.size > 0:
            return crop
        return None


def track_faces_simple(video_path: str, detector: FaceDetector) -> List[Dict]:
    """Simple face tracking across video.
    
    Args:
        video_path: Path to video file
        detector: FaceDetector instance
        
    Returns:
        List of face tracks
    """
    frames = extract_frames(video_path, max_frames=120, target_fps=12, max_dim=512)
    
    if not frames:
        return []
    
    tracks = []  # List of track dictionaries
    next_track_id = 0
    
    for frame_idx, frame in enumerate(frames):
        detections = detector.detect_faces(frame)
        
        # Simple tracking: match detections to existing tracks by proximity
        for det in detections:
            matched = False
            det_center = det['center']
            
            # Find closest existing track
            for track in tracks:
                if track['last_frame'] < frame_idx - 5:  # Skip stale tracks
                    continue
                
                last_center = track['centers'][-1]
                distance = np.sqrt((det_center[0] - last_center[0])**2 + 
                                 (det_center[1] - last_center[1])**2)
                
                # Match if close enough
                if distance < 100:  # Threshold in pixels
                    track['frames'].append(frame_idx)
                    track['bboxes'].append(det['bbox'])
                    track['centers'].append(det_center)
                    track['last_frame'] = frame_idx
                    matched = True
                    break
            
            # Create new track if no match
            if not matched:
                tracks.append({
                    'id': next_track_id,
                    'frames': [frame_idx],
                    'bboxes': [det['bbox']],
                    'centers': [det_center],
                    'last_frame': frame_idx
                })
                next_track_id += 1
    
    # Filter tracks by minimum length
    valid_tracks = [t for t in tracks if len(t['frames']) >= FACE_TRACK_MIN_LENGTH]
    
    return valid_tracks


def analyze_faces_in_video(video_path: str) -> Dict:
    """Analyze faces in video for deepfake detection.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with face analysis results
    """
    detector = FaceDetector()
    tracks = track_faces_simple(video_path, detector)
    
    if not tracks:
        return {
            'num_faces': 0,
            'num_tracks': 0,
            'avg_track_length': 0,
            'face_detected': False
        }
    
    avg_track_length = np.mean([len(t['frames']) for t in tracks])
    
    # For now, return basic stats
    # In full implementation, would run face deepfake models here
    return {
        'num_faces': len(tracks),
        'num_tracks': len(tracks),
        'avg_track_length': float(avg_track_length),
        'face_detected': True,
        'tracks': tracks
    }

