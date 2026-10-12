## ChatGPT

# Pass A — The Solana Bunker scene map

**The story is: a provocative warning sends us down a rabbit hole; we build an embarrassingly simple vault, improve it, discover why it still fails, and arrive at a better way to authorize spending—without changing the receiving address.**

The audience should leave remembering:

> **The address stays. The authorization changes.**

I’d start with **15 scenes across five acts**. These are presentation scenes, not necessarily separate pages: each can contain a few deliberate reveals, with optional technical detail inside it.

For planning, I’m budgeting approximately **three minutes for the pitch and eleven minutes for the technical walkthrough**. Those are working targets, not assumptions about submission limits. The website contains the complete experience; the two recordings take different routes through it.

---

# Act I — “Should we be worried?”

## Scene 1 — “Unfortunately, this presentation contains mathematics.”

**Purpose:** Establish the playful tone and introduce the warning that inspired the project.

**Primary visual:** The tweet occupies one side. On the other, two simplified address-generation paths contrast a hashed-public-key address with an ordinary Solana public-key address. Highlight the relevant sentence from the tweet rather than expecting anyone to read the whole thing.

Your opening joke leads directly into:

> “This advice made me wonder: what would bunker mode actually look like on Solana?”

The **“Should I panic?”** button reveals a brief clarification: this is a hypothetical threat model motivating an experimental application—not a demonstration that Solana’s cryptography has been broken.

Selected replies can be an optional, expandable layer if Mikhail supplies useful ones. They should illustrate the reaction, not serve as evidence.

**Audience takeaway:** There is a specific reason to investigate alternative authorization on Solana.

**Pacing:** Essential. Roughly **15 seconds in the pitch; 35 seconds technically**.

**Transition:** “But first, the warning contained another claim we wanted to investigate.”

---

## Scene 2 — “The curious case of the missing papers”

**Purpose:** Deliver the intriguing research detour without making the project depend on a conspiracy being true.

**Primary visual:** A two-part evidence board. One side contains the historical publication question; the other contains the OpenAI paper inventory and category distribution. A highlighted quote connects the allegation to the investigation.

The scene’s question is:

> “Is there a meaningful absence here—or are we telling ourselves a good story?”

Its final reveal depends on the actual findings. It could report a supported historical pattern, a classification-sensitive result, an inconclusive dataset, or no meaningful anomaly. We should design for every outcome.

**Audience takeaway:** We tested the premise instead of treating an exciting allegation as a fact.

**Pacing:** Optional for the short route, expandable for the technical route. Budget **10 seconds / 60 seconds** when included.

**Dependency:** Research results. No invented historical curve, implied statistical significance, or empty chart dressed up as a finding. If the evidence is weak, the scene becomes shorter—not more speculative.

**Transition:** “Regardless of the theory, the engineering question is interesting.”

---

# Act II — “Here’s the math. Here’s the experiment.”

## Scene 3 — “Tonight’s cast of characters”

**Purpose:** Your upfront concept roll call: anchor the vocabulary before teaching any of it.

**Primary visual:** A collection of labeled mathematical objects—not a bullet list. A keypair, curve, hash machine, fingerprint-like digest, tree, vault address, and signature each get a recognizable visual identity.

You rattle off something like:

> “Public keys. Elliptic curves. Hash functions. Preimages and digests. Program-derived addresses. Merkle trees. One-time signatures.”

Then:

> “Don’t worry. They’ll make sense when we need them.”

Each object later returns in its relevant scene. That makes this an introduction to the cast, rather than a glossary exam.

**Audience takeaway:** They have heard the vocabulary, seen the objects, and know the presentation will explain them.

**Pacing:** **Essential in both versions.** Approximately **8 seconds / 15 seconds**.

**Transition:** The objects assemble around the thing we are building.

---

## Scene 4 — “Meet Solana Bunker”

**Purpose:** Reveal the project and state the research question before the detailed demonstrations.

**Primary visual:** Our permanent treasury, with an address label above it and a separate authorization panel beside it. The panel changes; the treasury and its address do not.

Working central copy:

> **One receiving address. Replaceable authorization.**

Supporting research question:

> “Can a Solana program hold assets while enforcing a spending rule that doesn’t depend on the user’s Ed25519 key?”

