import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import type { Route, SceneDef, StepDef } from './types';

export function stepsFor(scene: SceneDef, route: Route): StepDef[] {
  return route === 'technical' ? scene.steps : scene.steps.filter((s) => !s.tech);
}

interface Pos {
  scene: number;
  step: number;
  route: Route;
}

/** what each scene currently displays; -1 means "nothing reached yet" */
interface Shown {
  idx: number;
  instant: boolean;
  /** reached by stepping forward (keyframe animations run) */
  anim: boolean;
}

export type Decks = Record<Route, SceneDef[]>;

function parseHash(decks: Decks): Pos | null {
  const m = location.hash.match(/^#(\d+)-(\d+)(-t)?$/);
  if (!m) return null;
  const route: Route = m[3] ? 'technical' : 'pitch';
  const scenes = decks[route];
  const scene = Math.min(+m[1], scenes.length - 1);
  const n = stepsFor(scenes[scene], route).length;
  return { scene, step: Math.min(+m[2], n - 1), route };
}

export function useDeck(decks: Decks) {
  const initial = useMemo<Pos>(() => {
    const h = parseHash(decks);
    if (h) return h;
    const r = (sessionStorage.getItem('sb-route') as Route) || 'pitch';
    return { scene: 0, step: 0, route: r === 'technical' ? 'technical' : 'pitch' };
  }, [decks]);
  const [pos, setPos] = useState<Pos>(initial);
  const [shown, setShown] = useState<Shown[]>(() =>
    decks.pitch.map((_, i) => ({ idx: i === initial.scene ? initial.step : -1, instant: true, anim: false })),
  );
  const [cut, setCut] = useState(true);
  const posRef = useRef(pos);
  posRef.current = pos;
  const token = useRef(0);

  const settle = useCallback((scene: number, idx: number, anim = false) => {
    const t = ++token.current;
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        if (t !== token.current) return;
        setShown((s) => s.map((x, i) => (i === scene ? (x.idx === -1 ? { idx, instant: false, anim } : { ...x, instant: false }) : x)));
        setCut(false);
      }),
    );
  }, []);

  useEffect(() => {
    settle(initial.scene, initial.step);
  }, [initial, settle]);

  const go = useCallback(
    (to: Pos, mode: 'forward' | 'jump') => {
      const from = posRef.current;
      setPos(to);
      if (mode === 'forward' && to.scene === from.scene) {
        setShown((s) => s.map((x, i) => (i === to.scene ? { idx: to.step, instant: false, anim: true } : x)));
      } else if (mode === 'forward') {
        // entering the next scene: start blank, then animate step 0 in
        setShown((s) => s.map((x, i) => (i === to.scene ? { idx: -1, instant: true, anim: false } : x)));
        settle(to.scene, to.step, true);
      } else {
        setShown((s) => s.map((x, i) => (i === to.scene ? { idx: to.step, instant: true, anim: false } : x)));
        setCut(to.scene !== from.scene);
        settle(to.scene, to.step);
      }
    },
    [settle],
  );

  const next = useCallback(() => {
    const p = posRef.current;
    const scenes = decks[p.route];
    const n = stepsFor(scenes[p.scene], p.route).length;
    if (p.step < n - 1) go({ ...p, step: p.step + 1 }, 'forward');
    else if (p.scene < scenes.length - 1) go({ ...p, scene: p.scene + 1, step: 0 }, 'forward');
  }, [go, decks]);

  const prev = useCallback(() => {
    const p = posRef.current;
    const scenes = decks[p.route];
    if (p.step > 0) go({ ...p, step: p.step - 1 }, 'jump');
    else if (p.scene > 0) {
      const n = stepsFor(scenes[p.scene - 1], p.route).length;
      go({ ...p, scene: p.scene - 1, step: n - 1 }, 'jump');
    }
  }, [go, decks]);

  const setRoute = useCallback(
    (route: Route) => {
      const p = posRef.current;
      if (route === p.route) return;
      const sc = decks[p.route][p.scene];
      const id = stepsFor(sc, p.route)[p.step].id;
      const target = decks[route][p.scene];
      const list = stepsFor(target, route);
      let step = list.findIndex((s) => s.id === id);
      if (step < 0 && target !== sc) step = 0;
      else if (step < 0) {
        // leaving a technical-only step: fall back to the nearest earlier pitch step
        const all = sc.steps;
        let k = all.findIndex((s) => s.id === id);
        while (k > 0 && all[k].tech) k--;
        step = Math.max(0, list.findIndex((s) => s.id === all[k].id));
      }
      sessionStorage.setItem('sb-route', route);
      go({ scene: p.scene, step, route }, 'jump');
    },
    [go, decks],
  );

  const home = useCallback(() => go({ ...posRef.current, scene: 0, step: 0 }, 'jump'), [go]);

  useEffect(() => {
    const h = `#${pos.scene}-${pos.step}${pos.route === 'technical' ? '-t' : ''}`;
    if (location.hash !== h) history.replaceState(null, '', h);
  }, [pos]);

  useEffect(() => {
    const onHash = () => {
      const h = parseHash(decks);
      const p = posRef.current;
      if (h && (h.scene !== p.scene || h.step !== p.step || h.route !== p.route)) go(h, 'jump');
    };
    addEventListener('hashchange', onHash);
    return () => removeEventListener('hashchange', onHash);
  }, [go, decks]);

  return { pos, shown, cut, next, prev, setRoute, home };
}

