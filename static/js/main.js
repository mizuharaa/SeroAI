// File upload and analysis handling
let currentFile = null;
let analysisInProgress = false;
let currentFeedbackId = null;
let feedbackSubmitted = false;
let feedbackChoice = null;
let currentJobId = null;
let currentAnalysisProgress = 0;
let progressPollInterval = null;

// Methods configuration
const methods = [
    {
        id: '1',
        name: 'Quality & Preprocessing',
        description: 'Assessing blur, compression, bitrate, and shake',
        icon: 'grid'
    },
    {
        id: '2',
        name: 'Watermark & OCR',
        description: 'Scanning for generator signatures and overlays',
        icon: 'eye'
    },
    {
        id: '3',
        name: 'Forensic Signals',
        description: 'Checking PRNU, flicker, and codec artifacts',
        icon: 'box'
    },
    {
        id: '4',
        name: 'Face Structure & Dynamics',
        description: 'Tracking faces, lip motion, and blink patterns',
        icon: 'eye'
    },
    {
        id: '5',
        name: 'Visual Artifact Heuristics',
        description: 'Evaluating edges, texture, color, and spectrum cues',
        icon: 'zap'
    },
    {
        id: '6',
        name: 'Scene Logic',
        description: 'Checking shot continuity and object persistence',
        icon: 'box'
    },
    {
        id: '7',
        name: 'Audio-Visual Sync',
        description: 'Measuring timing alignment between audio and video',
        icon: 'audio'
    },
    {
        id: '8',
        name: 'Fusion Decision',
        description: 'Combining all evidence into a final verdict',
        icon: 'grid'
    }
];

const stageToMethodIndex = {
    quality: 0,
    watermark: 1,
    forensics: 2,
    face_analysis: 3,
    face_dynamics: 3,
    artifact: 4,
    scene_logic: 5,
    audio_visual: 6,
    fusion: 7
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadZone();
    initializeFileInput();
    initializeFeedback();
    // Bind buttons (CSP-safe: no inline handlers)
    document.getElementById('newAnalysisBtn')?.addEventListener('click', () => {
        resetAnalysis();
        // scroll to top for a clear start
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    document.getElementById('chooseFileBtn')?.addEventListener('click', () => {
        document.getElementById('fileInput')?.click();
    });
    document.getElementById('removeFileBtn')?.addEventListener('click', () => {
        removeFile();
    });
});

// Basic HTML-escape to prevent DOM XSS when rendering server-provided strings
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Initialize upload zone
function initializeUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // Click to upload
    uploadZone.addEventListener('click', (e) => {
        if (!e.target.closest('.selected-file')) {
            fileInput.click();
        }
    });
}

// Initialize file input
function initializeFileInput() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(file) {
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'video/mp4', 'video/quicktime', 'video/x-msvideo'];
    if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type. Please upload PNG, JPG, MP4, MOV, or AVI files.');
        return;
    }

    // Validate file size (500MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size exceeds 500MB limit.');
        return;
    }

    currentFile = file;
    displaySelectedFile(file);
    startAnalysis(file);
}

// Display selected file
function displaySelectedFile(file) {
    const selectedFileDiv = document.getElementById('selectedFile');
    const fileNameSpan = document.getElementById('fileName');
    const fileIcon = selectedFileDiv.querySelector('i');
    
    // Set appropriate icon based on file type
    if (file.type.startsWith('image/')) {
        fileIcon.className = 'fas fa-file-image';
    } else if (file.type.startsWith('video/')) {
        fileIcon.className = 'fas fa-file-video';
    } else {
        fileIcon.className = 'fas fa-file';
    }
    
    fileNameSpan.textContent = file.name;
    selectedFileDiv.style.display = 'flex';
}

// Remove file
function removeFile() {
    currentFile = null;
    document.getElementById('selectedFile').style.display = 'none';
    document.getElementById('fileInput').value = '';
    resetAnalysis();
}

