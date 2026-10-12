/* clip-art for the cheap deck: deliberately plain shapes */
import type { CSSProperties } from 'react';

export function Vault({ size = 300, style, className }: { size?: number; style?: CSSProperties; className?: string }) {
  return (
    <svg className={className} style={style} width={size} height={size} viewBox="0 0 200 200" aria-hidden="true">
      <rect x={8} y={8} width={184} height={184} rx={14} fill="#c8c8c8" stroke="#000" strokeWidth={6} />
      <circle cx={100} cy={100} r={66} fill="#e6e6e6" stroke="#000" strokeWidth={6} />
      <circle className="wheel" cx={100} cy={100} r={14} fill="#000" />
      <g className="wheel" stroke="#000" strokeWidth={8} strokeLinecap="round">
        <line x1={100} y1={100} x2={100} y2={50} />
        <line x1={100} y1={100} x2={143} y2={125} />
        <line x1={100} y1={100} x2={57} y2={125} />
      </g>
      <rect x={176} y={70} width={12} height={60} fill="#000" />
    </svg>
  );
}

export function Coin({ kind, size = 110 }: { kind: 'SOL' | 'USDC'; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden="true">
      <circle cx={50} cy={50} r={46} fill={kind === 'SOL' ? '#ffd700' : '#3d7bff'} stroke="#000" strokeWidth={5} />
      <circle cx={50} cy={50} r={36} fill="none" stroke="#000" strokeWidth={2} strokeDasharray="4 4" />
      <text x={50} y={kind === 'SOL' ? 62 : 60} textAnchor="middle" fontFamily="Arial, Helvetica, sans-serif" fontWeight={700} fontSize={kind === 'SOL' ? 32 : 26} fill={kind === 'SOL' ? '#000' : '#fff'}>
        {kind}
      </text>
    </svg>
  );
}

/** cartoon robber: hat, mask, stripes */
export function Robber({ size = 200, style, className }: { size?: number; style?: CSSProperties; className?: string }) {
  return (
    <svg className={className} style={style} width={size} height={size * 1.2} viewBox="0 0 200 240" aria-hidden="true">
      <path d="M30,240 C34,180 64,160 100,160 C136,160 166,180 170,240 Z" fill="#fff" stroke="#000" strokeWidth={5} />
      <path d="M40,200 H160 M36,222 H164" stroke="#000" strokeWidth={10} />
      <circle cx={100} cy={110} r={52} fill="#f2c9a0" stroke="#000" strokeWidth={5} />
      <rect x={46} y={92} width={108} height={30} fill="#000" />
      <circle cx={78} cy={107} r={8} fill="#fff" />
      <circle cx={122} cy={107} r={8} fill="#fff" />
      <path d="M84,140 Q100,150 116,140" fill="none" stroke="#000" strokeWidth={4} />
      <rect x={52} y={36} width={96} height={40} fill="#000" />
      <rect x={28} y={70} width={144} height={14} rx={4} fill="#000" />
    </svg>
  );
}

export function Grid({ n = 1024, cols = 32, cell = 14, gap = 3, mark }: { n?: number; cols?: number; cell?: number; gap?: number; mark: (k: number) => string | undefined }) {
  const items = [];
  for (let k = 0; k < n; k++) items.push(<i key={k} className={mark(k)} />);
  return (
    <div className="cgrid" style={{ gridTemplateColumns: `repeat(${cols}, ${cell}px)`, gridAutoRows: `${cell}px`, gap }}>
      {items}
    </div>
  );
}
