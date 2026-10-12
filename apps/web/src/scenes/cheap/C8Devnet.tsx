import { CStamp, explorerAddr, explorerTx, short } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import './c89.css';

const W = story.withdrawal;
const R = story.rotation;
const fmt = (n: number) => n.toLocaleString('en-US');
const STORE: [string, number][] = [
  ['Version 1', 33126],
  ['Version 2', 390],
  ['Version 3', 422],
];

function Devnet({ at }: SceneProps) {
  return (
    <>
      <h1 className="ch-title">Live on devnet</h1>
      <div className="cbox c8-tx">
        <div className="c8-sig">
          <b>Signature:</b> {W.signature}
        </div>
        <div>
          <b>Result:</b> <span className="c8-ok">{W.success ? 'Success' : 'Failed'}</span>
        </div>
        <div>
          <b>Slot:</b> {fmt(W.slot)} &nbsp; <b>Version:</b> {W.version}
        </div>
        <div>
          <b>Compute:</b> {fmt(W.cu)} of {fmt(W.cuLimit)} units
        </div>
        <div>
          <b>Size:</b> {fmt(W.bytes)} bytes, 1 transaction
        </div>
        <a className="c8-link" href={explorerTx(W.signature)} target="_blank" rel="noreferrer" data-noadvance>
          Open in Solana Explorer
        </a>
      </div>
      <div className="cbox c8-store">
        <b>Bytes on chain</b>
        {STORE.map(([v, n]) => (
          <div key={v} className="c8-row">
            <span>
              {v}: <b>{fmt(n)}</b>
            </span>
            <i style={{ width: `${Math.max(1, (n / 33126) * 100)}%` }} />
          </div>
        ))}
      </div>
      <div className="c8-links">
        <a href={explorerAddr(story.program.id)} target="_blank" rel="noreferrer" data-noadvance>
          Program: {short(story.program.id, 8, 6)}
        </a>
        <a href={explorerTx(R.signature)} target="_blank" rel="noreferrer" data-noadvance>
          Re-key transaction: {short(R.signature, 8, 6)}
        </a>
      </div>
      <CStamp on={at('confirmed')} x={1500} y={900} size={110} d={40}>
        CONFIRMED
      </CStamp>
    </>
  );
}

export const C8: SceneDef = {
  key: 'c-devnet',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'tx' }, { id: 'storage' }, { id: 'links' }, { id: 'confirmed' }],
  C: Devnet,
};
