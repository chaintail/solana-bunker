import { cx } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import { CLUSTERS, CRYPTO, DOT, FH, FW } from '../S2Conspiracy';
import { Ins, paintArrow, rng, wobEllipse } from './mix';
import './c2.css';

/* ---------- right half: the polished dossier cluster, as is ---------- */
const FX = 1000,
  FY = 150; // field origin on the stage
const CX = FX + CRYPTO.x,
  CY = FY + CRYPTO.y;
const DIRECT = story.cryptoSubset.find((r) => r.relevance === 'direct')!.n;

/* ---------- left half: the timeline, one bar of cover pages per year ---------- */
const YEARS = story.fission.filter((r) => r.year >= 1936);
const AX = 120,
  AX1 = 940,
  BASE = 742,
  TOP = 300;
const SLOT = (AX1 - AX) / YEARS.length;
const PITCH = Math.floor((BASE - TOP - 14) / Math.max(...YEARS.map((r) => r.count))); // px per paper
const PER_YEAR = 420; // ms, the same for every year
const PAGE_W = 50;
const STICKY_YEAR = 1946;

function Timeline({ on, built }: { on: boolean; built: boolean }) {
  const r = rng(77);
  return (
    <div className={cx('c2-tl', on && 'on', built && 'built')}>
      <div className="c2-tl-cap">
        <b>Physical Review</b>
        <br />
        papers with “fission” in the title
      </div>
      <svg className="c2-axes" viewBox="0 0 1920 1080" aria-hidden="true">
        <path className="c2-ax" d={`M${AX},${TOP - 10} V${BASE}`} pathLength={1} />
        <path className="c2-ax" d={`M${AX},${BASE} H${AX1 + 8}`} pathLength={1} style={{ ['--d' as string]: '250ms' }} />
      </svg>
      {YEARS.map((y, i) => {
        const x = AX + i * SLOT + (SLOT - PAGE_W) / 2;
        const t0 = i * PER_YEAR;
        const pages = [];
        for (let k = 0; k < y.count; k++) {
          const dx = (r() - 0.5) * 5,
            rot = (r() - 0.5) * 4;
          pages.push(
            <i
              key={k}
              className={cx('c2-pg', y.year === STICKY_YEAR && k === 3 && 'mark')}
              style={{
                left: x + dx,
                top: BASE - (k + 1) * PITCH,
                height: PITCH - 3,
                ['--rot' as string]: `${rot.toFixed(2)}deg`,
                ['--d' as string]: `${Math.round(t0 + (k * (PER_YEAR - 140)) / Math.max(1, y.count))}ms`,
              }}
            />,
          );
        }
        return (
          <div key={y.year} className={cx('c2-yr', !y.count && 'z')}>
            {pages}
            {y.count > 0 && (
              <span className="c2-n" style={{ left: AX + i * SLOT, width: SLOT, top: BASE - y.count * PITCH - 52, ['--d' as string]: `${t0 + PER_YEAR - 120}ms` }}>
                {y.count}
              </span>
            )}
            <span className="c2-yl" style={{ left: AX + i * SLOT - 6, width: SLOT + 12, ['--d' as string]: `${120 + i * 45}ms`, ['--sd' as string]: `${t0}ms` }}>
              ’{String(y.year).slice(2)}
            </span>
          </div>
        );
      })}
      <div className="c2-note" style={{ ['--d' as string]: `${YEARS.length * PER_YEAR + 150}ms` }}>
        received 1941,
        <br />
        published 1946
      </div>
    </div>
  );
}

const CIRCLE = wobEllipse(CX, CY, 74, 64, 23);
const QARROW = paintArrow([CX - 210, CY + 150], [CX - 70, CY + 40], 31, 40, 6);

function Papers({ at }: SceneProps) {
  const proverb = at('proverb');
  return (
    <>
      {/* the polished cluster on parchment */}
      <div className={cx('c2-panel', proverb && 'gone')}>
        <div className="paper mottle" />
        <div className="paper grain" />
      </div>
      <div className={cx('c2-fieldw', proverb && 'gone')}>
        <svg className="field" viewBox={`0 0 ${FW} ${FH}`} style={{ left: FX, top: FY }}>
          {CLUSTERS.map((c, ci) => (
            <g key={c.name} className="cl" style={{ ['--ci' as string]: ci }}>
              {c.dots.map(([x, y], k) => (
                <circle key={k} className="dot" cx={x} cy={y} r={DOT} style={{ ['--k' as string]: k % 97 }} />
              ))}
              {c.lines.map((l, li) => (
                <text key={li} className="cl-l" x={c.x} y={c.y + c.R + 18 + li * 16} textAnchor="middle">
                  {l}
                </text>
              ))}
            </g>
          ))}
          <text className="crypto-l" x={CRYPTO.x} y={CRYPTO.y + CRYPTO.R + 22} textAnchor="middle">
            cryptography · {DIRECT}
          </text>
        </svg>
        <div className="c2-fcap">
          {story.manuscripts} papers · {story.categories.length} disciplines
        </div>
      </div>

      {/* cheap: wobbly red circle, arrow, ??? */}
      <div className={cx('c2-q', at('crypto0') && !proverb && 'on')}>
        <svg className="c2-svg" viewBox="0 0 1920 1080" aria-hidden="true">
          <path className="mkp draw1" d={CIRCLE} pathLength={1} strokeWidth={9} style={{ ['--dur' as string]: '520ms' }} />
          {QARROW.map((d, i) => (
            <path key={i} className="mkp draw1" d={d} pathLength={1} strokeWidth={9} style={{ ['--d' as string]: `${560 + i * 120}ms`, ['--dur' as string]: '220ms' }} />
          ))}
        </svg>
        <div className="mk c2-qq" style={{ left: CX - 470, top: CY + 120 }}>
          ???
        </div>
        <div className="mk c2-qw" style={{ left: CX - 680, top: CY + 244 }}>
          cryptography
        </div>
      </div>

      <Timeline on={at('axes')} built={at('bars')} />

      {/* trust, but verify */}
      <div className={cx('c2-prov', proverb && 'on')}>
        <div className="c2-dov">Doveryai, no proveryai</div>
        <div className="c2-cyr">Доверяй, но проверяй</div>
        <div className="c2-rp">Russian proverb</div>
        <div className="c2-tr">
          <span className="c2-trl">Translation:</span>
          <br />
          “trust, but
          <Ins on={at('agents')} word="have agents" className="c2-ins" />
          verify”
        </div>
      </div>

      <div className={cx('c2-big c2-b1', at('checked') && 'on')}>
        {story.journalRecords.toLocaleString('en-US')} records checked, {story.histYears[0]} to {story.histYears[1]}
      </div>
      <div className={cx('c2-big c2-b2', at('papers') && 'on')}>{story.manuscripts} papers, 2026</div>
    </>
  );
}

export const C2: SceneDef = {
  key: 'c-papers',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'dots' }, { id: 'crypto0' }, { id: 'axes' }, { id: 'bars' }, { id: 'proverb' }, { id: 'agents' }, { id: 'checked' }, { id: 'papers' }],
  C: Papers,
};
