import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { SummaryPanel } from './SummaryPanel';
import { Timeline } from './Timeline';

interface AnalysisLayoutProps {
  fileName: string;
  overallScore: number;
  processingTime: number;
  framesAnalyzed?: number;
  stages: Array<{
    id: string;
    name: string;
    description: string;
    status: 'complete' | 'analyzing' | 'queued';
    score?: number;
    icon: 'pixel' | 'motion' | 'frequency' | 'audio' | 'face' | 'verdict';
  }>;
}

export function AnalysisLayout({
  fileName,
  overallScore,
  processingTime,
  framesAnalyzed,
  stages,
}: AnalysisLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });

  // Dynamic background color based on scroll
  const bgHue = useTransform(scrollYProgress, [0, 1], [240, 280]);

  return (
    <div
      ref={containerRef}
      className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950"
    >
      {/* Dynamic gradient layers that fade on scroll */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-indigo-950 via-purple-950 to-pink-950"
        style={{ opacity: useTransform(scrollYProgress, [0, 0.5], [0, 1]) }}
      />
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-purple-950 via-pink-950 to-rose-950"
        style={{ opacity: useTransform(scrollYProgress, [0.5, 1], [0, 1]) }}
      />
      {/* Animated grid overlay */}
      <motion.div
        className="fixed inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(rgba(6, 182, 212, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(6, 182, 212, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          y: useTransform(scrollYProgress, [0, 1], [0, 60]),
        }}
      />

      {/* Floating particles */}
      {Array.from({ length: 20 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: Math.random() * 4 + 2,
            height: Math.random() * 4 + 2,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            background: `hsl(${200 + Math.random() * 80}, 70%, ${50 + Math.random() * 30}%)`,
            opacity: useTransform(scrollYProgress, [0, 1], [0.3, 0]),
            y: useTransform(scrollYProgress, [0, 1], [0, -100 * (i + 1)]),
          }}
        />
      ))}

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
        {/* Two-column layout on desktop, single column on mobile */}
        <div className="grid lg:grid-cols-3 gap-6 lg:gap-12">
          {/* Left: Sticky Summary Panel */}
          <div className="lg:col-span-1 order-1 lg:order-1">
            <SummaryPanel
              fileName={fileName}
              overallScore={overallScore}
              processingTime={processingTime}
              framesAnalyzed={framesAnalyzed}
            />
          </div>

          {/* Right: Scrollable Timeline */}
          <div className="lg:col-span-2 order-2 lg:order-2">
            <Timeline stages={stages} />
          </div>
        </div>
      </div>
    </div>
  );
}

