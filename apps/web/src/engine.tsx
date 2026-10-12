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
}

function parseHash(scenes: SceneDef[]): Pos | null {
  const m = location.hash.match(/^#(\d+)-(\d+)(-t)?$/);
  if (!m) return null;
  const route: Route = m[3] ? 'technical' : 'pitch';
  const scene = Math.min(+m[1], scenes.length - 1);
  const n = stepsFor(scenes[scene], route).length;
  return { scene, step: Math.min(+m[2], n - 1), route };
}

export function useDeck(scenes: SceneDef[]) {
  const initial = useMemo<Pos>(() => {
    const h = parseHash(scenes);
    if (h) return h;
    const r = (sessionStorage.getItem('sb-route') as Route) || 'pitch';
    return { scene: 0, step: 0, route: r === 'technical' ? 'technical' : 'pitch' };
  }, [scenes]);
  const [pos, setPos] = useState<Pos>(initial);
  const [shown, setShown] = useState<Shown[]>(() =>
    scenes.map((_, i) => ({ idx: i === initial.scene ? initial.step : -1, instant: true })),
  );
  const [cut, setCut] = useState(true);
  const posRef = useRef(pos);
  posRef.current = pos;
  const token = useRef(0);

  const settle = useCallback((scene: number, idx: number) => {
    const t = ++token.current;
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        if (t !== token.current) return;
        setShown((s) => s.map((x, i) => (i === scene ? { idx: x.idx === -1 ? idx : x.idx, instant: false } : x)));
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
        setShown((s) => s.map((x, i) => (i === to.scene ? { idx: to.step, instant: false } : x)));
      } else if (mode === 'forward') {
        // entering the next scene: start blank, then animate step 0 in
        setShown((s) => s.map((x, i) => (i === to.scene ? { idx: -1, instant: true } : x)));
        settle(to.scene, to.step);
      } else {
        setShown((s) => s.map((x, i) => (i === to.scene ? { idx: to.step, instant: true } : x)));
        setCut(to.scene !== from.scene);
        settle(to.scene, to.step);
      }
    },
    [settle],
  );

  const next = useCallback(() => {
    const p = posRef.current;
    const n = stepsFor(scenes[p.scene], p.route).length;
    if (p.step < n - 1) go({ ...p, step: p.step + 1 }, 'forward');
    else if (p.scene < scenes.length - 1) go({ ...p, scene: p.scene + 1, step: 0 }, 'forward');
  }, [go, scenes]);

  const prev = useCallback(() => {
    const p = posRef.current;
    if (p.step > 0) go({ ...p, step: p.step - 1 }, 'jump');
    else if (p.scene > 0) {
      const n = stepsFor(scenes[p.scene - 1], p.route).length;
      go({ ...p, scene: p.scene - 1, step: n - 1 }, 'jump');
    }
  }, [go, scenes]);

  const setRoute = useCallback(
    (route: Route) => {
      const p = posRef.current;
      if (route === p.route) return;
      const sc = scenes[p.scene];
      const id = stepsFor(sc, p.route)[p.step].id;
      const list = stepsFor(sc, route);
      let step = list.findIndex((s) => s.id === id);
      if (step < 0) {
        // leaving a technical-only step: fall back to the nearest earlier pitch step
        const all = sc.steps;
        let k = all.findIndex((s) => s.id === id);
        while (k > 0 && all[k].tech) k--;
        step = Math.max(0, list.findIndex((s) => s.id === all[k].id));
      }
      sessionStorage.setItem('sb-route', route);
      go({ scene: p.scene, step, route }, 'jump');
    },
    [go, scenes],
  );

  const home = useCallback(() => go({ ...posRef.current, scene: 0, step: 0 }, 'jump'), [go]);

  useEffect(() => {
    const h = `#${pos.scene}-${pos.step}${pos.route === 'technical' ? '-t' : ''}`;
    if (location.hash !== h) history.replaceState(null, '', h);
  }, [pos]);

  useEffect(() => {
    const onHash = () => {
      const h = parseHash(scenes);
      const p = posRef.current;
      if (h && (h.scene !== p.scene || h.step !== p.step || h.route !== p.route)) go(h, 'jump');
    };
    addEventListener('hashchange', onHash);
    return () => removeEventListener('hashchange', onHash);
  }, [go, scenes]);

  return { pos, shown, cut, next, prev, setRoute, home };
}

/** scale the 1920x1080 stage to fit the viewport */
export function useFit(ref: React.RefObject<HTMLDivElement | null>) {
  useLayoutEffect(() => {
    const fit = () => {
      const vv = window.visualViewport;
      const w = vv ? vv.width : innerWidth;
      const h = vv ? vv.height : innerHeight;
      const s = Math.min(w / 1920, h / 1080);
      if (ref.current) ref.current.style.transform = `scale(${s})`;
    };
    fit();
    addEventListener('resize', fit);
    window.visualViewport?.addEventListener('resize', fit);
    return () => {
      removeEventListener('resize', fit);
      window.visualViewport?.removeEventListener('resize', fit);
    };
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
      if (e.button !== 0) return;
      down = true;
      blocked = !!(e.target as Element).closest?.(NOADV);
      sx = e.clientX;
      sy = e.clientY;
      st = performance.now();
    };
    const onUp = (e: PointerEvent) => {
      if (!down) return;
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
    addEventListener('keydown', onKey);
    addEventListener('pointerdown', onDown);
    addEventListener('pointerup', onUp);
    addEventListener('pointercancel', () => (down = false));
    return () => {
      removeEventListener('keydown', onKey);
      removeEventListener('pointerdown', onDown);
      removeEventListener('pointerup', onUp);
    };
  }, []);
}
