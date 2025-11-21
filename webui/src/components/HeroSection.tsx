import React, { useRef } from 'react';
import {
  motion,
  useScroll,
  useTransform,
  MotionValue,
} from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { AIDetectionAnimation } from './AIDetectionAnimation';
import { getGradientForScroll } from '../utils/gradientPalette';

interface HeroSectionProps {
  onTryDemo: () => void;
  onUploadMedia: () => void;
}

export function HeroSection({ onTryDemo, onUploadMedia }: HeroSectionProps) {
  const sectionRef = useRef<HTMLElement>(null);

  // 🔥 Track GLOBAL window scroll (no target) so the gradient updates as page scrolls
  const { scrollYProgress } = useScroll();

  // Make transitions more dramatic / responsive
  const enhancedScrollProgress = useTransform(
    scrollYProgress,
    [0, 0.15, 0.4, 0.7, 1],
    [0, 0.25, 0.6, 0.85, 1]
  );

  // Map scroll → gradient string (light orange/rose → vibrant pink/purple)
  const gradientBackground: MotionValue<string> = useTransform(
    enhancedScrollProgress,
    (progress) => {
      const colors = getGradientForScroll(progress);
      return `linear-gradient(to bottom right, ${colors.from}, ${colors.via}, ${colors.to})`;
    }
  );

  // Blur blob gradients (more intense as you scroll)
  const blurGradient1Background: MotionValue<string> = useTransform(
    enhancedScrollProgress,
    (progress) => {
      const colors = getGradientForScroll(progress);
      const opacity1 = 0.4 + progress * 0.4; // 0.4 → 0.8
      const fromColor = colors.from
        .replace('rgb', 'rgba')
        .replace(')', `, ${opacity1})`);
      return `radial-gradient(circle, ${fromColor}, transparent)`;
    }
  );

  const blurGradient2Background: MotionValue<string> = useTransform(
    enhancedScrollProgress,
    (progress) => {
      const colors = getGradientForScroll(progress);
      const opacity2 = 0.35 + progress * 0.45; // 0.35 → 0.8
      const viaColor = colors.via
        .replace('rgb', 'rgba')
        .replace(')', `, ${opacity2})`);
      return `radial-gradient(circle, ${viaColor}, transparent)`;
    }
  );

  // Parallax effects for text
  const textY = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const textOpacity = useTransform(scrollYProgress, [0, 1], [1, 0.2]);
  const textScale = useTransform(scrollYProgress, [0, 1], [1, 0.92]);
  const textX = useTransform(scrollYProgress, [0, 1], [0, -40]);

  // Parallax for bullet points
  const bulletsY = useTransform(scrollYProgress, [0, 1], [0, 180]);
  const bulletsOpacity = useTransform(scrollYProgress, [0, 1], [1, 0.25]);
  const bulletsScale = useTransform(scrollYProgress, [0, 1], [1, 0.94]);

  return (
    <section
      ref={sectionRef}
      className="relative min-h-[95vh] flex items-center justify-center overflow-hidden pt-16 hero-section"
    >
      {/* 🔥 Scroll-based gradient background driven by MotionValue */}
      <motion.div
        className="absolute inset-0 hero-gradient-bg"
        style={{
          backgroundImage: gradientBackground,
          transition: 'background-image 0.08s linear',
          zIndex: 0,
          backgroundColor: 'transparent',
        }}
      >
        {/* Subtle dot grid overlay */}
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgb(251 146 60 / 0.15) 1px, transparent 0)',
            backgroundSize: '40px 40px',
            willChange: 'auto',
          }}
        />
      </motion.div>

      {/* Animated blur blobs that also react to scroll-based gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-0 left-0 w-[600px] h-[600px] rounded-full blur-3xl hero-blur-element"
          style={{
            backgroundImage: blurGradient1Background,
            transition: 'background-image 0.1s ease-out',
          }}
          animate={{ x: [0, 100, 0], y: [0, 80, 0], scale: [1, 1.2, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute top-20 right-0 w-[500px] h-[500px] rounded-full blur-3xl hero-blur-element"
          style={{
            backgroundImage: blurGradient2Background,
            transition: 'background-image 0.1s ease-out',
          }}
          animate={{ x: [0, -80, 0], y: [0, 100, 0], scale: [1, 1.15, 1] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      {/* Top right CTA */}
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

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex flex-col lg:flex-row items-center justify-center gap-12 lg:gap-16">
          {/* Left - Text */}
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
                scale: textScale,
              }}
              className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl text-gray-900 leading-tight font-black tracking-tight hero-text"
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
                scale: bulletsScale,
              }}
              className="space-y-5 pt-2 w-full hero-text"
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
                  transition={{ type: 'spring', stiffness: 400 }}
                  style={{ willChange: 'transform' }}
                />
                <span className="tracking-tight font-black">
                  90%+ Precision (high-signal)
                </span>
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
                  transition={{ type: 'spring', stiffness: 400 }}
                  style={{ willChange: 'transform' }}
                />
                <span className="tracking-tight font-black">
                  ≈ 8–12s Detection Time
                </span>
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
                  transition={{ type: 'spring', stiffness: 400 }}
                  style={{ willChange: 'transform' }}
                />
                <span className="tracking-tight font-black">
                  3K+ Videos Trained
                </span>
              </motion.li>
            </motion.ul>
          </motion.div>

          {/* Right - animation */}
          <div className="hidden lg:block w-full lg:w-auto">
            <AIDetectionAnimation />
          </div>
        </div>
      </div>
    </section>
  );
}
