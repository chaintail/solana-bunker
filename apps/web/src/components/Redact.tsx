import { useState, type CSSProperties } from 'react';
import { FORMULAS, type FormulaId } from '../formulas';
import { cx } from './bits';

/**
 * Explore mode: a black redaction bar over an equation. Click it to unredact
 * the real definition with a link to its standard.
 */
export function Redact({ eq, w, h = 24, style, className, align = 'left', drop = 'down' }: { eq: FormulaId; w: number; h?: number; style?: CSSProperties; className?: string; align?: 'left' | 'right'; drop?: 'down' | 'up' }) {
  const [open, setOpen] = useState(false);
  const f = FORMULAS[eq];
  return (
    <span
      className={cx('redact-x', open && 'open', className)}
      style={{ width: w, height: h, ...style }}
      data-noadvance
      onClick={(e) => {
        e.stopPropagation();
        setOpen((o) => !o);
      }}
      title={open ? '' : 'Declassify'}
    >
      <span className="redact bar" style={{ width: w, height: h }} />
      <span className="hint">declassify · {f.label}</span>
      <span className={cx('slip', align === 'right' && 'right', drop === 'up' && 'up')}>
        <span className="slip-h">
          <span>{f.title}</span>
          <span className="x">close ×</span>
        </span>
        <span className="slip-b">{f.body}</span>
        <a className="slip-src" href={f.href} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
          {f.source} ↗
        </a>
      </span>
    </span>
  );
}
