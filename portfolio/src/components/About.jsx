import Section from './Section'
import { profile, education } from '../data'

export default function About() {
  return (
    <Section id="about" kicker="Who I am" title="About">
      <div className="grid gap-10 md:grid-cols-3">
        <p className="md:col-span-2 text-lg leading-relaxed text-white/80">
          {profile.about}
        </p>
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-widest text-accent2">
              Based in
            </h3>
            <p className="mt-1 text-white/80">{profile.location}</p>
          </div>
          {education.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-widest text-accent2">
                Education
              </h3>
              {education.map((e, i) => (
                <div key={i} className="mt-1 text-white/80">
                  <p className="font-medium">{e.degree}</p>
                  <p className="text-sm text-muted">
                    {e.school} · {e.period}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Section>
  )
}