Small optional definitions distinguish an address, an account, a program, and a PDA. You don’t need to narrate them.

**Audience takeaway:** This is a programmable vault experiment, not a new blockchain or a claim to have invented cryptography.

**Pacing:** Essential. **15 seconds / 35 seconds**.

**Transition:** “We’re building on existing cryptography—and existing work on Solana.”

---

## Scene 5 — “We did not invent these bricks”

**Purpose:** Acknowledge prior work and locate our contribution.

**Primary visual:** A compact lineage of source cards feeding into Bunker: hash-signature constructions, reference implementations, existing Solana experiments, and relevant network research. Exact names and descriptions come from the verified prior-art inventory.

The Bunker card is labeled with what we actually implement and measure:

> **Progressive demonstrations. Stable treasury. Replaceable authorization. Reproducible measurements.**

Your spoken acknowledgment can be extremely brief. Source cards remain inspectable afterward.

**Audience takeaway:** The project’s contribution is the experiment, integration, comparison, and explanation—not a claim to have invented hash signatures or PDA custody.

**Pacing:** Brief in the pitch, expandable technically. **5 seconds / 20 seconds**.

**Transition:** “Let’s begin with the worst version.”

---

# Act III — “Build it. Improve it. Try to steal from it.”

## Scene 6 — “Version one: a drawer full of passwords”

**Purpose:** Introduce hashes through the simplest working authorization model.

**Primary visual:** Secrets enter a hash machine. Public commitments fill numbered drawers in the authorization account. The treasury remains beside it.

A selected secret is revealed, its hash matches a drawer, the slot becomes consumed, and a withdrawal is shown.

The one-line explanation:

> “We store the fingerprint of each secret. Reveal a matching secret, and the vault accepts it once.”

A storage indicator makes the accumulating commitments visible.

**Audience takeaway:** They understand the naive design and why storing many commitments takes space.

**Pacing:** Essential. **10 seconds / 35 seconds**.

**Transition:** “It works—but why store the entire drawer?”

---

## Scene 7 — “Version two: one root instead of a thousand commitments”

**Purpose:** Show exactly what the Merkle improvement buys us.

**Primary visual:** The commitment array assembles into a tree, then the stored commitment display collapses to one root. A separate usage bitmap stays visible.

For a withdrawal, highlight one leaf and its sibling path. Reconstruct the root from the bottom up; match it against the stored root.

The verdict:

> **Less commitment storage. More evidence per withdrawal.**

The graphic distinguishes the constant-size root, the authentication path, and the usage tracking. We should not visually imply that the entire application state becomes one hash.

**Audience takeaway:** A Merkle proof authenticates membership without storing every commitment onchain.

**Pacing:** Essential. **10 seconds / 40 seconds**.

**Transition:** “Beautiful. Unfortunately, we haven’t fixed the important problem.”

---

## Scene 8 — “The attacker doesn’t break the hash”

**Purpose:** Reveal the shared weakness of the first two experiments.

**Primary visual:** A pending withdrawal carries a revealed secret toward the vault. The attacker copies the secret and constructs a competing withdrawal with a different destination. In our controlled scenario, the attacker’s version executes first.

There is **no cracking animation**. No quantum computer. No enormous GPU cluster.

The verdict lands in the center:

> **“We didn’t break the hash. We copied the password.”**

A small label identifies this as a simulated adversarial-ordering demonstration.

**Audience takeaway:** One-time consumption does not guarantee that the right person wins the first use. Merkle membership does not bind a credential to an intended payment.

**Pacing:** Essential, with enough time for the failure to register. **15 seconds / 40 seconds**.

**Transition:** “We need to authorize a message—not hand over a password.”

---

## Scene 9 — “A signature made of hashes”

**Purpose:** Explain the conceptual jump to message-bound authorization.

**Primary visual:** Winternitz chains beside a plainly readable withdrawal instruction. Selected chain positions represent that message. The attacker tries to change the instruction; the checksum portion makes the attempted manipulation fail.

For the technical route, this scene has an optional **Lamport prelude**: paired secret commitments demonstrate the simpler one-time-signature idea before we compress it into chains.

The pitch does not need every mechanic. Its central sentence is:

> “Reveal carefully selected evidence that authorizes this exact instruction.”

