import { useMemo, useRef } from 'react';
import { Defs } from './components/Defs';
import { cx, Header } from './components/bits';
import { stepsFor, useDeck, useFit, useInput } from './engine';
import { DECKS } from './scenes';
import type { Route, SceneDef } from './types';

function SceneFrame({ def, num, total, idx, instant, anim, active, cut, route }: { def: SceneDef; num: number; total: number; idx: number; instant: boolean; anim: boolean; active: boolean; cut: boolean; route: Route }) {
  const steps = stepsFor(def, route);
  const reached = steps.slice(0, idx + 1).map((s) => s.id);
  const set = useMemo(() => new Set(reached), [reached.join(' ')]);
  const cur = idx >= 0 ? steps[idx].id : '';
  return (
    <section
      id={`s-${def.key}`}
      className={cx('scene', active && 'active', instant && 'instant', cut && 'cut', route === 'technical' && 'route-t', ...reached.map((r) => `r-${r}`), cur && `cur-${cur}`, cur && anim && `a-${cur}`)}
    >
      <div className="content">
        {!def.bare && !def.cheap && <Header exhibit={def.exhibit} title={def.title} sheet={`Sheet ${String(num).padStart(2, '0')} / ${String(total).padStart(2, '0')}`} />}
        <def.C at={(id) => set.has(id)} cur={cur} instant={instant} active={active} route={route} />
      </div>
    </section>
  );
}

declare global {
  interface Window {
    __deck?: { plan: () => { i: number; pitch: number; technical: number }[]; overflow: () => string[] };
  }
}
window.__deck = {
  plan: () => DECKS.pitch.map((s, i) => ({ i, pitch: stepsFor(s, 'pitch').length, technical: stepsFor(DECKS.technical[i], 'technical').length })),
  overflow: () => {
    const st = document.getElementById('stage')!.getBoundingClientRect();
    const bad: string[] = [];
    document.querySelectorAll('.scene.active .stamp.on, .scene.active .cstamp.on').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.left < st.left - 1 || r.top < st.top - 1 || r.right > st.right + 1 || r.bottom > st.bottom + 1) bad.push((el.textContent || '').trim());
    });
    return bad;
  },
};

export function App() {
  const stage = useRef<HTMLDivElement>(null);
  useFit(stage);
  const deck = useDeck(DECKS);
  const { pos, shown, cut } = deck;
  const posRoute = useRef(pos.route);
  posRoute.current = pos.route;
  useInput({
    next: deck.next,
    prev: deck.prev,
    home: deck.home,
    toggleRoute: () => deck.setRoute(posRoute.current === 'pitch' ? 'technical' : 'pitch'),
  });
  const scenes = DECKS[pos.route];
  const sc = scenes[pos.scene];
  const n = stepsFor(sc, pos.route).length;
  const cheap = !!sc.cheap;
  const toggle = () => deck.setRoute(pos.route === 'pitch' ? 'technical' : 'pitch');
  return (
    <>
    <div id="stage" ref={stage} className={cx(sc.bare && 'chrome-hide', cheap && 'cheap', pos.route === 'technical' && 'dossier')} data-scene={sc.key}>
      <Defs />
      {!cheap && (
        <>
          <div className="paper mottle" />
          <div className="paper grain" />
          <div className="paper vig" />
        </>
      )}
      {scenes.map((def, i) => (
        <SceneFrame key={`${pos.route}-${def.key}`} def={def} num={i} total={scenes.length - 1} idx={shown[i].idx} instant={shown[i].instant} anim={shown[i].anim} active={i === pos.scene} cut={cut} route={pos.route} />
      ))}
      {cheap && !sc.bare && <div className="slide-no">SLIDE {pos.scene + 1}</div>}
      {pos.route === 'technical' && (
        <div className="slide-no dossier-no">
          SLIDE {pos.scene + 1}
          <small>
            STEP {pos.step + 1} OF {n}
          </small>
        </div>
      )}
    </div>
    {/* outside the scaled stage so it stays a real 44px tap target on phones */}
    <button
      type="button"
      className={cx('deck-switch', pos.route === 'technical' && 'dossier')}
      data-noadvance
      aria-label="Switch to the other deck (T)"
      onClick={(e) => {
        e.stopPropagation();
        e.currentTarget.blur();
        toggle();
      }}
    >
      switch to the other deck
    </button>
    </>
  );
}
