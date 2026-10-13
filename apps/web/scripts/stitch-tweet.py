"""Stitch the founder's tweet screenshots (docs/presentation/assets/tweet-*.jpg)
into one 900px-wide column for the pitch deck, cut the magnifier crops at full
resolution, and re-encode the phone thumbnail.
Run from apps/web: python3 scripts/stitch-tweet.py

The first reply (tweet-7.jpg) is a meme with two profane words; both are
pixelated in every output so they never reach the screen."""
from PIL import Image, ImageOps

A = '../../docs/presentation/assets/'
W = 900
# tweet-7.jpg source pixels: "fuck" (line 1) and "fucking" (line 4) of the meme text
CENSOR = {'7': [(976, 1230, 1066, 1280), (866, 1412, 1006, 1462)]}


def load(n):
    im = Image.open(f'{A}tweet-{n}.jpg').convert('RGB')
    for box in CENSOR.get(n, []):
        reg = im.crop(box)
        small = reg.resize((max(1, reg.width // 15), max(1, reg.height // 15)), Image.BILINEAR)
        im.paste(small.resize(reg.size, Image.NEAREST), box[:2])
    return im


src = {n: load(n) for n in ['1-top', '2', '3', '4', '5', '6', '7']}
parts = [im.resize((W, round(im.height * W / im.width)), Image.LANCZOS) for im in src.values()]
out = Image.new('RGB', (W, sum(p.height for p in parts)))
y = 0
for p in parts:
    out.paste(p, (0, y))
    y += p.height
out.save('src/assets/drake-tweet-stitched.jpg', quality=62, optimize=True, progressive=True)

# magnifier crops, full resolution. The two text crops are inverted to light
# mode so a yellow highlighter can sit under the words (multiply blend).
ImageOps.invert(src['1-top'].crop((0, 230, 1290, 1160))).save('src/assets/tweet-lens-1.jpg', quality=82, optimize=True)
src['7'].crop((0, 1030, 1290, 1720)).save('src/assets/tweet-lens-7.jpg', quality=80, optimize=True)

Image.open(f'{A}bankless-thumb-phone-screenshot.png').convert('RGB').save('src/assets/bankless-thumb-phone.jpg', quality=80)
print(out.size)
