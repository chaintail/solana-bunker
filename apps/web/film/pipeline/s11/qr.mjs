// Runs on any box with node: the parchment outro's two codes (the links of the deck's closing slide, apps/web/src/scenes/cheap/C9Close.tsx),
// same settings as the film's other codes (uqr, ECC L, no border, no logo on the code; the logos are printed beneath with the links).
// usage: node qr.mjs <path to uqr package dir> > film/data/s11-qr.js
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const q = (text) => { const r = encode(text, { ecc: 'L', border: 0 }); let d = ''; r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`))); return { n: r.size, d, text }; };
console.log('window.S11_QR = ' + JSON.stringify({ repo: q('https://github.com/chaintail/solana-bunker'), tg: q('https://t.me/chaintail') }) + ';');
