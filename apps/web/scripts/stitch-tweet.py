"""Stitch the founder's tweet screenshots (docs/presentation/assets/tweet-*.jpg)
into one 900px-wide column for the pitch deck, and re-encode the phone
thumbnail. Run from apps/web: python3 scripts/stitch-tweet.py"""
from PIL import Image

A = '../../docs/presentation/assets/'
W = 900
parts = []
for n in ['1-top', '2', '3', '4', '5', '6', '7']:
    im = Image.open(f'{A}tweet-{n}.jpg').convert('RGB')
    parts.append(im.resize((W, round(im.height * W / im.width)), Image.LANCZOS))
out = Image.new('RGB', (W, sum(p.height for p in parts)))
y = 0
for p in parts:
    out.paste(p, (0, y))
    y += p.height
out.save('src/assets/drake-tweet-stitched.jpg', quality=62, optimize=True, progressive=True)
Image.open(f'{A}bankless-thumb-phone-screenshot.png').convert('RGB').save('src/assets/bankless-thumb-phone.jpg', quality=80)
print(out.size)
