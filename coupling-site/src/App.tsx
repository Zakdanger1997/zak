function Logo() {
  return (
    <svg width="18" height="18" viewBox="0 0 256 256" fill="none">
      <path fill="rgb(84, 84, 84)" d="REPLACE_WITH_YOUR_LOGO_PATH" />
    </svg>
  )
}

const navLinks = ['About', 'Products', 'Applications', 'Contact']

export default function App() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f0f0ee]">
      {/* Fullscreen background video */}
      <video
        className="absolute inset-0 w-full h-full object-cover"
        src="REPLACE_WITH_YOUR_COUPLING_VIDEO_URL"
        autoPlay
        muted
        loop
        playsInline
      />

      {/* Foreground content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Navbar */}
        <nav className="flex items-center justify-center pt-4 sm:pt-6 px-4 sm:px-8 gap-2 sm:gap-3">
          <div
            className="flex items-center justify-center rounded-full w-10 h-10 sm:w-11 sm:h-11 shrink-0"
            style={{ backgroundColor: '#EDEDED' }}
          >
            <Logo />
          </div>
          <div
            className="flex items-center gap-4 sm:gap-10 rounded-xl px-4 sm:px-8 py-2.5 sm:py-3"
            style={{ backgroundColor: '#EDEDED' }}
          >
            {navLinks.map((link) => (
              <a
                key={link}
                href="#"
                className="text-[12px] sm:text-[14px] font-medium text-gray-700 hover:text-gray-900 transition-colors duration-200"
              >
                {link}
              </a>
            ))}
          </div>
        </nav>

        {/* Hero content (bottom-left) */}
        <div className="flex-1 flex items-end pb-10 sm:pb-16 lg:pb-20 px-6 sm:px-12 md:px-20 lg:px-28">
          <div className="max-w-xs">
            <a
              href="#"
              className="inline-flex items-center gap-1.5 text-[11.5px] font-medium text-blue-500 hover:text-blue-600 transition-colors mb-3 group"
            >
              Trusted by industrial plants worldwide
              <span className="inline-block transition-transform duration-200 group-hover:translate-x-0.5">
                →
              </span>
            </a>

            <h1 className="text-[1.5rem] sm:text-[1.75rem] leading-[1.15] font-medium text-gray-900 tracking-tight mb-3">
              Reliable, precision couplings built to keep your machines running.
            </h1>

            <p className="text-[13px] text-gray-400 font-normal mb-3">
              Power transmission you can count on.
            </p>

            <a
              href="#"
              className="inline-flex items-center gap-2 text-[13px] font-medium text-blue-500 border border-blue-400 rounded-full px-5 py-2.5 hover:bg-blue-500 hover:text-white hover:border-blue-500 transition-all duration-200 group"
            >
              Request a free quote
              <span className="transition-transform duration-200 group-hover:translate-x-0.5">
                →
              </span>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
