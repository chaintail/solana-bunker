// Helpers shared by the dossier scenes (s01-title, s03-conspiracy). Needs lib/film.js loaded first.
(() => {
  const film = window.__film;
  const D = {};
  D.mk = (tag, cls, css, parent, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (css) e.style.cssText = css;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  };
  // rough-ink filter used by .stamp (displaced edge plus toner dropout)
  D.defs = () => {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('width', 0); s.setAttribute('height', 0); s.style.position = 'absolute';
    s.innerHTML = `<defs><filter id="rough" x="-8%" y="-8%" width="116%" height="116%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="2" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="5" result="d"/><feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="2" seed="5" result="s"/><feColorMatrix in="s" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -3.2 3.05" result="m"/><feComposite in="d" in2="m" operator="in"/></filter></defs>`;
    document.body.appendChild(s);
  };
  // typewriter: reveal text in el between t0 and t1, each key a one pixel jolt of the line
  D.type = (el, text, t0, t1, caret) => {
    film.onSeek((t) => {
      const p = film.prog(t, t0, t1);
      const n = Math.floor(p * text.length + 1e-6);
      el.textContent = text.slice(0, n) + (caret && p > 0 && p < 1 ? '█' : '');
      el.style.transform = n % 2 ? 'translateY(-1.6px)' : 'translateY(0)';
      el.style.visibility = t >= t0 ? 'visible' : 'hidden';
    });
  };
  // word time (global seconds) from the audio edit: W('p2','papers')
  D.W = (pid, word, start = true) => {
    const ws = window.CONSP.words[pid];
    const i = ws.findIndex((w) => w[0].toLowerCase().replace(/[^a-z0-9]/g, '').startsWith(word.toLowerCase().replace(/[^a-z0-9]/g, '')));
    if (i < 0) throw new Error('word not found ' + pid + ' ' + word);
    return start ? ws[i][1] : ws[i][2];
  };
  // short helpers over film.anim
  D.show = (el, at, dur = 0.01) => film.anim(el, [{ opacity: 0 }, { opacity: 1 }], at, dur);
  D.hide = (el, at, dur = 0.01) => film.anim(el, [{ opacity: 1 }, { opacity: 0 }], at, dur);
  D.fromTo = (el, a, b, at, dur, opts) => film.anim(el, [a, b], at, dur, opts);
  D.ease = { out: 'cubic-bezier(.16,.84,.3,1)', in: 'cubic-bezier(.6,0,.9,.5)', io: 'cubic-bezier(.65,0,.35,1)', back: 'cubic-bezier(.3,1.5,.5,1)' };
  // an ink-stamp slam: scale in from big with a hard stop, tilt kept in the element's own rotate
  D.slam = (el, at, rot, from = 3, dur = 0.14) => film.anim(el, [
    { opacity: 0, transform: `rotate(${rot}deg) scale(${from})` },
    { opacity: 1, transform: `rotate(${rot}deg) scale(.96)`, offset: .8 },
    { opacity: 1, transform: `rotate(${rot}deg) scale(1)` }], at, dur, { easing: 'cubic-bezier(.5,0,.9,.4)' });
  // paperclip svg
  D.clipSvg = (parent, css) => D.mk('div', 'clip', css, parent, `<svg viewBox="0 0 44 120" width="44" height="120"><path d="M30 14 V86 a12 12 0 0 1 -24 0 V24 a9 9 0 0 1 18 0 V80" fill="none" stroke="#9aa0a6" stroke-width="5" stroke-linecap="round"/><path d="M30 14 V86 a12 12 0 0 1 -24 0 V24 a9 9 0 0 1 18 0 V80" fill="none" stroke="#e8ecef" stroke-width="1.6" stroke-linecap="round" transform="translate(-.8 -.8)"/></svg>`);
  window.__D = D;
})();
