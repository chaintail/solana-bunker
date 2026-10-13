import thumb from '../../assets/bankless-thumb-phone.jpg';
import { CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Highlights, Ins, Lens, paintArrow, wobLine } from './mix';
import { TWEET } from './tweet';
import './c1.css';

/* plain arrow, still used by later cheap slides */
export function Arrow({ x1, y1, x2, y2, w = 6, color = '#000' }: { x1: number; y1: number; x2: number; y2: number; w?: number; color?: string }) {
  const a = Math.atan2(y2 - y1, x2 - x1);
  const L = w * 4.2;
  const p = (ang: number) => `${x2 - L * Math.cos(a + ang)},${y2 - L * Math.sin(a + ang)}`;
  return (
    <g>
      <line x1={x1} y1={y1} x2={x2 - L * 0.7 * Math.cos(a)} y2={y2 - L * 0.7 * Math.sin(a)} stroke={color} strokeWidth={w} />
      <polygon points={`${x2},${y2} ${p(0.45)} ${p(-0.45)}`} fill={color} />
    </g>
  );
}

/* the tweet column on the left */
const COL = { x: 50, y: 120, w: 680, h: 920 };
const CK = COL.w / TWEET.column.w; // column px -> stage px
const SK = COL.w / TWEET.sourceWidth; // source px -> stage px
const BOTTOM = -(TWEET.column.h * CK - COL.h);
const SCROLL: Record<string, number> = { debate: 0, bunker: 0, fresh: -150, diagram: -150 };
const scrollFor = (cur: string) => SCROLL[cur] ?? BOTTOM;

/* the lenses, right of the column */
const LX = 780,
  LW = 1100;
const REPLY_REGION: [number, number, number, number] = [150, TWEET.reply.region[1], 1290, TWEET.reply.region[3]];

/** focus box on the column for a source region (topInColumn: where that screenshot starts, column px) */
function focusRect(region: number[], topInColumn: number, scroll: number) {
  const [x0, y0, x1, y1] = region;
  return { left: COL.x + x0 * SK, top: COL.y + topInColumn * CK + y0 * SK + scroll, width: (x1 - x0) * SK, height: (y1 - y0) * SK };
}

const NAME_ARROW = paintArrow([560, 470], [905, 500], 11, 70, 12);
const X_STROKES = [wobLine([800, 590], [1560, 840], 14, 41, 5), wobLine([790, 836], [1570, 604], 14, 43, 5)];

function GoldBars() {
  const bar = (x: number, y: number, k: number) => (
    <g key={k} transform={`translate(${x},${y})`}>
      <polygon points="30,0 190,0 210,22 10,22" fill="#ffe36b" stroke="#000" strokeWidth={4} strokeLinejoin="round" />
      <polygon points="10,22 210,22 220,84 0,84" fill="#f2b705" stroke="#000" strokeWidth={4} strokeLinejoin="round" />
      <text x={110} y={66} textAnchor="middle" fontFamily="Arial, Helvetica, sans-serif" fontWeight={700} fontSize={30} fill="#8a6000">
        GOLD
      </text>
    </g>
  );
  return (
    <svg className="c1-gold" viewBox="0 0 700 300" width={700} height={300} aria-hidden="true">
      {[bar(0, 216, 1), bar(232, 216, 2), bar(464, 216, 3), bar(116, 132, 4), bar(348, 132, 5), bar(232, 48, 6)]}
      <path d="M600,40 l10,-28 l10,28 l28,10 l-28,10 l-10,28 l-10,-28 l-28,-10 z" fill="#fff" stroke="#000" strokeWidth={3} />
      <path d="M70,110 l7,-20 l7,20 l20,7 l-20,7 l-7,20 l-7,-20 l-20,-7 z" fill="#fff" stroke="#000" strokeWidth={3} />
    </svg>
  );
}

