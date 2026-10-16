// Slide 6's noir alley as a reusable module (copied from s06-signature.html at film/s06 v3, 4f43fd8; slide 6 itself is not rendered from this file).
// NoirAlley.markup(): the alley, interior, door reflection, swinging door (slot, shutter, eyes) and light cone, as one HTML string; ids as in slide 6.
// NoirAlley.init(f): builds the seeded bricks, side walls and the vault ring (call after the markup is in the DOM); returns { rain(ctx, t) }.
// NoirAlley.figs(f, sprite): the body + head compositing helpers of slide 6 (makeFig, place, setHead, narrFrame) for head sprite sheets `heads/<sprite>-NN.png`.
(() => {
const ALLEY = " <div class=\"L noir\" id=\"alley\"><svg width=\"1280\" height=\"720\" viewBox=\"0 0 1280 720\"><defs>\n  <linearGradient id=\"sky\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#070707\"/><stop offset=\"1\" stop-color=\"#1e1e1e\"/></linearGradient>\n  <radialGradient id=\"wallLight\" cx=\"690\" cy=\"300\" r=\"560\" gradientUnits=\"userSpaceOnUse\"><stop offset=\"0\" stop-color=\"#000\" stop-opacity=\"0\"/><stop offset=\".6\" stop-color=\"#000\" stop-opacity=\".32\"/><stop offset=\"1\" stop-color=\"#000\" stop-opacity=\".62\"/></radialGradient>\n  <linearGradient id=\"sideL\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\"><stop offset=\"0\" stop-color=\"#000\" stop-opacity=\".78\"/><stop offset=\"1\" stop-color=\"#000\" stop-opacity=\".35\"/></linearGradient>\n  <linearGradient id=\"sideR\" x1=\"1\" y1=\"0\" x2=\"0\" y2=\"0\"><stop offset=\"0\" stop-color=\"#000\" stop-opacity=\".82\"/><stop offset=\"1\" stop-color=\"#000\" stop-opacity=\".4\"/></linearGradient>\n  <linearGradient id=\"ground\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#222\"/><stop offset=\"1\" stop-color=\"#0a0a0a\"/></linearGradient>\n  <radialGradient id=\"pool\" cx=\"690\" cy=\"640\" r=\"330\" gradientTransform=\"translate(0 448) scale(1 .3)\" gradientUnits=\"userSpaceOnUse\"><stop offset=\"0\" stop-color=\"#fff\" stop-opacity=\".42\"/><stop offset=\".6\" stop-color=\"#fff\" stop-opacity=\".08\"/><stop offset=\"1\" stop-color=\"#fff\" stop-opacity=\"0\"/></radialGradient>\n  <filter id=\"soft\"><feGaussianBlur stdDeviation=\"6\"/></filter>\n  <filter id=\"smear\"><feGaussianBlur stdDeviation=\"3 14\"/></filter>\n </defs>\n <rect width=\"1280\" height=\"720\" fill=\"url(#sky)\"/>\n <g id=\"bricks\"></g>\n <rect x=\"170\" y=\"70\" width=\"960\" height=\"530\" fill=\"url(#wallLight)\"/>\n <rect x=\"236\" y=\"70\" width=\"14\" height=\"530\" fill=\"#333\"/><rect x=\"230\" y=\"160\" width=\"26\" height=\"8\" fill=\"#3c3c3c\"/><rect x=\"230\" y=\"420\" width=\"26\" height=\"8\" fill=\"#3c3c3c\"/>\n <g id=\"sideBricks\"></g>\n <polygon points=\"0,0 170,70 170,600 0,720\" fill=\"url(#sideL)\"/>\n <polygon points=\"1280,0 1130,70 1130,600 1280,720\" fill=\"url(#sideR)\"/>\n <g stroke=\"#000\" stroke-width=\"5\" fill=\"none\" opacity=\".9\"><path d=\"M1140 150 L1280 96 M1140 196 L1280 148 M1140 150 L1140 196 M1170 138 L1170 186 M1200 126 L1200 174 M1230 115 L1230 162 M1260 104 L1260 152\"/><path d=\"M1145 330 L1280 290 M1145 372 L1280 336 M1145 330 L1145 372 M1180 320 L1180 362 M1215 309 L1215 352 M1250 299 L1250 342\"/><path d=\"M1150 196 L1250 300\" stroke-width=\"7\"/></g>\n <polygon points=\"150,78 170,70 170,600 150,610\" fill=\"#fff\" opacity=\".12\"/>\n <circle cx=\"690\" cy=\"160\" r=\"150\" fill=\"#fff\" opacity=\".06\" filter=\"url(#soft)\"/>\n <polygon points=\"0,720 170,600 1130,600 1280,720\" fill=\"url(#ground)\"/>\n <rect x=\"170\" y=\"598\" width=\"960\" height=\"5\" fill=\"#2e2e2e\"/>\n <ellipse cx=\"690\" cy=\"650\" rx=\"380\" ry=\"60\" fill=\"url(#pool)\"/>\n <g fill=\"#000\" opacity=\".55\"><ellipse cx=\"420\" cy=\"672\" rx=\"120\" ry=\"14\"/><ellipse cx=\"1000\" cy=\"690\" rx=\"150\" ry=\"16\"/><ellipse cx=\"700\" cy=\"705\" rx=\"90\" ry=\"8\"/></g>\n <rect x=\"676\" y=\"606\" width=\"28\" height=\"110\" fill=\"#fff\" opacity=\".35\" filter=\"url(#smear)\"/>\n <path d=\"M560 70 L560 104 Q560 118 600 118 L690 118\" stroke=\"#0b0b0b\" stroke-width=\"7\" fill=\"none\"/>\n <path d=\"M664 118 L716 118 L728 142 L652 142 Z\" fill=\"#111\"/>\n <ellipse cx=\"690\" cy=\"144\" rx=\"30\" ry=\"6\" fill=\"#fff\"/>\n <circle cx=\"690\" cy=\"146\" r=\"46\" fill=\"#fff\" opacity=\".18\" filter=\"url(#soft)\"/>\n <rect x=\"744\" y=\"166\" width=\"252\" height=\"436\" fill=\"#202020\"/><rect x=\"736\" y=\"160\" width=\"268\" height=\"14\" fill=\"#2c2c2c\"/>\n <rect x=\"736\" y=\"592\" width=\"268\" height=\"12\" fill=\"#262626\"/>\n <ellipse id=\"bShadow\" cx=\"584\" cy=\"641\" rx=\"70\" ry=\"7\" fill=\"#000\" opacity=\".85\"/>\n </svg></div>\n\n <div class=\"L noir\" id=\"interior\"><svg width=\"1280\" height=\"720\"><defs>\n  <linearGradient id=\"inG\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#050505\"/><stop offset=\".7\" stop-color=\"#1a1a1a\"/><stop offset=\"1\" stop-color=\"#3a3a3a\"/></linearGradient>\n  <radialGradient id=\"inL\" cx=\"870\" cy=\"560\" r=\"160\" gradientUnits=\"userSpaceOnUse\"><stop offset=\"0\" stop-color=\"#fff\" stop-opacity=\".25\"/><stop offset=\"1\" stop-color=\"#fff\" stop-opacity=\"0\"/></radialGradient></defs>\n  <rect x=\"758\" y=\"176\" width=\"224\" height=\"420\" fill=\"url(#inG)\"/><rect x=\"758\" y=\"176\" width=\"224\" height=\"420\" fill=\"url(#inL)\"/>\n  <path d=\"M800 176 L800 300 M940 176 L940 260\" stroke=\"#2a2a2a\" stroke-width=\"3\"/></svg></div>\n\n <div class=\"L\" id=\"doorRefl\"><svg width=\"1280\" height=\"720\"><defs><filter id=\"refl\"><feGaussianBlur stdDeviation=\"2 10\"/></filter></defs>\n  <g filter=\"url(#refl)\"><rect x=\"758\" y=\"604\" width=\"224\" height=\"120\" fill=\"#6a080d\"/><rect x=\"822\" y=\"606\" width=\"96\" height=\"10\" fill=\"#7a5820\"/></g></svg></div>\n <div id=\"doorWrap\"><div id=\"doorPanel\"><svg width=\"1280\" height=\"720\" viewBox=\"0 0 1280 720\"><defs>\n  <linearGradient id=\"red\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#8e0c13\"/><stop offset=\".4\" stop-color=\"#5c060b\"/><stop offset=\"1\" stop-color=\"#1e0103\"/></linearGradient>\n  <linearGradient id=\"brass\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#c29a52\"/><stop offset=\".5\" stop-color=\"#7a5820\"/><stop offset=\"1\" stop-color=\"#3a290c\"/></linearGradient>\n  <radialGradient id=\"doorLight\" cx=\"740\" cy=\"260\" r=\"300\" gradientUnits=\"userSpaceOnUse\"><stop offset=\"0\" stop-color=\"#ff9c8c\" stop-opacity=\".20\"/><stop offset=\"1\" stop-color=\"#ff9c8c\" stop-opacity=\"0\"/></radialGradient>\n  <linearGradient id=\"doorShade\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\"><stop offset=\".35\" stop-color=\"#000\" stop-opacity=\"0\"/><stop offset=\"1\" stop-color=\"#000\" stop-opacity=\".55\"/></linearGradient>\n  <linearGradient id=\"lintel\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#000\" stop-opacity=\".7\"/><stop offset=\"1\" stop-color=\"#000\" stop-opacity=\"0\"/></linearGradient>\n  <clipPath id=\"slotClip\"><rect x=\"824\" y=\"246\" width=\"92\" height=\"18\"/></clipPath>\n </defs>\n <rect x=\"758\" y=\"176\" width=\"224\" height=\"420\" rx=\"3\" fill=\"url(#red)\" stroke=\"#1a0203\" stroke-width=\"3\"/>\n <rect x=\"776\" y=\"300\" width=\"188\" height=\"276\" fill=\"none\" stroke=\"#4a0508\" stroke-width=\"3\"/>\n <rect x=\"779\" y=\"303\" width=\"182\" height=\"270\" fill=\"none\" stroke=\"#c02028\" stroke-width=\"1\" opacity=\".5\"/>\n <rect x=\"764\" y=\"214\" width=\"9\" height=\"40\" rx=\"2\" fill=\"url(#brass)\"/><rect x=\"764\" y=\"500\" width=\"9\" height=\"40\" rx=\"2\" fill=\"url(#brass)\"/>\n <g id=\"ring\"></g>\n <rect x=\"818\" y=\"240\" width=\"104\" height=\"30\" rx=\"2\" fill=\"url(#brass)\"/>\n <g clip-path=\"url(#slotClip)\">\n  <rect x=\"824\" y=\"246\" width=\"92\" height=\"18\" fill=\"#080303\"/>\n  <g id=\"eyes\"><ellipse cx=\"856\" cy=\"256\" rx=\"9\" ry=\"5\" fill=\"#ddd\"/><ellipse cx=\"884\" cy=\"256\" rx=\"9\" ry=\"5\" fill=\"#ddd\"/><circle cx=\"858\" cy=\"256\" r=\"3.2\" fill=\"#000\"/><circle cx=\"886\" cy=\"256\" r=\"3.2\" fill=\"#000\"/></g>\n  <rect id=\"shutter\" x=\"824\" y=\"246\" width=\"92\" height=\"18\" fill=\"#5e070b\" stroke=\"#2a0204\" stroke-width=\"1.5\"/>\n </g>\n <rect x=\"958\" y=\"400\" width=\"12\" height=\"44\" rx=\"5\" fill=\"url(#brass)\"/>\n <rect x=\"758\" y=\"176\" width=\"224\" height=\"420\" fill=\"url(#doorLight)\"/><rect x=\"758\" y=\"176\" width=\"224\" height=\"420\" fill=\"url(#doorShade)\"/><rect x=\"758\" y=\"176\" width=\"224\" height=\"34\" fill=\"url(#lintel)\"/>\n </svg></div></div>\n\n";
const CONE = " <svg class=\"L\" style=\"mix-blend-mode:screen\" width=\"1280\" height=\"720\"><defs>\n  <linearGradient id=\"coneG\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#fff\" stop-opacity=\".30\"/><stop offset=\"1\" stop-color=\"#fff\" stop-opacity=\".03\"/></linearGradient>\n  <filter id=\"coneBlur\"><feGaussianBlur stdDeviation=\"10\"/></filter></defs><polygon points=\"662,146 718,146 920,660 440,660\" fill=\"url(#coneG)\" filter=\"url(#coneBlur)\"/></svg>\n";
function init(f) {
  const $ = (id) => document.getElementById(id);
  // ---------- alley details (seeded)
  { const r = f.rng(6); let g = ''; const W = 58, H = 22;
    for (let y = 70, row = 0; y < 600; y += H, row++) for (let x = 170 - (row % 2) * W / 2; x < 1130; x += W) {
      const v = 66 + Math.floor(r() * 40); g += `<rect x="${x + 2}" y="${y + 2}" width="${W - 4}" height="${H - 4}" fill="rgb(${v},${v - 4},${v - 6})"/>`; }
    $('bricks').innerHTML = `<rect x="170" y="70" width="960" height="530" fill="#191919"/>` + g;
    let s = ''; for (let i = 0; i <= 24; i++) { const yb = 70 + i * 22;
      s += `<line x1="170" y1="${yb}" x2="0" y2="${(yb - 335) * 1.45 + 335}" stroke="#4a4a4a" stroke-width="2"/><line x1="1130" y1="${yb}" x2="1280" y2="${(yb - 335) * 1.45 + 335}" stroke="#454545" stroke-width="2"/>`; }
    $('sideBricks').innerHTML = `<polygon points="0,0 170,70 170,600 0,720" fill="#454545"/><polygon points="1280,0 1130,70 1130,600 1280,720" fill="#3e3e3e"/>` + s;
    let b = ''; const cx = 870, cy = 438;     // vault bolt ring + wheel, recast from components/Door.tsx
    b += `<circle cx="${cx}" cy="${cy}" r="82" fill="#6a080d" stroke="#2a0204" stroke-width="3"/><circle cx="${cx}" cy="${cy}" r="62" fill="none" stroke="#a5141b" stroke-width="2"/>`;
    for (let k = 0; k < 36; k++) { const a = k / 36 * Math.PI * 2; b += `<circle cx="${(cx + 74 * Math.cos(a)).toFixed(1)}" cy="${(cy + 74 * Math.sin(a)).toFixed(1)}" r="2.6" fill="url(#brass)"/>`; }
    for (const a of [0, 120, 240]) b += `<g transform="rotate(${a + 15} ${cx} ${cy})"><rect x="${cx - 3}" y="${cy - 52}" width="6" height="40" fill="url(#brass)"/><circle cx="${cx}" cy="${cy - 56}" r="6" fill="url(#brass)"/></g>`;
    b += `<circle cx="${cx}" cy="${cy}" r="15" fill="url(#brass)" stroke="#2a0204" stroke-width="2"/>`;
    $('ring').innerHTML = b; }

  // rain: seeded streaks; brighter inside the light cone
  const R = f.rng(42), drops = Array.from({ length: 420 }, () => ({ x: R() * 1500 - 110, y: R() * 900, l: 16 + R() * 30, a: .12 + R() * .22, v: 1600 + R() * 700 }));
  
  const inCone = (x, y) => { if (y < 146 || y > 660) return 0; const p = (y - 146) / 514, l = 662 - 222 * p, r = 718 + 202 * p; return x > l && x < r ? 1 - Math.abs((x - (l + r) / 2) / ((r - l) / 2)) * .6 : 0; };
  function rain(t) {
    const ctx = rainCtx; ctx.clearRect(0, 0, 1280, 720); ctx.lineCap = 'round';
    for (const d of drops) { const y = ((d.y + d.v * t) % 900) - 90, x = d.x + y * .18, c = inCone(x, y);
      ctx.strokeStyle = `rgba(225,225,225,${(d.a + c * .45).toFixed(3)})`; ctx.lineWidth = c ? 1.8 : 1.3; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - d.l * .18, y - d.l); ctx.stroke(); }
    const S = f.rng(7 + Math.floor(t * 30)); ctx.strokeStyle = 'rgba(230,230,230,.35)'; ctx.lineWidth = 1;
    for (let i = 0; i < 46; i++) { const x = 60 + S() * 1160, y = 610 + S() * 105, w = 3 + S() * 6; ctx.beginPath(); ctx.ellipse(x, y, w, w * .3, 0, 0, Math.PI * 2); ctx.stroke(); }
  }

  return { rain: (ctx, t) => { rainCtx = ctx; rain(t); } };
}
let rainCtx = null;
function figs(f, sprite, D, chinKX = 338) {   // chinKX: key-px x of the narrator sprite's chin centre (slide 7 measures 308)
  const BODY = {
    suitX: { src: 'assets/bodies/1-suit-arms-crossed.png', ox: 511, chin: 306 },
    suitP: { src: 'assets/bodies/1-suit-point-right.png', ox: 352, chin: 309 },
    prof: { src: 'assets/bodies/5-physicist-professor-point.png', ox: 394.5, chin: 306 },
    // the same lab coat holding the clipboard (no point), registered on prof's torso (slide 7 v6): centre line (collar / tie knot) x 511.7 vs prof's 397.1, so
    // ox = 394.5 + 115; tie top y 400 = 400, shoulder outline within 1 px for 140 px either side of the neck, baseline 1462 vs 1463, so chin is unchanged.
    // This sprite is drawn 3.3 % wider than prof (clipboard edge +107, pocket +118 px): sx squeezes it horizontally about its centre line (best fit of
    // clipboard, collar, lapels, buttons, pocket and the clipboard shoulder: sx 0.967, mean abs diff 24.0 -> 11.1), so the torso edges coincide too.
    profC: { src: 'assets/bodies/5-physicist-holding-clipboard.png', ox: 509.5, chin: 306, sx: 0.967 },
  };
  const HK = 0.326;                  // key px -> body px (chin to collar line; see film-plan-s06.md section 3)
  function makeFig(parent, bodyKey, headKind) {
    const b = BODY[bodyKey], el = document.createElement('div'); el.className = 'fig';
    const mask = `radial-gradient(ellipse 103px 119px at ${b.ox}px ${b.chin - 107}px,transparent 97%,#000 100%)`;
    const o = b.ox, c = b.chin;
    const clip = `polygon(0 ${c - 6}px,${o - 59}px ${c - 6}px,${o - 49}px ${c + 16}px,${o - 8}px ${c + 41}px,${o + 10}px ${c + 41}px,${o + 51}px ${c + 16}px,${o + 60}px ${c - 6}px,1024px ${c - 6}px,1024px 1536px,0 1536px)`;
    const hl = o - 338 * HK, hn = o - chinKX * HK, ht = c - 905 * HK, hs = (760 * HK) / 152;
    let head;
    if (headKind === 'narr') head = `<div class="hd" data-base="translate(${hn}px,${ht}px) scale(${hs})" style="transform:translate(${hn}px,${ht}px) scale(${hs})">` + [0, 1, 2, 3, 4, 5].map((i) => `<img src="heads/${sprite}-0${i}.png">`).join('') + '</div>';
    else head = `<img src="heads/s06-${headKind}.png" style="width:${760 * HK}px;height:${1100 * HK}px;left:${hl}px;top:${ht}px">`;
    const sx = b.sx ? `transform-origin:${o}px 0;transform:scaleX(${b.sx});` : '';   // optional horizontal squeeze about the centre line (the head is not scaled)
    el.innerHTML = `<img src="${b.src}" width="1024" height="1536" style="${sx}-webkit-mask-image:${mask};mask-image:${mask}">${head}<img src="${b.src}" width="1024" height="1536" style="${sx}clip-path:${clip}">`;
    el.dataset.ox = o; el.dataset.chin = c; parent.appendChild(el); return el;
  }
  // neck point (x,y) on screen, rotation deg, scale, mirror. A mirrored body keeps an unmirrored head (the head is flipped back about the neck line x = ox).
  const place = (el, x, y, rot, s, flip = 1) => {
    el.style.transform = `translate(${x}px,${y}px) rotate(${rot}deg) scale(${s * flip},${s}) translate(${-el.dataset.ox}px,${-el.dataset.chin}px)`;
    const hd = el.querySelector('.hd'); if (hd) hd.style.transform = (flip < 0 ? `translate(${el.dataset.ox}px,0) scale(-1,1) translate(${-el.dataset.ox}px,0) ` : '') + hd.dataset.base;
  };
  const SHEET = 192, CELL_W = 152, CELL_H = 220;
  const cum = []; D.edl.reduce((a, e, i) => ((cum[i] = a), a + e.frames), 0);
  function narrFrame(t) {   // lip-sync frame; holds the last frame of the previous line through every pause (freeze when silent)
    let i = -1; for (let k = 0; k < D.edl.length; k++) if (t >= D.edl[k].out_in) i = k;
    if (i < 0) return 0;
    const e = D.edl[i]; return cum[i] + Math.min(e.frames - 1, Math.floor((t - e.out_in) * 30 + 1e-6));
  }
  function setHead(fig, idx) {
    const imgs = fig.querySelectorAll('.hd img'), sh = Math.floor(idx / SHEET), c = idx % SHEET;
    imgs.forEach((im, i) => { im.style.display = i === sh ? 'block' : 'none'; if (i === sh) { im.style.left = -(c % 16) * CELL_W + 'px'; im.style.top = -Math.floor(c / 16) * CELL_H + 'px'; } });
  }
  return { BODY, makeFig, place, setHead, narrFrame };
}
window.NoirAlley = { markup: () => ALLEY, cone: () => CONE, init, figs };
})();