/** scale the 1920x1080 stage to fit the viewport */
export function useFit(ref: React.RefObject<HTMLDivElement | null>) {
  useLayoutEffect(() => {
    const fit = () => {
      // layout viewport (not visualViewport) so pinch zoom is not undone
      const w = document.documentElement.clientWidth || innerWidth;
      const h = document.documentElement.clientHeight || innerHeight;
      const s = Math.min(w / 1920, h / 1080);
      if (ref.current) ref.current.style.transform = `scale(${s})`;
    };
    fit();
    addEventListener('resize', fit);
    return () => removeEventListener('resize', fit);
  }, [ref]);
}

const NOADV = 'a,button,input,label,[data-noadvance],.redact-x,.slip';

/** keyboard, tap halves and swipes */
export function useInput(h: {
  next: () => void;
  prev: () => void;
  toggleRoute: () => void;
  home: () => void;
}) {
  const hr = useRef(h);
  hr.current = h;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.repeat || e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key;
      if (k === 'ArrowRight' || k === ' ' || k === 'PageDown' || k === 'Enter') {
        e.preventDefault();
        hr.current.next();
      } else if (k === 'ArrowLeft' || k === 'PageUp' || k === 'Backspace') {
        e.preventDefault();
        hr.current.prev();
      } else if (k === 'Home') hr.current.home();
      else if (k === 'f' || k === 'F') {
        if (document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen?.().catch(() => {});
      } else if (k === 't' || k === 'T') hr.current.toggleRoute();
    };
    let sx = 0,
      sy = 0,
      st = 0,
      down = false,
      blocked = false;
    const onDown = (e: PointerEvent) => {
      if (e.button !== 0 || e.pointerType === 'touch') return;
      down = true;
      blocked = !!(e.target as Element).closest?.(NOADV);
      sx = e.clientX;
      sy = e.clientY;
      st = performance.now();
    };
    const onUp = (e: PointerEvent) => {
      if (!down || e.pointerType === 'touch') return;
      down = false;
      if (blocked) return;
      const dx = e.clientX - sx,
        dy = e.clientY - sy;
      const dist = Math.hypot(dx, dy);
      if (dist > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        if (dx < 0) hr.current.next();
        else hr.current.prev();
      } else if (dist < 12 && performance.now() - st < 600) {
        if (e.clientX >= innerWidth / 2) hr.current.next();
        else hr.current.prev();
      }
    };
    let tx = 0,
      ty = 0,
      tt = 0,
      multi = false,
      tblocked = false;
    const onTS = (e: TouchEvent) => {
      if (e.touches.length > 1) {
        multi = true;
        return;
      }
      multi = false;
      const t = e.touches[0];
      tblocked = !!(e.target as Element).closest?.(NOADV);
      tx = t.clientX;
      ty = t.clientY;
      tt = performance.now();
    };
    const onTE = (e: TouchEvent) => {
      if (multi || tblocked || e.touches.length > 0) return;
      const t = e.changedTouches[0];
      const dx = t.clientX - tx,
        dy = t.clientY - ty,
        dist = Math.hypot(dx, dy);
      const zoomed = (window.visualViewport?.scale ?? 1) > 1.05;
      if (!zoomed && dist > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        if (dx < 0) hr.current.next();
        else hr.current.prev();
      } else if (dist < 12 && performance.now() - tt < 600) {
        const vv = window.visualViewport;
        const x = vv ? t.clientX - vv.offsetLeft : t.clientX;
        const w = vv ? vv.width : innerWidth;
        if (x >= w / 2) hr.current.next();
        else hr.current.prev();
      }
    };
    addEventListener('touchstart', onTS, { passive: true });
    addEventListener('touchend', onTE, { passive: true });
    addEventListener('keydown', onKey);
    addEventListener('pointerdown', onDown);
    addEventListener('pointerup', onUp);
    addEventListener('pointercancel', () => (down = false));
    return () => {
      removeEventListener('touchstart', onTS);
      removeEventListener('touchend', onTE);
      removeEventListener('keydown', onKey);
      removeEventListener('pointerdown', onDown);
      removeEventListener('pointerup', onUp);
    };
  }, []);
}
