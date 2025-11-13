"""Feedback storage and adaptive weighting for detection metrics."""

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, Any, Optional
from numbers import Number

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

_INIT_LOCK = threading.Lock()
_INITIALIZED = False


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _initialize():
    global _INITIALIZED
    if _INITIALIZED:
        return
    with _INIT_LOCK:
        if _INITIALIZED:
            return
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    verdict TEXT,
                    prob_ai REAL,
                    features TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback_received INTEGER DEFAULT 0
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_id TEXT,
                    user_label TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(detection_id) REFERENCES detections(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS metric_stats (
                    metric TEXT PRIMARY KEY,
                    correct_count REAL DEFAULT 0,
                    incorrect_count REAL DEFAULT 0
                )
                """
            )
        _INITIALIZED = True


def store_detection(
    detection_id: str,
    filename: str,
    verdict: str,
    prob_ai: float,
    features: Dict[str, Any],
) -> None:
    _initialize()
    sanitized_features = _sanitize(features)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO detections (id, filename, verdict, prob_ai, features)
            VALUES (?, ?, ?, ?, ?)
            """,
            (detection_id, filename, verdict, prob_ai, json.dumps(sanitized_features)),
        )


def store_feedback(detection_id: str, user_label: str, notes: Optional[str] = None) -> bool:
    _initialize()
    if notes:
        notes = notes.strip()
        if len(notes) > 500:
            notes = notes[:500]
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT id, verdict, features, feedback_received FROM detections WHERE id = ?",
            (detection_id,),
        )
        row = cur.fetchone()
        if row is None:
            return False
        if row["feedback_received"]:
            return True  # already processed

        conn.execute(
            "INSERT INTO feedback (detection_id, user_label, notes) VALUES (?, ?, ?)",
            (detection_id, user_label, notes),
        )
        conn.execute(
            "UPDATE detections SET feedback_received = 1 WHERE id = ?",
            (detection_id,),
        )

        verdict = row["verdict"]
        features = json.loads(row["features"] or "{}")
        correct = 1 if user_label.lower() == verdict.lower() else 0
        incorrect = 1 - correct

        metrics = _extract_metric_contributions(features)
        note_metrics = _note_adjustments(notes)
        for key, value in note_metrics.items():
            metrics[key] = metrics.get(key, 0.0) + value
        for metric, contribution in metrics.items():
            weight = min(1.0, max(0.0, contribution))
            conn.execute(
                """
                INSERT INTO metric_stats (metric, correct_count, incorrect_count)
                VALUES (?, ?, ?)
                ON CONFLICT(metric) DO UPDATE SET
                    correct_count = correct_count + ?,
                    incorrect_count = incorrect_count + ?
                """,
                (metric, correct * weight, incorrect * weight, correct * weight, incorrect * weight),
            )

    return True


def _extract_metric_contributions(features: Dict[str, Any]) -> Dict[str, float]:
    metrics: Dict[str, float] = {}

    watermark = features.get("watermark", {})
    if watermark.get("detected"):
        metrics["watermark"] = float(watermark.get("confidence", 0.5))

    face = features.get("face_analysis", {})
    if face.get("face_detected"):
        metrics["face_analysis"] = min(1.0, float(face.get("num_tracks", 1)) / 5.0)

    forensics = features.get("forensics", {})
    metrics["forensics_flicker"] = float(forensics.get("flicker_score", 0.5))
    metrics["forensics_prnu"] = 1.0 - float(forensics.get("prnu_score", 0.5))
    metrics["forensics_codec"] = float(forensics.get("codec_score", 0.5))

    av = features.get("av_analysis", {})
    metrics["audio_sync"] = 1.0 - float(av.get("sync_score", 0.5))

    artifacts = features.get("artifact_analysis", {})
    metrics["edge_artifacts"] = float(artifacts.get("edge_artifact_score", 0.5))
    metrics["texture_inconsistency"] = float(artifacts.get("texture_inconsistency", 0.5))
    metrics["color_anomaly"] = float(artifacts.get("color_anomaly_score", 0.5))
    metrics["freq_artifacts"] = float(artifacts.get("freq_artifact_score", 0.5))

    face_dyn = features.get("face_dynamics", {})
    metrics["mouth_exaggeration"] = float(face_dyn.get("mouth_exaggeration_score", 0.5))
    metrics["mouth_static"] = float(face_dyn.get("mouth_static_score", 0.5))
    metrics["eye_blink"] = float(face_dyn.get("eye_blink_anomaly", 0.5))
    metrics["face_symmetry"] = float(face_dyn.get("face_symmetry_drift", 0.5))

    quality = features.get("quality", {})
    if quality.get("status") == "low":
        metrics["low_quality_flag"] = 0.6

    scene_logic = features.get("scene_logic", {})
    metrics["scene_logic"] = float(scene_logic.get("incoherence_score", 0.5))

    return metrics


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    if isinstance(value, tuple):
        return [_sanitize(v) for v in value]
    if hasattr(value, "item") and callable(getattr(value, "item")):
        return _sanitize(value.item())
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, Number):
        return float(value)
    return value


def _note_adjustments(notes: Optional[str]) -> Dict[str, float]:
    if not notes:
        return {}
    lowered = notes.lower()
    adjustments: Dict[str, float] = {}
    keyword_map = {
        'mouth': 'mouth_exaggeration',
        'lip': 'mouth_static',
        'blink': 'eye_blink',
        'eye': 'eye_blink',
        'hand': 'face_symmetry',
        'finger': 'face_symmetry',
        'blur': 'low_quality_flag',
        'lighting': 'color_anomaly',
        'color': 'color_anomaly',
        'edge': 'edge_artifacts',
        'texture': 'texture_inconsistency',
        'audio': 'audio_sync',
    }
    for keyword, metric in keyword_map.items():
        if keyword in lowered:
            adjustments[metric] = max(adjustments.get(metric, 0.0), 0.15)
    return adjustments


def get_metric_weights() -> Dict[str, float]:
    _initialize()
    weights: Dict[str, float] = {}
    with _get_conn() as conn:
        cur = conn.execute("SELECT metric, correct_count, incorrect_count FROM metric_stats")
        for row in cur.fetchall():
            correct = row["correct_count"]
            incorrect = row["incorrect_count"]
            total = correct + incorrect
            # Default neutral weight
            weight = 1.0
            if total > 0:
                # Laplace-smoothed reliability in [0,1]
                reliability = (float(correct) + 1.0) / (float(total) + 2.0)
                # Confidence scaling based on evidence volume (logarithmic)
                try:
                    import math
                    log_factor = 0.5 + 0.5 * (math.log10(float(total) + 10.0) / math.log10(100.0))
                    log_factor = max(0.5, min(1.5, log_factor))
                except Exception:
                    log_factor = 1.0
                # Map reliability to weight around 1.0 with expand/contract range
                # reliability=0.5 -> 1.0; >0.5 up-weights, <0.5 down-weights
                delta = (reliability - 0.5) * 2.0  # [-1, 1]
                weight = 1.0 + delta * log_factor
                # Clamp more decisively to allow learning effect
                weight = max(0.3, min(2.2, weight))
            weights[row["metric"]] = float(weight)
    return weights

