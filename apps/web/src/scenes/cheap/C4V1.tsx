import { CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Highlights, Lens, wobEllipse, wobLine } from './mix';
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
const N = 1024,
  COLS = 32;
const CELL = 20,
  GAP = 3;
const GX = 1063,
  GY = 272; // grid origin
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
const HAND: [number, number] = [262, 250];

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

function V1({ at, cur }: SceneProps) {
  const cells = [];
  for (let k = 0; k < N; k++) {
    const [x, y] = cellXY(k);
    cells.push(<i key={k} className={cx('c4-cell', k === 0 && 'c4-c0')} style={{ left: x, top: y, ['--d' as string]: `${tFill(k) + 900}ms`, ['--g' as string]: `${Math.floor(k / COLS) * 18}ms` }} />);
  }
  const [c0x, c0y] = cellXY(0);
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
        <pre className="c4-code-b">
          {'use solana_program::hash::hashv;\n\nlet h = hashv(&[secret]);'}
        </pre>
      </div>

      {/* 3. stick figure, the program, SOL flying in */}
      <div className={cx('c4-prog', at('program') && 'on')}>
        <StickFigure />
        <div className="c4-rect">
          <div className="c4-rect-t">Bunker Program 001</div>
        </div>
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} className={cx('c4-coin', i === 0 && 'c4-coin0')} style={{ ['--x' as string]: `${1600 + i * 48}px`, ['--d' as string]: `${300 + i * 160}ms` }}>
            <SolCoin />
          </div>
        ))}
      </div>

      {/* 4. the secrets, the grid */}
      <div className={cx('c4-list', at('secrets') && 'on', at('cascade') && 'dim')}>
        {LIST.map((s, i) => (
          <div key={i} className={cx('c4-li', i === 0 && 'first')} style={{ top: LY + i * LH, left: LX, ['--d' as string]: `${i * 90}ms` }}>
            {s}
          </div>
        ))}
      </div>
      <div className={cx('c4-grid', at('secrets') && 'on', at('cascade') && 'full')}>{cells}</div>

      {/* 5. cascade through MATH */}
      <div className={cx('c4-math', at('cascade') && 'on')} style={{ left: MATH.x, top: MATH.y, width: MATH.w, height: MATH.h }}>
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
      <svg className={cx('c4-svg c4-cross', at('spend') && 'on')} viewBox="0 0 1920 1080" aria-hidden="true">
        <path className="mkp" d={wobLine([c0x - 14, c0y - 14], [c0x + CELL + 14, c0y + CELL + 14], 2, 71, 2)} strokeWidth={8} />
        <path className="mkp" d={wobLine([c0x + CELL + 14, c0y - 14], [c0x - 14, c0y + CELL + 14], 2, 73, 2)} strokeWidth={8} />
      </svg>
      <div className={cx('c4-back', at('spend') && 'on')} style={{ ['--fx' as string]: '1600px', ['--fy' as string]: '146px', ['--tx' as string]: `${HAND[0] - 4}px`, ['--ty' as string]: `${HAND[1] - 34}px` }}>
        <SolCoin size={68} />
      </div>
      <CStamp on={at('spend')} x={620} y={420} size={56} r={-3} d={2500} className="c4-ok">
        SECRET ACCEPTED
      </CStamp>

      {/* 7. the bill */}
      <div className={cx('c4-rent', at('rent') && 'on')}>
        <div className="c4-rent-b">RENT: 0.234 SOL</div>
        <div className="c4-rent-s">38 transactions to set up</div>
      </div>
    </>
  );
}

export const C4: SceneDef = {
  key: 'c-v1',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'hash' }, { id: 'code' }, { id: 'program' }, { id: 'secrets' }, { id: 'cascade' }, { id: 'spend' }, { id: 'rent' }],
  C: V1,
};
