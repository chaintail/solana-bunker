// The vault door from scene 4 (film/s04 s04-bunker.html, function vault), ported for reuse: scene 10's "bunker protecting a bunker" box.
// window.vaultDraw(svg, cx, cy, R, level, col) draws the door into an <svg> (ink colour col, default scene 4's #eaf7fb) and returns its parts:
// { rings, spokes, hinges, extra: <path pathLength=1> (dash 1, offset 0 = drawn), bolts: <circle> (incl. the spoke knobs) }.
// Same geometry as scene 4; stroke widths scale with R (scene 4 drew at R 96-150) so a small inner door keeps proportionate lines.
(() => {
  const NS = 'http://www.w3.org/2000/svg', INKC = '#eaf7fb';
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };
  window.vaultDraw = (parent, cx, cy, R, level, col = INKC) => {
    const o = { rings: [], bolts: [], spokes: [], hinges: [], extra: [] }, sc = Math.min(1, Math.max(.4, R / 96)), sw = [3, 3.5, 4.5][level] * sc;
    const mp = (d, a = {}) => el('path', Object.assign({ d, pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 0, 'stroke-width': sw, stroke: col }, a), parent);
    const circ = (r) => `M${cx} ${cy}m${-r} 0a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0`;
    const radii = [[1, .86, .62], [1.03, .88, .7, .6], [1.08, .94, .8, .66, .56]][level];
    radii.forEach((k, i) => o.rings.push(mp(circ(R * k), { 'stroke-width': i === 0 ? sw + 2 * sc : sw })));
    const nb = [8, 12, 16][level];
    for (let i = 0; i < nb; i++) { const a = (i / nb) * Math.PI * 2, rr = R * (level === 0 ? .93 : level === 1 ? .94 : 1.0);
      o.bolts.push(el('circle', { cx: cx + rr * Math.cos(a), cy: cy + rr * Math.sin(a), r: R * (.045 + .005 * level), fill: col, stroke: 'none' }, parent)); }
    const ns = [4, 5, 6][level];
    for (let i = 0; i < ns; i++) { const a = (i / ns) * Math.PI * 2 - Math.PI / 2, r0 = R * .17, r1 = R * (level === 2 ? .52 : .58);
      o.spokes.push(mp(`M${cx + r0 * Math.cos(a)} ${cy + r0 * Math.sin(a)}L${cx + r1 * Math.cos(a)} ${cy + r1 * Math.sin(a)}`, { 'stroke-width': sw + sc }));
      o.bolts.push(el('circle', { cx: cx + r1 * Math.cos(a), cy: cy + r1 * Math.sin(a), r: R * .045, fill: col, stroke: 'none' }, parent)); }
    o.rings.push(mp(circ(R * .17), { 'stroke-width': sw + sc }));
    const nh = [2, 3, 4][level];
    for (let i = 0; i < nh; i++) { const yy = cy - R * .6 + i * (R * 1.2 / Math.max(1, nh - 1)), hh = 15 * sc, hw = 24 * sc;
      o.hinges.push(mp(`M${cx - R * 1.02} ${yy - hh}H${cx - R * 1.02 - hw}V${yy + hh}H${cx - R * 1.02}`)); }
    if (level > 0) { const nl = level === 1 ? 2 : 4;
      for (let i = 0; i < nl; i++) { const a = [-Math.PI / 4, Math.PI / 4, 3 * Math.PI / 4, -3 * Math.PI / 4][i], x = cx + R * 1.06 * Math.cos(a), y = cy + R * 1.06 * Math.sin(a), lw = 12 * sc, lh = 9 * sc;
        o.extra.push(mp(`M${x - lw} ${y - lh}H${x + lw}V${y + lh}H${x - lw}Z`)); } }
    return o;
  };
})();
