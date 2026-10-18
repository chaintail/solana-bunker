// Runs on any box with node: QR codes for scene 9's proof boxes and the CALL NOW repo link, same settings as slide 7 / scene 8
// (apps/web/src/scenes/cheap/proof.tsx: uqr, ECC L, no border, no logo). usage: node qr.mjs <path to uqr package dir> > film/data/s09-qr.js
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const code = 'https://github.com/chaintail/solana-bunker/blob/main/client/kdf.py#L10';          // bip39_seed
const paper = 'https://github.com/chaintail/solana-bunker/blob/main/research/whitepaper.md#L35'; // the BIP-39/HKDF project-seed recipe
const repo = 'https://github.com/chaintail/solana-bunker';                                        // CALL NOW
const q = (text) => { const r = encode(text, { ecc: 'L', border: 0 }); let d = ''; r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`))); return { n: r.size, d, text }; };
console.log('window.S09_QR = ' + JSON.stringify({ code: q(code), paper: q(paper), repo: q(repo) }) + ';');
