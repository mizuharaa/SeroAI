import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { motion, useInView, animate, useScroll, useTransform } from 'framer-motion'
import {
  Shield,
  ShieldAlert,
  ScanFace,
  Activity,
  Workflow,
  EyeOff,
  ArrowRight,
  Zap,
  Grid3x3,
  Brain,
  Code2,
  Gauge,
  CheckCircle2,
  FileCode,
  Book,
  Menu,
  X,
  Moon,
  Sun,
  ChevronDown,
  Upload,
  BarChart3,
  Lock,
  Search,
  Network,
  Timer,
  Sparkles,
  ScanLine,
  Orbit,
  Box,
  Signal,
  Headphones,
  FileVideo,
  Loader2
} from 'lucide-react'
import { Twitter, Github, Linkedin } from 'lucide-react'
import { SimpleGlobe } from './components/SimpleGlobe'
import { UploadZone } from './components/UploadZone'
import { AnalysisProgress } from './components/AnalysisProgress'
import { ResultsDisplay } from './components/ResultsDisplay'
import { AnalysisLayout } from './components/analysis/AnalysisLayout'
import { DetectHero } from './components/DetectHero'
import { SchoolsMarquee } from './components/SchoolsMarquee'
import {
  FrequencyDomain3D,
  PixelStability3D,
  BiologicalInconsistency3D,
  OpticalFlow3D,
  SpatialLogic3D,
  AudioVisualSync3D,
} from './components/analysis/Realistic3DIcons'

const navItems = {
  Product: {
    items: [
      { title: 'Detection Engine', desc: 'AI-powered deepfake detection', icon: Shield },
      { title: 'Analytics Dashboard', desc: 'Real-time insights and reports', icon: BarChart3 },
      { title: 'API Access', desc: 'Integrate into your workflow', icon: Code2 }
    ]
  },
  Solutions: {
    items: [
      { title: 'Media Companies', desc: 'Protect your content authenticity', icon: Upload },
      { title: 'Enterprise Security', desc: 'Corporate deepfake prevention', icon: Lock },
      { title: 'Developers', desc: 'Build with our API', icon: Code2 }
    ]
  },
  Resources: {
    items: [
      { title: 'Documentation', desc: 'API docs and guides', icon: Book },
      { title: 'Case Studies', desc: 'See Sero in action', icon: BarChart3 },
      { title: 'Blog', desc: 'Latest news and updates', icon: FileCode }
    ]
  }
} as const

const PixelGridIcon = () => (
  <svg className="w-8 h-8 text-white" viewBox="0 0 32 32" fill="none">
    {/* Futuristic code terminal with depth */}
    <defs>
      <linearGradient id="codeGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="currentColor" stopOpacity="1" />
        <stop offset="100%" stopColor="currentColor" stopOpacity="0.4" />
      </linearGradient>
      <linearGradient id="codeGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="currentColor" stopOpacity="0.8" />
        <stop offset="100%" stopColor="currentColor" stopOpacity="0.2" />
      </linearGradient>
    </defs>
    {/* Terminal frame with 3D effect */}
    <rect x="3" y="3" width="20" height="20" rx="2" fill="url(#codeGrad1)" opacity="0.15" />
    <rect x="3" y="3" width="20" height="20" rx="2" stroke="currentColor" strokeWidth="1.2" fill="none" />
    <rect x="5" y="5" width="16" height="16" rx="1" stroke="currentColor" strokeWidth="0.8" fill="none" opacity="0.3" />
    
    {/* Code lines with realistic depth */}
    <rect x="7" y="8" width="8" height="1.5" rx="0.5" fill="currentColor" opacity="0.9" />
    <rect x="7" y="11" width="12" height="1.5" rx="0.5" fill="currentColor" opacity="0.7" />
    <rect x="7" y="14" width="6" height="1.5" rx="0.5" fill="currentColor" opacity="0.8" />
    <rect x="7" y="17" width="10" height="1.5" rx="0.5" fill="currentColor" opacity="0.6" />
    
    {/* API connection nodes */}
    <circle cx="22" cy="22" r="3.5" fill="url(#codeGrad2)" stroke="currentColor" strokeWidth="1.5" />
    <circle cx="22" cy="22" r="2" fill="currentColor" opacity="0.6" />
    <path d="M25.5 24.5l3.5 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
    <circle cx="29" cy="28" r="1.5" fill="currentColor" opacity="0.9" />
    
    {/* Glowing connection lines */}
    <path d="M22 22l2.5 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
  </svg>
)

const RealtimeIcon = () => (
  <svg className="w-8 h-8 text-white" viewBox="0 0 32 32" fill="none">
    <defs>
      <radialGradient id="pulseGrad" cx="50%" cy="50%">
        <stop offset="0%" stopColor="currentColor" stopOpacity="0.8" />
        <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
      </radialGradient>
      <linearGradient id="streamGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="currentColor" stopOpacity="1" />
        <stop offset="100%" stopColor="currentColor" stopOpacity="0.3" />
      </linearGradient>
    </defs>
    
    {/* Central hub with depth */}
    <circle cx="16" cy="16" r="9" fill="url(#pulseGrad)" opacity="0.2" />
    <circle cx="16" cy="16" r="7" stroke="currentColor" strokeWidth="1.8" fill="none" />
    <circle cx="16" cy="16" r="4.5" fill="currentColor" opacity="0.9" />
    
    {/* Real-time data streams - wave patterns */}
    <path
      d="M6 12 Q10 8, 14 12 T22 12"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
      strokeLinecap="round"
      opacity="0.7"
    />
    <path
      d="M6 20 Q10 24, 14 20 T22 20"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
      strokeLinecap="round"
      opacity="0.7"
    />
    
    {/* Data particles flowing */}
    <circle cx="10" cy="12" r="1.5" fill="currentColor" opacity="0.9" />
    <circle cx="14" cy="12" r="1.2" fill="currentColor" opacity="0.7" />
    <circle cx="18" cy="12" r="1.5" fill="currentColor" opacity="0.9" />
    <circle cx="10" cy="20" r="1.2" fill="currentColor" opacity="0.7" />
    <circle cx="14" cy="20" r="1.5" fill="currentColor" opacity="0.9" />
    <circle cx="18" cy="20" r="1.2" fill="currentColor" opacity="0.7" />
    
    {/* Clock hands for real-time indication */}
    <path d="M16 16l0 -5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" opacity="0.9" />
    <path d="M16 16l4 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.8" />
    
    {/* Outer pulse rings */}
    <circle cx="16" cy="16" r="11" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <circle cx="16" cy="16" r="13" stroke="currentColor" strokeWidth="0.8" opacity="0.2" />
    
    {/* Connection arrows indicating flow */}
    <path d="M24 8l2 -2m0 0l-2 -2m2 2l-4 0" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.6" />
    <path d="M24 24l2 2m0 0l-2 2m2 -2l-4 0" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.6" />
  </svg>
)

const ShieldGridIcon = () => (
  <svg className="w-8 h-8 text-white" viewBox="0 0 32 32" fill="none">
    <defs>
      <linearGradient id="shieldGrad1" x1="50%" y1="0%" x2="50%" y2="100%">
        <stop offset="0%" stopColor="currentColor" stopOpacity="0.9" />
        <stop offset="100%" stopColor="currentColor" stopOpacity="0.3" />
      </linearGradient>
      <linearGradient id="shieldGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="currentColor" stopOpacity="0.6" />
        <stop offset="100%" stopColor="currentColor" stopOpacity="0.1" />
      </linearGradient>
      <pattern id="gridPattern" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
        <path d="M 4 0 L 0 0 0 4" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.3" />
      </pattern>
    </defs>
    
    {/* Main shield with 3D depth */}
    <path
      d="M16 3.5l8.5 2.8v5.7c0 6.2-3.8 11.8-8.5 14.3-4.7-2.5-8.5-8.1-8.5-14.3V6.3L16 3.5z"
      fill="url(#shieldGrad1)"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinejoin="round"
    />
    
    {/* Inner shield layer for depth */}
    <path
      d="M16 6.5l6.5 2.2v4.3c0 4.8-2.9 9.2-6.5 11.1-3.6-1.9-6.5-6.3-6.5-11.1V8.7L16 6.5z"
      fill="url(#shieldGrad2)"
      stroke="currentColor"
      strokeWidth="1"
      strokeLinejoin="round"
      opacity="0.4"
    />
    
    {/* Grid pattern overlay */}
    <path
      d="M16 3.5l8.5 2.8v5.7c0 6.2-3.8 11.8-8.5 14.3-4.7-2.5-8.5-8.1-8.5-14.3V6.3L16 3.5z"
      fill="url(#gridPattern)"
      opacity="0.4"
    />
    
    {/* Central security core */}
    <circle cx="16" cy="14" r="3.5" fill="currentColor" opacity="0.9" />
    <circle cx="16" cy="14" r="2.2" fill="none" stroke="currentColor" strokeWidth="1.2" opacity="0.6" />
    
    {/* Lock mechanism details */}
    <rect x="14.5" y="12" width="3" height="2.5" rx="0.5" fill="currentColor" opacity="0.8" />
    <path d="M14.5 12h3" stroke="currentColor" strokeWidth="0.8" opacity="0.5" />
    
    {/* Security verification lines */}
    <path d="M16 10.5v7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
    <path d="M12.5 14h7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
    <path d="M13.5 12h5" stroke="currentColor" strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    <path d="M13.5 16h5" stroke="currentColor" strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    
    {/* Outer protection rings */}
    <ellipse cx="16" cy="8" rx="6" ry="2" stroke="currentColor" strokeWidth="1" opacity="0.3" />
    <ellipse cx="16" cy="20" rx="7" ry="3" stroke="currentColor" strokeWidth="0.8" opacity="0.2" />
  </svg>
)

function useSmoothScroll() {
  useEffect(() => {
    if (typeof window === 'undefined') return
    const isPointerFine = window.matchMedia('(pointer: fine)').matches
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!isPointerFine || prefersReducedMotion) return
    let target = window.scrollY
    let current = window.scrollY
    let rafId: number | null = null

    const update = () => {
      current += (target - current) * 0.12
      window.scrollTo(0, current)
      if (Math.abs(target - current) > 0.5) {
        rafId = requestAnimationFrame(update)
      } else {
        rafId = null
      }
    }

    const onWheel = (event: WheelEvent) => {
      event.preventDefault()
      target = Math.min(
        document.body.scrollHeight - window.innerHeight,
        Math.max(0, target + event.deltaY)
      )
      if (rafId === null) {
        rafId = requestAnimationFrame(update)
      }
    }

    window.addEventListener('wheel', onWheel, { passive: false })
    return () => {
      window.removeEventListener('wheel', onWheel)
      if (rafId !== null) cancelAnimationFrame(rafId)
    }
  }, [])
}

type AuthUser = {
  id: number
  email: string
  name: string
  picture?: string | null
  provider: 'google' | 'local'
}

