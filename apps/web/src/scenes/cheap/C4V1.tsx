import { CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Arrow } from './C1Warning';
import { Coin, Grid, Vault } from './clip';
import './c45.css';

function V1({ at }: SceneProps) {
  const right = at('right');
  return (
    <>
      <h1 className="ch-title">Version one</h1>
      <div className="c45-acct">
        <div className="c45-h">1,024 one-time secrets</div>
        <Grid cell={12} gap={3} mark={(k) => (k < 7 ? 'used' : k === 7 ? cx('target', 's7') : undefined)} />
        <div className="c45-f">33,126 bytes on chain</div>
      </div>
      <Vault size={260} className="c45-vault" />
      <div className="cbox c45-dest">
        Address A: <b>{right ? 'got SOL' : 'nothing'}</b>
      </div>
      <svg className="c1-svg" viewBox="0 0 1920 1080">
        <g className={cx('c-in', (at('wrong') || right) && 'on')}>
          <Arrow x1={590} y1={400} x2={640} y2={400} w={8} />
        </g>
        <Arrow x1={1210} y1={460} x2={1390} y2={400} w={8} />
        <g className={cx('c-in', right && 'on')} style={{ ['--d' as string]: '400ms' }}>
          <Arrow x1={1530} y1={560} x2={1530} y2={680} w={8} />
        </g>
      </svg>

      <div className="cbox red c45-card cw">
        Withdraw SOL to A
        <br />
        Slot 7
        <br />
        Secret: <b>8b17e05c…</b>
      </div>
      <div className="c45-tag c45-refused">REFUSED</div>
      <div className="cbox blue c45-card cr">
        Withdraw SOL to A
        <br />
        Slot 7
        <br />
        Secret: <b>3f9c41a0…</b>
      </div>
      <div className="c45-chip">
        <Coin kind="SOL" size={90} />
      </div>
      <CStamp on={right} x={360} y={720} size={56} d={600}>
        SECRET ACCEPTED
      </CStamp>
    </>
  );
}

export const C4: SceneDef = {
  key: 'c-v1',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'v1' }, { id: 'wrong' }, { id: 'right' }],
  C: V1,
};