// Start analysis
async function startAnalysis(file) {
    if (analysisInProgress) return;
    
    analysisInProgress = true;
    currentAnalysisProgress = 0;
    currentJobId = null;
    if (progressPollInterval) {
        clearInterval(progressPollInterval);
        progressPollInterval = null;
    }
    
    // Show analysis section
    showAnalysisSection();
    
    // Hide other sections
    document.getElementById('heroSection').style.display = 'none';
    document.getElementById('educationalSection').style.display = 'none';
    
    // Upload file
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error('Upload failed');
        }
        
        const uploadData = await uploadResponse.json();
        document.getElementById('analyzingFileName').textContent = uploadData.original_name;
        
        prepareMethodList();
        updateProgress(0);
        updateMethodStatusesByStage(null, []);
        
        // Start actual analysis asynchronously
        const analysisResponse = await fetch('/analyze/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: uploadData.filename, originalName: uploadData.original_name })
        });
        
        if (!analysisResponse.ok) {
            throw new Error('Analysis failed');
        }
        
        const analysisData = await analysisResponse.json();
        const jobId = analysisData.jobId;
        if (!jobId) {
            throw new Error('Analysis job not created');
        }
        currentJobId = jobId;
        startProgressPolling(jobId, uploadData.original_name);
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during analysis: ' + error.message);
        resetAnalysis();
    } finally {
        analysisInProgress = false;
    }
}

function prepareMethodList() {
    const methodsList = document.getElementById('methodsList');
    methodsList.innerHTML = '';
    
    // Create method items
    methods.forEach((method, index) => {
        const methodItem = createMethodItem(method, 'pending');
        methodsList.appendChild(methodItem);
    });
}

// Update progress
function updateProgress(progress) {
    const progressFill = document.getElementById('overallProgress');
    const progressText = document.getElementById('progressText');
    
    progressFill.style.width = progress + '%';
    progressText.textContent = Math.round(progress) + '%';
}

function updateMethodStatusesByStage(currentStage, completedStages) {
    methods.forEach((method, index) => {
        updateMethodStatus(index, 'pending');
    });
    if (Array.isArray(completedStages)) {
        completedStages.forEach(stage => {
            const idx = stageToMethodIndex[stage];
            if (idx !== undefined) {
                updateMethodStatus(idx, 'complete');
            }
        });
    }
    if (currentStage) {
        const idx = stageToMethodIndex[currentStage] ?? stageToMethodIndex[currentStage.replace('face_dynamics', 'face_analysis')];
        if (idx !== undefined) {
            updateMethodStatus(idx, 'analyzing');
        }
    }
}

function startProgressPolling(jobId, fileName) {
    if (progressPollInterval) {
        clearInterval(progressPollInterval);
    }
    let consecutiveErrors = 0;
    const poll = async () => {
        try {
            const response = await fetch(`/analyze/status/${jobId}`);
            if (!response.ok) {
                throw new Error('Status request failed');
            }
            const data = await response.json();
            consecutiveErrors = 0;
            if (typeof data.progress === 'number') {
                updateProgress(data.progress);
            }
            updateMethodStatusesByStage(data.stage, data.completedStages || []);
            if (data.status === 'completed' && data.result) {
                clearInterval(progressPollInterval);
                progressPollInterval = null;
                analysisInProgress = false;
                showResults(data.result, fileName);
                currentJobId = null;
            } else if (data.status === 'error') {
                clearInterval(progressPollInterval);
                progressPollInterval = null;
                analysisInProgress = false;
                alert(data.error || 'Analysis failed');
                resetAnalysis();
            } else if (data.status === 'completed' && !data.result) {
                // Edge case: backend finished but result not yet attached; retry once more
                setTimeout(poll, 500);
                return;
            }
        } catch (error) {
            console.error('Progress polling error:', error);
            consecutiveErrors += 1;
            if (consecutiveErrors >= 5) {
                clearInterval(progressPollInterval);
                progressPollInterval = null;
                analysisInProgress = false;
                alert('Lost connection while tracking analysis progress.');
                resetAnalysis();
            }
        }
    };
    poll();
    progressPollInterval = setInterval(poll, 1500);
}

