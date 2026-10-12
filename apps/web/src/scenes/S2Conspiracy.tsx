import { cx, Stamp } from '../components/bits';
import story from '../data/story.json';
import type { SceneDef, SceneProps } from '../types';
import './s2.css';

/* ---------- 719 manuscripts as dots, clustered by discipline ---------- */
const FW = 880,
  FH = 600; // field, local coords
const DOT = 3.1,
  SP = 7.2; // dot radius, sunflower spacing
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
const CRYPTO = { x: 812, y: 470, R: 34 };

const CLUSTERS: Cl[] = (() => {
  const placed: { x0: number; y0: number; x1: number; y1: number }[] = [];
  // the empty cryptography slot sits at the edge; reserve it first
  placed.push({ x0: CRYPTO.x - 80, y0: CRYPTO.y - CRYPTO.R - 8, x1: FW, y1: CRYPTO.y + CRYPTO.R + 46 });
  const res: Cl[] = [];
  const cats = [...story.categories].sort((a, b) => b.n - a.n);
  for (const c of cats) {
    const R = SP * Math.sqrt(c.n) + DOT + 2;
    const lines = wrap(c.name, 20);
    lines[lines.length - 1] += ` · ${c.n}`;
    const lw = Math.max(...lines.map((l) => l.length)) * CH;
    const bw = Math.max(2 * R, lw) + 16,
      bh = 2 * R + 10 + lines.length * 16 + 12;
    let done = false;
    for (let t = 0; t < 4000 && !done; t += 0.35) {
      const r = 3.6 * t;
      const x = FW * 0.47 + r * Math.cos(t),
        y = FH * 0.47 + r * Math.sin(t) * 0.7;
      const box = { x0: x - bw / 2, y0: y - R - 6, x1: x + bw / 2, y1: y - R - 6 + bh };
      if (box.x0 < 0 || box.y0 < 0 || box.x1 > FW || box.y1 > FH) continue;
      if (placed.some((p) => !(box.x1 < p.x0 || box.x0 > p.x1 || box.y1 < p.y0 || box.y0 > p.y1))) continue;
      placed.push(box);
      const dots: [number, number][] = [];
      for (let k = 0; k < c.n; k++) {
        const rr = SP * Math.sqrt(k + 0.5),
          a = k * GOLD;
        dots.push([x + rr * Math.cos(a), y + rr * Math.sin(a)]);
      }
      res.push({ name: c.name, n: c.n, x, y, R, lines, dots });
      done = true;
    }
  }
  return res;
})();

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
      <Stamp on={at('classified')} instant={instant} x={1574} y={146} size={84} r={-8} d={420}>
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
