// Film runtime shared by every scene in apps/web/film/.
//
// Contract (what capture.mjs relies on):
//   * <html data-duration="8" data-fps="30"> declares the scene length in seconds.
//   * All motion is either a Web Animation / CSS animation that exists once the
//     page has loaded, timed from scene t = 0 (delay = start time), with
//     fill "both"; or JS-driven motion registered with film.onSeek(fn), which
//     is exposed as window.__seek(t) (t in seconds).
//   * Never two animations on the same element and property; nest wrappers.
//   * No Math.random / Date.now in scenes: use film.rng(seed).
//   * html[data-film-ready="1"] is set once fonts and images are ready.
//
// Modes (URL query):
//   (none)      play once in real time from t = 0 after assets are ready
//   ?loop       play and loop
//   ?t=2.5      preview: freeze at 2.5 s
//   ?capture    freeze at 0, the capture script drives the time
(() => {
  const q = new URLSearchParams(location.search);
  const root = document.documentElement;
  const hooks = [];
  const mode = q.has('t') ? 'preview' : q.has('capture') ? 'capture' : 'play';
  const pauseAll = () => { for (const a of document.getAnimations()) a.pause(); };

  const film = {
    mode,
    duration: Number(root.dataset.duration || 0),
    fps: Number(root.dataset.fps || 30),
    onSeek(fn) { hooks.push(fn); },
    // film.anim(el, keyframes, startSeconds, durationSeconds, extraTiming)
    anim(el, keyframes, at, dur, opts = {}) {
      const a = el.animate(keyframes, { delay: at * 1000, duration: dur * 1000, fill: 'both', easing: 'linear', ...opts });
      a.pause();
      return a;
    },
    seek(t) {
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
      window.__seek(t);
    },
    rng(seed) {
      let s = seed >>> 0;
      return () => { s = (s + 0x6d2b79f5) >>> 0; let r = Math.imul(s ^ (s >>> 15), 1 | s); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
    },
    // clamp(0..1) progress of t inside [a, b]
    prog(t, a, b) { return Math.min(1, Math.max(0, (t - a) / (b - a))); },
  };
  window.__film = film;
  window.__seek = (t) => { for (const f of hooks) f(t); };

  document.addEventListener('DOMContentLoaded', pauseAll);
  const loaded = new Promise((r) => (document.readyState === 'complete' ? r() : addEventListener('load', r, { once: true })));
  film.ready = loaded
    .then(() => document.fonts.ready)
    .then(() => Promise.all([...document.images].map((i) => i.decode().catch(() => {}))))
    .then(() => {
      pauseAll();
      if (mode === 'preview') film.seek(Number(q.get('t')) || 0);
      else if (mode === 'capture') film.seek(0);
      else {
        const start = () => {
          film.seek(0);
          for (const a of document.getAnimations()) a.play();
          const t0 = performance.now();
          const tick = () => {
            const t = (performance.now() - t0) / 1000;
            window.__seek(Math.min(t, film.duration));
            if (t < film.duration) requestAnimationFrame(tick);
            else if (q.has('loop')) start();
          };
          requestAnimationFrame(tick);
        };
        start();
      }
      root.dataset.filmReady = '1';
    });
})();
