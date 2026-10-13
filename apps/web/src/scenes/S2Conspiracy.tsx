import { cx, Stamp } from '../components/bits';
import story from '../data/story.json';
import type { SceneDef, SceneProps } from '../types';
import './s2.css';

/* ---------- 719 manuscripts as dots, clustered by discipline ---------- */
export const FW = 880,
  FH = 600; // field, local coords
export const DOT = 2.9,
  SP = 6.4; // dot radius, sunflower spacing
const GOLD = Math.PI * (3 - Math.sqrt(5));
const CH = 7.9; // mono char width at 13px

function wrap(s: string, max = 19) {
  const out: string[] = [];
  let line = '';
  for (const w of s.split(' ')) {
    if (line && (line + ' ' + w).length > max) {
      out.push(line);
      line = w;
    } else line = line ? line + ' ' + w : w;
  }
  out.push(line);
  return out;
}

type Cl = { name: string; n: number; x: number; y: number; R: number; lines: string[]; dots: [number, number][] };

/*
 * Shelf packing: clusters sorted by size fill rows left to right, each row is
 * centred, rows are spread over the field height. Every discipline is placed
 * (no silent drops); the empty cryptography slot closes the last row, at the edge.
 */
const PACK = (() => {
  const cats = [...story.categories].sort((a, b) => b.n - a.n);
  type Item = { name: string; n: number; R: number; lines: string[]; w: number; h: number; crypto?: boolean };
  const items: Item[] = cats.map((c) => {
    const R = SP * Math.sqrt(c.n) + DOT + 2;
    const lines = wrap(c.name, 18);
    lines[lines.length - 1] += ` · ${c.n}`;
    const lw = Math.max(...lines.map((l) => l.length)) * CH;
    return { name: c.name, n: c.n, R, lines, w: Math.max(2 * R, lw) + 14, h: 2 * R + lines.length * 16 + 22 };
  });
  items.push({ name: 'cryptography', n: 0, R: 34, lines: [], w: 150, h: 68 + 38, crypto: true });
  const rows: Item[][] = [];
  let row: Item[] = [],
    rw = 0;
  for (const it of items) {
    if (row.length && rw + it.w > FW) {
      rows.push(row);
      row = [];
      rw = 0;
    }
    row.push(it);
    rw += it.w;
  }
  rows.push(row);
  const heights = rows.map((r) => Math.max(...r.map((i) => i.h)));
  const gapY = Math.max(0, (FH - heights.reduce((s, h) => s + h, 0)) / (rows.length + 1));
  const res: Cl[] = [];
  let crypto = { x: FW - 70, y: FH - 80, R: 34 };
  let y0 = gapY;
  rows.forEach((r, ri) => {
    const used = r.reduce((s, i) => s + i.w, 0);
    const gapX = (FW - used) / (r.length + 1);
    let x0 = gapX;
    for (const it of r) {
      const x = x0 + it.w / 2,
        y = y0 + it.R + 4;
      if (it.crypto) crypto = { x: FW - it.w / 2, y, R: it.R };
      else {
        const dots: [number, number][] = [];
        for (let k = 0; k < it.n; k++) {
          const rr = SP * Math.sqrt(k + 0.5),
            a = k * GOLD;
          dots.push([x + rr * Math.cos(a), y + rr * Math.sin(a)]);
        }
        res.push({ name: it.name, n: it.n, x, y, R: it.R, lines: it.lines, dots });
      }
      x0 += it.w + gapX;
    }
    y0 += heights[ri] + gapY;
  });
  return { clusters: res, crypto, overflow: y0 - gapY > FH + 0.5 };
})();
export const CLUSTERS = PACK.clusters;
export const CRYPTO = PACK.crypto;
if (CLUSTERS.length !== story.categories.length || PACK.overflow) console.error('beat 2 cluster packing failed', CLUSTERS.length, PACK.overflow);