// Create method item
function createMethodItem(method, status) {
    const methodItem = document.createElement('div');
    methodItem.className = `method-item ${status}`;
    methodItem.id = `method-${method.id}`;
    
    const statusIcon = getStatusIcon(status);
    const iconClass = getIconClass(method.icon);
    
    methodItem.innerHTML = `
        <div class="method-status ${status}">
            ${statusIcon}
        </div>
        <div class="method-info">
            <h4>${method.name}</h4>
            <p>${method.description}</p>
        </div>
    `;
    
    return methodItem;
}

// Get status icon
function getStatusIcon(status) {
    switch(status) {
        case 'pending':
            return '<i class="fas fa-clock"></i>';
        case 'analyzing':
            return '<i class="fas fa-spinner"></i>';
        case 'complete':
            return '<i class="fas fa-check"></i>';
        default:
            return '';
    }
}

// Get icon class
function getIconClass(icon) {
    return icon;
}

// Update method status
function updateMethodStatus(index, status) {
    const methodItem = document.getElementById(`method-${methods[index].id}`);
    if (methodItem) {
        methodItem.className = `method-item ${status}`;
        const statusDiv = methodItem.querySelector('.method-status');
        statusDiv.className = `method-status ${status}`;
        statusDiv.innerHTML = getStatusIcon(status);
    }
}

// Show analysis section
function showAnalysisSection() {
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('analysisSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
}

// Show results
function showResults(data, fileName) {
    // Update progress to 100%
    updateProgress(100);
    
    // Mark all methods as complete (only the ones that will be shown)
    for (let i = 0; i < methods.length; i++) {
        updateMethodStatus(i, 'complete');
    }
    
    // Wait a bit then show results
    setTimeout(() => {
        document.getElementById('analysisSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        
        // Update results
        const verdict = data.verdict || 'UNSURE';
        const probAi = data.probAi || (data.overallScore / 100);
        const overallScore = data.overallScore || Math.round(probAi * 100);
        
        document.getElementById('overallScoreValue').textContent = overallScore + '%';
        document.getElementById('resultFileName').textContent = fileName;
        document.getElementById('processingTime').textContent = data.processingTime + 's';
        
        // Update verdict display
        updateVerdictDisplay(verdict, overallScore);
        
        // Update generator hint if available
        if (data.generatorHint) {
            document.getElementById('generatorHint').style.display = 'flex';
            document.getElementById('generatorHintText').textContent = data.generatorHint;
        } else {
            document.getElementById('generatorHint').style.display = 'none';
        }
        
        currentFeedbackId = data.feedbackId || null;
        feedbackSubmitted = false;
    feedbackChoice = null;
        const notesEl = document.getElementById('feedbackNotes');
        if (notesEl) notesEl.value = '';
        updateFeedbackUI(false, '');
        
        // Show quality warning if needed
        if (data.quality && data.quality.status === 'low') {
            showQualityWarning(data.quality.issues);
        }
        
        // Display result details
        displayResultDetails(data.results);
        
    }, 500);
}

// Display result details
function displayResultDetails(results) {
    const resultsDetails = document.getElementById('resultsDetails');
    resultsDetails.innerHTML = '';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';

        const iconBg = getIconBgForMethod(result.icon);

        const header = document.createElement('h4');
        const iconSpan = document.createElement('span');
        iconSpan.className = `result-icon ${iconBg}`;
        const iconI = document.createElement('i');
        iconI.className = `fas ${getIconForMethod(result.icon)}`;
        iconSpan.appendChild(iconI);
        header.appendChild(iconSpan);
        header.insertAdjacentText('beforeend', ` ${String(result.method || '')}`);

        const scoreDiv = document.createElement('div');
        scoreDiv.className = 'result-score';
        scoreDiv.textContent = `${Math.round(result.score || 0)}%`;

        const confP = document.createElement('p');
        confP.style.color = 'var(--gray-600)';
        confP.style.fontSize = '14px';
        confP.style.marginBottom = '8px';
        confP.textContent = `Confidence: ${Math.round(result.confidence || 0)}%`;

        const ul = document.createElement('ul');
        ul.className = 'result-details-list';
        (result.details || []).forEach(detail => {
            const li = document.createElement('li');
            li.textContent = String(detail ?? '');
            ul.appendChild(li);
        });

        resultItem.appendChild(header);
        resultItem.appendChild(scoreDiv);
        resultItem.appendChild(confP);
        resultItem.appendChild(ul);

        resultsDetails.appendChild(resultItem);
    });
}

