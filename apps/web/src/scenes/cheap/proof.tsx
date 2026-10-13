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
// Solscan opens mainnet unless told otherwise, so devnet links keep ?cluster=devnet
const txUrl = (sig: string) => `https://solscan.io/tx/${sig}?cluster=devnet`;
/* lowest error correction uqr offers, no logo overlay: verified to decode with OpenCV's standard detector at 1080p and 720p */
const ECC = 'L' as const;
const LOGO = false;
const LOGO_AREA = 0.06;

const GITHUB =
  'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12';

export type LogoKind = 'github' | 'solscan' | 'telegram';

/** Telegram: blue disc, white paper plane (24 grid) */
function TelegramMark() {
  return (
    <g>
      <circle cx={12} cy={12} r={12} fill="#229ed9" />
      <path d="M5.3,11.7 L17.4,7.0 C18.0,6.8 18.5,7.1 18.3,7.9 L16.3,17.2 C16.2,17.8 15.7,18.0 15.2,17.7 L12.1,15.4 L10.6,16.8 C10.4,17.0 10.3,17.1 10.0,17.1 L10.2,13.9 L15.9,8.8 C16.2,8.6 15.8,8.5 15.5,8.7 L8.5,13.1 L5.4,12.2 C4.8,12.0 4.8,11.8 5.3,11.7 Z" fill="#fff" />
    </g>
  );
}

export function LogoMark({ kind }: { kind: LogoKind }) {
  return kind === 'github' ? <GithubMark /> : kind === 'solscan' ? <SolscanMark /> : <TelegramMark />;
}

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

/**
 * QR with an optional logo knocked out of the centre. Whole pixels per module,
 * 4-module quiet zone; `logoArea` is the share of the symbol the logo may cover.
 */
export function QR({ text, size: max, ecc, logo, logoArea = 0.06, dark = '#000', light = '#fff' }: { text: string; size: number; ecc: 'L' | 'M' | 'Q' | 'H'; logo?: LogoKind; logoArea?: number; dark?: string; light?: string }) {
  const { n, d } = qr(text, ecc);
  const q = 4; // quiet zone, modules
  const size = Math.floor(max / (n + 2 * q)) * (n + 2 * q);
  const L = Math.round(n * Math.sqrt(logoArea)); // logo box side, modules
  const c0 = Math.round((n - L) / 2);
  return (
    <svg className="pf-qr" viewBox={`${-q} ${-q} ${n + 2 * q} ${n + 2 * q}`} width={size} height={size} shapeRendering="crispEdges" aria-hidden="true">
      <rect x={-q} y={-q} width={n + 2 * q} height={n + 2 * q} fill={light} />
      <path d={d} fill={dark} />
      {logo && (
        <g>
          <rect x={c0} y={c0} width={L} height={L} fill={light} />
          <g transform={`translate(${c0 + 0.5},${c0 + 0.5}) scale(${(L - 1) / 24})`} shapeRendering="auto">
            <LogoMark kind={logo} />
          </g>
        </g>
      )}
    </svg>
  );
}

/** the logos sit beside the headings: on top of the codes they stopped low-ECC codes decoding */
function Mark({ kind }: { kind: LogoKind }) {
  return (
    <svg className="pf-mark" viewBox="0 0 24 24" aria-hidden="true">
      <LogoMark kind={kind} />
    </svg>
  );
}

export function ProofColumn({ on, version, staged = false, className }: { on: boolean; version: Version; staged?: boolean; className?: string }) {
  const v = V[version];
  return (
    <div className={cx('proof', on && 'on', className)} data-version={version}>
      <div className="pf-box">
        <div className="pf-h">
          <Mark kind="github" /> see the code
        </div>
        <QR text={v.code} size={246} ecc={ECC} logo={LOGO ? 'github' : undefined} logoArea={LOGO_AREA} />
        <div className="pf-t">program/src/lib.rs line {v.line}</div>
        <QR text={SOLSCAN_PROGRAM} size={226} ecc={ECC} />
        <div className="pf-s">
          <Mark kind="solscan" /> on Solscan
        </div>
      </div>
      <div className={cx('pf-slot', staged && 'staged')}>
        <div className="pf-box pf-qrbox">
          <div className="pf-h">
            <Mark kind="solscan" /> proof it works
          </div>
          <QR text={txUrl(v.tx)} size={246} ecc={ECC} logo={LOGO ? 'solscan' : undefined} logoArea={LOGO_AREA} />
          <div className="pf-t">devnet tx {v.tx.slice(0, 8)}…</div>
        </div>
        {/* staged transport (003-a): measured on a local test validator only, so no devnet transaction to point at */}
        <div className="pf-box pf-staged">
          <div className="pf-h">proof it works</div>
          <div className="pf-st">
            5 transactions,
            <br />
            local test validator
          </div>
        </div>
      </div>
    </div>
  );
}

/** a single link box in the same column style: heading with a mark, QR, the file and line under it */
export function LinkBox({ title, url, text, mark = 'github' }: { title: string; url: string; text: string; mark?: LogoKind }) {
  return (
    <div className="pf-box">
      <div className="pf-h">
        <Mark kind={mark} /> {title}
      </div>
      <QR text={url} size={246} ecc={ECC} />
      <div className="pf-t">{text}</div>
    </div>
  );
}

export function LinkColumn({ on, children }: { on: boolean; children: React.ReactNode }) {
  return <div className={cx('proof', on && 'on')}>{children}</div>;
}
