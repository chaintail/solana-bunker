# contact-sheet.py out.png cols w h file[:label] ...  (opening v9: stills and the ident compare sheet)
import sys
from PIL import Image, ImageDraw, ImageFont
out, cols, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); fs = sys.argv[5:]
rows = (len(fs) + cols - 1) // cols; sheet = Image.new('RGB', (cols * w, rows * (h + 28)), (40, 40, 40)); d = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 20)
except Exception: font = None
for i, f in enumerate(fs):
    p, _, lab = f.partition(':'); im = Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS)
    x, y = (i % cols) * w, (i // cols) * (h + 28); sheet.paste(im, (x, y + 28)); d.text((x + 6, y + 4), lab or p.split('/')[-1], fill=(255, 255, 0), font=font)
sheet.save(out)
