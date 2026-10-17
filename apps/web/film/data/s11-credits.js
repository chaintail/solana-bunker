// Scene 11's end credits: Liam's final list, verbatim (film-brief-ending.md section C.3, main 4aef292; Liam 16352/16357).
// v7 (2026-10-16): MUSIC, ARCADE SCORE and NEWS STINGS after AUDIO ENGINEERS; SOUND EFFECTS as one line; the Lamport portrait line opens the closing lines.
// Initials only for surnames; Mikail without an H; "Claude-Do", never "Claude D.". The whole text lives here: a change to the list is one edit.
// a line may hold \n (a break) or be {it: text} (lighter weight, italic).
// {sp: text}: a line with a small gap above it (v8: the NEWS STINGS credits, which wrap onto two lines each, read as separate credits).
// roll: [heading, lines] where a line is a name (string) or [sub-role, name] (CAST, VOICE ACTORS); {joke: text} is a free line.
// cards: the full-screen cards after the roll (plan section 5, Q12); the last one carries the lemur logo, holds 3 s, then fades to black.
window.S11_CREDITS = {
  roll: [
    ['EXECUTIVE PRODUCERS', ['Liam C.', 'Claude-Do']],
    ['STORY INSPIRATION', ['Justin Drake']],
    ['CAST', [['NEWS ANCHOR', 'Liam C.'], ['SCIENTIST', 'Liam C.'], ['AVERAGE JOE', 'Liam C.'], ['BUNKER ENGINEER', 'Liam C.'], ['THE SUIT', 'Liam C.'], ['BANDIT DEVIL', 'Liam C.']]],
    ['VOICE ACTORS', [['THE ANNOUNCER', 'Enceladus\n(Google Chirp 3 HD)'], ['SPONSOR READ', 'Studio C\n(Google, en-GB)']]],
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
    ['AUDIO ENGINEERS', ['Codex', 'Claude Fable', 'Grok']],
    ['MUSIC', ['Suno, prompts by Liam C.']],
    ['ARCADE SCORE', ['Original 8-bit score, Chaintail Labs']],
    ['NEWS STINGS', ['Freesound.org (CC0)', {sp: 'code_box: Mini News Jingle'}, {sp: 'xkeril: Minimalist news transition'}, {sp: 'Antwash: Da Da Da Daaa Opening'}]],
    ['SOUND EFFECTS', ['Freesound.org and Kenney.nl (CC0)']],
    ['LOCATION', ['WorldOS v2', 'do-box', 'Solana devnet']],
    ['ANIMATION STUDIO', ['dev-mac']],
    ['ASSOCIATE PRODUCER', ['Grok']],
    ['HOSTING & CATERING', ['GitHub']],
    ['ARCHIVAL SOURCES', ['Physical Review, 1920 to 1947', '9,923 records checked']],
    ['STUNTS', ['Bunker Program HssAePJf…NK6V, Solana devnet', {it: 'Every transaction in this film is real and open in the explorer.'}]],
    ['SPECIAL THANKS', ['Leslie Lamport', 'Robert Winternitz', 'Ralph Merkle', 'NIST']],
    { joke: 'Leslie Lamport portrait: photo by Leslie Lamport, via Wikimedia Commons' },
    { joke: 'No curves were harmed in the making of this film.' },
    { joke: 'No meme coins were harmed either. Yet.' },
  ],
  cards: [
    { lines: ['Based on a true story.', 'Events were dramatized.', 'Characters and names may have been changed to protect the identity of victims.',
              'Any resemblance to actual elliptic curves, living or broken, is purely coincidental.'] },
    { product: 'PRODUCT OF', name: 'Chaintail Labs', logo: 'assets/chaintail-logo-white.svg', copy: '© 2026 Chaintail Labs' },
  ],
};
