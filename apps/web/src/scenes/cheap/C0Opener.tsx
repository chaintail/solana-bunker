import logo from '../../assets/chaintail-logo.svg';
import { CStamp } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import './c0.css';

/* the polished element: a browser tab strip, the slide is the page below it */
function TabBar() {
  return (
    <div className="c0-tabs" aria-hidden="true">
      <div className="c0-lights">
        <i />
        <i />
        <i />
      </div>
      <div className="c0-tab">
        <svg className="c0-fav" viewBox="0 0 40 40">
          <circle cx="20" cy="20" r="17" fill="#1f3a93" />
          <circle cx="20" cy="20" r="11" fill="none" stroke="#fff" strokeWidth="2.5" />
          <path d="M20,9 V31 M10.5,25.5 L29.5,14.5 M10.5,14.5 L29.5,25.5" stroke="#fff" strokeWidth="2.5" />
        </svg>
        <span className="c0-title">Solana Bunker</span>
        <span className="c0-x">
          <svg viewBox="0 0 40 40">
            <path d="M12,12 L28,28 M28,12 L12,28" stroke="#3c4043" strokeWidth="3.2" strokeLinecap="round" />
          </svg>
        </span>
      </div>
      <div className="c0-plus">
        <svg viewBox="0 0 40 40">
          <path d="M20,9 V31 M9,20 H31" stroke="#3c4043" strokeWidth="3.2" strokeLinecap="round" />
        </svg>
      </div>
    </div>
  );
}

function Cursor() {
  return (
    <div className="c0-cursor" aria-hidden="true">
      <svg viewBox="0 0 28 42" width={56} height={84}>
        <path d="M2,2 L2,33 L9.5,26 L14.5,38.5 L20,36.2 L15,24 L25,24 Z" fill="#000" stroke="#fff" strokeWidth={2.2} strokeLinejoin="round" />
      </svg>
    </div>
  );
}

function Opener({ at }: SceneProps) {
  return (
    <>
      <TabBar />
      <div className="c0-card loop">
        <div className="c0-warn">WARNING</div>
        <CStamp on={at('stamp')} x={960} y={590} size={124} r={-1.5} d={40}>
          CONTAINS MATH
        </CStamp>
      </div>
      {/* title: cheap text, the logo is the polished element */}
      <div className="c0-by">
        <div className="c0-by-1">R&amp;D from Chaintail Labs:</div>
        <div className="c0-by-2">Solana Bunker</div>
      </div>
      <img className="c0-logo" src={logo} alt="Chaintail" draggable={false} />
      {/* the slide number sits under the tab strip (the opener hides the deck chrome) */}
      <div className="slide-no c0-no">SLIDE 1</div>
      <Cursor />
    </>
  );
}

export const C0: SceneDef = {
  key: 'c-opener',
  exhibit: '',
  title: '',
  bare: true,
  cheap: true,
  steps: [{ id: 'blank' }, { id: 'warn' }, { id: 'stamp' }, { id: 'close' }, { id: 'stop' }],
  C: Opener,
};