function Warning({ at, cur }: SceneProps) {
  const sc = scrollFor(cur);
  const fBunker = focusRect(TWEET.bunker.region, 0, 0);
  const fFresh = focusRect(TWEET.fresh.region, 0, SCROLL.fresh);
  const fReply = focusRect(REPLY_REGION, TWEET.replyTop, BOTTOM);
  const focus = cur === 'bunker' ? fBunker : cur === 'fresh' ? fFresh : cur === 'reply' ? fReply : null;
  const late = at('broken');
  return (
    <>
      {/* 1. the debate thumbnail, the name, the sticky note */}
      <div className={cx('c1-debate', at('bunker') && 'gone')}>
        <img className="c1-thumb" src={thumb} alt="Bankless: Ethereum vs Solana" draggable={false} />
        <div className="c1-name">
          Justin
          <br />
          Drake
        </div>
        <svg className="c1-svg" viewBox="0 0 1920 1080" aria-hidden="true">
          {NAME_ARROW.map((d, i) => (
            <path key={i} className="mkp c1-paint" d={d} strokeWidth={16} />
          ))}
        </svg>
        <div className="sticky c1-sticky">This debate is when I first started to believe in Solana</div>
      </div>

      {/* 2. the tweet column */}
      <div className={cx('c1-col', at('bunker') && !late && 'on')} style={{ left: COL.x, top: COL.y, width: COL.w, height: COL.h }}>
        <img src={TWEET.column.src} alt="Justin Drake's bunker mode post" draggable={false} style={{ width: COL.w, transform: `translateY(${sc}px)` }} />
      </div>
      <i className={cx('c1-focus', focus && 'on')} style={focus ?? fBunker} />

      <Lens
        className={cx(cur === 'bunker' && 'on')}
        img={TWEET.lens1.src}
        imgW={TWEET.lens1.w}
        imgH={TWEET.lens1.h}
        origin={TWEET.lens1.origin}
        region={TWEET.bunker.region}
        width={LW}
        x={LX}
        y={150}
        over={<Highlights lines={TWEET.bunker.lines} seed={5} />}
      />
      <Lens
        className={cx(cur === 'fresh' && 'on')}
        img={TWEET.lens1.src}
        imgW={TWEET.lens1.w}
        imgH={TWEET.lens1.h}
        origin={TWEET.lens1.origin}
        region={TWEET.fresh.region}
        width={LW}
        x={LX}
        y={190}
        over={<Highlights lines={TWEET.fresh.lines} seed={9} />}
      />

      {/* 3. Ethereum vs Solana, polished, with a cheap marker X */}
      <div className={cx('c1-diag', cur === 'diagram' && 'on')}>
        <div className="c1-row-l" style={{ top: 150 }}>
          Ethereum
        </div>
        <div className="c1-node eth" style={{ left: 800, top: 236, width: 270 }}>
          key
        </div>
        <div className="c1-node eth" style={{ left: 1170, top: 236, width: 270, ['--d' as string]: '150ms' }}>
          hash
        </div>
        <div className="c1-node eth" style={{ left: 1540, top: 236, width: 340, ['--d' as string]: '300ms' }}>
          address
        </div>
        <div className="c1-sub" style={{ top: 378 }}>
          key stays hidden behind the hash
        </div>
        <div className="c1-row-l" style={{ top: 530 }}>
          Solana
        </div>
        <div className="c1-node sol" style={{ left: 800, top: 616, width: 270, ['--d' as string]: '500ms' }}>
          key
        </div>
        <div className="c1-eq" style={{ ['--d' as string]: '600ms' }}>=</div>
        <div className="c1-node sol" style={{ left: 1210, top: 616, width: 340, ['--d' as string]: '650ms' }}>
          address
        </div>
        <div className="c1-sub" style={{ top: 758, ['--d' as string]: '700ms' }}>
          the address is the key
        </div>
        <svg className="c1-svg" viewBox="0 0 1920 1080" aria-hidden="true">
          <g className="c1-arr">
            <path d="M1082,296 H1156 M1142,284 L1158,296 L1142,308" />
            <path d="M1452,296 H1526 M1512,284 L1528,296 L1512,308" />
          </g>
          {X_STROKES.map((d, i) => (
            <path key={i} className="mkp draw1 c1-x" d={d} pathLength={1} strokeWidth={24} style={{ ['--d' as string]: `${1300 + i * 380}ms`, ['--dur' as string]: '340ms' }} />
          ))}
        </svg>
      </div>

      {/* 4. the first reply */}
      <Lens
        className={cx(cur === 'reply' && 'on', 'c1-lens7')}
        img={TWEET.lens7.src}
        imgW={TWEET.lens7.w}
        imgH={TWEET.lens7.h}
        origin={TWEET.lens7.origin}
        region={REPLY_REGION}
        width={LW}
        x={LX}
        y={190}
      />

      {/* 5. sell it all for gold */}
      <div className={cx('c1-goldw', cur === 'gold' && 'on')}>
        <GoldBars />
        <div className="c1-goldt">Sell it all for gold?</div>
      </div>

      {/* 6. nothing is broken; this is all (conspiracy) theoretical */}
      <CStamp on={late} x={960} y={400} size={128} r={-2} d={40}>
        NOTHING IS BROKEN
      </CStamp>
      <div className={cx('c1-well', late && 'on')}>(well, until quantum)</div>
      <div className={cx('c1-theory', at('theory') && 'on')}>
        This is all
        <Ins on={at('theory')} word="conspiracy" className="c1-ins" />
        theoretical
      </div>
    </>
  );
}

export const C1: SceneDef = {
  key: 'c-warning',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'debate' }, { id: 'bunker' }, { id: 'fresh' }, { id: 'diagram' }, { id: 'reply' }, { id: 'gold' }, { id: 'broken' }, { id: 'theory' }],
  C: Warning,
};