// Get icon for method
function getIconForMethod(icon) {
    const icons = {
        'grid': 'fa-th',
        'zap': 'fa-bolt',
        'box': 'fa-cube',
        'waves': 'fa-wave-square',
        'audio': 'fa-volume-up',
        'eye': 'fa-eye'
    };
    return icons[icon] || 'fa-circle';
}

// Get icon class for method
function getIconClassForMethod(icon) {
    return icon;
}

// Get icon background for method
function getIconBgForMethod(icon) {
    const backgrounds = {
        'grid': 'grid',
        'zap': 'zap',
        'box': 'box',
        'waves': 'waves',
        'audio': 'audio',
        'eye': 'grid'
    };
    return backgrounds[icon] || 'grid';
}

// Reset analysis
function resetAnalysis() {
    analysisInProgress = false;
    currentFile = null;
    currentFeedbackId = null;
    feedbackSubmitted = false;
    feedbackChoice = null;
    currentJobId = null;
    currentAnalysisProgress = 0;
    
    if (progressPollInterval) {
        clearInterval(progressPollInterval);
        progressPollInterval = null;
    }
    
    // Reset UI
    document.getElementById('uploadSection').style.display = 'block';
    document.getElementById('analysisSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('heroSection').style.display = 'block';
    document.getElementById('educationalSection').style.display = 'block';
    document.getElementById('selectedFile').style.display = 'none';
    document.getElementById('fileInput').value = '';
    
    // Reset progress
    updateProgress(0);
    updateFeedbackUI(false, '');
    currentFeedbackId = null;
    const notesEl = document.getElementById('feedbackNotes');
    if (notesEl) notesEl.value = '';
    const notesContainer = document.getElementById('feedbackNotesContainer');
    if (notesContainer) notesContainer.style.display = 'none';
    const submitBtn = document.getElementById('feedbackSubmitBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submit';
    }
    const realBtn = document.getElementById('feedbackRealBtn');
    const aiBtn = document.getElementById('feedbackAiBtn');
    realBtn?.classList.remove('selected');
    aiBtn?.classList.remove('selected');
}

// Feedback handling
function initializeFeedback() {
    const feedbackCard = document.getElementById('feedbackCard');
    if (!feedbackCard) return;
    
    const realBtn = document.getElementById('feedbackRealBtn');
    const aiBtn = document.getElementById('feedbackAiBtn');
    const notesContainer = document.getElementById('feedbackNotesContainer');
    const submitBtn = document.getElementById('feedbackSubmitBtn');
    
    realBtn?.addEventListener('click', () => handleFeedbackChoice('REAL'));
    aiBtn?.addEventListener('click', () => handleFeedbackChoice('AI'));
    submitBtn?.addEventListener('click', () => submitFeedback(feedbackChoice));
}

function handleFeedbackChoice(label) {
    if (!currentFeedbackId || feedbackSubmitted) {
        updateFeedbackUI(true, feedbackSubmitted ? 'Feedback already submitted. Thank you!' : 'Feedback session expired.');
        return;
    }
    
    feedbackChoice = label;
    const notesContainer = document.getElementById('feedbackNotesContainer');
    const submitBtn = document.getElementById('feedbackSubmitBtn');
    const realBtn = document.getElementById('feedbackRealBtn');
    const aiBtn = document.getElementById('feedbackAiBtn');
    
    if (realBtn) realBtn.classList.remove('selected');
    if (aiBtn) aiBtn.classList.remove('selected');
    if (label === 'REAL' && realBtn) realBtn.classList.add('selected');
    if (label === 'AI' && aiBtn) aiBtn.classList.add('selected');
    
    if (notesContainer) notesContainer.style.display = 'block';
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = `Submit (${label === 'REAL' ? 'Real' : 'AI'})`;
    }
    
    updateFeedbackUI(false, 'Tell us if the verdict was correct, then submit.');
}

