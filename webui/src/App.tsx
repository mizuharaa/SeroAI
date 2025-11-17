import React, { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { motion, useInView, animate } from 'framer-motion'
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
  Sparkles
} from 'lucide-react'
import { Twitter, Github, Linkedin } from 'lucide-react'
import { SimpleGlobe } from './components/SimpleGlobe'
import { UploadZone } from './components/UploadZone'
import { AnalysisProgress } from './components/AnalysisProgress'
import { ResultsDisplay } from './components/ResultsDisplay'
import { SchoolsMarquee } from './components/SchoolsMarquee'

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

export default function App() {
  // Simple client-side routing without extra deps
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
                  className="text-8xl text-white tracking-tight block"
                  style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
                >
                  Sero
                </span>
              </motion.div>
            </motion.div>
          </div>
        </>
      )}

      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? 'bg-white/90 dark:bg-slate-950/90 border-b border-gray-200 dark:border-slate-800' : 'bg-transparent'
        }`}
        onMouseLeave={() => setActiveDropdown(null)}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <a
              href="/"
              className="flex items-center cursor-pointer"
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
              <span
                className="text-4xl bg-gradient-to-r from-orange-500 to-orange-400 bg-clip-text text-transparent tracking-tight"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
              >
                Sero
              </span>
            </a>
            <div className="hidden lg:flex items-center gap-1">
              {Object.keys(navItems).map((item) => (
                <div key={item} onMouseEnter={() => setActiveDropdown(item)} className="relative">
                  <button className="px-4 py-2 text-gray-900 dark:text-gray-100 hover:text-orange-500 dark:hover:text-orange-400 transition-colors flex items-center gap-1">
                    <span>{item}</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <a
                href="#pricing"
                className="px-4 py-2 text-gray-900 dark:text-gray-100 hover:text-orange-500 dark:hover:text-orange-400 transition-colors"
              >
                Pricing
              </a>
              <a
                href="#contact"
                className="px-4 py-2 text-gray-900 dark:text-gray-100 hover:text-orange-500 dark:hover:text-orange-400 transition-colors"
              >
                Contact
              </a>
            </div>
            <div className="hidden lg:flex items-center gap-3">
              <button
                onClick={handleDarkModeToggle}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-2"
                aria-label="Toggle dark mode"
                role="switch"
                aria-checked={isDarkMode}
              >
                {isDarkMode ? <Sun className="w-5 h-5 text-gray-400" /> : <Moon className="w-5 h-5 text-gray-600" />}
                <span className="text-sm text-gray-700 dark:text-gray-300">{isDarkMode ? 'Dark' : 'Light'}</span>
              </button>
              <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="px-4 py-2 text-gray-900 dark:text-gray-100 hover:text-orange-500 transition-colors">
                Sign in
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => withLogoSplash(() => navigate('/detect'))}
                className="px-5 py-2 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-lg shadow-lg shadow-orange-500/30 transition-shadow hover:shadow-orange-500/50"
              >
                Get Started
              </motion.button>
            </div>
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
        {activeDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="absolute inset-x-0 mt-2"
            onMouseLeave={() => setActiveDropdown(null)}
          >
            <div className="mx-auto w-full max-w-5xl px-6">
              <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-2xl shadow-xl overflow-hidden">
                <div className="p-6">
                  <div className="grid grid-cols-3 gap-4">
                    {navItems[activeDropdown as keyof typeof navItems]?.items.map((item, index) => {
                      const Icon = item.icon
                      return (
                        <motion.a
                          key={item.title}
                          href="#"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2, delay: index * 0.05 }}
                          whileHover={{ x: 5, transition: { duration: 0.2 } }}
                          className="flex flex-col items-start gap-3 p-4 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
                        >
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                            <Icon className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="text-gray-900 dark:text-white mb-1">{item.title}</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
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
                  className="block px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                  {item}
                </a>
              ))}
              <a
                href="#pricing"
                className="block px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                Pricing
              </a>
              <a
                href="#contact"
                className="block px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                Contact
              </a>
              <div className="pt-4 border-t border-gray-200 dark:border-slate-800 space-y-2">
                <button
                  onClick={handleDarkModeToggle}
                  className="w-full px-4 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors flex items-center justify-between"
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
                <button className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
                  Sign in
                </button>
                <button
                  onClick={() => {
                    setIsMobileMenuOpen(false)
                    withLogoSplash(() => navigate('/detect'))
                  }}
                  className="w-full px-4 py-2 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-lg"
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
          <HeroLeft />
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
      {/* Top banner styled like hero background */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-200 via-rose-300 to-pink-300 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900" />
        <motion.div
          aria-hidden
          className="absolute -top-24 -left-24 w-[520px] h-[520px] rounded-full bg-gradient-to-tr from-orange-400/40 to-pink-400/40 blur-3xl"
          animate={{ x: [0, 60, -40, 0], y: [0, 40, -20, 0], scale: [1, 1.08, 1] }}
          transition={{ duration: 24, repeat: Infinity, ease: 'linear' }}
        />
        <motion.div
          aria-hidden
          className="absolute bottom-[-120px] right-[-120px] w-[620px] h-[620px] rounded-full bg-gradient-to-bl from-rose-400/40 via-amber-400/30 to-pink-400/40 blur-3xl"
          animate={{ x: [0, -80, 50, 0], y: [0, -30, 40, 0], scale: [1, 1.1, 1] }}
          transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
        />
        <div className="relative max-w-7xl mx-auto px-6 py-16">
          <div className="flex items-center justify-between flex-wrap gap-6">
            <div>
              <h1
                className="text-4xl md:text-6xl text-gray-900 dark:text-white tracking-tight"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
              >
                Deepfake Detection
              </h1>
              <p className="text-lg md:text-xl text-gray-700 dark:text-gray-300 mt-3">
                Upload a video or image and get a fast, detailed authenticity report.
              </p>
            </div>
            <div className="hidden md:block">
              <div className="rounded-2xl p-4 bg-white/80 dark:bg-slate-900/80 border border-gray-200 dark:border-slate-700 shadow">
                <div className="text-sm text-gray-600 dark:text-gray-300">Typical processing time</div>
                <div className="text-2xl font-semibold text-orange-600 dark:text-orange-400">~ 8–12s</div>
              </div>
            </div>
          </div>

          {/* Quick facts cards */}
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { title: 'Supported Formats', desc: 'MP4, MOV, AVI, WebM, JPG, PNG', color: 'from-blue-500 to-cyan-500' },
              { title: 'Limits', desc: 'Up to 500MB • ~5 minutes', color: 'from-emerald-500 to-green-500' },
              { title: 'Privacy', desc: 'Files never shared. Local processing options.', color: 'from-purple-500 to-pink-500' }
            ].map((c) => (
              <div key={c.title} className="rounded-2xl p-4 border bg-white/70 dark:bg-slate-900/70 border-gray-200 dark:border-slate-700 shadow flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${c.color}`} />
                <div>
                  <div className="text-gray-900 dark:text-white font-semibold">{c.title}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{c.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Main detect content */}
      <DetectSection />
      <SchoolsMarquee />
      <Footer />
    </div>
  )
}

