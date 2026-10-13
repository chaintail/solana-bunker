import { useEffect, useRef } from 'react';
import { CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Highlights, Lens, rng, wobEllipse, wobLine } from './mix';
import { ProofColumn } from './proof';
import { HASH_TOUR, HASH_WORDS, PARTS, TWEET } from './tweet';
import './c4.css';

/* ---------- 1. the tweet again, same place as slide 2; the lens tours every "hash" ---------- */
const COL = { x: 50, y: 120, w: 680, h: 920 };
const CK = COL.w / TWEET.column.w;
const BOTTOM = -(TWEET.column.h * CK - COL.h);
const colY = (part: string, y: number) => (PARTS[part].top + y * PARTS[part].k) * CK; // stage px inside the column
const TOUR = HASH_TOUR.map((t, i) => {
  const [x0, y0, x1, y1] = t.region;
  const scroll = Math.max(BOTTOM, Math.min(0, -(colY(t.part, (y0 + y1) / 2) - COL.h / 2)));
  const words = HASH_WORDS.filter(([p, , , y]) => p === t.part && y > y0 && y < y1).map(([, a, b, y]) => [a, b, y] as [number, number, number]);
  const width = 1100;
  const h = ((y1 - y0) * width) / (x1 - x0);
  return { ...t, scroll, words, width, y: [300, 220, 180][i] ?? 200, h, hl: t.part === '5' ? 46 : 62, x0 };
});

/* ---------- 3-6. stick figure, Bunker Program 001, 1,024 secrets ---------- */
const RECT = { x: 960, y: 126, w: 650, h: 920 };
const N = 1024,
  COLS = 32;
const CELL = 17,
  GAP = 2;
const GX = RECT.x + (RECT.w - (COLS * (CELL + GAP) - GAP)) / 2,
  GY = 268; // grid origin
const cellXY = (k: number) => [GX + (k % COLS) * (CELL + GAP), GY + Math.floor(k / COLS) * (CELL + GAP)] as [number, number];
const T_FILL = 3000; // ms for the rest after the first five
/** the first five one by one, then faster and faster */
const tFill = (k: number) => (k < 5 ? k * 520 : Math.round(5 * 520 + T_FILL * Math.sqrt((k - 5) / (N - 6))));
const LIST = ['secret_1', 'secret_2', 'secret_3', 'secret_4', 'secret_5', '…', `secret_${N}`];
const LX = 70,
  LY = 470,
  LH = 74;
const rowOf = (k: number) => (k < 5 ? k : k === N - 1 ? 6 : 5);
const CHIPS = [0, 1, 2, 3, 4, 6, 9, 13, 18, 25, 34, 46, 62, 83, 110, 145, 190, 248, 320, 410, 520, 650, 800, N - 1];
const MATH = { x: 560, y: 560, w: 300, h: 190 };
const MATH_IN = { x: 985, y: 262, k: 0.6 }; // where MATH sits once it moves into the program (version two)
const HAND: [number, number] = [262, 250];
const COIN_X = (i: number) => 1430 + i * 32,
  COIN_Y = 210;

/* ---------- version two: Merkle tree over the leaves ---------- */
const LEAVES = 16,
  LPITCH = 34,
  LSIZE = 26;
const LEAF_X = (i: number) => RECT.x + 48 + i * LPITCH; // centre
const LEVEL_Y = [962, 852, 742, 632, 522];
const GAP_LEAVES = [7, 8]; // drawn as an ellipsis
const CLUSTER: [number, number] = [1263, 600];
const TREE = (() => {
  const levels: { x: number; y: number }[][] = [Array.from({ length: LEAVES }, (_, i) => ({ x: LEAF_X(i), y: LEVEL_Y[0] }))];
  for (let l = 1; l < LEVEL_Y.length; l++) {
    const prev = levels[l - 1];
    levels.push(Array.from({ length: prev.length / 2 }, (_, j) => ({ x: (prev[2 * j].x + prev[2 * j + 1].x) / 2, y: LEVEL_Y[l] })));
  }
  return levels;
})();
const ROOT = TREE[TREE.length - 1][0];
const BITS = 32;
const BIT_X = RECT.x + RECT.w - 44,
  BIT_Y = 330;
