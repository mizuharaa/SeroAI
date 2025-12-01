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

      {/* Floating tech particles - More particles */}
      {Array.from({ length: 40 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: Math.random() * 8 + 2,
            height: Math.random() * 8 + 2,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            background: `hsl(${180 + Math.random() * 100}, 70%, ${50 + Math.random() * 30}%)`,
            opacity: 0.5,
            filter: 'blur(1px)',
            boxShadow: `0 0 ${10 + Math.random() * 15}px hsl(${180 + Math.random() * 100}, 70%, 60%)`,
          }}
          animate={{
            y: [0, -40, 0],
            x: [0, Math.random() * 30 - 15, 0],
            opacity: [0.3, 0.9, 0.3],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 3 + Math.random() * 3,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Binary Code Rain Effect */}
      {Array.from({ length: 30 }).map((_, i) => (
        <motion.div
          key={`binary-${i}`}
          className="absolute font-mono text-cyan-400/30 text-xs md:text-sm"
          style={{
            left: `${(i * 3.33) % 100}%`,
            top: '-10%',
            fontFamily: 'monospace',
          }}
          animate={{
            y: ['-10%', '110%'],
            opacity: [0, 0.6, 0.6, 0],
          }}
          transition={{
            duration: 10 + Math.random() * 10,
            repeat: Infinity,
            delay: Math.random() * 5,
            ease: 'linear',
          }}
        >
          {Array.from({ length: Math.floor(Math.random() * 5 + 3) }).map((_, j) => (
            <div key={j} className="opacity-70">
              {Math.random() > 0.5 ? '1' : '0'}
            </div>
          ))}
        </motion.div>
      ))}

      {/* Holographic Data Streams */}
      {Array.from({ length: 12 }).map((_, i) => (
        <motion.div
          key={`hologram-${i}`}
          className="absolute"
          style={{
            width: '3px',
            height: '200px',
            left: `${Math.random() * 100}%`,
            top: `${-10 + Math.random() * 20}%`,
            background: `linear-gradient(to bottom, transparent, hsl(${180 + Math.random() * 100}, 80%, 60%), transparent)`,
            opacity: 0.4,
            filter: 'blur(2px)',
            boxShadow: `0 0 20px hsl(${180 + Math.random() * 100}, 80%, 60%)`,
          }}
          animate={{
            y: ['-10%', '110%'],
            opacity: [0, 0.8, 0.8, 0],
            scaleY: [1, 1.5, 1],
          }}
          transition={{
            duration: 6 + Math.random() * 4,
            repeat: Infinity,
            delay: Math.random() * 3,
            ease: 'linear',
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

      {/* Neural Network Nodes - Tech Background Elements */}
      {Array.from({ length: 15 }).map((_, i) => (
        <motion.div
          key={`node-${i}`}
          className="absolute rounded-full"
          style={{
            width: 8 + Math.random() * 12,
            height: 8 + Math.random() * 12,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            background: `radial-gradient(circle, hsl(${180 + Math.random() * 100}, 80%, 60%) 0%, transparent 70%)`,
            boxShadow: `0 0 ${20 + Math.random() * 30}px hsl(${180 + Math.random() * 100}, 80%, 60%)`,
          }}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.8, 0.3],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Connection Lines Between Nodes */}
      <svg className="absolute inset-0 w-full h-full opacity-20" style={{ zIndex: 1 }}>
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.line
            key={`line-${i}`}
            x1={`${20 + Math.random() * 60}%`}
            y1={`${20 + Math.random() * 60}%`}
            x2={`${20 + Math.random() * 60}%`}
            y2={`${20 + Math.random() * 60}%`}
            stroke={`hsl(${180 + Math.random() * 100}, 70%, 50%)`}
            strokeWidth="1"
            strokeDasharray="5,5"
            animate={{
              strokeDashoffset: [0, 20],
              opacity: [0.2, 0.6, 0.2],
            }}
            transition={{
              duration: 4 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}
      </svg>

      {/* Holographic Grid Overlay */}
      <div className="absolute inset-0 opacity-15" style={{ zIndex: 1 }}>
        <div
          className="w-full h-full"
          style={{
            backgroundImage: `
              linear-gradient(rgba(6, 182, 212, 0.3) 1px, transparent 1px),
              linear-gradient(90deg, rgba(6, 182, 212, 0.3) 1px, transparent 1px),
              linear-gradient(rgba(139, 92, 246, 0.2) 1px, transparent 1px),
              linear-gradient(90deg, rgba(139, 92, 246, 0.2) 1px, transparent 1px)
            `,
            backgroundSize: '100px 100px, 100px 100px, 200px 200px, 200px 200px',
            backgroundPosition: '0 0, 0 0, 50px 50px, 50px 50px',
          }}
        />
      </div>

      {/* Circuit Board Pattern */}
      <svg className="absolute inset-0 w-full h-full opacity-10" style={{ zIndex: 1 }}>
        <defs>
          <pattern id="circuitBoard" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
            <rect width="100" height="100" fill="none" />
            <path d="M0,50 L100,50 M50,0 L50,100" stroke="rgba(6, 182, 212, 0.3)" strokeWidth="1" />
            <circle cx="25" cy="25" r="3" fill="rgba(6, 182, 212, 0.5)" />
            <circle cx="75" cy="75" r="3" fill="rgba(139, 92, 246, 0.5)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#circuitBoard)" />
      </svg>

      {/* Content - More Compact Layout */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12 md:py-16">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8">
          {/* Left: Main heading - LARGER TEXT */}
          <motion.div
            className="flex-1"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge - Larger */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-3 px-5 py-2.5 mb-4 rounded-full border-2 border-cyan-500/40 bg-cyan-500/15 backdrop-blur-md shadow-lg shadow-cyan-500/20"
            >
              <Zap className="w-5 h-5 text-cyan-400" />
              <span className="text-sm uppercase tracking-widest text-cyan-400 font-bold">Neural Forensics</span>
            </motion.div>

            {/* Main heading - MUCH LARGER */}
            <div className="relative mb-4">
              <motion.h1
                className="text-6xl md:text-8xl lg:text-9xl xl:text-[10rem] font-black tracking-tight relative z-10 leading-[0.9]"
                style={{
                  background: 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 50%, #ec4899 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  filter: 'drop-shadow(0 0 60px rgba(6, 182, 212, 0.8))',
                  textShadow: '0 0 80px rgba(6, 182, 212, 0.5)',
                }}
              >
                Deepfake
                <br />
                <span className="block">Detection</span>
              </motion.h1>
              {/* Animated glow layers */}
              <motion.h1
                className="absolute inset-0 text-6xl md:text-8xl lg:text-9xl xl:text-[10rem] font-black tracking-tight pointer-events-none leading-[0.9]"
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
                  filter: 'blur(30px)',
                }}
              >
                Deepfake
                <br />
                <span className="block">Detection</span>
              </motion.h1>
            </div>

            {/* Subtitle - Larger */}
            <motion.p
              className="text-2xl md:text-3xl lg:text-4xl text-gray-200 mb-6 max-w-3xl leading-tight font-medium"
              style={{ y: useTransform(scrollYProgress, [0, 1], [0, 30]) }}
            >
              Upload a video or image and get a fast, detailed authenticity report powered by advanced neural networks.
            </motion.p>

            {/* Stats - Larger */}
            <motion.div
              className="flex flex-wrap items-center gap-4"
              style={{ opacity }}
            >
              <div className="flex items-center gap-4 px-6 py-3 rounded-xl bg-white/10 border-2 border-cyan-500/30 backdrop-blur-md shadow-xl shadow-cyan-500/20">
                <Clock className="w-6 h-6 text-cyan-400" />
                <div>
                  <div className="text-sm text-gray-300 font-medium">Processing Time</div>
                  <div className="text-2xl font-bold text-white">~ 8–12s</div>
                </div>
              </div>
            </motion.div>
          </motion.div>

          {/* Right: Info cards - Larger and More Compact */}
          <motion.div
            className="w-full lg:w-auto lg:min-w-[360px] space-y-3"
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
                whileHover={{ scale: 1.03, y: -4, borderColor: 'rgba(6, 182, 212, 0.6)' }}
                className="group relative overflow-hidden rounded-2xl border-2 border-white/20 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl p-6 hover:border-cyan-500/50 transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-cyan-500/20"
              >
                {/* Animated gradient overlay */}
                <motion.div
                  className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-20 transition-opacity`}
                  animate={{
                    opacity: [0, 0.15, 0],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                  }}
                />
                {/* Tech scan line effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-400/20 to-transparent"
                  animate={{
                    y: ['-100%', '200%'],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    delay: idx * 0.5,
                  }}
                />
                <div className="relative flex items-start gap-4">
                  <div className="text-3xl">{card.icon}</div>
                  <div className="flex-1">
                    <div className="text-base font-bold text-white mb-1.5">{card.title}</div>
                    <div className="text-sm text-gray-300 leading-relaxed">{card.desc}</div>
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