function HeroLeft() {
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
        <span className="text-gray-700 dark:text-gray-300 font-medium">Powered by Neural Forensics</span>
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
            className="block text-7xl sm:text-8xl lg:text-9xl font-black bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 bg-clip-text text-transparent"
            style={{
              textShadow: '0 0 80px rgba(249, 115, 22, 0.3)',
              WebkitTextStroke: '1px rgba(249, 115, 22, 0.1)'
            }}
          >
            with Sero
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
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.8 }} className="flex flex-wrap items-center gap-4">
      <motion.button
        whileHover={{ scale: 1.05, y: -3 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => {
          if (window.location.pathname !== '/detect') {
            window.history.pushState({}, '', '/detect')
          }
          window.dispatchEvent(new PopStateEvent('popstate'))
        }}
        className="group px-8 py-4 bg-gray-900 dark:bg-slate-100 text-white dark:text-gray-900 rounded-xl shadow-xl hover:shadow-2xl transition-shadow flex items-center gap-2"
      >
        <span>Start now</span>
        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </motion.button>
      <motion.button
        whileHover={{ scale: 1.05, y: -3 }}
        whileTap={{ scale: 0.95 }}
        className="px-8 py-4 bg-white dark:bg-slate-800 text-gray-900 dark:text-white rounded-xl border border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 hover:shadow-lg transition-all flex items-center gap-3"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18.17 10.19c0-.63-.06-1.24-.16-1.83H10v3.46h4.58c-.2 1.05-.8 1.93-1.69 2.53v2.11h2.73c1.6-1.47 2.53-3.64 2.53-6.27z" fill="#4285F4" />
          <path d="M10 18.5c2.28 0 4.2-.75 5.6-2.04l-2.73-2.11c-.76.51-1.73.81-2.87.81-2.21 0-4.08-1.49-4.75-3.5H2.42v2.18A8.5 8.5 0 0010 18.5z" fill="#34A853" />
          <path d="M5.25 10.66c-.17-.51-.27-1.05-.27-1.61s.1-1.1.27-1.61V5.26H2.42A8.5 8.5 0 001.5 10c0 1.37.33 2.67.92 3.82l2.83-2.16z" fill="#FBBC05" />
          <path d="M10 4.24c1.25 0 2.37.43 3.25 1.27l2.44-2.44C14.2 1.69 12.28.9 10 .9a8.5 8.5 0 00-7.58 4.68l2.83 2.18c.67-2.01 2.54-3.5 4.75-3.5z" fill="#EA4335" />
        </svg>
        <span>Sign up with Google</span>
      </motion.button>
    </motion.div>
  )
}

