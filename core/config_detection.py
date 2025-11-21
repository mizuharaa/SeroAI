"""Configuration for rule-based deepfake detection.

This config controls the new rule-based detector that prioritizes
forensic features over the old biased supervised model.
"""

# Legacy Model Control
USE_LEGACY_MODEL = False  # Set to False to ignore old biased supervised model
LEGACY_MODEL_WEIGHT = 0.1  # If enabled, weight for legacy model (keep low)

# Feature Weights (must sum to ~1.0)
# Higher weight = more influence on final score
WEIGHTS = {
    "watermark": 0.35,           # Watermark evidence (highest priority, slightly reduced)
    "noise_shimmer": 0.20,       # Motion pixel / grain shimmer (slightly reduced)
    "anatomy": 0.20,             # Hands/mouth/eyes (only if human present, increased from 0.15)
    "temporal_identity": 0.15,   # Face embedding / identity jitter (increased from 0.10)
    "frequency_artifacts": 0.07,  # DCT/FFT artifacts
    "audio_sync": 0.03,          # Audio-lip mismatch
}

# Human Presence Gating
HUMAN_PRESENCE_MIN_FRAMES = 10  # Minimum frames with detected face/person
HUMAN_PRESENCE_MIN_FRACTION = 0.3  # Minimum fraction of frames with human
HUMAN_DETECTION_FRACTION_THRESHOLD = 0.15  # Minimum fraction to consider human present (for gating)
# If human not detected, anatomy features are ignored (weight = 0)

# Watermark Detection Thresholds
WATERMARK_CONFIDENCE_THRESHOLD = 0.4  # Minimum confidence to trigger watermark boost (lowered from 0.7)
WATERMARK_STRONG_THRESHOLD = 0.3  # Threshold for "strong" watermark (uses 1.2x multiplier)
WATERMARK_FORCE_MIN_SCORE = 0.5  # If watermark detected, force score >= this
WATERMARK_FORCE_UNCERTAIN = True  # Never output "REAL" if watermark detected

# Noise/Shimmer Detection Thresholds (lowered significantly)
SHIMMER_INTENSITY_THRESHOLD = 0.05  # High-frequency texture change threshold (was 0.6)
SHIMMER_INTENSITY_HIGH = 0.15  # Upper bound for soft scoring (threshold * 3)
BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD = 0.40  # Static region motion threshold (was 0.5)
BACKGROUND_MOTION_INCONSISTENCY_HIGH = 1.0  # Upper bound for soft scoring
FLAT_REGION_NOISE_DRIFT_THRESHOLD = 0.15  # Flat patch pixel drift threshold (was 0.4)
FLAT_REGION_NOISE_DRIFT_HIGH = 0.6  # Upper bound for soft scoring

# Constant Motion & Motion Entropy Thresholds
CONSTANT_MOTION_RATIO_LOW = 0.3  # Lower bound for soft scoring
CONSTANT_MOTION_RATIO_HIGH = 0.7  # Upper bound for soft scoring
MOTION_ENTROPY_LOW = 0.3  # Lower bound for entropy suspicion (low entropy = suspicious)
MOTION_ENTROPY_HIGH = 0.8  # Upper bound for entropy suspicion

# Anatomy Feature Thresholds (only used if human present, for soft scoring)
HAND_MISSING_FINGER_LOW = 0.2  # Lower bound for soft scoring
HAND_MISSING_FINGER_HIGH = 0.6  # Upper bound for soft scoring
HAND_ABNORMAL_ANGLE_LOW = 0.2  # Lower bound for soft scoring
HAND_ABNORMAL_ANGLE_HIGH = 0.6  # Upper bound for soft scoring
EXTREME_MOUTH_OPEN_LOW = 0.2  # Lower bound for soft scoring
EXTREME_MOUTH_OPEN_HIGH = 0.7  # Upper bound for soft scoring
BLINK_IRREGULARITY_LOW = 0.6  # Lower bound for soft scoring (0.5 = normal)
BLINK_IRREGULARITY_HIGH = 0.9  # Upper bound for soft scoring

# Temporal Identity Thresholds (for soft scoring)
TEMPORAL_IDENTITY_STD_LOW = 0.5  # Lower bound for soft scoring
TEMPORAL_IDENTITY_STD_HIGH = 0.9  # Upper bound for soft scoring
HEAD_POSE_JITTER_LOW = 0.6  # Lower bound for soft scoring
HEAD_POSE_JITTER_HIGH = 1.0  # Upper bound for soft scoring

# Frequency Artifact Thresholds
BOUNDARY_ARTIFACT_THRESHOLD = 0.6  # Boundary artifact score threshold
FREQ_ENERGY_RATIO_THRESHOLD = 0.7  # High/low frequency ratio threshold

# Audio Sync Thresholds
LIP_AUDIO_CORRELATION_THRESHOLD = 0.45  # Minimum correlation (lower = more suspicious, raised from 0.4)
AUDIO_SUSPICION_THRESHOLD = 0.55  # Suspicion threshold (1.0 - correlation), equivalent to corr < 0.45
PHONEME_LAG_THRESHOLD = 0.5  # Maximum acceptable lag

# Cumulative Evidence Boost
CUMULATIVE_EVIDENCE_BOOST_3PLUS = 1.3  # Boost multiplier when 3+ categories show evidence
CUMULATIVE_EVIDENCE_BOOST_2 = 1.15  # Boost multiplier when 2 categories show evidence

# Final Score Thresholds
SCORE_REAL_THRESHOLD = 0.25  # Below this = REAL
SCORE_UNCERTAIN_LOW = 0.25   # Start of uncertain range
SCORE_UNCERTAIN_HIGH = 0.75  # End of uncertain range
SCORE_DEEPFAKE_THRESHOLD = 0.75  # Above this = DEEPFAKE

# Feature Extraction Settings
MOTION_FEATURES_FPS = 12.0
MOTION_FEATURES_MAX_FRAMES = 50
ANATOMY_FEATURES_FPS = 8.0
ANATOMY_FEATURES_MAX_FRAMES = 30
FREQUENCY_FEATURES_FPS = 10.0
FREQUENCY_FEATURES_MAX_FRAMES = 20
AUDIO_SYNC_FEATURES_FPS = 12.0
AUDIO_SYNC_FEATURES_MAX_FRAMES = 50

