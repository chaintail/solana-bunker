// Runs on any box with node: scene 10's whitepaper code (OTS box on "white paper"), same settings as the film's other codes (uqr, ECC L, no border, no logo).
// usage: node qr.mjs <path to uqr package dir> > film/data/s10-qr.js
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const q = (text) => { const r = encode(text, { ecc: 'L', border: 0 }); let d = ''; r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`))); return { n: r.size, d, text }; };
console.log('window.S10_QR = ' + JSON.stringify({ paper: q('https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md') }) + ';');
