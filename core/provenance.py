"""Provenance and content credentials (C2PA) probe.

This is a light, optional wrapper. If c2pa libs are not installed,
the function returns 'unknown' without failing the pipeline.
"""
from __future__ import annotations

from typing import Dict
import os


def check_provenance(path: str) -> Dict:
    """Return a provenance summary.
    
    {
      'has_manifest': bool,
      'valid': bool|None,
      'generator': str|None,
      'ai': 'true'|'false'|'unknown',
      'reason': str
    }
    """
    result = {
        'has_manifest': False,
        'valid': None,
        'generator': None,
        'ai': 'unknown',
        'reason': 'no_c2pa_lib'
    }
    try:
        # Optional imports (prefer c2pa-python if present)
        import c2pa  # type: ignore
        result['reason'] = 'no_manifest'
        if not os.path.exists(path):
            result['reason'] = 'file_not_found'
            return result
        try:
            # API surface differs between versions; keep robust
            manifest = c2pa.read_manifest(path)  # type: ignore[attr-defined]
            if manifest is None:
                return result
            result['has_manifest'] = True
            # validity may not be available in all toolkits; default to None
            try:
                result['valid'] = bool(getattr(manifest, 'valid', True))
            except Exception:
                result['valid'] = None
            # Extract claimed generator/tool if available
            gen = None
            try:
                claim = getattr(manifest, 'claim', None)
                gen = getattr(claim, 'generator', None) if claim else None
            except Exception:
                gen = None
            result['generator'] = gen
            # Basic policy: if generator mentions 'veo','sora','text-to-video'
            gen_l = (gen or '').lower()
            if any(k in gen_l for k in ['veo', 'sora', 'text-to-video', 'runway', 'pika']):
                result['ai'] = 'true'
                result['reason'] = 'c2pa_ai_generator'
            else:
                result['ai'] = 'unknown'
                result['reason'] = 'c2pa_present'
        except Exception:
            # Manifest parsing error
            result['reason'] = 'manifest_error'
    except Exception:
        # c2pa lib not installed; safe fallback
        result['reason'] = 'no_c2pa_lib'
    return result


