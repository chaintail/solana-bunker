import thumb from '../assets/bankless-debate-thumb.jpg';
import { cx, Stamp } from '../components/bits';
import { Redact } from '../components/Redact';
import type { SceneDef, SceneProps } from '../types';
import { Cast } from './Cast';
import './s1.css';

const DEV_WALLET = 'N4FZnqmfXWoGhofuJAYnDdnYF8ows635ZAw2omFCtW1';

function Warning({ at, instant }: SceneProps) {
  return (
    <>
      <div className="debate">
        <figure className="thumb">
          <img src={thumb} alt="Bankless debate: Ethereum versus Solana" draggable={false} />
          <i className="corner tl" />
          <i className="corner tr" />
          <i className="corner bl" />
          <i className="corner br" />
        </figure>
        <p className="caption">This debate is when I first started to believe in Solana.</p>
        <svg className="jd-arrow" viewBox="0 0 480 300" aria-hidden="true">
          <path className="pen" d="M236,236 C300,232 360,200 398,150 C414,128 424,104 430,84" pathLength={1} />
          <path className="pen" d="M412,98 L431,80 L437,106" pathLength={1} />
        </svg>
        <div className="jd-name">Justin Drake</div>
      </div>

      <article className="tweet">
        <header>
          <span className="av">JD</span>
          <span className="who">
            <b>Justin Drake</b>
            <span>@drakefjustin</span>
          </span>
        </header>
        <p>
          <mark className="hlt">Today I call upon the blockchain industry to calmly begin planning for ‘bunker&nbsp;mode’.</mark> My personal recommendation is to set in motion a controlled mass migration of assets to fresh addresses, i.e. addresses whose pubkeys remain hidden behind a hash.
        </p>
      </article>

      <div className="lower l1">
        <span className="tag">Correction</span>
        <span className="txt">ECDSA on secp256k1 · Ed25519 on Solana</span>
      </div>
      <div className="lower l2">
        <span className="tag">Correction</span>
        <span className="txt">quantum is the known threat; AI is the speculative one</span>
      </div>

      <div className="contrast">
        <div className="row eth">
          <div className="chain">ETHEREUM</div>
          <div className="nd">
            <span className="lbl">private key</span>
            <span className="redact" style={{ width: 120, height: 18 }} />
          </div>
          <i className="ar" />
          <div className="nd hid">
            <span className="lbl">public key</span>
            <span className="v">hidden</span>
          </div>
          <i className="ar" />
          <div className="nd fn">
            <span className="lbl">hash</span>
            <span className="v">Keccak-256</span>
          </div>
          <i className="ar" />
          <div className="nd">
            <span className="lbl">address</span>
            <span className="v">0x · last 20 bytes</span>
          </div>
          <span className="eq-eth">
            <span className="lbl">derivation</span>
            <Redact eq="eth" w={300} h={20} />
          </span>
        </div>
        <div className="row sol">
          <div className="chain">SOLANA</div>
          <div className="nd">
            <span className="lbl">private key</span>
            <span className="redact" style={{ width: 120, height: 18 }} />
          </div>
          <i className="ar" />
          <div className="nd exposed">
            <span className="lbl">public key = address</span>
            <span className="v">{DEV_WALLET.slice(0, 22)}…</span>
          </div>
          <span className="note">Ed25519 · 32 bytes · base58</span>
        </div>
      </div>

      <Stamp on={at('drill')} instant={instant} x={1372} y={772} size={116} r={-7} d={80} className="st-drill">
        This is a drill
      </Stamp>

      <Cast on={at('cast')} />
      <div className={cx('wash', at('cast') && 'go')} />
    </>
  );
}

export const S1: SceneDef = {
  key: 'warning',
  exhibit: 'Exhibit 1',
  title: 'The warning',
  steps: [{ id: 'debate' }, { id: 'tweet' }, { id: 'fix1' }, { id: 'fix2' }, { id: 'contrast' }, { id: 'drill' }, { id: 'cast', tech: true }],
  C: Warning,
};
