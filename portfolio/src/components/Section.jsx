import { motion } from 'framer-motion'

// Shared reveal-on-scroll wrapper for a titled section.
export default function Section({ id, kicker, title, children }) {
  return (
    <section id={id} className="section">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.6 }}
      >
        {kicker && <p className="section-kicker">{kicker}</p>}
        {title && <h2 className="section-title">{title}</h2>}
        <div className="mt-10">{children}</div>
      </motion.div>
    </section>
  )
}
