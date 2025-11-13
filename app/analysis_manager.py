import threading
import time
import uuid
from typing import Any, Dict, Optional

from app.service import analyze_media
from app.result_formatter import build_ui_response

_jobs: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def start_job(file_path: str, original_name: str) -> str:
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            'status': 'queued',
            'progress': 0.0,
            'stage': None,
            'message': 'Queued',
            'completedStages': [],
            'result': None,
            'error': None,
            'file_path': file_path,
            'original_name': original_name,
            'startedAt': time.time()
        }
    thread = threading.Thread(
        target=_run_job,
        args=(job_id, file_path, original_name),
        daemon=True
    )
    thread.start()
    return job_id


def _run_job(job_id: str, file_path: str, original_name: str) -> None:
    def progress_callback(progress: float, stage: Optional[str], message: str, completed: bool = False):
        with _lock:
            job = _jobs.get(job_id)
            if not job or job.get('status') in ('completed', 'error'):
                return
            job['status'] = 'running'
            job['progress'] = max(job.get('progress', 0.0), min(progress, 100.0))
            job['message'] = message
            if completed and stage:
                completedStages = job.setdefault('completedStages', [])
                if stage not in completedStages:
                    completedStages.append(stage)
                job['stage'] = None
            elif stage:
                job['stage'] = stage

    try:
        progress_callback(2.0, 'quality', 'Preparing media', completed=False)
        result = analyze_media(file_path, progress_callback=progress_callback)
        ui_payload = build_ui_response(result)
        with _lock:
            job = _jobs.get(job_id)
            if job is None:
                return
            job['status'] = 'completed'
            job['progress'] = 100.0
            job['stage'] = None
            job['message'] = 'Analysis complete'
            job['result'] = ui_payload
            job.setdefault('completedStages', [])
    except Exception as exc:
        with _lock:
            job = _jobs.get(job_id)
            if job is None:
                return
            job['status'] = 'error'
            job['error'] = str(exc)
            job['stage'] = None
            job['message'] = 'Error during analysis'


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        return {
            'status': job.get('status'),
            'progress': job.get('progress', 0.0),
            'stage': job.get('stage'),
            'message': job.get('message'),
            'completedStages': list(job.get('completedStages', [])),
            'result': job.get('result') if job.get('status') == 'completed' else None,
            'error': job.get('error')
        }

