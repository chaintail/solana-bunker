#!/usr/bin/env python3
"""Bakes the scene 6/5 devil: heads/s06-devil.png (red closed-mouth head, 152x220) + horns on the crown + domino mask lowered over the eyes
-> heads/s06-devil-v2.png, 200x260 canvas, head at offset (12,40). Run from apps/web/film. (v1 had the horns/mask as SVG in the page, mask sat above the eyes.)"""
import subprocess, os, sys
svg = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="260" viewBox="0 0 200 260"><g transform="translate(12 40)">
<image xlink:href="%s" x="0" y="0" width="152" height="220"/>
<path transform="translate(0 7)" d="M26,26 Q8,-4 10,-34 Q40,-10 52,12 Z" fill="#d00000" stroke="#000" stroke-width="5" stroke-linejoin="round"/>
<path transform="translate(0 7)" d="M110,26 Q128,-4 126,-34 Q96,-10 84,12 Z" fill="#d00000" stroke="#000" stroke-width="5" stroke-linejoin="round"/>
<path fill-rule="evenodd" fill="#050505" d="M-2,76 Q66,66 134,76 L134,102 Q66,112 -2,102 Z M24,89 a15,9 0 1,0 30,0 a15,9 0 1,0 -30,0 Z M67,89 a15,9 0 1,0 30,0 a15,9 0 1,0 -30,0 Z"/>
<path d="M134,82 Q148,78 158,86 M134,94 Q148,100 156,108" stroke="#050505" stroke-width="6" fill="none" stroke-linecap="round"/>
</g></svg>''' % 's06-devil.png'
open('heads/_devil-v2.svg','w').write(svg)
subprocess.run(['rsvg-convert','-o','heads/s06-devil-v2.png','heads/_devil-v2.svg'],check=True); os.remove('heads/_devil-v2.svg')
