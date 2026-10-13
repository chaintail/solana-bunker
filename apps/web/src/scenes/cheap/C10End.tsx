import { cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Vault } from './clip';
import { Ins, wobEllipse, wobLine } from './mix';
import { LogoMark, QR } from './proof';
import './c10end.css';

const WHITEPAPER = 'https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md';
const LINES = ['Thanks for sticking around.', 'If you made it this far,', 'And you didn’t fall asleep', 'You must be a real'];
const ids = LINES.map((_, i) => `l${i}`);

function Beaker() {
  return (
    <svg viewBox="0 0 200 240" width={200} height={240} aria-hidden="true">
      <path d="M100,150 C80,170 60,200 64,226 L136,226 C140,200 120,170 100,150 Z" fill="#7cf0c0" opacity={0.85} />
      <g className="mkp" stroke="#000" strokeWidth={8}>
        <path d={wobLine([70, 20], [130, 20], 3, 3, 3)} />
        <path d={wobLine([80, 20], [80, 100], 3, 5, 3)} />
        <path d={wobLine([120, 20], [120, 100], 3, 7, 3)} />
        <path d={wobLine([80, 100], [24, 226], 4, 9, 4)} />
        <path d={wobLine([120, 100], [176, 226], 4, 11, 4)} />
        <path d={wobLine([24, 226], [176, 226], 3, 13, 4)} />
      </g>
      <path className="mkp" d={wobEllipse(92, 190, 9, 9, 15)} stroke="#000" strokeWidth={5} />
      <path className="mkp" d={wobEllipse(118, 170, 6, 6, 17)} stroke="#000" strokeWidth={5} />
    </svg>
  );
}

function End({ at, cur }: SceneProps) {
  const k = ids.indexOf(cur);
  const nerd = at('nerd');
  const paper = at('paper');
  return (
    <>
      {LINES.map((l, i) => (
        <div key={i} className={cx('c10-line', !nerd && i === k && 'on', !nerd && i === k - 1 && 'prev')}>
          {l}
        </div>
      ))}
      <div className={cx('c10-nerd', nerd && !paper && 'on')}>
        CRYPTO
        <Ins on={at('graphy')} word="graphy" className="c10-ins" />
        NERD
      </div>
      <div className={cx('c10-us', at('us') && !paper && 'on')}>Nerd like us!</div>
      <div className={cx('c10-worth', at('worth') && !paper && 'on')}>I told you the math would be worth it.</div>

      <a className={cx('c10-wp', paper && 'on')} href={WHITEPAPER} target="_blank" rel="noreferrer" data-noadvance>
        <QR text={WHITEPAPER} size={300} ecc="L" />
        <span>research/whitepaper.md</span>
      </a>
      <div className={cx('c10-wpt', paper && 'on')}>
        <svg viewBox="0 0 24 24" width={64} height={64} aria-hidden="true">
          <LogoMark kind="github" />
        </svg>
        There is a lot more in the whitepaper. Go check it out.
      </div>

      <div className={cx('c10-next', at('next') && 'on')}>
        <div className="c10-nh">Next steps</div>
        <div className="c10-beaker">
          <Beaker />
        </div>
        <div className="c10-slh">SLH-DSA</div>
        <div className="c10-slhs">bigger signatures, no spent-key tracking</div>
      </div>
      <div className={cx('c10-vv', at('vv') && 'on')}>
        <div className="c10-v1">
          <Vault size={260} />
        </div>
        <div className="c10-v2">
          <Vault size={110} />
        </div>
        <div className="c10-vvt">the bunker protects the bunker</div>
      </div>
      <div className={cx('c10-lab', at('lab') && 'on')}>Lots more to cook up in the Lab.</div>
    </>
  );
}

export const C10End: SceneDef = {
  key: 'c-end',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [...ids.map((id) => ({ id })), { id: 'nerd' }, { id: 'graphy' }, { id: 'us' }, { id: 'worth' }, { id: 'paper' }, { id: 'next' }, { id: 'vv' }, { id: 'lab' }],
  C: End,
};
