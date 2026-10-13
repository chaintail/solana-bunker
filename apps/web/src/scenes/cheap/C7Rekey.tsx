import { CStamp, cx } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import { Highlights, Lens, rng, Tick, wobEllipse } from './mix';
import { ProofColumn } from './proof';
import { TWEET } from './tweet';
import { Devil, Form, FORM_AMOUNT, Quill, VaultDoor } from './vaultscene';
import lens6 from '../../assets/tweet-lens-6.jpg';
import './c7.css';

/* the tweet again, magnifier on line 23 of drake-tweet.txt */
const COL = { x: 50, y: 120, w: 680, h: 920 };
const CK = COL.w / TWEET.column.w;
const T6 = 6926; // tweet-6.jpg top in the column, column px
const LENS_REGION: [number, number, number, number] = [10, 1500, 1290, 1730];
const SCROLL = -((T6 + ((LENS_REGION[1] + LENS_REGION[3]) / 2) * (900 / 1290)) * CK - COL.h / 2);

/* Lamport: 256 pairs, one of each lit */
const PAIRS = 256,
  PCOLS = 32;
const BOX = 22,
  PX0 = 330,
  PY0 = 250;
const r = rng(1979);
const LIT = Array.from({ length: PAIRS }, () => (r() < 0.5 ? 0 : 1));
/* Winternitz: 67 chains; the 512 boxes become the first 512 chain nodes */
const CHAINS = 67,
  NODES = 8;
const CPITCH = 22,
  CX0 = 960 - (CHAINS * CPITCH) / 2 + CPITCH / 2,
  CY0 = 700,
  NPITCH = 38;
const REVEAL = Array.from({ length: CHAINS }, () => Math.floor(r() * NODES));
const boxes = Array.from({ length: PAIRS * 2 }, (_, k) => {
  const p = k >> 1,
    half = k & 1;
  const x = PX0 + (p % PCOLS) * 30,
    y = PY0 + Math.floor(p / PCOLS) * 62 + half * (BOX + 3);
  const c = Math.floor(k / NODES),
    n = k % NODES;
  const nx = CX0 + c * CPITCH - BOX / 2,
    ny = CY0 + n * NPITCH - BOX / 2;
  return { x, y, dx: nx - x, dy: ny - y, lit: LIT[p] === half, rev: REVEAL[c] === n, d: (k % 64) * 6 + Math.floor(k / 64) * 20 };
});
const EXTRA = Array.from({ length: CHAINS * NODES - PAIRS * 2 }, (_, i) => {
  const k = PAIRS * 2 + i,
    c = Math.floor(k / NODES),
    n = k % NODES;
  return { x: CX0 + c * CPITCH - BOX / 2, y: CY0 + n * NPITCH - BOX / 2, rev: REVEAL[c] === n };
});
/* Merkle: 8 leaves over the chains, up to a root */
const TREE = (() => {
  const lv: { x: number; y: number }[][] = [];
  const span = (CHAINS - 1) * CPITCH;
  lv.push(Array.from({ length: 8 }, (_, i) => ({ x: CX0 + ((i + 0.5) * span) / 8, y: 600 })));
  for (let l = 1; l < 4; l++) lv.push(Array.from({ length: lv[l - 1].length / 2 }, (_, j) => ({ x: (lv[l - 1][2 * j].x + lv[l - 1][2 * j + 1].x) / 2, y: 600 - l * 100 })));
  return lv;
})();

const ROTATE_TEXT =
  'And because every one time key gets used exactly once, the vault keeps a bitmap of which leaves are spent. When you run low, or you just get paranoid, you sign one more message that installs a brand new tree. New root, new keys, same address, same balance. The new tree comes from the same twelve word seed phrase, just the next generation. So recovery is one instruction: rotate.';

