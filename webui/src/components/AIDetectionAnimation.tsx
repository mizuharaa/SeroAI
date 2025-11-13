import React from 'react'
import { motion } from 'framer-motion'

export function AIDetectionAnimation() {
  return (
    <div className="relative w-[520px] h-[360px] rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-xl">
      <div className="absolute inset-0 bg-gradient-to-br from-orange-100/40 via-rose-100/30 to-amber-100/40 dark:from-slate-800/60 dark:via-slate-900/60 dark:to-slate-800/60" />
      <div className="relative z-10 p-6">
        <div className="text-sm text-gray-600 dark:text-gray-300 font-semibold mb-3">Live AI Analysis</div>
        <div className="space-y-3">
          {[0, 1, 2, 3, 4].map((i) => (
            <motion.div
              key={i}
              initial={{ width: '10%' }}
              animate={{ width: ['10%', '95%', '40%', '85%', '65%'][i % 5] }}
              transition={{ duration: 1.6, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
              className="h-3 rounded-full bg-gradient-to-r from-orange-500 to-pink-500"
            />
          ))}
        </div>
        <div className="mt-6 grid grid-cols-3 gap-3">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
              className="h-20 rounded-xl bg-white/70 dark:bg-slate-800/70 border border-gray-200 dark:border-slate-700"
            />
          ))}
        </div>
        <div className="mt-6 text-xs text-gray-500 dark:text-gray-400">This is a visual placeholder used during development.</div>
      </div>
    </div>
  )
}


