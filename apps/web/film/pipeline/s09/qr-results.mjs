// Runs on any box with node. The testimonial's results cards (film-plan-ending.md part A): every account and signature is read from
// artifacts/public-deployment.json by operation name or vault mode, nothing typed in. Same QR settings as qr.mjs (uqr, ECC L, no border, no logo).
// Solscan opens mainnet unless told otherwise, so every link keeps ?cluster=devnet.
// The robbery and the rejection have no devnet signature (risk RA1). Composer ruling R-A1 (b): their cards get a QR to the GitHub evidence on branch
// main, at the file and line: the M03 entry of artifacts/acceptance-matrix.json (local SVM test) and the devnet simulation entry of
// artifacts/public-deployment.json. The line numbers are found in main's copies of the two files (pass them in), not typed in.
// usage: node qr-results.mjs <path to uqr package dir> <public-deployment.json> <acceptance-matrix.json> > film/data/s09-results.js
//   (both json files as on main, e.g. git show main:artifacts/public-deployment.json > /tmp/x/pd.json)
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { encode } = require(process.argv[2]);
const DT = readFileSync(process.argv[3], 'utf8'), D = JSON.parse(DT), MT = readFileSync(process.argv[4], 'utf8'), M = JSON.parse(MT);
const line = (text, needle) => { const i = text.split('\n').findIndex((l) => l.includes(needle)); if (i < 0) throw new Error('not found ' + needle); return i + 1; };
const GH = 'https://github.com/chaintail/solana-bunker/blob/main/';
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
  robbery: { sig: null, note: 'version two front-run: local SVM test only (acceptance matrix M03), no devnet signature', label: 'local test' },
  rejection: { sig: null, op: rej.operation, evidence: rej.evidence_level, err: rej.expected_error_verified, log: rejLog.replace(/^Program \S+ /, 'Program '), label: 'devnet simulation' },
};
{ const m = M.items ? M.items.find((x) => x.id === 'M03') : null; const m03 = m || JSON.stringify(M).includes('"M03"');
  if (!m03) throw new Error('no M03 in the acceptance matrix');
  const L1 = line(MT, '"id": "M03"'), L2 = line(DT, `"operation": "${rej.operation}"`);
  out.robbery.url = `${GH}artifacts/acceptance-matrix.json#L${L1}`; out.robbery.ref = `acceptance-matrix.json line ${L1}`; out.robbery.qr = q(out.robbery.url);
  out.rejection.url = `${GH}artifacts/public-deployment.json#L${L2}`; out.rejection.ref = `public-deployment.json line ${L2}`; out.rejection.qr = q(out.rejection.url); }
for (const k of ['sol', 'usdc', 'rotation']) { out[k].qr = q(txu(out[k].sig)); out[k].short = short(out[k].sig); }
console.log('window.S09_RESULTS = ' + JSON.stringify(out) + ';');
