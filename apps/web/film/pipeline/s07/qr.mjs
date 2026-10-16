// Runs on any box with node: QR codes for slide 7's VERSION 3 boxes, same content and settings as the presentation's proof column
// (apps/web/src/scenes/cheap/proof.tsx: uqr, ECC L, no border, no logo). usage: node qr.mjs <path to uqr package dir> > film/data/s07-qr.js
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const code = 'https://github.com/chaintail/solana-bunker/blob/main/program/src/lib.rs#L118';
const tx = 'CiZmcGsaX4G7upT1ECscLUr1vVrX1htShX4Q2y8K4wd1hJcsVpfZEQc9GZtod8MxVSmP4Hy6mbVqiM75QiAJdBM';   // artifacts/public-deployment.json, version 3 withdrawal
const proof = `https://solscan.io/tx/${tx}?cluster=devnet`;
const q = (text) => { const r = encode(text, { ecc: 'L', border: 0 }); let d = ''; r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`))); return { n: r.size, d, text }; };
console.log('window.S07_QR = ' + JSON.stringify({ code: q(code), proof: q(proof), tx }) + ';');
