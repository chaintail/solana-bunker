// Period-TV texture: scanlines + seeded static + flicker. Deterministic: everything keyed on the frame number.
// usage: film.crt({ noise: .07, flicker: .05, seed: 7 })
(() => {
  const film = window.__film;
  film.crt = (o = {}) => {
    const noise = o.noise ?? 0.07, flick = o.flicker ?? 0.05, seed = o.seed ?? 1;
    const wrap = document.createElement('div');
    wrap.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:50';
    const cv = document.createElement('canvas');
    cv.width = 160; cv.height = 90;
    cv.style.cssText = `position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated;opacity:${noise};mix-blend-mode:screen`;
    const lines = document.createElement('div');
    lines.style.cssText = 'position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.16) 0 2px,transparent 2px 5px)';
    const vig = document.createElement('div');
    vig.style.cssText = 'position:absolute;inset:0;background:radial-gradient(ellipse 75% 75% at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%)';
    const fl = document.createElement('div');
    fl.style.cssText = 'position:absolute;inset:0;background:#fff;opacity:0;mix-blend-mode:overlay';
    wrap.append(cv, lines, vig, fl);
    document.body.append(wrap);
    const ctx = cv.getContext('2d');
    const img = ctx.createImageData(160, 90);
    film.onSeek((t) => {
      const fr = Math.floor(t * film.fps + 1e-6);
      const r = film.rng(seed * 100003 + fr);
      for (let i = 0; i < img.data.length; i += 4) { const v = r() * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      ctx.putImageData(img, 0, 0);
      fl.style.opacity = String(r() < 0.18 ? flick * (0.4 + r()) * 4 : 0);
      lines.style.transform = `translateY(${(fr % 5) * 1}px)`;
    });
    return wrap;
  };
})();
