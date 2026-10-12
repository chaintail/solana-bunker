import { CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Arrow } from './C1Warning';
import { Robber } from './clip';
import './c6.css';

function Tree() {
  const leaves = 8,
    lit = 5;
  const lv: { x: number; y: number; on: boolean }[][] = [];
  for (let l = 0; l <= 3; l++) {
    const n = leaves >> l;
    lv.push(Array.from({ length: n }, (_, j) => ({ x: 20 + ((j + 0.5) * 480) / n, y: 270 - l * 85, on: j === lit >> l })));
  }
  return (
    <svg viewBox="0 0 520 300" width={520} height={300} aria-hidden="true">
      {lv.slice(0, 3).map((row, l) => row.map((n, j) => <line key={`${l}${j}`} x1={n.x} y1={n.y} x2={lv[l + 1][j >> 1].x} y2={lv[l + 1][j >> 1].y} stroke={n.on ? '#0000ff' : '#000'} strokeWidth={n.on ? 9 : 4} />))}
      {lv.map((row, l) => row.map((n, j) => <circle key={`c${l}${j}`} cx={n.x} cy={n.y} r={l === 3 ? 24 : 16} fill={n.on ? '#0000ff' : '#fff'} stroke="#000" strokeWidth={4} />))}
    </svg>
  );
}

function Sig({ at }: SceneProps) {
  const attack = at('attack');
  return (
    <>
      <h1 className="ch-title">A signature made of hashes</h1>
      <div className={cx('c6-col c6-lam', attack && 'dim')}>
        <div className="c6-h">Lamport</div>
        <div className="c6-pair">
          <div className="c6-sec">
            <span className="bar" />
          </div>
          <div className="c6-sec s1">
            <span className="bar" />
            <span className="val">61b0f3d2</span>
          </div>
        </div>
        <div className="c6-pair c6-lbl">
          <span>secret 0</span>
          <span>secret 1</span>
        </div>
        <div className="c6-bit">
          bit = <b className="c-blue">1</b>: show secret 1 only
        </div>
      </div>
      <div className={cx('c6-col c6-chain', attack && 'dim')}>
        <div className="c6-h">Winternitz</div>
        <svg viewBox="0 0 540 90" width={540} height={90} aria-hidden="true">
          {Array.from({ length: 16 }, (_, k) => (
            <g key={k}>
              {k > 0 && <line x1={18 + (k - 1) * 33} x2={18 + k * 33} y1={45} y2={45} stroke="#000" strokeWidth={4} />}
              <circle className={cx('cn', k <= 5 && 'past')} cx={18 + k * 33} cy={45} r={13} style={{ ['--k' as string]: k }} />
            </g>
          ))}
        </svg>
        <div className="c-mid c6-ct">
          sign 5: show H<sup>5</sup>(secret)
          <br />
          hash 10 more = public key
        </div>
      </div>
      <div className={cx('c6-col c6-tree', attack && 'dim')}>
        <div className="c6-h">Merkle tree</div>
        <Tree />
        <div className="c-mid">1,024 keys, 1 root</div>
      </div>

      <div className="c6-atk">
        <Robber size={150} className="c6-robber" />
        <div className="cbox red c6-copy">
          Send SOL to <b className="c-red">B</b>
          <br />
          signature made for A
        </div>
        <svg className="c1-svg" viewBox="0 0 1920 1080">
          <Arrow x1={995} y1={835} x2={1055} y2={835} w={10} color="#ff0000" />
        </svg>
        <div className="cbox red c6-ver">
          Check: <b className="c-red">FAIL</b>
        </div>
      </div>
      <CStamp on={attack} x={1500} y={962} size={100} d={500}>
        REJECTED
      </CStamp>
    </>
  );
}

export const C6: SceneDef = {
  key: 'c-sig',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'lamport' }, { id: 'reveal' }, { id: 'chain' }, { id: 'tree' }, { id: 'attack' }],
  C: Sig,
};