// Detection page section (standalone page)
function DetectSection() {
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
  }
  const [results, setResults] = useState<
    Array<{ method: string; score: number; confidence: number; details: string[]; icon: 'eye' | 'zap' | 'waves' | 'box' | 'audio' | 'grid' }>
  >([])
  const [methods, setMethods] = useState<LocalAnalysisMethod[]>([
    // Order matches backend stage completion so checks cascade top→bottom
    { id: '1', name: 'Frequency Domain Analysis', description: 'Detecting GAN fingerprints in spectral data', status: 'pending' }, // forensics
    { id: '2', name: 'Pixel Stability Analysis', description: 'Analyzing temporal consistency in static regions', status: 'pending' }, // artifact
    { id: '3', name: 'Biological Inconsistency Detection', description: 'Examining facial landmarks and body movements', status: 'pending' }, // face_dynamics
    { id: '4', name: 'Optical Flow Analysis', description: 'Analyzing motion vectors and patterns', status: 'pending' }, // temporal
    { id: '5', name: 'Spatial Logic Verification', description: 'Checking scene coherence and object persistence', status: 'pending' }, // scene_logic
    { id: '6', name: 'Audio-Visual Sync Check', description: 'Verifying lip-sync and audio authenticity', status: 'pending' } // audio_visual
  ])

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
    <section id="detect" className="py-24 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-10">
          <h2 className="text-4xl md:text-5xl text-gray-900 dark:text-white mb-4">Upload Your Media</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">Drop a video or image to start deepfake detection</p>
        </div>
        <div className="grid lg:grid-cols-2 gap-10">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow p-8">
            <UploadZone onFileSelect={handleFileSelect} isAnalyzing={overallProgress > 0 && overallProgress < 100} />
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow p-8">
            <AnalysisProgress
              methods={methods}
              overallProgress={overallProgress}
            />
          </div>
        </div>
        {selectedFile && results.length > 0 && (
          <div className="mt-10">
            <ResultsDisplay overallScore={overallScore} results={results} fileName={selectedFile.name} processingTime={processingTime} feedbackId={feedbackId || undefined} />
          </div>
        )}
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
    }, 100)
    return () => clearInterval(interval)
  }, [])
  const detectionMethods = [
    { name: 'Pixel Stability', color: 'bg-blue-500', icon: Grid3x3 },
    { name: 'Optical Flow', color: 'bg-emerald-500', icon: Zap },
    { name: 'Spatial Logic', color: 'bg-green-500', icon: Brain },
    { name: 'Frequency Analysis', color: 'bg-purple-500', icon: Gauge },
    { name: 'Audio Sync', color: 'bg-pink-500', icon: CheckCircle2 },
    { name: 'Face Analysis', color: 'bg-orange-500', icon: Shield }
  ] as const
  return (
    <div className="relative">
      <div className="relative bg-white/90 dark:bg-slate-900/90 rounded-3xl p-8 border border-gray-200 dark:border-slate-700 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-pink-500 flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-gray-900 dark:text.white dark:text-white">Analyzing Media</h3>
              <p className="text-gray-600 dark:text-gray-400">demo_video.mp4</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-gray-600 dark:text-gray-400">Progress</p>
            <p className="text-2xl text-gray-900 dark:text-white">{progress}%</p>
          </div>
        </div>
        <div className="mb-8">
          <div className="h-2 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-orange-500 to-pink-500 rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-6">
          {detectionMethods.map((method, index) => {
            const Icon = method.icon
            const isComplete = progress > (index / detectionMethods.length) * 100
            return (
              <div
                key={method.name}
                className={`p-4 rounded-xl border transition-colors duration-300 ${
                  isComplete
                    ? 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800'
                    : 'bg-gray-50 dark:bg-slate-800/50 border-gray-200 dark:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg ${method.color} flex items-center justify-center flex-shrink-0`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white truncate">{method.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{isComplete ? 'Complete' : 'Pending'}</p>
                  </div>
                  {isComplete && <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />}
                </div>
              </div>
            )
          })}
        </div>
        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-xl border border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-gray-900 dark:text-white">Authenticity Score</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Analyzing video integrity</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl text-blue-600 dark:text-blue-400">{Math.min(Math.round(progress * 0.98), 98)}%</p>
            </div>
          </div>
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
              icon: Search,
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
              start: -60
            },
            {
              icon: Network,
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
              start: 60
            },
            {
              icon: Timer,
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
              start: 60
            }
          ].map((item, index) => {
            const Icon = item.icon
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
                  {/* Floating icon with subtle animation */}
                  <motion.div
                    className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-6 shadow-2xl relative`}
                    whileHover={{ scale: 1.1, y: -4 }}
                    animate={{ y: [0, -4, 0] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <Icon className="w-10 h-10 text-white" strokeWidth={2.5} />
                    {/* Icon glow */}
                    <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${item.gradient} blur-xl opacity-50`} />
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
    <section ref={ref} className="py-24 bg-gray-50 dark:bg-slate-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div initial={{ opacity: 0, x: -60 }} animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -60 }} transition={{ duration: 0.6 }}>
            <h2
              className="text-5xl lg:text-7xl text-gray-900 dark:text-white mb-6 tracking-tight"
              style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
            >
              Built for <span className="bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-transparent">Developers</span>
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
              Simple, powerful API that integrates seamlessly into your workflow. Start detecting deepfakes in minutes.
            </p>
            <div className="space-y-4 mb-8">
              {[
                { icon: Code2, text: 'RESTful API with comprehensive docs' },
                { icon: Zap, text: '99.9% uptime SLA guarantee' },
                { icon: Shield, text: 'Enterprise-grade security' }
              ].map((item, index) => {
                const Icon = item.icon
                return (
                  <motion.div key={index} initial={{ opacity: 0, x: -40 }} animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -40 }} transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }} className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 text-lg">{item.text}</p>
                  </motion.div>
                )
              })}
            </div>
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              whileHover={{ scale: 1.05, y: -3 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-xl flex items-center gap-2 shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 transition-shadow"
            >
              <Book className="w-5 h-5" />
              <span>View Documentation</span>
            </motion.button>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 60 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-slate-900 rounded-3xl p-8 shadow-xl border border-slate-700"
          >
            <div className="flex items-center gap-2 mb-6">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <pre className="text-sm text-gray-300 overflow-x-auto">
              <code>{`import { SeroAI } from 'sero-sdk';
const sero = new SeroAI({
  apiKey: process.env.SERO_API_KEY
});
const result = await sero.detect({
  file: 'video.mp4',
  type: 'video'
});
console.log(result.isDeepfake);
// false
console.log(result.confidence);
// 0.98`}</code>
            </pre>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function WhySeroSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: '-100px' })
  const stats = [
    { value: '90%+', label: 'Precision (high-signal)', desc: 'On strong evidence cases', color: 'orange' },
    { value: '8–12s', label: 'Detection Speed', desc: 'Typical end-to-end time', color: 'purple' },
    { value: '3K+', label: 'Videos Trained', desc: 'Supervised fusion model', color: 'blue' },
    { value: 'Weekdays', label: 'Support', desc: 'Email-based assistance', color: 'green' }
  ] as const
  return (
    <section ref={ref} className="py-24 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.6 }}
            className="text-5xl lg:text-7xl text-gray-900 dark:text-white mb-6 tracking-tight"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
          >
            Why Choose <span className="bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-transparent">Sero</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto"
          >
            Industry-leading performance backed by cutting-edge AI research
          </motion.p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 40 }}
                animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
              transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
              className={`${
                stat.color === 'orange'
                  ? 'bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-900/50'
                  : stat.color === 'purple'
                  ? 'bg-purple-50 dark:bg-purple-950/20 border-purple-200 dark:border-purple-900/50'
                  : stat.color === 'blue'
                  ? 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900/50'
                  : 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900/50'
              } p-8 rounded-3xl border text-center`}
            >
              <div
                className={`text-5xl mb-4 ${
                  stat.color === 'orange'
                    ? 'text-orange-600 dark:text-orange-400'
                    : stat.color === 'purple'
                    ? 'text-purple-600 dark:text-purple-400'
                    : stat.color === 'blue'
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-green-600 dark:text-green-400'
                }`}
                style={{ fontWeight: 900 }}
                dangerouslySetInnerHTML={{ __html: stat.value }}
              />
              <h3 className="text-gray-900 dark:text-white mb-2">{stat.label}</h3>
              <p className="text-gray-600 dark:text-gray-400">{stat.desc}</p>
            </motion.div>
          ))}
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
            Stripe-level polish for your{' '}
            <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent">detection cockpit</span>
          </motion.h2>
          <motion.p
            className="mt-4 text-lg text-slate-300 max-w-3xl mx-auto"
            variants={cardVariants}
          >
            A handcrafted dashboard tuned for analysts: verdict certainty, anomaly context, and workflow signals in one responsive hero surface.
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
                <div className="mx-auto flex h-44 w-44 items-center justify-center rounded-3xl border border-white/10 bg-slate-900/40 p-4 shadow-inner">
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
                </div>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.6 }}
                  >
                    <p className="text-xs uppercase tracking-wide text-slate-400">Confidence</p>
                    <p className="text-4xl font-bold text-white">{Math.round(aiScore * 100)}%</p>
                    <p className="text-sm text-slate-400">Hard AI evidence</p>
                  </motion.div>
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
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="inline-flex items-center gap-2 rounded-full bg-white/5 px-2.5 py-0.5 text-xs font-semibold text-slate-200">
                        {card.badge}
                      </span>
                      <p className="mt-3 text-2xl font-semibold text-white">
                        {card.value}
                        {card.suffix}
                      </p>
                      <p className="text-sm text-slate-400">{card.description}</p>
                    </div>
                    <motion.div
                      className="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-700/60 bg-slate-900/60 shadow-inner"
                      animate={isInView ? { y: [-4, 0, -4] } : { y: 0 }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                    >
                      <Icon className={`h-5 w-5 ${card.accent}`} />
                    </motion.div>
                  </div>
                  <div className="mt-5 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
                    <div className="flex items-center gap-1">
                      <div className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      Stable
                    </div>
                    <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/40 to-transparent" />
                    <EyeOff className="h-4 w-4 text-slate-500" />
                    Noise gated
                  </div>
                  <motion.div
                    className="absolute bottom-4 right-4 flex flex-col gap-1.5 text-[10px] uppercase tracking-[0.2em] text-white/30"
                    animate={isInView ? { opacity: [0.5, 0.8, 0.5] } : { opacity: 0.4 }}
                    transition={{ duration: 4, repeat: Infinity }}
                    aria-hidden
                  >
                    <span>01 · 10</span>
                    <span>DATA FLOW</span>
                  </motion.div>
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
                className="text-4xl bg-gradient-to-r from-orange-500 to-orange-400 bg-clip-text text-transparent"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
              >
                Sero
              </span>
            </div>
            <p className="text-gray-300 leading-relaxed mb-6" style={{ fontWeight: 500 }}>
              AI-powered deepfake detection that restores trust in digital media.
            </p>
            <div className="flex items-center gap-3">
              <a href="#twitter" className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors" aria-label="Twitter">
                <Twitter className="w-5 h-5 text-gray-300" />
              </a>
              <a href="https://github.com/mizuharaa/SeroAI" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors" aria-label="GitHub">
                <Github className="w-5 h-5 text-gray-300" />
              </a>
              <a href="https://www.linkedin.com/in/trkang/" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors" aria-label="LinkedIn">
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


