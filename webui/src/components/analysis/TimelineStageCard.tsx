import React from 'react';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import { StatusChip } from './StatusChip';
import { Sparkline, BarChart, Waveform, FaceGrid } from './MicroCharts';
import {
  PixelStabilityIcon,
  OpticalFlowIcon,
  FrequencyIcon,
  AudioSyncIcon,
  FaceAnalysisIcon,
  VerdictIcon,
} from './StageIcons';

interface TimelineStageCardProps {
  stage: {
    id: string;
    name: string;
    description: string;
    status: 'complete' | 'analyzing' | 'queued';
    score?: number;
    icon: 'pixel' | 'motion' | 'frequency' | 'audio' | 'face' | 'verdict';
  };
  index: number;
  isActive: boolean;
}

const iconMap = {
  pixel: PixelStabilityIcon,
  motion: OpticalFlowIcon,
  frequency: FrequencyIcon,
  audio: AudioSyncIcon,
  face: FaceAnalysisIcon,
  verdict: VerdictIcon,
};

const chartMap = {
  pixel: () => <Sparkline data={[65, 72, 68, 75, 70, 78, 74]} />,
  motion: () => <BarChart values={[75, 82, 68, 90, 85]} />,
  frequency: () => <BarChart values={[60, 70, 65, 80, 75, 70]} />,
  audio: () => <Waveform />,
  face: () => <FaceGrid />,
  verdict: () => null,
};

export function TimelineStageCard({ stage, index, isActive }: TimelineStageCardProps) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: false, margin: '-100px' });

  const Icon = iconMap[stage.icon];
  const Chart = chartMap[stage.icon];

  const getGradient = () => {
    switch (stage.icon) {
      case 'pixel':
        return 'from-purple-500/20 to-pink-500/20 border-purple-500/30';
      case 'motion':
        return 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30';
      case 'frequency':
        return 'from-orange-500/20 to-red-500/20 border-orange-500/30';
      case 'audio':
        return 'from-pink-500/20 to-rose-500/20 border-pink-500/30';
      case 'face':
        return 'from-blue-500/20 to-cyan-500/20 border-blue-500/30';
      case 'verdict':
        return 'from-cyan-500/20 to-purple-500/20 border-cyan-500/30';
      default:
        return 'from-slate-500/20 to-slate-500/20 border-slate-500/30';
    }
  };

  const getIconGradient = () => {
    switch (stage.icon) {
      case 'pixel':
        return 'from-purple-500 to-pink-500';
      case 'motion':
        return 'from-emerald-500 to-teal-500';
      case 'frequency':
        return 'from-orange-500 to-red-500';
      case 'audio':
        return 'from-pink-500 to-rose-500';
      case 'face':
        return 'from-blue-500 to-cyan-500';
      case 'verdict':
        return 'from-cyan-500 to-purple-500';
      default:
        return 'from-slate-500 to-slate-500';
    }
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -6, scale: 1.02 }}
      className={`relative bg-gradient-to-br ${getGradient()} backdrop-blur-xl border-2 rounded-3xl p-8 md:p-10 shadow-xl hover:shadow-2xl hover:shadow-cyan-500/40 transition-all duration-300 cursor-pointer group overflow-hidden`}
    >
      {/* Animated border glow */}
      <motion.div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100"
        style={{
          background: `linear-gradient(135deg, rgba(6, 182, 212, 0.3) 0%, rgba(139, 92, 246, 0.3) 50%, rgba(236, 72, 153, 0.3) 100%)`,
          filter: 'blur(20px)',
          zIndex: -1,
        }}
        animate={{
          scale: [1, 1.05, 1],
        }}
        transition={{ duration: 3, repeat: Infinity }}
      />
      
      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 opacity-0 group-hover:opacity-100"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%)',
        }}
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
      />

      <div className="relative z-10 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-6">
          <div className="flex items-start gap-5 flex-1">
            <div className={`p-5 rounded-2xl bg-gradient-to-br ${getIconGradient()} shadow-2xl group-hover:shadow-2xl group-hover:shadow-cyan-500/50 transition-all duration-300 group-hover:scale-110 border-2 border-white/20`}>
              <Icon className="w-10 h-10 text-white" strokeWidth={2.5} />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-2xl md:text-3xl font-black text-white mb-3 drop-shadow-2xl tracking-tight">{stage.name}</h3>
              <p className="text-base md:text-lg text-gray-200 leading-relaxed font-medium">{stage.description}</p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs uppercase tracking-widest text-cyan-400 font-bold">Forensic Analysis</span>
                <span className="text-gray-500">•</span>
                <span className="text-xs text-gray-400">Real-time processing</span>
              </div>
            </div>
          </div>
          <StatusChip status={stage.status} />
        </div>

        {/* Micro chart - larger */}
        {Chart && (
          <div className="h-24 md:h-28 flex items-center justify-center bg-black/30 rounded-xl p-4 border-2 border-white/20 backdrop-blur-sm">
            <Chart />
          </div>
        )}

        {/* Score - more prominent */}
        {stage.score !== undefined && (
          <div className="flex items-center justify-between pt-4 border-t-2 border-white/20">
            <div>
              <span className="text-xs md:text-sm text-gray-400 uppercase tracking-widest font-bold block mb-1">Confidence Score</span>
              <span className="text-xs text-gray-500">Based on neural network analysis</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-3xl md:text-4xl font-black text-white drop-shadow-lg">{stage.score}%</span>
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-purple-400 flex items-center justify-center shadow-lg">
                <span className="text-lg font-black text-white">✓</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

