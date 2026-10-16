// Scene 11's end credits: Liam's final list, verbatim (film-brief-ending.md section C.3, main 4aef292; Liam 16352/16357).
// Initials only for surnames; Mikail without an H; "Claude-Do", never "Claude D.". The whole text lives here: a change to the list is one edit.
// roll: [heading, lines] where a line is a name (string) or [sub-role, name] (CAST, VOICE ACTORS); {joke: text} is a free line.
// cards: the full-screen cards after the roll (plan section 5, Q12); the last one carries the lemur logo, holds 3 s, then fades to black.
window.S11_CREDITS = {
  roll: [
    ['EXECUTIVE PRODUCERS', ['Liam C.', 'Claude-Do']],
    ['STORY INSPIRATION', ['Justin Drake']],
    ['CAST', [['NEWS ANCHOR', 'Liam C.'], ['SCIENTIST', 'Liam C.'], ['AVERAGE JOE', 'Liam C.'], ['BUNKER ENGINEER', 'Liam C.'], ['THE SUIT', 'Liam C.'], ['BANDIT DEVIL', 'Liam C.']]],
    ['VOICE ACTORS', [['THE ANNOUNCER', 'Enceladus (Google Chirp 3 HD)'], ['SPONSOR READ', 'Studio C (Google, en-GB)']]],
    ['WRITTEN BY', ['Liam C.']],
    ['DIRECTED BY', ['Claude-Do']],
    ['RESEARCH & DEVELOPMENT', ['Liam C.', 'Mikail R.', 'ChatGPT', 'Codex']],
    ['STORYBOARD', ['Claude Fable', 'Liam C.']],
    ['ART DIRECTION', ['Claude Fable', 'Liam C.']],
    ['SET DESIGN', ['Claude Fable', 'Claude Opus']],
    ['ANIMATION', ['Claude Opus']],
    ['COSTUME DESIGN', ['Codex GPT-6.1']],
    ['MATTE & COMPOSITING', ['ffmpeg', 'Chrome headless']],
    ['TRANSCRIPTION', ['NVIDIA Parakeet']],
    ['SOUND EFFECTS', ['freesound.org contributors (CC0)', 'Kenney']],
    ['LOCATION', ['WorldOS v2', 'do-box', 'Solana devnet']],
    ['ANIMATION STUDIO', ['dev-mac']],
    ['HOSTING & CATERING', ['GitHub']],
    ['ARCHIVAL SOURCES', ['Physical Review, 1920 to 1947', '9,923 records checked']],
    ['STUNTS', ['Bunker Program HssAePJf…NK6V, Solana devnet', 'Every transaction in this film is real and open in the explorer.']],
    ['SPECIAL THANKS', ['Leslie Lamport', 'Robert Winternitz', 'Ralph Merkle', 'NIST']],
    { joke: 'No curves were harmed in the making of this film.' },
    { joke: 'No meme coins were harmed either. Yet.' },
  ],
  cards: [
    { lines: ['Based on a true story.', 'Events were dramatized.', 'Characters and names may have been changed to protect the identity of victims.',
              'Any resemblance to actual elliptic curves, living or broken, is purely coincidental.'] },
    { product: 'PRODUCT OF', name: 'Chaintail Labs', logo: 'assets/chaintail-logo-white.svg', copy: '© 2026 Chaintail Labs' },
  ],
};
