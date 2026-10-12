import type { CSSProperties, ReactNode } from 'react';
import { Coin } from './Door';
import { cx, Pin, short } from './bits';
import story from '../data/story.json';

/* Shared vault rig for beats 4 to 7, ported from the mockup's scenes B and C. */

export const TREASURY = short(story.withdrawal.treasury, 8, 7);
export const DEST_A = '4Nd1sWq…Zq7e';
export const DEST_B = '9gHt3Rk…Vb2c';
export const SECRET_7 = ['3f9c41a0 7be2d915 c0e84f6a 29d3b710', '5ea8c6f4 127d9b3e 8a05c1f7 d64e2b93'];
export const SECRET_BAD = ['8b17e05c 44a9d2f1 9e3c7a08 b5d16f42', '0c7f93e1 6ad28b54 f1e0c937 2b8d46a5'];
export const SECRET_8 = ['e21b07c4 9a3f58d0 66c1b2e9 04f7a8d3', 'b95e0c21 7fd4a630 c8e2915b 3a06f7e4'];

export function Grid({ n = 1024, cls, className, style }: { n?: number; cls: (k: number) => string | undefined; className?: string; style?: CSSProperties }) {
  const items = [];
  for (let k = 0; k < n; k++) {
    const c = cls(k);
    items.push(<i key={k} className={c} />);
  }
  return (
    <div className={cx('cells', className)} style={style}>
      {items}
    </div>
  );
}

export function Treasury({ className, children }: { className?: string; children?: ReactNode }) {
  return (
    <>
      <Pin x={1078} y={286} addr={TREASURY} className="rig-pin" />
      <div className={cx('box treas', className)} style={{ left: 1080, top: 408 }}>
        <span className="lbl">Treasury · PDA</span>
        <svg className="door">
          <use href="#vault" />
        </svg>
        <div className="bal coins2">
          <Coin kind="sol" size={44} />
          <Coin kind="usdc" size={44} />
        </div>
        {children}
      </div>
    </>
  );
}

export function Dest({ id, label, addr, top, received, className }: { id: string; label: string; addr: string; top: number; received: ReactNode; className?: string }) {
  return (
    <div className={cx('box dest', className)} id={id} style={{ top }}>
      <span className="lbl">{label}</span>
      <div className="addr" style={{ marginTop: 22 }}>
        {addr}
      </div>
      <div className="rcv">received {received}</div>
    </div>
  );
}

export function TxCard({ id, className, head, right, rows, style }: { id?: string; className?: string; head: string; right: ReactNode; rows: [string, ReactNode, string?][]; style?: CSSProperties }) {
  return (
    <div className={cx('card', className)} id={id} style={style}>
      <div className="card-h">
        <span>{head}</span>
        <span>{right}</span>
      </div>
      <dl>
        {rows.map(([k, v, c]) => (
          <div key={k} style={{ display: 'contents' }}>
            <dt>{k}</dt>
            <dd className={c}>{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function Hex({ lines, className }: { lines: string[]; className?: string }) {
  return (
    <span className={cx('hexv', className)}>
      {lines[0]}
      <br />
      {lines[1]}
    </span>
  );
}
