/*
 * "see the code" and "proof it works": the top-right column shown whenever a
 * Bunker Program version is on screen. Links are Liam's, verbatim; the
 * signatures are the confirmed devnet withdrawals in artifacts/public-deployment.json.
 */
import { encode } from 'uqr';
import { cx } from '../../components/bits';
import './proof.css';

export type Version = '001' | '002' | '003';

const SOLSCAN_PROGRAM = 'https://solscan.io/account/HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V?cluster=devnet';
const V: Record<Version, { code: string; line: number; tx: string }> = {
  '001': {
    code: 'https://github.com/chaintail/solana-bunker/blob/main/program/src/lib.rs#L113',
    line: 113,
    tx: '5mHxtbGLuEhxVCDhRRc6A1pdpQzn3KgQyfvzSoUS4GzySBZ2AkDJQgKbwb3UrNaZ4rMEzJ2syQb3yvWw35TMhwjr',
  },
  '002': {
    code: 'https://github.com/chaintail/solana-bunker/blob/main/program/src/lib.rs#L114',
    line: 114,
    tx: '5XPHXjBKRvZJ5vNkEqDF5TXtk88ZZd96R92MuSxf7uAYRXTVER6AnYgDyqZoqEMe8Tn8zwez3hSRme1VZv9BaKBw',
  },
  '003': {
    code: 'https://github.com/chaintail/solana-bunker/blob/main/program/src/lib.rs#L118',
    line: 118,
    tx: 'CiZmcGsaX4G7upT1ECscLUr1vVrX1htShX4Q2y8K4wd1hJcsVpfZEQc9GZtod8MxVSmP4Hy6mbVqiM75QiAJdBM',
  },
};
const txUrl = (sig: string) => `https://solscan.io/tx/${sig}?cluster=devnet`;

const GITHUB =
  'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12';

function GithubMark() {
  return <path d={GITHUB} fill="#000" />;
}
/** the Solscan mark (teal ring open at the lower right, purple dot), drawn on a 24 grid */
function SolscanMark() {
  return (
    <g>
      <path d="M19.9,18.4 A9.6,9.6 0 1 1 21.4,14.2" fill="none" stroke="#00e8b5" strokeWidth={4.8} strokeLinecap="butt" />
      <circle cx={12} cy={10.6} r={4.9} fill="#c74ae3" />
    </g>
  );
}

const cache = new Map<string, { n: number; d: string }>();
function qr(text: string, ecc: 'L' | 'M' | 'Q' | 'H') {
  const key = ecc + text;
  let v = cache.get(key);
  if (!v) {
    const r = encode(text, { ecc, border: 0 });
    let d = '';
    r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`)));
    v = { n: r.size, d };
    cache.set(key, v);
  }
  return v;
}

/** QR with an optional logo knocked out of the centre (quiet zone included in the drawing) */
function QR({ text, size: max, ecc, logo }: { text: string; size: number; ecc: 'L' | 'M' | 'Q' | 'H'; logo?: 'github' | 'solscan' }) {
  const { n, d } = qr(text, ecc);
  const q = 2; // quiet zone, modules
  const size = Math.floor(max / (n + 2 * q)) * (n + 2 * q); // whole pixels per module, so screens render it sharp
  const L = n * 0.24; // logo box, modules
  const c = n / 2;
  return (
    <svg className="qr" viewBox={`${-q} ${-q} ${n + 2 * q} ${n + 2 * q}`} width={size} height={size} shapeRendering="crispEdges" aria-hidden="true">
      <rect x={-q} y={-q} width={n + 2 * q} height={n + 2 * q} fill="#fff" />
      <path d={d} fill="#000" />
      {logo && (
        <g>
          <rect x={c - L / 2 - 0.6} y={c - L / 2 - 0.6} width={L + 1.2} height={L + 1.2} rx={1} fill="#fff" shapeRendering="auto" />
          <g transform={`translate(${c - L / 2},${c - L / 2}) scale(${L / 24})`} shapeRendering="auto">
            {logo === 'github' ? <GithubMark /> : <SolscanMark />}
          </g>
        </g>
      )}
    </svg>
  );
}

export function ProofColumn({ on, version, className }: { on: boolean; version: Version; className?: string }) {
  const v = V[version];
  return (
    <div className={cx('proof', on && 'on', className)} data-version={version}>
      <div className="pf-box">
        <div className="pf-h">see the code</div>
        <QR text={v.code} size={244} ecc="Q" logo="github" />
        <div className="pf-t">program/src/lib.rs line {v.line}</div>
        <div className="pf-row">
          <QR text={SOLSCAN_PROGRAM} size={130} ecc="L" />
          <span>on Solscan</span>
        </div>
      </div>
      <div className="pf-box">
        <div className="pf-h">proof it works</div>
        <QR text={txUrl(v.tx)} size={244} ecc="Q" logo="solscan" />
        <div className="pf-t">devnet tx {v.tx.slice(0, 8)}…</div>
      </div>
    </div>
  );
}
