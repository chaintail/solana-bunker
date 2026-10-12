import { Coin } from '../components/Door';
import { Counter, cx, Stamp, Swap } from '../components/bits';
import { Redact } from '../components/Redact';
import { Dest, DEST_A, DEST_B, Grid, Hex, SECRET_8, Treasury, TxCard } from '../components/Rig';
import type { SceneDef, SceneProps } from '../types';
import './s5.css';

function Agent({ className }: { className?: string }) {
  return (
    <div className={cx('agent', className)}>
      <svg>
        <use href="#agent" />
      </svg>
      <div className="lbl">Name</div>
      <span className="redact" style={{ width: 92, height: 13 }} />
    </div>
  );
}

function V2({ at, instant }: SceneProps) {
  const fold = at('fold'),
    robbed = at('robbed');
  return (
    <>
      <h1 className="hl">Version two</h1>
      <div className="bp-grid" />
      <div className="group" style={{ left: 660, top: 236, width: 700, height: 534 }}>
        <span className="lbl">Bunker program</span>
      </div>

      <div className="box drawer">
        <span className="lbl">Authorization account</span>
        <div className="sub">
          <Swap value={fold ? 1 : 0} options={['1,024 SHA-256 commitments', '1 Merkle root + usage bitmap']} d={420} />
        </div>
        <span className="ix ix-a" style={{ left: 21, top: 66 }}>
          #0000
        </span>
        <span className="ix ix-a" style={{ left: 79, top: 66, color: 'var(--blue)' }}>
          #0008 &nbsp;next
        </span>
        <span className="ix ix-a" style={{ right: 21, top: 410 }}>
          #1023
        </span>
        <Grid className="big" style={{ left: 21, top: 84 }} cls={(k) => (k < 8 ? 'x' : k === 8 ? 'tg' : undefined)} />
        <div className="rootbox">
          <span className="lbl" style={{ color: 'var(--blue)' }}>
            Merkle root · 32 bytes
          </span>
          <div className="h">a7c3e910…5b41f02d</div>
        </div>
        <div className="minibox">
          <span className="lbl" style={{ position: 'absolute', left: 0, top: 0, color: 'var(--blue)' }}>
            Usage bitmap · 128 bytes
          </span>
          <Grid className="mini" style={{ left: 79, top: 22 }} cls={(k) => (k < 8 ? 'c' : k === 8 ? 'r2' : undefined)} />
        </div>
        <div className="root-eq">
          <span className="lbl">root =</span>
          <Redact eq="merkle" w={230} h={18} />
        </div>
        <div className="ftr">
          <span>
            storage <Counter on={fold} from={33126} to={390} instant={instant} ms={1100} delay={500} /> bytes
          </span>
          <span>
            used <Swap value={robbed ? 1 : 0} options={['8', '9']} d={400} /> / 1,024
          </span>
        </div>
      </div>

      <Treasury />
      <Dest id="dA5" label="Destination A" addr={DEST_A} top={296} received="nothing" />
      <Dest id="dB5" label="Destination B" addr={DEST_B} top={560} received={<Swap value={robbed ? 1 : 0} options={['nothing', 'SOL']} d={550} />} className="redd" />

      <svg className="wires" viewBox="0 0 1920 1080">
        <path className="wire" d="M1040,560 L1080,560" markerEnd="url(#ah)" />
        <path className="wire dash" d="M1340,452 C1400,452 1420,350 1478,350" markerEnd="url(#ah)" opacity=".7" />
        <path className={cx('wire dash fade wB', at('copy') && 'go')} d="M1340,650 C1400,650 1420,614 1478,614" markerEnd="url(#ahr)" style={{ stroke: '#b3242a', ['--d' as string]: '2000ms' }} />
        <path className={cx('wire dash fade wfl', at('flight') && !robbed && 'go')} d="M628,347 L676,347" style={{ ['--d' as string]: '400ms' }} />
        <path className={cx('wire draw wcopy2', robbed && 'go')} pathLength={1} d="M628,607 C700,607 770,540 817,483" style={{ ['--d' as string]: '0ms', stroke: '#b3242a', strokeWidth: 2 }} />
        <path className={cx('wire draw wuser2', robbed && 'go')} pathLength={1} d="M628,347 C700,347 780,420 815,470" style={{ ['--d' as string]: '300ms', strokeWidth: 2, opacity: 0.6 }} />
      </svg>

      <div className="flight">In flight · readable before it lands</div>
      <TxCard
        id="u2"
        head="Pending withdrawal"
        right="tx 1 of 1"
        rows={[
          ['withdraw', 'SOL'],
          ['to', <>address A<small>4Nd1…Zq7e</small></>],
          ['leaf', '#0008'],
          ['secret', <Hex lines={SECRET_8} className={cx(at('copy') && 'lit')} />],
          ['proof', '10 hashes · 320 bytes'],
        ]}
      />
      <div className="refused2">Refused · leaf #0008 already used</div>
      <Agent className="agent5" />
      <div id="c2w">
        <TxCard
          id="c2"
          className="redc"
          head="Pending withdrawal"
          right="priority fee ×10"
          rows={[
            ['withdraw', 'SOL'],
            [
              'to',
              <>
                address{' '}
                <span className="ed">
                  <span className="was">A</span>
                  <span className="now">B</span>
                </span>
                <span className="kx">
                  <small className="k1">4Nd1…Zq7e</small>
                  <small className="k2">9gHt…Vb2c</small>
                </span>
              </>,
            ],
            ['leaf', '#0008'],
            ['secret', <Hex lines={SECRET_8} className="redhex lit" />],
            ['proof', '10 hashes · 320 bytes'],
          ]}
        />
      </div>

      <div className="chipw chip-b">
        <div className="chip">
          <Coin kind="sol" size={22} />
          SOL
        </div>
      </div>

      <div className="line-b">
        <span className="type">We didn’t break the hash. We copied the password.</span>
      </div>
      <Stamp on={robbed} instant={instant} x={1010} y={518} size={156} r={-9} d={380}>
        Robbed
      </Stamp>
    </>
  );
}

export const S5: SceneDef = {
  key: 'v2',
  exhibit: 'Exhibit 5',
  title: 'Version two · Merkle root',
  steps: [{ id: 'start' }, { id: 'fold' }, { id: 'flight' }, { id: 'copy' }, { id: 'robbed' }, { id: 'line' }],
  C: V2,
};
