import { Stamp } from '../components/bits';
import type { SceneDef, SceneProps } from '../types';
import './s0.css';

function Opener({ at, instant }: SceneProps) {
  return (
    <>
      <div className="op-warn">WARNING</div>
      <Stamp on={at('stamp')} instant={instant} x={968} y={600} size={176} r={-9} d={60} bold className="op-stamp">
        Contains math
      </Stamp>
    </>
  );
}

export const S0: SceneDef = {
  key: 'opener',
  exhibit: '',
  title: '',
  bare: true,
  steps: [{ id: 'blank' }, { id: 'warn' }, { id: 'stamp' }],
  C: Opener,
};
