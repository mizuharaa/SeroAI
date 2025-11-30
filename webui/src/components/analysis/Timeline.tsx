import React, { useRef, useState, useEffect } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { TimelineStageCard } from './TimelineStageCard';

interface TimelineProps {
  stages: Array<{
    id: string;
    name: string;
    description: string;
    status: 'complete' | 'analyzing' | 'queued';
    score?: number;
    icon: 'pixel' | 'motion' | 'frequency' | 'audio' | 'face' | 'verdict';
  }>;
  className?: string;
}

export function Timeline({ stages, className = '' }: TimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const stageRefs = stages.map(() => useRef<HTMLDivElement>(null));

  useEffect(() => {
    const observers = stageRefs.map((ref, index) => {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setActiveIndex(index);
          }
        },
        { threshold: 0.3, rootMargin: '-50px 0px' }
      );

      if (ref.current) {
        observer.observe(ref.current);
      }

      return observer;
    });

    return () => {
      observers.forEach((obs) => obs.disconnect());
    };
  }, []);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Vertical line - hidden on mobile */}
      <div className="hidden sm:block absolute left-8 top-0 bottom-0 w-0.5 bg-white/10">
        <motion.div
          className="absolute top-0 left-0 w-full bg-gradient-to-b from-cyan-500 via-purple-500 to-pink-500"
          initial={{ height: '0%' }}
          animate={{ height: `${((activeIndex + 1) / stages.length) * 100}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{ filter: 'drop-shadow(0 0 8px rgba(6, 182, 212, 0.5))' }}
        />
      </div>

      {/* Timeline dots and cards */}
      <div className="space-y-6 sm:space-y-8 sm:pl-20">
        {stages.map((stage, index) => (
          <div key={stage.id} ref={stageRefs[index]} className="relative">
            {/* Dot - hidden on mobile */}
            <motion.div
              className="hidden sm:block absolute -left-12 top-6 w-4 h-4 rounded-full border-2 border-white/20 bg-slate-900 z-10"
              animate={{
                scale: index <= activeIndex ? 1.5 : 1,
                borderColor: index <= activeIndex ? 'rgba(6, 182, 212, 0.8)' : 'rgba(255, 255, 255, 0.2)',
                boxShadow:
                  index <= activeIndex
                    ? '0 0 12px rgba(6, 182, 212, 0.6), 0 0 24px rgba(6, 182, 212, 0.3)'
                    : 'none',
              }}
              transition={{ duration: 0.3 }}
            >
              {index <= activeIndex && (
                <motion.div
                  className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-400 to-purple-400"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.3 }}
                />
              )}
            </motion.div>

            {/* Card */}
            <TimelineStageCard stage={stage} index={index} isActive={index <= activeIndex} />
          </div>
        ))}
      </div>
    </div>
  );
}