export default function App() {
  // Simple client-side routing without extra deps
  useSmoothScroll()
  const [route, setRoute] = useState<string>(typeof window !== 'undefined' ? window.location.pathname : '/')
  useEffect(() => {
    const onPop = () => setRoute(window.location.pathname)
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])
  const navigate = (path: string) => {
    if (window.location.pathname !== path) {
      window.history.pushState({}, '', path)
      setRoute(path)
    }
  }
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const getInitialTheme = () => {
    if (typeof window === 'undefined') return false
    try {
      const saved = localStorage.getItem('theme')
      if (saved === 'dark' || saved === 'light') {
        return saved === 'dark'
      }
      // Fallback to system preference
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    } catch {
      return false
    }
  }
  const [isDarkMode, setIsDarkMode] = useState<boolean>(getInitialTheme)
  const [themeTransitionTarget, setThemeTransitionTarget] = useState<'dark' | 'light' | null>(null)
  const [scrolled, setScrolled] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [authUser, setAuthUser] = useState<AuthUser | null>(null)
  const [authLoading, setAuthLoading] = useState<boolean>(true)
  const startGoogleLogin = () => {
    if (typeof window === 'undefined') return
    window.location.assign('/auth/google')
  }

  // Helper: show logo splash, then run callback (e.g., navigate)
  const withLogoSplash = (action: () => void) => {
    setIsTransitioning(true)
    // Brief pre-delay for pop
    setTimeout(() => {
      action()
      // Keep splash visible a moment after route change
      setTimeout(() => setIsTransitioning(false), 900)
    }, 150)
  }

  // Delayed theme flip: play animation first, then switch theme for a smoother effect
  const handleDarkModeToggle = () => {
    const html = document.documentElement
    const newDark = !html.classList.contains('dark')

    setThemeTransitionTarget(newDark ? 'dark' : 'light')
    setIsTransitioning(true)

    // Apply the actual theme after the animation finishes
    const ANIM_MS = 900
    setTimeout(() => {
      if (newDark) {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
      try {
        localStorage.setItem('theme', newDark ? 'dark' : 'light')
      } catch {}
      setIsDarkMode(newDark)
      setIsTransitioning(false)
      setThemeTransitionTarget(null)
    }, ANIM_MS)
  }

  // Initialize state from whatever index.html already applied; do not mutate here
  useLayoutEffect(() => {
    const initialDark = document.documentElement.classList.contains('dark')
    setIsDarkMode(initialDark)
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const fetchAuthState = async () => {
    try {
      const res = await fetch('/auth/me')
      if (!res.ok) return
      const data = await res.json()
      setAuthUser(data.authenticated ? data.user : null)
    } catch (err) {
      console.error('Failed to load auth state', err)
    } finally {
      setAuthLoading(false)
    }
  }

  useEffect(() => {
    fetchAuthState()
  }, [])

  const handleLogout = async () => {
    try {
      await fetch('/auth/logout', { method: 'POST' })
      setAuthUser(null)
    } catch (err) {
      console.error('Failed to logout', err)
    }
  }

  const scrollToAuthPanel = () => {
    const target = document.getElementById('auth-panel')
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  // Apply theme changes and persist to localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return
    const html = document.documentElement
    if (isDarkMode) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
    try {
      localStorage.setItem('theme', isDarkMode ? 'dark' : 'light')
    } catch {
      // ignore storage failures
    }
  }, [isDarkMode])

  // (handler defined above)

  const overlayTheme = themeTransitionTarget ?? (isDarkMode ? 'dark' : 'light')
  const overlayColorClass = overlayTheme === 'dark' ? 'bg-slate-950' : 'bg-white'

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      {isTransitioning && (
        <>
          <motion.div
            initial={{ clipPath: 'circle(0% at 100% 0%)' }}
            animate={{ clipPath: 'circle(150% at 100% 0%)' }}
            transition={{ duration: 0.8, ease: [0.43, 0.13, 0.23, 0.96] }}
            className={`fixed inset-0 z-[100] pointer-events-none ${overlayColorClass}`}
          />
          <div className="fixed inset-0 z-[101] flex items-center justify-center pointer-events-none">
            <motion.div className="relative">
              <motion.div
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: [0, 1, 1, 0], scale: [0.7, 1.15, 1.15, 1.1] }}
                transition={{ duration: 1.2, times: [0, 0.25, 0.7, 1], ease: 'easeOut' }}
                className="absolute -inset-8 rounded-full bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 blur-2xl"
              />
              <motion.div
                initial={{ y: 0, scale: 0.8, opacity: 0 }}
                animate={{ y: [0, -10, -10, 400], scale: [0.8, 1.05, 1.05, 1.0], opacity: [0, 1, 1, 0] }}
                transition={{ duration: 1.2, times: [0, 0.25, 0.7, 1], ease: [0.34, 1.56, 0.64, 1] }}
                className="relative px-12 py-8 rounded-3xl bg-gradient-to-br from-orange-500 via-pink-500 to-purple-500 shadow-2xl"
              >
                <span
                  className="text-8xl text-white tracking-tight block sero-brand"
                  style={{ 
                    background: 'linear-gradient(135deg, #ffffff 0%, #ffffff 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Sero
                </span>
              </motion.div>
            </motion.div>
          </div>
        </>
      )}

      <nav
        className={`sticky top-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-gradient-to-r from-orange-50/95 via-pink-50/95 to-rose-50/95 dark:from-slate-950/95 dark:via-slate-950/90 dark:to-slate-950/95 backdrop-blur-2xl border-b-2 border-orange-200/50 dark:border-slate-700/50 shadow-2xl shadow-orange-500/10'
            : 'bg-gradient-to-r from-orange-100/80 via-pink-100/70 to-rose-100/80 dark:from-slate-950/20 dark:via-slate-950/15 dark:to-slate-950/20 backdrop-blur-2xl border-b-2 border-orange-300/40 dark:border-slate-800/40 shadow-xl shadow-orange-500/20'
        }`}
        onMouseLeave={() => setActiveDropdown(null)}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className={`flex items-center justify-between transition-all duration-300 ${scrolled ? 'h-14' : 'h-16'}`}>
            <a
              href="/"
              className="flex items-center cursor-pointer group"
              onClick={(e) => {
                e.preventDefault()
                navigate('/')
                setIsMobileMenuOpen(false)
                setActiveDropdown(null)
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  navigate('/')
                  setIsMobileMenuOpen(false)
                  setActiveDropdown(null)
                  window.scrollTo({ top: 0, behavior: 'smooth' })
                }
              }}
              aria-label="Go to home"
              title="Go to home"
            >
              <span className="text-4xl sero-brand tracking-tighter relative inline-block group-hover:scale-105 transition-transform duration-300" style={{
                background: 'linear-gradient(135deg, #f97316 0%, #ec4899 50%, #f43f5e 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>
                Sero
              </span>
            </a>
            <div className="hidden lg:flex items-center gap-2">
              {Object.keys(navItems).map((item) => (
                <div key={item} onMouseEnter={() => setActiveDropdown(item)} className="relative">
                  <button className="px-5 py-2.5 text-gray-900 dark:text-gray-100 font-semibold transition-all duration-300 flex items-center gap-1.5 hover:text-orange-600 dark:hover:text-orange-400 hover:bg-gradient-to-r hover:from-orange-100/80 hover:to-pink-100/80 dark:hover:from-orange-900/30 dark:hover:to-pink-900/30 rounded-full hover:shadow-lg hover:shadow-orange-500/20 hover:scale-105 border border-transparent hover:border-orange-300/50 dark:hover:border-orange-700/50">
                    <span>{item}</span>
                    <ChevronDown className="w-4 h-4 transition-transform duration-300 group-hover:rotate-180" />
                  </button>
                </div>
              ))}
              <a
                href="#pricing"
                className="px-5 py-2.5 text-gray-900 dark:text-gray-100 font-semibold transition-all duration-300 hover:text-orange-600 dark:hover:text-orange-400 hover:bg-gradient-to-r hover:from-orange-100/80 hover:to-pink-100/80 dark:hover:from-orange-900/30 dark:hover:to-pink-900/30 rounded-full hover:shadow-lg hover:shadow-orange-500/20 hover:scale-105 border border-transparent hover:border-orange-300/50 dark:hover:border-orange-700/50"
              >
                Pricing
              </a>
              <a
                href="#contact"
                className="px-5 py-2.5 text-gray-900 dark:text-gray-100 font-semibold transition-all duration-300 hover:text-orange-600 dark:hover:text-orange-400 hover:bg-gradient-to-r hover:from-orange-100/80 hover:to-pink-100/80 dark:hover:from-orange-900/30 dark:hover:to-pink-900/30 rounded-full hover:shadow-lg hover:shadow-orange-500/20 hover:scale-105 border border-transparent hover:border-orange-300/50 dark:hover:border-orange-700/50"
              >
                Contact
              </a>
            </div>
            <div className="hidden lg:flex items-center gap-3">
              <button
                onClick={handleDarkModeToggle}
                className="p-2.5 rounded-full hover:bg-gradient-to-r hover:from-orange-100/60 hover:to-pink-100/60 dark:hover:from-orange-900/20 dark:hover:to-pink-900/20 transition-all duration-300 flex items-center gap-2 border border-transparent hover:border-orange-300/30 dark:hover:border-orange-700/30 hover:shadow-md"
                aria-label="Toggle dark mode"
                role="switch"
                aria-checked={isDarkMode}
              >
                {isDarkMode ? <Sun className="w-5 h-5 text-orange-500" /> : <Moon className="w-5 h-5 text-orange-600" />}
                <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{isDarkMode ? 'Dark' : 'Light'}</span>
              </button>
              {!authUser ? (
                <>
                  <motion.button
                    whileHover={{ scale: 1.08, y: -1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={scrollToAuthPanel}
                    className="px-5 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100 border-2 border-orange-400/60 dark:border-orange-500/40 rounded-full hover:bg-gradient-to-r hover:from-orange-50 hover:to-pink-50 dark:hover:from-orange-900/20 dark:hover:to-pink-900/20 hover:border-orange-500 dark:hover:border-orange-400 hover:shadow-lg hover:shadow-orange-500/30 transition-all duration-300"
                  >
                    Login / Sign up
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.08, y: -1 }}
                    whileTap={{ scale: 0.95 }}
                    type="button"
                    onClick={startGoogleLogin}
                    className="px-5 py-2.5 text-gray-900 dark:text-gray-100 hover:text-orange-600 dark:hover:text-orange-400 transition-all duration-300 flex items-center gap-2 rounded-full border-2 border-gray-300 dark:border-slate-600 hover:border-orange-400 dark:hover:border-orange-500 hover:bg-gradient-to-r hover:from-orange-50 hover:to-pink-50 dark:hover:from-orange-900/20 dark:hover:to-pink-900/20 hover:shadow-lg hover:shadow-orange-500/20 font-semibold"
                  >
                    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M18.17 10.19c0-.63-.06-1.24-.16-1.83H10v3.46h4.58c-.2 1.05-.8 1.93-1.69 2.53v2.11h2.73c1.6-1.47 2.53-3.64 2.53-6.27z" fill="#4285F4" />
                      <path d="M10 18.5c2.28 0 4.2-.75 5.6-2.04l-2.73-2.11c-.76.51-1.73.81-2.87.81-2.21 0-4.08-1.49-4.75-3.5H2.42v2.18A8.5 8.5 0 0010 18.5z" fill="#34A853" />
                      <path d="M5.25 10.66c-.17-.51-.27-1.05-.27-1.61s.1-1.1.27-1.61V5.26H2.42A8.5 8.5 0 001.5 10c0 1.37.33 2.67.92 3.82l2.83-2.16z" fill="#FBBC05" />
                      <path d="M10 4.24c1.25 0 2.37.43 3.25 1.27l2.44-2.44C14.2 1.69 12.28.9 10 .9a8.5 8.5 0 00-7.58 4.68l2.83 2.18c.67-2.01 2.54-3.5 4.75-3.5z" fill="#EA4335" />
                    </svg>
                    <span>Google</span>
                  </motion.button>
                </>
              ) : (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-3 px-3 py-1.5 rounded-full bg-white/90 dark:bg-slate-800/90 border-2 border-orange-200/50 dark:border-orange-700/50 shadow-lg">
                    {authUser.picture ? (
                      <img src={authUser.picture} alt={authUser.name} className="w-8 h-8 rounded-full object-cover ring-2 ring-orange-400/50" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-orange-500 to-pink-500 flex items-center justify-center text-white text-sm font-bold ring-2 ring-orange-400/50">
                        {authUser.name
                          .split(' ')
                          .map((n) => n[0])
                          .slice(0, 2)
                          .join('')
                          .toUpperCase()}
                      </div>
                    )}
                    <div className="text-left">
                      <p className="text-sm font-bold text-gray-900 dark:text-white leading-tight">{authUser.name}</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400 leading-tight">{authUser.email}</p>
                    </div>
                  </div>
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={handleLogout} className="px-5 py-2 text-gray-900 dark:text-gray-100 hover:text-orange-600 dark:hover:text-orange-400 transition-all duration-300 rounded-full border-2 border-transparent hover:border-orange-400 dark:hover:border-orange-500 hover:bg-gradient-to-r hover:from-orange-50 hover:to-pink-50 dark:hover:from-orange-900/20 dark:hover:to-pink-900/20 font-semibold hover:shadow-lg hover:shadow-orange-500/20">
                    Sign out
                  </motion.button>
                </div>
              )}
              <motion.button
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => withLogoSplash(() => navigate('/detect'))}
                className="px-6 py-2.5 bg-gradient-to-r from-orange-500 via-pink-500 to-rose-500 text-white rounded-full font-bold shadow-xl shadow-orange-500/40 hover:shadow-2xl hover:shadow-orange-500/60 transition-all duration-300 border-2 border-white/20 hover:border-white/40 relative overflow-hidden group"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></span>
                <span className="relative">Get Started</span>
              </motion.button>
            </div>
            <button
              className="lg:hidden p-2 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
        {activeDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="absolute inset-x-0 -mt-1 pt-1"
            onMouseLeave={() => setActiveDropdown(null)}
            onMouseEnter={() => setActiveDropdown(activeDropdown)}
          >
            <div className="mx-auto w-full max-w-5xl px-6 pt-2">
              <div className="bg-gradient-to-br from-white via-orange-50/30 to-pink-50/30 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 border-2 border-orange-200/60 dark:border-orange-700/60 rounded-3xl shadow-2xl shadow-orange-500/20 overflow-hidden backdrop-blur-xl">
                <div className="p-6">
                  <div className="grid grid-cols-3 gap-4">
                    {navItems[activeDropdown as keyof typeof navItems]?.items.map((item, index) => {
                      const Icon = item.icon
                      return (
                        <motion.a
                          key={item.title}
                          href="#"
                          initial={{ opacity: 0, x: -20, scale: 0.9 }}
                          animate={{ opacity: 1, x: 0, scale: 1 }}
                          transition={{ duration: 0.3, delay: index * 0.08, ease: 'easeOut' }}
                          whileHover={{ x: 8, scale: 1.05, transition: { duration: 0.2 } }}
                          className="flex flex-col items-start gap-4 p-5 rounded-2xl hover:bg-gradient-to-br hover:from-orange-100/80 hover:to-pink-100/80 dark:hover:from-orange-900/30 dark:hover:to-pink-900/30 transition-all duration-300 border-2 border-transparent hover:border-orange-300/50 dark:hover:border-orange-700/50 hover:shadow-xl hover:shadow-orange-500/20 cursor-pointer group"
                        >
                          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 via-pink-500 to-rose-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-orange-500/40 group-hover:shadow-xl group-hover:shadow-orange-500/60 group-hover:scale-110 transition-all duration-300">
                            <Icon className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h3 className="text-gray-900 dark:text-white mb-1.5 font-bold text-lg group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">{item.title}</h3>
                            <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">{item.desc}</p>
                          </div>
                        </motion.a>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950">
            <div className="px-6 py-4 space-y-2">
              {Object.keys(navItems).map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="block px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors"
                >
                  {item}
                </a>
              ))}
              <a
                href="#pricing"
                className="block px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors"
              >
                Pricing
              </a>
              <a
                href="#contact"
                className="block px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors"
              >
                Contact
              </a>
              <div className="pt-4 border-t border-gray-200 dark:border-slate-800 space-y-2">
                <button
                  onClick={handleDarkModeToggle}
                  className="w-full px-4 py-2 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors flex items-center justify-between"
                  aria-label="Toggle dark mode (mobile)"
                  role="switch"
                  aria-checked={isDarkMode}
                >
                  <span className="text-gray-900 dark:text-gray-100">Theme</span>
                  <span className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                    {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                    {isDarkMode ? 'Dark' : 'Light'}
                  </span>
                </button>
                {!authUser ? (
                  <>
                <button
                  className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors"
                      onClick={() => {
                        scrollToAuthPanel()
                        setIsMobileMenuOpen(false)
                      }}
                    >
                      Login / Sign up
                    </button>
                    <button
                  className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors flex items-center justify-center gap-2"
                      type="button"
                      onClick={startGoogleLogin}
                    >
                      <svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18.17 10.19c0-.63-.06-1.24-.16-1.83H10v3.46h4.58c-.2 1.05-.8 1.93-1.69 2.53v2.11h2.73c1.6-1.47 2.53-3.64 2.53-6.27z" fill="#4285F4" />
                        <path d="M10 18.5c2.28 0 4.2-.75 5.6-2.04l-2.73-2.11c-.76.51-1.73.81-2.87.81-2.21 0-4.08-1.49-4.75-3.5H2.42v2.18A8.5 8.5 0 0010 18.5z" fill="#34A853" />
                        <path d="M5.25 10.66c-.17-.51-.27-1.05-.27-1.61s.1-1.1.27-1.61V5.26H2.42A8.5 8.5 0 001.5 10c0 1.37.33 2.67.92 3.82l2.83-2.16z" fill="#FBBC05" />
                        <path d="M10 4.24c1.25 0 2.37.43 3.25 1.27l2.44-2.44C14.2 1.69 12.28.9 10 .9a8.5 8.5 0 00-7.58 4.68l2.83 2.18c.67-2.01 2.54-3.5 4.75-3.5z" fill="#EA4335" />
                      </svg>
                      Google
                    </button>
                  </>
                ) : (
                  <button
                className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors"
                    onClick={() => {
                      handleLogout()
                      setIsMobileMenuOpen(false)
                    }}
                  >
                    Sign out
                  </button>
                )}
                <button
                  onClick={() => {
                    setIsMobileMenuOpen(false)
                    withLogoSplash(() => navigate('/detect'))
                  }}
                  className="w-full px-4 py-2 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-full"
                >
                  Get Started
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {route !== '/detect' && (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-200 via-rose-300 to-pink-300 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
          <motion.div
            animate={{ x: [0, 120, -60, 0], y: [0, -90, 70, 0] }}
            transition={{ duration: 22, repeat: Infinity, ease: 'linear' }}
            className="absolute top-14 left-1/4 w-[560px] h-[560px] bg-gradient-to-br from-orange-400/50 to-pink-400/50 rounded-full blur-3xl"
          />
          <motion.div
            animate={{ x: [0, -80, 50, 0], y: [0, 60, -50, 0] }}
            transition={{ duration: 26, repeat: Infinity, ease: 'linear' }}
            className="absolute bottom-10 right-1/5 w-[480px] h-[480px] bg-gradient-to-tr from-rose-400/45 via-amber-400/30 to-pink-400/45 rounded-full blur-3xl"
          />
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-12 items-center">
          <HeroLeft user={authUser} onAuthChange={setAuthUser} loading={authLoading} startGoogleLogin={startGoogleLogin} />
          <motion.div initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.3 }}>
            <AIDetectionDemo />
          </motion.div>
        </div>
      </section>
      )}

      {route !== '/detect' ? (
        <>
          <HowItWorksSection />
          <DeveloperSection />
          <WhySeroSection />
          <GlobalSection />
          <DashboardSection />
          <SchoolsMarquee />
          <StartFreeButton onClick={() => withLogoSplash(() => navigate('/detect'))} />
          <Footer />
        </>
      ) : (
        <DetectPage />
      )}
    </div>
  )
}

function DetectPage() {
  return (
    <div className="pt-20">
      {/* New innovative hero with scroll animations */}
      <DetectHero />
      {/* Main detect content */}
      <DetectSection />
      <SchoolsMarquee />
      <Footer />
    </div>
  )
}

// Lightweight Sero colorwave animation component
function SeroColorwave() {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: false, margin: '-100px' })
  const letters = ['S', 'e', 'r', 'o']

  return (
    <span
      ref={ref}
      className="inline-block relative"
      style={{
        fontFamily: 'system-ui, -apple-system, sans-serif',
      }}
    >
      {letters.map((letter, idx) => (
        <span
          key={idx}
          className="inline-block font-black bg-clip-text text-transparent"
          style={{
            backgroundImage: 'linear-gradient(90deg, #fed7aa 0%, #fdba74 12%, #fb923c 25%, #f97316 37%, #ea580c 50%, #dc2626 62%, #f97316 75%, #fb923c 87%, #fdba74 100%)',
            backgroundSize: '400% 100%',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            animation: isInView ? `colorwave 8s linear infinite` : 'none',
            animationDelay: `${idx * 0.3}s`,
          }}
        >
          {letter}
        </span>
      ))}
      <style>{`
        @keyframes colorwave {
          0% { background-position: 400% 0; }
          100% { background-position: -400% 0; }
        }
      `}</style>
    </span>
  )
}

function HeroLeft(props: {
  user: AuthUser | null
  onAuthChange: (user: AuthUser | null) => void
  loading: boolean
  startGoogleLogin: () => void
}) {
  const { user, onAuthChange, loading, startGoogleLogin } = props
  return (
    <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }} className="space-y-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="inline-flex items-center gap-2 px-4 py-2 bg-white/70 dark:bg-slate-800/70 rounded-full border border-orange-200 dark:border-orange-900/30 backdrop-blur-sm"
      >
        <motion.div
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        >
          <Zap className="w-4 h-4 text-orange-600" />
        </motion.div>
        <span className="text-gray-700 dark:text-gray-300 font-medium">Now with chatbot integration</span>
      </motion.div>
      <div className="space-y-4">
        <h1
          className="text-gray-900 dark:text-white tracking-tight leading-[0.9]"
          style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
        >
          <motion.span 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ duration: 0.5, delay: 0.3 }} 
            className="block text-7xl sm:text-8xl lg:text-9xl font-black"
          >
            See Beyond
          </motion.span>
          <motion.span 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ duration: 0.5, delay: 0.4 }} 
            className="block text-7xl sm:text-8xl lg:text-9xl font-black"
          >
            Reality
          </motion.span>
          <motion.span
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="block text-7xl sm:text-8xl lg:text-9xl font-black relative"
            style={{
              fontFamily: 'system-ui, -apple-system, sans-serif',
            }}
          >
            <span className="text-gray-900 dark:text-white">with </span>
            <SeroColorwave />
          </motion.span>
        </h1>
      </div>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="text-xl lg:text-2xl text-gray-600 dark:text-gray-400 max-w-xl leading-relaxed"
      >
        AI that detects deepfakes and restores trust in digital media. Protect authenticity. <span className="text-gray-900 dark:text-white">Empower truth.</span>
      </motion.p>
      <StatsRow />
      <CTAs />
      <AuthPanel user={user} onAuthChange={onAuthChange} loading={loading} startGoogleLogin={startGoogleLogin} />
    </motion.div>
  )
}

