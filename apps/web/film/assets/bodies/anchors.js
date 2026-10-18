// Character kit manifest (stand-in bodies). Each asset = <name>.png (body, transparent, 640x720) + <name>-front.png (collar layer, drawn over
// the bottom of the neck) + a head anchor. Crop box 640x720+320+0 of the export frame; figure centre x = 320 in the crop.
//   S      export scale (px per figure unit)      base  figure unit that sits on crop y = 700 (floor for full figures, hem for the physicist)
//   chin   figure unit where the chin goes        anchor = { x: 320, y: 700 - (base - chin) * S }  (px in the crop)
// Replacing a stand-in with a generated body = new PNG pair with the same crop box + new numbers here.
window.BODIES = {
  'physicist-point': { S: 1.6,  base: 476, chin: 156 },
  'joe-rest':        { S: 1.25, base: 618, chin: 160 },
  'joe-up':          { S: 1.25, base: 618, chin: 160 },
  'eng-walk1':       { S: 1.25, base: 618, chin: 164 },
  'eng-walk2':       { S: 1.25, base: 618, chin: 164 },
  'eng-point':       { S: 1.25, base: 618, chin: 164 },
};
for (const b of Object.values(window.BODIES)) b.anchor = { x: 320, y: 700 - (b.base - b.chin) * b.S };
