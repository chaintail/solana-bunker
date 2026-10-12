/* Vault door, front elevation: ported from the Pass B cover drawing. */
export function Door({ className }: { className?: string }) {
  const bolts = [];
  for (let k = 0; k < 36; k++) {
    const a = (k / 36) * Math.PI * 2;
    bolts.push(<circle key={k} cx={(320 + 243 * Math.cos(a)).toFixed(1)} cy={(330 + 243 * Math.sin(a)).toFixed(1)} r="2.6" />);
  }
  return (
    <svg className={className} viewBox="0 0 640 700" aria-hidden="true">
      <g fill="none" stroke="#1f3a93" strokeWidth="1.2">
        <line x1="40" y1="330" x2="600" y2="330" strokeDasharray="14 4 2 4" opacity=".55" />
        <line x1="320" y1="40" x2="320" y2="620" strokeDasharray="14 4 2 4" opacity=".55" />
        <circle cx="320" cy="330" r="250" />
        <circle cx="320" cy="330" r="236" />
        <circle cx="320" cy="330" r="176" />
        <circle cx="320" cy="330" r="168" opacity=".5" />
        <circle cx="320" cy="330" r="62" />
        <circle cx="320" cy="330" r="24" />
        <g className="door-wheel">
          <g id="hs">
            <line x1="320" y1="268" x2="320" y2="170" />
            <line x1="314" y1="268" x2="314" y2="176" opacity=".5" />
            <circle cx="320" cy="158" r="12" />
          </g>
          <use href="#hs" transform="rotate(120 320 330)" />
          <use href="#hs" transform="rotate(240 320 330)" />
        </g>
        <rect x="52" y="230" width="22" height="58" rx="3" />
        <rect x="52" y="372" width="22" height="58" rx="3" />
        <rect x="262" y="96" width="116" height="34" rx="2" />
        <line x1="70" y1="620" x2="570" y2="620" />
        <line x1="70" y1="610" x2="70" y2="630" />
        <line x1="570" y1="610" x2="570" y2="630" />
        <path d="M378,113 L470,70 L600,70" opacity=".8" />
        <path d="M344,330 L470,470 L600,470" opacity=".8" />
      </g>
      <g fill="#1f3a93">{bolts}</g>
      <g fontFamily="Courier Prime, monospace" fill="#1f3a93" fontSize="13" letterSpacing="2.2">
        <text x="470" y="62">A  ADDRESS PLATE</text>
        <text x="470" y="88" fill="#4c463d" letterSpacing="1">
          fixed
        </text>
        <text x="470" y="462">B  LOCK ASSEMBLY</text>
        <text x="470" y="488" fill="#4c463d" letterSpacing="1">
          replaceable
        </text>
        <text x="320" y="652" textAnchor="middle">
          DOOR, FRONT ELEVATION · NOT TO SCALE
        </text>
      </g>
    </svg>
  );
}

export function Coin({ kind, size = 56, className, style }: { kind: 'sol' | 'usdc'; size?: number; className?: string; style?: React.CSSProperties }) {
  return (
    <svg className={className} style={style} width={size} height={size} viewBox="0 0 60 60" aria-hidden="true">
      <use href={kind === 'sol' ? '#coin-sol' : '#coin-usdc'} />
    </svg>
  );
}