This is a good place for the recurring math joke: briefly reveal the real expression, acknowledge the mathematics, and return to the visual explanation.

**Audience takeaway:** A digital signature can be constructed from hashes, and it authenticates the message rather than merely revealing a bearer credential.

**Pacing:** Essential, with the largest technical expansion. **12 seconds / 80 seconds**.

**Transition:** “That gives us one signature. How do we make a useful wallet?”

---

## Scene 10 — “Version three: a whole tree of signing keys”

**Purpose:** Assemble the XMSS centerpiece from objects the audience already recognizes.

**Primary visual:** Each leaf now represents a one-time signing public key, rather than a password commitment. The tree authenticates the key; the signature authenticates the withdrawal.

A selected leaf signs, its authentication path lights up, and the usage bitmap marks it consumed. A second withdrawal uses a different leaf while the root stays unchanged.

Working copy:

> **The signature proves authorization. The tree proves membership.**

An optional technical beat demonstrates retrying the same signed intent and burning an uncertain leaf. Keep it brief; this is not a recovery seminar.

**Audience takeaway:** XMSS combines the one-time-signature mechanism with tree authentication, while retaining signing-state responsibilities.

**Pacing:** Essential. **15 seconds / 60 seconds**.

**Transition:** “Now let’s put that inside an actual Solana vault.”

---

# Act IV — “Show the program. Show the numbers.”

## Scene 11 — “Inside the bunker”

**Purpose:** Explain our account architecture and the path from user intent to execution.

**Primary visual:** The Bunker program above two accounts: the authorization state PDA and the treasury PDA. SOL and mock-USDC representations sit with the treasury side of the diagram.

A synthetic recovery-phrase graphic branches into hash-signing material and the public authority record. A separately drawn relayer pays for submission. The signed intent travels to the program, which checks it before moving assets.

For the technical version, distinguish the phrase’s ability to regenerate keys from the signer’s responsibility to track their use. No real mnemonic or private material appears on screen.

The visual should also leave room to distinguish the native-SOL treasury from the token account controlled by the PDA.

**Audience takeaway:** The relayer submits the transaction; the hash-based authorization controls spending; the two PDAs have distinct jobs.

**Pacing:** Expandable. **8 seconds / 60 seconds**.

**Transition:** “Enough animation. Let’s show what actually runs.”

---

## Scene 12 — “Same address. New authority.”

**Purpose:** Deliver the real implementation payoff.

**Primary visual:** The lab panel opens beside the persistent vault illustration. It shows the cluster, addresses, balances, active authorization mode, and transaction status.

The preferred demonstration is a prepared vault performing a withdrawal and an authorization-root rotation. The address stays visibly pinned while the authority changes.

For the technical recording, expand into both SOL and mock USDC, the controlled attacker test, and leaf burning. The short pitch should feature the strongest completed operation, not a tour of every button.

**Audience takeaway:** The program demonstrates a real, inspectable state transition—not just an animated proposal.

**Pacing:** Essential. **20 seconds / 60 seconds**, excluding unpredictable waiting time.

**Dependency:** Actual implementation results. A clearly labeled recorded run is the fallback for a live network failure. A missing feature is described as incomplete, not simulated as if it succeeded.

**Transition:** “And what does that cost?”

---

## Scene 13 — “The mathematics has a receipt”

**Purpose:** Turn implementation results into the research contribution.

**Primary visual:** A transaction fills with colored blocks representing its actual serialized components. Beside it, a compute meter fills to the measured amount. A compact comparison shows the three experiments’ storage, witness size, transaction count, and execution cost.

Use the **actual tested transaction format and limits**, not numbers inherited uncritically from our earlier conversation.

This scene gets its data directly from Codex’s experimental outputs. Every number should be identifiable as measured, calculated, or still pending.

**Audience takeaway:** The tradeoffs are concrete and reproducible.

**Pacing:** Essential. **12 seconds / 40 seconds**.

**Dependency:** Benchmarks. If a verifier exceeds a limit, show that honestly as a result, together with the attempted execution strategy.

**Transition:** “What have we proved—and what haven’t we?”

---

# Act V — “A research result, not a magic shield”

## Scene 14 — “What this bunker does—and does not—protect”

