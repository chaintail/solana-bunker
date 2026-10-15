// Real screenshot of a live page via headless Chrome (CDP): node shot-url.mjs <url> <out.png> [waitMs] [width] [height]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const [url, out, wait = '9000', w = '1440', h = '900', js = ''] = process.argv.slice(2);   // js: expression run after the first wait (e.g. dismiss dialogs), then 2.5 s more
const port = 9300 + Math.floor(Math.random() * 400), profile = mkdtempSync(join(tmpdir(), 'shot-chrome-'));
const chrome = spawn(process.env.CHROME || '/usr/bin/google-chrome', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, '--no-first-run', '--hide-scrollbars', '--force-color-profile=srgb', '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36', 'about:blank'], { stdio: 'ignore', detached: true });
const cleanup = () => { try { process.kill(-chrome.pid, 'SIGKILL'); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
process.on('exit', cleanup);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
for (let i = 0; i < 60; i++) { try { const l = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); ws = new WebSocket(l.find((t) => t.type === 'page').webSocketDebuggerUrl); await new Promise((r, j) => ((ws.onopen = r), (ws.onerror = j))); break; } catch { await sleep(200); } }
let id = 0; const pend = new Map(); ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url }); await sleep(+wait);
if (js) { await send('Runtime.evaluate', { expression: js, awaitPromise: true }); await sleep(2500); }
const r = await send('Page.captureScreenshot', { format: 'png' }); writeFileSync(out, Buffer.from(r.result.data, 'base64')); console.log('saved', out);
cleanup(); process.exit(0);
