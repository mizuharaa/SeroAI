DECISION = {
    # decisive band
    "UNSURE_LOW": 0.40,
    "UNSURE_HIGH": 0.60,

    # final thresholds (after calibration)
    "AI_THRESHOLD": 0.80,
    "REAL_THRESHOLD": 0.20,

    # quality gating
    "BLUR_MIN": 60.0,            # Laplacian variance; tune by dataset
    "BRISQUE_MAX": 45.0,         # worse quality => higher score
    "BITRATE_MIN": 200_000,      # bits/s
    "ALLOW_ABSTAIN_ON_LOW_QUALITY": True,

    # hard-evidence boosts (added to fusion logit prior to calibration)
    "LOGIC_BREAK_LOGIT_BONUS": 2.0,   # object/material “impossible changes”
    "WATERMARK_LOGIT_BONUS":   1.2,   # safer default, further gated below
    "ANATOMY_LOGIT_BONUS":     1.4,   # missing fingers, twisted limbs
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