async function submitFeedback(label) {
    if (!currentFeedbackId || feedbackSubmitted || !label) {
        updateFeedbackUI(true, feedbackSubmitted ? 'Feedback already submitted. Thank you!' : 'Select an option first.');
        return;
    }
    
    updateFeedbackUI(false, 'Submitting feedback...');
    
    try {
        const notes = document.getElementById('feedbackNotes').value.trim();
        const response = await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                feedbackId: currentFeedbackId,
                userLabel: label,
                notes: notes || null
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit feedback');
        }
        
        feedbackSubmitted = true;
        updateFeedbackUI(true, 'Thanks! Your feedback will help improve the detector.');
        const submitBtn = document.getElementById('feedbackSubmitBtn');
        if (submitBtn) submitBtn.disabled = true;
    } catch (error) {
        console.error('Feedback error:', error);
        updateFeedbackUI(false, 'Could not submit feedback. Please try again later.');
    }
}

function updateFeedbackUI(completed, message) {
    const feedbackCard = document.getElementById('feedbackCard');
    const statusEl = document.getElementById('feedbackStatus');
    const realBtn = document.getElementById('feedbackRealBtn');
    const aiBtn = document.getElementById('feedbackAiBtn');
    const notesContainer = document.getElementById('feedbackNotesContainer');
    const submitBtn = document.getElementById('feedbackSubmitBtn');
    const notesEl = document.getElementById('feedbackNotes');
    
    if (!feedbackCard) return;
    feedbackCard.style.display = currentFeedbackId ? 'block' : 'none';
    
    if (statusEl) {
        statusEl.textContent = message || '';
    }
    
    const disabled = feedbackSubmitted || completed && message.includes('Thanks');
    if (realBtn) realBtn.disabled = disabled;
    if (aiBtn) aiBtn.disabled = disabled;
    
    if (!currentFeedbackId || feedbackSubmitted) {
        feedbackChoice = null;
        if (notesContainer) notesContainer.style.display = 'none';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submit';
        }
        if (notesEl) notesEl.value = '';
        if (realBtn) realBtn.classList.remove('selected');
        if (aiBtn) aiBtn.classList.remove('selected');
    }
}

// Update verdict display
function updateVerdictDisplay(verdict, score) {
    const scoreCircle = document.querySelector('.score-circle');
    const scoreLabel = document.querySelector('.score-label');
    
    if (!scoreCircle) return;
    
    // Update label based on verdict
    const verdictText = {
        'AI': 'AI Generated',
        'REAL': 'Authentic',
        'UNSURE': 'Uncertain',
        'ABSTAIN': 'Cannot Determine'
    };
    
    if (scoreLabel) {
        scoreLabel.textContent = verdictText[verdict] || 'Deepfake Probability';
    }
    
    // Update color based on verdict
    scoreCircle.style.background = {
        'AI': 'linear-gradient(135deg, #ef4444, #dc2626)',
        'REAL': 'linear-gradient(135deg, #10b981, #059669)',
        'UNSURE': 'linear-gradient(135deg, #f59e0b, #d97706)',
        'ABSTAIN': 'linear-gradient(135deg, #6b7280, #4b5563)'
    }[verdict] || 'linear-gradient(135deg, #2563eb, #9333ea)';
}

// Show quality warning
function showQualityWarning(issues) {
    // Create or update quality warning element
    let warningEl = document.getElementById('qualityWarning');
    if (!warningEl) {
        warningEl = document.createElement('div');
        warningEl.id = 'qualityWarning';
        warningEl.className = 'card warning-card';
        warningEl.style.marginTop = '16px';
        const resultsCard = document.querySelector('.results-card');
        if (resultsCard) {
            resultsCard.parentNode.insertBefore(warningEl, resultsCard.nextSibling);
        }
    }
    
    warningEl.innerHTML = `
        <p><strong>Quality Warning:</strong> Video quality may affect detection accuracy. Issues detected: ${issues.join(', ')}</p>
    `;
}

// Mobile menu (if needed)
document.getElementById('mobileMenuBtn')?.addEventListener('click', function() {
    // Mobile menu functionality can be added here
    alert('Mobile menu - Settings and PRD options');
});

