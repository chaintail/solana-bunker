import { Coin, Door } from '../components/Door';
import { cx, Pin, short, Stamp } from '../components/bits';
import { Redact } from '../components/Redact';
import story from '../data/story.json';
import type { SceneDef, SceneProps } from '../types';
import './s3.css';

const DISCLAIMER =
  '*with a properly secured upgrade authority, assuming no bugs in the program, not covering consensus failures, relayer compromise, lost seed phrases, or anything else ChatGPT warned us about.';

// coin stream: start points (stage px) and kinds, flying into the door hub
const COINS = Array.from({ length: 16 }, (_, i) => {
  const row = i % 4;
  return {
    kind: (i % 3 === 1 ? 'usdc' : 'sol') as 'sol' | 'usdc',
    x: -80 - (i % 5) * 46,
    y: 330 + row * 120 + ((i * 37) % 50),
    d: i * 20,
  };
});

function Bunker({ at, instant }: SceneProps) {
  const w = story.withdrawal;
  return (
    <>
      <h1 className="hl">The Solana Bunker</h1>
      <dl className="form">
        <dt>SUBJECT</dt>
        <dd>A vault at a program derived address</dd>
        <dt>ADDRESS</dt>
        <dd>off the Ed25519 curve, no private key</dd>
        <dt>HOLDS</dt>
        <dd>SOL · USDC</dd>
        <dt>SPENDING</dt>
        <dd>hash-based authorization only*</dd>
        <dt>BUILT</dt>
        <dd>three times</dd>
        <dt>PROGRAM</dt>
        <dd>{short(story.program.id, 8, 6)} · devnet</dd>
        <dt>CLEARED FOR</dt>
        <dd>
          <span className="redact" style={{ width: 252, height: 17 }} />
        </dd>
      </dl>

      <div className="vault3">
        <Door className="door3" />
        <Pin x={226} y={72} addr={short(w.treasury, 8, 7)} className="pin3" />
        <div className="contents">
          <Coin kind="sol" size={40} />
          <Coin kind="usdc" size={40} />
          <span>contents</span>
        </div>
      </div>

      <div className="stream" aria-hidden="true">
        {COINS.map((c, i) => (
          <div key={i} className="coin-fly" style={{ ['--x' as string]: `${c.x}px`, ['--y' as string]: `${c.y}px`, ['--d' as string]: `${c.d}ms` }}>
            <Coin kind={c.kind} size={58} />
          </div>
        ))}
      </div>

      <div className={cx('ticker')}>
        <div className="loop tk-run">
          <span>{DISCLAIMER}</span>
          <span>{DISCLAIMER}</span>
        </div>
      </div>

      <Stamp on={at('stamp')} instant={instant} x={600} y={700} size={84} r={-6} d={60}>
        Not your key,
        <br />
        still your coins
      </Stamp>

      <div className={cx('prior', at('prior') && 'go')}>
        <div className="prior-h lbl">Technical file · prior work this builds on</div>
        {story.priorWork.map((p, i) => (
          <a key={p.name} className="src" href={p.url} target="_blank" rel="noreferrer" style={{ ['--i' as string]: i }}>
            <span className="lbl">
              {p.category} · {p.date ?? 'undated'}
            </span>
            <b>{p.name}</b>
            <span className="org">{p.org}</span>
            <span className="desc">{p.description}</span>
            <span className="rel">{p.relation}</span>
          </a>
        ))}
        <div className="src-eq">
          <span className="lbl">SLH-DSA, the stateless sibling</span>
          <Redact eq="slh" w={320} h={20} align="right" drop="up" />
        </div>
      </div>
      <div className={cx('wash', at('prior') && 'go')} />
    </>
  );
}

export const S3: SceneDef = {
  key: 'bunker',
  exhibit: 'Exhibit 3',
  title: 'The vault',
  steps: [{ id: 'vault' }, { id: 'coins' }, { id: 'disclaimer' }, { id: 'stamp' }, { id: 'prior', tech: true }],
  C: Bunker,
};
