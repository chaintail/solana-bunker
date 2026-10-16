// Runs on any box with node. The testimonial's results cards (film-plan-ending.md part A): every account and signature is read from
// artifacts/public-deployment.json by operation name or vault mode, nothing typed in. Same QR settings as qr.mjs (uqr, ECC L, no border, no logo).
// Solscan opens mainnet unless told otherwise, so every link keeps ?cluster=devnet.
// usage: node qr-results.mjs <path to uqr package dir> <public-deployment.json> > film/data/s09-results.js
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const D = JSON.parse(readFileSync(process.argv[3], 'utf8'));
const q = (text) => { const r = encode(text, { ecc: 'L', border: 0 }); let d = ''; r.data.forEach((row, y) => row.forEach((on, x) => on && (d += `M${x},${y}h1v1h-1z`))); return { n: r.size, d, text }; };
const tx = (op) => { const t = D.confirmed_transactions.find((x) => x.operation === op); if (!t || !t.confirmed || !t.success) throw new Error('no confirmed tx ' + op); return t.transaction_signature; };
const vault = (mode) => { const v = D.vaults.find((x) => x.mode === mode); if (!v) throw new Error('no vault ' + mode); return v; };
const sim = (op) => { const s = D.simulations.find((x) => x.operation === op); if (!s) throw new Error('no simulation ' + op); return s; };
const acct = (a) => `https://solscan.io/account/${a}?cluster=devnet`, txu = (s) => `https://solscan.io/tx/${s}?cluster=devnet`;
const short = (s) => s.slice(0, 8) + '…' + s.slice(-4);
const run = D.demo_run_id;
const rej = sim(`${run}-xmss-withdraw-sol-destination-substitution`);
const rejLog = rej.result.value.logs.find((l) => / failed: /.test(l)) || '';
const out = {
  cluster: D.cluster, program: D.program_id,
  live: { qr: q(acct(D.program_id)), id: D.program_id, short: short(D.program_id) },
  vaults: ['array', 'merkle', 'xmss'].map((m) => { const v = vault(m); return { mode: m, treasury: v.treasury, short: short(v.treasury), leaves: v.leaf_capacity, qr: q(acct(v.treasury)) }; }),
  sol: { sig: tx(`${run}-xmss-withdraw-sol`), qr: null }, usdc: { sig: tx(`${run}-xmss-withdraw-mock-usdc`), qr: null, label: D.mock_token_label },
  rotation: { sig: tx(`${run}-xmss-rotate-root`), qr: null, epoch: D.vaults.find((x) => x.mode === 'xmss').final_snapshot.epoch },
  // no devnet transaction exists for these two (see the plan, risk RA1): the robbery is local SVM test M03, the rejection a devnet simulation
  robbery: { sig: null, note: 'version two front-run: local SVM test only (acceptance matrix M03), no devnet signature' },
  rejection: { sig: null, op: rej.operation, evidence: rej.evidence_level, err: rej.expected_error_verified, log: rejLog.replace(/^Program \S+ /, 'Program ') },
};
for (const k of ['sol', 'usdc', 'rotation']) { out[k].qr = q(txu(out[k].sig)); out[k].short = short(out[k].sig); }
console.log('window.S09_RESULTS = ' + JSON.stringify(out) + ';');
