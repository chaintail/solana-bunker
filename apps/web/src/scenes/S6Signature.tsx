import { cx, Stamp } from '../components/bits';
import { Redact } from '../components/Redact';
import { DEST_A, DEST_B } from '../components/Rig';
import type { SceneDef, SceneProps } from '../types';
import './s6.css';

const X0 = 'c4e1907a 2fd35b88';
const X1 = '61b0f3d2 9a4e07c5';
const HX0 = '0d93a7e2…48f1';
const HX1 = '7be6c015…a3d9';

/* tree geometry: 16 leaves drawn, leaf 5 lit */
const LEAVES = 16;
const LIT = 5;
function treeNodes() {
  const W = 500,
    top = 70,
    H = 230;
  const levels: { x: number; y: number; on: boolean; path: boolean }[][] = [];
  for (let l = 0; l <= 4; l++) {
    const n = LEAVES >> l;
    const y = top + H - (l * H) / 4;
    const row = [];
    for (let j = 0; j < n; j++) {
      const x = 22 + ((j + 0.5) * (W - 44)) / n;
      const anc = LIT >> l;
      row.push({ x, y, on: j === anc, path: j === (anc ^ 1) && l < 4 });
    }
    levels.push(row);
  }
  return levels;
}
const TREE = treeNodes();

function Lamport8({ on }: { on: boolean }) {
  // message byte 0x42 ("B") bit by bit
  const bits = [0, 1, 0, 0, 0, 0, 1, 0];
  return (
    <div className={cx('tech-ov lam8', on && 'go')}>
      <span className="lbl tech-h">Technical file · Lamport over one byte</span>
      <p className="tech-sub">Sign the byte 0x42. Each bit reveals one of its two secrets; the other stays sealed.</p>
      <div className="l8">
        {bits.map((b, i) => (
          <div className="l8c" key={i} style={{ ['--i' as string]: i }}>
            <span className="l8b">{b}</span>
            <span className={cx('l8s', b === 0 && 'rev')}>
              x<sub>{i},0</sub>
            </span>
            <span className={cx('l8s', b === 1 && 'rev')}>
              x<sub>{i},1</sub>
            </span>
          </div>
        ))}
      </div>
      <p className="tech-note">
        Flip bit 7 from 0 to 1 and the forger needs x<sub>7,1</sub>, a secret that was never revealed. Real keys use 256 bit pairs: 512 secrets, 256 revealed per signature, one signature per key.
      </p>
    </div>
  );
}

function Checksum({ on }: { on: boolean }) {
  const cells = Array.from({ length: 16 }, (_, k) => k);
  return (
    <div className={cx('tech-ov wsum', on && 'go')}>
      <span className="lbl tech-h">Technical file · why the Winternitz chain needs a checksum</span>
      <p className="tech-sub">A signature reveals H<sup>b</sup>(sk). Anyone can hash forward, so b could be pushed up. The checksum chain moves the other way.</p>
      <div className="wrow">
        <span className="wl">message digit b = 5</span>
        {cells.map((k) => (
          <i key={k} className={cx(k === 5 && 'at', k > 5 && 'fwd')} />
        ))}
        <span className="wn blue">forger can reach 6, 7, … by hashing</span>
      </div>
      <div className="wrow">
        <span className="wl">checksum digit 15 − b = 10</span>
        {cells.map((k) => (
          <i key={k} className={cx(k === 10 && 'at', k < 10 && 'back')} />
        ))}
        <span className="wn red">raising b means lowering this: needs a preimage</span>
      </div>
      <p className="tech-note">WOTS+ in RFC 8391 uses w = 16: 64 message digits plus 3 checksum digits, len = 67 chains of 32-byte values per one-time key.</p>
    </div>
  );
}

