import { useEffect, useRef } from 'react';
import { cx } from '../../components/bits';
import { Door } from '../../components/Door';
import type { SceneDef, SceneProps } from '../../types';
import { Vault } from './clip';
import { EO_PHOTO } from './eo-photo';
import { rng, smooth, wobLine } from './mix';
import './c3.css';

/* hand-drawn elliptic curve y^2 = x^3 - 2x + 2, plus a point that is not on it */
const CURVE = (() => {
  const r = rng(91);
  const ox = 1200,
    oy = 770,
    sx = 104,
    sy = 74;
  const up: [number, number][] = [],
    lo: [number, number][] = [];
  const root = -1.7693;
  for (let i = 0; i <= 14; i++) {
    const x = root + ((2.05 - root) * i) / 14;
    const y = Math.sqrt(Math.max(0, x * x * x - 2 * x + 2));
    const j = () => (r() - 0.5) * 6;
    up.push([ox + x * sx + j(), oy - y * sy + j()]);
    lo.push([ox + x * sx + j(), oy + y * sy + j()]);
  }
  return smooth([...up.reverse(), ...lo.slice(1)]);
})();

const SPLIT = wobLine([982, -10], [944, 1090], 5, 61, 7);

/* the polished odometer: real carry behaviour, keeps ticking while shown */
const DIGITS = 7;
function Odometer({ run }: { run: boolean }) {
  const drums = useRef<(HTMLSpanElement | null)[]>([]);
  useEffect(() => {
    const set = (v: number) => {
      for (let i = 0; i < DIGITS; i++) {
        const p = 10 ** i;
        const d = Math.floor(v / p) % 10;
        const frac = i === 0 ? v % 1 : Math.max(0, (v % p) - (p - 1));
        const el = drums.current[DIGITS - 1 - i];
        if (el) el.style.transform = `translateY(${-(d + frac) * 10}%)`;
      }
    };
    if (!run) {
      set(0);
      return;
    }
    let raf = 0;
    const t0 = performance.now();
    const tick = (now: number) => {
      const t = (now - t0) / 1000;
      set(2.6e6 * (1 - Math.exp(-t / 1.8)) + 1500 * t);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [run]);
  const cells = [];
  for (let k = 0; k < DIGITS; k++) {
    if (k === 1 || k === 4) cells.push(<i key={`s${k}`} className="odo-sep">,</i>);
    cells.push(
      <span key={k} className="odo-win">
        <span className="odo-drum" ref={(el) => void (drums.current[k] = el)}>
          {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map((n, j) => (
            <b key={j}>{n}</b>
          ))}
        </span>
      </span>,
    );
  }
  return (
    <div className="odo">
      <div className="odo-face">{cells}</div>
    </div>
  );
}

function VoiceNote({ seed, d }: { seed: number; d: number }) {
  const r = rng(seed);
  const bars = Array.from({ length: 20 }, () => 8 + Math.round(r() * 30));
  return (
    <div className="vn" style={{ ['--d' as string]: `${d}ms` }}>
      <svg viewBox="0 0 270 72" width={270} height={72} aria-hidden="true">
        <circle cx={38} cy={36} r={26} fill="#3390ec" />
        <polygon points="31,22 31,50 54,36" fill="#fff" />
        {bars.map((h, i) => (
          <rect key={i} x={80 + i * 9} y={36 - h / 2} width={5} height={h} fill={i < 7 ? '#3390ec' : '#9cc3ea'} />
        ))}
      </svg>
    </div>
  );
}

function Bunker({ at, cur, active }: SceneProps) {
  const pda = at('pda') && !at('eo');
  const eo = at('eo') && !at('tokens');
  const tokens = at('tokens') && !at('three');
  const three = at('three');
  return (
    <>
      {/* left half: parchment and the polished vault */}
      <div className="c3-parch">
        <div className="paper mottle" />
        <div className="paper grain" />
        <div className="paper vig" />
      </div>
      <svg className="c3-svg" viewBox="0 0 1920 1080" aria-hidden="true">
        <path d={SPLIT} fill="none" stroke="#1c1a17" strokeWidth={3} />
      </svg>
      <h2 className="c3-hl">The Solana Bunker</h2>
      <div className={cx('c3-door', three && 'moved')}>
        <Door className="door3" />
      </div>

      {/* right half, cheap: PDA and the curve */}
      <div className={cx('c3-pda', pda && 'on')}>
        <div className="c3-pda-big">PDA</div>
        <div className="c3-pda-sub">program derived address</div>
        <svg className="c3-svg" viewBox="0 0 1920 1080" aria-hidden="true">
          <path className="c3-curve draw1" d={CURVE} pathLength={1} />
          <circle className="c3-dot" cx={1690} cy={610} r={20} />
        </svg>
        <div className="mk c3-off">
          not on
          <br />
          the curve
        </div>
      </div>

      {/* the executive order */}
      <div className={cx('c3-eo', eo && 'on')}>
        <div className="c3-photo">{EO_PHOTO && <img src={EO_PHOTO} alt="Executive Order 14365 signing" draggable={false} />}</div>
        <div className="c3-cap">
          <div className="c3-cap1">Executive Order 14365,</div>
          <div className="c3-cap1">September 29, 2026:</div>
          <div className="c3-cap2">
            <span className="c3-art">
              Artificial
              <svg viewBox="0 0 300 80" preserveAspectRatio="none" aria-hidden="true" className={cx('c3-strike', at('super') && 'on')}>
                <path d="M-6,46 C60,38 150,44 306,34" />
              </svg>
              <span className={cx('cstamp c3-super', at('super') && 'on')}>SUPER</span>
            </span>{' '}
            Intelligence
          </div>
          <div className="c3-cap3">renamed Super Intelligence in federal documents</div>
        </div>
      </div>

      {/* tokens and voice notes */}
      <div className={cx('c3-tok', tokens && 'on')}>
        <Odometer run={tokens && active && cur === 'tokens'} />
        <div className="c3-tok-l">tokens</div>
        <div className="c3-vns">
          {[0, 1, 2, 3, 4, 5, 6].map((k) => (
            <VoiceNote key={k} seed={300 + k} d={250 + k * 170} />
          ))}
        </div>
        <div className="c3-vn-l">voice notes</div>
      </div>

      {/* built three times */}
      <div className={cx('c3-three', three && 'on')}>
        <div className="c3-3t">We built it three times</div>
        <Vault size={240} className="c3-v1" />
        <Vault size={240} className="c3-v2" />
        <div className="c3-vl" style={{ left: 1030 }}>
          V1
        </div>
        <div className="c3-vl" style={{ left: 1320 }}>
          V2
        </div>
        <div className="c3-vl" style={{ left: 1610 }}>
          V3
        </div>
      </div>
    </>
  );
}

export const C3: SceneDef = {
  key: 'c-bunker',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'vault' }, { id: 'pda' }, { id: 'eo' }, { id: 'super' }, { id: 'tokens' }, { id: 'three' }],
  C: Bunker,
};
