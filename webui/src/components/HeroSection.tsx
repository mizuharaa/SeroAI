import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { AIDetectionAnimation } from './AIDetectionAnimation';

interface HeroSectionProps {
  onTryDemo: () => void;
  onUploadMedia: () => void;
}

export function HeroSection({ onTryDemo, onUploadMedia }: HeroSectionProps) {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end start"]
  });

  // Parallax effects for text - pan in/out on scroll
  const textY = useTransform(scrollYProgress, [0, 0.8, 1], [0, 150, 200]);
  const textOpacity = useTransform(scrollYProgress, [0, 0.6, 1], [1, 0.8, 0.2]);
  const textScale = useTransform(scrollYProgress, [0, 0.6, 1], [1, 0.98, 0.92]);
  const textX = useTransform(scrollYProgress, [0, 0.5, 1], [0, -20, -40]);
  
  // Parallax effects for bullet points
  const bulletsY = useTransform(scrollYProgress, [0, 0.8, 1], [0, 120, 180]);
  const bulletsOpacity = useTransform(scrollYProgress, [0, 0.6, 1], [1, 0.85, 0.25]);
  const bulletsScale = useTransform(scrollYProgress, [0, 0.6, 1], [1, 0.98, 0.94]);

  return (
    <section ref={sectionRef} className="relative min-h-[95vh] flex items-center justify-center overflow-hidden pt-16">
      <div className="absolute inset-0 bg-gradient-to-br from-orange-50 via-rose-50 to-amber-50">
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, rgb(251 146 60 / 0.15) 1px, transparent 0)`,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-0 left-0 w-[600px] h-[600px] bg-gradient-to-br from-orange-400/40 via-rose-400/30 to-transparent rounded-full blur-3xl"
          animate={{ x: [0, 100, 0], y: [0, 80, 0], scale: [1, 1.2, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute top-20 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-pink-400/35 via-rose-300/25 to-transparent rounded-full blur-3xl"
          animate={{ x: [0, -80, 0], y: [0, 100, 0], scale: [1, 1.15, 1] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-gradient-to-t from-amber-400/35 via-orange-300/25 to-transparent rounded-full blur-3xl"
          animate={{ x: [0, 60, 0], y: [0, -60, 0], scale: [1, 1.1, 1] }}
          transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      {/* Top right - Start now button aligned with ACCESS text in login card */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="absolute top-6 sm:top-8 right-4 sm:right-6 lg:right-12 xl:right-16 z-20"
      >
        <Button
          size="lg"
          onClick={onTryDemo}
          className="bg-gray-900 hover:bg-gray-800 text-white border-0 shadow-xl hover:shadow-2xl transition-all text-sm sm:text-base px-6 sm:px-8 py-3 sm:py-4 h-auto group font-semibold rounded-full"
        >
          Start now
          <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 ml-2 group-hover:translate-x-1 transition-transform" />
        </Button>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex flex-col lg:flex-row items-center justify-center gap-12 lg:gap-16">
          {/* Left side - Text content centered */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="w-full lg:w-auto flex flex-col items-center lg:items-start text-center lg:text-left space-y-6 lg:space-y-8 max-w-2xl"
          >
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              style={{
                y: textY,
                x: textX,
                opacity: textOpacity,
                scale: textScale
              }}
              className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl text-gray-900 leading-tight font-black tracking-tight"
            >
              <span className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 bg-clip-text text-transparent">
                AI that detects deepfakes and restores trust in digital media. Protect authenticity.{' '}
              </span>
              <span className="font-black bg-gradient-to-r from-orange-600 via-rose-600 to-pink-600 bg-clip-text text-transparent">
                Empower truth.
              </span>
            </motion.p>

            <motion.ul
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              style={{
                y: bulletsY,
                opacity: bulletsOpacity,
                scale: bulletsScale
              }}
              className="space-y-5 pt-2 w-full"
            >
              <motion.li
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                whileHover={{ x: 10, scale: 1.04 }}
                className="flex items-center justify-center lg:justify-start gap-4 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl text-gray-900 font-black cursor-default transition-all"
              >
                <motion.span
                  className="w-5 h-5 rounded-full bg-green-400 flex-shrink-0 shadow-lg shadow-green-400/60"
                  whileHover={{ scale: 1.5, rotate: 180 }}
                  transition={{ type: "spring", stiffness: 400 }}
                ></motion.span>
                <span className="tracking-tight font-black">90%+ Precision (high-signal)</span>
              </motion.li>
              <motion.li
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.55 }}
                whileHover={{ x: 10, scale: 1.04 }}
                className="flex items-center justify-center lg:justify-start gap-4 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl text-gray-900 font-black cursor-default transition-all"
              >
                <motion.span
                  className="w-5 h-5 rounded-full bg-orange-400 flex-shrink-0 shadow-lg shadow-orange-400/60"
                  whileHover={{ scale: 1.5, rotate: 180 }}
                  transition={{ type: "spring", stiffness: 400 }}
                ></motion.span>
                <span className="tracking-tight font-black">≈ 8–12s Detection Time</span>
              </motion.li>
              <motion.li
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                whileHover={{ x: 10, scale: 1.04 }}
                className="flex items-center justify-center lg:justify-start gap-4 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl text-gray-900 font-black cursor-default transition-all"
              >
                <motion.span
                  className="w-5 h-5 rounded-full bg-purple-400 flex-shrink-0 shadow-lg shadow-purple-400/60"
                  whileHover={{ scale: 1.5, rotate: 180 }}
                  transition={{ type: "spring", stiffness: 400 }}
                ></motion.span>
                <span className="tracking-tight font-black">3K+ Videos Trained</span>
              </motion.li>
            </motion.ul>
          </motion.div>
          
          {/* Right side - Login card or animation */}
          <div className="hidden lg:block w-full lg:w-auto">
            <AIDetectionAnimation />
          </div>
        </div>
      </div>
    </section>
  );
}


