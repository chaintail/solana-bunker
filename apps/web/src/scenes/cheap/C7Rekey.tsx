import { CStamp, cx, short } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import { Grid } from './clip';
import './c7.css';

const W = story.withdrawal;
const R = story.rotation;
const SPENT = new Set(R.consumedBefore);
const fmt = (n: number) => n.toLocaleString('en-US');
const STAGED = ['create a temp account', 'upload signature, part 1', 'upload signature, part 2', 'upload signature, part 3', 'withdraw'];

function Rekey({ at }: SceneProps) {
  const rot = at('rotate');
  return (
    <>
      <h1 className="ch-title">One transaction, and re-keying</h1>
      <div className="c7-five">
        {STAGED.map((t, i) => (
          <div key={i} className="cbox c7-tx" style={{ ['--i' as string]: i }}>
            <b>Transaction {i + 1} of 5:</b> {t}
          </div>
        ))}
        <div className="c-big c7-fivecap">
          {fmt(W.witnessBytes)}-byte signature = 5 transactions
        </div>
      </div>
      <div className="cbox blue c7-one">
        <b>
          {fmt(W.bytes)} bytes · {fmt(W.cu)} CU · 1 transaction
        </b>
      </div>
      <CStamp on={at('one') && !at('bitmap')} x={1340} y={640} size={64} d={300}>
        ONE TRANSACTION
      </CStamp>

      <div className="c7-rig">
        <div className="c7-grid">
          <Grid cell={14} gap={3} mark={(k) => (SPENT.has(k) ? 'used sp' : undefined)} />
        </div>
        <div className="c-big c7-used">{rot ? '0' : String(SPENT.size)} of 1,024 keys used</div>
        <div className="cbox c7-info">
          Root: <b className={cx(rot && 'c-blue')}>{rot ? 'd41c88a2…e5f307ab' : '9f3a1c6e…0b7dc2e1'}</b>
          <br />
          Epoch: <b className={cx(rot && 'c-blue')}>{rot ? '1' : '0'}</b>
          <br />
          Address: <b>{short(W.treasury, 8, 7)}</b> <span className={cx('c7-nm', rot && 'on')}>(not moved)</span>
        </div>
        <div className={cx('c-mid c7-rotcap', rot && 'on')}>
          rotation: {fmt(R.bytes)} bytes, {fmt(R.cu)} CU, 1 transaction
        </div>
        <div className="cbox red c7-old">Old key signs a withdrawal</div>
      </div>
      <CStamp on={at('oldroot') && !at('rekeyed')} x={1560} y={700} size={84} d={400}>
        REJECTED
      </CStamp>

      <div className="c7-words">
        {Array.from({ length: 12 }, (_, k) => (
          <div key={k} className="c7-w" style={{ ['--k' as string]: k }}>
            <i />
            <span>{k + 1}</span>
          </div>
        ))}
      </div>
      <div className="c7-gen g0">generation 0</div>
      <div className="c7-gen g1">generation 1</div>

      <div className={cx('c7-wash', at('rekeyed') && 'on')} />
      <CStamp on={at('rekeyed')} x={960} y={560} size={220} d={200} className="c7-rk">
        RE-KEYED
      </CStamp>
    </>
  );
}

export const C7: SceneDef = {
  key: 'c-rekey',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'five' }, { id: 'one' }, { id: 'bitmap' }, { id: 'rotate' }, { id: 'oldroot' }, { id: 'words' }, { id: 'rekeyed' }],
  C: Rekey,
};
