import { motion } from 'framer-motion'
import Section from './Section'
import { projects } from '../data'

export default function Projects() {
  return (
    <Section id="work" kicker="Featured work" title="Projects">
      <div className="grid gap-6 md:grid-cols-2">
        {projects.map((p, i) => (
          <motion.a
            key={i}
            href={p.link || undefined}
            target={p.link ? '_blank' : undefined}
            rel="noreferrer"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="card group block"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-display text-xl font-semibold text-white group-hover:text-accent">
                {p.title}
              </h3>
              {p.link && (
                <span className="text-muted transition-transform group-hover:translate-x-1 group-hover:-translate-y-1">
                  ↗
                </span>
              )}
            </div>
            <p className="mt-3 text-white/70">{p.description}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {p.tags.map((t, ti) => (
                <span
                  key={ti}
                  className="rounded-md bg-accent/10 px-2 py-1 text-xs font-medium text-accent2"
                >
                  {t}
                </span>
              ))}
            </div>
          </motion.a>
        ))}
      </div>
    </Section>
  )
}
