import { cx } from '../../components/bits';
import type { SceneDef, SceneProps } from '../../types';
import { Bouncer, Devil, Form, FORM_AMOUNT, FORM_TO, Quill, VaultDoor } from './vaultscene';
import './c6.css';

/* slide 6: a secret is just a password; what we want is a SIGNATURE */
function Sig({ at }: SceneProps) {
  const sig = at('signature');
  return (
    <>
      <VaultDoor on={at('vault')} open={at('sign')} />

      <div className={cx('c6-t c6-okay', at('open') && !at('password') && 'on')}>Okay, this is where things</div>
      <div className="c6-math">the math</div>
      <div className={cx('c6-t c6-cool', at('math') && !at('password') && 'on')}>start to get cool</div>

      <div className={cx('c6-t c6-pw', at('password') && !sig && 'on')}>a secret is just a password</div>
      <div className={cx('c6-t c6-first', at('password') && !sig && 'on')}>whoever shows it first gets in</div>

      <div className={cx('c6-bouncer', at('vault') && 'on')}>
        <Bouncer />
      </div>
      <div className="c6-devil">
        <Devil />
      </div>
      <div className="vs-bubble c6-bubble">secret_2</div>

      <div className={cx('c6-sigw', sig && 'on', at('form') && 'up')}>SIGNATURE</div>
      <div className={cx('c6-t c6-exact', sig && !at('form') && 'on')}>this exact withdrawal, to this exact address, and nothing else</div>

      <Form to={FORM_TO} amount={FORM_AMOUNT} sig={5} sigColor="#0000ff" className={cx('c6-form', at('form') && 'on', at('sign') && 'signed')} />
      <div className="vs-quill c6-quill">
        <Quill />
      </div>
    </>
  );
}

export const C6: SceneDef = {
  key: 'c-sig',
  exhibit: '',
  title: '',
  cheap: true,
  steps: [{ id: 'open' }, { id: 'math' }, { id: 'password' }, { id: 'vault' }, { id: 'signature' }, { id: 'form' }, { id: 'sign' }],
  C: Sig,
};
