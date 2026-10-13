import stitched from '../../assets/drake-tweet-stitched.jpg';
import lens1 from '../../assets/tweet-lens-1.jpg';
import lens7 from '../../assets/tweet-lens-7.jpg';
import lens5 from '../../assets/tweet-lens-5.jpg';
import lens6 from '../../assets/tweet-lens-6.jpg';

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
    region: [10, 500, 1230, 1118] as [number, number, number, number],
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

/** where each screenshot starts in the column (column px) and its source -> column scale */
export const PARTS: Record<string, { top: number; k: number }> = {
  '1-top': { top: 0, k: 900 / 1290 },
  '2': { top: 1372, k: 900 / 1290 },
  '3': { top: 2740, k: 900 / 1290 },
  '4': { top: 4362, k: 900 / 1290 },
  '5': { top: 5749, k: 900 / 979 },
  '6': { top: 6926, k: 900 / 1290 },
  '7': { top: 8453, k: 900 / 1290 },
};

/** every "hash" in the post (drake-tweet.txt), as [part, x0, x1, line centre y] in that screenshot's pixels */
export const HASH_WORDS: [string, number, number, number][] = [
  ['1-top', 640, 760, 695],
  ['3', 640, 760, 984],
  ['5', 666, 800, 247],
  ['6', 980, 1105, 1292],
  ['6', 30, 155, 1678],
  ['6', 390, 515, 1910],
  ['7', 290, 410, 156],
];

/** the three spots the magnifier visits on slide 5 */
export const HASH_TOUR = [
  { part: '1-top', img: { src: lens1, origin: [0, 230] as [number, number], w: 1290, h: 930 }, region: [10, 500, 1230, 740] as [number, number, number, number] },
  { part: '5', img: { src: lens5, origin: [0, 0] as [number, number], w: 979, h: 340 }, region: [0, 20, 979, 330] as [number, number, number, number] },
  { part: '6', img: { src: lens6, origin: [0, 1230] as [number, number], w: 1290, h: 740 }, region: [10, 1250, 1290, 1950] as [number, number, number, number] },
];
