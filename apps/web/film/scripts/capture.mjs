// Render a film scene to PNG frames with headless Chrome (CDP, no dependencies).
//   node film/scripts/capture.mjs <scene> [--layer=front|back] [--still=<t>[,<t>...]] [--from=<s>] [--to=<s>] [--out=<dir>]
// --speed=<f> (or --speed <f>) time-scales the frame sequence: output frame k samples the page at t = k/fps * f, frame count ceil(N/f) for the N = duration*fps
//   frames of the scene; the last output frame is pinned to the scene's last frame (N-1)/fps so the hand-off frame is unchanged. --from/--to are output seconds then.
// Frames: apps/web/render/<scene>[-<layer>]/f%05d.png (fps from data-fps), gitignored.
// With --layer the page background is transparent, so the PNGs carry alpha.
// With --still, writes <out>/still-<t>.png for each time instead of the frame sequence.
// CHROME env overrides the browser binary (macOS: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome").
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2).reduce((a, x, i, all) => { if (i > 0 && all[i - 1] === '--speed' && !x.startsWith('--')) a[a.length - 1] = '--speed=' + x; else a.push(x); return a; }, []);
const scene = args.find((a) => !a.startsWith('--'));
const opt = Object.fromEntries(args.filter((a) => a.startsWith('--')).map((a) => { const [k, v = '1'] = a.slice(2).split('='); return [k, v]; }));
if (!scene) { console.error('usage: capture.mjs <scene> [--layer=front|back] [--still=t,t] [--from=s] [--to=s] [--out=dir]'); process.exit(2); }
const layer = opt.layer || '';
const out = resolve(opt.out || join(here, '../../render', scene + (layer ? '-' + layer : '')));
mkdirSync(out, { recursive: true });

const port = 9800 + Math.floor(Math.random() * 400);
const profile = mkdtempSync(join(tmpdir(), 'film-chrome-'));
const chrome = spawn(process.env.CHROME || '/usr/bin/google-chrome', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, '--no-first-run', '--hide-scrollbars', '--force-color-profile=srgb', '--allow-file-access-from-files', 'about:blank'], { stdio: 'ignore', detached: true });   // own process group so helper processes die with it
// Always quit this Chrome and delete its user-data-dir, on normal exit, errors, and SIGINT/SIGTERM/SIGHUP (leaked profiles filled dev-mac's disk).
let cleaned = false;
const cleanup = () => {
  if (cleaned) return; cleaned = true;
  try { process.kill(-chrome.pid, 'SIGKILL'); } catch { try { chrome.kill('SIGKILL'); } catch {} }
  try { rmSync(profile, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 }); } catch {}
};
process.on('exit', cleanup);
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(sig, () => { cleanup(); process.exit(130); });
process.on('uncaughtException', (e) => { console.error(e); cleanup(); process.exit(1); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
for (let i = 0; i < 60; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => ((ws.onopen = r), (ws.onerror = j)));
    break;
  } catch { await sleep(200); }
}
let id = 0; const pending = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } };
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, (d) => (d.error ? rej(new Error(method + ': ' + d.error.message)) : res(d.result))); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expression) => (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result.value;

try {
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  if (layer) await send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
  await send('Page.navigate', { url: `file://${resolve(here, '..', scene + '.html')}?capture${layer ? '&layer=' + layer : ''}` });
  for (let i = 0; i < 300; i++) { if (await ev("document.documentElement.dataset.filmReady==='1'")) break; await sleep(100); }
  const shot = async (t, file) => {
    await ev(`(async()=>{window.__film.seek(${t});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return 1})()`);
    const { data } = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
    writeFileSync(file, Buffer.from(data, 'base64'));
  };
  if (opt.still) {
    for (const t of opt.still.split(',')) await shot(Number(t), join(out, `still-${t}.png`));
  } else {
    const fps = await ev('window.__film.fps'), dur = await ev('window.__film.duration');
    const speed = Number(opt.speed || 1); if (!(speed > 0)) throw new Error('--speed must be > 0');
    const N = Math.round(dur * fps), M = speed === 1 ? N : Math.ceil(N / speed - 1e-9);   // source frames, output frames
    const pt = (f) => (speed === 1 ? f : f === M - 1 ? N - 1 : Math.min(f * speed, N - 1)) / fps;   // output frame -> page time
    if (speed !== 1) console.log(`speed ${speed}: ${N} scene frames -> ${M} output frames`);
    const a = Math.round(Number(opt.from ?? 0) * fps), b = Math.min(M, opt.to ? Math.round(Number(opt.to) * fps) : Infinity);
    for (let f = a; f < b; f++) {
      await shot(pt(f), join(out, `f${String(f).padStart(5, '0')}.png`));
      if (f % 100 === 0) console.log(`${scene}${layer ? ':' + layer : ''} frame ${f}/${b}`);
    }
  }
  console.log('done ->', out);
} finally { cleanup(); }
process.exit(0);
