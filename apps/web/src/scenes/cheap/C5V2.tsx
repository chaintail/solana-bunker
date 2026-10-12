import { Counter, CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Arrow } from './C1Warning';
import { Coin, Grid, Robber, Vault } from './clip';
import './c45.css';

function V2({ at, instant }: SceneProps) {
  const fold = at('fold'),
    robbed = at('robbed');
  return (
    <>
      <h1 className="ch-title">Version two</h1>
      <div className="c45-acct c5-acct">
        <div className="c45-h">{fold ? '1 Merkle root' : '1,024 one-time secrets'}</div>
        <div className="c5-grid">
          <Grid cell={12} gap={3} mark={(k) => (k < 8 ? 'used' : k === 8 ? 'target' : undefined)} />
        </div>
        <div className="c5-root">
          root
          <br />
          <b>a7c3e910…5b41f02d</b>
        </div>
        <div className="c45-f c5-count">
          <Counter on={fold} from={33126} to={390} instant={instant} ms={700} delay={200} /> bytes
        </div>
      </div>
      <Vault size={220} className="c5-vault" />
      <div className="cbox c5-a">
        Address A: <b>nothing</b>
      </div>
      <div className="cbox red c5-b">
        Address B: <b className="c-red">{robbed ? 'got SOL' : 'nothing'}</b>
      </div>

      <div className="c5-flight">in flight: anyone can read it</div>
      <div className="cbox blue c45-card c5-user">
        Withdraw SOL to A
        <br />
        Leaf 8
        <br />
        Secret: <b>e21b07c4…</b>
      </div>
      <div className="c5-refused">Refused: leaf 8 already used</div>
      <Robber size={170} className="c5-robber" />
      <div className="cbox red c45-card c5-copy">
        Withdraw SOL to <b className="c-red">B</b>
        <br />
        Same secret
        <br />
        <b className="c-red">Priority fee ×10</b>
      </div>
      <svg className="c1-svg" viewBox="0 0 1920 1080">
        <g className={cx('c-in', robbed && 'on')}>
          <Arrow x1={650} y1={575} x2={700} y2={500} w={10} color="#ff0000" />
          <Arrow x1={1262} y1={600} x2={1330} y2={760} w={10} color="#ff0000" />
        </g>
      </svg>
      <div className="c45-chip c5-chip">
        <Coin kind="SOL" size={90} />
      </div>
      <CStamp on={robbed} x={960} y={520} size={190} r={-2} d={380}>
        ROBBED
      </CStamp>
      <div className="c-line c5-line">We didn’t break the hash. We copied the password.</div>
    </>
  );
}

export const C5: SceneDef = {
  key: 'c-v2',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'start' }, { id: 'fold' }, { id: 'flight' }, { id: 'copy' }, { id: 'robbed' }, { id: 'line' }],
  C: V2,
};
