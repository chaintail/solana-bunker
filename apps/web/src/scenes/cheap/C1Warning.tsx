import thumb from '../../assets/bankless-thumb-phone.jpg';
import { CStamp, cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { TWEET } from './tweet';
import './c1.css';

/* tweet viewport on the left half */
const VP = { x: 50, y: 40, w: 900, h: 1000 };
const S = VP.w / TWEET.sourceWidth; // source px -> display px
const SCROLL = TWEET.naturalHeight * (VP.w / TWEET.naturalWidth) - VP.h;
const MAG = 1.6;
const [lx0, ly0, lx1, ly1] = TWEET.lens;
const LENS = (() => {
  const w = (lx1 - lx0) * S * MAG,
    h = (ly1 - ly0) * S * MAG;
  const cxs = VP.x + ((lx0 + lx1) / 2) * S,
    cys = VP.y + ((ly0 + ly1) / 2) * S;
  return { left: Math.max(24, cxs - w / 2), top: cys - h / 2, w, h };
})();

export function Arrow({ x1, y1, x2, y2, w = 6, color = '#000' }: { x1: number; y1: number; x2: number; y2: number; w?: number; color?: string }) {
  const a = Math.atan2(y2 - y1, x2 - x1);
  const L = w * 4.2;
  const p = (ang: number) => `${x2 - L * Math.cos(a + ang)},${y2 - L * Math.sin(a + ang)}`;
  return (
    <g>
      <line x1={x1} y1={y1} x2={x2 - (L * 0.7) * Math.cos(a)} y2={y2 - (L * 0.7) * Math.sin(a)} stroke={color} strokeWidth={w} />
      <polygon points={`${x2},${y2} ${p(0.45)} ${p(-0.45)}`} fill={color} />
    </g>
  );
}

function Atom() {
  return (
    <svg viewBox="0 0 160 160" width={160} height={160} aria-hidden="true">
      <g stroke="#000" strokeWidth={6} strokeLinecap="round" className="legs">
        <line className="leg l1" x1={66} y1={112} x2={56} y2={152} />
        <line className="leg l2" x1={94} y1={112} x2={104} y2={152} />
      </g>
      <g fill="none" stroke="#0000ff" strokeWidth={6}>
        <ellipse cx={80} cy={72} rx={70} ry={26} transform="rotate(30 80 72)" />
        <ellipse cx={80} cy={72} rx={70} ry={26} transform="rotate(-30 80 72)" />
      </g>
      <circle cx={80} cy={72} r={22} fill="#ff0000" stroke="#000" strokeWidth={4} />
      <circle cx={73} cy={68} r={4} fill="#fff" />
      <circle cx={87} cy={68} r={4} fill="#fff" />
      <circle cx={142} cy={40} r={7} fill="#0000ff" />
      <circle cx={20} cy={104} r={7} fill="#0000ff" />
    </svg>
  );
}

function Robot() {
  return (
    <svg viewBox="0 0 170 170" width={170} height={170} aria-hidden="true">
      <line x1={85} y1={40} x2={85} y2={10} stroke="#000" strokeWidth={6} />
      <circle cx={85} cy={10} r={9} fill="#ff0000" stroke="#000" strokeWidth={3} />
      <rect x={20} y={40} width={130} height={120} rx={6} fill="#a8a8a8" stroke="#000" strokeWidth={6} />
      <rect x={8} y={80} width={12} height={36} fill="#000" />
      <rect x={150} y={80} width={12} height={36} fill="#000" />
      <circle cx={58} cy={88} r={18} fill="#fff" stroke="#000" strokeWidth={4} />
      <circle cx={112} cy={88} r={18} fill="#fff" stroke="#000" strokeWidth={4} />
      <circle className="pupil" cx={52} cy={90} r={7} fill="#000" />
      <circle className="pupil" cx={106} cy={90} r={7} fill="#000" />
      <rect x={48} y={124} width={74} height={20} fill="#fff" stroke="#000" strokeWidth={4} />
      <path d="M66,124 v20 M85,124 v20 M104,124 v20" stroke="#000" strokeWidth={4} />
    </svg>
  );
}

function Warning({ at }: SceneProps) {
  const diagram = at('diagram');
  return (
    <>
      {/* debate thumbnail (founder's phone screenshot), caption, name */}
      <div className={cx('c1-top', diagram && 'gone')}>
        <img className="c1-thumb" src={thumb} alt="Bankless: Ethereum vs Solana" draggable={false} />
        <p className="c1-cap">This debate is when I first started to believe in Solana.</p>
        <div className="c1-name">
          Justin
          <br />
          Drake
        </div>
        <svg className="c1-svg" viewBox="0 0 1920 1080">
          <Arrow x1={1214} y1={338} x2={1340} y2={314} w={7} />
        </svg>
      </div>

      {/* the tweet: a tall column that scrolls, then a magnifier */}
      <div className={cx('c1-tweet', diagram && 'gone')} style={{ left: VP.x, top: VP.y, width: VP.w, height: VP.h }}>
        <div className="c1-col" style={{ ['--scroll' as string]: `${-SCROLL}px` }}>
          <img src={TWEET.src} alt="Justin Drake's bunker mode post" draggable={false} style={{ width: VP.w }} />
        </div>
      </div>
      <div className={cx('c1-lens', diagram && 'gone')} style={{ left: LENS.left, top: LENS.top, width: LENS.w, height: LENS.h }}>
        <img
          src={TWEET.src}
          alt=""
          draggable={false}
          style={{ width: VP.w * MAG, left: -lx0 * S * MAG, top: -ly0 * S * MAG }}
        />
        {TWEET.highlight.map(([x0, y0, x1, y1], i) => (
          <i
            key={i}
            className="c1-hl"
            style={{ left: (x0 - lx0) * S * MAG, top: (y0 - ly0) * S * MAG, width: (x1 - x0) * S * MAG, height: (y1 - y0) * S * MAG, ['--i' as string]: i }}
          />
        ))}
      </div>

      {/* the cheesy diagram */}
      <div className="c1-diag">
        <div className="c1-fancy">fancy math</div>
        <div className="c1-eq">
          y<sup>2</sup> = x<sup>3</sup> + ax + b
        </div>
        <svg className="c1-svg c1-arrows" viewBox="0 0 1920 1080">
          <path className="scrib" d="M110,250 C100,190 260,168 400,170 C560,172 700,195 690,248 C682,300 540,322 390,318 C250,316 96,300 118,236 C126,214 170,200 210,196" />
          <g className="a1">
            <Arrow x1={470} y1={330} x2={548} y2={392} />
          </g>
          <g className="a2">
            <Arrow x1={760} y1={545} x2={610} y2={700} />
          </g>
          <g className="a3">
            <Arrow x1={1160} y1={545} x2={1310} y2={700} />
          </g>
        </svg>
        <div className="c1-box">ELLIPTIC CURVES</div>
        <div className="c1-ecdsa">
          <svg viewBox="0 0 100 160" width={100} height={160} aria-hidden="true">
            <polygon points="50,0 100,80 50,108 0,80" fill="#555" stroke="#000" strokeWidth={4} />
            <polygon points="50,118 100,90 50,160 0,90" fill="#888" stroke="#000" strokeWidth={4} />
          </svg>
          <span>ECDSA</span>
        </div>
        <div className="c1-ed">
          <span>Ed25519</span>
          <svg viewBox="0 0 140 120" width={140} height={120} aria-hidden="true">
            <polygon points="24,4 136,4 116,30 4,30" fill="#9945ff" stroke="#000" strokeWidth={3} />
            <polygon points="4,46 116,46 136,72 24,72" fill="#14f195" stroke="#000" strokeWidth={3} />
            <polygon points="24,88 136,88 116,114 4,114" fill="#9945ff" stroke="#000" strokeWidth={3} />
          </svg>
        </div>
        <div className="c1-atom">
          <div className="c1-atom-b">
            <Atom />
          </div>
        </div>
        <div className="c1-robot">
          <Robot />
        </div>
      </div>

      <CStamp on={at('drill')} x={960} y={950} size={110} r={-1.5} d={40}>
        THIS IS A DRILL
      </CStamp>
    </>
  );
}

export const C1: SceneDef = {
  key: 'c-warning',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'debate' }, { id: 'tweet' }, { id: 'scroll' }, { id: 'magnify' }, { id: 'diagram' }, { id: 'atom' }, { id: 'robot' }, { id: 'drill' }],
  C: Warning,
};
