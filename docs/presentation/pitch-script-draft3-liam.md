# Solana Bunker — pitch script draft 3 (Liam's edit, slides 1–4, received 2026-10-13 10:41 ICT)

Liam's own words for beats 1–3 with his screen directions (lines starting with `>`). Beats 4–9 still on draft 2 until he sends them.

Design intent (Liam): juxtapose high-quality motion graphics and deliberately low-quality slides, sometimes on the same slide.

## Beat 1, opening

### SLIDE 1
Who's excited for some mathematics?
... Nobody?
No, wait, don't close the tab!
I swear this gets good!

### SLIDE 2
Last week, this lead Ethereum Foundation researcher put out a massive post
And it sent crypto Twitter into a spiral!

> we show yt thumbnail and point to Justin and show his name. Also show text box comment about me loving the debate. I will not talk about it though.

He said get ready for bunker mode!

> we show the top of tweet, magnify the start and highlight bunker mode sentence.

Just in case AI breaks public/private key cryptography before quantum computers

His advice?
Move your funds to a fresh address,
One that has never sent a transaction,

> scroll tweet, magnify and highlight fresh address part

Long story short… that works on Ethereum, because an Ethereum address is a hash of your public key. The public key stays hidden until you sign something.

But this doesn't work on Solana,
Here a wallet address *is* your public key.

> scroll tweet to bottom and magnify first comment

So… are we screwed??
Do we sell it all for Gold?

Not so fast. Nothing is broken.
And maybe it never will (well, until quantum)

> NOTHING IS BROKEN
> This is all [conspiracy] theoretical

## Beat 2, the conspiracy

But here is where the conspiracy starts.

### SLIDE 3

> we show the original high quality graphic on the *right* side of screen

Last month OpenAI dropped over 700 math papers
This turned the field on its head overnight.
The drop was massive, covering seventeen disciplines.
But one area was suspiciously missing… Cryptography.

> highlight missing cryptography area, like the second low quality version

Maybe that is because the math is sound.
But the conspiracy minded were quick to point out that the US government may be leaning on OpenAI to hold back the dangerous paper.

And there is precedence for this. At least this is what CT was repeating.

> start animating in the timeline empty graph. First the axes, then the dates.
> then fill up each year one at a time with a bar made of what look like cover pages to a white paper
> equal time for each year.
> for the empty years, shake the x-axis date as we skip over it

During the Second World War,
as the Manhattan Project got going,
physicists mysteriously stopped publishing papers on atomic physics.

> show text "Doveryai, no proveryai"
> - russian proverb
> beside is Translation: "trust, but verify"

This was repeated all over twitter.
But rather than trust a bro, we checked.

> add \/ to indicate insert text into trust but [have agents] verify
> grow large text 92XX (whatever number papers) checked 1939-1946 (or whatever years)
> then grow large text 719 paper 2026

The silence is real.

We will let you draw your own conclusions.

## Beat 3, we made a Solana Bunker

### SLIDE 4

We love a good conspiracy theory
But we also love nerding out on math

Whether or not anyone is hiding anything,
there is a cool research question under all of this.

And thus began a fascinating side quest: can we create a Solana Bunker

> now we show our high quality vault. Left half of slide is parchment bg and vault, right side stay white

As solana dev, you often hear the term "off curve address".
Oh yes, a PDA!

> we show PDA in large and program derived address in smaller text below on right side of screen.

But do you every really stop to think about what that is?

So we turn to the Artifi- er, Super Intelligence

> show pic of trump and AI leaders from recent meeting where signed executive order to rename AI to SI. add text saying executive order XXXX renames Artificial intelligence to Super Intelligence [date]

that same AI, no, SI
that might put all our meme coins at risk
To chat about ideas for using a PDA as a vault

A Solana Bunker, immune to any future weakness in Ed25519.

And after a few million tokens and several hours of voice notes…
We built it.
Actually, we built it three times,
each version better than the last.

## Beat 4, version one

### SLIDE 5

Back to Justin's tweet. The first idea was let's use a Hash.

> bring back tweet in same position left side of screen. Magnify some section or maybe multiple sections and just highlight the word hash wherever that appears.

Justin is super smart,
if he likes a hash we like a hash

And hashing is super simple!
> can we show code snippet or sys prog call instruction or whatever is used to do sha256 on solana?

