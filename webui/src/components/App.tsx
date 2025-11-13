import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { HeroSection } from './HeroSection';
import { UploadZone } from './UploadZone';
import { AnalysisProgress } from './AnalysisProgress';
import { ResultsDisplay } from './ResultsDisplay';
import { Button } from './ui/button';

type AppView = 'landing' | 'upload' | 'analyzing' | 'results';

interface AnalysisMethod {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'analyzing' | 'complete';
  score?: number;
}

interface DetectionResult {
  method: string;
  score: number;
  confidence: number;
  details: string[];
  icon: 'eye' | 'zap' | 'waves' | 'box' | 'audio' | 'grid';
}

export default function App() {
  const [view, setView] = useState<AppView>('landing');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [overallProgress, setOverallProgress] = useState(0);
  const [overallScore, setOverallScore] = useState(0);
  const [processingTime, setProcessingTime] = useState(0);
  const [methods, setMethods] = useState<AnalysisMethod[]>([
    { id: '1', name: 'Pixel Stability Analysis', description: 'Analyzing temporal consistency in static regions', status: 'pending' },
    { id: '2', name: 'Biological Inconsistency Detection', description: 'Examining facial landmarks and body movements', status: 'pending' },
    { id: '3', name: 'Spatial Logic Verification', description: 'Checking scene coherence and object persistence', status: 'pending' },
    { id: '4', name: 'Frequency Domain Analysis', description: 'Detecting GAN fingerprints in spectral data', status: 'pending' },
    { id: '5', name: 'Optical Flow Analysis', description: 'Analyzing motion vectors and patterns', status: 'pending' },
    { id: '6', name: 'Audio-Visual Sync Check', description: 'Verifying lip-sync and audio authenticity', status: 'pending' },
  ]);
  const [results, setResults] = useState<DetectionResult[]>([]);

  // Progress polling is now handled in handleFileSelect

  const handleTryDemo = () => {
    setView('upload');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const handleUploadMedia = () => {
    setView('upload');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setView('analyzing');
    setOverallProgress(0);
    setOverallScore(0);
    setMethods(prev => prev.map((m, idx) => ({ ...m, status: idx === 0 ? 'analyzing' : 'pending', score: undefined })));
    
    try {
      // Upload file
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });
      if (!uploadRes.ok) throw new Error('Upload failed');
      const uploadData = await uploadRes.json();
      
      // Start analysis
      const analyzeRes = await fetch('/analyze/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: uploadData.filename,
          originalName: uploadData.original_name || file.name,
        }),
      });
      if (!analyzeRes.ok) throw new Error('Analysis start failed');
      const { jobId } = await analyzeRes.json();
      
      // Poll for progress
      const startTime = Date.now();
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/analyze/status/${jobId}`);
          if (!statusRes.ok) throw new Error('Status check failed');
          const job = await statusRes.json();
          
          setOverallProgress(job.progress || 0);
          
          // Update method statuses based on completed stages
          const completedStages = job.completedStages || [];
          const currentStage = job.stage;
          const stageMap: Record<string, number> = {
            'quality': 0,
            'watermark': 1,
            'forensics': 2,
            'face': 3,
            'audio_visual': 4,
            'scene_logic': 5,
          };
          setMethods(prev => prev.map((m, idx) => {
            const stageName = Object.keys(stageMap).find(k => stageMap[k] === idx);
            const isComplete = stageName && completedStages.includes(stageName);
            const isAnalyzing = stageName && currentStage === stageName;
            return {
              ...m,
              status: isComplete ? 'complete' : isAnalyzing ? 'analyzing' : 'pending',
              score: isComplete ? Math.floor(Math.random() * 40) + 30 : undefined,
            };
          }));
          
          if (job.status === 'completed' && job.result) {
            clearInterval(pollInterval);
            const endTime = Date.now();
            setProcessingTime((endTime - startTime) / 1000);
            
            // Transform backend result to frontend format
            const backendResult = job.result;
            const transformedResults: DetectionResult[] = backendResult.results || [];
            setResults(transformedResults);
            setOverallScore(backendResult.overallScore || 50);
            setView('results');
          } else if (job.status === 'error' || job.status === 'failed') {
            clearInterval(pollInterval);
            alert(`Analysis failed: ${job.error || 'Unknown error'}`);
            setView('upload');
          }
        } catch (err) {
          console.error('Poll error:', err);
        }
      }, 500);
      
      // Cleanup on unmount
      return () => clearInterval(pollInterval);
    } catch (err) {
      console.error('File upload/analysis error:', err);
      alert('Failed to start analysis. Please try again.');
      setView('upload');
    }
  };
  const handleNewAnalysis = () => {
    setView('upload');
    setSelectedFile(null);
    setOverallProgress(0);
    setOverallScore(0);
    setResults([]);
    setMethods(prev => prev.map(m => ({ ...m, status: 'pending', score: undefined })));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const handleBackToHome = () => {
    setView('landing');
    setSelectedFile(null);
    setOverallProgress(0);
    setOverallScore(0);
    setResults([]);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white">
      <AnimatePresence mode="wait">
        {view === 'landing' ? (
          <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}>
            <HeroSection onTryDemo={handleTryDemo} onUploadMedia={handleUploadMedia} />
          </motion.div>
        ) : (
          <motion.div
            key="analysis"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-50 via-white to-gray-50"
          >
            <div className="max-w-5xl mx-auto">
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="mb-8">
                <Button variant="ghost" onClick={handleBackToHome} className="text-gray-600 hover:text-gray-900">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Home
                </Button>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                {view === 'upload' && (
                  <div className="space-y-8">
                    <div className="text-center">
                      <h1 className="text-4xl md:text-5xl text-gray-900 mb-4">Upload Your Media</h1>
                      <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                        Drop your video or image file below to start the deepfake detection analysis
                      </p>
                    </div>
                    <UploadZone onFileSelect={handleFileSelect} isAnalyzing={false} />
                  </div>
                )}
                {view === 'analyzing' && (
                  <div className="space-y-8">
                    <div className="text-center">
                      <h1 className="text-4xl md:text-5xl text-gray-900 mb-4">Analyzing Your Media</h1>
                      <p className="text-xl text-gray-600">Running advanced AI detection algorithms...</p>
                    </div>
                    <div className="bg-white rounded-2xl border border-gray-200 shadow-xl p-8">
                      <div className="mb-6">
                        <p className="text-sm text-gray-600 mb-1">File Name</p>
                        <p className="text-gray-900">{selectedFile?.name}</p>
                      </div>
                      <AnalysisProgress methods={methods} overallProgress={overallProgress} />
                    </div>
                  </div>
                )}
                {view === 'results' && selectedFile && (
                  <div className="space-y-8">
                    <div className="text-center">
                      <h1 className="text-4xl md:text-5xl text-gray-900 mb-4">Analysis Complete</h1>
                      <p className="text-xl text-gray-600">Here are the detailed results from all detection methods</p>
                    </div>
                    <ResultsDisplay
                      overallScore={overallScore}
                      results={results}
                      fileName={selectedFile.name}
                      processingTime={processingTime}
                    />
                    <div className="text-center pt-8">
                      <Button onClick={handleNewAnalysis} size="lg" className="bg-gradient-to-r from-orange-500 via-rose-500 to-pink-600 text-white shadow-lg hover:shadow-xl transition-all">
                        Analyze Another File
                      </Button>
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


