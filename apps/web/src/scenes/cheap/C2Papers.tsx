import { CStamp, cx } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import './c2.css';

const GOLD = Math.PI * (3 - Math.sqrt(5));
const CATS = [...story.categories].sort((a, b) => b.n - a.n);
const CELL_W = 143,
  CELL_H = 190;
const FIELD = CATS.map((c, i) => {
  const cx0 = (i % 6) * CELL_W + CELL_W / 2,
    cy0 = Math.floor(i / 6) * CELL_H + CELL_H / 2;
  const dots: [number, number][] = [];
  for (let k = 0; k < c.n; k++) {
    const r = 6.1 * Math.sqrt(k + 0.5),
      a = k * GOLD;
    dots.push([cx0 + r * Math.cos(a), cy0 + r * Math.sin(a)]);
  }
  return { ...c, dots, i };
});
const CRYPTO0 = { x: 5 * CELL_W + CELL_W / 2, y: 2 * CELL_H + CELL_H / 2 };
const DIRECT = story.cryptoSubset.find((r) => r.relevance === 'direct')!.n;
const PR = story.fission;
const ZERO = PR.filter((r) => r.year >= 1942 && r.year <= 1944);

function Chart() {
  const X0 = 20,
    W = 840,
    BASE = 470,
    PX = 105,
    w = W / PR.length;
  const bx0 = X0 + 7 * w,
    bx1 = X0 + 10 * w;
  return (
    <svg className="c2-chart" viewBox="0 0 860 560">
      <rect x={bx0} y={40} width={bx1 - bx0} height={BASE - 40} fill="#ffff00" />
      <text x={(bx0 + bx1) / 2} y={BASE - 30} textAnchor="middle" className="c2-zero">
        0
      </text>
      {PR.map((r, i) => {
        const h = r.share * 100 * PX;
        return (
          <g key={r.year}>
            {r.count > 0 && <rect className="c2-bar" x={X0 + i * w + 8} y={BASE - h} width={w - 16} height={h} style={{ ['--i' as string]: i }} />}
            <text x={X0 + (i + 0.5) * w} y={BASE + 48} textAnchor="middle" className="c2-yr">
              ’{String(r.year).slice(2)}
            </text>
          </g>
        );
      })}
      <line x1={X0} x2={X0 + W} y1={BASE} y2={BASE} stroke="#000" strokeWidth={5} />
    </svg>
  );
}

function Papers({ at }: SceneProps) {
  const fission = at('fission');
  return (
    <>
      <h1 className="ch-title">The missing papers</h1>
      <CStamp on={at('classified')} x={1350} y={92} size={60} d={300}>
        CLASSIFIED
      </CStamp>

      <svg className="c2-field" viewBox="0 0 858 570">
        {FIELD.map((c) => (
          <g key={c.name} style={{ ['--ci' as string]: c.i }} className="c2-cl">
            {c.dots.map(([x, y], k) => (
              <circle key={k} cx={x} cy={y} r={2.7} />
            ))}
          </g>
        ))}
        <g className="c2-crypto">
          <circle cx={CRYPTO0.x} cy={CRYPTO0.y} r={60} />
          <text x={CRYPTO0.x} y={CRYPTO0.y + 16} textAnchor="middle">
            {DIRECT}
          </text>
        </g>
      </svg>
      <div className="c-big c2-capL">
        {story.manuscripts} papers · {story.categories.length} subjects
      </div>

      <ol className={cx('c2-list', fission && 'gone')}>
        {CATS.map((c) => (
          <li key={c.name}>
            {c.name} <b>{c.n}</b>
          </li>
        ))}
        <li className="c2-cryptoli">
          Cryptography <b>{DIRECT}</b>
        </li>
      </ol>

      <div className="c2-fission">
        <Chart />
        <div className="c-mid c2-capR">Physical Review, “fission” papers (% per year)</div>
        <div className="c-mid c2-zl">
          1942–44: 0 of {ZERO.reduce((s, r) => s + r.total, 0)}
        </div>
      </div>
      <CStamp on={fission} x={1590} y={350} size={46} r={-2} d={700}>
        RECEIVED 1941
        <br />
        PUBLISHED 1946
      </CStamp>

      <div className="c2-flash">I had my agents check. It’s true.</div>
      <div className="c-line c2-tally">
        {story.manuscripts} papers reviewed · {story.journalRecords.toLocaleString('en-US')} journal records, {story.histYears[0]}–{story.histYears[1]}
      </div>
      <div className="c-line c2-conc">Draw your own conclusions.</div>
    </>
  );
}

export const C2: SceneDef = {
  key: 'c-papers',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'classified' }, { id: 'dots' }, { id: 'crypto0' }, { id: 'fission' }, { id: 'checked' }, { id: 'hold' }, { id: 'conclude' }],
  C: Papers,
};
