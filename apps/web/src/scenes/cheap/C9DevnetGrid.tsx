import { CStamp, cx } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import { LogoMark, QR } from './proof';
import './c9devnet.css';

const LINES = [
  'This is not a bunch of diagrams.',
  'All of it is live on devnet right now.',
  'Three vaults, SOL and USDC, the robbery, the rejection, the rotation.',
  'Every number on this screen is a transaction you can open in the explorer.',
];
const ids = LINES.map((_, i) => `l${i}`);

function Devnet({ at, cur }: SceneProps) {
  const grid = at('grid');
  const k = ids.indexOf(cur);
  return (
    <>
      {LINES.map((l, i) => (
        <div key={i} className={cx('c9d-line', !grid && i === k && 'on', !grid && i === k - 1 && 'prev')}>
          {l}
        </div>
      ))}
      <div className={cx('c9d-grid', grid && 'on')}>
        {story.proofOps.map((o, i) => (
          <a key={o.signature} className="c9d-cell" href={`https://solscan.io/tx/${o.signature}?cluster=devnet`} target="_blank" rel="noreferrer" data-noadvance style={{ ['--i' as string]: i }}>
            <QR text={`https://solscan.io/tx/${o.signature}?cluster=devnet`} size={300} ecc="L" />
            <span className="c9d-l">{o.label}</span>
          </a>
        ))}
        <div className="c9d-h">
          <svg viewBox="0 0 24 24" width={40} height={40} aria-hidden="true">
            <LogoMark kind="solscan" />
          </svg>
          every proof on Solscan, devnet
        </div>
      </div>
      <CStamp on={at('confirmed')} x={960} y={985} size={84} r={-3} d={60}>
        CONFIRMED
      </CStamp>
    </>
  );
}

export const C9Devnet: SceneDef = {
  key: 'c-devnet2',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [...ids.map((id) => ({ id })), { id: 'grid' }, { id: 'confirmed' }],
  C: Devnet,
};
