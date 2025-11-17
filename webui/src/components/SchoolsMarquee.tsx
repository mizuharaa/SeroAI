import React from 'react'
import { motion } from 'framer-motion'

type School = { name: string; domain: string }

// Logos are fetched dynamically via Clearbit Logo CDN using official domains.
// Example: https://logo.clearbit.com/harvard.edu
const row1: School[] = [
  { name: 'Harvard', domain: 'harvard.edu' },
  { name: 'MIT', domain: 'mit.edu' },
  { name: 'Stanford', domain: 'stanford.edu' },
  { name: 'Princeton', domain: 'princeton.edu' },
  { name: 'Columbia', domain: 'columbia.edu' },
  { name: 'Yale', domain: 'yale.edu' },
  { name: 'UPenn', domain: 'upenn.edu' },
  { name: 'Brown', domain: 'brown.edu' },
  { name: 'Cornell', domain: 'cornell.edu' },
  { name: 'Dartmouth', domain: 'dartmouth.edu' },
  { name: 'UChicago', domain: 'uchicago.edu' },
  { name: 'Caltech', domain: 'caltech.edu' },
  { name: 'Johns Hopkins', domain: 'jhu.edu' },
  { name: 'Duke', domain: 'duke.edu' },
  { name: 'Northwestern', domain: 'northwestern.edu' }
]

const row2: School[] = [
  { name: 'UC Berkeley', domain: 'berkeley.edu' },
  { name: 'UCLA', domain: 'ucla.edu' },
  { name: 'UMass Amherst', domain: 'umass.edu' },
  { name: 'Michigan', domain: 'umich.edu' },
  { name: 'CMU', domain: 'cmu.edu' },
  { name: 'Georgia Tech', domain: 'gatech.edu' },
  { name: 'NYU', domain: 'nyu.edu' },
  { name: 'Vanderbilt', domain: 'vanderbilt.edu' },
  { name: 'Oxford', domain: 'ox.ac.uk' },
  { name: 'Cambridge', domain: 'cam.ac.uk' }
]

function Row({ items, reverse = false, duration = 30 }: { items: School[]; reverse?: boolean; duration?: number }) {
  const doubled = [...items, ...items]
  return (
    <div
      className="overflow-hidden"
      style={{
        WebkitMaskImage: 'linear-gradient(to right, transparent, black 10%, black 90%, transparent)',
        maskImage: 'linear-gradient(to right, transparent, black 10%, black 90%, transparent)'
      }}
    >
      <motion.div
        className="flex gap-10 min-w-max py-4"
        animate={{ x: reverse ? ['-50%', '0%'] : ['0%', '-50%'] }}
        transition={{ duration, ease: 'linear', repeat: Infinity }}
      >
        {doubled.map((s, idx) => {
          const src = `https://logo.clearbit.com/${s.domain}?size=80`
          return (
            <img
              key={`${s.domain}-${idx}`}
              src={src}
              alt={s.name}
              loading="lazy"
              onError={(e) => {
                // Hide if logo not found
                (e.currentTarget as HTMLImageElement).style.display = 'none'
              }}
              className="h-10 md:h-12 object-contain opacity-80 hover:opacity-100 transition-opacity duration-200 filter grayscale hover:grayscale-0"
              style={{ maxWidth: 160 }}
            />
          )
        })}
      </motion.div>
    </div>
  )
}

export function SchoolsMarquee() {
  return (
    <section className="py-20 bg-gradient-to-b from-transparent to-black/0 dark:from-transparent dark:to-black/20">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-8">
          <h3
            className="text-2xl md:text-3xl text-gray-900 dark:text-white"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
          >
            Join learners from top schools and teams
          </h3>
        </div>
        <Row items={row1} duration={28} />
        <div className="h-4" />
        <Row items={row2} reverse duration={32} />
      </div>
    </section>
  )
}