const STOLEN = 1; // leaf / secret index taken by the attacker (secret_2)
const RPC = { x: 560, y: 190, w: 240, h: 110 };

function StickFigure() {
  const s = 7;
  return (
    <svg className="c4-svg" viewBox="0 0 1920 1080" aria-hidden="true">
      <g className="mkp c4-stick" strokeWidth={s}>
        <path d={wobEllipse(170, 175, 44, 48, 3, 1.08)} />
        <path d={wobLine([170, 224], [166, 340], 4, 5, 3)} />
        <path d={wobLine([168, 252], [96, 318], 4, 7, 3)} />
        <path d={wobLine([168, 252], [258, 246], 4, 9, 3)} />
        <path d={wobLine([166, 340], [118, 430], 4, 11, 3)} />
        <path d={wobLine([166, 340], [214, 430], 4, 13, 3)} />
      </g>
    </svg>
  );
}

function SolCoin({ size = 64 }: { size?: number }) {
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} aria-hidden="true">
      <circle cx={32} cy={32} r={29} fill="#000" stroke="#000" strokeWidth={3} />
      <polygon points="21,19 47,19 43,25 17,25" fill="#14f195" />
      <polygon points="17,29 43,29 47,35 21,35" fill="#9945ff" />
      <polygon points="21,39 47,39 43,45 17,45" fill="#14f195" />
    </svg>
  );
}

function Horns({ w }: { w: number }) {
  return (
    <svg className="c4-horns" viewBox={`0 0 ${w} 40`} width={w} height={40} aria-hidden="true">
      <path d={`M${w * 0.12},40 Q${w * 0.06},14 ${w * 0.02},0 Q${w * 0.2},12 ${w * 0.3},40 Z`} fill="#d00000" stroke="#000" strokeWidth={3} />
      <path d={`M${w * 0.88},40 Q${w * 0.94},14 ${w * 0.98},0 Q${w * 0.8},12 ${w * 0.7},40 Z`} fill="#d00000" stroke="#000" strokeWidth={3} />
    </svg>
  );
}

function DevilHead() {
  return (
    <svg className="c4-devil" viewBox="0 0 200 220" width={200} height={220} aria-hidden="true">
      <path d="M48,70 Q30,30 26,4 Q60,26 76,52 Z" fill="#d00000" stroke="#000" strokeWidth={5} />
      <path d="M152,70 Q170,30 174,4 Q140,26 124,52 Z" fill="#d00000" stroke="#000" strokeWidth={5} />
      <circle cx={100} cy={120} r={70} fill="#ff2a2a" stroke="#000" strokeWidth={7} />
      <path d="M62,104 L88,116 M138,104 L112,116" stroke="#000" strokeWidth={7} strokeLinecap="round" />
      <circle cx={80} cy={124} r={7} fill="#000" />
      <circle cx={120} cy={124} r={7} fill="#000" />
      <path d="M66,152 Q100,182 134,152" fill="none" stroke="#000" strokeWidth={7} strokeLinecap="round" />
    </svg>
  );
}

/* 33,000 -> 390, ticking down when the step plays */
function Ticker({ run, instant }: { run: boolean; instant: boolean }) {
  const el = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const set = (v: number) => el.current && (el.current.textContent = Math.round(v).toLocaleString('en-US'));
    if (!run) return void set(33000);
    if (instant) return void set(390);
    let raf = 0;
    const t0 = performance.now() + 350;
    const tick = (now: number) => {
      const t = Math.min(1, Math.max(0, (now - t0) / 1700));
      const e = 1 - Math.pow(1 - t, 3);
      set(33000 + (390 - 33000) * e);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [run, instant]);
  return <span ref={el}>33,000</span>;
}