function StatsRow() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.7 }} className="flex flex-wrap items-center gap-6">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
        <span className="text-gray-700 dark:text-gray-300">
          <span className="text-gray-900 dark:text-white">90%+</span> Precision (high-signal)
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
        <span className="text-gray-700 dark:text-gray-300">
          <span className="text-gray-900 dark:text-white">≈ 8–12s</span> Detection Time
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" />
        <span className="text-gray-700 dark:text-gray-300">
          <span className="text-gray-900 dark:text-white">3K+</span> Videos Trained
        </span>
      </div>
    </motion.div>
  )
}

function CTAs() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.8 }}
      className="flex flex-wrap items-center justify-center gap-4 text-center w-full"
    >
      <motion.button
        whileHover={{ scale: 1.05, y: -3 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => {
          if (window.location.pathname !== '/detect') {
            window.history.pushState({}, '', '/detect')
          }
          window.dispatchEvent(new PopStateEvent('popstate'))
        }}
        className="group px-10 py-4 bg-gray-900 dark:bg-slate-100 text-white dark:text-gray-900 rounded-full shadow-xl hover:shadow-2xl transition-shadow flex items-center gap-3 mx-auto"
      >
        <span>Start now</span>
        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </motion.button>
    </motion.div>
  )
}

function AuthPanel({
  user,
  onAuthChange,
  loading,
  startGoogleLogin
}: {
  user: AuthUser | null
  onAuthChange: (user: AuthUser | null) => void
  loading: boolean
  startGoogleLogin: () => void
}) {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [formLoading, setFormLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormLoading(true)
    setError(null)
    setMessage(null)
    try {
      const endpoint = mode === 'signup' ? '/auth/register' : '/auth/login'
      const payload: Record<string, string> = {
        email: form.email.trim(),
        password: form.password
      }
      if (mode === 'signup') {
        payload.name = form.name.trim() || form.email.trim().split('@')[0]
      }
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Unable to authenticate')
      }
      onAuthChange(data.user)
      setMessage(mode === 'signup' ? 'Account created' : 'Welcome back')
      setForm({ name: '', email: '', password: '' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setFormLoading(false)
    }
  }

  const logout = async () => {
    await fetch('/auth/logout', { method: 'POST' })
    onAuthChange(null)
  }

  if (loading) {
    return (
      <div id="auth-panel" className="w-full max-w-md rounded-3xl border border-white/10 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl shadow-2xl p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded-full" />
          <div className="h-10 w-full bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          <div className="h-10 w-full bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        </div>
      </div>
    )
  }

  return (
    <div id="auth-panel" className="w-full max-w-md rounded-3xl border border-white/15 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-2xl p-6 space-y-5">
      {!user ? (
        <>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.5em] text-gray-500 dark:text-gray-400">Access</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">Secure your workspace</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setMode('login')}
                className={`px-3 py-1.5 text-sm rounded-full border ${mode === 'login' ? 'border-orange-400 text-orange-500' : 'border-transparent text-gray-500 dark:text-gray-400'}`}
              >
                Login
              </button>
              <button
                onClick={() => setMode('signup')}
                className={`px-3 py-1.5 text-sm rounded-full border ${mode === 'signup' ? 'border-orange-400 text-orange-500' : 'border-transparent text-gray-500 dark:text-gray-400'}`}
              >
                Sign up
              </button>
            </div>
          </div>
          <button
            onClick={startGoogleLogin}
          className="w-full flex items-center justify-center gap-3 rounded-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 py-3 text-gray-900 dark:text-white font-semibold hover:border-orange-400 transition-colors"
            type="button"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18.17 10.19c0-.63-.06-1.24-.16-1.83H10v3.46h4.58c-.2 1.05-.8 1.93-1.69 2.53v2.11h2.73c1.6-1.47 2.53-3.64 2.53-6.27z" fill="#4285F4" />
              <path d="M10 18.5c2.28 0 4.2-.75 5.6-2.04l-2.73-2.11c-.76.51-1.73.81-2.87.81-2.21 0-4.08-1.49-4.75-3.5H2.42v2.18A8.5 8.5 0 0010 18.5z" fill="#34A853" />
              <path d="M5.25 10.66c-.17-.51-.27-1.05-.27-1.61s.1-1.1.27-1.61V5.26H2.42A8.5 8.5 0 001.5 10c0 1.37.33 2.67.92 3.82l2.83-2.16z" fill="#FBBC05" />
              <path d="M10 4.24c1.25 0 2.37.43 3.25 1.27l2.44-2.44C14.2 1.69 12.28.9 10 .9a8.5 8.5 0 00-7.58 4.68l2.83 2.18c.67-2.01 2.54-3.5 4.75-3.5z" fill="#EA4335" />
            </svg>
            Continue with Google
          </button>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-gray-200 dark:bg-slate-700" />
            <span className="text-xs uppercase tracking-[0.5em] text-gray-400 dark:text-gray-500">or</span>
            <div className="flex-1 h-px bg-gray-200 dark:bg-slate-700" />
          </div>
          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === 'signup' && (
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-300">Full name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                  className="mt-1 w-full rounded-xl border border-gray-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-400 dark:focus:ring-orange-500"
                  placeholder="Ada Lovelace"
                  required
                />
              </div>
            )}
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-300">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
                className="mt-1 w-full rounded-xl border border-gray-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-400 dark:focus:ring-orange-500"
                placeholder="you@company.com"
                required
              />
            </div>
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-300">Password</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                className="mt-1 w-full rounded-xl border border-gray-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-400 dark:focus:ring-orange-500"
                placeholder="Minimum 8 characters"
                required
              />
            </div>
            {error && <p className="text-sm text-rose-500">{error}</p>}
            {message && <p className="text-sm text-emerald-500">{message}</p>}
            <button
              type="submit"
              disabled={formLoading}
              className="w-full rounded-full bg-gradient-to-r from-orange-500 to-pink-500 text-white py-3 font-semibold shadow-lg shadow-orange-500/30 disabled:opacity-60"
            >
              {formLoading ? 'Processing…' : mode === 'signup' ? 'Create account' : 'Log in'}
            </button>
          </form>
        </>
      ) : (
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.5em] text-gray-500 dark:text-gray-400">You’re in</p>
          <div className="flex items-center gap-4">
            {user.picture ? (
              <img src={user.picture} alt={user.name} className="w-14 h-14 rounded-2xl object-cover" />
            ) : (
              <div className="w-14 h-14 rounded-2xl bg-orange-500/80 flex items-center justify-center text-white text-xl font-bold">
                {user.name
                  .split(' ')
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join('')
                  .toUpperCase()}
              </div>
            )}
            <div>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{user.name}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
              <p className="text-xs uppercase tracking-[0.4em] text-gray-400 dark:text-gray-500 mt-1">{user.provider}</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            You’re authenticated. Upload footage, save reports, and track investigations across your workspace.
          </p>
          <button onClick={logout} className="w-full rounded-full border border-gray-200 dark:border-slate-700 py-3 text-gray-900 dark:text-white hover:border-orange-400 transition-colors">
            Sign out
          </button>
        </div>
      )}
    </div>
  )
}

