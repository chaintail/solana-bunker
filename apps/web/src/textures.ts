/*
 * The paper textures from the Pass B mockup are SVG feTurbulence images. Used
 * directly as CSS backgrounds, Chrome may re-rasterize them per tile on every
 * repaint, which stalls software-rendered machines. Rasterize each one once
 * into a bitmap and hand CSS a blob URL instead. Same SVG, same look.
 */
const MOTTLE = `<svg xmlns='http://www.w3.org/2000/svg' width='960' height='540'><filter id='m'><feTurbulence type='fractalNoise' baseFrequency='0.0035 0.006' numOctaves='4' seed='7' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.45 0 0 0 0 0.33 0 0 0 0 0.14 0 0 0 1.5 -0.62'/></filter><rect width='100%' height='100%' filter='url(#m)'/></svg>`;
const GRAIN = `<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='g'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' seed='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.25 0 0 0 0 0.19 0 0 0 0 0.1 0 0 0 1.1 -0.42'/></filter><rect width='100%' height='100%' filter='url(#g)'/></svg>`;

async function bake(name: string, svg: string, w: number, h: number) {
  const img = new Image();
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  await img.decode();
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  c.getContext('2d')!.drawImage(img, 0, 0, w, h);
  const blob = await new Promise<Blob | null>((r) => c.toBlob(r, 'image/png'));
  if (!blob) return;
  document.documentElement.style.setProperty(`--tex-${name}`, `url(${URL.createObjectURL(blob)})`);
}

export function bakeTextures() {
  bake('mottle', MOTTLE, 960, 540).catch(() => {});
  bake('grain', GRAIN, 240, 240).catch(() => {});
}
