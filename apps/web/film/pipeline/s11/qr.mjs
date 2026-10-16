// Runs on any box with node: the parchment outro's three codes (Liam's look-C notes): the repo, Telegram and X/Twitter, ECC H so a logo can sit in the
// centre of each without breaking decoding (as the deck's closing slide, C9Close.tsx: ECC H, logo over at most 16 % of the symbol). uqr, no border; minVersion 5, so all three are 37 modules and render at the same size.
// usage: node qr.mjs <path to uqr package dir> > film/data/s11-qr.js
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const q = (text) => { const r = encode(text, { ecc: 'H', border: 0, minVersion: 5 }); let d = ''; r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`))); return { n: r.size, d, text }; };
console.log('window.S11_QR = ' + JSON.stringify({ repo: q('https://github.com/chaintail/solana-bunker'), tg: q('https://t.me/chaintail'), x: q('https://x.com/ChaintailLabs') }) + ';');
