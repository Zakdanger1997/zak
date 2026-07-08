import Section from './Section'
import { experience } from '../data'

export default function Experience() {
  return (
    <Section id="experience" kicker="Where I've worked" title="Experience">
      <div className="relative border-l border-white/10 pl-8">
        {experience.map((job, i) => (
          <div key={i} className="relative mb-10 last:mb-0">
            <span className="absolute -left-[41px] top-1.5 h-3.5 w-3.5 rounded-full border-2 border-accent bg-ink" />
            <p className="text-sm font-mono text-accent2">{job.period}</p>
            <h3 className="mt-1 font-display text-xl font-semibold text-white">
              {job.role}
            </h3>
            <p className="text-muted">{job.company}</p>
            <p className="mt-2 max-w-2xl text-white/70">{job.summary}</p>
          </div>
        ))}
      </div>
    </Section>
  )
}
