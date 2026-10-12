import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from 'react';

export const cx = (...a: (string | false | null | undefined)[]) => a.filter(Boolean).join(' ');

export function Header({ exhibit, title, sheet }: { exhibit: string; title: string; sheet: string }) {
  return (
    <div className="hdr">
      <div>
        <b>Solana Bunker</b>
        <span className="sep">/</span>
        {exhibit}
        <span className="sep">/</span>
        {title}
      </div>
      <div>{sheet}</div>
    </div>
  );
}

const SHAKE: Keyframe[] = [
  { transform: 'translate(0,0)' },
  { transform: 'translate(2px,-1.5px)' },
  { transform: 'translate(-1.5px,1px)' },
  { transform: 'translate(.5px,0)' },
  { transform: 'translate(0,0)' },
];

export function Stamp(props: {
  on: boolean;
  instant: boolean;
  x: number;
  y: number;
  size: number;
  r?: number;
  d?: number;
  bold?: boolean;
  shake?: boolean;
  className?: string;
  style?: CSSProperties;
  children: ReactNode;
}) {
  const { on, instant, x, y, size, r = -6, d = 0, bold, shake = true } = props;
  const ref = useRef<HTMLDivElement>(null);
  const inst = useRef(instant);
  inst.current = instant;
  useEffect(() => {
    if (!on || inst.current || !shake) return;
    const t = setTimeout(() => {
      const c = ref.current?.closest('.content') as HTMLElement | null;
      c?.animate(SHAKE, { duration: 170, easing: 'linear' });
    }, d + 230);
    return () => clearTimeout(t);
  }, [on, d, shake]);
  return (
    <div
      ref={ref}
      className={cx('stamp', on && 'on', bold && 'bold', props.className)}
      style={{ left: x, top: y, fontSize: size, ['--r' as string]: `${r}deg`, ['--d' as string]: `${d}ms`, ...props.style }}
    >
      {props.children}
    </div>
  );
}

/** pinned address tag (mockup #pin) */
export function Pin({ x, y, label = 'Treasury address · PDA', addr, style, className }: { x: number; y: number; label?: string; addr: string; style?: CSSProperties; className?: string }) {
  return (
    <div className={cx('pin', className)} style={{ left: x, top: y, ...style }}>
      <div className="tagp">
        <div className="lbl">{label}</div>
        <div className="addr">{addr}</div>
      </div>
      <div className="tack" />
    </div>
  );
}

/** a value that swaps by state: renders each option, the active one slides in */
export function Swap({ value, options, d = 0 }: { value: number; options: ReactNode[]; d?: number }) {
  return (
    <span className="sw">
      {options.map((o, i) => (
        <span key={i} className={i === value ? 'up' : i < value ? 'gone' : ''} style={{ ['--d' as string]: `${d}ms` }}>
          {o}
        </span>
      ))}
    </span>
  );
}

/** number that counts between two values when `on` flips (instant jumps) */
export function Counter({ on, from, to, instant, ms = 900, delay = 0, fmt = (n: number) => Math.round(n).toLocaleString('en-US') }: { on: boolean; from: number; to: number; instant: boolean; ms?: number; delay?: number; fmt?: (n: number) => string }) {
  const [v, setV] = useState(on ? to : from);
  const inst = useRef(instant);
  inst.current = instant;
  useEffect(() => {
    const target = on ? to : from;
    if (inst.current) {
      setV(target);
      return;
    }
    const start = on ? from : to;
    let raf = 0;
    const t0 = performance.now() + delay;
    const tick = (t: number) => {
      const k = Math.min(1, Math.max(0, (t - t0) / ms));
      const e = 1 - Math.pow(1 - k, 3);
      setV(start + (target - start) * e);
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [on, from, to, ms, delay]);
  return <>{fmt(v)}</>;
}

export function short(addr: string, a = 4, b = 4) {
  return `${addr.slice(0, a)}…${addr.slice(-b)}`;
}

export const explorerTx = (sig: string) => `https://explorer.solana.com/tx/${sig}?cluster=devnet`;
export const explorerAddr = (a: string) => `https://explorer.solana.com/address/${a}?cluster=devnet`;

/** cheap deck stamp: plain red outlined box, nearly horizontal, no ink filter */
export function CStamp({ on, x, y, size, r = -1.5, d = 0, className, children }: { on: boolean; x: number; y: number; size: number; r?: number; d?: number; className?: string; children: ReactNode }) {
  return (
    <div className={cx('cstamp', on && 'on', className)} style={{ left: x, top: y, fontSize: size, ['--r' as string]: `${r}deg`, ['--d' as string]: `${d}ms` }}>
      {children}
    </div>
  );
}
