from typing import Dict, List


METHOD_NAME_MAP = {
    'watermark': 'Watermark Detection',
    'face_analysis': 'Face Analysis',
    'flicker': 'Temporal Flicker Analysis',
    'prnu': 'Sensor Pattern Analysis',
    'audio_sync': 'Audio-Visual Sync',
    'edge_artifacts': 'Edge Artifact Consistency',
    'texture_inconsistency': 'Texture Stability Check',
    'color_anomaly': 'Color Cohesion',
    'frequency_artifact': 'Frequency Spectrum',
    'mouth_exaggeration': 'Mouth Dynamics',
    'mouth_static': 'Lip Motion Variability',
    'eye_blink': 'Eye Blink Pattern',
    'face_symmetry': 'Facial Symmetry Drift'
}

ICON_MAP = {
    'watermark': 'eye',
    'face_analysis': 'eye',
    'flicker': 'waves',
    'prnu': 'grid',
    'audio_sync': 'audio',
    'edge_artifacts': 'grid',
    'texture_inconsistency': 'box',
    'color_anomaly': 'zap',
    'frequency_artifact': 'waves',
    'mouth_exaggeration': 'audio',
    'mouth_static': 'box',
    'eye_blink': 'eye',
    'face_symmetry': 'grid'
}


def build_ui_response(result: Dict) -> Dict:
    prob_ai = result.get('prob_ai', 0.5)
    verdict = result.get('verdict', 'UNSURE')
    reasons: List[Dict] = result.get('reasons', [])
    quality = result.get('quality', {})
    debug = result.get('debug', {})

    ui_results = []
    for reason in reasons[:5]:
        name = reason.get('name')
        method_name = METHOD_NAME_MAP.get(name, name.replace('_', ' ').title() if name else 'Analysis')
        icon = ICON_MAP.get(name, 'box')
        confidence = float(reason.get('confidence', 0.5))
        ui_results.append({
            'method': method_name,
            'score': int(confidence * 100),
            'confidence': int(confidence * 100),
            'icon': icon,
            'details': [reason.get('detail', 'Analysis performed')]
        })

    generator_hint = None
    if debug.get('watermark_detected') or any(r.get('name') == 'watermark' for r in reasons):
        watermark_detail = next((r for r in reasons if r.get('name') == 'watermark'), None)
        if watermark_detail:
            generator_hint = f"Watermark detected: {watermark_detail.get('detail', 'AI generator')}"
    elif prob_ai > 0.7:
        generator_hint = "High probability of AI-generated content"

    processing_time = round(debug.get('processing_time', 0.0), 2)

    return {
        'success': True,
        'verdict': verdict,
        'overallScore': int(prob_ai * 100),
        'probAi': prob_ai,
        'results': ui_results,
        'reasons': reasons,
        'processingTime': processing_time,
        'generatorHint': generator_hint,
        'feedbackId': result.get('feedback_id'),
        'quality': {
            'status': quality.get('status', 'good'),
            'issues': quality.get('issues', [])
        }
    }

