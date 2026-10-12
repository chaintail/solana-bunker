import { Coin } from '../components/Door';
import { cx, Stamp, Swap } from '../components/bits';
import { Dest, Grid, Hex, SECRET_7, SECRET_BAD, Treasury, TxCard, DEST_A } from '../components/Rig';
import type { SceneDef, SceneProps } from '../types';
import './s4.css';

function V1({ at, instant }: SceneProps) {
  const right = at('right');
  return (
    <>
      <h1 className="hl">Version one</h1>
      <div className="bp-grid" />
      <div className="group rig-in" style={{ left: 660, top: 236, width: 700, height: 534 }}>
        <span className="lbl">Bunker program</span>
      </div>

      <div className="box drawer rig-in" style={{ ['--d' as string]: '120ms' }}>
        <span className="lbl">Authorization account</span>
        <div className="sub">1,024 SHA-256 commitments</div>
        <span className="ix" style={{ left: 21, top: 66 }}>
          #0000
        </span>
        <span className="ix" style={{ left: 79, top: 66, color: 'var(--blue)' }}>
          #0007 &nbsp;next
        </span>
        <span className="ix" style={{ right: 21, top: 410 }}>
          #1023
        </span>
        <Grid className="big" style={{ left: 21, top: 84 }} cls={(k) => (k < 7 ? 'x' : k === 7 ? 'tg x7 s7' : undefined)} />
        <div className="ftr">
          <span>storage 33,126 bytes</span>
          <span>
            used <Swap value={right ? 1 : 0} options={['7', '8']} d={900} /> / 1,024
          </span>
        </div>
      </div>

      <Treasury className="rig-in" />
      <Dest id="dA" label="Destination A" addr={DEST_A} top={296} received={<Swap value={right ? 1 : 0} options={['nothing', 'SOL']} d={1500} />} className="rig-in" />

      <svg className="wires" viewBox="0 0 1920 1080">
        <path className="wire rig-in" d="M1040,560 L1080,560" markerEnd="url(#ah)" />
        <path className="wire dash rig-in" d="M1340,452 C1400,452 1420,350 1478,350" markerEnd="url(#ah)" opacity=".7" />
        <path className={cx('wire dash redw fade w-bad', at('wrong') && !right && 'go')} d="M628,347 L676,347" />
        <path className={cx('wire draw w-good', right && 'go')} pathLength={1} d="M628,347 L766,352" style={{ ['--d' as string]: '350ms' }} />
      </svg>

      <TxCard
        id="cw"
        className="redc"
        head="Pending withdrawal"
        right="tx 1 of 1"
        rows={[
          ['withdraw', 'SOL'],
          ['to', <>address A<small>4Nd1…Zq7e</small></>],
          ['slot', '#0007'],
          ['secret', <Hex lines={SECRET_BAD} className="redhex lit" />],
        ]}
      />
      <div className="tagred refused1">REFUSED · hash does not match #0007</div>

      <TxCard
        id="cr"
        head="Pending withdrawal"
        right="tx 1 of 1"
        rows={[
          ['withdraw', 'SOL'],
          ['to', <>address A<small>4Nd1…Zq7e</small></>],
          ['slot', '#0007'],
          ['secret', <Hex lines={SECRET_7} className={cx(right && 'lit')} />],
        ]}
      />

      <div className="chipw chip-a">
        <div className="chip">
          <Coin kind="sol" size={22} />
          SOL
        </div>
      </div>

      <Stamp on={right} instant={instant} x={472} y={560} size={40} r={-5} d={1250}>
        Secret accepted
      </Stamp>
    </>
  );
}

export const S4: SceneDef = {
  key: 'v1',
  exhibit: 'Exhibit 4',
  title: 'Version one · one-time secrets',
  steps: [{ id: 'v1' }, { id: 'wrong' }, { id: 'right' }],
  C: V1,
};
