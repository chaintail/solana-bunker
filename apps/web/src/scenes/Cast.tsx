import type { ReactNode } from 'react';
import { cx } from '../components/bits';

/* Technical route: the cast of concepts, pinned like specimen cards. */
const B = '#1f3a93';
const g = (c: ReactNode) => (
  <svg viewBox="0 0 220 110" className="spec-art" aria-hidden="true">
    <g fill="none" stroke={B} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      {c}
    </g>
  </svg>
);

const CAST: { name: string; def: string; art: ReactNode }[] = [
  {
    name: 'Public key',
    def: 'The half of a keypair you show the world.',
    art: g(
      <>
        <circle cx="70" cy="55" r="22" />
        <circle cx="70" cy="55" r="8" />
        <path d="M92,55 H170 M150,55 V72 M162,55 V68" />
      </>,
    ),
  },
  {
    name: 'Elliptic curve',
    def: 'Ed25519 on Solana, secp256k1 on Ethereum.',
    art: g(
      <>
        <path d="M20,55 H200 M110,8 V102" strokeDasharray="3 4" opacity=".5" />
        <path d="M150,8 C118,30 92,40 92,55 C92,70 118,80 150,102" />
        <path d="M62,55 C62,40 76,34 84,40 C90,45 90,65 84,70 C76,76 62,70 62,55 Z" />
        <circle cx="128" cy="25" r="3.5" fill={B} />
        <circle cx="96" cy="70" r="3.5" fill={B} />
      </>,
    ),
  },
  {
    name: 'Hash function',
    def: 'SHA-256: any input, 32 bytes out, no way back.',
    art: g(
      <>
        <path d="M20,30 H70 M20,55 H70 M20,80 H70" />
        <rect x="74" y="22" width="72" height="66" />
        <text x="110" y="61" textAnchor="middle" fontFamily="Courier Prime, monospace" fontSize="15" fill={B} stroke="none">H</text>
        <path d="M146,55 H198" />
        <path d="M190,49 L198,55 L190,61" />
      </>,
    ),
  },
  {
    name: 'Preimage and digest',
    def: 'The secret, and its fingerprint.',
    art: g(
      <>
        <rect x="18" y="38" width="64" height="34" strokeDasharray="4 3" />
        <text x="50" y="60" textAnchor="middle" fontFamily="Courier Prime, monospace" fontSize="14" fill={B} stroke="none">x</text>
        <path d="M86,55 H130 M122,49 L130,55 L122,61" />
        <rect x="136" y="38" width="66" height="34" />
        <text x="169" y="60" textAnchor="middle" fontFamily="Courier Prime, monospace" fontSize="14" fill={B} stroke="none">H(x)</text>
      </>,
    ),
  },
  {
    name: 'Program derived address',
    def: 'An address off the curve. No private key exists.',
    art: g(
      <>
        <path d="M30,96 C60,90 80,20 110,20 C140,20 160,90 190,96" />
        <circle cx="110" cy="74" r="6" />
        <path d="M104,68 L116,80 M116,68 L104,80" stroke="#b3242a" />
        <path d="M130,74 H190" strokeDasharray="3 4" />
      </>,
    ),
  },
  {
    name: 'Merkle tree',
    def: 'Many hashes folded into one root.',
    art: g(
      <>
        <circle cx="110" cy="16" r="6" fill={B} />
        <path d="M110,22 L66,50 M110,22 L154,50" />
        <circle cx="66" cy="54" r="5" />
        <circle cx="154" cy="54" r="5" />
        <path d="M66,59 L44,88 M66,59 L88,88 M154,59 L132,88 M154,59 L176,88" />
        <rect x="38" y="88" width="12" height="12" />
        <rect x="82" y="88" width="12" height="12" />
        <rect x="126" y="88" width="12" height="12" />
        <rect x="170" y="88" width="12" height="12" />
      </>,
    ),
  },
  {
    name: 'One-time signature',
    def: 'Sign once with a key, then retire it.',
    art: g(
      <>
        <path d="M24,74 C44,30 58,92 78,52 C90,30 98,80 116,58" />
        <path d="M20,88 H130" />
        <rect x="148" y="34" width="52" height="46" />
        <path d="M152,38 L196,76 M196,38 L152,76" stroke="#b3242a" />
      </>,
    ),
  },
];

export function Cast({ on }: { on: boolean }) {
  return (
    <div className={cx('cast', on && 'go')}>
      <div className="cast-h">
        <span className="lbl">Technical file · cast of characters</span>
      </div>
      {CAST.map((c, i) => (
        <div className="spec" key={c.name} style={{ ['--i' as string]: i }}>
          <i className="tack" />
          <span className="lbl">Specimen {String(i + 1).padStart(2, '0')}</span>
          {c.art}
          <b>{c.name}</b>
          <span className="def">{c.def}</span>
        </div>
      ))}
    </div>
  );
}
