"""
Enhanced watermark detection for AI generator identification.

Improvements over v1:
- Multiple crop strategies (corners, bottom band, center)
- Multiple preprocessing passes (scales, blur, sharpen, thresholds)
- Expanded vocabulary with common AI generators
- Looser string matching for short words
- Persistence tracking across frames
- Generator hint flag for hard AI evidence
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import pytesseract
from Levenshtein import distance as levenshtein_distance
import os

# Configure Tesseract
if os.name == 'nt':
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# Expanded AI generator vocabulary
AI_GENERATORS = [
    # OpenAI
    "SORA", "SORA AI", "OPENAI", "CHATGPT",
    # Google
    "VEO", "IMAGEN", "GOOGLE AI",
    # Runway
    "RUNWAY", "RUNWAYML", "GEN-2", "GEN-3",
    # Midjourney
    "MIDJOURNEY", "MJ",
    # Stability
    "STABLE DIFFUSION", "STABILITY", "STABLE VIDEO",
    # Others
    "PIKA", "SYNTHESIA", "D-ID", "HEYGEN",
    # Social handles (common in AI demos)
    "@LONGLIVEAI", "@OPENAI", "@RUNWAYML",
    # Generic
    "AI GENERATED", "SYNTHETIC", "DEEPFAKE",
]

# Blacklist (common false positives)
BLACKLIST = [
    "the", "and", "or", "of", "to", "in", "a", "is",
    "for", "on", "with", "by", "at", "from",
]


def extract_multiple_crops(frame: np.ndarray) -> List[Tuple[np.ndarray, str, Tuple]]:
    """
    Extract multiple crops with different strategies.
    OPTIMIZED: Reduced to 3 most common locations for speed.
    
    Returns:
        List of (crop, location_name, bbox) tuples
    """
    h, w = frame.shape[:2]
    crops = []
    
    # Strategy 1: Corner crops (most common for watermarks)
    corner_size = max(200, int(min(w, h) * 0.15))
    # Only check bottom-right and bottom-left (most common)
    corners = {
        'bottom_left': frame[h-corner_size:h, 0:corner_size],
        'bottom_right': frame[h-corner_size:h, w-corner_size:w],
    }
    for name, crop in corners.items():
        if crop.size > 0:
            crops.append((crop, name, (0, 0, crop.shape[1], crop.shape[0])))
    
    # Strategy 2: Bottom band (common for TikTok/Reels/YouTube Shorts)
    band_height = max(150, int(h * 0.12))
    bottom_band = frame[h-band_height:h, :]
    if bottom_band.size > 0:
        crops.append((bottom_band, 'bottom_band', (0, h-band_height, w, band_height)))
    
    return crops


def preprocess_for_ocr(region: np.ndarray) -> List[np.ndarray]:
    """
    Apply multiple preprocessing strategies to improve OCR.
    OPTIMIZED: Reduced to 3 most effective passes for speed.
    
    Returns:
        List of preprocessed images to try OCR on
    """
    if len(region.shape) == 3:
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    else:
        gray = region
    
    preprocessed = []
    
    # 1. CLAHE (contrast enhancement) - most effective for watermarks
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    preprocessed.append(enhanced)
    
    # 2. Adaptive threshold - good for varying lighting
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
    preprocessed.append(adaptive)
    
    # 3. Inverted (white text on black background) - common for overlays
    inverted = cv2.bitwise_not(gray)
    preprocessed.append(inverted)
    
    return preprocessed


def ocr_with_multiple_strategies(region: np.ndarray) -> List[Tuple[str, float]]:
    """
    Run OCR with multiple preprocessing strategies.
    
    Returns:
        List of (text, confidence) tuples
    """
    all_texts = []
    
    preprocessed_images = preprocess_for_ocr(region)
    
    for img in preprocessed_images:
        try:
            # Strategy 1: Word-level OCR with confidence (most reliable)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT,
                                              config='--psm 6')  # Assume uniform block of text
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])
                if text and conf > 0:
                    all_texts.append((text, conf / 100.0))
            
            # Strategy 2: Single line mode (for watermarks) - REMOVED full text extraction for speed
            line_text = pytesseract.image_to_string(img, config='--psm 7').strip()
            if line_text:
                all_texts.append((line_text, 0.75))
        
        except Exception:
            continue
    
    # Deduplicate and return
    seen = set()
    unique_texts = []
    for text, conf in all_texts:
        text_upper = text.upper().strip()
        if text_upper and text_upper not in seen:
            seen.add(text_upper)
            unique_texts.append((text_upper, conf))
    
    return unique_texts


def match_ai_generator(text: str) -> Optional[Tuple[str, float, bool]]:
    """
    Match text against AI generator vocabulary.
    
    Returns:
        (matched_generator, confidence, is_generator_hint) or None
    """
    text_upper = text.upper().strip()
    
    # Filter blacklist
    if text_upper.lower() in BLACKLIST:
        return None
    
    # Exact match (highest confidence)
    for gen in AI_GENERATORS:
        if text_upper == gen.upper():
            return (gen, 1.0, True)
    
    # Substring match (medium confidence)
    for gen in AI_GENERATORS:
        if gen.upper() in text_upper or text_upper in gen.upper():
            return (gen, 0.85, True)
    
    # Levenshtein distance match (lower confidence)
    # Use distance ≤ 3 for longer words, ≤ 2 for short words
    for gen in AI_GENERATORS:
        gen_upper = gen.upper()
        max_dist = 3 if len(gen_upper) > 6 else 2
        dist = levenshtein_distance(text_upper, gen_upper)
        if dist <= max_dist:
            confidence = 1.0 - (dist / max(len(text_upper), len(gen_upper)))
            return (gen, confidence, True)
    
    return None


def detect_watermark_in_frame_v2(frame: np.ndarray) -> Dict:
    """
    Enhanced watermark detection in a single frame.
    
    Returns:
        Dict with:
            - detected: bool
            - watermark: str (matched generator name)
            - confidence: float
            - generator_hint: bool (True if AI generator detected)
            - location: str (where watermark was found)
            - persistent: bool (will be set by video-level detection)
            - corner: bool (True if found in corner)
    """
    crops = extract_multiple_crops(frame)
    
    all_detections = []
    
    for crop, location, bbox in crops:
        texts = ocr_with_multiple_strategies(crop)
        
        for text, ocr_conf in texts:
            match = match_ai_generator(text)
            if match:
                gen_name, match_conf, is_gen = match
                final_conf = ocr_conf * match_conf
                
                all_detections.append({
                    'generator': gen_name,
                    'text': text,
                    'confidence': final_conf,
                    'location': location,
                    'ocr_confidence': ocr_conf,
                    'match_confidence': match_conf,
                    'generator_hint': is_gen,
                    'corner': 'corner' in location or location in ['top_left', 'top_right', 'bottom_left', 'bottom_right'],
                })
    
    if all_detections:
        # Return best detection
        best = max(all_detections, key=lambda x: x['confidence'])
        return {
            'detected': True,
            'watermark': best['generator'],
            'confidence': best['confidence'],
            'text': best['text'],
            'generator_hint': best['generator_hint'],
            'location': best['location'],
            'corner': best['corner'],
            'persistent': False,  # Will be set by video-level detection
            'all_detections': all_detections,
        }
    
    return {
        'detected': False,
        'watermark': None,
        'confidence': 0.0,
        'text': None,
        'generator_hint': False,
        'location': None,
        'corner': False,
        'persistent': False,
        'all_detections': [],
    }


def detect_watermark_in_video_v2(video_path: str, max_frames: int = 5) -> Dict:
    """
    Enhanced watermark detection in video with persistence tracking.
    
    Args:
        video_path: Path to video
        max_frames: Maximum frames to check (default: 5 for speed)
    
    Returns:
        Dict with watermark detection results
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        cap.release()
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }
    
    # Sample frames evenly across video
    frame_indices = np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int)
    
    detections_per_frame = []
    
    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        
        result = detect_watermark_in_frame_v2(frame)
        if result['detected']:
            detections_per_frame.append(result)
    
    cap.release()
    
    if not detections_per_frame:
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }
    
    # Aggregate detections
    # Check if same watermark appears in multiple frames (persistence)
    watermark_counts = {}
    for det in detections_per_frame:
        wm = det['watermark']
        if wm not in watermark_counts:
            watermark_counts[wm] = []
        watermark_counts[wm].append(det)
    
    # Get most common watermark
    most_common_wm = max(watermark_counts.keys(), key=lambda k: len(watermark_counts[k]))
    wm_detections = watermark_counts[most_common_wm]
    
    # Check persistence (appears in ≥3 frames OR ≥30% of checked frames)
    persistence_threshold = max(3, len(frame_indices) * 0.3)
    is_persistent = len(wm_detections) >= persistence_threshold
    
    # Check if found in corner
    is_corner = any(det['corner'] for det in wm_detections)
    
    # Average confidence
    avg_confidence = np.mean([det['confidence'] for det in wm_detections])
    
    # Check if generator hint
    is_generator = all(det['generator_hint'] for det in wm_detections)
    
    return {
        'detected': True,
        'watermark': most_common_wm,
        'confidence': float(avg_confidence),
        'generator_hint': is_generator,
        'persistent': is_persistent,
        'corner': is_corner,
        'detection_count': len(wm_detections),
        'frames_checked': len(frame_indices),
        'all_detections': wm_detections,
    }


# Backward compatibility - use v2 by default
def detect_watermark_in_video(video_path: str) -> Dict:
    """Wrapper for backward compatibility."""
    return detect_watermark_in_video_v2(video_path)


def detect_watermark_in_image(image_path: str) -> Dict:
    """Detect watermark in a single image."""
    frame = cv2.imread(image_path)
    if frame is None:
        return {
            'detected': False,
            'watermark': None,
            'confidence': 0.0,
            'generator_hint': False,
            'persistent': False,
            'corner': False,
        }
    
    result = detect_watermark_in_frame_v2(frame)
    # For single image, persistence is N/A
    result['persistent'] = False
    return result

