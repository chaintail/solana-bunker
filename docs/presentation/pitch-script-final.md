# Solana Bunker, pitch script (Liam's draft 3, cleaned, spoken words only)

## Slide 1, title

Who's excited for some mathematics? ... Nobody? No, wait, don't close the tab! I swear this gets good!

## Slide 2, the tweet

Last week, this lead Ethereum Foundation researcher put out a massive post, and it sent crypto Twitter into a spiral!

He said get ready for bunker mode! Just in case AI breaks public key cryptography before quantum computers do.

His advice? Move your funds to a fresh address, one that has never sent a transaction.

Long story short, that works on Ethereum, because an Ethereum address is a hash of your public key. The public key stays hidden until you sign something.

But this doesn't work on Solana. Here a wallet address is your public key.

So, are we screwed? Do we sell it all for gold?

Not so fast. Nothing is broken. And maybe it never will be. Well, until quantum.

## Slide 3, the conspiracy

But here is where the conspiracy starts.

Last month OpenAI dropped over seven hundred math papers. This turned the field on its head overnight. The drop was massive, covering seventeen disciplines. But one area was suspiciously missing. Cryptography.

Maybe that is because the math is sound. But the conspiracy minded were quick to point out that the US government may be leaning on OpenAI to hold back the dangerous papers.

And there is precedent for this. At least, this is what crypto Twitter was repeating.

During the Second World War, as the Manhattan Project got going, physicists mysteriously stopped publishing papers on atomic physics.

This was repeated all over Twitter. But rather than trust a bro, we checked. Nine thousand nine hundred twenty three journal records from 1920 to 1947. Seven hundred nineteen papers from 2026.

The silence is real.

We will let you draw your own conclusions.

## Slide 4, we made a Solana Bunker

We love a good conspiracy theory. But we also love nerding out on math.

Whether or not anyone is hiding anything, there is a cool research question under all of this.

And thus began a fascinating side quest: can we create a Solana Bunker?

As a Solana dev, you often hear the term "off curve address". Oh yes, a PDA! But do you ever really stop to think about what that is?

So we turned to the Artifi... er, Super Intelligence. That same AI, no, SI, that might put all our meme coins at risk. To chat about ideas for using a PDA as a vault.

A Solana Bunker, immune to any future weakness in Ed25519.

And after a few million tokens and several hours of voice notes, we built it. Actually, we built it three times, each version better than the last.

## Slide 5, version one, version two, robbed

Back to Justin's tweet. The first idea was: let's use a hash. Justin is super smart. If he likes a hash, we like a hash.

And hashing is super simple!

So the idea. Create a bunch of one-time secrets, hash each of them, and store the hashes in the vault.

To spend, you reveal one of the secrets. If it matches, the vault lets you in and crosses that one off.

Pretty simple, eh? Sure, keeping track of a thousand one-time passwords is annoying. But the real pain in the a... wallet is storing them all on chain. Thirty three thousand bytes. A quarter of a SOL in rent.

And that is why we built version two.

So we go to the standard whenever you want to compress data on chain. A Merkle tree!

Same thousand secrets, but now we commit them as a single Merkle root. Thirty three thousand bytes of storage becomes three hundred ninety.

And it's time to celebrate. Our funds are safe in the Bunker. Let's spend some...

Oh crap. What the flip happened there? We got robbed!

Here is the theoretical problem. It is unlikely, especially with the crazy fast block times on Solana. But if an attacker can see our transaction before it lands, and has already broken Ed25519, they copy our secret, swap the destination, pay a bigger fee, and beat our transaction!

A timing attack!

And it all worked as coded. The vault does not know the difference.

## Slide 6, a signature

Okay, this is where things start to get cool.

The problem with versions one and two is that a secret is just a password. Whoever shows the password first gets into the vault.

But a password says nothing about where the money should go. So if someone steals it on the way to the vault, they can get in first!

What we actually want is a signature. Something that says: this exact withdrawal, to this exact address, and nothing else.

## Slide 7, a signature made of hashes, and one transaction

And lucky for us, it turns out you can build a signature out of nothing but hash functions. No curves at all.

Shout out to Leslie Lamport, who figured this out in 1979. Yes, that Lamport, the namesake for the smallest unit of Solana.

Unfortunately, Lamport signatures are massive. Eight kilobytes each.

But Winternitz made these smaller, with hash chains. Merkle put thousands of those one-time keys into a tree.

That whole thing is called XMSS. It is a NIST standard, and it is what we built for version three.

So now when the attacker copies our transaction and swaps the destination, the signature does not match anymore, and the program throws it out.

XMSS signatures seem awesome. They are way smaller. Twenty five hundred bytes.

But... damn that twelve hundred thirty two byte transaction size limit!

Sigh. I guess we could use temporary data accounts to upload signatures in pieces. But from our research, that took five transactions just to do a simple withdrawal! That's not cool.

Solana transactions version one to the rescue! Four thousand ninety six bytes.

So we rebuilt it. One transaction, thirty one hundred bytes, about half a million compute units, and the full signature verifies on chain in a single shot.

## Slide 8, the seed phrase

Ok, but there's still one really annoying part. How are we supposed to keep track of our thousand one-time secrets?

If only there was a convenient way to derive secret keys from something memorable. Rather than memorizing thousands of strings of gibberish, what if... BIP-39.

Yeah, we did that too! Check it out.

## Slide 9, live on devnet

This is not a bunch of diagrams. All of it is live on devnet right now. Three vaults, SOL and USDC, the robbery, the rejection, the rotation. Every number on this screen is a transaction you can open in the explorer.

## Slide 10, close

Thanks for sticking around. If you made it this far, and you didn't fall asleep, you must be a real crypto... nerd. Like us!

I told you the math would be worth it.

There is a lot more in the whitepaper. Go check it out.

The next coolest piece of research is a stateless version of this. For this we want to explore SLH-DSA. The signatures are bigger, but you never have to track which keys are spent.

And my personal favourite idea we did not get to: using the vault to guard its own upgrade authority, so the bunker protects the bunker.

Lots more to cook up in the Lab.

## Slide 11, outro

Feel free to reach out with any questions!
