import React, { useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { Zap, Clock } from 'lucide-react';

export function DetectHero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });

  // Transform scroll progress into color values
  const hue = useTransform(scrollYProgress, [0, 1], [200, 280]); // Cyan to purple
  const saturation = useTransform(scrollYProgress, [0, 1], [70, 90]);
  const lightness = useTransform(scrollYProgress, [0, 1], [15, 25]);

  // Parallax transforms
  const y1 = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const y2 = useTransform(scrollYProgress, [0, 1], [0, -150]);
  const y3 = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const scale = useTransform(scrollYProgress, [0, 1], [1, 1.2]);
  const opacity = useTransform(scrollYProgress, [0, 1], [1, 0.3]);

  return (
    <div ref={containerRef} className="relative min-h-[90vh] overflow-hidden">
      {/* Dynamic gradient background layers that fade on scroll */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-950 via-purple-950 to-pink-950" />
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-950 via-indigo-950 to-purple-950"
        style={{ opacity: useTransform(scrollYProgress, [0, 1], [0, 1]) }}
      />
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-purple-950 via-pink-950 to-rose-950"
        style={{ opacity: useTransform(scrollYProgress, [0.5, 1], [0, 1]) }}
      />

      {/* Animated grid pattern */}
      <div className="absolute inset-0 opacity-20">
        <div
          className="w-full h-full"
          style={{
            backgroundImage: `
              linear-gradient(rgba(6, 182, 212, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(6, 182, 212, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* Tech circuit lines */}
      <svg className="absolute inset-0 w-full h-full opacity-10" style={{ zIndex: 1 }}>
        <defs>
          <linearGradient id="circuitGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="0.3" />
          </linearGradient>
        </defs>
        <motion.path
          d="M0,100 Q200,50 400,100 T800,100"
          stroke="url(#circuitGradient)"
          strokeWidth="2"
          fill="none"
          strokeDasharray="5,5"
          animate={{
            strokeDashoffset: [0, 20],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
        <motion.path
          d="M0,300 Q300,250 600,300 T1200,300"
          stroke="url(#circuitGradient)"
          strokeWidth="2"
          fill="none"
          strokeDasharray="5,5"
          animate={{
            strokeDashoffset: [20, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </svg>

      {/* Floating tech particles */}
      {Array.from({ length: 25 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: Math.random() * 6 + 2,
            height: Math.random() * 6 + 2,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            background: `hsl(${180 + Math.random() * 100}, 70%, ${50 + Math.random() * 30}%)`,
            opacity: 0.4,
            filter: 'blur(1px)',
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, Math.random() * 20 - 10, 0],
            opacity: [0.4, 0.8, 0.4],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Hexagonal tech pattern */}
      <svg className="absolute inset-0 w-full h-full opacity-5" style={{ zIndex: 1 }}>
        <defs>
          <pattern id="hexagons" x="0" y="0" width="50" height="43.4" patternUnits="userSpaceOnUse">
            <polygon points="24.8,22 37.3,14.2 37.3,7.1 24.8,0 12.3,7.1 12.3,14.2" fill="none" stroke="#06b6d4" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#hexagons)" />
      </svg>

      {/* Data stream lines */}
      {Array.from({ length: 8 }).map((_, i) => (
        <motion.div
          key={`stream-${i}`}
          className="absolute h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
          style={{
            width: '200px',
            left: `${Math.random() * 100}%`,
            top: `${20 + i * 12}%`,
            opacity: 0.3,
          }}
          animate={{
            x: [0, 300, 0],
            opacity: [0, 0.6, 0],
          }}
          transition={{
            duration: 4 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 3,
            ease: 'linear',
          }}
        />
      ))}

      {/* Floating orbs with parallax */}
      <motion.div
        className="absolute top-20 left-10 w-96 h-96 rounded-full blur-3xl"
        style={{
          y: y1,
          scale,
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.4) 0%, transparent 70%)',
        }}
      />
      <motion.div
        className="absolute top-40 right-20 w-80 h-80 rounded-full blur-3xl"
        style={{
          y: y2,
          scale,
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, transparent 70%)',
        }}
      />
      <motion.div
        className="absolute bottom-20 left-1/3 w-72 h-72 rounded-full blur-3xl"
        style={{
          y: y3,
          scale,
          background: 'radial-gradient(circle, rgba(236, 72, 153, 0.3) 0%, transparent 70%)',
        }}
      />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-24 md:py-32">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-12">
          {/* Left: Main heading with scroll-based color changes */}
          <motion.div
            className="flex-1"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full border border-cyan-500/30 bg-cyan-500/10 backdrop-blur-sm"
            >
              <Zap className="w-4 h-4 text-cyan-400" />
              <span className="text-xs uppercase tracking-widest text-cyan-400 font-semibold">Neural Forensics</span>
            </motion.div>

            {/* Main heading with dynamic color layers */}
            <div className="relative">
              <motion.h1
                className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight mb-6 relative z-10"
                style={{
                  background: 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 50%, #ec4899 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  filter: 'drop-shadow(0 0 40px rgba(6, 182, 212, 0.6))',
                }}
              >
                Deepfake
                <br />
                <span className="block mt-2">Detection</span>
              </motion.h1>
              {/* Animated glow layers */}
              <motion.h1
                className="absolute inset-0 text-5xl md:text-7xl lg:text-8xl font-black tracking-tight mb-6 pointer-events-none"
                style={{
                  background: useTransform(
                    scrollYProgress,
                    [0, 0.5, 1],
                    [
                      'linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #f97316 100%)',
                      'linear-gradient(135deg, #ec4899 0%, #f97316 50%, #06b6d4 100%)',
                      'linear-gradient(135deg, #f97316 0%, #06b6d4 50%, #8b5cf6 100%)',
                    ]
                  ),
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  opacity: useTransform(scrollYProgress, [0, 0.5, 1], [0, 0.5, 0]),
                  filter: 'blur(20px)',
                }}
              >
                Deepfake
                <br />
                <span className="block mt-2">Detection</span>
              </motion.h1>
            </div>

            {/* Subtitle with parallax */}
            <motion.p
              className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl leading-relaxed"
              style={{ y: useTransform(scrollYProgress, [0, 1], [0, 30]) }}
            >
              Upload a video or image and get a fast, detailed authenticity report powered by advanced neural networks.
            </motion.p>

            {/* Stats with scroll fade */}
            <motion.div
              className="flex flex-wrap items-center gap-6"
              style={{ opacity }}
            >
              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 border border-cyan-500/20 backdrop-blur-sm">
                <Clock className="w-5 h-5 text-cyan-400" />
                <div>
                  <div className="text-xs text-gray-400">Processing Time</div>
                  <div className="text-lg font-bold text-white">~ 8–12s</div>
                </div>
              </div>
            </motion.div>
          </motion.div>

          {/* Right: Info cards with parallax */}
          <motion.div
            className="w-full lg:w-auto lg:min-w-[320px] space-y-4"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            style={{ y: useTransform(scrollYProgress, [0, 1], [0, -50]) }}
          >
            {[
              {
                title: 'Supported Formats',
                desc: 'MP4, MOV, AVI, WebM, JPG, PNG',
                gradient: 'from-cyan-500 to-blue-500',
                icon: '📹',
              },
              {
                title: 'Limits',
                desc: 'Up to 500MB • ~5 minutes',
                gradient: 'from-purple-500 to-pink-500',
                icon: '⚡',
              },
              {
                title: 'Privacy',
                desc: 'Files never shared. Local processing options.',
                gradient: 'from-pink-500 to-rose-500',
                icon: '🔒',
              },
            ].map((card, idx) => (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + idx * 0.1 }}
                whileHover={{ scale: 1.02, y: -4 }}
                className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-xl p-5 hover:border-cyan-500/30 transition-all duration-300"
              >
                {/* Gradient overlay on hover */}
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-10 transition-opacity`}
                />
                <div className="relative flex items-start gap-4">
                  <div className="text-2xl">{card.icon}</div>
                  <div className="flex-1">
                    <div className="text-sm font-bold text-white mb-1">{card.title}</div>
                    <div className="text-xs text-gray-400">{card.desc}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        initial={{ opacity: 1 }}
        style={{ opacity: useTransform(scrollYProgress, [0, 0.3], [1, 0]) }}
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 rounded-full border-2 border-cyan-500/50 flex items-start justify-center p-2"
        >
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-1 h-3 rounded-full bg-cyan-400"
          />
        </motion.div>
      </motion.div>
    </div>
  );
}

