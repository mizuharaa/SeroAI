DECISION = {
    # decisive band
    "UNSURE_LOW": 0.40,
    "UNSURE_HIGH": 0.60,

    # final thresholds (after calibration)
    "AI_THRESHOLD": 0.80,
    "REAL_THRESHOLD": 0.20,

    # quality gating (used to DOWN-WEIGHT fragile features, NOT to detect AI)
    # These thresholds identify low-quality videos where analysis is less reliable
    # Lower thresholds = more lenient (fewer videos marked as "low quality")
    "BLUR_MIN": 40.0,            # Laplacian variance; lowered from 60 (more lenient)
    "BRISQUE_MAX": 60.0,         # Perceptual quality; raised from 45 (more lenient)
    "BITRATE_MIN": 150_000,      # bits/s; lowered from 200k (more lenient)
    "ALLOW_ABSTAIN_ON_LOW_QUALITY": True,

    # hard-evidence boosts (added to fusion logit prior to calibration)
    "LOGIC_BREAK_LOGIT_BONUS": 2.5,   # object/material "impossible changes"
    "WATERMARK_LOGIT_BONUS":   1.2,   # safer default, further gated below
    "ANATOMY_LOGIT_BONUS":     1.5,   # missing fingers, twisted limbs
    
    # HARD AI EVIDENCE (new - for generator watermarks and obvious AI)
    "WATERMARK_GENERATOR_LOGIT_BONUS": 6.0,  # Strong boost for AI generator watermarks (Sora, Runway, etc.)
    "LOGIC_BREAK_STRONG_LOGIT_BONUS": 5.0,   # Strong scene logic breaks
    "HARD_AI_MIN_PROB": 0.95,                 # Minimum probability when hard AI evidence present
    "HARD_AI_REAL_CAP": 0.25,                 # Maximum "real" probability when generator watermark detected
}

WATERMARK = {
    # spatial corner zones as fraction of width/height
    "ZONE_FRAC": 0.22,
    # temporal persistence within window
    "PERSISTENCE_WINDOW_SEC": 2.0,
    "MIN_PERSISTENCE": 0.60,           # ≥60% of frames in window
    # stability constraints
    "MIN_IOU": 0.5,
    "MAX_CENTER_SHIFT_FRAC": 0.03,     # 3% of frame diagonal
    # style constraints
    "MAX_FONT_HEIGHT_FRAC": 0.12,      # reject tall captions/titles
    # text policy
    "LEXICON": {"sora","sora.ai","veo","runway","imagen"},
    "BLACKLIST": {"image","imagine","imagenes","imaging"},
    "MIN_CONF": 0.85,
    # boost gating
    "REQUIRE_CORNER": True,
    "REQUIRE_PERSISTENT": True,
    "BOOST_CAP": 1.2
}

FACE = {
    "QUALITY_BLUR_MIN": 60.0,
    "QUALITY_BBOX_MIN_FRAC": 0.03,
    "QUALITY_TRACK_MIN_LEN": 48,
    # temperature scaling for face logits
    "CALIBRATION_TEMPERATURE": 1.2
}

SCENE = {
    "MAX_FRAMES": 60,
    "RESIZE_WIDTH": 320,
    "HIST_DIFF_THR": 0.35,
    "COLOR_JUMP_THR": 0.40,
    "MAX_SECONDS": 3.5  # hard cap per scene-logic stage
}