/* ---------- Physical Review fission chart (ported from the mockup's Fig. A-1) ---------- */
function FissionChart() {
  const PR = story.fission;
  const X0 = 70,
    X1 = 812,
    BASE = 468,
    PX = 84,
    w = (X1 - X0) / PR.length;
  const bx0 = X0 + 7 * w,
    bx1 = X0 + 10 * w;
  const zeroBand = PR.filter((r) => r.year >= 1942 && r.year <= 1944);
  const zeroTotal = zeroBand.reduce((s, r) => s + r.total, 0);
  return (
    <svg className="chart" viewBox="0 0 824 580">
      <text x={X0 - 12} y={26} className="tk" style={{ letterSpacing: '.14em' }}>
        % OF RECORDS
      </text>
      {[1, 2, 3, 4].map((k) => (
        <g key={k}>
          <line className="gl" x1={X0} x2={X1} y1={BASE - k * PX} y2={BASE - k * PX} />
          <text className="tk" x={X0 - 12} y={BASE - k * PX + 5} textAnchor="end">
            {k}
          </text>
        </g>
      ))}
      <g className="band">
        <rect x={bx0} y={44} width={bx1 - bx0} height={BASE - 44} fill="url(#hatch)" />
        <path d={`M${bx0 + 4},${BASE + 46} v8 H${bx1 - 4} v-8`} fill="none" stroke="#b3242a" strokeWidth={1.4} />
        <text className="zl" x={(bx0 + bx1) / 2} y={BASE + 78} textAnchor="middle">
          0 of {zeroTotal} records
        </text>
      </g>
      {PR.map((r, i) => {
        const s = r.share * 100,
          cxp = X0 + (i + 0.5) * w,
          bw = 32,
          hgt = s * PX,
          dl = 80 + i * 45;
        return (
          <g key={r.year}>
            {r.count > 0 && <rect className="fbar" style={{ ['--d' as string]: `${dl}ms` }} x={cxp - bw / 2} y={BASE - hgt} width={bw} height={hgt} />}
            <text className={cx('vb', !r.count && 'z')} style={{ ['--d' as string]: `${dl + 380}ms` }} x={cxp} y={r.count ? BASE - hgt - 10 : BASE - 9} textAnchor="middle">
              {r.count ? s.toFixed(1) : '0'}
            </text>
            <text className="yr" x={cxp} y={BASE + 28} textAnchor="middle">
              {r.year}
            </text>
          </g>
        );
      })}
      <line className="ax" x1={X0 - 6} x2={X1} y1={BASE} y2={BASE} />
    </svg>
  );
}

function Conspiracy({ at, instant }: SceneProps) {
  const total = story.manuscripts;
  let di = 0;
  return (
    <>
      <h1 className="hl">The missing papers</h1>
      <Stamp on={at('classified')} instant={instant} x={1636} y={198} size={76} r={-8} d={420}>
        Classified
      </Stamp>

      <div className="field-wrap">
        <svg className="field" viewBox={`0 0 ${FW} ${FH}`}>
          {CLUSTERS.map((c, ci) => (
            <g key={c.name} className="cl" style={{ ['--ci' as string]: ci }}>
              {c.dots.map(([x, y], k) => (
                <circle key={k} className="dot" cx={x} cy={y} r={DOT} style={{ ['--k' as string]: (di++ % 97) + k * 0 }} />
              ))}
              {c.lines.map((l, li) => (
                <text key={li} className="cl-l" x={c.x} y={c.y + c.R + 18 + li * 16} textAnchor="middle">
                  {l}
                </text>
              ))}
            </g>
          ))}
          <g className="crypto">
            <circle className="crypto-c" cx={CRYPTO.x} cy={CRYPTO.y} r={CRYPTO.R} pathLength={1} />
            <text className="crypto-l" x={CRYPTO.x} y={CRYPTO.y + CRYPTO.R + 22} textAnchor="middle">
              cryptography · {story.cryptoSubset.find((r) => r.relevance === 'direct')!.n}
            </text>
          </g>
        </svg>
        <div className="cap capL">
          <span className="fig">FIG. 2-A · OPENAI MATHEMATICS RELEASE, BY PRIMARY DISCIPLINE</span>
          {total} manuscripts · {story.categories.length} disciplines
        </div>
      </div>

      <div className="fission">
        <FissionChart />
        <div className="cap capR">
          <span className="fig">FIG. 2-B · PHYSICAL REVIEW, “FISSION” IN THE TITLE, 1935–1947</span>
          share of journal records per year
        </div>
        <div className="foot">
          <i>†</i>Properties of 94(239), Phys. Rev. 70, 555
        </div>
      </div>
      <Stamp on={at('fission')} instant={instant} x={1530} y={452} size={30} r={-7} d={900} className="st-pu">
        Received<big>1941</big>
        <span className="rl" />
        Published
        <big>
          1946<sup>†</sup>
        </big>
      </Stamp>

      <div className="telegram">
        <span>I had my agents check. It’s true.</span>
      </div>
      <p className="tally">
        {total} papers reviewed · {story.journalRecords.toLocaleString('en-US')} journal records, {story.histYears[0]}–{story.histYears[1]}
      </p>
      <p className="conclude">Draw your own conclusions.</p>
    </>
  );
}

export const S2: SceneDef = {
  key: 'conspiracy',
  exhibit: 'Exhibit 2',
  title: 'Publication record',
  steps: [{ id: 'classified' }, { id: 'dots' }, { id: 'crypto0' }, { id: 'fission' }, { id: 'checked' }, { id: 'hold' }, { id: 'conclude' }],
  C: Conspiracy,
};
