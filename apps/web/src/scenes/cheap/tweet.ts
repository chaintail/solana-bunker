import stitched from '../../assets/drake-tweet-stitched.jpg';
import lens1 from '../../assets/tweet-lens-1.jpg';
import lens7 from '../../assets/tweet-lens-7.jpg';

/*
 * The tweet shown on slide 2, built by scripts/stitch-tweet.py from the
 * founder's seven phone screenshots. `column` is one tall 900 px column; the
 * lens images are full-resolution crops. Geometry is in source pixels of the
 * screenshot named in each entry (all 1290 px wide), so swapping images only
 * means changing this file.
 */
export const TWEET = {
  column: { src: stitched, w: 900, h: 9714 },
  sourceWidth: 1290,
  /** where tweet-7.jpg starts inside the column, in column (900 px) pixels */
  replyTop: 8453,
  /** tweet-1-top.jpg crop [0,230,1290,1160], inverted to light mode */
  lens1: { src: lens1, origin: [0, 230] as [number, number], w: 1290, h: 930 },
  /** tweet-7.jpg crop [0,1030,1290,1720], profanity pixelated */
  lens7: { src: lens7, origin: [0, 1030] as [number, number], w: 1290, h: 690 },
  /** first paragraph; highlight the "bunker mode" sentence */
  bunker: {
    region: [10, 262, 1180, 738] as [number, number, number, number],
    lines: [
      [27, 1135, 308],
      [27, 1062, 386],
    ] as [number, number, number][],
  },
  /** "fresh addresses" ... "addresses that have never signed a transaction" */
  fresh: {
    region: [10, 500, 1180, 1118] as [number, number, number, number],
    lines: [
      [1040, 1142, 542],
      [27, 266, 617],
      [27, 1145, 1004],
      [27, 333, 1079],
    ] as [number, number, number][],
  },
  /** the first reply: header and the meme */
  reply: { region: [0, 1040, 1290, 1712] as [number, number, number, number] },
};
