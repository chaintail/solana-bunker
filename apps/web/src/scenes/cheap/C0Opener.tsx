import { CStamp } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import './c0.css';

function Opener({ at }: SceneProps) {
  return (
    <>
      <div className="c0-warn">WARNING</div>
      <CStamp on={at('stamp')} x={960} y={690} size={124} r={-1.5} d={40}>
        CONTAINS MATH
      </CStamp>
    </>
  );
}

export const C0: SceneDef = {
  key: 'c-opener',
  exhibit: '',
  title: '',
  bare: true,
  cheap: true,
  steps: [{ id: 'blank' }, { id: 'warn' }, { id: 'stamp' }],
  C: Opener,
};
