/*
 * The door scene shared by slides 6 and 7: polished dossier vault on parchment
 * (right half), a hand-drawn bouncer, the devil bandit, a cheap paper form, a
 * quill, the door slot. Step-specific motion lives in vaultscene.css, keyed on
 * the slide's step classes (a-vault, a-signature, a-sign on slide 6; a-attack on 7).
 */
import { cx } from '../../components/bits';
import { Door } from '../../components/Door';
import story from '../../data/story.json';
import { rng, smooth, wobEllipse, wobLine } from './mix';
import './vaultscene.css';

const short = (a: string) => `${a.slice(0, 6)}…${a.slice(-4)}`;
export const FORM_TO = short(story.withdrawal.recipient);
export const FORM_AMOUNT = `${story.withdrawal.amountLamports.toLocaleString('en-US')} lamports`;

/** a scribbled signature: loops along a line, seeded so ours and the attacker's differ */
export function signaturePath(seed: number, w = 380, h = 70) {
  const r = rng(seed);
  const pts: [number, number][] = [];
  const n = 16;
  for (let i = 0; i <= n; i++) {
    const x = (i / n) * w + (r() - 0.5) * 14;
    const y = h / 2 + Math.sin(i * (1.3 + r() * 0.9)) * h * (0.25 + r() * 0.25) * (i % 3 === 1 ? -1 : 1);
    pts.push([x, y]);
  }
  return smooth(pts);
}

function Bouncer() {
  const s = 8;
  return (
    <svg className="vs-bouncer-svg" viewBox="0 0 240 470" width={240} height={470} aria-hidden="true">
      <g className="mkp vs-ink" strokeWidth={s}>
        <path d={wobEllipse(120, 62, 46, 50, 7, 1.06)} fill="#fff" />
        <path d={wobLine([40, 150], [200, 150], 4, 9, 4)} />
        <path d={`${wobLine([40, 150], [52, 330], 4, 11, 4)} ${wobLine([200, 150], [188, 330], 4, 13, 4)}`} />
        <path d={wobLine([52, 330], [188, 330], 3, 15, 4)} />
        <path d={wobLine([90, 330], [80, 460], 4, 17, 3)} />
        <path d={wobLine([150, 330], [160, 460], 4, 19, 3)} />
        <path d={wobLine([58, 200], [182, 230], 4, 21, 3)} />
        <path d={wobLine([182, 200], [58, 230], 4, 23, 3)} />
      </g>
      <rect x={82} y={48} width={34} height={18} rx={3} fill="#000" />
      <rect x={124} y={48} width={34} height={18} rx={3} fill="#000" />
      <path d="M116,56 h8" stroke="#000" strokeWidth={4} />
      <path d={wobLine([104, 92], [138, 90], 2, 25, 2)} className="mkp vs-ink" strokeWidth={5} />
      <text x={120} y={290} textAnchor="middle" fontFamily="Arial, Helvetica, sans-serif" fontWeight={700} fontSize={30} fill="#000">
        SECURITY
      </text>
      <g className="vs-wave">
        <path d={wobLine([196, 160], [232, 70], 3, 27, 3)} className="mkp vs-ink" strokeWidth={s} />
        <path d={wobEllipse(234, 60, 14, 14, 29, 1.05)} className="mkp vs-ink" strokeWidth={6} fill="#fff" />
      </g>
    </svg>
  );
}

export function Devil() {
  return (
    <svg className="vs-devil-svg" viewBox="0 0 200 430" width={200} height={430} aria-hidden="true">
      <path d="M48,70 Q30,30 26,4 Q60,26 76,52 Z" fill="#d00000" stroke="#000" strokeWidth={5} />
      <path d="M152,70 Q170,30 174,4 Q140,26 124,52 Z" fill="#d00000" stroke="#000" strokeWidth={5} />
      <circle cx={100} cy={120} r={70} fill="#ff2a2a" stroke="#000" strokeWidth={7} />
      <path d="M62,104 L88,116 M138,104 L112,116" stroke="#000" strokeWidth={7} strokeLinecap="round" />
      <circle cx={80} cy={124} r={7} fill="#000" />
      <circle cx={120} cy={124} r={7} fill="#000" />
      <path d="M66,152 Q100,182 134,152" fill="none" stroke="#000" strokeWidth={7} strokeLinecap="round" />
      <g fill="none" stroke="#d00000" strokeWidth={9} strokeLinecap="round">
        <path d="M100,190 L100,320" />
        <path d="M100,230 L40,290 M100,230 L168,270" />
        <path d="M100,320 L60,420 M100,320 L140,420" />
        <path d="M100,320 Q150,350 170,330 l10,-14 l2,22 z" />
      </g>
    </svg>
  );
}

export function Quill() {
  return (
    <svg className="vs-quill-svg" viewBox="0 0 120 200" width={120} height={200} aria-hidden="true">
      <path d="M10,196 C30,150 60,60 116,4 C96,70 70,140 18,196 Z" fill="#f4f1ea" stroke="#000" strokeWidth={4} strokeLinejoin="round" />
      <path d="M14,194 C46,140 80,70 112,10" fill="none" stroke="#000" strokeWidth={3} />
      <path d="M4,200 L14,180 L22,186 Z" fill="#000" />
    </svg>
  );
}

/** cheap paper form */
export function Form({ to, amount, sig, sigColor, className, children }: { to: string; amount: string; sig: number; sigColor: string; className?: string; children?: React.ReactNode }) {
  return (
    <div className={cx('vs-form', className)}>
      <div className="vs-f-h">WITHDRAWAL</div>
      <div className="vs-f-row vs-f-to">
        to: <b>{to}</b>
      </div>
      <div className="vs-f-row vs-f-amt">
        amount: <b>{amount}</b>
      </div>
      <div className="vs-f-row vs-f-sig">
        signature:
        <svg viewBox="-10 0 400 70" width={390} height={70} aria-hidden="true">
          <path className="vs-sigpath" d={signaturePath(sig)} pathLength={1} stroke={sigColor} />
        </svg>
      </div>
      {children}
    </div>
  );
}

/** parchment, the door, the slot and the shutter */
export function VaultDoor({ on, open, shut, className }: { on: boolean; open?: boolean; shut?: boolean; className?: string }) {
  return (
    <div className={cx('vs-wrap', on && 'on', open && 'open', shut && 'shut', className)}>
      <div className="vs-parch">
        <div className="paper mottle" />
        <div className="paper grain" />
        <div className="paper vig" />
      </div>
      <svg className="vs-split" viewBox="0 0 1920 1080" aria-hidden="true">
        <path d={wobLine([962, -10], [928, 1090], 5, 63, 7)} fill="none" stroke="#1c1a17" strokeWidth={3} />
      </svg>
      <div className="vs-interior" />
      <div className="vs-door">
        <Door className="door3" />
        <i className="vs-slot" />
        <i className="vs-shutter" />
      </div>
    </div>
  );
}

export { Bouncer };
