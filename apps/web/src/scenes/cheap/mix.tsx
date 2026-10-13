/* Shared pieces for the mixed slides: hand-drawn marker strokes (cheap) and
 * the glass magnifier (polished). Randomness is seeded so frames are stable. */
import { useEffect, useRef, type CSSProperties, type ReactNode } from 'react';
import { cx } from '../../components/bits';
import './mix.css';

export function rng(seed: number) {
  let s = seed >>> 0 || 1;
  return () => {
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    return ((s >>> 0) % 10000) / 10000;
  };
}

/** smooth path through points (Catmull-Rom to cubic Bezier) */
export function smooth(pts: [number, number][]) {
  if (pts.length < 2) return '';
  let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)],
      p1 = pts[i],
      p2 = pts[i + 1],
      p3 = pts[Math.min(pts.length - 1, i + 2)];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6],
      c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return d;
}

/** a wobbly line from a to b */
export function wobLine(a: [number, number], b: [number, number], amp: number, seed: number, n = 6) {
  const r = rng(seed);
  const pts: [number, number][] = [];
  const dx = b[0] - a[0],
    dy = b[1] - a[1],
    L = Math.hypot(dx, dy) || 1;
  const nx = -dy / L,
    ny = dx / L;
  for (let i = 0; i <= n; i++) {
    const t = i / n,
      o = i === 0 || i === n ? (r() - 0.5) * amp * 0.5 : (r() - 0.5) * 2 * amp;
    pts.push([a[0] + dx * t + nx * o, a[1] + dy * t + ny * o]);
  }
  return smooth(pts);
}

/** a hand-drawn loop around an ellipse that overshoots its start */
export function wobEllipse(cx0: number, cy0: number, rx: number, ry: number, seed: number, turns = 1.15) {
  const r = rng(seed);
  const pts: [number, number][] = [];
  const n = 22,
    a0 = -2.3;
  for (let i = 0; i <= n; i++) {
    const a = a0 + (i / n) * Math.PI * 2 * turns,
      k = 1 + (r() - 0.5) * 0.12 + (i / n) * 0.08;
    pts.push([cx0 + rx * k * Math.cos(a), cy0 + ry * k * Math.sin(a)]);
  }
  return smooth(pts);
}

/** MS Paint style arrow: wobbly shaft plus a two-stroke head, as one path list */
export function paintArrow(a: [number, number], b: [number, number], seed: number, head = 60, amp = 10) {
  const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
  const h = (s: number) => [b[0] - head * Math.cos(ang + s), b[1] - head * Math.sin(ang + s)] as [number, number];
  return [wobLine(a, b, amp, seed, 5), wobLine(b, h(0.5), 3, seed + 1, 2), wobLine(b, h(-0.5), 3, seed + 2, 2)];
}

/** red proofreading caret that inserts `word` at this point of an inline text line */
export function Ins({ on, word, className }: { on: boolean; word: string; className?: string }) {
  return (
    <span className={cx('ins', on && 'on', className)}>
      <svg viewBox="0 0 60 70" aria-hidden="true">
        <path d="M4,66 L31,6 L56,64" pathLength={1} />
      </svg>
      <b>{word}</b>
    </span>
  );
}

/**
 * The glass magnifier. `region` is the source-pixel rectangle shown, `img` is
 * placed at `origin` in source pixels; `children` draw in the same coordinates
 * (above the image when `over`, below it otherwise).
 */
export function Lens(props: {
  img: string;
  imgW: number;
  imgH: number;
  origin: [number, number];
  region: [number, number, number, number];
  width: number;
  x: number;
  y: number;
  className?: string;
  under?: ReactNode;
  over?: ReactNode;
  style?: CSSProperties;
}) {
  const [x0, y0, x1, y1] = props.region;
  const k = props.width / (x1 - x0);
  const h = (y1 - y0) * k;
  return (
    <div className={cx('lens', props.className)} style={{ left: props.x, top: props.y, width: props.width, height: h, ...props.style }}>
      <svg viewBox={`${x0} ${y0} ${x1 - x0} ${y1 - y0}`} width={props.width} height={h}>
        <rect x={x0} y={y0} width={x1 - x0} height={y1 - y0} fill="#fff" />
        <image href={props.img} x={props.origin[0]} y={props.origin[1]} width={props.imgW} height={props.imgH} />
        {props.over}
      </svg>
      <i className="lens-glass" />
    </div>
  );
}

/** hand-drawn highlighter strokes over text lines, in source pixels */
export function Highlights({ lines, seed, h = 64 }: { lines: [number, number, number][]; seed: number; h?: number }) {
  const r = rng(seed);
  return (
    <g className="hl-strokes">
      {lines.map(([xa, xb, y], i) => {
        const d = wobLine([xa - 8, y + 4 + (r() - 0.5) * 6], [xb + 10, y - 2 + (r() - 0.5) * 8], 4, seed + i * 7, 4);
        return <path key={i} d={d} pathLength={1} strokeWidth={h} style={{ ['--i' as string]: i }} />;
      })}
    </g>
  );
}

/** a number that ticks from `from` to `to` when `run` turns on (instant: jump straight to `to`) */
export function Tick({ from, to, run, instant, ms = 1600, delay = 300 }: { from: number; to: number; run: boolean; instant: boolean; ms?: number; delay?: number }) {
  const el = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const set = (v: number) => el.current && (el.current.textContent = Math.round(v).toLocaleString('en-US'));
    if (!run) return void set(from);
    if (instant) return void set(to);
    let raf = 0;
    const t0 = performance.now() + delay;
    const tick = (now: number) => {
      const t = Math.min(1, Math.max(0, (now - t0) / ms));
      set(from + (to - from) * (1 - Math.pow(1 - t, 3)));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [from, to, run, instant, ms, delay]);
  return <span ref={el}>{from.toLocaleString('en-US')}</span>;
}
