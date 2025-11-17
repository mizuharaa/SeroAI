from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import os
import sys
import uuid
from werkzeug.utils import secure_filename
import json
import time
import warnings
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.service import analyze_media
from core.feedback_store import store_feedback
from app.analysis_manager import start_job, get_job
from app.result_formatter import build_ui_response
from core.fusion import DeepfakeFusion

# ----------------------------
# Reduce noisy runtime logs
# ----------------------------
# TensorFlow/mediapipe
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # 0=all,1=INFO,2=WARNING,3=ERROR
try:
    import absl.logging as absl_logging  # type: ignore
    absl_logging.set_verbosity(absl_logging.ERROR)
    logging.getLogger('absl').setLevel(logging.ERROR)
except Exception:
    pass
# Protobuf deprecation noise
warnings.filterwarnings(
    "ignore",
    message=".*SymbolDatabase.GetPrototype\\(\\) is deprecated.*",
    category=Warning,
)
# Show startup info (keep standard INFO so users see the URL)
logging.getLogger('werkzeug').setLevel(logging.INFO)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Warm up fusion model at startup so users see a clear log line
_ = DeepfakeFusion()

def allowed_file(filename: str) -> bool:
    return bool(filename) and '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

WEBUI_DIR = os.path.join(os.path.dirname(__file__), 'webui')
WEBUI_DIST_DIR = os.path.join(WEBUI_DIR, 'dist')


@app.route('/')
def index():
    """
    Serve the React build if available; otherwise fall back to the legacy template.
    """
    dist_index = os.path.join(WEBUI_DIST_DIR, 'index.html')
    if os.path.exists(dist_index):
        return send_file(dist_index)
    # If the build doesn't exist yet, fall back to the old template
    # and instruct the developer in console to build the webui.
    print("[webui] dist/index.html not found. Run `npm install && npm run build` in SeroAI/webui to enable the new UI.")
    return render_template('index.html')


@app.route('/detect')
def detect_route():
    """
    Deepfake detection SPA route - serve the same React index so the client-side router can render /detect.
    """
    dist_index = os.path.join(WEBUI_DIST_DIR, 'index.html')
    if os.path.exists(dist_index):
        return send_file(dist_index)
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_webui_assets(filename: str):
    """
    Serve Vite build assets when present (SeroAI/webui/dist/assets/*).
    """
    assets_dir = os.path.join(WEBUI_DIST_DIR, 'assets')
    if os.path.exists(os.path.join(assets_dir, filename)):
        return send_from_directory(assets_dir, filename)
    return jsonify({'error': 'Asset not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    original_filename: str = (file.filename or '')
    if not original_filename:
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(original_filename):
        # Generate unique filename
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_name': original_filename
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Run new deepfake detection pipeline
        result = analyze_media(filepath)
        payload = build_ui_response(result)
        return jsonify(payload)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/analyze/start', methods=['POST'])
def analyze_start():
    try:
        data = request.get_json(force=True)
        filename = data.get('filename')
        original_name = data.get('originalName') or data.get('original_name') or filename
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        job_id = start_job(filepath, original_name)
        return jsonify({'success': True, 'jobId': job_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/analyze/status/<job_id>', methods=['GET'])
def analyze_status(job_id):
    try:
        job = get_job(job_id)
        if job is None:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(job)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json(force=True)
        feedback_id = data.get('feedbackId')
        user_label = data.get('userLabel')
        notes = data.get('notes')
        
        if not feedback_id or not user_label:
            return jsonify({'error': 'feedbackId and userLabel required'}), 400
        
        stored = store_feedback(feedback_id, user_label, notes)
        if not stored:
            return jsonify({'error': 'Feedback session not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("\nDeceptor.ai starting at http://127.0.0.1:5000  (or http://localhost:5000)\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