function V1({ at, cur, anim }: SceneProps) {
  const r = rng(404);
  const cells = [];
  for (let k = 0; k < N; k++) {
    const [x, y] = cellXY(k);
    const wx = (r() - 0.5) * 900,
      wy = (r() - 0.5) * 700,
      wr = (r() - 0.5) * 720;
    const gx = CLUSTER[0] - x + (r() - 0.5) * 80,
      gy = CLUSTER[1] - y + (r() - 0.5) * 80;
    cells.push(
      <i
        key={k}
        className={cx('c4-cell', k === 0 && 'c4-c0')}
        style={{
          left: x,
          top: y,
          ['--d' as string]: `${tFill(k) + 900}ms`,
          ['--g' as string]: `${Math.floor(k / COLS) * 18}ms`,
          ['--wx' as string]: `${wx.toFixed(0)}px`,
          ['--wy' as string]: `${wy.toFixed(0)}px`,
          ['--wr' as string]: `${wr.toFixed(0)}deg`,
          ['--gx' as string]: `${gx.toFixed(0)}px`,
          ['--gy' as string]: `${gy.toFixed(0)}px`,
        }}
      />,
    );
  }
  const [c0x, c0y] = cellXY(0);
  const v2 = at('v2');
  const spent = at('spend') && !v2;
  const leafX = LEAF_X(STOLEN);
  return (
    <>
      {/* 1. the hash tour */}
      <div className={cx('c4-tour', cur === 'hash' && 'on')}>
        <div className="c4-col" style={{ left: COL.x, top: COL.y, width: COL.w, height: COL.h }}>
          <div className="c4-colin" style={{ ['--s1' as string]: `${TOUR[0].scroll}px`, ['--s2' as string]: `${TOUR[1].scroll}px`, ['--s3' as string]: `${TOUR[2].scroll}px` }}>
            <img src={TWEET.column.src} alt="Justin Drake's bunker mode post" draggable={false} style={{ width: COL.w }} />
            {HASH_WORDS.map(([p, a, b, y], i) => {
              const k = PARTS[p].k * CK;
              return <i key={i} className="c4-hw" style={{ left: a * k - 3, top: colY(p, y) - 30 * k, width: (b - a) * k + 6, height: 60 * k, ['--i' as string]: i }} />;
            })}
          </div>
        </div>
        {TOUR.map((t, i) => (
          <Lens
            key={i}
            className={`c4-t c4-t${i + 1}`}
            img={t.img.src}
            imgW={t.img.w}
            imgH={t.img.h}
            origin={t.img.origin}
            region={t.region}
            width={t.width}
            x={780}
            y={t.y}
            over={<Highlights lines={t.words} seed={20 + i} h={t.hl} />}
          />
        ))}
      </div>

      {/* 2. the actual call */}
      <div className={cx('c4-code', cur === 'code' && 'on')}>
        <div className="c4-code-l">SHA-256 on Solana, one syscall</div>
        <pre className="c4-code-b">{'use solana_program::hash::hashv;\n\nlet h = hashv(&[secret]);'}</pre>
      </div>

      {/* 3. stick figure, the program, SOL flying in */}
      <div className={cx('c4-prog', at('program') && 'on')}>
        <StickFigure />
        <div className="c4-rect" style={{ left: RECT.x, top: RECT.y, width: RECT.w, height: RECT.h }}>
          <div className="c4-rect-t">
            Bunker Program{' '}
            <span className="c4-ver">
              001
              <svg viewBox="0 0 100 50" preserveAspectRatio="none" aria-hidden="true" className={cx('c4-vstrike', v2 && 'on')}>
                <path d="M-4,34 L104,14" />
              </svg>
            </span>
            <span className={cx('mk c4-v2', v2 && 'on')}>002</span>
          </div>
        </div>
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} className={cx('c4-coin', i === 0 && 'c4-coin0')} style={{ ['--x' as string]: `${COIN_X(i)}px`, ['--y' as string]: `${COIN_Y}px`, ['--d' as string]: `${300 + i * 160}ms` }}>
            <SolCoin size={48} />
          </div>
        ))}
      </div>
      <ProofColumn on={at('program')} version={v2 ? '002' : '001'} />

      {/* 4. the secrets, the grid */}
      <div className={cx('c4-list', at('secrets') && 'on', at('cascade') && 'dim')}>
        {LIST.map((s, i) => (
          <div key={i} className={cx('c4-li', i === 0 && spent && 'hi', i === STOLEN && at('tx') && 'hi')} style={{ top: LY + i * LH, left: LX, ['--d' as string]: `${i * 90}ms` }}>
            {s}
          </div>
        ))}
      </div>
      <div className={cx('c4-grid', at('secrets') && 'on', at('cascade') && 'full')}>{cells}</div>

      {/* 5. cascade through MATH */}
      <div
        className={cx('c4-math', at('cascade') && 'on', at('tree') && 'in')}
        style={{ left: MATH.x, top: MATH.y, width: MATH.w, height: MATH.h, ['--mx' as string]: `${MATH_IN.x - MATH.x}px`, ['--my' as string]: `${MATH_IN.y - MATH.y}px`, ['--mk' as string]: MATH_IN.k }}
      >
        MATH
      </div>
      <div className="c4-chips" aria-hidden="true">
        {CHIPS.map((k) => {
          const [x, y] = cellXY(k);
          return (
            <span key={k}>
              <b
                className="c4-chip"
                style={{
                  ['--fx' as string]: `${LX}px`,
                  ['--fy' as string]: `${LY + rowOf(k) * LH}px`,
                  ['--tx' as string]: `${MATH.x + 60}px`,
                  ['--ty' as string]: `${MATH.y + MATH.h / 2 - 22}px`,
                  ['--d' as string]: `${tFill(k)}ms`,
                }}
              >
                secret_{k + 1}
              </b>
              <i
                className="c4-sq"
                style={{
                  ['--fx' as string]: `${MATH.x + MATH.w - 10}px`,
                  ['--fy' as string]: `${MATH.y + MATH.h / 2 - 10}px`,
                  ['--tx' as string]: `${x}px`,
                  ['--ty' as string]: `${y}px`,
                  ['--d' as string]: `${tFill(k) + 450}ms`,
                }}
              />
            </span>
          );
        })}
      </div>

      {/* 6. spend one */}
      <b className={cx('c4-spend', at('spend') && 'on')} style={{ ['--fx' as string]: `${LX}px`, ['--fy' as string]: `${LY}px`, ['--hx' as string]: `${HAND[0] - 40}px`, ['--hy' as string]: `${HAND[1] - 80}px`, ['--tx' as string]: `${c0x - 60}px`, ['--ty' as string]: `${c0y - 20}px` }}>
        secret_1
      </b>
      <svg className={cx('c4-svg c4-cross', spent && 'on')} viewBox="0 0 1920 1080" aria-hidden="true">
        <path className="mkp" d={wobLine([c0x - 14, c0y - 14], [c0x + CELL + 14, c0y + CELL + 14], 2, 71, 2)} strokeWidth={8} />
        <path className="mkp" d={wobLine([c0x + CELL + 14, c0y - 14], [c0x - 14, c0y + CELL + 14], 2, 73, 2)} strokeWidth={8} />
      </svg>
      <div className={cx('c4-back', at('spend') && 'on')} style={{ ['--fx' as string]: `${COIN_X(0)}px`, ['--fy' as string]: `${COIN_Y}px`, ['--tx' as string]: `${HAND[0] - 4}px`, ['--ty' as string]: `${HAND[1] - 34}px` }}>
        <SolCoin size={60} />
      </div>
      <CStamp on={spent} x={620} y={420} size={56} r={-3} d={2500} className="c4-ok">
        SECRET ACCEPTED
      </CStamp>

      {/* 7. the bill */}
      <div className={cx('c4-card c4-rent', at('rent') && !v2 && 'on')}>
        <div className="c4-rent-a">RENT:</div>
        <div className="c4-rent-b">33,000 bytes → 0.234 SOL!</div>
        <div className="c4-rent-s">38 transactions to set up</div>
      </div>

      {/* ---------- version two ---------- */}
      {/* 9. the grid flies, regroups, becomes the leaves; the tree grows; the root lights up */}
      <div className={cx('c4-tree', at('tree') && 'on')}>
        <svg className="c4-svg" viewBox="0 0 1920 1080" aria-hidden="true">
          <g className="c4-tr">
            {TREE.slice(1).map((row, l) =>
              row.map((n, j) =>
                [0, 1].map((c) => {
                  const ch = TREE[l][2 * j + c];
                  const ellip = l === 0 && GAP_LEAVES.includes(2 * j + c);
                  return (
                    <line
                      key={`${l}-${j}-${c}`}
                      className={cx('c4-edge', ellip && 'dash')}
                      x1={n.x}
                      y1={n.y}
                      x2={ch.x}
                      y2={ch.y - (l === 0 ? LSIZE / 2 : 0)}
                      pathLength={1}
                      style={{ ['--d' as string]: `${1900 + l * 280}ms` }}
                    />
                  );
                }),
              ),
            )}
            {TREE.slice(1, -1).map((row, l) =>
              row.map((n, j) => <circle key={`n${l}-${j}`} className="c4-node" cx={n.x} cy={n.y} r={13} style={{ ['--d' as string]: `${2100 + l * 280}ms` }} />),
            )}
          </g>
          <circle className="c4-root" cx={ROOT.x} cy={ROOT.y} r={28} />
        </svg>
        <div className="c4-root-l" style={{ left: ROOT.x + 40, top: ROOT.y - 26 }}>
          Merkle root
        </div>
        {TREE[0].map((n, i) =>
          GAP_LEAVES.includes(i) ? null : (
            <i
              key={i}
              className="c4-leaf"
              style={{
                left: n.x - LSIZE / 2,
                top: n.y - LSIZE / 2,
                ['--cx' as string]: `${CLUSTER[0] - n.x}px`,
                ['--cy' as string]: `${CLUSTER[1] - n.y}px`,
              }}
            />
          ),
        )}
        <div className="c4-ell" style={{ left: (LEAF_X(7) + LEAF_X(8)) / 2 - 40, top: LEVEL_Y[0] - 44 }}>
          …
        </div>
      </div>

      {/* 10. 33,000 -> 390 bytes, 0.234 -> 0.0066 SOL */}
      <div className={cx('c4-card c4-shrink', cur === 'shrink' && 'on')}>
        <div className="c4-sh-n">
          <Ticker run={at('shrink')} instant={!anim || cur !== 'shrink'} /> <small>bytes</small>
        </div>
        <div className="c4-sh-s">
          <span className="c4-old">
            0.234 SOL
            <svg viewBox="0 0 100 50" preserveAspectRatio="none" aria-hidden="true">
              <path d="M-4,40 L104,8" />
            </svg>
          </span>{' '}
          <span className="c4-new">0.0066 SOL</span>
        </div>
      </div>

      {/* 11. an RPC; secret_2 goes out as a transaction, slowly */}
      <div className={cx('c4-rpc', at('tx') && 'on')} style={{ left: RPC.x, top: RPC.y, width: RPC.w, height: RPC.h }}>
        RPC
      </div>
      <div
        className={cx('c4-tx', at('tx') && 'on')}
        style={{
          ['--ax' as string]: `${LX}px`,
          ['--ay' as string]: `${LY + STOLEN * LH}px`,
          ['--hx' as string]: '190px',
          ['--hy' as string]: '150px',
          ['--rx' as string]: `${RPC.x + 55}px`,
          ['--ry' as string]: `${RPC.y + 15}px`,
          ['--sx' as string]: '806px',
          ['--sy' as string]: `${RPC.y + 15}px`,
          ['--ex' as string]: '846px',
        }}
      >
        <b className="c4-tx-s">secret_2</b>
        <span className="c4-tx-b">TX</span>
      </div>

      {/* 12. robbed */}
      <div className={cx('c4-devilw', at('robbed') && 'on')}>
        <DevilHead />
      </div>
      <div
        className={cx('c4-rtx', at('robbed') && 'on')}
        style={{ ['--lx' as string]: `${leafX - 65}px`, ['--ly' as string]: `${LEVEL_Y[0] - 40}px` }}
      >
        <Horns w={130} />
        <span>TX</span>
      </div>
      <svg className={cx('c4-svg c4-lx', at('robbed') && 'on')} viewBox="0 0 1920 1080" aria-hidden="true">
        <path className="mkp" d={wobLine([leafX - 24, LEVEL_Y[0] - 24], [leafX + 24, LEVEL_Y[0] + 24], 2, 81, 2)} strokeWidth={9} />
        <path className="mkp" d={wobLine([leafX + 24, LEVEL_Y[0] - 24], [leafX - 24, LEVEL_Y[0] + 24], 2, 83, 2)} strokeWidth={9} />
      </svg>
      <div className={cx('c4-bits', at('robbed') && 'on')}>
        <div className="c4-bits-l" style={{ left: BIT_X - 170, top: BIT_Y - 34 }}>
          used leaves bitmap
        </div>
        {Array.from({ length: BITS }, (_, i) => (
          <i key={i} className={cx('c4-bit', i === STOLEN && 'used')} style={{ left: BIT_X, top: BIT_Y + i * 17 }} />
        ))}
      </div>
      <CStamp on={at('robbed') && !at('theory')} x={790} y={560} size={170} r={-6} d={3000} className="c4-robbed">
        ROBBED
      </CStamp>

      {/* 13-19. the theoretical problem, the timing attack */}
      <div className={cx('c4-ov', at('theory') && 'on')}>
        <div className="c4-ov-1">
          <b>THEORETICAL</b> problem
        </div>
        <div className={cx('c4-ov-2', at('ed') && 'on')}>and has already broken Ed25519*</div>
        <div className={cx('c4-ov-l', at('copy') && 'on')} style={{ top: 470 }}>
          copy our secret
        </div>
        <div className={cx('c4-ov-l', at('swap') && 'on')} style={{ top: 560 }}>
          swap the destination
        </div>
        <div className={cx('c4-ov-l', at('fee') && 'on')} style={{ top: 650 }}>
          pay a bigger fee
        </div>
        <CStamp on={at('timing')} x={810} y={830} size={110} r={-3} d={40}>
          TIMING ATTACK
        </CStamp>
        <div className={cx('c4-ov-f', at('vault') && 'on')}>The vault does not know the difference.</div>
      </div>
    </>
  );
}

export const C4: SceneDef = {
  key: 'c-v1',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [
    { id: 'hash' },
    { id: 'code' },
    { id: 'program' },
    { id: 'secrets' },
    { id: 'cascade' },
    { id: 'spend' },
    { id: 'rent' },
    { id: 'v2' },
    { id: 'tree' },
    { id: 'shrink' },
    { id: 'tx' },
    { id: 'robbed' },
    { id: 'theory' },
    { id: 'ed' },
    { id: 'copy' },
    { id: 'swap' },
    { id: 'fee' },
    { id: 'timing' },
    { id: 'vault' },
  ],
  C: V1,
};
