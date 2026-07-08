import Section from './Section'
import { profile } from '../data'

const socialLabels = {
  linkedin: 'LinkedIn',
  github: 'GitHub',
  twitter: 'Twitter',
  website: 'Website',
}

export default function Contact() {
  const socials = Object.entries(profile.socials).filter(
    ([, url]) => url && !url.startsWith('PLACEHOLDER'),
  )

  return (
    <Section id="contact" kicker="Say hello" title="Let's build something">
      <div className="card mx-auto max-w-2xl text-center">
        <p className="text-lg text-white/80">
          Interested in working together or just want to chat? My inbox is open.
        </p>
        <a
          href={`mailto:${profile.email}`}
          className="mt-6 inline-block rounded-full bg-accent px-8 py-4 text-lg font-semibold text-white transition-transform hover:scale-105"
        >
          {profile.email}
        </a>
        {socials.length > 0 && (
          <div className="mt-8 flex justify-center gap-6">
            {socials.map(([key, url]) => (
              <a
                key={key}
                href={url}
                target="_blank"
                rel="noreferrer"
                className="text-muted transition-colors hover:text-white"
              >
                {socialLabels[key] || key}
              </a>
            ))}
          </div>
        )}
      </div>
      <p className="mt-16 text-center text-sm text-muted">
        © {new Date().getFullYear()} {profile.name}. Built with React, Three.js
        &amp; Tailwind.
      </p>
    </Section>
  )
}
