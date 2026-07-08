import { motion } from 'framer-motion'
import Scene3D from './Scene3D'
import { profile } from '../data'

export default function Hero() {
  return (
    <section id="top" className="relative min-h-screen w-full overflow-hidden">
      {/* 3D background */}
      <div className="absolute inset-0">
        <Scene3D />
      </div>
      <div className="glow pointer-events-none absolute inset-0" />

      {/* Content */}
      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6">
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-4 font-mono text-sm font-semibold uppercase tracking-widest text-accent2"
        >
          {profile.location}
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-2xl font-display text-5xl font-bold leading-tight tracking-tight md:text-7xl"
        >
          {profile.name}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-4 max-w-xl text-xl text-white/80 md:text-2xl"
        >
          {profile.headline}
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-6 max-w-lg text-base text-muted"
        >
          {profile.tagline}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-10 flex flex-wrap gap-4"
        >
          <a
            href="#work"
            className="rounded-full bg-accent px-6 py-3 font-semibold text-white transition-transform hover:scale-105"
          >
            View my work
          </a>
          <a
            href="#contact"
            className="rounded-full border border-white/20 px-6 py-3 font-semibold text-white transition-colors hover:bg-white/5"
          >
            Contact me
          </a>
        </motion.div>
      </div>

      {/* Scroll hint */}
      <div className="absolute bottom-8 left-1/2 z-10 -translate-x-1/2 text-white/40">
        <div className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-white/20 p-1.5">
          <div className="h-2 w-1 animate-bounce rounded-full bg-white/60" />
        </div>
      </div>
    </section>
  )
}
