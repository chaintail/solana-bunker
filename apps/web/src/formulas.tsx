import type { ReactNode } from 'react';

const V = ({ children }: { children: ReactNode }) => <i className="v">{children}</i>;

export type FormulaId = 'lamport' | 'wots' | 'xmss' | 'slh' | 'eth' | 'merkle';

export const FORMULAS: Record<FormulaId, { label: string; title: string; body: ReactNode; source: string; href: string }> = {
  lamport: {
    label: 'Lamport',
    title: 'Lamport one-time signature (1979)',
    body: (
      <>
        <span className="ln">
          <V>sk</V> = ( <V>x</V><sub>i,0</sub>, <V>x</V><sub>i,1</sub> ) for <V>i</V> = 1 … 256
        </span>
        <span className="ln">
          <V>pk</V> = ( <V>H</V>(<V>x</V><sub>i,0</sub>), <V>H</V>(<V>x</V><sub>i,1</sub>) )
        </span>
        <span className="ln">
          sign <V>m</V>: &nbsp;<V>σ</V><sub>i</sub> = <V>x</V><sub>i, m<sub>i</sub></sub>
        </span>
        <span className="ln">
          verify: &nbsp;<V>H</V>(<V>σ</V><sub>i</sub>) = <V>pk</V><sub>i, m<sub>i</sub></sub> &nbsp;for every <V>i</V>
        </span>
      </>
    ),
    source: 'L. Lamport, Constructing Digital Signatures from a One Way Function, SRI CSL-98, 1979',
    href: 'https://www.microsoft.com/en-us/research/publication/constructing-digital-signatures-one-way-function/',
  },
  wots: {
    label: 'WOTS+ chain',
    title: 'WOTS+ chaining function',
    body: (
      <>
        <span className="ln">
          <V>c</V><sup>0</sup>(<V>X</V>, <V>i</V>) = <V>X</V>
        </span>
        <span className="ln">
          <V>c</V><sup>s</sup>(<V>X</V>, <V>i</V>) = <V>F</V>( <V>KEY</V>, <V>c</V><sup>s−1</sup>(<V>X</V>, <V>i</V>) ⊕ <V>BM</V> )
        </span>
        <span className="ln sm">
          <V>KEY</V>, <V>BM</V> = <V>PRF</V>(<V>SEED</V>, <V>ADRS</V>) at hash address <V>i</V>+<V>s</V>−1
        </span>
        <span className="ln">
          <V>pk</V><sub>j</sub> = <V>c</V><sup>w−1</sup>(<V>sk</V><sub>j</sub>, 0) &nbsp;&nbsp; <V>σ</V><sub>j</sub> = <V>c</V><sup>b<sub>j</sub></sup>(<V>sk</V><sub>j</sub>, 0)
        </span>
        <span className="ln">
          verify: <V>c</V><sup>w−1−b<sub>j</sub></sup>(<V>σ</V><sub>j</sub>, <V>b</V><sub>j</sub>) = <V>pk</V><sub>j</sub> &nbsp;&nbsp;(<V>w</V> = 16, <V>len</V> = 67)
        </span>
      </>
    ),
    source: 'RFC 8391 §3.1.2, WOTS+ Chaining Function',
    href: 'https://www.rfc-editor.org/rfc/rfc8391#section-3.1.2',
  },
  xmss: {
    label: 'XMSS tree hash',
    title: 'XMSS randomized tree hashing',
    body: (
      <>
        <span className="ln">
          <V>node</V><sub>h, j</sub> = <V>RAND_HASH</V>( <V>node</V><sub>h−1, 2j</sub>, <V>node</V><sub>h−1, 2j+1</sub>, <V>SEED</V>, <V>ADRS</V> )
        </span>
        <span className="ln">
          <V>RAND_HASH</V>(<V>L</V>, <V>R</V>) = <V>H</V>( <V>KEY</V>, (<V>L</V> ⊕ <V>BM</V><sub>0</sub>) ‖ (<V>R</V> ⊕ <V>BM</V><sub>1</sub>) )
        </span>
        <span className="ln">
          <V>node</V><sub>0, j</sub> = <V>L-tree</V>( <V>pk</V><sub>WOTS+, j</sub> ) &nbsp;&nbsp; <V>root</V> = <V>node</V><sub>10, 0</sub>
        </span>
        <span className="ln sm">XMSS-SHA2_10_256: height 10, 2<sup>10</sup> = 1,024 one-time keys, n = 32 bytes</span>
      </>
    ),
    source: 'RFC 8391 §4.1.4, Randomized Tree Hashing',
    href: 'https://www.rfc-editor.org/rfc/rfc8391#section-4.1.4',
  },
  slh: {
    label: 'SLH-DSA',
    title: 'SLH-DSA (stateless hash-based signatures)',
    body: (
      <>
        <span className="ln">
          <V>PK</V> = ( <V>PK.seed</V>, <V>PK.root</V> )
        </span>
        <span className="ln">
          <V>SIG</V> = <V>R</V> ‖ <V>SIG</V><sub>FORS</sub> ‖ <V>SIG</V><sub>HT</sub>
        </span>
        <span className="ln sm">a FORS few-time signature on the message digest, certified by a hypertree of XMSS layers; no leaf state to track</span>
      </>
    ),
    source: 'NIST FIPS 205, Stateless Hash-Based Digital Signature Standard',
    href: 'https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf',
  },
  eth: {
    label: 'address',
    title: 'Ethereum account address',
    body: (
      <>
        <span className="ln">
          <V>address</V> = last 20 bytes of <V>Keccak-256</V>( <V>pk</V> )
        </span>
        <span className="ln sm">Solana keypair wallet: address = base58( Ed25519 <V>pk</V> ), 32 bytes</span>
      </>
    ),
    source: 'ethereum.org, Ethereum accounts',
    href: 'https://ethereum.org/en/developers/docs/accounts/',
  },
  merkle: {
    label: 'Merkle root',
    title: 'Version two: Merkle commitment to 1,024 secrets',
    body: (
      <>
        <span className="ln">
          <V>leaf</V><sub>j</sub> = <V>SHA-256</V>( "BUNKER-LEAF-V1" ‖ <V>j</V> ‖ <V>SHA-256</V>(<V>s</V><sub>j</sub>) )
        </span>
        <span className="ln">
          <V>node</V> = <V>SHA-256</V>( "BUNKER-NODE-V1" ‖ <V>left</V> ‖ <V>right</V> )
        </span>
        <span className="ln sm">withdraw: reveal <V>s</V><sub>j</sub> plus 10 sibling hashes (320 bytes); the program recomputes the 32-byte root</span>
      </>
    ),
    source: 'solana-bunker program/src/lib.rs, MERKLE mode',
    href: 'https://github.com/chaintail/solana-bunker/blob/main/program/src/lib.rs',
  },
};