**Purpose:** State the experiment’s boundaries and open the stateless-signature research direction without restarting the architecture discussion.

**Primary visual:** A boundary around the demonstrated authorization path. Outside it sit the unchanged assumptions: runtime and consensus, trusted program upgrades, secret handling, and client signing-state management.

Then an optional reveal introduces SLH-DSA as a larger authorization package with no persistent one-time signing counter. It is shown as a **future-work module**, unless we actually implement and measure it.

The technical route can briefly contrast compact stateful spending with a possible stateless administration path. No recovery state machine, multi-device enrollment tour, or timelock design here.

**Audience takeaway:** We know the scope of the claim, and there is a clear next experiment.

**Pacing:** Essential boundary statement; expandable future-work beat. **10 seconds / 40 seconds**.

**Transition:** “But this part already gives us something worth exploring.”

---

## Scene 15 — “Keep the address. Change the lock.”

**Purpose:** Close on the contribution rather than a collection of caveats.

**Primary visual:** The same treasury from the beginning, surrounded by the three demonstrated authorization models. The address is unchanged.

Working closing line:

> **“Solana Bunker explores a permanent receiving address with replaceable authorization—starting with hashes.”**

The whitepaper QR code is dominant. Source code, reproducible experiments, and the lab are secondary destinations. In the app, “Read the research” and “Open the lab” are direct controls.

Your final joke can callback to the opening:

> “You survived the mathematics. The passwords didn’t.”

**Audience takeaway:** They remember the experiment and know where to inspect it.

**Pacing:** Essential. **10 seconds / 20 seconds**.

---

# How the two recordings differ

**The pitch is the transformation story.** Warning, quick concept roll call, Bunker’s promise, the three experiments, the copied-password failure, the real result, and the measured tradeoff. The research mystery and prior work are brief flashes rather than detours.

**The technical presentation is the explanation story.** It uses the same scene order but opens the historical investigation, Lamport prelude, Winternitz checksum, bitmap, account architecture, transaction internals, and stateless future-work sections.

**The website is the complete artifact.** Visitors can replay a particular explanation, inspect sources, open benchmark details, and enter the lab without connecting a wallet just to read the research.

The proposed timings total about **2 minutes 55 seconds** and **10 minutes 40 seconds**, before transitions or live waits. We should rehearse against those budgets rather than turn every optional detail into mandatory narration.

# The three moments I’d protect above everything else

**The array collapsing into a root.** The audience immediately sees why the second experiment exists.

**The attacker copying the password.** They understand why improved storage is not improved authorization.

**The root changing while the address stays fixed.** They see the project’s central promise delivered.

Those are our visual anchors. Fancy transitions, historical charts, equations, and stateless-signature illustrations should not take development time away from making those three moments excellent.

# What this lets us design next

For Pass B, I’d prototype **Scene 1, Scene 6, and Scene 9**: the editorial opening, the simplest animated experiment, and the most demanding cryptographic explanation.

Across those three, we can establish the typography, layout, recurring objects, humor, and animation language. Then the rest of this scene map becomes much easier to build consistently.

**The narrative is now concrete enough to design against, but flexible enough to survive whatever the research and benchmarks actually find.**

---

Here's a quick summary of the conversation:

The conversation explores a comprehensive approach to post-quantum cryptographic security, focusing on a "bunker mode" to mitigate potential risks from advances in AI-driven cryptanalysis that could break ECDSA signatures. Key strategies include migrating assets to fresh, unused addresses that hide public keys behind hashes and advocating for hash-based cryptography as a long-term solution. The discussion emphasizes a careful, controlled migration without panic and highlights ongoing institutional efforts like Project11's tracking and upcoming events to raise awareness.

Additionally, the conversation shifts towards designing a Solana-based smart wallet vault to implement multi-signature schemes resistant to elliptic curve risks posed by AI advancements. It highlights using hash functions like SHA-256, hierarchical key management, and post-quantum signature schemes such as XMSS and SPHINCS, incorporating motion graphics for educational outreach and illustrating challenges like timing attacks and transaction size constraints for future research and development.

- Continue with Pass B design for key scenes
- Summarize the entire scene map as TL;DR bullet points
- Create a checklist of scenes with core audience takeaways

