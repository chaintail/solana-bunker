import { CStamp, short } from '../../components/bits';
import story from '../../data/story.json';
import type { SceneDef, SceneProps } from '../../types';
import { Coin, Vault } from './clip';
import './c3.css';

const DISCLAIMER =
  '*with a properly secured upgrade authority, assuming no bugs in the program, not covering consensus failures, relayer compromise, lost seed phrases, or anything else ChatGPT warned us about.';
const COINS = Array.from({ length: 10 }, (_, i) => ({ kind: (i % 3 === 1 ? 'USDC' : 'SOL') as 'SOL' | 'USDC', y: 260 + ((i * 97) % 420), d: i * 40 }));

function Bunker({ at }: SceneProps) {
  return (
    <>
      <h1 className="ch-title">We made a Solana Bunker</h1>
      <ul className="c-bullets c3-list">
        <li>A vault at a program derived address</li>
        <li>No private key behind it</li>
        <li>Holds SOL and USDC*</li>
        <li>We built it three times</li>
      </ul>
      <div className="c3-vault">
        <Vault size={380} />
        <div className="c3-addr">{short(story.withdrawal.treasury, 8, 7)}</div>
      </div>
      <div className="c3-coins" aria-hidden="true">
        {COINS.map((c, i) => (
          <div key={i} className="c3-coin" style={{ ['--y' as string]: `${c.y}px`, ['--d' as string]: `${c.d}ms` }}>
            <Coin kind={c.kind} size={100} />
          </div>
        ))}
      </div>
      <div className="c3-ticker">
        <div className="loop c3-run">
          <span>{DISCLAIMER}</span>
          <span>{DISCLAIMER}</span>
        </div>
      </div>
      <CStamp on={at('stamp')} x={640} y={740} size={84} r={-1.5} d={40}>
        NOT YOUR KEY,
        <br />
        STILL YOUR COINS
      </CStamp>
    </>
  );
}

export const C3: SceneDef = {
  key: 'c-bunker',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'vault' }, { id: 'coins' }, { id: 'disclaimer' }, { id: 'stamp' }],
  C: Bunker,
};