> draw stick figure on top left side of screen.
> draw large rectangle on right side of screen with title Bunker Program 001
> have come circles with solana logo fly from stick man into program

So the idea. Create a bunch of one-time secrets

> draw out vertical list of secret_1, secret_2…. Secret_1000
> down left side of screen
> draw out 1000 squares in grid. Bunker Program 001 taking up right half of screen.

hash each of them, and store the hashes in the vault.

> animate the secrets moving cascading, start slower and speed up
> they fly through black MATH hash box and then out other side each into one for the squares
> leave the list on left side of screen still, but all the text is dimmed.

To spend, you reveal one of the secrets.
> highlight a secret. Move it to the stick man, move it to the program square, cross it out, have SOL token move back to the stick man.

If it matches, the vault lets you in and crosses that one off.

Pretty simple, eh?
Sure, keeping track of a thousand one time passwords is annoying
But the real pain in the a– … wallet is storing them all on chain

> show RENT:
> 33,000 bytes -> XXX SOL!

and that is why we built version two.

## Beat 5, version two, robbed

### SLIDE 5 continues

So we go to the standard whenever you want to compress data on chain
A merkle tree!

> slash the title Bunker Program ~001~ 002

Same thousand secrets, but now we commit them as a single Merkle root.

> all the squares fly around wildly for a second group together then line up (we don't need to keep all 1000 add … along leaves row at bottom)
> and show tree grow above.
> then dim the tree and highlight the root node.

Thirty three thousand bytes of storage
becomes three hundred ninety.

> large 33,000
> ticks down to 390
> slash the XXX SOL and show new rent

And it's time to celebrate. Our funds are safe in the Bunker.
Let's spend some…

> oh i guess we should have an RPC on the slide somewhere.
> highlight another secret. secret_x moves to user, wraps in box with TX on it.
> TX box moves to RPC (same as previous withdraw)
> TX box slowly moves out of RPC towards the Program
> then a red stick figure head peak up from bottom of screen with devil horns
> a Red TX box fly up with swooping motion. This red TX box also have devil horns
> swoop past our slow moving black TX and pass it and enter Program box first.
> pass through hash box, move to a leaf node and cross it out… or maybe we show bit map representation on far right hand side inside program box, don't need to talk about it here. Can have text box (this doesn't need to be tiny screen readable) describing the used nonce tracking

oh crap. What the flip happened there?
We got robbed!

Here is the THEORETICAL problem.

It is unlikely, especially with the crazy fast block times on solana,
but if an attacker can see our transaction before it lands,

> large text in middle of screen for a second
> and has already broken Ed25519 (literally I want the * in the text we show)

they copy our secret,
swap the destination,
pay a bigger fee,
and beat our transaction!

A timing attack!

And it all worked as coded.
The vault does not know the difference.

## Beat 6, a signature made of hashes

### SLIDE 6

Okay,
this is where things

> flash "*the math*" for 500ms

start to get cool

The problem with versions one and two is that a secret is just a password.

Whoever shows the password first gets into the vault

But PASSWORD says nothing about where money should go. So if someone steals it on the way to the vault they can get in first!

> show our high quality vault on right side of screen with bouncer outside
> devil bandit whispers secret and gets let in. or maybe we use a tavern door with sliding slot?

What we actually want is a SIGNATURE.

> bouncer fly off screen

Something that says: this exact withdrawal, to this exact address, and nothing else.

> show a paper form with field maybe
> fill in to: $xxxx amount: $xxxx
> then quill signs paper. Paper gets handed through the door and it opens.

### SLIDE 7

And lucky for us, it turns out you can build a signature out of nothing but hash functions.
> show tweet again and highlight a part about hash-based signatures

No curves at all.

Shout out to Leslie Lamport who figured this out in 1979.
Yes, that Lamport, the namesake for the smallest unit of Solana.

Unfortunately Lamport signatures are massive
> some animation to represent them
> then show their size in bytes

But Winternitz made these smaller,
with hash chains.
> morph the lamport representation into chains

Merkle put thousands of those one time keys into a tree.

That whole thing is called XMSS,
it is a NIST standard,
and it is what we built for version three.

> show NIST logo

So now when the attacker copies our transaction and swaps the destination, the signature does not match anymore, and the program throws it out.

> back to slide 6 visuals, devil bandit tries to sign similar form but his signature is different. Door slit slams shut? Or maybe we have a bouncer?

