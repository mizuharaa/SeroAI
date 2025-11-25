"""Configuration for rule-based deepfake detection.

This config controls the new rule-based detector that prioritizes
forensic features over the old biased supervised model.
"""

# Legacy Model Control
USE_LEGACY_MODEL = False  # Set to False to ignore old biased supervised model
LEGACY_MODEL_WEIGHT = 0.1  # If enabled, weight for legacy model (keep low)

# Feature Weights (must sum to ~1.0)
# Rebalanced: anatomy + temporal + frequency + shimmer + audio > watermark
# Watermark should never be the main deciding factor
WEIGHTS = {
    "anatomy": 0.25,             # Hands/mouth/eyes (highest priority - most reliable)
    "temporal_identity": 0.20,    # Face embedding / identity jitter (second priority)
    "frequency_artifacts": 0.15, # DCT/FFT artifacts
    "noise_shimmer": 0.15,       # Motion pixel / grain shimmer
    "audio_sync": 0.15,          # Audio-lip mismatch
    "watermark": 0.10,           # Watermark evidence (lowest priority - least reliable)
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

# Noise/Shimmer Detection Thresholds
# RAISED significantly to be very conservative - only flag CLEARLY abnormal values
SHIMMER_INTENSITY_THRESHOLD = 0.20  # High-frequency texture change threshold (raised from 0.12)
SHIMMER_INTENSITY_HIGH = 0.35  # Upper bound for soft scoring
BACKGROUND_MOTION_INCONSISTENCY_THRESHOLD = 0.70  # Static region motion threshold (raised from 0.55)
BACKGROUND_MOTION_INCONSISTENCY_HIGH = 1.0  # Upper bound for soft scoring
FLAT_REGION_NOISE_DRIFT_THRESHOLD = 0.40  # Flat patch pixel drift threshold (raised from 0.25)
FLAT_REGION_NOISE_DRIFT_HIGH = 0.7  # Upper bound for soft scoring

# Constant Motion & Motion Entropy Thresholds
# RAISED significantly to only flag clearly abnormal motion patterns
CONSTANT_MOTION_RATIO_LOW = 0.65  # Lower bound for soft scoring (normal is 0.2-0.4, raised from 0.5)
CONSTANT_MOTION_RATIO_HIGH = 0.85  # Upper bound for soft scoring (raised from 0.8)
MOTION_ENTROPY_LOW = 0.5  # Lower bound for entropy suspicion (normal entropy is 0.5-0.7, raised from 0.4)
MOTION_ENTROPY_HIGH = 0.85  # Upper bound for entropy suspicion (raised from 0.8)

# Minimum evidence threshold - only include evidence above this in scoring
# Prevents tiny detections from accumulating to high scores
MIN_EVIDENCE_THRESHOLD = 0.25  # Only count evidence with score >= 0.25

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
# RAISED significantly to only flag clearly abnormal temporal inconsistencies
TEMPORAL_IDENTITY_STD_LOW = 0.75  # Lower bound for soft scoring (normal is 0.3-0.5, raised from 0.65)
TEMPORAL_IDENTITY_STD_HIGH = 0.95  # Upper bound for soft scoring (raised from 0.9)
HEAD_POSE_JITTER_LOW = 0.80  # Lower bound for soft scoring (normal is 0.3-0.6, raised from 0.7)
HEAD_POSE_JITTER_HIGH = 1.0  # Upper bound for soft scoring

# Face-Body Motion Coherence (NEW - most reliable discriminator)
# Measures if face moves rigidly with head/body (real) vs. drifts independently (deepfake)
FACE_BODY_MOTION_COHERENCE_THRESHOLD = 0.15  # Below this = suspicious (face drifting from body)
FACE_BODY_MOTION_COHERENCE_LOW = 0.10  # Lower bound for soft scoring
FACE_BODY_MOTION_COHERENCE_HIGH = 0.20  # Upper bound for soft scoring

# Frequency Artifact Thresholds
# RAISED to only flag clearly abnormal frequency patterns
BOUNDARY_ARTIFACT_THRESHOLD = 0.7  # Boundary artifact score threshold (raised from 0.6)
FREQ_ENERGY_RATIO_THRESHOLD = 0.8  # High/low frequency ratio threshold (raised from 0.7)

# Audio Sync Thresholds
LIP_AUDIO_CORRELATION_THRESHOLD = 0.45  # Minimum correlation (lower = more suspicious, raised from 0.4)
AUDIO_SUSPICION_THRESHOLD = 0.55  # Suspicion threshold (1.0 - correlation), equivalent to corr < 0.45
PHONEME_LAG_THRESHOLD = 0.5  # Maximum acceptable lag

# Cumulative Evidence Boost
CUMULATIVE_EVIDENCE_BOOST_3PLUS = 1.3  # Boost multiplier when 3+ categories show evidence
CUMULATIVE_EVIDENCE_BOOST_2 = 1.15  # Boost multiplier when 2 categories show evidence

# Final Score Thresholds (for new real/fake evidence system)
# Deepfake probability thresholds - adjusted to be more confident
DEEPFAKE_PROB_REAL_THRESHOLD = 0.30  # Below this = REAL (raised from 0.25)
DEEPFAKE_PROB_UNCERTAIN_LOW = 0.30   # Start of uncertain range
DEEPFAKE_PROB_UNCERTAIN_HIGH = 0.70  # End of uncertain range (lowered from 0.75)
DEEPFAKE_PROB_DEEPFAKE_THRESHOLD = 0.70  # Above this = DEEPFAKE (lowered from 0.75)

# Sigmoid slope for converting evidence difference to probability
EVIDENCE_SIGMOID_SLOPE = 6.0  # Higher = sharper transition (raised from 4.0 for more decisive results)

# Default score when no evidence is found (authentic videos)
# Set low so videos with no suspicious features default to REAL
DEFAULT_NO_EVIDENCE_SCORE = 0.10  # Low score = REAL (was 0.5 = UNCERTAIN)

# Normalcy bonus: reduce score when features are in normal ranges
# This rewards videos that show normal patterns (not just "no evidence")
NORMALCY_BONUS_MULTIPLIER = 0.7  # Multiply score by this if all features are normal
NORMALCY_BONUS_MIN_SCORE = 0.05  # Minimum score after normalcy bonus (very confident REAL)

# Feature Extraction Settings
MOTION_FEATURES_FPS = 12.0
MOTION_FEATURES_MAX_FRAMES = 50
ANATOMY_FEATURES_FPS = 8.0
ANATOMY_FEATURES_MAX_FRAMES = 30
FREQUENCY_FEATURES_FPS = 10.0
FREQUENCY_FEATURES_MAX_FRAMES = 20
AUDIO_SYNC_FEATURES_FPS = 12.0
AUDIO_SYNC_FEATURES_MAX_FRAMES = 50

