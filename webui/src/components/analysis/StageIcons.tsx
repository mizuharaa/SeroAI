import React from 'react';

interface IconProps {
  className?: string;
  strokeWidth?: number;
}

// Highly detailed, asymmetric, hand-crafted looking icons
export function PixelStabilityIcon({ className = 'w-6 h-6', strokeWidth = 2 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
      {/* Asymmetric pixel grid with detailed connections */}
      <rect x="1.5" y="1.5" width="5" height="5" rx="0.8" fill="currentColor" opacity="0.9" />
      <rect x="9" y="2" width="4.5" height="4.5" rx="0.8" fill="currentColor" opacity="0.7" />
      <rect x="16" y="1.5" width="5" height="5" rx="0.8" fill="currentColor" opacity="0.9" />
      <rect x="2" y="9" width="4.5" height="4.5" rx="0.8" fill="currentColor" opacity="0.8" />
      <rect x="9.5" y="9.5" width="4" height="4" rx="0.8" fill="currentColor" opacity="0.6" />
      <rect x="16.5" y="9" width="4.5" height="4.5" rx="0.8" fill="currentColor" opacity="0.8" />
      <rect x="1.5" y="16.5" width="5" height="5" rx="0.8" fill="currentColor" opacity="0.9" />
      <rect x="9" y="17" width="4.5" height="4.5" rx="0.8" fill="currentColor" opacity="0.7" />
      <rect x="16" y="16.5" width="5" height="5" rx="0.8" fill="currentColor" opacity="0.9" />
      {/* Detailed connection network */}
      <path d="M4 4l1.5 0M11.5 4l1.5 0M18.5 4l1.5 0" strokeWidth={strokeWidth * 0.8} />
      <path d="M4.5 11l1 0M11 11.5l1.5 0M18 11l1.5 0" strokeWidth={strokeWidth * 0.8} />
      <path d="M4 18.5l1.5 0M11.5 19l1.5 0M18.5 18.5l1.5 0" strokeWidth={strokeWidth * 0.8} />
      <path d="M1.5 4.5v1.5M1.5 11.5v1M1.5 18.5v1.5" strokeWidth={strokeWidth * 0.8} />
      <path d="M9 4.5v1M9 11.5v1.5M9 18.5v1" strokeWidth={strokeWidth * 0.8} />
      <path d="M16.5 4.5v1.5M16.5 11.5v1M16.5 18.5v1.5" strokeWidth={strokeWidth * 0.8} />
      {/* Cross-connections */}
      <path d="M4 4l5 5M11.5 4l4.5 4.5M4 11.5l5 5M11.5 11.5l4.5 4.5" strokeWidth={strokeWidth * 0.6} opacity="0.4" strokeDasharray="1 1" />
    </svg>
  );
}

export function OpticalFlowIcon({ className = 'w-6 h-6', strokeWidth = 2 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
      {/* Asymmetric motion points */}
      <circle cx="5.5" cy="5.5" r="2.2" fill="currentColor" opacity="0.9" />
      <circle cx="12" cy="11.5" r="2.5" fill="currentColor" opacity="0.8" />
      <circle cx="18.5" cy="18" r="2.2" fill="currentColor" opacity="0.9" />
      <circle cx="7" cy="15" r="1.5" fill="currentColor" opacity="0.6" />
      {/* Detailed motion vectors with varying angles */}
      <path d="M7.5 5.5l2.5 3M9.5 8.5l2 2.5" strokeWidth={strokeWidth * 0.9} />
      <path d="M14.5 12l2.5 3M16.5 15l2 2.5" strokeWidth={strokeWidth * 0.9} />
      <path d="M5.5 7.5l2-2M12 13.5l2.5-2.5M18.5 16l2-2" strokeWidth={strokeWidth * 0.9} />
      {/* Curved flow paths with varying thickness */}
      <path d="M5.5 5.5 Q8.5 8 12 11.5 T18.5 18" strokeWidth={strokeWidth * 1.2} strokeDasharray="3 2" opacity="0.7" />
      <path d="M7 15 Q10 12 12 11.5" strokeWidth={strokeWidth * 0.8} strokeDasharray="2 1.5" opacity="0.5" />
      {/* Additional flow indicators */}
      <path d="M3 7l1.5-1.5M20 16l1.5-1.5" strokeWidth={strokeWidth * 0.7} opacity="0.4" />
    </svg>
  );
}

export function FrequencyIcon({ className = 'w-6 h-6', strokeWidth = 2 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
      {/* Asymmetric frequency bars with detailed variations */}
      <rect x="1.5" y="21" width="3" height="1.5" rx="0.6" fill="currentColor" opacity="0.8" />
      <rect x="5.5" y="18" width="2.8" height="4.5" rx="0.6" fill="currentColor" opacity="0.9" />
      <rect x="9.5" y="13" width="3" height="9.5" rx="0.6" fill="currentColor" opacity="0.85" />
      <rect x="13.5" y="7" width="2.8" height="17" rx="0.6" fill="currentColor" opacity="0.95" />
      <rect x="17.5" y="15" width="3" height="7.5" rx="0.6" fill="currentColor" opacity="0.8" />
      <rect x="21" y="19" width="2" height="3.5" rx="0.6" fill="currentColor" opacity="0.7" />
      {/* Overlaid frequency waves with varying patterns */}
      <path d="M1.5 20 Q4 18 6.5 19 T12 17 T17.5 19 T22 17" strokeWidth={strokeWidth * 0.8} strokeDasharray="1.5 1" opacity="0.5" />
      <path d="M2 18.5 Q5 16.5 8.5 18 T15 16 T20 18" strokeWidth={strokeWidth * 0.6} strokeDasharray="1 0.8" opacity="0.4" />
      {/* Harmonic indicators */}
      <circle cx="4" cy="19.5" r="0.8" fill="currentColor" opacity="0.6" />
      <circle cx="11" cy="15" r="0.8" fill="currentColor" opacity="0.6" />
      <circle cx="18" cy="17" r="0.8" fill="currentColor" opacity="0.6" />
    </svg>
  );
}