function Xmss({ at, cur, anim }: SceneProps) {
  const lam = at('lamport') && !at('attack');
  const wots = at('wots');
  const beat7 = at('size');
  const late = at('one');
  return (
    <>
      {/* 1. the tweet */}
      <div className={cx('c7-tweet', cur === 'tweet' && 'on')}>
        <div className="c7-col" style={{ left: COL.x, top: COL.y, width: COL.w, height: COL.h }}>
          <img src={TWEET.column.src} alt="Justin Drake's bunker mode post" draggable={false} style={{ width: COL.w, transform: `translateY(${SCROLL}px)` }} />
        </div>
        <Lens
          className="on"
          img={lens6}
          imgW={1290}
          imgH={740}
          origin={[0, 1230]}
          region={LENS_REGION}
          width={1100}
          x={780}
          y={330}
          over={
            <Highlights
              lines={[
                [895, 1168, 1605],
                [28, 692, 1682],
              ]}
              seed={61}
            />
          }
        />
        <div className="c7-nocurve">No curves at all.</div>
      </div>

      {/* 2-6. Lamport, Winternitz, Merkle, XMSS */}
      <div className={cx('c7-title', lam && 'on')}>
        <span className={cx(cur === 'lamport' || cur === 'lsize' ? 'on' : '')}>Leslie Lamport, 1979</span>
        <span className={cx(cur === 'wots' && 'on')}>Winternitz: hash chains</span>
        <span className={cx(cur === 'merkle' && 'on')}>Merkle: a tree of keys</span>
      </div>
      <div className={cx('c7-boxes', lam && 'on', wots && 'chains')}>
        <svg className="c7-svg c7-links" viewBox="0 0 1920 1080" aria-hidden="true">
          {Array.from({ length: CHAINS }, (_, c) => (
            <line key={c} x1={CX0 + c * CPITCH} x2={CX0 + c * CPITCH} y1={CY0} y2={CY0 + (NODES - 1) * NPITCH} />
          ))}
        </svg>
        {boxes.map((b, k) => (
          <i
            key={k}
            className={cx('c7-b', b.lit && 'lit', b.rev && 'rev')}
            style={{ left: b.x, top: b.y, ['--dx' as string]: `${b.dx}px`, ['--dy' as string]: `${b.dy}px`, ['--d' as string]: `${b.d}ms` }}
          />
        ))}
        {EXTRA.map((b, k) => (
          <i key={`e${k}`} className={cx('c7-b c7-x', b.rev && 'rev')} style={{ left: b.x, top: b.y }} />
        ))}
      </div>
      <div className={cx('c7-lsize', cur === 'lsize' && 'on')}>
        8,192 bytes <small>per signature</small>
      </div>
      <svg className={cx('c7-svg c7-tree', at('merkle') && lam && 'on', at('xmss') && 'dim')} viewBox="0 0 1920 1080" aria-hidden="true">
        {TREE.slice(1).map((row, l) =>
          row.map((n, j) => [0, 1].map((c) => <line key={`${l}${j}${c}`} x1={n.x} y1={n.y} x2={TREE[l][2 * j + c].x} y2={TREE[l][2 * j + c].y} style={{ ['--d' as string]: `${l * 250}ms` }} />)),
        )}
        {TREE[0].map((n, i) => (
          <line key={`d${i}`} className="c7-down" x1={n.x} y1={n.y} x2={n.x} y2={CY0 - 20} />
        ))}
        {TREE.map((row, l) => row.map((n, j) => <circle key={`n${l}${j}`} cx={n.x} cy={n.y} r={l === 3 ? 22 : 15} className={l === 3 ? 'root' : ''} style={{ ['--d' as string]: `${l * 250}ms` }} />))}
      </svg>
      <div className={cx('c7-xmss', at('xmss') && lam && 'on')}>
        <div className="c7-xm">XMSS</div>
        <div className="c7-nist">
          <b>NIST</b>
          <span>SP 800-208</span>
        </div>
      </div>

      {/* 7. the attacker tries again: copied form, wrong signature, slot slams shut */}
      <VaultDoor on={at('attack') && !beat7} shut={at('attack')} />
      <div className={cx('c7-atk', at('attack') && !beat7 && 'on')}>
        <div className="c7-devil">
          <Devil />
        </div>
        <Form to="Attacker" amount={FORM_AMOUNT} sig={23} sigColor="#d00000" className="c7-form">
          <svg className="c7-ring" viewBox="0 0 520 140" aria-hidden="true">
            <path className="mkp" d={wobEllipse(260, 70, 250, 60, 9, 1.1)} strokeWidth={7} />
          </svg>
        </Form>
        <div className="mk c7-nomatch">signature does not match</div>
        <div className="vs-quill c7-quill">
          <Quill />
        </div>
      </div>
      <CStamp on={at('attack') && !beat7} x={520} y={960} size={110} r={-4} d={3300} className="c7-rej">
        REJECTED
      </CStamp>

      {/* beat 7: size, the 1,232 byte limit, staged 003-a, v1 transactions, 003-b */}
      <div className={cx('c7-size', beat7 && !late && 'on')}>
        <div className="c7-sl">
          <span className="c7-lamp">Lamport</span>
          <span className="c7-xl">XMSS</span>
        </div>
        <div className="c7-sn">
          <Tick from={8192} to={story.withdrawal.witnessBytes} run={at('size')} instant={!anim || cur !== 'size'} delay={1200} /> bytes
        </div>
      </div>
      <div className={cx('c7-limit', at('limit') && !late && 'on')}>
        {story.withdrawal.witnessBytes.toLocaleString('en-US')} <span className="c7-op">&gt;</span>{' '}
        <Tick from={1232} to={4096} run={at('v1tx')} instant={!anim || cur !== 'v1tx'} delay={900} />
      </div>
      <div className={cx('c7-new', at('v1tx') && !late && 'on')}>
        <span className="c7-brand loop">BRAND NEW</span>
        <div>Solana Transactions V1 to the rescue!</div>
      </div>
      <div className={cx('c7-prog', at('staged') && !at('table') && 'on')}>
        Bunker Program 003<span className={cx('c7-sa', at('b') && 'gone')}>-a</span>
        <span className={cx('c7-sb', at('b') && 'on')}>-b</span>
      </div>
      <ProofColumn on={at('staged')} version="003" staged={!at('b')} />

      <div className={cx('c7-one', late && !at('table') && 'on')}>
        <div>one transaction</div>
        <div>{story.withdrawal.bytes.toLocaleString('en-US')} bytes</div>
        <div>{story.withdrawal.cu.toLocaleString('en-US')} compute units</div>
      </div>
      <CStamp on={late && !at('table')} x={805} y={720} size={120} r={-3} d={900}>
        ONE SHOT
      </CStamp>

      <table className={cx('c7-table', at('table') && 'on')}>
        <thead>
          <tr>
            <th>confirmed on devnet</th>
            <th>signature</th>
            <th>bytes</th>
            <th>compute units</th>
          </tr>
        </thead>
        <tbody>
          {story.xmssOps.map((o) => (
            <tr key={o.signature}>
              <td>{o.label}</td>
              <td className="mono">{o.signature.slice(0, 8)}…</td>
              <td>{o.bytes.toLocaleString('en-US')}</td>
              <td>{o.cu.toLocaleString('en-US')}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className={cx('c7-rot', at('rotate') && 'on')}>{ROTATE_TEXT}</div>
    </>
  );
}

export const C7: SceneDef = {
  key: 'c-xmss',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [
    { id: 'tweet' },
    { id: 'lamport' },
    { id: 'lsize' },
    { id: 'wots' },
    { id: 'merkle' },
    { id: 'xmss' },
    { id: 'attack' },
    { id: 'size' },
    { id: 'limit' },
    { id: 'staged' },
    { id: 'v1tx' },
    { id: 'b' },
    { id: 'one' },
    { id: 'table' },
    { id: 'rotate' },
  ],
  C: Xmss,
};
