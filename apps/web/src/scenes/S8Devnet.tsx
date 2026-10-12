import { cx, explorerAddr, explorerTx, short, Stamp } from '../components/bits';
import story from '../data/story.json';
import type { SceneDef, SceneProps } from '../types';
import './s8.css';

const W = story.withdrawal;
const R = story.rotation;
const fmt = (n: number) => n.toLocaleString('en-US');
const when = new Date(W.blockTime * 1000);
const STAMP_TIME = `${when.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })} ${when.toISOString().slice(11, 19)} UTC`;
const STORAGE: [string, string, number][] = [
  ['Version one', '1,024 hashes in an array', 33126],
  ['Version two', 'one Merkle root', 390],
  ['Version three', 'XMSS root + public seed', 422],
];

function Devnet({ at, instant }: SceneProps) {
  return (
    <>
      <h1 className="hl">Live on devnet</h1>

      <div className="xp">
        <i className="corner tl" />
        <i className="corner tr" />
        <i className="corner bl" />
        <i className="corner br" />
        <div className="xp-bar">
          <span className="xp-logo">
            <svg width="26" height="20" viewBox="0 0 26 20" aria-hidden="true">
              <path d="M5,2 H24 L21,5.5 H2 Z M2,8.3 H21 L24,11.7 H5 Z M5,14.5 H24 L21,18 H2 Z" fill="currentColor" />
            </svg>
            Explorer
          </span>
          <span className="xp-net">Devnet</span>
        </div>
        <div className="xp-title">Transaction</div>
        <div className="xp-card">
          <div className="xp-h">Overview</div>
          <dl>
            <dt>Signature</dt>
            <dd className="sig">{W.signature}</dd>
            <dt>Result</dt>
            <dd>
              <span className="ok">{W.success ? 'Success' : 'Failed'}</span>
            </dd>
            <dt>Timestamp</dt>
            <dd>{STAMP_TIME}</dd>
            <dt>Slot</dt>
            <dd>{fmt(W.slot)}</dd>
            <dt>Version</dt>
            <dd>{W.version}</dd>
            <dt>Fee (SOL)</dt>
            <dd>◎{(W.fee / 1e9).toFixed(6)}</dd>
            <dt>Compute units</dt>
            <dd>
              {fmt(W.cu)} of {fmt(W.cuLimit)} compute units
            </dd>
            <dt>Size</dt>
            <dd>{fmt(W.bytes)} bytes, one transaction</dd>
          </dl>
          <div className="xp-log">
            {W.logs.map((l, i) => (
              <div key={i}>
                <span>&gt;</span> {l}
              </div>
            ))}
          </div>
        </div>
        <a className="xp-link" href={explorerTx(W.signature)} target="_blank" rel="noreferrer" data-noadvance>
          explorer.solana.com/tx/{short(W.signature, 6, 6)}?cluster=devnet ↗
        </a>
      </div>

      <div className="store">
        <span className="lbl sh">Authorization state on chain · bytes</span>
        {STORAGE.map(([v, d, n], i) => (
          <div key={v} className="srow" style={{ ['--i' as string]: i }}>
            <div className="sv">
              <b>{v}</b>
              <span>{d}</span>
            </div>
            <div className="strack">
              <i style={{ width: `${Math.max(0.6, (n / 33126) * 100)}%` }} />
            </div>
            <div className="sn">{fmt(n)}</div>
          </div>
        ))}
      </div>

      <div className="links">
        <span className="lbl sh">Open it yourself</span>
        <a href={explorerAddr(story.program.id)} target="_blank" rel="noreferrer" data-noadvance>
          <span className="lbl">Program</span>
          <b>{story.program.id}</b>
        </a>
        <a href={explorerTx(R.signature)} target="_blank" rel="noreferrer" data-noadvance>
          <span className="lbl">Root rotation · slot {fmt(R.slot)}</span>
          <b>{short(R.signature, 22, 10)}</b>
        </a>
        <a href={explorerAddr(W.treasury)} target="_blank" rel="noreferrer" data-noadvance>
          <span className="lbl">XMSS treasury</span>
          <b>{W.treasury}</b>
        </a>
      </div>

      <Stamp on={at('confirmed')} instant={instant} x={1476} y={946} size={100} r={-7} d={80} className={cx('st-conf')}>
        Confirmed
      </Stamp>
    </>
  );
}

export const S8: SceneDef = {
  key: 'devnet',
  exhibit: 'Exhibit 8',
  title: 'Evidence',
  steps: [{ id: 'tx' }, { id: 'storage' }, { id: 'links' }, { id: 'confirmed' }],
  C: Devnet,
};
