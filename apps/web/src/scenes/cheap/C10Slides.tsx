import { textSlide } from './textslide';

/* slides 8, 9 and 10 as spoken lines (draft 3); full slides replace these one by one */
export const C8Seed = textSlide('c-seed', [
  'Ok but there’s still one really annoying part…',
  'how are we supposed to keep track of our 1000 one-time use secrets?',
  'If only there was a convenient way to derive secret keys from something memorable…',
  'BIP-39',
  'yeah, we did that too! check it out!',
]);
export const C9Devnet = textSlide('c-devnet2', [
  'This is not a bunch of diagrams.',
  'All of it is live on devnet right now.',
  'Three vaults, SOL and USDC, the robbery, the rejection, the rotation.',
  'Every number on this screen is a transaction you can open in the explorer.',
]);
export const C10End = textSlide('c-end', [
  'Thanks for sticking around.',
  'If you made it this far,',
  'And you didn’t fall asleep',
  'You must be a real CRYPTOgraphy NERD',
  'Nerd like us!',
  'I told you the math would be worth it.',
  'There is a lot more in the whitepaper. Go check it out.',
  'Next steps: a stateless version with SLH-DSA',
  'bigger signatures, no spent-key tracking',
  'the bunker protects the bunker',
  'Lots more to cook up in the Lab.',
]);
