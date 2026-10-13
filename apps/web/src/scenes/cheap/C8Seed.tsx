import { cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { LinkBox, LinkColumn } from './proof';
import './c8seed.css';

/* 24 words from the BIP-39 English list, picked by hand for the slide: not a real seed, holds nothing */
const WORDS = 'orbit velvet canyon ladder mango silent harvest pilot ribbon cactus frozen tribe anchor meadow puzzle sketch voyage lunar copper glimpse walnut rescue tunnel jungle'.split(' ');

function Seed({ at }: SceneProps) {
  const bip = at('bip');
  return (
    <>
      <div className={cx('c8-q', !bip && at('q1') && 'on')}>
        Ok but there’s still one really annoying part…
        <br />
        how do we keep track of 1,000 one-time secrets?
      </div>
      <div className={cx('c8-q c8-q2', !bip && at('q2') && 'on')}>
        what if we could <i>derive</i> them from something memorable?
      </div>
      <div className={cx('c8-bip', bip && 'on')}>BIP-39</div>
      <ol className={cx('c8-words', at('words') && 'on')}>
        {WORDS.map((w, i) => (
          <li key={i} style={{ ['--i' as string]: i }}>
            <span>{i + 1}.</span> {w}
          </li>
        ))}
      </ol>
      <div className={cx('c8-yeah', at('yeah') && 'on')}>yeah, we did that too!</div>
      <div className={cx('c8-check', at('check') && 'on')}>check it out!</div>
      <LinkColumn on={at('check')}>
        <LinkBox title="code" url="https://github.com/chaintail/solana-bunker/blob/main/client/kdf.py#L10" text="client/kdf.py line 10" />
        <LinkBox title="whitepaper" url="https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md#L35" text="research/whitepaper.md line 35" />
      </LinkColumn>
      <div className={cx('c8-desc', at('check') && 'on')}>
        One seed phrase. Every one-time key for every generation of the tree is derived from it with HKDF, so recovery after a rotation is the same phrase, next generation.
      </div>
    </>
  );
}

export const C8Seed: SceneDef = {
  key: 'c-seed',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'q1' }, { id: 'q2' }, { id: 'bip' }, { id: 'words' }, { id: 'yeah' }, { id: 'check' }],
  C: Seed,
};