export function AudioSyncIcon({ className = 'w-6 h-6', strokeWidth = 2 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
      {/* Detailed headphones with asymmetry */}
      <path d="M3.5 13.5v-3.5a5.5 5.5 0 0 1 5.5-5.5h6a5.5 5.5 0 0 1 5.5 5.5v3.5" strokeWidth={strokeWidth * 1.1} />
      <path d="M8.5 13.5v4.5a2.5 2.5 0 0 0 2.5 2.5h2a2.5 2.5 0 0 0 2.5-2.5v-4.5" strokeWidth={strokeWidth * 1.1} />
      {/* Detailed sound waves with varying patterns */}
      <path d="M2.5 11.5h2.5M19 11.5h2.5" strokeWidth={strokeWidth * 1.2} />
      <path d="M1.5 13h1.5M21 13h1.5" strokeWidth={strokeWidth * 0.9} opacity="0.7" />
      <path d="M4.5 9.5h1M18.5 9.5h1" strokeWidth={strokeWidth * 0.8} opacity="0.6" />
      <path d="M5.5 15.5h0.8M17.5 15.5h0.8" strokeWidth={strokeWidth * 0.7} opacity="0.5" />
      {/* Sync indicator with detailed checkmark */}
      <circle cx="12" cy="9.5" r="2" fill="currentColor" opacity="0.9" />
      <path d="M10.2 9.5l1.3 1.3 3-3" strokeWidth={strokeWidth * 1.3} stroke="white" opacity="0.9" />
      {/* Additional sync lines */}
      <path d="M9 7.5l3 2M12 7.5l3 2" strokeWidth={strokeWidth * 0.6} opacity="0.4" strokeDasharray="1 1" />
    </svg>
  );
}

export function FaceAnalysisIcon({ className = 'w-6 h-6', strokeWidth = 2 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
      {/* Asymmetric face outline */}
      <ellipse cx="12" cy="13" rx="8.5" ry="9.5" strokeWidth={strokeWidth * 1.1} />
      {/* Detailed eyes with varying sizes */}
      <circle cx="8.5" cy="10.5" r="1.8" fill="currentColor" opacity="0.9" />
      <circle cx="15.5" cy="10.5" r="1.8" fill="currentColor" opacity="0.9" />
      <circle cx="8.5" cy="10.5" r="0.8" fill="white" opacity="0.8" />
      <circle cx="15.5" cy="10.5" r="0.8" fill="white" opacity="0.8" />
      {/* Detailed nose */}
      <path d="M12 13v2.5" strokeWidth={strokeWidth * 1.2} />
      <path d="M11 15.5h2" strokeWidth={strokeWidth * 1.1} />
      <path d="M11.5 14l0.5 1.5M12.5 14l-0.5 1.5" strokeWidth={strokeWidth * 0.8} opacity="0.6" />
      {/* Asymmetric mouth */}
      <path d="M8.5 17 Q12 19.5 15.5 17" strokeWidth={strokeWidth * 1.1} />
      <path d="M9 17.5 Q12 19 15 17.5" strokeWidth={strokeWidth * 0.7} opacity="0.5" />
      {/* Detailed landmark dots with varying sizes */}
      <circle cx="6.5" cy="8.5" r="0.8" fill="currentColor" opacity="0.8" />
      <circle cx="17.5" cy="8.5" r="0.8" fill="currentColor" opacity="0.8" />
      <circle cx="12" cy="5.5" r="0.8" fill="currentColor" opacity="0.8" />
      <circle cx="9" cy="7" r="0.5" fill="currentColor" opacity="0.6" />
      <circle cx="15" cy="7" r="0.5" fill="currentColor" opacity="0.6" />
      {/* Analysis grid overlay */}
      <path d="M6 6l6 6M18 6l-6 6M12 4v18M4 12h16" strokeWidth={strokeWidth * 0.4} opacity="0.2" strokeDasharray="1 2" />
    </svg>
  );
}

export function VerdictIcon({ className = 'w-6 h-6', strokeWidth = 2 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
      {/* Detailed shield with texture */}
      <path d="M12 2L3.5 6.5v6.5c0 5.8 4 11.2 8.5 12.5 4.5-1.3 8.5-6.7 8.5-12.5V6.5L12 2z" strokeWidth={strokeWidth * 1.2} />
      <path d="M12 2.5L4 6.8v6.2c0 5.2 3.5 10 7.5 11.2 4-1.2 7.5-6 7.5-11.2V6.8L12 2.5z" strokeWidth={strokeWidth * 0.6} opacity="0.4" />
      {/* Detailed checkmark */}
      <path d="M8.5 12l2.5 2.5 5-5" strokeWidth={strokeWidth * 1.8} strokeLinecap="round" />
      <path d="M9 12.5l2 2 4-4" strokeWidth={strokeWidth * 1.2} stroke="white" opacity="0.9" strokeLinecap="round" />
      {/* Additional security indicators */}
      <circle cx="12" cy="9" r="1.5" fill="currentColor" opacity="0.3" />
      <path d="M10.5 7.5l3 3M13.5 7.5l-3 3" strokeWidth={strokeWidth * 0.5} opacity="0.4" />
    </svg>
  );
}
