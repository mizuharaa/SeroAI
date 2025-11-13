"""Configuration and thresholds for deepfake detection pipeline."""

# Quality Gate Thresholds
BLUR_MIN = 60.0  # Laplacian variance threshold (lower = more blur)
BRISQUE_MAX = 45.0  # BRISQUE score threshold (higher = worse quality)
BITRATE_MIN = 200_000  # Minimum bits per second
SHAKE_MAX = 1.5  # Maximum shake in pixels per frame after stabilization

# Decision Thresholds
AI_THRESHOLD = 0.80  # Probability above this = AI
REAL_THRESHOLD = 0.20  # Probability below this = REAL
UNSURE_THRESHOLD_HIGH = 0.60  # Between REAL_THRESHOLD and this = UNSURE (leaning REAL)
UNSURE_THRESHOLD_LOW = 0.40  # Between this and AI_THRESHOLD = UNSURE (leaning AI)

# Pipeline Settings
ABSTAIN_ON_LOW_QUALITY = True
WATERMARK_LOGIT_BONUS = 1.5  # Bonus to AI probability when watermark detected
MIN_FACES_FOR_FACE_ANALYSIS = 1  # Minimum faces needed to use face branch

# Face Detection
FACE_CONFIDENCE_THRESHOLD = 0.5
MIN_FACE_SIZE = 64  # Minimum face size in pixels
FACE_TRACK_MIN_LENGTH = 32  # Minimum track length for analysis

# Audio-Visual Sync
SYNC_THRESHOLD_MS = 100  # Maximum allowed mis-sync in milliseconds
MIN_AUDIO_LENGTH_SEC = 0.5  # Minimum audio length for A/V analysis

# Watermark Detection
WATERMARK_KEYWORDS = ['SORA', 'SORA.AI', 'SoraAI', 'VEO', 'VEo', 'RUNWAY', 'RunwayML', 
                      'MIDJOURNEY', 'STABLE', 'DIFFUSION', 'DALL-E', 'IMAGEN']
WATERMARK_EDIT_DISTANCE_THRESHOLD = 2  # Maximum edit distance for watermark match
OCR_CONFIDENCE_THRESHOLD = 0.6  # Minimum OCR confidence for watermark

# Scene Logic
SHOT_CHANGE_THRESHOLD = 0.3  # Histogram difference threshold for shot detection
MIN_OBJECT_PERSISTENCE_FRAMES = 10  # Minimum frames for object persistence check

# Model Paths (will be created/loaded)
FACE_MODEL_PATH = 'models/face/deepfake_face.pth'
SCENE_MODEL_PATH = 'models/scene/deepfake_scene.pth'
FUSION_MODEL_PATH = 'models/fusion.pkl'
CALIBRATION_PATH = 'models/calibration.json'

# Feature Extraction
MAX_FRAMES_TO_ANALYZE = 300  # Maximum frames to extract from video
FRAME_SAMPLE_RATE = 1  # Sample every Nth frame
TARGET_FPS = 25  # Target FPS for analysis

