import { useState, useEffect } from 'react'
import { profile } from '../data'

const links = [
  ['About', '#about'],
  ['Skills', '#skills'],
  ['Experience', '#experience'],
  ['Work', '#work'],
  ['Contact', '#contact'],
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const initials = profile.name
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-ink/80 backdrop-blur-md border-b border-white/10'
          : 'bg-transparent'
      }`}
    >
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <a href="#top" className="font-display text-lg font-bold tracking-tight">
          <span className="text-accent">{initials}</span>
          <span className="text-white/40">.</span>
        </a>
        <ul className="hidden gap-8 md:flex">
          {links.map(([label, href]) => (
            <li key={href}>
              <a
                href={href}
                className="text-sm text-muted transition-colors hover:text-white"
              >
                {label}
              </a>
            </li>
          ))}
        </ul>
        <a
          href="#contact"
          className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-white transition-transform hover:scale-105"
        >
          Get in touch
        </a>
      </nav>
    </header>
  )
}
