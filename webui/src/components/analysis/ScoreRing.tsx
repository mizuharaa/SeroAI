import React from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function ScoreRing({ score, size = 120, strokeWidth = 8, className = '' }: ScoreRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = useMotionValue(0);
  const springProgress = useSpring(progress, { stiffness: 100, damping: 30 });

  React.useEffect(() => {
    progress.set(score / 100);
  }, [score, progress]);

  const offset = useTransform(springProgress, (p) => circumference - p * circumference);

  const getColor = (val: number) => {
    if (val <= 20) return '#10b981'; // green
    if (val <= 40) return '#84cc16'; // lime
    if (val <= 60) return '#eab308'; // yellow
    if (val <= 80) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const color = getColor(score);

  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          style={{
            strokeDashoffset: offset,
            filter: `drop-shadow(0 0 8px ${color})`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center"
        >
          <motion.span
            key={score}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
            className="text-3xl font-black block"
            style={{ color }}
          >
            {Math.round(score)}%
          </motion.span>
        </motion.div>
      </div>
    </div>
  );
}

