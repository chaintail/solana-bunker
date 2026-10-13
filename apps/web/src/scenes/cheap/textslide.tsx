/* plain big-text slide: one spoken line per step (stand-in until the full slide is built) */
import { cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import './textslide.css';

export function textSlide(key: string, lines: string[]): SceneDef {
  const ids = lines.map((_, i) => `l${i}`);
  function Text({ at, cur }: SceneProps) {
    const k = ids.indexOf(cur);
    return (
      <>
        {lines.map((l, i) => (
          <div key={i} className={cx('ts-line', at(ids[i]) && i === k && 'on', at(ids[i]) && i === k - 1 && 'prev')}>
            {l}
          </div>
        ))}
      </>
    );
  }
  return { key, exhibit: '', title: '', cheap: true, steps: ids.map((id) => ({ id })), C: Text };
}
