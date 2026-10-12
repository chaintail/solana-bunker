import { encode } from 'uqr';
import type { SceneDef } from '../../types';
import './c89.css';

const REPO = 'https://github.com/chaintail/solana-bunker';
const QR = encode(REPO, { ecc: 'M', border: 0 });

function Close() {
  let d = '';
  QR.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`)));
  const n = QR.size;
  return (
    <>
      <a className="c9-qr" href={REPO} target="_blank" rel="noreferrer" data-noadvance>
        <svg viewBox={`-2 -2 ${n + 4} ${n + 4}`} shapeRendering="crispEdges" aria-label={REPO}>
          <rect x={-2} y={-2} width={n + 4} height={n + 4} fill="#fff" />
          <path d={d} fill="#000" />
        </svg>
      </a>
      <a className="c9-url" href={REPO} target="_blank" rel="noreferrer" data-noadvance>
        github.com/chaintail/solana-bunker
      </a>
      <div className="c9-name">Liam</div>
    </>
  );
}

export const C9: SceneDef = {
  key: 'c-close',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'close' }],
  C: Close,
};
