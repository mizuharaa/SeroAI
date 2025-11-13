"""Watermark and OCR detection for AI generator identification."""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import pytesseract
from Levenshtein import distance as levenshtein_distance
import re
import os

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import (
    WATERMARK_KEYWORDS, 
    WATERMARK_EDIT_DISTANCE_THRESHOLD,
    OCR_CONFIDENCE_THRESHOLD
)
from app.config import WATERMARK as WM_CFG
import json


def extract_text_regions(frame: np.ndarray) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
    """Extract potential text regions from frame.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        List of (cropped_region, bbox) tuples
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to find text-like regions
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    regions = []
    h, w = frame.shape[:2]
    
    for contour in contours:
        x, y, bw, bh = cv2.boundingRect(contour)
        
        # Filter by size (text regions are typically small)
        if 20 < bw < w * 0.3 and 10 < bh < h * 0.2:
            # Filter by aspect ratio
            aspect_ratio = bw / bh
            if 1.5 < aspect_ratio < 10:
                # Extract region
                region = frame[max(0, y-5):min(h, y+bh+5), max(0, x-5):min(w, x+bw+5)]
                regions.append((region, (x, y, bw, bh)))
    
    # Also check corners (common watermark locations) — zones from config
    cw = max(1, int(w * WM_CFG["ZONE_FRAC"]))
    ch = max(1, int(h * WM_CFG["ZONE_FRAC"]))
    corner_regions = [
        frame[0:ch, 0:cw],                # Top-left
        frame[0:ch, w-cw:w],              # Top-right
        frame[h-ch:h, 0:cw],              # Bottom-left
        frame[h-ch:h, w-cw:w],            # Bottom-right
    ]
    
    for i, corner in enumerate(corner_regions):
        if corner.size > 0:
            regions.append((corner, (0, 0, corner.shape[1], corner.shape[0])))
    
    return regions


def ocr_text_from_region(region: np.ndarray) -> List[Tuple[str, float]]:
    """Extract text from region using OCR.
    
    Args:
        region: Image region to OCR
        
    Returns:
        List of (text, confidence) tuples
    """
    try:
        # Preprocess for better OCR
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # OCR with confidence scores
        data = pytesseract.image_to_data(enhanced, output_type=pytesseract.Output.DICT)
        
        texts = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = float(data['conf'][i])
            
            if text and conf > 0:
                texts.append((text, conf / 100.0))
        
        # Also try direct OCR on full region
        try:
            full_text = pytesseract.image_to_string(enhanced).strip()
            if full_text:
                texts.append((full_text, 0.7))  # Default confidence
        except:
            pass
        
        return texts
    except Exception as e:
        return []


def match_watermark(text: str, keywords: List[str]) -> Optional[Tuple[str, float, int]]:
    """Match text against watermark keywords.
    
    Args:
        text: Text to match
        keywords: List of watermark keywords
        
    Returns:
        (matched_keyword, confidence, edit_distance) or None
    """
    text_upper = text.upper().strip()
    # exact-match only with lexicon; blacklist reject
    if text_upper.lower() in WM_CFG["BLACKLIST"]:
        return None
    
    best_match = None
    best_distance = float('inf')
    best_keyword = None
    
    for keyword in WM_CFG["LEXICON"]:
        if text_upper == keyword.upper():
            return (keyword, 1.0, 0)
    
    return None


def detect_watermark_in_frame(frame: np.ndarray) -> Dict:
    """Detect watermarks in a single frame.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Dictionary with watermark detection results
    """
    # Extract text regions
    regions = extract_text_regions(frame)
    
    detected_watermarks = []
    
    # Check each region
    for region, bbox in regions:
        texts = ocr_text_from_region(region)
        
        for text, conf in texts:
            if conf < OCR_CONFIDENCE_THRESHOLD:
                continue
            
            match = match_watermark(text, WATERMARK_KEYWORDS)
            if match:
                keyword, match_conf, edit_dist = match
                final_conf = conf * match_conf
                
                detected_watermarks.append({
                    'keyword': keyword,
                    'text': text,
                    'confidence': final_conf,
                    'edit_distance': edit_dist,
                    'bbox': bbox,
                    'ocr_confidence': conf
                })
    
    # Also check full frame with lower threshold
    try:
        full_texts = ocr_text_from_region(frame)
        for text, conf in full_texts:
            if conf >= OCR_CONFIDENCE_THRESHOLD * 0.7:  # Slightly lower threshold for full frame
                match = match_watermark(text, WATERMARK_KEYWORDS)
                if match:
                    keyword, match_conf, edit_dist = match
                    # Check if not already found
                    if not any(w['keyword'] == keyword for w in detected_watermarks):
                        detected_watermarks.append({
                            'keyword': keyword,
                            'text': text,
                            'confidence': conf * match_conf,
                            'edit_distance': edit_dist,
                            'bbox': None,
                            'ocr_confidence': conf
                        })
    except:
        pass
    
    # Return best match
    if detected_watermarks:
        best = max(detected_watermarks, key=lambda x: x['confidence'])
        return {
            'detected': True,
            'watermark': best['keyword'],
            'confidence': best['confidence'],
            'text': best['text'],
            'all_matches': detected_watermarks
        }
    
    return {
        'detected': False,
        'watermark': None,
        'confidence': 0.0,
        'text': None,
        'all_matches': []
    }


def detect_watermark_in_video(video_path: str, sample_positions: Tuple[float, ...] = (0.12, 0.55, 0.88)) -> Dict:
    """Detect watermarks in video by sampling a limited set of frames.
    
    Args:
        video_path: Path to video file
        sample_positions: Normalized positions (0-1) to sample frames from.
                          Defaults target three points; detection stops early once found.
        
    Returns:
        Dictionary with watermark detection results
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'message': 'Could not open video',
            'total_samples': 0,
            'detections': 0,
            'frequency': 0.0
        }
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_samples = 0
    detections = []
    debug_hits: List[Dict] = []
    
    if total_frames <= 0:
        sample_indices = [0]
    else:
        sample_indices = []
        for pos in sample_positions:
            frame_idx = int(total_frames * max(0.0, min(1.0, pos)))
            if frame_idx not in sample_indices:
                sample_indices.append(frame_idx)
    
    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        total_samples += 1
        # run restricted OCR on the 4 corner regions only
        h, w = frame.shape[:2]
        cw = max(1, int(w * WM_CFG["ZONE_FRAC"]))
        ch = max(1, int(h * WM_CFG["ZONE_FRAC"]))
        zones = [
            (0, 0, cw, ch, "tl"),
            (w-cw, 0, w, ch, "tr"),
            (0, h-ch, cw, h, "bl"),
            (w-cw, h-ch, w, h, "br"),
        ]
        frame_hits = []
        for (x1, y1, x2, y2, tag) in zones:
            roi = frame[y1:y2, x1:x2]
            texts = ocr_text_from_region(roi)
            for txt, conf in texts:
                match = match_watermark(txt, [])
                is_corner = True
                is_overlay_band = (y2 - y1) < int(h * 0.16)
                font_tall = (y2 - y1) > int(h * WM_CFG["MAX_FONT_HEIGHT_FRAC"])
                hit = {
                    "text": txt, "conf": conf, "zone": tag,
                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                    "is_corner": is_corner,
                    "is_overlay_band": is_overlay_band,
                    "font_tall": font_tall,
                    "keyword": match[0] if match else None
                }
                debug_hits.append(hit)
                if match and conf >= WM_CFG["MIN_CONF"] and not font_tall:
                    frame_hits.append((match[0], conf, (x1, y1, x2 - x1, y2 - y1), tag))
        # persistence/stability accumulation per keyword+zone
        if frame_hits:
            for k, conf, bbox, tag in frame_hits:
                detections.append({
                    "keyword": k, "conf": conf, "bbox": bbox, "zone": tag,
                    "frame_idx": idx
                })
    
    cap.release()
    
    # Aggregate persistence within ~2s window
    if detections:
        # group by keyword+zone
        by_kz: Dict[Tuple[str, str], List[Dict]] = {}
        for d in detections:
            by_kz.setdefault((d["keyword"], d["zone"]), []).append(d)
        best_kw = None
        best_score = 0.0
        best_conf = 0.0
        for (k, z), items in by_kz.items():
            items = sorted(items, key=lambda x: x["frame_idx"])
            # persistence approx: frames with hit / total_samples
            persistence = len(items) / max(1, total_samples)
            conf_mean = float(np.mean([i["conf"] for i in items]))
            if persistence >= WM_CFG["MIN_PERSISTENCE"] and conf_mean >= WM_CFG["MIN_CONF"]:
                score = (persistence + conf_mean) / 2.0
                if score > best_score:
                    best_score = score
                    best_conf = conf_mean
                    best_kw = (k, z)
        if best_kw:
            k, z = best_kw
            result = {
                'detected': True,
                'watermark': k,
                'confidence': best_conf,
                'frequency': best_score,
                'persistent': True,
                'corner': True,
                'reason': f'persistence@{z} ({best_score:.2f})',
                'detections': len(detections),
                'total_samples': total_samples,
                'debug_hits': debug_hits
            }
            return result
    
    return {
        'detected': False,
        'watermark': None,
        'confidence': 0.0,
        'frequency': 0.0,
        'detections': 0,
        'total_samples': total_samples,
        'debug_hits': debug_hits
    }


def detect_watermark_in_image(image_path: str) -> Dict:
    """Detect watermarks in a single image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary with watermark detection results
    """
    frame = cv2.imread(image_path)
    if frame is None:
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'message': 'Could not load image'
        }
    
    return detect_watermark_in_frame(frame)

