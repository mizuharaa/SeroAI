import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { AIDetectionAnimation } from './AIDetectionAnimation';

interface HeroSectionProps {
  onTryDemo: () => void;
  onUploadMedia: () => void;
}

export function HeroSection({ onTryDemo, onUploadMedia }: HeroSectionProps) {
  return (
    <section className="relative min-h-[95vh] flex items-center justify-center overflow-hidden pt-16">
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

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/90 backdrop-blur-md rounded-full border border-orange-200/50 shadow-lg"
            >
              <Sparkles className="w-4 h-4 text-orange-600" />
              <span className="text-sm text-gray-800 font-medium">Powered by Advanced Detection Algorithms</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-5xl sm:text-6xl lg:text-7xl text-gray-900 tracking-tight leading-[1.1] font-extrabold"
            >
              See Beyond Reality
              <br />
              <span className="bg-gradient-to-r from-orange-600 via-rose-500 to-pink-600 bg-clip-text text-transparent">
                with Sero
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-xl text-gray-700 max-w-xl leading-relaxed font-medium"
            >
              AI that detects deepfakes and restores trust in digital media. Protect authenticity. Empower truth.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-4 pt-4"
            >
              <Button
                size="lg"
                onClick={onTryDemo}
                className="bg-gray-900 hover:bg-gray-800 text-white border-0 shadow-xl hover:shadow-2xl transition-all text-base px-8 py-6 h-auto group font-semibold"
              >
                Start now
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={onUploadMedia}
                className="border-2 border-gray-300 bg-white hover:bg-gray-50 text-gray-900 shadow-lg text-base px-8 py-6 h-auto group font-semibold flex items-center gap-2"
              >
                Sign up with Google
              </Button>
            </motion.div>
          </motion.div>
          <div className="hidden lg:block">
            <AIDetectionAnimation />
          </div>
        </div>
      </div>
    </section>
  );
}


