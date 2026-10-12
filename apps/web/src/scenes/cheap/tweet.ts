import stitched from '../../assets/drake-tweet-stitched.jpg';

/*
 * The tweet shown on slide 2. `src` is one tall column (the founder's seven
 * phone screenshots stitched by scripts/stitch-tweet.py). Swapping in other
 * images only means changing this object: the step logic reads geometry from here.
 * All coordinates are in source pixels of tweet-1-top.jpg (1290 px wide).
 */
export const TWEET = {
  src: stitched,
  naturalWidth: 900,
  naturalHeight: 9714,
  sourceWidth: 1290,
  /** the lines of "controlled mass migration ... hidden behind a hash" */
  highlight: [
    [27, 512, 1145, 578],
    [27, 588, 1085, 654],
    [27, 663, 785, 730],
  ] as [number, number, number, number][],
  /** region the magnifier shows, x0 y0 x1 y1 */
  lens: [10, 420, 1190, 745] as [number, number, number, number],
};
