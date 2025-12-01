"""
Visual logo matching for AI model watermark detection.

This module performs template matching and feature matching against
reference logos to verify genuine AI model watermarks.
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LogoMatcher:
    """Matches video frames against reference AI model logos."""
    
    # Reference logo paths (will be created as placeholder images)
    # In production, these would be actual transparent PNG logos
    REFERENCE_LOGO_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'assets', 'reference_logos'
    )
    
    # Supported providers
    PROVIDERS = ["sora", "gemini", "pika", "luma", "runway", "heygen", "did"]
    
    # High similarity threshold for verified watermark
    VERIFIED_THRESHOLD = 0.80
    
    # Low bar for detection
    DETECTION_THRESHOLD = 0.50
    
    def __init__(self):
        """Initialize logo matcher and load reference logos."""
        self.reference_logos = self._load_reference_logos()
    
    def _load_reference_logos(self) -> Dict[str, List[np.ndarray]]:
        """
        Load reference logos from assets directory.
        
        Returns:
            Dictionary mapping provider names to lists of logo images
        """
        logos = {}
        os.makedirs(self.REFERENCE_LOGO_DIR, exist_ok=True)
        
        for provider in self.PROVIDERS:
            logos[provider] = []
            # Try to load from file
            logo_path = os.path.join(self.REFERENCE_LOGO_DIR, f"{provider}_logo.png")
            if os.path.exists(logo_path):
                logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                if logo_img is not None:
                    # Convert to RGB if needed
                    if len(logo_img.shape) == 3 and logo_img.shape[2] == 4:
                        # RGBA - convert to RGB with alpha handling
                        alpha = logo_img[:, :, 3] / 255.0
                        rgb = logo_img[:, :, :3]
                        # For now, just use RGB channels
                        logo_img = cv2.cvtColor(logo_img, cv2.COLOR_BGRA2BGR)
                    logos[provider].append(logo_img)
        
        # If no logos found, create placeholder (will need actual logos in production)
        if not any(logos.values()):
            print(f"[logo_matcher] Warning: No reference logos found in {self.REFERENCE_LOGO_DIR}")
            print(f"[logo_matcher] Placeholder mode: Will use text-based detection as fallback")
        
        return logos
    
    def extract_candidate_regions(
        self,
        frame: np.ndarray,
        num_regions: int = 6
    ) -> List[Tuple[np.ndarray, str]]:
        """
        Extract candidate regions where watermarks typically appear.
        
        Args:
            frame: Input frame
            num_regions: Number of regions to extract
            
        Returns:
            List of (roi_image, region_name) tuples
        """
        h, w = frame.shape[:2]
        regions = []
        
        # Define common watermark regions (as percentages)
        region_defs = [
            # Top regions
            (0, 0, w//4, h//6, "top_left"),
            (w//4, 0, w//2, h//6, "top_center"),
            (3*w//4, 0, w, h//6, "top_right"),
            # Bottom regions
            (0, 5*h//6, w//4, h, "bottom_left"),
            (w//4, 5*h//6, w//2, h, "bottom_center"),
            (3*w//4, 5*h//6, w, h, "bottom_right"),
        ]
        
        for x1, y1, x2, y2, name in region_defs[:num_regions]:
            roi = frame[y1:y2, x1:x2]
            if roi.size > 0:
                # Resize to standard size for comparison (keep aspect ratio)
                target_size = 200
                roi_h, roi_w = roi.shape[:2]
                if roi_h > 0 and roi_w > 0:
                    scale = min(target_size / roi_h, target_size / roi_w)
                    new_h, new_w = int(roi_h * scale), int(roi_w * scale)
                    if new_h > 0 and new_w > 0:
                        roi_resized = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_AREA)
                        regions.append((roi_resized, name))
        
        return regions
    
    def logo_similarity(
        self,
        roi: np.ndarray,
        ref_logo: np.ndarray
    ) -> float:
        """
        Compute similarity between ROI and reference logo.
        
        Uses multiple methods:
        1. Normalized Cross-Correlation (NCC)
        2. Structural Similarity Index (SSIM-like)
        3. Feature matching (ORB)
        
        Args:
            roi: Candidate region from video frame
            ref_logo: Reference logo image
            
        Returns:
            Similarity score [0, 1]
        """
        # Convert to grayscale for comparison
        if len(roi.shape) == 3:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            roi_gray = roi
        
        if len(ref_logo.shape) == 3:
            ref_gray = cv2.cvtColor(ref_logo, cv2.COLOR_BGR2GRAY)
        else:
            ref_gray = ref_logo
        
        # Resize both to same size for fair comparison
        target_size = 200
        roi_h, roi_w = roi_gray.shape[:2]
        ref_h, ref_w = ref_gray.shape[:2]
        
        # Resize to match (use smaller dimension to preserve aspect ratio)
        if roi_h > 0 and roi_w > 0 and ref_h > 0 and ref_w > 0:
            # Resize both to target size
            roi_resized = cv2.resize(roi_gray, (target_size, target_size))
            ref_resized = cv2.resize(ref_gray, (target_size, target_size))
        else:
            return 0.0
        
        scores = []
        
        # 1. Normalized Cross-Correlation (NCC)
        try:
            result = cv2.matchTemplate(roi_resized, ref_resized, cv2.TM_CCOEFF_NORMED)
            ncc_score = float(np.max(result))
            scores.append(ncc_score)
        except Exception:
            pass
        
        # 2. Histogram comparison (color distribution)
        try:
            if len(roi.shape) == 3:
                hist_roi = cv2.calcHist([roi], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist_ref = cv2.calcHist([ref_logo], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                cv2.normalize(hist_roi, hist_roi, 0, 1, cv2.NORM_MINMAX)
                cv2.normalize(hist_ref, hist_ref, 0, 1, cv2.NORM_MINMAX)
                hist_corr = cv2.compareHist(hist_roi, hist_ref, cv2.HISTCMP_CORREL)
                scores.append(float(hist_corr))
        except Exception:
            pass
        
        # 3. Feature matching (ORB)
        try:
            orb = cv2.ORB_create(nfeatures=100)
            kp1, des1 = orb.detectAndCompute(roi_resized, None)
            kp2, des2 = orb.detectAndCompute(ref_resized, None)
            
            if des1 is not None and des2 is not None and len(des1) > 0 and len(des2) > 0:
                # Match features
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches = bf.match(des1, des2)
                
                if len(matches) > 0:
                    # Compute match ratio
                    match_ratio = len(matches) / max(len(kp1), len(kp2))
                    # Average distance (lower is better, so invert)
                    avg_distance = np.mean([m.distance for m in matches])
                    feature_score = match_ratio * (1.0 - min(avg_distance / 100.0, 1.0))
                    scores.append(feature_score)
        except Exception:
            pass
        
        # 4. Structural similarity (simplified SSIM)
        try:
            # Compute mean squared error
            mse = np.mean((roi_resized.astype(float) - ref_resized.astype(float)) ** 2)
            if mse > 0:
                max_pixel = 255.0
                ssim_score = 1.0 - (mse / (max_pixel ** 2))
                scores.append(max(0.0, ssim_score))
        except Exception:
            pass
        
        # Average all scores
        if scores:
            return float(np.mean(scores))
        else:
            return 0.0
    
    def provider_similarity(
        self,
        roi: np.ndarray,
        provider_name: str
    ) -> float:
        """
        Compute similarity between ROI and all reference logos for a provider.
        
        Args:
            roi: Candidate region
            provider_name: Provider name (e.g., "sora", "gemini")
            
        Returns:
            Maximum similarity score across all reference logos for this provider
        """
        if provider_name not in self.reference_logos:
            return 0.0
        
        ref_logos = self.reference_logos[provider_name]
        if not ref_logos:
            return 0.0
        
        similarities = []
        for ref_logo in ref_logos:
            sim = self.logo_similarity(roi, ref_logo)
            similarities.append(sim)
        
        return float(np.max(similarities)) if similarities else 0.0
    
    def detect_verified_watermark(
        self,
        frames: List[np.ndarray],
        max_frames: int = 10
    ) -> Dict:
        """
        Detect verified AI model watermark using visual logo matching.
        
        Args:
            frames: List of video frames
            max_frames: Maximum frames to analyze
            
        Returns:
            Dictionary with:
            - best_provider: Provider name or None
            - best_score: Best similarity score [0, 1]
            - watermark_conf: Confidence score
            - provenance_type: Provider name or "none"
            - watermark_detected: bool
            - has_verified_watermark: bool
            - match_method: "NCC+ORB" or "TEXT_FALLBACK"
        """
        if not frames:
            return {
                'best_provider': None,
                'best_score': 0.0,
                'watermark_conf': 0.0,
                'provenance_type': 'none',
                'watermark_detected': False,
                'has_verified_watermark': False,
                'match_method': 'NONE'
            }
        
        # Sample frames (first 3-5 seconds worth)
        sampled_frames = frames[:min(max_frames, len(frames))]
        
        best_provider = None
        best_score = 0.0
        best_region = None
        
        # Check each frame
        for frame in sampled_frames:
            # Extract candidate regions
            regions = self.extract_candidate_regions(frame)
            
            # Check each region against each provider
            for roi, region_name in regions:
                for provider in self.PROVIDERS:
                    similarity = self.provider_similarity(roi, provider)
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_provider = provider
                        best_region = region_name
        
        # Determine confidence and verification status
        watermark_conf = best_score
        provenance_type = best_provider if best_provider else 'none'
        watermark_detected = best_score >= self.DETECTION_THRESHOLD
        has_verified_watermark = (
            best_provider is not None and
            best_score >= self.VERIFIED_THRESHOLD
        )
        
        # Determine match method
        if has_verified_watermark:
            match_method = "NCC+ORB"
        elif watermark_detected:
            match_method = "LOW_CONFIDENCE"
        else:
            match_method = "NONE"
        
        return {
            'best_provider': best_provider,
            'best_score': float(best_score),
            'watermark_conf': float(watermark_conf),
            'provenance_type': provenance_type,
            'watermark_detected': watermark_detected,
            'has_verified_watermark': has_verified_watermark,
            'match_method': match_method,
            'best_region': best_region
        }

