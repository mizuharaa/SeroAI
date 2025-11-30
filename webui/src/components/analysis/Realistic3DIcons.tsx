import React from 'react';
import { motion } from 'framer-motion';

interface IconProps {
  className?: string;
  isActive?: boolean;
  size?: number;
}

// Futuristic, minimalistic Frequency Domain Analysis Icon
export function FrequencyDomain3D({ className = 'w-8 h-8', isActive = false }: IconProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={isActive ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
      style={{ width: '100%', height: '100%' }}
    >
      <svg viewBox="0 0 32 32" fill="none" className="w-full h-full" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="freqGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#f97316" stopOpacity="1" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="1" />
          </linearGradient>
        </defs>
        
        {/* Minimalistic frequency spectrum bars */}
        <rect x="4" y="24" width="2.5" height="4" rx="1.25" fill="url(#freqGrad)" opacity="0.9" />
        <rect x="8" y="20" width="2.5" height="8" rx="1.25" fill="url(#freqGrad)" opacity="0.95" />
        <rect x="12" y="14" width="2.5" height="14" rx="1.25" fill="url(#freqGrad)" opacity="1" />
        <rect x="16" y="10" width="2.5" height="18" rx="1.25" fill="url(#freqGrad)" opacity="1" />
        <rect x="20" y="16" width="2.5" height="12" rx="1.25" fill="url(#freqGrad)" opacity="0.95" />
        <rect x="24" y="22" width="2.5" height="6" rx="1.25" fill="url(#freqGrad)" opacity="0.9" />
        
        {/* Animated pulse when active */}
        {isActive && (
          <motion.rect
            x="16" y="10" width="2.5" height="18" rx="1.25"
            fill="url(#freqGrad)"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </svg>
    </motion.div>
  );
}

// Futuristic, minimalistic Pixel Stability Icon
export function PixelStability3D({ className = 'w-8 h-8', isActive = false }: IconProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={isActive ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
      style={{ width: '100%', height: '100%' }}
    >
      <svg viewBox="0 0 32 32" fill="none" className="w-full h-full" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="pixelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a855f7" stopOpacity="1" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="1" />
          </linearGradient>
        </defs>
        
        {/* Minimalistic grid pattern */}
        <rect x="6" y="6" width="6" height="6" rx="1" fill="url(#pixelGrad)" opacity="0.9" />
        <rect x="20" y="6" width="6" height="6" rx="1" fill="url(#pixelGrad)" opacity="0.9" />
        <rect x="6" y="20" width="6" height="6" rx="1" fill="url(#pixelGrad)" opacity="0.9" />
        <rect x="20" y="20" width="6" height="6" rx="1" fill="url(#pixelGrad)" opacity="0.9" />
        <rect x="13" y="13" width="6" height="6" rx="1" fill="url(#pixelGrad)" opacity="1" />
        
        {/* Connection lines */}
        <line x1="12" y1="9" x2="20" y2="9" stroke="url(#pixelGrad)" strokeWidth="1.5" opacity="0.6" />
        <line x1="9" y1="12" x2="9" y2="20" stroke="url(#pixelGrad)" strokeWidth="1.5" opacity="0.6" />
        <line x1="16" y1="13" x2="16" y2="13" stroke="url(#pixelGrad)" strokeWidth="2" opacity="0.8" />
        
        {/* Animated pulse when active */}
        {isActive && (
          <motion.rect
            x="13" y="13" width="6" height="6" rx="1"
            fill="url(#pixelGrad)"
            animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.1, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </svg>
    </motion.div>
  );
}

// Futuristic, minimalistic Biological Inconsistency Icon
export function BiologicalInconsistency3D({ className = 'w-8 h-8', isActive = false }: IconProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={isActive ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
      style={{ width: '100%', height: '100%' }}
    >
      <svg viewBox="0 0 32 32" fill="none" className="w-full h-full" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="bioGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="1" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="1" />
          </linearGradient>
        </defs>
        
        {/* Minimalistic face outline */}
        <ellipse cx="16" cy="18" rx="9" ry="10" stroke="url(#bioGrad)" strokeWidth="2" fill="none" opacity="0.8" />
        
        {/* Minimalistic eyes */}
        <circle cx="11" cy="14" r="2" fill="url(#bioGrad)" opacity="0.9" />
        <circle cx="21" cy="14" r="2" fill="url(#bioGrad)" opacity="0.9" />
        
        {/* Minimalistic mouth */}
        <path d="M10 24 Q16 26 22 24" stroke="url(#bioGrad)" strokeWidth="2" fill="none" strokeLinecap="round" opacity="0.8" />
        
        {/* Analysis points */}
        <circle cx="8" y="10" r="1.5" fill="url(#bioGrad)" opacity="0.7" />
        <circle cx="24" y="10" r="1.5" fill="url(#bioGrad)" opacity="0.7" />
        <circle cx="16" y="6" r="1.5" fill="url(#bioGrad)" opacity="0.7" />
        
        {/* Animated pulse when active */}
        {isActive && (
          <motion.circle
            cx="16" cy="18" r="9"
            stroke="url(#bioGrad)"
            strokeWidth="1.5"
            fill="none"
            animate={{ opacity: [0.3, 0.6, 0.3], scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}
      </svg>
    </motion.div>
  );
}

// Futuristic, minimalistic Optical Flow Icon
export function OpticalFlow3D({ className = 'w-8 h-8', isActive = false }: IconProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={isActive ? { rotate: [0, 360] } : {}}
      transition={{ duration: 8, repeat: isActive ? Infinity : 0, ease: 'linear' }}
      style={{ width: '100%', height: '100%' }}
    >
      <svg viewBox="0 0 32 32" fill="none" className="w-full h-full" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="1" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="1" />
          </linearGradient>
        </defs>
        
        {/* Minimalistic flow nodes */}
        <circle cx="8" cy="8" r="2.5" fill="url(#flowGrad)" opacity="0.9" />
        <circle cx="16" cy="12" r="2.5" fill="url(#flowGrad)" opacity="1" />
        <circle cx="24" cy="8" r="2.5" fill="url(#flowGrad)" opacity="0.9" />
        <circle cx="8" cy="24" r="2.5" fill="url(#flowGrad)" opacity="0.9" />
        <circle cx="24" cy="24" r="2.5" fill="url(#flowGrad)" opacity="0.9" />
        
        {/* Minimalistic flow vectors */}
        <line x1="8" y1="8" x2="16" y2="12" stroke="url(#flowGrad)" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
        <line x1="16" y1="12" x2="24" y2="8" stroke="url(#flowGrad)" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
        <line x1="8" y1="24" x2="16" y2="12" stroke="url(#flowGrad)" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
        <line x1="16" y1="12" x2="24" y2="24" stroke="url(#flowGrad)" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
        
        {/* Animated pulse when active */}
        {isActive && (
          <motion.circle
            cx="16" cy="12" r="2.5"
            fill="url(#flowGrad)"
            animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </svg>
    </motion.div>
  );
}

// Futuristic, minimalistic Spatial Logic Icon
export function SpatialLogic3D({ className = 'w-8 h-8', isActive = false }: IconProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={isActive ? { rotate: [0, 360] } : {}}
      transition={{ duration: 6, repeat: isActive ? Infinity : 0, ease: 'linear' }}
      style={{ width: '100%', height: '100%' }}
    >
      <svg viewBox="0 0 32 32" fill="none" className="w-full h-full" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="spatialGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a855f7" stopOpacity="1" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="1" />
          </linearGradient>
        </defs>
        
        {/* Minimalistic infinity symbol */}
        <path
          d="M8 16 Q12 12 16 16 T24 16 M8 16 Q12 20 16 16 T24 16"
          stroke="url(#spatialGrad)"
          strokeWidth="2.5"
          fill="none"
          strokeLinecap="round"
          opacity="0.9"
        />
        
        {/* Central node */}
        <circle cx="16" cy="16" r="3" fill="url(#spatialGrad)" opacity="1" />
        
        {/* Animated pulse when active */}
        {isActive && (
          <motion.circle
            cx="16" cy="16" r="3"
            fill="url(#spatialGrad)"
            animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </svg>
    </motion.div>
  );
}

// Futuristic, minimalistic Audio-Visual Sync Icon
export function AudioVisualSync3D({ className = 'w-8 h-8', isActive = false }: IconProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={isActive ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
      style={{ width: '100%', height: '100%' }}
    >
      <svg viewBox="0 0 32 32" fill="none" className="w-full h-full" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="audioGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#f43f5e" stopOpacity="1" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="1" />
          </linearGradient>
        </defs>
        
        {/* Minimalistic headphones */}
        <path
          d="M6 14 v-3 a5 5 0 0 1 5-5 h10 a5 5 0 0 1 5 5 v3"
          stroke="url(#audioGrad)"
          strokeWidth="2.5"
          fill="none"
          strokeLinecap="round"
          opacity="0.9"
        />
        <path
          d="M11 14 v5 a2.5 2.5 0 0 0 2.5 2.5 h5 a2.5 2.5 0 0 0 2.5-2.5 v-5"
          stroke="url(#audioGrad)"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
          opacity="0.8"
        />
        
        {/* Minimalistic sound waves */}
        <line x1="3" y1="12" x2="5" y2="12" stroke="url(#audioGrad)" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
        <line x1="27" y1="12" x2="29" y2="12" stroke="url(#audioGrad)" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
        <line x1="2" y1="14" x2="4" y2="14" stroke="url(#audioGrad)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
        <line x1="28" y1="14" x2="30" y2="14" stroke="url(#audioGrad)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
        
        {/* Sync indicator */}
        <circle cx="16" cy="9" r="2.5" fill="url(#audioGrad)" opacity="1" />
        <path d="M14.5 9 L15.5 10 L17.5 8" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        
        {/* Animated pulse when active */}
        {isActive && (
          <motion.circle
            cx="16" cy="9" r="2.5"
            fill="url(#audioGrad)"
            animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </svg>
    </motion.div>
  );
}