## Beat 7, one transaction, and re-keying

XMSS signatures seem awesome. They are way smaller…

> show Lamport and byte size large number
> then fade out Lamport replace with XMSS
> number tick down to 2,750 bytes

But… damn that 1,232 byte transaction size limit!

> Then show in large 2,750 > 1,232

Sigh… i guess we could use temporary data accounts to upload signatures in pieces, but from our research that took 5 transactions just to do a simple withdrawal!

> show Bunker Program 003-a
> show proof boxes

That's not cool…

> large text Solana Transactions V1 to the rescue!
> flash a brand new label above this
> then have the 1,232 number tick up to 4096
> the > sign grows and rotates and shrinks back to be flipped <

So we rebuilt it.

> Bunker Program 003-a throw away the -a, fly in -b. The -b grows and settles in
> old proof boxes grow and shrink to disappear one after another.
> new proof boxes pop into their places

One transaction,
thirty one hundred bytes,
about half a million compute units,
and the full signature verifies on chain in a single shot.

> then show a table of all the different transactions we built for rotation, mock usdc etc.

> turn this into a text box on screen: And because every one time key gets used exactly once, the vault keeps a bitmap of which leaves are spent. When you run low, or you just get paranoid, you sign one more message that installs a brand new tree. New root, new keys, same address, same balance. The new tree comes from the same twelve word seed phrase, just the next generation. So recovery is one instruction: rotate.

---

## Fact fills (composer, verified)

- Executive order: **Executive Order 14365, "Inaugurating The Era of Super Intelligence", signed 2026-09-29**, directs agencies to use "Super Intelligence"/"SI" for "artificial intelligence"/"AI" in non-statutory documents. Same day as the tech-CEO White House meeting. Sources: White House fact sheet, CNBC, Forbes.
- Physical Review records checked: **9,923 records, 1920 to 1947**. Fission-title papers: 54 in 1939–41, **0 in 1942–44** (0 of 543). Plutonium paper received 1941, published 1946 (Phys. Rev. 70, 555).
- OpenAI drop: **719 manuscripts, 17 disciplines, 0 explicitly cryptographic** (strict count).
- Timeline bars (fission in the title, Physical Review, per year): 1936 0, 1937 0, 1938 0, 1939 17, 1940 22, 1941 17, 1942 0, 1943 0, 1944 0, 1945 2, 1946 6, 1947 18. Source: docs/research-story/visualizations.json, chart `historical_publication_trend`, subject `fission_title`.
- Design rule (Liam, 15589): 90% of the information on every step must be understandable at 426x240.
- Slide 5 rent: array state at 1,024 leaves is 33,126 bytes; measured setup rent **234,433,680 lamports = 0.234 SOL** over 38 transactions. Merkle version: 6,591,120 lamports = 0.0066 SOL over 2 transactions (research/results-summary.md). The SHA-256 call in the program is the `hashv` syscall from `solana_program::hash` (program/src/lib.rs line 108).
- "See the code" box (Liam, 15606): each time a new program version appears, top right: QR with GitHub logo to the mode's line in program/src/lib.rs (001 array line 113, 002 Merkle line 114, 003 XMSS line 118, links on branch main) plus a Solscan QR for the devnet program HssAePJfZrERFjEAhm89nY9Tc9BWAobxp2GqGhefNK6V.
- "Proof it works" box (Liam, 15607): under the see-the-code box, Solscan QR to the confirmed devnet SOL withdrawal for that version: 001 `5mHxtbGL…`, 002 `5XPHXjBK…`, 003 `CiZmcGsa…` (full signatures in artifacts/public-deployment.json).
- Slides 6–7 facts: Lamport signature for a 256-bit digest with SHA-256 = 256 revealed 32-byte secrets = **8,192 bytes** (public key 16,384 bytes). XMSS-SHA2_10_256 signature = **2,500 bytes** (not 2,750). Legacy transaction cap **1,232 bytes**; v1 cap **4,096**. Staged transport = **5 transactions** (stage create, three uploads, execute), measured on the local SVM only, no devnet proof transactions exist for it. Inline v1 SOL withdraw: **3,117 bytes, 518,509 CU**. Tweet lines mentioning hash-based schemes: lines 21, 23, 25 of drake-tweet.txt (SPHINCS; "go all-in on hash-based cryptography"; roadmap).
