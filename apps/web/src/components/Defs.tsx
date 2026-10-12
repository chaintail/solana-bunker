/* SVG filters, patterns, markers and symbols ported verbatim from the Pass B mockup. */
export function Defs() {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
      <defs>
        <filter id="ink" x="-8%" y="-12%" width="116%" height="124%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves={2} seed={4} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={5} xChannelSelector="R" yChannelSelector="G" result="rough" />
          <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves={2} seed={9} result="speck" />
          <feColorMatrix in="speck" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -4.2 2.95" result="speckA" />
          <feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves={3} seed={21} result="blot" />
          <feColorMatrix in="blot" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 2.4 -0.35" result="blotA" />
          <feComposite in="speckA" in2="blotA" operator="in" result="mask" />
          <feComposite in="rough" in2="mask" operator="in" />
        </filter>
        <filter id="inkbold" x="-6%" y="-12%" width="112%" height="124%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves={2} seed={6} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={7} xChannelSelector="R" yChannelSelector="G" result="rough" />
          <feTurbulence type="fractalNoise" baseFrequency="0.32" numOctaves={2} seed={13} result="speck" />
          <feColorMatrix in="speck" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -4.6 3.45" result="speckA" />
          <feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves={3} seed={2} result="blot" />
          <feColorMatrix in="blot" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 2.2 -0.1" result="blotA" />
          <feComposite in="speckA" in2="blotA" operator="in" result="mask" />
          <feComposite in="rough" in2="mask" operator="in" />
        </filter>
        <filter id="bar" x="-4%" y="-20%" width="108%" height="140%">
          <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves={2} seed={5} result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale={3.2} xChannelSelector="R" yChannelSelector="G" />
        </filter>
        <filter id="pen" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves={2} seed={11} result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale={2.4} xChannelSelector="R" yChannelSelector="G" />
        </filter>
        <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="7" stroke="#b3242a" strokeWidth="1.2" opacity=".32" />
        </pattern>
        <marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M1,1 L9,5 L1,9" fill="none" stroke="#1f3a93" strokeWidth="1.6" />
        </marker>
        <marker id="ahr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
          <path d="M1,1 L9,5 L1,9" fill="none" stroke="#b3242a" strokeWidth="1.6" />
        </marker>
        <symbol id="vault" viewBox="0 0 120 120">
          <g fill="none" stroke="#1f3a93" strokeWidth="1.3">
            <circle cx="60" cy="60" r="56" />
            <circle cx="60" cy="60" r="46" />
            <circle cx="60" cy="60" r="11" />
            <circle cx="60" cy="60" r="5" />
            <g id="spk">
              <line x1="60" y1="49" x2="60" y2="24" />
              <circle cx="60" cy="21" r="3.5" />
            </g>
            <use href="#spk" transform="rotate(120 60 60)" />
            <use href="#spk" transform="rotate(240 60 60)" />
            <line x1="2" y1="60" x2="14" y2="60" strokeDasharray="3 2" />
            <line x1="106" y1="60" x2="118" y2="60" strokeDasharray="3 2" />
          </g>
          <g fill="#1f3a93">
            <circle cx="60" cy="8.5" r="1.8" />
            <circle cx="60" cy="111.5" r="1.8" />
            <circle cx="8.5" cy="60" r="1.8" />
            <circle cx="111.5" cy="60" r="1.8" />
            <circle cx="96.4" cy="23.6" r="1.8" />
            <circle cx="23.6" cy="23.6" r="1.8" />
            <circle cx="96.4" cy="96.4" r="1.8" />
            <circle cx="23.6" cy="96.4" r="1.8" />
          </g>
        </symbol>
        <symbol id="agent" viewBox="0 0 112 124">
          <g fill="#1c1a17">
            <path d="M14,124 C15,92 32,78 56,78 C80,78 97,92 98,124 Z" />
            <path d="M56,78 L46,104 L56,124 L66,104 Z" fill="#f7f1e3" opacity=".9" />
            <circle cx="56" cy="56" r="17" />
            <path d="M37,40 C37,22 42,13 56,13 C70,13 75,22 75,40 Z" />
            <path d="M44,17 C50,22 62,22 68,17" stroke="#f7f1e3" strokeWidth="1.6" fill="none" opacity=".5" />
            <ellipse cx="56" cy="41" rx="34" ry="6" />
          </g>
        </symbol>
        <symbol id="coin-sol" viewBox="0 0 60 60">
          <g fill="none" stroke="#1f3a93" strokeWidth="1.6">
            <circle cx="30" cy="30" r="27" />
            <circle cx="30" cy="30" r="22.5" strokeWidth="1" strokeDasharray="2 2.4" />
            <path d="M20,21 H41 L37,25 H16 Z" />
            <path d="M16,28 H37 L41,32 H20 Z" />
            <path d="M20,35 H41 L37,39 H16 Z" />
          </g>
          <text x="30" y="50" textAnchor="middle" fontFamily="Courier Prime, monospace" fontSize="7.5" fontWeight="700" fill="#1f3a93" letterSpacing="1">SOL</text>
        </symbol>
        <symbol id="coin-usdc" viewBox="0 0 60 60">
          <g fill="none" stroke="#1f3a93" strokeWidth="1.6">
            <circle cx="30" cy="30" r="27" />
            <path d="M18,17 A17,17 0 0 0 18,43" strokeWidth="1.2" />
            <path d="M42,17 A17,17 0 0 1 42,43" strokeWidth="1.2" />
            <path d="M35,22.5 C33.5,20.5 26,19.8 25,23.8 C24,28 36,27.6 35.2,33 C34.4,37.6 26.4,37.4 24.6,34.6" />
            <line x1="30" y1="17.5" x2="30" y2="20.6" />
            <line x1="30" y1="37" x2="30" y2="40" />
          </g>
          <text x="30" y="52.5" textAnchor="middle" fontFamily="Courier Prime, monospace" fontSize="7" fontWeight="700" fill="#1f3a93" letterSpacing=".6">USDC</text>
        </symbol>
      </defs>
    </svg>
  );
}
