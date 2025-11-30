import React from 'react';
import { motion } from 'framer-motion';

interface SparklineProps {
  data: number[];
  className?: string;
}

export function Sparkline({ data, className = '' }: SparklineProps) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = 80;
  const height = 30;
  const stepX = width / (data.length - 1);

  const points = data
    .map((value, i) => {
      const x = i * stepX;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className={`${className}`}>
      <svg width={width} height={height} className="overflow-visible">
        <motion.polyline
          points={points}
          fill="none"
          stroke="url(#sparklineGradient)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5, ease: 'easeInOut' }}
        />
        <defs>
          <linearGradient id="sparklineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.8" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

interface BarChartProps {
  values: number[];
  className?: string;
}

export function BarChart({ values, className = '' }: BarChartProps) {
  const max = Math.max(...values) || 1;
  const barWidth = 60 / values.length - 2;

  return (
    <div className={`flex items-end gap-1 h-12 ${className}`}>
      {values.map((value, i) => (
        <motion.div
          key={i}
          initial={{ height: 0 }}
          animate={{ height: `${(value / max) * 100}%` }}
          transition={{ duration: 0.8, delay: i * 0.1, ease: 'easeOut' }}
          className="flex-1 bg-gradient-to-t from-cyan-500 to-purple-500 rounded-t"
          style={{ minHeight: '4px' }}
        />
      ))}
    </div>
  );
}

interface WaveformProps {
  className?: string;
}

export function Waveform({ className = '' }: WaveformProps) {
  const bars = Array.from({ length: 12 }, () => Math.random() * 0.8 + 0.2);

  return (
    <div className={`flex items-end gap-0.5 h-12 ${className}`}>
      {bars.map((height, i) => (
        <motion.div
          key={i}
          initial={{ height: 0 }}
          animate={{ height: `${height * 100}%` }}
          transition={{ duration: 0.3, delay: i * 0.05, repeat: Infinity, repeatType: 'reverse' }}
          className="w-1 bg-gradient-to-t from-pink-500 to-rose-500 rounded-t"
          style={{ minHeight: '2px' }}
        />
      ))}
    </div>
  );
}

interface FaceGridProps {
  className?: string;
}

export function FaceGrid({ className = '' }: FaceGridProps) {
  return (
    <div className={`grid grid-cols-3 gap-1 ${className}`}>
      {Array.from({ length: 9 }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.05 }}
          className="aspect-square rounded bg-gradient-to-br from-orange-500/20 to-pink-500/20 border border-orange-500/30 flex items-center justify-center"
        >
          <div className="w-4 h-4 rounded-full bg-gradient-to-br from-orange-400 to-pink-400 opacity-60" />
        </motion.div>
      ))}
    </div>
  );
}