function Signature({ at, instant }: SceneProps) {
  const attack = at('attack');
  return (
    <>
      <h1 className="hl">A signature made of hashes</h1>

      {/* Lamport, one bit */}
      <section className={cx('panel p-lam', attack && 'dim')}>
        <span className="lbl ph">Lamport · one bit</span>
        <div className="lam">
          {[0, 1].map((b) => (
            <div key={b} className={cx('lcol', `b${b}`)}>
              <span className="lk">secret x{b === 0 ? '₀' : '₁'}</span>
              <div className="sec">
                <span className="redact sealbar" style={{ width: 168, height: 22 }} />
                <span className="hexr">{b === 0 ? X0 : X1}</span>
              </div>
              <i className="down" />
              <span className="lk">public H(x{b === 0 ? '₀' : '₁'})</span>
              <div className="pubh">{b === 0 ? HX0 : HX1}</div>
            </div>
          ))}
        </div>
        <div className="msgbit">
          message bit <b>1</b> → reveal x₁, keep x₀ sealed
        </div>
        <div className="peq">
          <span className="lbl">definition</span>
          <Redact eq="lamport" w={220} h={18} />
        </div>
      </section>

      {/* Winternitz chain */}
      <section className={cx('panel p-chain', attack && 'dim')}>
        <span className="lbl ph">Winternitz · one hash chain, w = 16</span>
        <svg className="chain" viewBox="0 0 520 120">
          {Array.from({ length: 16 }, (_, k) => (
            <g key={k}>
              {k > 0 && <line className="cl" x1={20 + (k - 1) * 32 + 9} x2={20 + k * 32 - 9} y1={50} y2={50} />}
              <circle className={cx('cn', k <= 5 && 'past', k === 0 && 'sk', k === 15 && 'pk')} cx={20 + k * 32} cy={50} r={8} style={{ ['--k' as string]: k }} />
            </g>
          ))}
          <text x={20} y={90} textAnchor="middle" className="ct">
            sk
          </text>
          <text x={20 + 5 * 32} y={90} textAnchor="middle" className="ct blue-t">
            σ = H⁵(sk)
          </text>
          <text x={20 + 15 * 32} y={90} textAnchor="middle" className="ct">
            pk = H¹⁵(sk)
          </text>
          <g className="tick" style={{ ['--to' as string]: `${5 * 32}px` }}>
            <path d="M20,22 l-7,-10 h14 z" fill="#b3242a" />
          </g>
        </svg>
        <div className="cnote">signs the digit 5: reveal H⁵(sk); the verifier hashes 10 more times and must land on pk</div>
        <div className="peq">
          <span className="lbl">definition</span>
          <Redact eq="wots" w={220} h={18} />
        </div>
      </section>

      {/* Merkle tree, one leaf lit */}
      <section className={cx('panel p-tree', attack && 'dim')}>
        <span className="lbl ph">XMSS · 1,024 one-time keys under one root</span>
        <svg className="tree" viewBox="0 0 500 330">
          {TREE.slice(0, 4).map((row, l) =>
            row.map((n, j) => {
              const p = TREE[l + 1][j >> 1];
              return <line key={`${l}-${j}`} className={cx('te', n.on && 'on')} x1={n.x} y1={n.y} x2={p.x} y2={p.y} />;
            }),
          )}
          {TREE.map((row, l) =>
            row.map((n, j) =>
              l === 0 ? (
                <rect key={`n${l}-${j}`} className={cx('tn leaf', n.on && 'on', n.path && 'path')} x={n.x - 9} y={n.y - 9} width={18} height={18} />
              ) : (
                <circle key={`n${l}-${j}`} className={cx('tn', n.on && 'on', n.path && 'path', l === 4 && 'root')} cx={n.x} cy={n.y} r={l === 4 ? 11 : 7} />
              ),
            ),
          )}
          <text x={250} y={40} textAnchor="middle" className="ct">
            root (stored on chain, 32 bytes)
          </text>
          <text x={TREE[0][LIT].x} y={330} textAnchor="middle" className="ct blue-t">
            one-time key in use
          </text>
        </svg>
        <div className="cnote">blue: the authentication path that travels with the signature</div>
        <div className="peq">
          <span className="lbl">definition</span>
          <Redact eq="xmss" w={220} h={18} align="right" />
        </div>
      </section>

      {/* the attack, again */}
      <div className="atk">
        <div className="agent a6">
          <svg>
            <use href="#agent" />
          </svg>
          <div className="lbl">Name</div>
          <span className="redact" style={{ width: 92, height: 13 }} />
        </div>
        <div className="card redc c6">
          <div className="card-h">
            <span>Copied withdrawal</span>
            <span>priority fee ×10</span>
          </div>
          <dl>
            <dt>to</dt>
            <dd>
              address <s className="red-s">A</s> <span className="red">B</span>
              <small>{DEST_B}</small>
            </dd>
            <dt>signature</dt>
            <dd style={{ fontWeight: 400 }}>XMSS · 2,500 bytes, signed for address A</dd>
          </dl>
        </div>
        <svg className="wires a6w" viewBox="0 0 1920 1080">
          <path className={cx('wire draw redw', attack && 'go')} pathLength={1} d="M906,850 L960,850" style={{ ['--d' as string]: '300ms', strokeWidth: 2 }} />
        </svg>
        <div className="box verif6">
          <span className="lbl">Verifier · XMSS</span>
          <div className="vrow">
            message <b>withdraw SOL → {DEST_B}</b>
          </div>
          <div className="vrow">
            signed <b>withdraw SOL → {DEST_A}</b>
          </div>
          <div className="vres">FAIL · signature does not match</div>
        </div>
      </div>
      <Stamp on={attack} instant={instant} x={1606} y={904} size={100} r={-8} d={1100}>
        Rejected
      </Stamp>

      <Lamport8 on={at('lamport8') && !at('chain')} />
      <Checksum on={at('checksum') && !at('tree')} />
      <div className={cx('wash w6', (at('lamport8') && !at('chain')) || (at('checksum') && !at('tree')) ? 'go' : '')} />
    </>
  );
}

export const S6: SceneDef = {
  key: 'sig',
  exhibit: 'Exhibit 6',
  title: 'Version three · hash-based signatures',
  steps: [{ id: 'lamport' }, { id: 'reveal' }, { id: 'lamport8', tech: true }, { id: 'chain' }, { id: 'checksum', tech: true }, { id: 'tree' }, { id: 'attack' }],
  C: Signature,
};
