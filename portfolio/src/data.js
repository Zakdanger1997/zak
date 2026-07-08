// ============================================================================
//  YOUR CONTENT LIVES HERE.
//  Everything on the site reads from this file. Replace the PLACEHOLDER_*
//  values with your real LinkedIn info and the whole portfolio updates.
// ============================================================================

export const profile = {
  name: 'PLACEHOLDER_NAME',
  headline: 'PLACEHOLDER_HEADLINE', // e.g. "Full-Stack Developer & 3D Web Enthusiast"
  location: 'PLACEHOLDER_LOCATION',
  email: 'PLACEHOLDER_EMAIL',
  // Short punchy tagline shown in the hero
  tagline: 'PLACEHOLDER_TAGLINE',
  // 2-4 sentence "About" section
  about:
    'PLACEHOLDER_ABOUT — paste your LinkedIn About section here. A couple of ' +
    'sentences on who you are, what you do, and what you care about.',
  resumeUrl: '', // optional: link to a hosted PDF resume
  socials: {
    linkedin: 'PLACEHOLDER_LINKEDIN_URL',
    github: '',
    twitter: '',
    website: '',
  },
}

// Skills grouped by category — shown as animated pills.
export const skills = [
  { group: 'PLACEHOLDER_GROUP_1', items: ['Skill A', 'Skill B', 'Skill C'] },
  { group: 'PLACEHOLDER_GROUP_2', items: ['Skill D', 'Skill E', 'Skill F'] },
  { group: 'PLACEHOLDER_GROUP_3', items: ['Skill G', 'Skill H'] },
]

// Work history — most recent first. Rendered as a vertical timeline.
export const experience = [
  {
    role: 'PLACEHOLDER_ROLE',
    company: 'PLACEHOLDER_COMPANY',
    period: 'PLACEHOLDER_DATES', // e.g. "2023 — Present"
    summary: 'PLACEHOLDER — one or two lines on what you did and achieved.',
  },
  {
    role: 'PLACEHOLDER_ROLE_2',
    company: 'PLACEHOLDER_COMPANY_2',
    period: 'PLACEHOLDER_DATES_2',
    summary: 'PLACEHOLDER — impact, tools, results.',
  },
]

// Projects / featured work — the "show off" section.
export const projects = [
  {
    title: 'PLACEHOLDER_PROJECT',
    description: 'PLACEHOLDER — what it is, what you built, the outcome.',
    tags: ['Tag1', 'Tag2'],
    link: '',
  },
  {
    title: 'PLACEHOLDER_PROJECT_2',
    description: 'PLACEHOLDER — what it is, what you built, the outcome.',
    tags: ['Tag1', 'Tag2'],
    link: '',
  },
]

export const education = [
  {
    school: 'PLACEHOLDER_SCHOOL',
    degree: 'PLACEHOLDER_DEGREE',
    period: 'PLACEHOLDER_DATES',
  },
]
