import { cx, Stamp, Swap } from '../components/bits';
import { Grid, Treasury, TREASURY } from '../components/Rig';
import story from '../data/story.json';
import type { SceneDef, SceneProps } from '../types';
import './s7.css';

const W = story.withdrawal;
const SPENT = new Set(story.rotation.consumedBefore);
const STAGED = [
  ['create witness account', '2,625 temporary bytes'],
  ['upload signature, chunk 1 of 3', ''],
  ['upload signature, chunk 2 of 3', ''],
  ['upload signature, chunk 3 of 3', ''],
  ['execute withdrawal', '674 bytes'],
];

function Arch({ on }: { on: boolean }) {
  return (
    <div className={cx('tech-ov arch', on && 'go')}>
      <span className="lbl tech-h">Technical file · account architecture, XMSS vault</span>
      <div className="acc acc-prog">
        <span className="lbl">Program · executable</span>
        <b>{story.program.id.slice(0, 10)}…</b>
        <span>{story.program.binaryBytes.toLocaleString('en-US')}-byte SBF binary · owns the state</span>
      </div>
      <div className="acc acc-state">
        <span className="lbl">State · PDA · 422 bytes</span>
        <div className="layout">
          <div className="seg hdr358">
            <span>header · 358 bytes</span>
            <div className="seg bm">leaf-use bitmap · 128 bytes</div>
          </div>
          <div className="seg r32">root · 32</div>
          <div className="seg s32">public seed · 32</div>
        </div>
        <span className="note">epoch and nonce live in the header; the program checks every intent against them</span>
      </div>
      <div className="acc acc-tre">
        <span className="lbl">Treasury · PDA · 8 bytes</span>
        <b>{TREASURY}</b>
        <span>holds SOL · signs token transfers as authority</span>
      </div>
      <div className="acc acc-tok">
        <span className="lbl">Token account · 165 bytes</span>
        <b>{W.tokenAccount.slice(0, 8)}…{W.tokenAccount.slice(-7)}</b>
        <span>holds USDC · owner: the treasury PDA</span>
      </div>
      <svg className="arch-w" viewBox="0 0 1920 1080">
        <path className="wire" d="M560,420 L700,420" markerEnd="url(#ah)" />
        <path className="wire dash" d="M1290,420 C1340,420 1340,330 1390,330" markerEnd="url(#ah)" />
        <path className="wire dash" d="M1290,470 C1340,470 1340,560 1390,560" markerEnd="url(#ah)" />
      </svg>
      <p className="tech-note bmnote">
        Bitmap: bit i set means one-time key i is spent. 1,024 keys, 1,024 bits, 128 bytes. A signature on a spent leaf is refused before it is verified. Persistent custody total: 595 bytes.
      </p>
    </div>
  );
}

