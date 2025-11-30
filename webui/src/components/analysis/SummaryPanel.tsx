import React from 'react';
import { motion } from 'framer-motion';
import { ScoreRing } from './ScoreRing';
import { FileVideo, Clock, Database, Shield } from 'lucide-react';

interface SummaryPanelProps {
  fileName: string;
  overallScore: number;
  processingTime: number;
  framesAnalyzed?: number;
  className?: string;
}

export function SummaryPanel({
  fileName,
  overallScore,
  processingTime,
  framesAnalyzed = 0,
  className = '',
}: SummaryPanelProps) {
  const getRiskLabel = (score: number) => {
    if (score <= 20) return { text: 'Low Risk', color: 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400' };
    if (score <= 40) return { text: 'Low-Medium Risk', color: 'bg-lime-500/20 border-lime-500/50 text-lime-400' };
    if (score <= 60) return { text: 'Medium Risk', color: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400' };
    if (score <= 80) return { text: 'High Risk', color: 'bg-orange-500/20 border-orange-500/50 text-orange-400' };
    return { text: 'Very High Risk', color: 'bg-red-500/20 border-red-500/50 text-red-400' };
  };

  const risk = getRiskLabel(overallScore);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className={`lg:sticky lg:top-24 ${className}`}
    >
      <div className="relative overflow-hidden bg-gradient-to-br from-cyan-500/15 via-purple-500/10 to-pink-500/15 backdrop-blur-xl border-2 border-cyan-500/30 rounded-2xl shadow-2xl shadow-cyan-500/20 p-8 space-y-8 before:absolute before:inset-0 before:bg-gradient-to-br before:from-cyan-500/10 before:to-transparent before:pointer-events-none">
        {/* File name and tag */}
        <div>
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/40">
              <FileVideo className="w-5 h-5 text-cyan-400" />
            </div>
            <span className="text-sm uppercase tracking-widest text-cyan-400 font-bold">Media Authenticity Sweep</span>
          </div>
          <p className="text-base md:text-lg text-white font-bold truncate drop-shadow-lg" title={fileName}>
            {fileName}
          </p>
          <p className="text-xs text-gray-400 mt-1">Complete forensic analysis report</p>
        </div>

        {/* Score ring */}
        <div className="flex justify-center">
          <ScoreRing score={overallScore} size={140} strokeWidth={10} />
        </div>

        {/* Risk label */}
        <div className="flex justify-center">
          <div className={`px-4 py-2 rounded-full border ${risk.color} text-sm font-bold`}>
            {risk.text}
          </div>
        </div>

        {/* Key stats - larger and more detailed */}
        <div className="space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-4 px-5 py-4 bg-white/10 rounded-xl border-2 border-cyan-500/30 hover:bg-white/15 hover:border-cyan-500/50 transition-all shadow-lg shadow-cyan-500/10"
          >
            <div className="p-3 rounded-lg bg-cyan-500/20 border border-cyan-500/40">
              <Shield className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs uppercase tracking-wider text-gray-400 font-semibold mb-1">Precision Rate</p>
              <p className="text-2xl md:text-3xl font-black text-white drop-shadow-lg">90%+</p>
              <p className="text-xs text-gray-400 mt-1">High-signal detection</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-4 px-5 py-4 bg-white/10 rounded-xl border-2 border-purple-500/30 hover:bg-white/15 hover:border-purple-500/50 transition-all shadow-lg shadow-purple-500/10"
          >
            <div className="p-3 rounded-lg bg-purple-500/20 border border-purple-500/40">
              <Clock className="w-6 h-6 text-purple-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs uppercase tracking-wider text-gray-400 font-semibold mb-1">Detection Time</p>
              <p className="text-2xl md:text-3xl font-black text-white drop-shadow-lg">{processingTime.toFixed(1)}s</p>
              <p className="text-xs text-gray-400 mt-1">Real-time analysis</p>
            </div>
          </motion.div>

          {framesAnalyzed > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex items-center gap-4 px-5 py-4 bg-white/10 rounded-xl border-2 border-pink-500/30 hover:bg-white/15 hover:border-pink-500/50 transition-all shadow-lg shadow-pink-500/10"
            >
              <div className="p-3 rounded-lg bg-pink-500/20 border border-pink-500/40">
                <Database className="w-6 h-6 text-pink-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs uppercase tracking-wider text-gray-400 font-semibold mb-1">Frames Analyzed</p>
                <p className="text-2xl md:text-3xl font-black text-white drop-shadow-lg">{framesAnalyzed.toLocaleString()}</p>
                <p className="text-xs text-gray-400 mt-1">Comprehensive scan</p>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