// Detection page section (standalone page)
function DetectSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-50px' })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [overallProgress, setOverallProgress] = useState(0)
  const [overallScore, setOverallScore] = useState(0)
  const [processingTime, setProcessingTime] = useState(0)
  const [feedbackId, setFeedbackId] = useState<string | null>(null)
  type LocalAnalysisMethod = {
    id: string
    name: string
    description: string
    status: 'pending' | 'analyzing' | 'complete'
    icon: typeof Search | typeof Network | typeof Timer | typeof ScanFace | typeof Signal | typeof Headphones
    gradient: string
    glowColor: string
  }
  const [results, setResults] = useState<
    Array<{ method: string; score: number; confidence: number; details: string[]; icon: 'eye' | 'zap' | 'waves' | 'box' | 'audio' | 'grid' }>
  >([])
  const [methods, setMethods] = useState<LocalAnalysisMethod[]>([
    // Order matches backend stage completion so checks cascade top→bottom
    { id: '1', name: 'Frequency Domain Analysis', description: 'Detecting GAN fingerprints in spectral data', status: 'pending', icon: Search, gradient: 'from-orange-400 to-red-500', glowColor: '249, 115, 22' }, // forensics
    { id: '2', name: 'Pixel Stability Analysis', description: 'Analyzing temporal consistency in static regions', status: 'pending', icon: Grid3x3, gradient: 'from-purple-500 to-pink-500', glowColor: '168, 85, 247' }, // artifact
    { id: '3', name: 'Biological Inconsistency Detection', description: 'Examining facial landmarks and body movements', status: 'pending', icon: ScanFace, gradient: 'from-blue-500 to-cyan-500', glowColor: '59, 130, 246' }, // face_dynamics
    { id: '4', name: 'Optical Flow Analysis', description: 'Analyzing motion vectors and patterns', status: 'pending', icon: Activity, gradient: 'from-emerald-500 to-teal-500', glowColor: '16, 185, 129' }, // temporal
    { id: '5', name: 'Spatial Logic Verification', description: 'Checking scene coherence and object persistence', status: 'pending', icon: Workflow, gradient: 'from-violet-500 to-purple-500', glowColor: '139, 92, 246' }, // scene_logic
    { id: '6', name: 'Audio-Visual Sync Check', description: 'Verifying lip-sync and audio authenticity', status: 'pending', icon: Headphones, gradient: 'from-pink-500 to-rose-500', glowColor: '236, 72, 153' } // audio_visual
  ])
  
  // Icon component mapping for 3D icons
  const iconComponents = [
    FrequencyDomain3D,
    PixelStability3D,
    BiologicalInconsistency3D,
    OpticalFlow3D,
    SpatialLogic3D,
    AudioVisualSync3D,
  ]

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file)
    setOverallProgress(0)
    setOverallScore(0)
    setResults([])
    setMethods((prev) => prev.map((m, idx) => ({ ...m, status: idx === 0 ? 'analyzing' : 'pending' })))

    try {
      const formData = new FormData()
      formData.append('file', file)
      const uploadRes = await fetch('/upload', { method: 'POST', body: formData })
      if (!uploadRes.ok) throw new Error('Upload failed')
      const uploadData = await uploadRes.json()

      const analyzeRes = await fetch('/analyze/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: uploadData.filename, originalName: uploadData.original_name || file.name })
      })
      if (!analyzeRes.ok) throw new Error('Analysis start failed')
      const { jobId } = await analyzeRes.json()

      const startTime = Date.now()
      const poll = setInterval(async () => {
        try {
          const statusRes = await fetch(`/analyze/status/${jobId}`)
          if (!statusRes.ok) throw new Error('Status check failed')
          const job = await statusRes.json()
          setOverallProgress(job.progress || 0)
          const completed = job.completedStages || []
          const currentStage = job.stage
          // Map backend stages to our 6 UI steps in the order shown to users.
          // Backend emits: quality, watermark, forensics, face_analysis, artifact, face_dynamics, temporal, scene_logic, audio_visual, fusion
          const indexToStage: Record<number, string> = {
            0: 'forensics',
            1: 'artifact',
            2: 'face_dynamics',
            3: 'temporal',
            4: 'scene_logic',
            5: 'audio_visual'
          }
          setMethods((prev) =>
            prev.map((m, idx) => {
              const stageName = indexToStage[idx]
              const isComplete = stageName ? completed.includes(stageName) : false
              const isAnalyzing = stageName ? currentStage === stageName : false
              return { ...m, status: isComplete ? 'complete' : isAnalyzing ? 'analyzing' : 'pending' }
            })
          )
          if (job.status === 'completed' && job.result) {
            clearInterval(poll)
            const endTime = Date.now()
            setProcessingTime((endTime - startTime) / 1000)
            const backendResult = job.result
            const transformed: typeof results = backendResult.results || []
            setResults(transformed)
            setOverallScore(backendResult.overallScore || 50)
            setFeedbackId(backendResult.feedbackId || null)
          } else if (job.status === 'error' || job.status === 'failed') {
            clearInterval(poll)
            alert(`Analysis failed: ${job.error || 'Unknown error'}`)
          }
        } catch (e) {
          console.error(e)
        }
      }, 500)
    } catch (e) {
      console.error('Upload/analysis error', e)
      alert('Failed to start analysis.')
    }
  }

  return (
    <section ref={ref} id="detect" className="relative min-h-screen py-12 md:py-16 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
      {/* Animated background with flowing particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {/* Flowing gradient orbs */}
        <motion.div
          animate={{ x: [0, 100, 0], y: [0, 50, 0], scale: [1, 1.2, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-orange-500/30 via-pink-500/20 to-purple-500/30 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ x: [0, -80, 0], y: [0, -60, 0], scale: [1, 1.3, 1] }}
          transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
          className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-500/30 via-cyan-500/20 to-teal-500/30 rounded-full blur-3xl"
        />
        {/* Flowing particles */}
        {Array.from({ length: 15 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              width: Math.random() * 8 + 4,
              height: Math.random() * 8 + 4,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: `linear-gradient(135deg, rgba(249, 115, 22, 0.4), rgba(236, 72, 153, 0.4))`,
            }}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0.3, 0.8, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Hero Header - Mathical Style */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-8 md:mb-12"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="inline-flex items-center gap-2 rounded-full px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 text-sm uppercase tracking-[0.4em] text-white/80 mb-6"
          >
            <Sparkles className="w-4 h-4 text-orange-400" />
            Neural Forensics
          </motion.div>
          <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-white mb-6 tracking-tight leading-tight text-punched">
            Drop a video or image to start <br />
            <span className="bg-gradient-to-r from-orange-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">deepfake detection</span>
          </h2>
          <p className="text-lg sm:text-xl text-white/70 max-w-2xl mx-auto leading-relaxed font-medium">
            Get instant, detailed authenticity reports powered by advanced neural networks.
          </p>
        </motion.div>

        {/* Main Content Grid - Mathical Style */}
        <div className="grid lg:grid-cols-3 gap-6 md:gap-8 mb-12">
          {/* Upload Zone Card - Left Column */}
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -60 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="lg:col-span-1 relative group"
          >
            <div className="relative bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-xl curved-card-lg border border-white/20 shadow-2xl p-6 md:p-8 h-full">
              <UploadZone onFileSelect={handleFileSelect} isAnalyzing={overallProgress > 0 && overallProgress < 100} />
            </div>
          </motion.div>

          {/* Progress & Methods Card - Right Column (2 columns) */}
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 60 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="lg:col-span-2 relative"
          >
            <div className="relative bg-gradient-to-br from-slate-900/90 to-slate-800/90 backdrop-blur-xl curved-card-lg border border-white/10 shadow-2xl p-6 md:p-8">
              {/* Overall Progress - Mathical Style */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white text-punched">Overall Progress</h3>
                  <motion.span
                    key={overallProgress}
                    initial={{ scale: 1.2 }}
                    animate={{ scale: 1 }}
                    className="text-3xl font-black bg-gradient-to-r from-orange-400 via-pink-400 to-purple-400 bg-clip-text text-transparent"
                  >
                    {Math.round(overallProgress)}%
                  </motion.span>
                </div>
                {/* Pill-shaped progress bar */}
                <div className="relative h-6 bg-slate-800 rounded-full overflow-hidden shadow-inner border border-white/10">
                  <motion.div
                    className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 shadow-lg"
                    animate={{ width: `${overallProgress}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                    />
                  </motion.div>
                </div>
              </div>

              {/* Detection Methods - Mathical Style with 3D Icons */}
              <div className="space-y-4">
                <h4 className="text-lg font-bold text-white mb-4 text-punched">Detection Methods</h4>
                <div className="grid sm:grid-cols-2 gap-4">
                  {methods.map((method, index) => {
                    const Icon3D = iconComponents[index]
                    const isActive = method.status === 'analyzing'
                    const isComplete = method.status === 'complete'
                    const progress = isActive ? 50 + (index * 8) : isComplete ? 100 : 0
                    
                    return (
                      <motion.div
                        key={method.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                        transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                        whileHover={{ scale: 1.02, y: -4 }}
                        className={`relative overflow-hidden curved-card border-2 p-5 transition-all backdrop-blur-sm ${
                          isComplete
                            ? `bg-gradient-to-br ${method.gradient} bg-opacity-15 border-opacity-60`
                            : isActive
                            ? `bg-gradient-to-br ${method.gradient} bg-opacity-10 border-opacity-80`
                            : 'bg-slate-800/50 border-slate-700/50'
                        }`}
                      >
                        {/* Animated glow for active methods */}
                        {isActive && (
                          <motion.div
                            className={`absolute inset-0 bg-gradient-to-r ${method.gradient} opacity-20`}
                            animate={{ opacity: [0.2, 0.4, 0.2] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          />
                        )}
                        <div className="relative flex items-start gap-4">
                          {/* 3D Icon Container */}
                          <motion.div
                            className={`flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${method.gradient} shadow-xl border border-white/20 relative overflow-visible`}
                            animate={isActive ? { scale: [1, 1.05, 1] } : {}}
                            transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
                          >
                            {/* Always show the 3D icon */}
                            <div className="absolute inset-0 flex items-center justify-center">
                              <Icon3D className="w-8 h-8" isActive={isActive} />
                            </div>
                            {/* Status overlay */}
                            {isComplete && (
                              <div className="absolute -top-1 -right-1 bg-green-500 rounded-full p-1 shadow-lg z-20">
                                <CheckCircle2 className="w-4 h-4 text-white" />
                              </div>
                            )}
                            {isActive && (
                              <div className="absolute -top-1 -right-1 bg-blue-500 rounded-full p-1 shadow-lg z-20 animate-pulse">
                                <Loader2 className="w-4 h-4 text-white animate-spin" />
                              </div>
                            )}
                          </motion.div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2 mb-2">
                              <p className={`text-sm font-bold ${isActive || isComplete ? 'text-white text-punched' : 'text-white/70'}`}>
                                {method.name}
                              </p>
                              {(isActive || isComplete) && (
                                <motion.span
                                  className="text-xs font-semibold text-white/60 px-2 py-1 rounded-full bg-white/10"
                                  animate={isActive ? { opacity: [0.6, 1, 0.6] } : {}}
                                  transition={{ duration: 1.5, repeat: isActive ? Infinity : 0 }}
                                >
                                  {isComplete ? 'Complete' : 'Analyzing...'}
                                </motion.span>
                              )}
                            </div>
                            <p className="text-xs text-white/60 mb-3 font-medium">{method.description}</p>
                            {/* Pill-shaped progress indicator */}
                            {(isActive || isComplete) && (
                              <div className="relative h-2 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div
                                  className={`h-full rounded-full bg-gradient-to-r ${method.gradient}`}
                                  initial={{ width: '0%' }}
                                  animate={{ width: `${progress}%` }}
                                  transition={{ duration: 0.8, ease: 'easeOut' }}
                                />
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Results Display - New Analysis Layout */}
        {selectedFile && results.length > 0 && (
          <div className="mt-12 -mx-4 sm:-mx-6 lg:-mx-8">
            <AnalysisLayout
              fileName={selectedFile.name}
              overallScore={overallScore}
              processingTime={processingTime}
              framesAnalyzed={Math.round(processingTime * 30)} // Estimate frames based on time
              stages={methods.map((method, idx) => {
                // Map backend results to stages
                const result = results.find((r) => {
                  const methodMap: Record<number, string> = {
                    0: 'Frequency Domain Analysis',
                    1: 'Pixel Stability Analysis',
                    2: 'Biological Inconsistency Detection',
                    3: 'Optical Flow Analysis',
                    4: 'Spatial Logic Verification',
                    5: 'Audio-Visual Sync Check',
                  };
                  return r.method === methodMap[idx];
                });

                const iconMap: Record<number, 'pixel' | 'motion' | 'frequency' | 'audio' | 'face' | 'verdict'> = {
                  0: 'frequency',
                  1: 'pixel',
                  2: 'face',
                  3: 'motion',
                  4: 'pixel', // Spatial logic can use pixel icon
                  5: 'audio',
                };

                // Map status: 'pending' -> 'queued'
                const statusMap: Record<'pending' | 'analyzing' | 'complete', 'queued' | 'analyzing' | 'complete'> = {
                  pending: 'queued',
                  analyzing: 'analyzing',
                  complete: 'complete',
                };

                return {
                  id: method.id,
                  name: method.name,
                  description: method.description,
                  status: statusMap[method.status],
                  score: result?.score,
                  icon: iconMap[idx] || 'pixel',
                };
              })}
            />
          </div>
        )}

        {/* Info Cards - Mathical Style */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="grid sm:grid-cols-3 gap-4 md:gap-6 mt-12"
        >
          {[
            { icon: FileVideo, title: 'Supported Formats', desc: 'MP4, MOV, AVI, WebM, JPG, PNG', gradient: 'from-blue-500 to-cyan-500' },
            { icon: Timer, title: 'Processing Time', desc: '~ 8-12s typical', gradient: 'from-purple-500 to-pink-500' },
            { icon: Lock, title: 'Privacy First', desc: 'Files never shared', gradient: 'from-emerald-500 to-teal-500' }
          ].map((item, index) => {
            const Icon = item.icon
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                transition={{ duration: 0.5, delay: 0.7 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -4 }}
                className={`relative overflow-hidden curved-card bg-gradient-to-br ${item.gradient} bg-opacity-15 border-2 border-white/20 p-6 backdrop-blur-sm`}
              >
                <div className={`flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${item.gradient} mb-4 shadow-xl border border-white/20`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <h4 className="text-lg font-bold text-white mb-2 text-punched">{item.title}</h4>
                <p className="text-sm text-white/70 font-medium">{item.desc}</p>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}

function AIDetectionDemo() {
  const [progress, setProgress] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 0
        return prev + 1
      })
    }, 90)
    return () => clearInterval(interval)
  }, [])

  const detectionMethods = [
    { name: 'Pixel Stability', icon: ScanLine, badge: 'Temporal', desc: 'Frame parity and texture drift' },
    { name: 'Optical Flow', icon: Orbit, badge: 'Motion', desc: 'Vector coherence and flicker' },
    { name: 'Spatial Logic', icon: Box, badge: 'Scene', desc: 'Object persistence and physics' },
    { name: 'Frequency Analysis', icon: Signal, badge: 'Spectral', desc: 'GAN signatures and noise' },
    { name: 'Audio Sync', icon: Headphones, badge: 'A/V', desc: 'Lip sync and rPPG alignment' },
    { name: 'Face Analysis', icon: ScanFace, badge: 'Forensic', desc: 'Landmarks and biometrics' }
  ] as const

  const perStep = 100 / detectionMethods.length

  return (
    <div className="relative">
      <div className="absolute -inset-6 rounded-[32px] bg-gradient-to-r from-orange-400/20 via-pink-500/15 to-purple-500/20 blur-3xl" />
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="relative overflow-hidden curved-card-lg border border-white/10 bg-gradient-to-br from-white/95 via-white/85 to-white/70 dark:from-slate-900/90 dark:via-slate-950/85 dark:to-slate-900/75 p-8 shadow-[0_35px_120px_rgba(15,23,42,0.45)] backdrop-blur-xl dark:border-white/5"
      >
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.15]"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgba(15,23,42,0.25) 1px, transparent 0), linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 60%)',
            backgroundSize: '40px 40px, 200% 200%'
          }}
        />
        <div className="relative space-y-8">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full bg-slate-900/5 dark:bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-slate-600 dark:text-white/70">
                Live analysis
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-pink-500 shadow-lg shadow-orange-500/45">
                  <FileVideo className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">File in review</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white text-punched" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                    demo_video.mp4
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Media authenticity sweep</p>
                </div>
              </div>
              <motion.span
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-2 rounded-full bg-white/60 px-3 py-1 text-xs font-semibold text-slate-700 shadow-sm dark:bg-white/10 dark:text-white/70"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-pink-400 animate-ping" />
                Sero core is active
              </motion.span>
            </div>
            <div className="text-right">
              <p className="text-xs uppercase tracking-[0.25em] text-gray-500 dark:text-gray-400">Progress</p>
              <motion.p
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="text-5xl font-black text-gray-900 dark:text-white"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {progress}%
              </motion.p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Signal quality {progress > 80 ? 'stable' : 'sampling'}</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="relative">
              <div className="h-3 rounded-full bg-white/70 shadow-inner dark:bg-slate-900/60" />
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-white/40 to-transparent blur-xl opacity-70 pointer-events-none" />
              <motion.div
                className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 shadow-[0_0_30px_rgba(236,72,153,0.45)]"
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              />
              <motion.div
                className="absolute top-1/2 -translate-y-1/2 rounded-full bg-white shadow-lg shadow-pink-500/40 dark:bg-slate-950 flex items-center justify-center"
                style={{ height: '18px', width: '18px' }}
                animate={{ x: `calc(${progress}% - 9px)` }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              >
                <span className="h-2 w-2 rounded-full bg-gradient-to-r from-orange-500 to-pink-400 animate-pulse" />
              </motion.div>
            </div>
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.25em] text-gray-500 dark:text-gray-400">
              <span>Signal correlation</span>
              <span>{progress}% complete</span>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {detectionMethods.map((method, index) => {
              const Icon = method.icon
              const raw = progress - index * perStep
              const pct = Math.max(0, Math.min((raw / perStep) * 100, 100))
              const complete = pct >= 100
              return (
                <motion.div
                  key={method.name}
                  whileHover={{ scale: 1.015, translateY: -4 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 25 }}
                  className="relative overflow-hidden curved-card border border-white/30 bg-white/80 p-5 shadow-lg shadow-slate-900/10 dark:border-white/10 dark:bg-slate-900/60 dark:shadow-[0_15px_40px_rgba(0,0,0,0.55)] backdrop-blur"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900/70 border border-slate-800/80 text-white shadow-xl shadow-black/20 dark:bg-white/10 dark:border-white/20">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white text-punched">{method.name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-300 font-medium">{method.desc}</p>
                    </div>
                    <span className="ml-auto rounded-full bg-slate-900/5 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-slate-500 dark:bg-white/10 dark:text-white/70">
                      {method.badge}
                    </span>
                  </div>
                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-200/80 dark:bg-slate-800">
                    <motion.div
                      className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-emerald-500 to-emerald-600"
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.4 }}
                    />
                  </div>
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>{complete ? 'Complete' : pct > 0 ? 'Analyzing' : 'Queued'}</span>
                    <span>{Math.round(pct)}%</span>
                  </div>
                  {complete && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="absolute top-4 right-4 text-emerald-400"
                    >
                      <CheckCircle2 className="h-4 w-4" />
                    </motion.div>
                  )}
                </motion.div>
              )
            })}
          </div>

          <motion.div
            whileHover={{ scale: 1.01 }}
            className="flex flex-wrap items-center justify-between gap-4 curved-card border border-blue-200/70 bg-gradient-to-r from-blue-50/80 to-cyan-50/70 p-5 shadow-inner dark:border-blue-900/50 dark:bg-gradient-to-r dark:from-blue-900/40 dark:to-cyan-900/30"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 text-white shadow-xl shadow-blue-500/40">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <p className="text-base font-semibold text-gray-900 dark:text-white text-punched">Authenticity score</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">Synth + watermark fusion underway</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-4xl font-black text-blue-600 dark:text-cyan-300" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                {Math.min(Math.round(progress * 0.97), 99)}%
              </p>
              <p className="text-xs uppercase tracking-[0.3em] text-blue-500/70 dark:text-cyan-200">Integrity</p>
            </div>
          </motion.div>
          <div className="flex items-center gap-2 pt-2 text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Sero is analyzing 6 independent signals in real time
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function StartFreeButton({ onClick }: { onClick: () => void }) {
  const letters = useMemo(() => 'StartFree'.split(''), [])
  const scatter = useMemo(
    () =>
      letters.map(() => ({
        x: (Math.random() - 0.5) * 180,
        y: (Math.random() - 0.5) * 120,
        rotate: (Math.random() - 0.5) * 50
      })),
    [letters]
  )
  const finalPositions = useMemo(() => {
    const baseSpacing = 36
    return letters.map((_, index) => {
      const offset = index >= 5 ? 40 : 0
      const centerOffset = ((letters.length - 1) * baseSpacing + 40) / 2
      return {
        x: index * baseSpacing + offset - centerOffset,
        y: 0
      }
    })
  }, [letters])
  const [hovered, setHovered] = useState(false)
  return (
    <div className="px-6 py-24">
      <div className="max-w-6xl mx-auto">
        <motion.button
          type="button"
          onClick={onClick}
          onHoverStart={() => setHovered(true)}
          onHoverEnd={() => setHovered(false)}
          className="relative w-full min-h-[260px] rounded-[56px] border border-white/30 dark:border-white/10 bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 text-white py-16 md:py-24 overflow-hidden shadow-[0_40px_120px_rgba(212,119,14,0.35)]"
        >
          <motion.div
            aria-hidden
            animate={{ opacity: hovered ? 0.9 : 0.4 }}
            className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_65%)]"
          />
          <div className="relative h-36 md:h-44 flex items-center justify-center">
            {letters.map((char, index) => (
              <motion.span
                key={`${char}-${index}`}
                className="absolute text-5xl md:text-7xl font-black tracking-[0.2em] drop-shadow-[0_10px_30px_rgba(0,0,0,0.25)]"
                animate={{
                  x: hovered ? finalPositions[index].x : scatter[index].x,
                  y: hovered ? finalPositions[index].y : scatter[index].y,
                  rotate: hovered ? 0 : scatter[index].rotate,
                  scale: hovered ? 1 : 0.95
                }}
                transition={{ type: 'spring', stiffness: 160, damping: 15 }}
              >
                {char}
              </motion.span>
            ))}
          </div>
          <div className="relative mt-8 text-center text-sm uppercase tracking-[0.6em] text-white/70">
            Start free
          </div>
        </motion.button>
      </div>
    </div>
  )
}

// Visualization components for feature cards
function PixelAnalysisViz({ gradient }: { gradient: string }) {
  return (
    <div className="w-full h-full relative flex items-center justify-center p-2">
      {/* Side-by-side comparison */}
      <div className="flex gap-1 w-full h-full">
        {/* Original side */}
        <div className="flex-1 relative rounded-lg overflow-hidden bg-slate-800/50">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <div className="w-8 h-8 rounded-full bg-white/40" />
            </div>
          </div>
          <div className="absolute top-1 left-1 text-[6px] font-bold text-white/80">ORIGINAL</div>
        </div>
        
        {/* Deepfake side with grid overlay */}
        <div className="flex-1 relative rounded-lg overflow-hidden bg-slate-800/50">
          <div className="absolute inset-0 bg-gradient-to-br from-orange-600/30 to-red-600/30 rounded-lg" />
          {/* Grid pattern overlay */}
          <svg className="absolute inset-0 w-full h-full opacity-40" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="grid-pixel" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgb(34, 197, 94)" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#grid-pixel)" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center relative">
              <div className="w-8 h-8 rounded-full bg-white/40" />
              {/* Facial landmarks overlay */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="1.5" fill="white" opacity="0.9" />
                <circle cx="65" cy="40" r="1.5" fill="white" opacity="0.9" />
                <circle cx="50" cy="55" r="1.5" fill="white" opacity="0.9" />
                <path d="M 40 65 Q 50 70 60 65" stroke="white" strokeWidth="1" fill="none" opacity="0.7" />
              </svg>
            </div>
          </div>
          <div className="absolute top-1 left-1 text-[6px] font-bold text-green-400">DEEPFAKE</div>
        </div>
      </div>
    </div>
  )
}

function NeuralNetworkViz({ gradient }: { gradient: string }) {
  return (
    <div className="w-full h-full relative flex items-center justify-center p-3">
      {/* Face with landmarks and 3D box */}
      <div className="relative w-20 h-20">
        {/* Face circle */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-white/10" />
        </div>
        
        {/* Facial landmarks (red dots) */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* Eye landmarks */}
          <circle cx="35" cy="40" r="2" fill="#ef4444" opacity="0.9" />
          <circle cx="65" cy="40" r="2" fill="#ef4444" opacity="0.9" />
          {/* Nose landmarks */}
          <circle cx="50" cy="50" r="1.5" fill="#ef4444" opacity="0.9" />
          <circle cx="45" cy="55" r="1.5" fill="#ef4444" opacity="0.9" />
          <circle cx="55" cy="55" r="1.5" fill="#ef4444" opacity="0.9" />
          {/* Mouth landmarks */}
          <circle cx="40" cy="65" r="1.5" fill="#ef4444" opacity="0.9" />
          <circle cx="50" cy="68" r="1.5" fill="#ef4444" opacity="0.9" />
          <circle cx="60" cy="65" r="1.5" fill="#ef4444" opacity="0.9" />
          {/* Additional face points */}
          <circle cx="30" cy="30" r="1" fill="#ef4444" opacity="0.7" />
          <circle cx="70" cy="30" r="1" fill="#ef4444" opacity="0.7" />
          <circle cx="25" cy="50" r="1" fill="#ef4444" opacity="0.7" />
          <circle cx="75" cy="50" r="1" fill="#ef4444" opacity="0.7" />
        </svg>
        
        {/* 3D bounding box (wireframe) */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" style={{ transform: 'rotateX(15deg) rotateY(-10deg)' }}>
          <g stroke="#3b82f6" strokeWidth="1.5" fill="none" opacity="0.8">
            {/* Front face */}
            <rect x="20" y="25" width="60" height="50" />
            {/* Back face (offset) */}
            <rect x="25" y="30" width="60" height="50" />
            {/* Connecting lines */}
            <line x1="20" y1="25" x2="25" y2="30" />
            <line x1="80" y1="25" x2="85" y2="30" />
            <line x1="20" y1="75" x2="25" y2="80" />
            <line x1="80" y1="75" x2="85" y2="80" />
          </g>
        </svg>
        
        {/* Eye tracking lines (green) */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          <line x1="35" y1="40" x2="35" y2="38" stroke="#22c55e" strokeWidth="2" />
          <line x1="65" y1="40" x2="65" y2="38" stroke="#22c55e" strokeWidth="2" />
        </svg>
      </div>
    </div>
  )
}

function RealTimeViz({ gradient }: { gradient: string }) {
  return (
    <div className="w-full h-full relative flex items-center justify-center p-2">
      {/* Video frame with analysis overlays */}
      <div className="w-full h-full relative rounded-lg overflow-hidden bg-slate-800/50">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg" />
        
        {/* Face region */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center relative">
            <div className="w-12 h-12 rounded-full bg-white/20" />
          </div>
        </div>
        
        {/* Analysis overlays */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* Scanning lines */}
          <motion.g
            initial={{ y: 0 }}
            animate={{ y: [0, 70, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <line x1="0" y1="30" x2="100" y2="30" stroke="#3b82f6" strokeWidth="1" opacity="0.6" />
          </motion.g>
          <motion.g
            initial={{ y: 0 }}
            animate={{ y: [0, 50, 0] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "linear", delay: 0.5 }}
          >
            <line x1="0" y1="50" x2="100" y2="50" stroke="#3b82f6" strokeWidth="1" opacity="0.4" />
          </motion.g>
          
          {/* Corner detection markers */}
          <circle cx="20" cy="20" r="2" fill="#3b82f6" opacity="0.8">
            <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1.5s" repeatCount="indefinite" />
          </circle>
          <circle cx="80" cy="20" r="2" fill="#3b82f6" opacity="0.8">
            <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1.5s" repeatCount="indefinite" begin="0.3s" />
          </circle>
          <circle cx="20" cy="80" r="2" fill="#3b82f6" opacity="0.8">
            <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1.5s" repeatCount="indefinite" begin="0.6s" />
          </circle>
          <circle cx="80" cy="80" r="2" fill="#3b82f6" opacity="0.8">
            <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1.5s" repeatCount="indefinite" begin="0.9s" />
          </circle>
          
          {/* Processing indicator */}
          <rect x="45" y="85" width="10" height="3" fill="#22c55e" opacity="0.8">
            <animate attributeName="width" values="10;30;10" dur="1.5s" repeatCount="indefinite" />
          </rect>
        </svg>
        
        {/* Status text */}
        <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[6px] font-bold text-green-400">
          ANALYZING...
        </div>
      </div>
    </div>
  )
}

function HowItWorksSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-100px' })
  return (
    <section ref={ref} className="py-24 bg-white dark:bg-slate-950 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Circuit-like mesh grid */}
        <div className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]" style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, rgb(249 115 22) 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
        
        {/* Floating orbs */}
        <motion.div
          animate={{ y: [0, -20, 0], x: [0, 10, 0] }}
          transition={{ duration: 6, repeat: Infinity }}
          className="absolute top-20 left-10 w-32 h-32 bg-orange-400/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ y: [0, 20, 0], x: [0, -10, 0] }}
          transition={{ duration: 7, repeat: Infinity }}
          className="absolute bottom-20 right-10 w-40 h-40 bg-pink-400/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ y: [0, -15, 0], x: [0, 15, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-1/2 right-1/4 w-36 h-36 bg-purple-400/10 rounded-full blur-3xl"
        />
      </div>
      
      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.6 }}
            className="text-5xl lg:text-7xl text-gray-900 dark:text-white mb-6 tracking-tight font-black"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
          >
            How <span className="bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 bg-clip-text text-transparent">Sero Works</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto"
          >
            Three powerful detection methods working together to identify deepfakes
          </motion.p>
        </div>
        
        {/* Connection lines between cards */}
        <div className="hidden md:block absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-5xl h-px pointer-events-none">
          <svg className="w-full h-full" style={{ position: 'absolute', top: 0, left: 0 }}>
            <motion.line
              x1="20%" y1="0" x2="50%" y2="0"
              stroke="url(#gradient1)"
              strokeWidth="2"
              strokeDasharray="5,5"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={isInView ? { pathLength: 1, opacity: 0.3 } : { pathLength: 0, opacity: 0 }}
              transition={{ duration: 1.5, delay: 0.5 }}
            />
            <motion.line
              x1="50%" y1="0" x2="80%" y2="0"
              stroke="url(#gradient2)"
              strokeWidth="2"
              strokeDasharray="5,5"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={isInView ? { pathLength: 1, opacity: 0.3 } : { pathLength: 0, opacity: 0 }}
              transition={{ duration: 1.5, delay: 0.7 }}
            />
            <defs>
              <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(249, 115, 22)" />
                <stop offset="100%" stopColor="rgb(168, 85, 247)" />
              </linearGradient>
              <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(168, 85, 247)" />
                <stop offset="100%" stopColor="rgb(59, 130, 246)" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 relative">
          {[
            {
              title: 'Pixel Analysis',
              badge: 'Forensic',
              badgeBg: 'bg-orange-100 dark:bg-orange-950/50',
              badgeText: 'text-orange-700 dark:text-orange-300',
              desc: 'Advanced algorithms examine pixel-level inconsistencies and artifacts that indicate synthetic content generation.',
              gradient: 'from-orange-400 to-red-500',
              glowColor: '249, 115, 22',
              bg: 'bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/20 dark:to-red-950/20',
              border: 'border-orange-300 dark:border-orange-700',
              direction: 'x',
              start: -60,
              vizType: 'pixel'
            },
            {
              title: 'Neural Networks',
              badge: 'ML Engine',
              badgeBg: 'bg-purple-100 dark:bg-purple-950/50',
              badgeText: 'text-purple-700 dark:text-purple-300',
              desc: 'Deep learning models trained on millions of samples to detect even the most sophisticated deepfake techniques.',
              gradient: 'from-purple-500 to-pink-500',
              glowColor: '168, 85, 247',
              bg: 'bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20',
              border: 'border-purple-300 dark:border-purple-700',
              direction: 'y',
              start: 60,
              vizType: 'neural'
            },
            {
              title: 'Real-time Processing',
              badge: 'Speed',
              badgeBg: 'bg-blue-100 dark:bg-blue-950/50',
              badgeText: 'text-blue-700 dark:text-blue-300',
              desc: 'Lightning-fast analysis delivers results in under 5 seconds, perfect for high-volume workflows.',
              gradient: 'from-sky-400 to-blue-600',
              glowColor: '59, 130, 246',
              bg: 'bg-gradient-to-br from-sky-50 to-blue-50 dark:from-sky-950/20 dark:to-blue-950/20',
              border: 'border-blue-300 dark:border-blue-700',
              direction: 'x',
              start: 60,
              vizType: 'realtime'
            }
          ].map((item, index) => {
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, [item.direction as 'x' | 'y']: item.start }}
                animate={isInView ? { opacity: 1, [item.direction as 'x' | 'y']: 0 } : { opacity: 0, [item.direction as 'x' | 'y']: item.start }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                whileHover={{ scale: 1.02, y: -8 }}
                className={`${item.bg} p-8 rounded-3xl border-2 ${item.border} relative group overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300`}
              >
                {/* Gradient overlay on hover */}
                <div className={`absolute inset-0 bg-gradient-to-br ${item.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500 rounded-3xl`} />
                
                {/* Glow effect */}
                <div
                  className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    boxShadow: `0 0 40px rgba(${item.glowColor}, 0.4)`
                  }}
                />
                
                {/* Noise texture */}
                <div className="absolute inset-0 opacity-[0.02] dark:opacity-[0.03] mix-blend-overlay pointer-events-none" style={{
                  backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")'
                }} />
                
                {/* Diagonal accent */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/20 to-transparent dark:from-white/5 rounded-bl-[100px] opacity-50" />
                
                <div className="relative z-10">
                  {/* Custom visualization instead of icon */}
                  <motion.div
                    className={`w-full h-32 rounded-2xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-6 shadow-2xl relative overflow-hidden`}
                    whileHover={{ scale: 1.05 }}
                    animate={{ y: [0, -4, 0] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  >
                    {/* Visualization content */}
                    {item.vizType === 'pixel' && <PixelAnalysisViz gradient={item.gradient} />}
                    {item.vizType === 'neural' && <NeuralNetworkViz gradient={item.gradient} />}
                    {item.vizType === 'realtime' && <RealTimeViz gradient={item.gradient} />}
                    {/* Glow effect */}
                    <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${item.gradient} blur-xl opacity-30`} />
                  </motion.div>
                  
                  {/* Title with badge */}
                  <div className="flex items-center gap-3 mb-4">
                    <h3 className={`text-2xl font-bold bg-gradient-to-r ${item.gradient} bg-clip-text text-transparent`}>
                      {item.title}
                    </h3>
                    <span className={`text-xs font-semibold ${item.badgeBg} ${item.badgeText} px-2.5 py-1 rounded-full`}>
                      {item.badge}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed text-sm">
                    {item.desc}
                  </p>
                </div>
                
                {/* Bottom accent */}
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-white/20 to-transparent dark:from-white/5 rounded-tr-[100px] opacity-50" />
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

function DeveloperSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-100px' })
  return (
    <section ref={ref} className="relative py-28 bg-gradient-to-b from-white via-gray-50 to-white dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 overflow-hidden">
      <div className="absolute inset-x-0 top-12 h-72 bg-gradient-to-r from-orange-200/30 via-pink-200/30 to-purple-200/30 dark:from-orange-500/10 dark:via-pink-500/10 dark:to-purple-500/10 blur-3xl" aria-hidden />
      <div className="max-w-7xl mx-auto px-6 relative z-10 grid lg:grid-cols-[1.1fr,_0.9fr] gap-16 items-center">
        <motion.div initial={{ opacity: 0, x: -60 }} animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -60 }} transition={{ duration: 0.6 }}>
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-2 bg-black/5 dark:bg-white/10 text-sm uppercase tracking-[0.4em] text-gray-700 dark:text-gray-300 mb-6">
            API-FIRST
          </div>
          <h2 className="text-5xl sm:text-6xl lg:text-7xl font-black text-gray-900 dark:text-white leading-tight mb-6">
            Built for <span className="bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 bg-clip-text text-transparent">developers</span> who ship real defences.
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-10 leading-relaxed">
            Trigger scans from CI/CD, hydrate evidence trails, and feed SOC dashboards with exact tensor receipts. One API key. No guesswork.
          </p>
          <div className="space-y-4 mb-10">
            {[
              { title: 'SDKs + REST', detail: 'Node · Python · Go-ready', Icon: PixelGridIcon },
              { title: 'Realtime ingest', detail: 'Webhooks and stream hooks', Icon: RealtimeIcon },
              { title: 'Zero trust', detail: 'SOC automation baked in', Icon: ShieldGridIcon }
            ].map((item, index) => {
              const { Icon } = item
              return (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, x: -40 }}
                  animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -40 }}
                  transition={{ duration: 0.45, delay: 0.15 + index * 0.1 }}
                  className="flex items-center gap-4 rounded-2xl border border-white/60 dark:border-white/10 bg-white/90 dark:bg-white/5 px-5 py-4 shadow-xl shadow-black/5 backdrop-blur"
                >
                  <div className="relative w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500 via-pink-500 to-purple-500 flex items-center justify-center shadow-2xl">
                    <div className="absolute inset-0 rounded-2xl bg-white/15 blur-lg" aria-hidden />
                    <Icon />
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">{item.title}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{item.detail}</p>
                  </div>
                </motion.div>
              )
            })}
          </div>
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            whileHover={{ scale: 1.05, y: -4 }}
            whileTap={{ scale: 0.97 }}
            className="inline-flex items-center gap-3 px-8 py-3 bg-gradient-to-r from-black via-slate-900 to-black text-white rounded-full shadow-[0_20px_60px_rgba(15,23,42,0.35)]"
          >
            <Book className="w-5 h-5" />
            <span>View API docs</span>
          </motion.button>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 80 }}
          animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 80 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="relative rounded-[32px] bg-slate-950 border border-white/10 shadow-[0_35px_80px_rgba(15,23,42,0.65)] p-8 overflow-hidden"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_transparent_55%)]" aria-hidden />
          <div className="relative flex items-center gap-2 mb-6">
            <span className="w-3 h-3 rounded-full bg-rose-400" />
            <span className="w-3 h-3 rounded-full bg-amber-400" />
            <span className="w-3 h-3 rounded-full bg-emerald-400" />
            <span className="ml-auto text-xs uppercase tracking-[0.4em] text-white/40">LIVE</span>
          </div>
          <div className="relative">
            <pre className="text-sm text-slate-200 font-mono leading-relaxed">
{`import { SeroAI } from 'sero-sdk';

const client = new SeroAI({
  apiKey: process.env.SERO_API_KEY,
  region: 'auto'
});

const report = await client.detect({
  file: 'press.wav',
  type: 'video',
  explain: true
});

console.log(report.isDeepfake);
// false
console.log(report.confidence);
// 0.98
console.log(report.chainOfEvidence);
// ['watermark','sceneLogic','tensorForensics']`}
            </pre>
            <motion.div
              aria-hidden
              animate={{ opacity: [0.3, 0.9, 0.3] }}
              transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent"
            />
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function WhySeroSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-100px' })
  
  // Scroll progress for connecting animation
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  })
  
  // Transform scroll progress to control connection animation
  const connectionProgress = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 1])
  const scatterProgress = useTransform(scrollYProgress, [0, 0.3], [1, 0])
  
  const stats = [
    { value: '90%+', label: 'Precision (high-signal)', desc: 'On strong evidence cases', color: 'orange' },
    { value: '8–12s', label: 'Detection Speed', desc: 'Typical end-to-end time', color: 'purple' },
    { value: '3K+', label: 'Videos Trained', desc: 'Supervised fusion model', color: 'blue' },
    { value: 'Weekdays', label: 'Support', desc: 'Email-based assistance', color: 'green' }
  ] as const
  
  // Split heading into words for scattering
  const headingWords = ["Why", "Choose", "Sero"]
  const subtitleWords = "Industry-leading performance backed by cutting-edge AI research".split(" ")
  
  return (
    <section ref={ref} className="py-20 sm:py-24 lg:py-32 relative overflow-hidden bg-gradient-to-br from-gray-50 via-orange-50/30 to-rose-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-orange-200/20 dark:bg-orange-900/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-rose-200/20 dark:bg-rose-900/10 rounded-full blur-3xl" />
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-12 sm:mb-16 lg:mb-20">
          {/* Scattered heading that connects on scroll */}
          <motion.h2
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl text-gray-900 dark:text-white mb-4 sm:mb-6 tracking-tight font-black flex flex-wrap justify-center items-center gap-2 sm:gap-3 md:gap-4"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
          >
            {headingWords.map((word, index) => {
              const isSero = word === "Sero"
              // Calculate scattered positions (random but consistent)
              const scatterX = (index % 2 === 0 ? 1 : -1) * (50 + index * 30)
              const scatterY = (index % 3 === 0 ? 1 : -1) * (40 + index * 25)
              const scatterRotate = (index % 2 === 0 ? 1 : -1) * (15 + index * 10)
              
              return (
                <motion.span
                  key={word}
                  style={{
                    x: useTransform(scatterProgress, [0, 1], [0, scatterX]),
                    y: useTransform(scatterProgress, [0, 1], [0, scatterY]),
                    rotate: useTransform(scatterProgress, [0, 1], [0, scatterRotate]),
                    opacity: useTransform(connectionProgress, [0, 0.5, 1], [0.3, 0.8, 1]),
                    scale: useTransform(connectionProgress, [0, 0.5, 1], [0.8, 1.1, 1]),
                  }}
                  className={isSero ? "sero-brand bg-gradient-to-r from-orange-600 via-rose-600 to-pink-600 bg-clip-text text-transparent" : ""}
                >
                  {word}
                </motion.span>
              )
            })}
          </motion.h2>
          
          {/* Scattered subtitle */}
          <motion.p
            className="text-lg sm:text-xl md:text-2xl text-gray-700 dark:text-gray-300 max-w-3xl mx-auto font-semibold flex flex-wrap justify-center items-center gap-1 sm:gap-2"
          >
            {subtitleWords.map((word, index) => {
              const scatterX = (index % 3 === 0 ? 1 : -1) * (20 + (index % 5) * 15)
              const scatterY = (index % 2 === 0 ? 1 : -1) * (15 + (index % 4) * 10)
              
              return (
                <motion.span
                  key={`${word}-${index}`}
                  style={{
                    x: useTransform(scatterProgress, [0, 1], [0, scatterX]),
                    y: useTransform(scatterProgress, [0, 1], [0, scatterY]),
                    opacity: useTransform(connectionProgress, [0, 0.6, 1], [0.2, 0.7, 1]),
                    scale: useTransform(connectionProgress, [0, 0.6, 1], [0.7, 1.05, 1]),
                  }}
                  className="inline-block"
                >
                  {word}
                </motion.span>
              )
            })}
          </motion.p>
        </div>
        
        {/* Stats cards that scatter and connect */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8 lg:gap-10">
          {stats.map((stat, index) => {
            // Calculate scattered positions for cards
            const cardScatterX = (index % 2 === 0 ? 1 : -1) * (100 + index * 50)
            const cardScatterY = (index % 3 === 0 ? 1 : -1) * (80 + index * 40)
            const cardRotate = (index % 2 === 0 ? 1 : -1) * (20 + index * 15)
            
            return (
              <motion.div
                key={stat.label}
                style={{
                  x: useTransform(scatterProgress, [0, 1], [0, cardScatterX]),
                  y: useTransform(scatterProgress, [0, 1], [0, cardScatterY]),
                  rotate: useTransform(scatterProgress, [0, 1], [0, cardRotate]),
                  opacity: useTransform(connectionProgress, [0, 0.4, 1], [0, 0.6, 1]),
                  scale: useTransform(connectionProgress, [0, 0.5, 1], [0.5, 1.1, 1]),
                }}
                whileHover={{ y: -8, scale: 1.02, rotate: 0 }}
                className={`relative group ${
                  stat.color === 'orange'
                    ? 'bg-gradient-to-br from-orange-100 to-orange-50 dark:from-orange-950/40 dark:to-orange-900/20 border-2 border-orange-300 dark:border-orange-800/50 shadow-lg shadow-orange-200/50 dark:shadow-orange-900/20'
                    : stat.color === 'purple'
                    ? 'bg-gradient-to-br from-purple-100 to-purple-50 dark:from-purple-950/40 dark:to-purple-900/20 border-2 border-purple-300 dark:border-purple-800/50 shadow-lg shadow-purple-200/50 dark:shadow-purple-900/20'
                    : stat.color === 'blue'
                    ? 'bg-gradient-to-br from-blue-100 to-blue-50 dark:from-blue-950/40 dark:to-blue-900/20 border-2 border-blue-300 dark:border-blue-800/50 shadow-lg shadow-blue-200/50 dark:shadow-blue-900/20'
                    : 'bg-gradient-to-br from-green-100 to-green-50 dark:from-green-950/40 dark:to-green-900/20 border-2 border-green-300 dark:border-green-800/50 shadow-lg shadow-green-200/50 dark:shadow-green-900/20'
                } p-6 sm:p-8 lg:p-10 rounded-3xl text-center transition-all duration-300 hover:shadow-2xl`}
              >
                {/* Glow effect on hover */}
                <div className={`absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
                  stat.color === 'orange'
                    ? 'bg-gradient-to-br from-orange-400/20 to-transparent'
                    : stat.color === 'purple'
                    ? 'bg-gradient-to-br from-purple-400/20 to-transparent'
                    : stat.color === 'blue'
                    ? 'bg-gradient-to-br from-blue-400/20 to-transparent'
                    : 'bg-gradient-to-br from-green-400/20 to-transparent'
                }`} />
                
                <div
                  className={`relative text-4xl sm:text-5xl md:text-6xl lg:text-7xl mb-4 sm:mb-6 font-black ${
                    stat.color === 'orange'
                      ? 'bg-gradient-to-r from-orange-600 to-orange-500 dark:from-orange-400 dark:to-orange-300 bg-clip-text text-transparent'
                      : stat.color === 'purple'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-500 dark:from-purple-400 dark:to-purple-300 bg-clip-text text-transparent'
                      : stat.color === 'blue'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-500 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent'
                      : 'bg-gradient-to-r from-green-600 to-green-500 dark:from-green-400 dark:to-green-300 bg-clip-text text-transparent'
                  }`}
                  dangerouslySetInnerHTML={{ __html: stat.value }}
                />
                <h3 className="text-base sm:text-lg md:text-xl lg:text-2xl text-gray-900 dark:text-white mb-2 sm:mb-3 font-black tracking-tight">
                  {stat.label}
                </h3>
                <p className="text-sm sm:text-base md:text-lg text-gray-700 dark:text-gray-300 font-medium">
                  {stat.desc}
                </p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

function GlobalSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-100px' })
  return (
    <section ref={ref} className="py-24 bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ y: [0, -20, 0], x: [0, 10, 0] }}
          transition={{ duration: 6, repeat: Infinity }}
          className="absolute top-20 left-10 w-20 h-20 bg-orange-400/10 rounded-full blur-xl"
        />
        <motion.div
          animate={{ y: [0, 20, 0], x: [0, -10, 0] }}
          transition={{ duration: 7, repeat: Infinity }}
          className="absolute bottom-20 right-10 w-32 h-32 bg-pink-400/10 rounded-full blur-xl"
        />
        <motion.div
          animate={{ y: [0, -15, 0], x: [0, 15, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-1/2 right-1/4 w-24 h-24 bg-purple-400/10 rounded-full blur-xl"
        />
      </div>
      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div initial={{ opacity: 0, scale: 0.8, x: -60 }} animate={isInView ? { opacity: 1, scale: 1, x: 0 } : { opacity: 0, scale: 0.8, x: -60 }} transition={{ duration: 0.8 }} className="flex justify-center w-full">
            <SimpleGlobe className="h-[420px] w-full md:h-[520px] rounded-3xl overflow-hidden" />
          </motion.div>
          <motion.div initial={{ opacity: 0, x: 60 }} animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 60 }} transition={{ duration: 0.6 }}>
            <h2
              className="text-5xl lg:text-7xl text-white mb-6 tracking-tight"
              style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
            >
              Trusted <span className="bg-gradient-to-r from-orange-400 to-pink-400 bg-clip-text text-transparent">Globally</span>
            </h2>
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              Piloted with teams across 15+ countries. Designed for media teams, researchers, and developers who need practical, explainable detection.
            </p>
            <div className="grid grid-cols-2 gap-6">
              {[
                { number: '15+', label: 'Countries' },
                { number: '20+', label: 'Teams Using' },
                { number: '99.0%', label: 'Uptime (dev)' },
                { number: '10K+', label: 'Total Scans' }
              ].map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
                  transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                  className="bg-white/5 p-6 rounded-2xl border border-white/10"
                >
                  <div className="text-3xl text-orange-400 mb-2" style={{ fontWeight: 900 }}>
                    {stat.number}
                  </div>
                  <div className="text-gray-300">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function DashboardSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-120px' })
  const [detectionsToday, setDetectionsToday] = useState(0)

  useEffect(() => {
    if (!isInView) return
    const controls = animate(0, 248, {
      duration: 1.4,
      ease: 'easeOut',
      onUpdate: (value) => setDetectionsToday(Math.round(value))
    })
    return () => controls.stop()
  }, [isInView])

  const containerVariants = {
    hidden: { opacity: 0, y: 24 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { staggerChildren: 0.08, delayChildren: 0.1 }
    }
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 24, scale: 0.96 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { type: 'spring', stiffness: 220, damping: 24 }
    }
  }

  const aiScore = 0.82
  const gaugeRadius = 42
  const gaugeCircumference = 2 * Math.PI * gaugeRadius

  const statCards = [
    {
      title: 'Detections today',
      value: `${detectionsToday}`,
      suffix: '',
      badge: 'Live feed',
      icon: ShieldAlert,
      accent: 'text-amber-300',
      description: 'Escalations surfaced by fusion engine in the last 24h.'
    },
    {
      title: 'Accuracy (7d)',
      value: '97.4%',
      suffix: '',
      badge: 'ML engine',
      icon: Activity,
      accent: 'text-emerald-300',
      description: 'Precision on confirmed truth-set for the last 7 days.'
    },
    {
      title: 'Avg analysis time',
      value: '8.2s',
      suffix: '',
      badge: 'Speed',
      icon: Workflow,
      accent: 'text-sky-300',
      description: 'End-to-end runtime per video including OCR + fusion.'
    }
  ] as const

  return (
    <section ref={ref} className="relative py-24 bg-[#050B18] text-white overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 opacity-70 bg-[radial-gradient(circle_at_top,_rgba(10,15,31,0.85),_#050B18_70%)]" />
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              'linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(0deg, rgba(255,255,255,0.04) 1px, transparent 1px)',
            backgroundSize: '120px 120px'
          }}
        />
        <div className="hidden lg:block absolute left-32 top-40 w-64 h-64 border border-cyan-400/20 rounded-full blur-3xl" />
        <div className="hidden lg:block absolute right-10 bottom-16 w-80 h-80 border border-pink-400/10 rounded-full blur-3xl" />
      </div>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate={isInView ? 'visible' : 'hidden'}
        className="relative max-w-7xl mx-auto px-6"
      >
        <div className="text-center mb-16">
          <motion.span
            className="inline-flex items-center gap-2 rounded-full bg-emerald-500/10 px-3.5 py-1 text-sm font-medium text-emerald-300"
            variants={cardVariants}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 animate-pulse" />
            Live monitoring
          </motion.span>
          <motion.h2
            className="mt-5 text-4xl md:text-5xl lg:text-6xl font-black tracking-tight"
            variants={cardVariants}
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
          >
            Command-grade clarity for your{' '}
            <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent">detection workflows</span>
          </motion.h2>
          <motion.p
            className="mt-4 text-lg text-slate-300 max-w-3xl mx-auto"
            variants={cardVariants}
          >
            A handcrafted dashboard tuned for analysts, surfacing verdict certainty, anomaly context, and workflow readiness in one responsive surface.
          </motion.p>
        </div>
        <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] items-start">
          <motion.div
            variants={cardVariants}
            whileHover={{ scale: 1.03, translateY: -4 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
            className="relative overflow-hidden rounded-3xl border border-white/10 bg-[#0C1429]/80 p-8 shadow-[0_25px_80px_rgba(0,0,0,0.55)] backdrop-blur-xl"
          >
            <div className="absolute inset-0 pointer-events-none opacity-60">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(19,114,255,0.25),_transparent_55%)]" />
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(255,85,132,0.2),_transparent_60%)]" />
            </div>
            <div className="relative flex flex-col gap-8 lg:flex-row lg:items-center">
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="inline-flex items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-sm font-semibold text-amber-200">
                    <Shield className="h-4 w-4" />
                    Verdict: AI
                  </span>
                  <span className="inline-flex items-center gap-2 rounded-full bg-cyan-500/10 px-3 py-1 text-xs uppercase tracking-wide text-cyan-200">
                    Forensic
                  </span>
                  <span className="inline-flex items-center gap-2 rounded-full bg-purple-500/10 px-3 py-1 text-xs uppercase tracking-wide text-purple-200">
                    ML Engine
                  </span>
                </div>
                <h3 className="mt-5 text-3xl font-bold text-white">Detection overview</h3>
                <p className="mt-2 text-slate-300">
                  Fusion model aggregated 42 signals. Motion logic, watermark OCR, and PRNU mismatch registered as high-confidence anomalies.
                </p>
                <div className="mt-6">
                  <div className="flex items-center justify-between text-xs font-medium text-slate-400">
                    <span>AI probability</span>
                    <span className="text-slate-200">{Math.round(aiScore * 100)}%</span>
                  </div>
                  <div className="relative mt-2 h-3 overflow-hidden rounded-full bg-slate-800/60">
                    <motion.div
                      initial={{ width: '0%' }}
                      animate={isInView ? { width: `${aiScore * 100}%` } : { width: '0%' }}
                      transition={{ duration: 0.9, delay: 0.2 }}
                      className="h-full rounded-full bg-gradient-to-r from-amber-400 via-pink-500 to-purple-500 shadow-[0_0_20px_rgba(255,90,135,0.6)]"
                    />
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={isInView ? { opacity: 1, x: `${aiScore * 100}%` } : { opacity: 0, x: 0 }}
                      transition={{ duration: 0.9, delay: 0.35 }}
                      className="absolute top-1/2 -translate-y-1/2 translate-x-[-50%]"
                    >
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-xs font-semibold text-white shadow-lg backdrop-blur">
                        <Sparkles className="h-3 w-3" />
                      </span>
                    </motion.span>
                  </div>
                </div>
                <div className="mt-8">
                  <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-slate-400">
                    <span>Confidence stream</span>
                    <span>Last 90s</span>
                  </div>
                  <svg viewBox="0 0 180 50" className="mt-3 h-20 w-full">
                    <defs>
                      <linearGradient id="sparklineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.1" />
                        <stop offset="60%" stopColor="#fb7185" stopOpacity="0.6" />
                        <stop offset="100%" stopColor="#c084fc" stopOpacity="0.9" />
                      </linearGradient>
                    </defs>
                    <motion.path
                      d="M0 40 L25 32 L50 36 L75 18 L100 25 L125 12 L150 28 L175 14"
                      fill="none"
                      stroke="url(#sparklineGradient)"
                      strokeWidth={2.5}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      initial={{ strokeDasharray: 260, strokeDashoffset: 260 }}
                      animate={isInView ? { strokeDashoffset: 0 } : { strokeDashoffset: 260 }}
                      transition={{ duration: 1.4, delay: 0.3 }}
                    />
                    <motion.circle
                      r={4}
                      fill="#f472b6"
                      initial={{ opacity: 0, cx: 0, cy: 40 }}
                      animate={
                        isInView
                          ? {
                              opacity: 1,
                              cx: [0, 25, 50, 75, 100, 125, 150, 175],
                              cy: [40, 32, 36, 18, 25, 12, 28, 14]
                            }
                          : { opacity: 0, cx: 0, cy: 40 }
                      }
                      transition={{ duration: 3.2, ease: 'easeInOut', repeat: Infinity, repeatDelay: 0.6 }}
                    />
                  </svg>
                </div>
              </div>
              <div className="relative flex-shrink-0">
                <div className="mb-3 text-center">
                  <motion.p
                    initial={{ opacity: 0, y: -6 }}
                    animate={isInView ? { opacity: 0.85, y: 0 } : { opacity: 0, y: -6 }}
                    transition={{ duration: 0.4 }}
                    className="text-[0.65rem] uppercase tracking-[0.4em] text-slate-400"
                  >
                    Confidence
                  </motion.p>
                </div>
                <div className="relative mx-auto flex h-44 w-44 items-center justify-center rounded-3xl border border-white/10 bg-slate-900/40 p-4 shadow-inner">
                  <svg viewBox="0 0 120 120" className="h-full w-full">
                    <circle cx="60" cy="60" r={gaugeRadius} stroke="rgba(255,255,255,0.12)" strokeWidth="10" fill="transparent" />
                    <motion.circle
                      cx="60"
                      cy="60"
                      r={gaugeRadius}
                      stroke="url(#gaugeStroke)"
                      strokeWidth="10"
                      strokeLinecap="round"
                      fill="transparent"
                      strokeDasharray={gaugeCircumference}
                      initial={{ strokeDashoffset: gaugeCircumference }}
                      animate={isInView ? { strokeDashoffset: gaugeCircumference * (1 - aiScore) } : { strokeDashoffset: gaugeCircumference }}
                      transition={{ duration: 1.2, ease: 'easeOut' }}
                    />
                    <defs>
                      <linearGradient id="gaugeStroke" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#fb923c" />
                        <stop offset="50%" stopColor="#fb7185" />
                        <stop offset="100%" stopColor="#a855f7" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center gap-1">
                    <motion.p
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
                      transition={{ duration: 0.6 }}
                      className="text-4xl font-black text-white"
                      style={{ textShadow: '0 3px 12px rgba(5,10,24,0.6)' }}
                    >
                      {Math.round(aiScore * 100)}%
                    </motion.p>
                    <span className="mt-1 rounded-full bg-white/10 px-3 py-0.5 text-[0.65rem] font-semibold uppercase tracking-[0.25em] text-white">
                      Hard AI evidence
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative mt-10 grid gap-6 text-sm text-slate-300 md:grid-cols-3">
              {[
                { label: 'Watermark OCR', value: 'SORA • persistent', accent: 'text-amber-200' },
                { label: 'Scene logic', value: 'Discontinuous motion', accent: 'text-cyan-200' },
                { label: 'Optical flow', value: 'Flicker + rPPG drift', accent: 'text-purple-200' }
              ].map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                  <p className="text-xs uppercase tracking-wide text-slate-400">{item.label}</p>
                  <p className={`mt-1 text-base font-semibold ${item.accent}`}>{item.value}</p>
                </div>
              ))}
            </div>
          </motion.div>
          <div className="space-y-6">
            {statCards.map((card, index) => {
              const Icon = card.icon
              return (
                <motion.div
                  key={card.title}
                  variants={cardVariants}
                  whileHover={{ scale: 1.03, translateY: -4 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                  className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0D152D]/80 p-6 shadow-[0_18px_45px_rgba(0,0,0,0.55)] backdrop-blur-lg"
                >
                  <motion.div
                    className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-gradient-to-br from-cyan-400/20 to-purple-500/10 blur-3xl"
                    animate={isInView ? { scale: [1, 1.08, 1] } : { scale: 1 }}
                    transition={{ duration: 6, repeat: Infinity, repeatType: 'mirror' }}
                    aria-hidden
                  />
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-3">
                      <span className="inline-flex items-center gap-2 rounded-full bg-white/5 px-2.5 py-0.5 text-xs font-semibold text-slate-200">
                        {card.badge}
                      </span>
                      <div>
                        <p className="text-3xl font-semibold text-white leading-tight">
                          {card.value}
                          {card.suffix}
                        </p>
                        <p className="mt-1 text-sm text-slate-400 leading-relaxed">{card.description}</p>
                      </div>
                    </div>
                    <motion.div
                      className="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-700/60 bg-slate-900/60 shadow-inner"
                      animate={isInView ? { y: [-4, 0, -4] } : { y: 0 }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                    >
                      <Icon className={`h-5 w-5 ${card.accent}`} />
                    </motion.div>
                  </div>
                  <div className="mt-6 border-t border-white/5 pt-4 text-xs uppercase tracking-[0.25em] text-slate-500 flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      Stable
                    </span>
                    <span className="flex items-center gap-2 text-[10px] tracking-[0.35em] text-white/40">
                      <EyeOff className="h-4 w-4 text-slate-500" />
                      Noise gated · Data flow
                    </span>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </motion.div>
    </section>
  )
}

function Footer() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-50px' })
  return (
    <footer ref={ref} className="bg-slate-900 dark:bg-black text-white py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }} transition={{ duration: 0.5 }}>
            <div className="flex items-center mb-6">
              <span
                className="text-4xl sero-brand bg-gradient-to-r from-orange-500 via-rose-500 to-pink-500 bg-clip-text text-transparent"
              >
                Sero
              </span>
            </div>
            <p className="text-gray-300 leading-relaxed mb-6" style={{ fontWeight: 500 }}>
              AI-powered deepfake detection that restores trust in digital media.
            </p>
            <div className="flex items-center gap-3">
              <a href="#twitter" className="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors" aria-label="Twitter">
                <Twitter className="w-5 h-5 text-gray-300" />
              </a>
              <a href="https://github.com/mizuharaa/SeroAI" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors" aria-label="GitHub">
                <Github className="w-5 h-5 text-gray-300" />
              </a>
              <a href="https://www.linkedin.com/in/trkang/" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors" aria-label="LinkedIn">
                <Linkedin className="w-5 h-5 text-gray-300" />
              </a>
            </div>
          </motion.div>
          {[
            { title: 'Product', items: ['Features', 'Pricing', 'API Docs', 'Dashboard', 'Changelog'] },
            { title: 'Company', items: ['About', 'Blog', 'Careers', 'Press Kit', 'Contact'] },
            { title: 'Legal', items: ['Privacy', 'Terms', 'Security', 'Cookies', 'Licenses'] }
          ].map((section, index) => (
            <motion.div key={section.title} initial={{ opacity: 0, y: 30 }} animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }} transition={{ duration: 0.5, delay: 0.1 + index * 0.1 }}>
              <h4 className="text-white mb-6" style={{ fontWeight: 700 }}>
                {section.title}
              </h4>
              <ul className="space-y-3">
                {section.items.map((item) => (
                  <li key={item}>
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="pt-8 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p className="text-gray-400">© 2025 Sero. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              Status
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              Twitter
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              GitHub
            </a>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}


