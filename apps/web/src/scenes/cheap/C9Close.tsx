import logo from '../../assets/chaintail-logo.svg';
import { Door } from '../../components/Door';
import type { SceneDef } from '../../types';
import { QR } from './proof';
import './c9.css';

/** brand lines; Liam may switch the product line to "Solana Bunker" */
export const BRAND = 'Chaintail Labs R&D';
export const BRAND_PRODUCT = 'Solana Vault';

const REPO = 'https://github.com/chaintail/solana-bunker';
const TELEGRAM = 'https://t.me/chaintail';
/* highest error correction; the logo covers at most this share of the code (verified to decode, see report) */
const LOGO_AREA = 0.16;

function Close() {
  return (
    <>
      <div className="c9-parch">
        <div className="paper mottle" />
        <div className="paper grain" />
        <div className="paper vig" />
      </div>
      <div className="c9-brand">
        <div className="c9-b1">{BRAND}</div>
        <div className="c9-b2">{BRAND_PRODUCT}</div>
      </div>
      <img className="c9-lemur" src={logo} alt="Chaintail" draggable={false} />
      <div className="c9-door">
        <Door className="door3" />
      </div>
      <a className="c9-q c9-gh" href={REPO} target="_blank" rel="noreferrer" data-noadvance>
        <QR text={REPO} size={372} ecc="H" logo="github" logoArea={LOGO_AREA} dark="#1c1a17" light="#f7f1e3" />
        <span>{REPO}</span>
      </a>
      <a className="c9-q c9-tg" href={TELEGRAM} target="_blank" rel="noreferrer" data-noadvance>
        <QR text={TELEGRAM} size={372} ecc="H" logo="telegram" logoArea={LOGO_AREA} dark="#1c1a17" light="#f7f1e3" />
        <span>{TELEGRAM}</span>
      </a>
      <div className="c9-ask">Feel free to reach out with any questions!</div>
    </>
  );
}

export const C9: SceneDef = {
  key: 'c-close',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'close' }],
  C: Close,
};
