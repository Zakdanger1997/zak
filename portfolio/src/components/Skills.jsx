import { motion } from 'framer-motion'
import Section from './Section'
import { skills } from '../data'

export default function Skills() {
  return (
    <Section id="skills" kicker="What I use" title="Skills & Tools">
      <div className="grid gap-8 md:grid-cols-3">
        {skills.map((cat, ci) => (
          <div key={ci} className="card">
            <h3 className="mb-4 font-display text-lg font-semibold text-white">
              {cat.group}
            </h3>
            <div className="flex flex-wrap gap-2">
              {cat.items.map((item, i) => (
                <motion.span
                  key={i}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.05 }}
                  className="pill"
                >
                  {item}
                </motion.span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Section>
  )
}
