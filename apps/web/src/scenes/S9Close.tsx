import { encode } from 'uqr';
import type { SceneDef } from '../types';
import './s9.css';

const REPO = 'https://github.com/chaintail/solana-bunker';
const QR = encode(REPO, { ecc: 'M', border: 0 });

function QrCode() {
  const n = QR.size;
  let d = '';
  QR.data.forEach((row, y) =>
    row.forEach((on, x) => {
      if (on) d += `M${x},${y}h1v1h-1z`;
    }),
  );
  return (
    <svg className="qr" viewBox={`-2 -2 ${n + 4} ${n + 4}`} shapeRendering="crispEdges" aria-label={REPO}>
      <rect x={-2} y={-2} width={n + 4} height={n + 4} fill="#f7f1e3" />
      <path d={d} fill="#1c1a17" />
    </svg>
  );
}

function Close() {
  return (
    <>
      <a className="qr-wrap" href={REPO} target="_blank" rel="noreferrer" data-noadvance>
        <QrCode />
        <i className="tack" />
      </a>
      <div className="close-r">
        <span className="lbl">Source, evidence and the whitepaper</span>
        <a className="repo" href={REPO} target="_blank" rel="noreferrer" data-noadvance>
          github.com/chaintail/solana-bunker
        </a>
        <div className="who">Liam</div>
      </div>
    </>
  );
}

export const S9: SceneDef = {
  key: 'close',
  exhibit: 'File closed',
  title: 'Solana Bunker',
  steps: [{ id: 'close' }],
  C: Close,
};
