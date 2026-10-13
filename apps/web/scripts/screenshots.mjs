// Screenshot every step of every scene on both routes with headless Chrome (CDP, no deps).
// usage: node scripts/screenshots.mjs <baseUrl> [outDir] [filter]
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const base = process.argv[2] || 'http://127.0.0.1:5173/';
const out = resolve(process.argv[3] || 'screenshots');
const filter = process.argv[4] ? new RegExp(process.argv[4]) : null;
const sizes = (process.env.SIZES || '1920x1080,390x844').split(',').map((s) => s.split('x').map(Number));
mkdirSync(out, { recursive: true });

const port = 9300 + Math.floor(Math.random() * 500);
const prof = mkdtempSync(join(tmpdir(), 'sb-chrome-'));
const chrome = spawn('/usr/bin/google-chrome', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--no-first-run', '--hide-scrollbars', '--force-color-profile=srgb', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
for (let i = 0; i < 50; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    const page = list.find((t) => t.type === 'page');
    ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((r, j) => ((ws.onopen = r), (ws.onerror = j)));
    break;
  } catch {
    await sleep(200);
  }
}
let id = 0;
const pending = new Map();
const events = [];
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) {
    pending.get(d.id)(d);
    pending.delete(d.id);
  } else if (d.method) events.push(d);
};
const send = (method, params = {}) =>
  new Promise((r) => {
    const i = ++id;
    const t = setTimeout(() => {
      pending.delete(i);
      console.log('timeout', method, JSON.stringify(params).slice(0, 80));
      r({});
    }, 15000);
    pending.set(i, (d) => {
      clearTimeout(t);
      r(d);
    });
    ws.send(JSON.stringify({ id: i, method, params }));
  });
const evalJs = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.result?.value;

await send('Page.enable');
await send('Runtime.enable');
const problems = [];
for (const [w, h] of sizes) {
  await send('Page.navigate', { url: 'about:blank' });
  await sleep(300);
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 800 });
  await send('Page.navigate', { url: base + (process.env.FULL ? '' : '?lite') + '#0-0' });
  await sleep(2500);
  await evalJs('document.fonts.ready.then(()=>1)');
  const plan = await evalJs('JSON.stringify(window.__deck && window.__deck.plan())');
  if (!plan) throw new Error('window.__deck missing');
  for (const route of ['pitch', 'technical']) {
    for (const [i, n] of JSON.parse(plan)[route].entries()) {
      const sc = { i };
      if (process.env.ROUTES && !process.env.ROUTES.includes(route)) continue;
      for (let s = 0; s < n; s++) {
        const name = `${w}x${h}_${route === 'technical' ? 't' : 'p'}_${String(sc.i).padStart(2, '0')}-${String(s).padStart(2, '0')}`;
        if (filter && !filter.test(name)) continue;
        const hash = `#${sc.i}-${s}${route === 'technical' ? '-t' : ''}`;
        await evalJs(`location.hash=${JSON.stringify(hash)};1`);
        await sleep(+(process.env.WAIT || 450));
        const ov = await evalJs('JSON.stringify(window.__deck.overflow())');
        if (ov && ov !== '[]') problems.push(`${name}: ${ov}`);
        const shot = await send('Page.captureScreenshot', { format: 'png' });
        if (!shot.result) continue;
        if (process.env.V) console.log(name);
        writeFileSync(join(out, name + '.png'), Buffer.from(shot.result.data, 'base64'));
      }
    }
  }
}
console.log('done', out);
if (problems.length) console.log('OUT OF STAGE:\n' + problems.join('\n'));
ws.close();
chrome.kill();