function Rekey({ at, instant }: SceneProps) {
  const rot = at('rotate');
  const old = at('oldroot');
  return (
    <>
      <h1 className="hl">One transaction, and re-keying</h1>

      {/* five staged transactions collapse into one v1 transaction */}
      <div className="txs">
        {STAGED.map(([t, n], i) => (
          <div key={i} className="txc" style={{ ['--i' as string]: i }}>
            <span className="lbl">tx {i + 1} of 5</span>
            <b>{t}</b>
            {n && <span className="n">{n}</span>}
          </div>
        ))}
        <div className="txsum">
          XMSS signature <b>{W.witnessBytes.toLocaleString('en-US')} bytes</b> · legacy transactions: <b>5 per withdrawal</b>, 4,532 bytes in total
        </div>
      </div>
      <div className="onetx">
        <div className="card-h">
          <span>Version 1 transaction · devnet</span>
          <span>limit 4,096 bytes</span>
        </div>
        <div className="big">
          {W.bytes.toLocaleString('en-US')} bytes · {W.cu.toLocaleString('en-US')} CU · 1 transaction
        </div>
        <div className="fill">
          <i style={{ width: `${(W.bytes / 4096) * 100}%` }} />
        </div>
        <div className="parts">
          <span>intent + full 2,500-byte XMSS signature, verified on chain in one instruction</span>
        </div>
      </div>
      <Stamp on={at('one')} instant={instant} x={1440} y={640} size={44} r={-6} d={900} className="st-one">
        One transaction
      </Stamp>

      {/* rotation rig (ported from the mockup's scene C) */}
      <div className="rig7">
        <div className="bp-grid" />
        <div className="group" style={{ left: 470, top: 236, width: 890, height: 534 }}>
          <span className="lbl">Bunker program</span>
        </div>
        <div className="box verif">
          <span className="lbl">Verifier</span>
          <div className="rd">
            XMSS verify
            <span className="st">
              <Swap value={old ? 2 : rot ? 1 : 0} options={[<span style={{ color: 'var(--ink3)' }}>—</span>, <span className="blue">OK</span>, <span className="red">FAIL</span>]} d={old ? 880 : 1000} />
            </span>
            <span className="why">
              <Swap value={old ? 1 : 0} options={[' ', 'unknown root']} d={880} />
            </span>
          </div>
        </div>
        <div className="box drawer authC">
          <span className="lbl">Authorization account</span>
          <div className="sub">XMSS tree · 1,024 one-time keys</div>
          <div className="kv" style={{ left: 18 }}>
            ROOT
            <b>
              <Swap value={rot ? 1 : 0} options={['9f3a1c6e…0b7dc2e1', <span className="blue">d41c88a2…e5f307ab</span>]} d={1150} />
            </b>
          </div>
          <div className="kv" style={{ left: 252 }}>
            EPOCH
            <b>
              <Swap value={rot ? 1 : 0} options={['0', <span className="blue">1</span>]} d={1150} />
            </b>
          </div>
          <div className="used">
            <span>LEAVES USED</span>
            <b>
              <Swap value={rot ? 1 : 0} options={[String(SPENT.size), '0']} d={1150} /> / 1,024
            </b>
          </div>
          <Grid style={{ left: 21, top: 150 }} cls={(k) => (SPENT.has(k) ? 'x sp' : undefined)} />
        </div>
        <Treasury>
          <div className="tre-ok">Balances unchanged</div>
        </Treasury>
        <div className="reg">
          <i />
          <i />
          <i />
          <i />
          <span>Not moved</span>
        </div>
        <svg className="wires" viewBox="0 0 1920 1080">
          <path className={cx('wire draw', rot && 'go')} pathLength={1} d="M458,372 L486,372" style={{ ['--d' as string]: '500ms' }} />
          <path className={cx('wire draw', rot && 'go')} pathLength={1} d="M652,372 L676,372" style={{ ['--d' as string]: '800ms' }} />
          <path className="wire" d="M1040,580 L1080,580" markerEnd="url(#ah)" />
          <path className={cx('wire draw redw', old && 'go')} pathLength={1} d="M458,632 C520,632 566,560 570,476" style={{ ['--d' as string]: '560ms', strokeWidth: 2 }} />
        </svg>
        <div className="card i1">
          <div className="card-h">
            <span>Signed intent</span>
            <span>epoch 0</span>
          </div>
          <dl>
            <dt>action</dt>
            <dd>rotate root</dd>
            <dt>new root</dt>
            <dd>→ d41c88a2…e5f307ab</dd>
            <dt>signer</dt>
            <dd>unused leaf, old tree</dd>
            <dt>signature</dt>
            <dd style={{ fontWeight: 400 }}>XMSS · 2,500 bytes</dd>
          </dl>
          <div className="done">Executed · {story.rotation.bytes.toLocaleString('en-US')} bytes · {story.rotation.cu.toLocaleString('en-US')} CU</div>
        </div>
        <div className="card o1 redc">
          <div className="card-h">
            <span>Signed intent</span>
            <span>old root</span>
          </div>
          <dl>
            <dt>action</dt>
            <dd>withdraw SOL</dd>
            <dt>root</dt>
            <dd>9f3a1c6e…0b7dc2e1</dd>
            <dt>signer</dt>
            <dd>unused leaf, old tree</dd>
            <dt>signature</dt>
            <dd style={{ fontWeight: 400 }}>XMSS · 2,500 bytes</dd>
          </dl>
        </div>
        <div className="rec">
          <span className="lbl">Change record · rotation</span>
          <table>
            <tbody>
              <tr>
                <th>FIELD</th>
                <th>BEFORE</th>
                <th>AFTER</th>
              </tr>
              {[
                ['address', TREASURY.replace('…', '…'), TREASURY, 'eq'],
                ['SOL', 'held', 'held', 'eq'],
                ['USDC', 'held', 'held', 'eq'],
                ['root', '9f3a…c2e1', 'd41c…07ab', 'ch'],
                ['epoch', '0', '1', 'ch'],
                ['leaves used', String(SPENT.size), '0', 'ch'],
              ].map(([f, b, a, c], i) => (
                <tr key={f}>
                  <td>{f}</td>
                  <td>{b}</td>
                  <td className={c}>
                    <span className="type" style={{ ['--d' as string]: `${1300 + i * 100}ms`, ['--n' as string]: 16, ['--t' as string]: '300ms' }}>
                      {a}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Stamp on={old} instant={instant} x={286} y={660} size={58} r={-7} d={1150}>
          Rejected
        </Stamp>

        <div className="words">
          {Array.from({ length: 12 }, (_, k) => (
            <div className="w" key={k} style={{ ['--d' as string]: `${k * 45}ms` }}>
              <span className="redact" />
              <span>word {k + 1}</span>
            </div>
          ))}
        </div>
        <svg className="brk" viewBox="0 0 1920 1080">
          <path className={cx('wire draw', at('words') && 'go')} pathLength={1} d="M248,850 L248,860 L1672,860 L1672,850 M960,860 L960,884 M770,884 L1150,884 M770,884 L770,892 M1150,884 L1150,892" style={{ ['--d' as string]: '700ms' }} />
          <text x={970} y={877} fontFamily="Courier Prime, monospace" fontSize={12} letterSpacing={2} fill="#1f3a93" className={cx('fade', at('words') && 'go')} style={{ ['--d' as string]: '1000ms' }}>
            DERIVES
          </text>
        </svg>
        <div className="gen g0">generation 0</div>
        <div className="gen g1">generation 1 · active</div>
      </div>

      <Arch on={at('arch') && !at('rotate')} />
      <div className={cx('wash w7t', at('arch') && !at('rotate') && 'go')} />
      <div className={cx('wash w7', at('rekeyed') && 'go')} />
      <Stamp on={at('rekeyed')} instant={instant} x={960} y={575} size={150} r={-4} d={520} bold className="st-rk">
        Re-keyed
      </Stamp>
    </>
  );
}

export const S7: SceneDef = {
  key: 'rekey',
  exhibit: 'Exhibit 7',
  title: 'One transaction · rotation',
  steps: [{ id: 'five' }, { id: 'one' }, { id: 'bitmap' }, { id: 'arch', tech: true }, { id: 'rotate' }, { id: 'oldroot' }, { id: 'words' }, { id: 'rekeyed' }],
  C: Rekey,
};
