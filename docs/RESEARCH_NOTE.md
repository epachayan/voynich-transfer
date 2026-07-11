# Inventory-transfer analysis reveals a robust one-dimensional structural gradient in Voynichese

## Unsupervised segmentation transfer across dialects, scribes, sections, folios, labels, and synthetic controls — v11

*Draft for critique — July 2026. Version 11, superseding v10 (a corrections-and-reframing pass: retitled; result-JSON artifacts reconciled with the prose; "machinery" reserved for merge-inventory and within-word-sequence effects; abstract tightened — experiment content unchanged from v10, which added Experiment 20 — a calibrated self-copying generator that fails to reach the pole informatively, localizing the residual structure to the pole's word-templates. This version closes the current computational pass; further progress likely requires external replication, codicological evidence, and independent model-building. This is a solo research project carried out with extensive AI assistance throughout — including Claude (Fable 5 and Opus 4.8, via Claude Code) and ChatGPT-5 — used for ideation, experiment design and critique, writing and debugging the analysis code, running the computations, and drafting/editing this note; see the repository README for the full disclosure. All computations were run in a sandboxed Python environment against publicly available corpora, with fixed seeds throughout.*

---

## Summary

We introduce a simple instrument — **inventory transfer** — and apply it across the Voynich Manuscript. A greedy optimizer discovers, for any stretch of text, the sequence of adjacent glyph-pair merges that maximally raises conditional character entropy (h2); the discovered merge inventory of region X is then replayed on region Y, and the fraction of Y's own optimal entropy gain that X's inventory recovers serves as a *merge-transfer similarity* score between the structural organization of the two regions. Twenty experiments, each pre-specified, yield the following picture:

1. **The optimizer rediscovers the literature unsupervised** (Exp 1). Its first seventeen moves on the full manuscript reproduce the hand-curated verbose-cipher inventory of the past 25 years (benches, q-gallows glue, the aiin minim family, ol/or/ar/al, dy/edy), then begin absorbing whole high-frequency words. Natural-language h2 is purchasable (Italian at 24 merges, Latin at 31) but the receipt is damning: a 45–52 symbol inventory forcing homophony, plaintext words of ~2.6 units against 5–6 letters in real medieval texts, and an overshooting h1. A meaningless Markov control with matched bigrams passes every language threshold more easily — entropy repair by grouping is evidence about structure, never meaning — while the real manuscript's *resistance* to repair (stalling ~0.2 bits below its own bigram shadow) reveals order beyond bigrams.

2. **Currier A and B differ in machinery, not just vocabulary** (Exp 2). Run separately at matched size, the searches diverge at the first move (A builds `ch`; B builds `he`, because in B the bench attaches to *e*). Cross-dialect transfer recovers 77–80% of native gain, symmetrically; the ~20% residue is constant across search depth.

3. **The split follows dialect, not penmanship** (Exp 3). Across Lisa Fagin Davis's scribal hands with split-half controls: same-scribe transfer 98.7% (ceiling), different-scribe-same-dialect 94.2%, across-dialect 75.5%. As a by-product, a lexical classifier finds tiny hand 4 (353 words) unambiguously A-type (31.2 A-signature words per 1000, zero B-signature words), siding with the revised attribution (Scribes 1 and 4 → A) against the assignment printed in Davis (2020); hand 5 classifies as B.

4. **The dialect effect survives a full topic control — but "Currier B" is not one machine** (Exp 4). In a factorial over Herbal-A, Herbal-B, Biological-B and Stars-B at matched size: Herbal-A↔Herbal-B (same subject, different dialect) transfers at 79.7%, confirming the dialect boundary is not a topic artifact. But same-dialect cross-topic transfer, predicted ≥90%, ranges 80.7–97.8%: Biological-B is an extreme pole (baseline h2 = 1.788, the most compressible text measured; its inventory recovers only 44–48% on Herbal-A — the worst transfer in the project), while Herbal-B behaves as a *mixture*, its own merges interleaving A-tokens with B-suffixes, and served equally well by the Herbal-A inventory (bootstrap 95% CI [78.9, 82.4]%) and the Biological-B inventory ([77.5, 84.4]%).

5. **The A/B machinery gap is parse-robust** (Exp 5). Under the entirely different "Minimal" parse (ligatures as single symbols), the cross-dialect recovery replicates at 76.7% / 80.6%, with the same attachment signatures.

6. **The whole manuscript lies on a single gradient** (Exp 6). A 13-unit transfer map (2,000 contiguous words per unit, all major section×language cells) is in near-perfect Robinson form: the first MDS axis carries **84.1%** of the variance (axis 2: 8.2%). Spectral seriation orders the units HA–HA–HA–PA–SB–SB–HB–SB–SB–SB–BB–BB–BB, with mean adjacent similarity 92.5% and endpoint (Herbal-A ↔ Biological-B) similarity 43.0%. The Currier boundary is a **threshold on this continuum, not a cliff** (the A→B crossing sits at ~83%, higher than several within-B pairs). Two stable anomalies: Herbal-B — physically interleaved among Herbal-A pages — is machinery-wise embedded in the Stars-B cloud (92.4% on an alternate window); and the pharmaceutical section, nominally Currier A, sits at the exact **center** of the gradient, closer to Herbal-B (86%) than to Herbal-A (~80%), replicated on a disjoint window. The gradient is neither codex position (the biological section is physically central yet is the extreme pole) nor the Currier label (Pharma-A breaks it); baseline compressibility co-varies with it, bottoming at BB1's h2 = 1.739.

7. **The gradient resolves to single folios** (Exp 7). A cheap per-folio estimator — one global merge inventory, each folio scored by projecting its token-frequency vector onto the Herbal-A ↔ Biological-B pole axis — reproduces the 13-unit seriation at **r = 0.938**, validating folio coordinates for all 182 substantial folios. Section plateaus survive at page resolution (within-section adjacent-folio jump 0.135 vs overall spread 0.352); Biological-B is the only section clearing +0.80; Pharma's centrality holds folio-by-folio (all 16 positive, tight at +0.33). Coordinates fall out for pages Currier never classified, including the opening folio **f1r = −0.09** — past the Herbal-A centroid, the purest o-attachment machinery in the book.

8. **The gradient is register traversed by scribes, not penmanship** (Exp 8). Joining folio coordinates to Davis's scribal attribution: hold section and dialect fixed and swap the scribe, the coordinate barely moves (Herbal-B by Scribes 2/3/5 spans just 0.11, below the folio noise floor); hold the scribe fixed and change the section, it moves a lot (Scribe 1 shifts +0.32 Herbal-A→Pharma-A within dialect A; Scribe 2 traverses +0.62 Cosmo/Herbal-B→Biological-B within dialect B, **personally reaching the extreme pole**). A commonality decomposition gives section+dialect a unique R² of **+0.235** against scribe's **+0.010** — penmanship explains ~1% of coordinate variance once regime is known, resolving the Experiment-3 confound in favour of regime by 23:1. The gradient runs orthogonally through the Currier A/B axis: one scribe within one dialect still traverses it by section.

9. **The gradient behaves as Timm's drift model predicts — where that model actually bites** (Exp 9). Timm published a *model* of sequential self-copying, not a page chronology; testing its commitments against the coordinate: length-controlled repetitiveness climbs the gradient **within Currier B** (ρ = +0.475) — his "increasingly monotonous" claim as a measurable continuum peaking at the Biological pole — while flat-to-falling within A (−0.212) and null globally (+0.053), so word-level monotony growth is a B-phenomenon riding the axis, not the axis itself. Binding position predicts almost nothing within sections (ρ from −0.32 to +0.22; distance-decay 0.82–1.47×), consistent with drift between sections plus the documented rebinding. And the transfer matrix is time-asymmetric in the direction forward-copying predicts (Biological-B's inventory reconstructs Herbal-A at 44–48% versus 60–62% reversed): the process accumulated *and forgot* — pure-additive drift is rejected.

10. **The gradient is neither an EVA artifact nor a greedy artifact** (Exp 10). Rerun under **v101** — a third transliteration with a wholly different alphabet — the A/B recovery replicates at **77.2 / 77.7%** (vs EVA-Maximal 77–80%, EVA-Minimal 76.7/80.6%), and Currier B independently rebuilds the q-gallows attachment (v101 `4o`, `4oh` = EVA `qo`, `qok`). Made **stochastic** (sampling among the top-3 improving merges, 5 seeds/dialect), recovery holds at mean 78.4 / 78.9% (sd ~5); no restart drops toward the 44–48% that genuinely different machinery gives, and the first ~13 of 17 merges are path-invariant. Effect sizes (20–56 points) dwarf the parse and path noise (a few points).

11. **A first-order model generates the gradient's interior in (coordinate, h2); its pole needs memory** (Exp 11). Fitting character-transition distributions to the two poles and dialing a single mixing parameter θ between them, generated corpora scored with the Exp-7 instrument place the real sections **on** the one-parameter (coordinate, h2) curve to within ±0.08 bits — so on those two statistics the mid-gradient is indistinguishable from a two-pole blend (this bounds the two statistics, and is not a claim that the text is a blend or that a bigram model explains the manuscript). But at θ=1 the memoryless generator reaches only coordinate +0.79, not the real Biological pole's +1.00: real Bio-B reuses whole words far more (type/token repetition 0.719 vs 0.612), so **the pole's extremity is a self-copying memory effect** outside any bigram model — unifying Exp 1's control, Exp 9's drift-with-forgetting, and Timm's self-citation as the mechanism that builds the extreme regime.

12. **Labels — the one probe aimed at meaning — do not, under these tests, separate like names** (Exp 12). Using the ~4,800 label/legend tokens filtered out of every prior experiment (a label is anchored to a drawn object, the nearest thing the manuscript offers to a bilingual crib): labels are a *distinct register*, systematically pulled toward the o-attachment pole relative to their section's prose (H1 falsified, initial-glyph TV 0.14–0.33). They carry significant between-section structure, more than running text does (H2, p = 0.0005), but along the same register axis — and the direct referent contrast is null: star-labels and plant-labels, annotating utterly different things, are morphologically near-identical (coordinate +0.01 vs −0.00, both 43% `o`-initial, TV 0.154). A naming system would make them differ; instead, under these morphology tests, the best crib candidate does not separate like referent names — pointing mildly *away* from readability, though these coarse features could miss a naming scheme.

13. **Controls and robustness — the gradient is real and reproducible, but not by itself diagnostic** (Exp 13–15). Through the identical map pipeline: a random-bigram null shows *no* gradient (axis-1 42%, min-similarity 98% — the pipeline does not manufacture one), yet both a meaningless section-mixture bigram (74%) and verbose-ciphered real Latin+Italian (88%) reproduce a dominant-axis gradient — so a one-axis gradient signals neither meaning nor its absence. What no control reproduces is the manuscript's *combination* of a strong gradient with anomalously low entropy; only a bigram mixture fit to the (already low-entropy) sections matches it, while a crude self-copying control and the verbose cipher come out far too high-entropy. Leave-one-section-out confirms nothing is baked in (Pharma stays mid-gradient at +0.27 with the instrument rebuilt without it; the held-out Biological pole still projects +0.95). Shuffle nulls localize the signal: word *order* contributes nothing, while ~74 of the 88 axis points survive destroying within-word glyph order — the gradient is dominated by section glyph-frequency and word-length, with a genuine but secondary (~14-point) sequential-'machinery' component. Net: robust and real, but constraining interpretation rather than deciding it.

14. **Deeper robustness and a revised label finding** (Exp 16–19). A *faithful-in-mechanism* self-copying generator (whole-word copying with mutations confined to attested similarity classes, plus drift) answers the question Experiment 13 left open: structured self-copying **does** reproduce the manuscript's low-entropy gradient (unit h2 1.1–1.9, bracketing real Bio-B; map axis-1 88.7%, min-similarity 18%) — where the crude random-mutation control failed at h2 2.4–3.6 — though it overshoots repetition and, on the real instrument, drifts only to +0.12 rather than the full pole, reproducing the *phenomenology* but not the exact manuscript. **Beam search** (width 5/10) confirms the A/B machinery gap is no greedy artifact (recovery 80.7/81.0% vs greedy 76.6/77.2%, still far from 100%). **Cross-transcriber** replication holds the gap on two independent transcriptions (Friedman-group 70/82%, another 68/68%, vs Takahashi 77/77%) — not a transcription artifact. And a **richer label n-gram test** revises Experiment 12: with 2–3-gram prefix/suffix templates, star-labels and plant-labels separate more than the coarse initial-glyph test showed (TV 0.25–0.33 vs 0.154) and within-dialect referent separation is significant (p = 0.0005) — but the separating pattern is the same e-vs-o register axis, so it stays entangled with register rather than being clearly semantic. None resolves meaning; all sharpen the constraints.

15. **Calibrating the self-copying generator to the pole fails — informatively** (Exp 20). Fitting mutation directions to the measured Herbal-A→Bio-B glyph shift and pushing toward the pole, the generator reaches the pole's *statistical neighborhood* (coordinate +0.76, low entropy, axis-1 81%) but no further, and produces *malformed* pseudo-words (`qcheeetedy`, `otcheeel`) rather than Bio-B's coherent vocabulary (`qokedy`, `chedy`) — overshooting entropy and repetition. Local feature-stacking cannot assemble the pole's rigid word-templates, so the Biological pole's extremity requires coherent template structure that directed local self-copying does not manufacture. With Experiment 16 (regime but not axis), the two bracket the claim: self-copying reproduces the manuscript's *phenomenology* but not its *vocabulary*, and the pole is the locus of the residual structure — any self-copying account must include a slot grammar, not just random drift.

**One-sentence version:** an unsupervised optimizer rediscovered the field's glyph grammar; transfer testing split it into a shared chassis with regime-specific attachments; a topic factorial and a scribe decomposition showed the regimes track content and are traversed by individual scribes (penmanship ~1% of the variance); at folio resolution the whole manuscript is a single validated register gradient carrying 84% of the variance, anchored by Herbal-A and Biological-B, on which "Currier A/B" is one coarse threshold and the pharmaceutical section stands at the midpoint — an axis that behaves like Timm's self-copying drift wherever his model makes quantitative commitments, that is real (a random-bigram null yields no gradient), robust to beam search and to independent transcribers, yet reproducible by both meaningful and meaningless structured processes — a faithful-in-mechanism self-copying generator reproduces its low-entropy gradient but not, even when calibrated, its pole vocabulary — which requires coherent word-templates beyond drift, so it constrains interpretation without deciding it; while remaining silent, as it must, on whether the drifting system carried meaning — and whose labels, the nearest thing to a crib, do not separate like referent-names under these morphology tests.

None of this is a decipherment, and Experiment 1's control shows why entropy statistics alone can never be one. These are constraints. But they are new constraints: any proposal about Voynichese — cipher, language, or generated text — must now explain a *continuous, one-dimensional machinery gradient* with section-level plateaus that individual scribes traverse by content — not a two-way dialect split, and not a scribal fingerprint.

---

### Suggested reading order

The experiments are numbered in the order they were run; for the argument rather than the lab notebook, read them thematically: **method** (§2 data/estimator, Exp 1 — the warning that entropy is not meaning); **the A/B distinction** (Exp 2); **the section map and gradient** (Exp 4, 6); **folio projection** (Exp 7); **scribe decomposition** (Exp 8); **robustness** — parse, path, beam, transcriber (Exp 5, 10, 17, 18); **controls** — synthetic, leave-one-out, shuffles (Exp 13, 14, 15); **labels** (Exp 12, 19); **self-copying generators** (Exp 11, 16, 20); and finally **what this does and does not imply** (Prediction ledger, Limitations). Experiments 3 and 9 (parse/scribe detail; the Timm drift-model tests) are supporting rather than load-bearing.

---

## 1. Background and prior work

The verbose-cipher hypothesis — that several Voynich glyphs encode one plaintext unit — is the mainstream response to the manuscript's anomalously low conditional character entropy (h2 ≈ 2.1 bits vs ≈ 3.0–3.5 for European languages). Entropy analysis goes back to Bennett (1976); Stallings (1998) showed a verbose cipher over Latin can reproduce the Voynich entropy profile; Pelling (2006) developed a verbose-cipher theory at book length; Gheuens (2020) ran hand-picked regrouping experiments to raise h2, with Zandbergen noting the combinatorial search space and suggesting it "could be a good area for AI methods"; Zattera (2022) formalised the prefix–root–suffix "slot" structure of Voynich words; a 2025 *Cryptologia* study constructed the "Naibbe cipher," a hand-executable verbose homophonic system producing statistically Voynich-like ciphertext. On the null side, Timm & Schinner (2019) showed a meaningless self-copying process reproduces many of the same statistics, and argued the manuscript's internal variation reflects gradual *evolution* of the system during writing.

On internal divisions: Currier (1976) identified two statistical "languages," A and B; Davis (2020) identified five scribal hands; a 2026 arXiv study (arXiv:2604.25979) confirmed the A/B distinction as intrinsic and unsupervised-recoverable via frequency-ratio shifts in visually similar character pairs. Lindemann & Bowern's entropy work (arXiv:2010.14697; *Annual Review of Linguistics* 2021) and its public corpus repository provide the parses, partitions, interlinear source file, and comparison texts used throughout.

What appears **not** to have been tried before this note: (a) automated, objective-driven discovery of the merge inventory; (b) inventory **transfer** as a similarity metric between manuscript regions; (c) that metric applied per dialect, per scribal hand, per section×dialect cell, and as a whole-manuscript seriation, with matched sizes, split-half ceilings, alternate-window checks, and bootstrap intervals. Components exist; the composition, to our knowledge, does not. Corrections welcome — that is partly what this note is for.

---

## 2. Data, estimator, calibration

**Corpus.** All Voynich text derives from the public repository `github.com/chirila/Voynich-public`. Experiments 1–3 and 5 use the prepared partitions ("Maximal Simplified … Text" and "Minimal … Text"). Experiments 4 and 6 rebuild corpora directly from the repository's `interlinear_full_words.txt` (per-word folio, section, Currier language, hand, transcriber, placement), filtering to transcriber H (Takahashi), paragraph placements only, lowercased, `a–z` words only — a pipeline that **exactly reproduces** the prepared full corpus (33,107 words, h2 = 2.112, matching to the third decimal), so all cuts are on one footing.

**Reference texts** (same repository): *Secreta Secretorum* (Latin, 39,349 w); Brunetto Latini's *Rettorica* (Italian, 13th c., 32,230 w); the Middle English *Cirurgie* (97,949 w); unpointed Hebrew Genesis.

**Estimator.** Space-joined symbol stream, space counts as a symbol; h1 = unigram entropy; h2 = H(adjacent bigram) − h1, in bits. Calibration against the repository's published statistics:

| Text | ours h1 / h2 | Yale CSV h1 / h2 |
|---|---|---|
| Full Voynich (Max. Simp. Text) | 3.872 / 2.112 | 3.877 / 2.115 |
| Latin — Secreta Secretorum | 4.017 / 3.277 | 4.017 / 3.277 |
| Italian — Rettorica | 4.032 / 3.141 | 4.032 / 3.141 |
| Middle English — Cirurgie | ~4.13 / ~3.25 | 4.132 / 3.240 |
| Hebrew — Bereshit (unpointed) | ~4.20 / 3.53 | 4.202 / 3.526 |
| Currier A (Max. Simp. Text) | 3.832 / 2.140 | 3.842 / 2.146 |
| Currier B (Max. Simp. Text) | 3.873 / 2.003 | 3.875 / 2.005 |

**Search.** Byte-stream representation; per step, evaluate the 90 most frequent adjacent within-word symbol pairs (merges never cross a space), apply the merge maximising h2, record the sequence ("ops"). Greedy hill-climbing — deliberately the simplest member of the family.

**Transfer metric.** Replay X's ops (first k) on corpus Y; **recovery** = (Y's h2 gain under X's ops) / (Y's h2 gain under its own ops). 100% = X's machinery explains Y's compressible structure as well as Y's own. Structural depth k = 17 throughout unless noted.

---

## 3. Experiment 1 — Full manuscript vs. medieval languages, with a meaningless control

Greedy search, 40 merges, full manuscript (baseline h1 = 3.872, h2 = 2.112, 5.07 glyphs/word). Control: order-1 character Markov text fitted to the manuscript (seed 1404) — matched unigrams/bigrams, zero meaning.

**Discovered inventory (merge order):**

```
ch  ai  ol  dy  che  ok  in  aiin  sh  qok  ee  ar  or  al  ot  she  ain
daiin  chedy  eey  qot  edy  eedy  ey  ody  hy  chol  am  chy  dar  chey
cho  dal  shedy  qo  chor  air  dain  chdy  chc
```

Moves 1–17 recapitulate the hand-curated literature (ch first, sh ninth — the ligature parse is rediscovered before anything else — then qok, the minim family, or/ar/ol/al, ee, dy/edy). From move 18 the optimizer swallows whole high-frequency words (daiin, chedy, chol, shedy): the manuscript's commonest words statistically behave as single symbols.

**Crossing the language band:**

| Target | h2 | Crossed at merge | Inventory K | Units/word | Real letters/word | h1 there |
|---|---|---|---|---|---|---|
| Italian — Rettorica | 3.141 | 24 | 45 (vs 29-symbol alphabet) | 2.74 | 5.15 | 4.57 |
| Middle English — Cirurgie | ~3.25 | 30 | 51 | 2.59 | 4.15 | — |
| Latin — Secreta | 3.277 | 31 | 52 (vs 25) | 2.57 | 5.66 | 4.69 |
| Hebrew — unpointed Genesis | 3.53 | **never** (3.403 at 40) | — | — | 4.40 | — |

Language-level h2 is purchasable at the price of (i) a doubled inventory — any letter mapping must be homophonic, independently the Naibbe conclusion; (ii) plaintext words of ~2.6 units — half of real Romance word length, in *syllables-per-word* territory, which is presumably why syllabary, abbreviation, and East-Asian-structure readings keep resurfacing; (iii) a broken h1. The one unreachable target is unpointed Hebrew — ironically the top pick of the 2016 machine-learning language ranking.

**Control.** The Markov gibberish starts at h2 = 2.115 and climbs faster and higher (3.594 vs 3.403 at merge 40, overtaking near merge 12). Entropy repair by grouping carries no evidence of meaning; and the real manuscript's *resistance* to repair reveals order beyond bigrams (Zipfian whole-word reuse, positional word grammar) that its order-1 shadow lacks.

---

## 4. Experiment 2 — Currier A vs Currier B

Currier A (11,077 words) vs Currier B block-subsampled to matched size (seed 1438). Matched-size baselines: A 2.140, B 1.970. Pre-specified: early structural merges nearly identical; divergence confined to the vocabulary tail. **Falsified in its strong form.**

```
A:  ch  ol  da  cho  sh  in  iin  che  qo  or  daiin  dy  aiin  ke  chol  ey  chy
B:  he  dy  ai  che  qo  ol  qok  edy  in  aiin  ar  she  ch  al  ain  chedy  ok
```

Divergence begins at move one: in B the bench attaches overwhelmingly to *e* (`h+e` outbids `c+h`; plain `ch` not built until B's step 13); in A it attaches to *o* (cho, chol, chor, chy), and A alone discovers the benched gallows (ct → cth → cthy). `daiin` arrives at A's step 11 vs B's 26; `chedy` at B's 16 and never in A's 40. First-17 Jaccard 0.26; all-40 Jaccard 0.43. Full-40 exclusives — A: `cho chol chor chy ct cth cthy da dain iin ir ke qoke sho shol yt`; B: `ai ain am chc chdy chedy edy eedy eey he lk olk qokain qokedy qokeedy shedy`.

**Transfer:** k=17: A own 2.944 / B-inv 2.756; B own 2.851 / A-inv 2.650. k=40: 3.363/3.112; 3.299/3.036. Recovery **77–80%**, symmetric, ~20% residue constant across depth. Three B subsamples (seeds 1438, 2026, 408) give 16/17 identical first inventories.

---

## 5. Experiment 3 — Scribal hands: dialect beats penmanship ~5:1

Hands 1–3 (10.0–11.3k words) each split into two disjoint 5,000-word block samples (seeds 1401–1403); k = 17; full 6×6 transfer.

|      | 1a | 1b | 2a | 2b | 3a | 3b |
|---|---|---|---|---|---|---|
| **1a** | 100.0 | 99.3 | 78.3 | 79.6 | 77.7 | 74.2 |
| **1b** | 98.9 | 100.0 | 78.7 | 81.2 | 79.7 | 77.8 |
| **2a** | 69.8 | 74.4 | 100.0 | 98.7 | 95.8 | 93.9 |
| **2b** | 69.1 | 75.8 | 98.6 | 100.0 | 98.6 | 93.4 |
| **3a** | 72.4 | 77.6 | 93.7 | 93.7 | 100.0 | 97.5 |
| **3b** | 67.8 | 74.6 | 91.6 | 92.8 | 99.4 | 100.0 |

Tiers: within-scribe (ceiling) **98.7%**; within-B across-scribe **94.2%**; across-dialect **75.5%**. Split-half inventory agreement 16/17, 16/17, 14/17 (hand 3 the most heterogeneous). Hand 2 is the extreme regime (baseline h2 ≈ 1.94–1.96, openers `he, dy, edy`) — noteworthy alongside Davis's suggestion that Scribe 2 may have led the project.

**Hands 4 and 5** (353 / 580 words; lexical signatures per 1,000 — A-set: chol, chor, cthy, ckhy, cthor; B-set: chedy, shedy, qokeedy, qokedy, qokain, qokaiin): hand 4 = 31.2 A-words, **0.0** B-words → unambiguously A-type, siding with the revised grouping (Scribes 1 and 4 → A) against the printed 2020 assignment (2–5 → B per Currier's tests; plausibly reconciled by Currier's unclassified pages). Hand 5 = 12.1 / 46.6 plus a decisive entropy-repair preference (+0.625 B-inv vs +0.476 A-inv) → B. Remaining confound stated plainly: at scale, Currier A is essentially one scribe; hand 4's 353 words are the only independent A hand, and they fall on the A side — thinly. What stands regardless: within B, three hands share one machine at 94% of the same-scribe ceiling. The system is trained, not personal.

---

## 6. Experiment 4 — Topic × dialect factorial: the boundary is real, and B is not one machine

**Design.** From the interlinear file (transcriber H, paragraphs): Herbal-A 7,843 w; Herbal-B 3,426; Biological-B 6,198; Stars-B 10,455 (also Pharma-A 2,302, Cosmo-B 1,225, Text-A/B 932/328, unused here). Six corpora at matched n = 3,400: HAa/HAb disjoint (seed 2601), SBa/SBb disjoint (seed 2602), HB (2603), BB (2604). Pre-specified: (i) Herbal-A↔Herbal-B ≈ 75–80%; (ii) same-dialect cross-topic ≥ 90%; (iii) Minimal-parse rerun (Exp 5) reproduces the A/B gap.

**Baselines and openers:** HAa 2.108 (`ch cho da ol…`), HAb 2.081 (`ch cho da sh…`), HB 2.099 (`ch dy edy da ka…` — a mixture of A-tokens and B-suffixes), BB **1.788** (`he dy qo qok…` — the extreme pole and the lowest entropy measured anywhere), SBa 2.000 (`ch che ai dy…`), SBb 1.996 (`ch ed ai edy…`).

|      | HAa | HAb | HB | BB | SBa | SBb |
|---|---|---|---|---|---|---|
| **HAa** | 100.0 | 99.1 | 78.9 | 48.0 | 74.2 | 75.6 |
| **HAb** | 99.6 | 100.0 | 78.2 | 44.0 | 73.6 | 74.5 |
| **HB** | 80.5 | 81.4 | 100.0 | 80.7 | 97.3 | 97.8 |
| **BB** | 62.1 | 59.8 | 82.5 | 100.0 | 89.6 | 88.3 |
| **SBa** | 74.2 | 70.1 | 85.9 | 83.7 | 100.0 | 97.5 |
| **SBb** | 74.7 | 71.8 | 87.9 | 84.0 | 97.7 | 100.0 |

Tiers: same-dialect same-topic (ceiling) **98.5%**; same-dialect different-topic **87.8%** (range 80.7–97.8); different-dialect same-topic (herbal) **79.7%**; different-dialect different-topic **66.9%**.

**Prediction (i) confirmed:** the dialect effect survives the topic control at 79.7% — the A/B split is not a subject-matter artifact. **Prediction (ii) falsified**, and informatively: "Currier B" spans from near-ceiling (Herbal-B under Stars-B inventories: 97.3–97.8%) down to 80.7% (Herbal-B under Biological-B). Biological-B's inventory recovers only **44–48%** on Herbal-A — the worst transfer in the project, worse than any cross-dialect pair. And the bootstrap intervals deliver the sharpest sentence: on Herbal-B text, the Herbal-A inventory recovers **[78.9, 82.4]%** and the Biological-B inventory **[77.5, 84.4]%** — for herbal-B, same-topic-different-dialect helps exactly as much as same-dialect-different-topic. Ordered, the cells form a chain HA — HB — SB — BB with recovery falling monotonically along it: the first sighting of the gradient that Experiment 6 maps in full.

---

## 7. Experiment 5 — Parse robustness: the Minimal parse

Under the repository's "Minimal" parse (ligatures as single symbols; baselines A 2.476, B 2.253 at matched 11,077 words, seed 1438), the search signatures persist — A's early merges include `So` (=cho) while B's open `dy, edy`, and both assemble `daM` (=daiin) — and cross-dialect recovery replicates at **76.7%** (A text under B inventory) and **80.6%** (B under A). **Prediction (iii) confirmed:** the machinery gap is not an artifact of the EVA-style decomposition.

---

## 8. Experiment 6 — The transfer map: one gradient, 84% of the variance

**Design.** Thirteen units of 2,000 *contiguous* words in manuscript order: HA1–3, PA (Pharma-A), HB, SB1–5, BB1–3 (cells below 2,000 words excluded). Greedy search per unit (k = 17); full 13×13 recovery matrix; symmetrised similarity S; spectral seriation (Fiedler vector of the graph Laplacian); classical MDS on 1 − S for axis variance. Pre-specified: (a) one dominant axis; (b) ordering Herbal-A/Pharma-A → Herbal-B → Stars-B → Biological-B; (c) a clumpy, no-dominant-axis outcome kills the drift reading.

**Result:** MDS axis 1 = **84.1%** of variance; axis 2 = 8.2%; axis 3 = 4.2%. Seriation (Fiedler coordinates):

```
 HA3 ── HA1 ── HA2 ── PA ── SB5 ── SB2 ── HB ── SB1 ── SB4 ── SB3 ── BB2 ── BB3 ── BB1
 -.62   -.44   -.31  -.03  +.03   +.06  +.07  +.10   +.10   +.17   +.24   +.28   +.36
```

Symmetrised similarity in seriated order (×100):

```
       HA3  HA1  HA2   PA  SB5  SB2   HB  SB1  SB4  SB3  BB2  BB3  BB1
 HA3   100   98   98   80   74   71   68   68   66   59   51   45   43
 HA1    98  100   99   79   76   73   76   68   67   59   53   51   49
 HA2    98   99  100   81   80   77   78   72   71   65   57   56   53
  PA    80   79   81  100   83   82   86   84   80   75   74   75   72
 SB5    74   76   80   83  100   93   87   92   92   84   84   79   75
 SB2    71   73   77   82   93  100   91   94   96   89   87   85   75
  HB    68   76   78   86   87   91  100   89   89   83   87   89   83
 SB1    68   68   72   84   92   94   89  100   96   93   93   87   84
 SB4    66   67   71   80   92   96   89   96  100   95   91   83   78
 SB3    59   59   65   75   84   89   83   93   95  100   92   89   86
 BB2    51   53   57   74   84   87   87   93   91   92  100   94   96
 BB3    45   51   56   75   79   85   89   87   83   89   94  100   99
 BB1    43   49   53   72   75   75   83   84   78   86   96   99  100
```

Near-perfect Robinson form: similarity decays monotonically away from the diagonal (HA3's row reads 98 98 80 74 71 68 68 66 59 51 45 43). Mean adjacent similarity along the order: **92.5%**; endpoints (HA3 ↔ BB1): **43.0%**. The manuscript's machinery is a ramp with section-level plateaus — Herbal-A internally 98–99% self-similar (the tightest cluster), Stars-B 92–96, Biological-B 94–99 — while within-section chunk order is scrambled, so at this resolution the drift lives *between* sections, not smoothly page by page.

**Predictions (a) and (c) confirmed; (b) confirmed with two stable deviations.** First, Herbal-B — physically interleaved among Herbal-A pages in the early quires — is machinery-wise **embedded in the Stars-B cloud** (91–98% with SB units; replicated on an alternate disjoint window: 92.4% with SB2, vs 74.6% with HA1). Second, **Pharma-A, nominally Currier A, sits at the exact center of the gradient** (Fiedler −0.027), closer to Herbal-B (86%) than to Herbal-A (~80%); replicated on a disjoint window (81.2% to SB2, 77.8% to HA1, 70.9% to BB1). The Currier A→B crossing (PA → SB5) occurs at ~83% similarity — *higher* than several pairs safely inside dialect B: **the boundary is a threshold on a continuum, not a cliff.**

**The gradient is neither codex position nor the Currier label.** Physically the manuscript runs herbal quires (Herbal-B interleaved) → biological (Q13) → pharmaceutical → stars (Q20); on the gradient, the physically central biological section is the extreme pole, and the physically late pharmaceutical section is the midpoint. Baseline compressibility co-varies with gradient position, bottoming at BB1 (h2 = 1.739). The axis is a latent production dimension — register, stage, or setting of the writing system — that the existing labels only coarsely approximate.

---

## 9. Experiment 7 — Folio resolution: the gradient at single-page scale

**Design.** The 13-unit map is too coarse to place individual folios, and per-folio greedy searches are unstable at ~100 words. Instead: run one greedy search on the whole manuscript to fix a **global** 40-merge inventory; tokenise every folio with it; represent each folio by its token relative-frequency vector; define the gradient axis as the vector between the Herbal-A and Biological-B pole centroids; project each folio onto that axis (0 = Herbal-A pole, 1 = Biological-B pole). Folios below 60 words excluded. Pre-specified: (1) validation — the 13 map units' projections must correlate r > 0.9 with their Fiedler coordinates; (2) Pharma centrality holds folio-by-folio; (3) Herbal-B folios land up-gradient individually; (4) exploratory — coordinates for Currier-unclassified pages.

**Validation (gate passed).** Over the 13 units, projection vs Fiedler coordinate: **r = 0.938**. The cheap estimator faithfully reproduces the expensive seriation, so folio coordinates are trustworthy. The discovered axis is the same machinery throughout: the Herbal-A pole loads on `o, ch, cho` (o-attachment), the Biological-B pole on `qok, edy, chedy, eedy, shedy` (q-gallows + e cascade).

**Per-section folio distributions** (0 = Herbal-A pole … 1 = Bio-B pole):

| Section / dialect | n | mean | range |
|---|---|---|---|
| Herbal-A | 83 | +0.00 | [−0.22, +0.40] |
| Pharma-A | 16 | +0.33 | [+0.07, +0.70] |
| Cosmo-B | 4 | +0.39 | [+0.28, +0.52] |
| Herbal-B | 32 | +0.42 | [+0.01, +0.67] |
| Stars-B | 23 | +0.58 | [+0.28, +0.89] |
| Biological-B | 19 | +1.01 | [+0.80, +1.16] |

Predictions confirmed: (2) all 16 Pharma-A folios positive, tightly clustered at +0.33 — centrality is not a chunk artifact; (3) all 32 Herbal-B folios up-gradient (mean +0.42), none near the Herbal-A pole they are physically bound with; Biological-B is the only section clearing +0.80, essentially disjoint. **Noise check:** mean adjacent-folio |Δ| within a section = 0.135 vs overall folio SD = 0.352 — folios cohere ~2.6× tighter than the manuscript's range, so the plateaus are real at page resolution: the ramp is a staircase of section-level treads, not smooth per-page drift.

**(4) Currier-unclassified pages** receive coordinates for the first time: **f1r = −0.09** (the opening page, past the Herbal-A centroid — the purest o-attachment machinery in the codex); the text-only bifolium **f58r / f58v = +0.33 / +0.54** (mid-gradient, and internally split, recto more A-like than verso); the rosettes-foldout panel **f85r1 = +0.37** and the zodiac page **f70r2 = +0.30**, both in the Herbal-B/Pharma band.

---

## 10. Experiment 8 — Scribe vs. regime: penmanship explains ~1%

**Design.** The interlinear file carries a per-word `d.hand` column — Davis's scribal attribution (Scribe 1: 100 folios; 2: 44; 3: 30; 5: 6; 4: 1). Joining each folio's modal scribe to its Experiment-7 coordinate finally separates the two factors confounded since Experiment 3 (at scale, Currier A is essentially one scribe). Pre-specified: if the gradient is *regime*, holding section fixed and swapping scribe leaves the coordinate ~unchanged, holding scribe fixed and changing section moves it, and section explains far more unique variance than scribe.

**Scribe × section grid** (mean coordinate, folio n; 0 = Herbal-A pole, 1 = Bio-B pole):

| | Herbal-A | Pharma-A | Cosmo-B | Herbal-B | Stars-B | Bio-B |
|---|---|---|---|---|---|---|
| Scribe 1 | +0.00 (83) | +0.33 (16) | | | | |
| Scribe 2 | | | +0.39 (4) | +0.43 (20) | | +1.01 (19) |
| Scribe 3 | | | | +0.47 (6) | +0.58 (22) | |
| Scribe 5 | | | | +0.36 (6) | | |

**Same scribe, same dialect, different section → the coordinate moves.** Scribe 1 writes Herbal-A at +0.00 and Pharma-A at +0.33 (span 0.32, dialect A throughout). Scribe 2 writes Cosmo-B +0.39, Herbal-B +0.43, and **Biological-B +1.01** (span 0.62, dialect B throughout) — the extreme pole of the manuscript is one identified scribe writing the biological quire, not a different system or a different hand. **Same section+dialect, different scribe → the coordinate barely moves.** Herbal-B, written by Scribes 2, 3, 5, gives +0.43 / +0.47 / +0.36 — span **0.11**, below the 0.135 folio noise floor.

**Commonality decomposition** of folio coordinate (one-hot section+dialect vs one-hot scribe):

```
 unique to section+dialect:  +0.235
 unique to scribe:           +0.010
 shared (confounded):         0.614
```

Scribe contributes ~1% uniquely once section is known; it appeared predictive earlier only because Davis's scribes are section-segregated (the 0.61 shared term). This resolves the Experiment-3 confound in favour of **regime over penmanship, ~23:1 in unique variance**, and retroactively confirms the interpretation asserted there. Two consequences: Pharma-A's mid-gradient position becomes the cleanest controlled result in the project (one scribe, one dialect, two sections, +0.32 shift purely by content — not a labelling error); and the gradient is **orthogonal to** the Currier A/B axis rather than identical to it — dialect is near-perfectly scribe-segregated (Scribe 1 pure A; Scribes 2/3/5 essentially pure B), yet the register gradient runs *through* each dialect, Scribe 1 moving 0.32 inside A and Scribe 2 moving 0.62 inside B.

**Residual confound, stated plainly.** The *dialect-level* A/B question keeps its confound: no scribe writes substantial amounts of both dialects, so "A vs B" and "Scribe 1 vs the rest" remain inseparable. What Experiment 8 cleanly separates is the finer within-dialect register gradient from the scribe. Small cells (Scribes 3, 5 at 6 folios) and collinear regressors make the unique components lower bounds — but a near-zero cannot be inflated by collinearity, so scribe's ~1% is robust.

---

## 11. Experiment 9 — The gradient versus Timm's writing-order model

**What was locatable.** Timm's 2014 analysis (arXiv:1407.6639, 96 pp.) publishes no per-folio chronology; it publishes a *model* with three testable commitments. From the vocabulary asymmetry between the dialects he concludes that "the pages using Currier B were written after the pages in Currier A"; he reports that words of intermediate frequency recur on subsequent sheets far more often than on the two sides of one leaf (37 vs 5 instances), implying the scribe copied preferentially from the last completed sheet; and he argues that cumulative copy-and-modify changed the text's character over time, with Currier B more repetitive than A and the biological section the most monotonous. A structural caveat applies to any order-based test: bifolios are known to have been rebound, so the surviving page sequence is not the original one. Experiment 9 therefore tests the model's predictions, not a sequence. Pre-specified: (T1) folio repetitiveness correlates with the gradient coordinate, ρ ≥ +0.6 globally and positive within B; (T2) within-section binding-order correlations stay weak (|ρ| < 0.4); (T3, no new computation) the transfer matrix is time-asymmetric in the forward-copying direction.

**T1 — partially falsified, and sharpened.** Metric: 1 − (types/60) over each folio's first 60 paragraph words (length-bias-free). Globally ρ = **+0.053** — the ≥ +0.6 prediction fails. But within Currier B, ρ = **+0.475** (n = 79): repetitiveness climbs the gradient continuously toward the Biological pole — Timm's monotony claim recovered as a *within-dialect continuum* rather than an A/B dichotomy. Within Currier A, ρ = **−0.212** (n = 102). The global null is a rising limb averaged with a flat-to-falling one: word-level monotony growth is a Currier-B phenomenon *riding* the register axis, not the axis itself. This also corrects our own earlier shorthand that "compressibility tracks the gradient": glyph-level h2 does; 60-word lexical diversity, on the A side, does not.

**T2 — confirmed.** Per-section Spearman between binding position and folio coordinate: Herbal-A +0.215, Herbal-B −0.011, Stars-B −0.071, Biological-B −0.121, Pharma-A −0.321 — all sub-threshold. Adjacent folios differ nearly as much as distant ones inside a section (distance-decay 0.82–1.47×, against the ~2.6× separation of the section plateaus). The drift lives between sections; any finer original-order signal, if it existed, is invisible in the current binding — exactly what the rebinding caveat predicts.

**T3 — confirmed.** The transfer matrix is time-asymmetric in the forward-copying direction: Biological-B's inventory reconstructs Herbal-A text at only 44–48%, while Herbal-A's reconstructs Biological-B at 60–62% (and across the dialect boundary in the scribe matrix, B-side inventories recover A-text at ~78% versus ~73% reversed). The process accumulated new machinery while losing old — the extreme pole can no longer represent o-attachment text — so pure-additive drift is rejected in favour of **drift-with-forgetting**, the signature of iterative copy-and-modify.

**Synthesis.** The register gradient is compatible with the self-citation-drift picture at every point where that picture makes a quantitative commitment; it contributes a coordinate that turns "changes over time" into a measurement; and it localizes Timm's monotony growth to Currier B. It remains agnostic on his meaninglessness thesis: Experiment 1's control showed these statistics cannot distinguish cipher from gibberish in either direction.

---

## 12. Experiment 10 — Robustness: a third parse and alternate search paths

Two objections could deflate the programme: that the machinery gap is an artifact of the EVA transliteration, or of greedy hill-climbing following one path. Experiment 10 attacks both. Pre-specified: (i) under v101 the A/B recovery lands 70–85% both directions; (ii) under stochastic restarts, recovery central tendency stays within ±3 points of greedy and no path collapses into the low-recovery regime.

**A third, independent parse (v101).** The v101 alphabet encodes Voynichese completely differently from EVA — a large single-character inventory in which digits and punctuation are glyph codes and ligatures are segmented on different principles. Matching v101 folios to their Currier language (194 folios; A = 9,490 words, B = 21,368 subsampled to match) and rerunning the A/B transfer from scratch: baselines differ (A h2 = 2.770, B = 2.498 — v101 is coarser, like the Minimal parse), and the first merges again diverge — A opens `oe am 1o oh` (o-attachment), B opens `89 1c 4o … 4oh`. Since v101 code `4` is the q-gallows, **B independently rebuilds the q-gallows attachment (`4o`, `4oh`) that EVA rendered `qo`, `qok`** — the same signature through a different encoding. Cross-dialect recovery: **A←B 77.2%, B←A 77.7%.** Three transliteration philosophies now agree — EVA-Maximal 77–80%, EVA-Minimal 76.7/80.6%, v101 77.2/77.7% — so the gap is parse-invariant. **(i) confirmed.**

**Alternate search paths.** Making the search stochastic — at each step sampling uniformly among the top-3 entropy-improving candidates rather than the argmax — over 5 seeds per dialect on the EVA corpus: A←B mean 78.4% (sd 5.2), B←A mean 78.9% (sd 5.6), against deterministic 76.6 / 77.2%. Every stochastic path stays in the high-recovery regime — the worst restart (71.3%) is still far above the 44–48% that genuinely different machinery produces (Biological-B ↔ Herbal-A) — so the A/B similarity is not a fragile property of one path; the ~5-point path noise is dwarfed by the effect. Inventory-wise the structural core is path-invariant while the tail wanders: restarts share ~13/17 first-17 tokens with the deterministic inventory (A 13.4, B 13.0) and ~11–12/17 with each other — roughly the first dozen merges are forced, the last few are near-tied alternatives. **(ii) confirmed** for central tendency and non-collapse (with the honest caveat of ~5-point single-path sd and a ~4-token tail).

**Verdict.** The machinery gap — and the gradient built from it — is neither an EVA artifact nor a greedy artifact. Real regime differences of 20–56 points sit an order of magnitude above the parse and path noise of a few points.

---

## 13. Experiment 11 — One knob: a generative model of the gradient

The constructive test of a one-dimensional gradient is whether a single parameter can *generate* it. Fit character-level transition distributions (word boundaries included) to the two poles — Herbal-A (P_A) and Biological-B (P_B) — set P_θ = (1−θ)P_A + θP_B, generate a corpus at each θ, and score it with the Experiment-7 instrument (global inventory, projection onto the pole axis). The decisive test is not that θ moves the coordinate — a 1-D dial trivially traces a 1-D curve — but whether the **real sections lie on that curve** in a space of two partly-independent statistics, coordinate and h2. Pre-specified: (P1) mixing raises entropy, so h2(θ) bulges above the endpoint-interpolation line mid-range; (P2) real intermediate sections therefore sit *below* the generative h2 curve (coherent regimes, not blends); (P3) generated coordinate is monotonic in θ and spans ~[0,1].

**P1 confirmed.** h2(θ) rises from 2.10 (θ=0) to a peak 2.135 (θ=0.2) before falling to 1.81 (θ=1) — non-monotonic, above the endpoint line at every interior θ by up to 0.09 bits. Linear blending of two regimes does not trace a monotonic entropy ramp; the mixture-entropy hump is real.

**P2 falsified — and the falsification is the finding.** Residuals (real h2 minus generator h2 at the same coordinate) are small and mixed-sign: Herbal-A +0.002, Pharma-A −0.033, Cosmo-B −0.078, Herbal-B +0.029, Stars-B +0.018, Bio-B −0.012 (mean intermediate −0.016). The real sections lie essentially **on** the one-parameter curve, within ±0.08 bits — not systematically below it. The real data is itself non-monotonic in h2-vs-coordinate: real Herbal-B (h2 = 2.098 at coord +0.41) nearly matches real Herbal-A (2.101 at +0.00), mirroring the generative hump. On these two statistics the manuscript's mid-gradient is **indistinguishable from a two-pole blend** — one dial matches it to ±0.08 bits. This bounds what coordinate and h2 can resolve; it is emphatically *not* a claim that the interior text *is* a blend, nor that a bigram model explains the manuscript. Any regime-vs-blend distinction evidently lives in statistics beyond these two — see P3.

**P3 half-confirmed, and the failure is diagnostic.** Generated coordinate is monotonic in θ but spans only [+0.02, +0.79]: at θ=1 (pure P_B) generated text reaches +0.79, not the real Biological pole's +1.00 — the pole is beyond the memoryless model's reach. A follow-up says why: real Bio-B repeats whole words far more than a bigram chain fit to it reproduces (type/token repetition **0.719 vs 0.612**), and that repetition drives the coordinate-defining tokens (the qokedy-type words). **The pole's extremity is a memory effect** — whole-word self-copying — outside any bigram model.

**Synthesis.** To be explicit about scope: this result concerns two summary statistics — the projection coordinate and h2 — not the manuscript text itself. A **first-order (bigram) mixing model** reproduces the gradient's *interior in the (coordinate, h2) projection* — real sections lie on the one-parameter curve to ±0.08 bits — but cannot manufacture the extreme *pole*, which is built by whole-word repetition. So within these two statistics the middle is blend-like; the endpoint demands a memory process. This does not adjudicate meaning (Experiment 1 showed these statistics cannot), and it does not claim the interior text is a two-pole mixture — only that coordinate and h2, the axes on which the gradient is defined, do not by themselves separate the two hypotheses in the mid-range. What the model *does* pin down is where a memoryless account fails: the pole. That failure unifies the arc — Experiment 1's self-copying control, Experiment 9's drift-with-forgetting (T3), and Experiment 11's pole-as-memory all point to the same supra-bigram self-citation mechanism generating the most extreme regime, consistent with Timm's proposal and here localized to the pole and quantified.

---

## 14. Experiment 12 — Labels: the one probe aimed at interpretation

Every prior experiment used only running paragraph text. This one uses its complement — the ~4,800 label, legend and circular-band tokens (placements L/R/S/C…) filtered out throughout — because a label is anchored to a drawn object, the closest thing the manuscript offers to a bilingual crib. If label *form* tracks the depicted *thing*, that is a structural bridge toward meaning. Pre-specified: (H1) labels share their section's running-text machinery; (H2) within a fixed dialect (controlling register), label morphology separates by referent-category more than a permutation null; (H0) labels are undifferentiated. Referent-category correlates with dialect (plants = A, nymphs/cosmological = B), so the clean H2 test runs *within* dialect B (Bio / Cosmo / Stars) and *within* dialect A (Pharma / Herbal / Text); the star-vs-plant contrast is dialect-confounded and reported descriptively only. Instrument: the Experiment-7 coordinate (works on small samples) plus initial/final-glyph distributions and word length; distances are total variation (TV); nulls are permutations that reshuffle referent tags at fixed group sizes (2000 draws).

**H1 falsified — labels are a distinct register.** In every section the label coordinate differs from the paragraph coordinate, with large initial-glyph TV (0.14–0.33), and the shift is directional: labels sit systematically *toward the o-attachment (Herbal-A) pole* relative to their own section's running text — Pharma labels +0.01 vs paragraph +0.25, Cosmo −0.03 vs +0.26, Bio +0.75 vs +1.00. Labels are not their section's prose in miniature; they are a partially separate register, consistently pulled toward the A-pole. This quantifies the long-noted distinctiveness of Voynich "label lines".

**H2 confirmed statistically, but the separation is register, not evidently referent.** Within dialect B, label sets separate by section far above chance (between-referent initial-glyph TV = 0.257, null 0.086, p = 0.0005) and more than paragraphs do (0.186); within dialect A the gap is starker (labels 0.355 vs paragraphs 0.120, both p = 0.0005). So labels carry significant between-section structure — more than running text. But this is the register axis re-expressed, not semantic naming: the B-dialect label separation runs along the *same* pole axis as the paragraph gradient (Bio labels near the B-pole at +0.75, Cosmo labels near the A-pole at −0.03, mirroring their sections' running-text order).

**The marquee contrast is null — the interpretation-relevant negative.** Star-labels (Zodiac + Astro, n = 1998) and plant-labels (Herbal + Pharma, n = 336) — annotating utterly different things — are nearly identical: gradient coordinate +0.01 vs −0.00, both beginning with `o` 43% of the time, initial-glyph TV just 0.154. A semantic naming system would make star-names and plant-names look *different*, as they do in any real language; instead they are drawn from a common morphological mould. (Dialect-confounded, hence descriptive — but a confound cannot manufacture *similarity* across a referent gap this large.)

**Verdict for interpretation.** Under these morphology tests, the best crib candidate in the manuscript does not separate like referent-naming. Labels are structurally distinct from prose (a real finding) and separate by section along the register axis, but words attached to stars and words attached to plants are morphologically near-identical — the opposite of a naming system, and consistent with the generative-artifact reading of Experiments 1, 9 and 11. This is the nearest the whole programme reaches toward meaning, and it points, mildly, *away* from readability rather than toward a decipherment. It does not prove meaninglessness — labels could encode referents in a way these features miss — but the simplest reading of the label evidence is register, not names.

---

## 15. Experiment 13 — Synthetic controls: is the gradient distinctive?

Does any structured text yield the 84%-one-axis gradient, or is it distinctive? Four synthetic corpora were pushed through the *identical* map pipeline (up to 12 units × 2,000 words, pairwise k=17 recovery, symmetrised, classical-MDS axis-1 %, minimum pairwise similarity as spread). Experiment 13 uses a separate 10-unit real benchmark matched to the synthetic-control construction (some units fell short of the length cutoff), so its 88.1% axis-1 value is *not* the same map as Experiment 6's 13-unit 84.1% result — the two are different constructions and should not be compared directly. Pre-specified: (1) a random-bigram null shows no gradient; (2) a section-mixture bigram reproduces one (gradient largely first-order); (3) self-copying with drift produces a 1-D gradient; (4) verbose-ciphered Latin+Italian shows a register structure.

| corpus | axis-1 % | min-sim % | h2 range |
|---|---|---|---|
| REAL manuscript | 88.1 | 48.7 | 1.74–2.13 |
| random bigram (one whole-MS model) | 41.7 | 98.5 | 2.06–2.12 |
| section-mixture bigram | 74.1 | 67.8 | 1.78–2.17 |
| self-copying + drift (Timm-lite) | 65.2 | 94.8 | 2.44–3.62 |
| verbose-ciphered Latin + Italian | 88.2 | 80.4 | 2.90–3.08 |

**The pipeline does not manufacture gradients.** The random-bigram null — twelve units from one shared model — yields near-uniform recovery (min-similarity 98.5%) and no dominant axis (42%). The manuscript's 88% is a property of the data, not the method.

**But a one-axis gradient is not by itself diagnostic.** Both a *meaningless* section-mixture bigram (74%) and *meaningful* verbose-ciphered Latin+Italian (88%, the Latin/Italian split as the dominant axis) reproduce a dominant-axis gradient. "There is a 1-D gradient" therefore signals neither meaning nor its absence.

**What is distinctive is the combination with low entropy.** Only the section-mixture bigram reproduces both the gradient *and* the manuscript's anomalously low conditional entropy (h2 1.78–2.17 vs real 1.74–2.13) — and it does so trivially, being fit to the real, already-low-entropy sections. The verbose cipher (h2 2.90–3.08) and the crude self-copying control (2.44–3.62) both come out far too high-entropy. (The self-copying control uses random-substitution mutation, which *raises* entropy; a faithful Timm–Schinner generator, which modifies text while preserving low entropy, remains the right tool and is still un-built — this experiment re-motivates it.)

**Reading.** The gradient is real (the null passes) but reproducible by both meaningful and meaningless structured processes, and largely a first-order per-section phenomenon; the low-entropy anomaly, not the gradient, is the manuscript's distinctive feature — and it is reproduced by a meaningless bigram mixture. This deflates the gradient as evidence about meaning while leaving the structural finding intact.

---

## 16. Experiment 14 — Leave-one-section-out: is anything baked in?

The coordinate uses the manuscript's own sections to build the instrument and the pole axis. Are Pharma-at-the-midpoint and the Biological pole artifacts of self-definition? For each non-pole section the inventory was rebuilt on the manuscript *minus that section* and the section reprojected; for the pole sections the pole centroid was defined from one half and the other half projected.

| section | in-sample | leave-one-out | Δ | test |
|---|---|---|---|---|
| Pharma | +0.25 | +0.27 | +0.02 | inventory rebuilt without Pharma |
| Cosmo | +0.26 | +0.26 | −0.00 | inventory rebuilt without Cosmo |
| Stars | +0.48 | +0.46 | −0.02 | inventory rebuilt without Stars |
| Herbal (A-pole) | +0.00 | +0.17 | +0.17 | pole from one half, project the other |
| Bio (B-pole) | +1.00 | +0.95 | −0.05 | pole from one half, project the other |

Non-pole sections are essentially unchanged out-of-sample (|Δ| ≤ 0.02): **Pharma stays mid-gradient at +0.27 when the instrument never sees it**, so its midpoint is not baked in. The Biological pole is robust (held-out half +0.95). The A-pole half moves most (+0.17) — the exact zero is partly self-defined — but the held-out Herbal half still sits at the extreme A-end, far below every other section. The gradient and its anomalies survive out-of-sample construction.

---

## 17. Experiment 15 — Shuffle nulls: what carries the gradient?

Two shuffles separate the possible sources of the signal, each rerun through the 12×12 map.

| condition | axis-1 % | min-sim % |
|---|---|---|
| real (unshuffled) | 88.1 | 48.7 |
| word-order shuffled within units | 88.1 | 48.7 |
| glyph-shuffled (word lengths + unigram frequency preserved) | 74.0 | 45.2 |

**Word order contributes nothing.** Shuffling word order within each unit leaves the map *identical* (88.1 / 48.7) — because the transfer metric merges only within words, it is a pure function of the word multiset. The gradient is not a sentence- or word-sequence phenomenon.

**Most of the gradient is glyph-frequency and word-length; a minority is genuine within-word sequence.** Destroying within-word glyph order while preserving each section's glyph frequencies and word lengths drops the dominant axis from 88% to 74% — without collapsing it. So ~74 of the 88 points are carried by *which glyphs each section uses and how long its words are*, and ~14 points by genuine within-word sequential structure (the "machinery" proper). This 74% matches the section-mixture bigram of Experiment 13, triangulating the same decomposition: the gradient is dominated by lower-order per-section differences, with a real but secondary sequential component. Inventory transfer is thus sensitive to both low-order section composition and within-word sequential structure; the shuffle controls show the dominant gradient is largely *compositional* (glyph frequency + word length), with a smaller but non-zero sequential component. **Terminology.** Accordingly this note reserves *machinery* for the merge-inventory and within-word-sequence effects, describes the headline result as a *structural / register gradient*, and calls the method *merge-transfer similarity*; where "machinery gap" appears for Currier A/B it refers specifically to the divergent merge inventories, which are a genuine within-word-sequence effect.

---

## 18. Experiment 16 — A faithful-in-mechanism self-copying generator

Experiment 13's crude self-copying control raised entropy (h2 2.4–3.6) and so could not test whether *structured* self-copying reproduces the manuscript's low-entropy gradient. This generator is faithful in mechanism (not in Timm–Schinner's exact unpublished table): whole-word copying from the last 600 words, with mutations confined to *attested* Voynich similarity classes (k↔t, p↔f, ch↔sh, o↔a, e↔ee, i-run ±1, y↔dy↔edy, q-prefix add/drop, final r↔s), a drift parameter θ biasing direction as the real gradient runs (o-attachment early → e-cascade / q-prefix late), and verbatim-copy probability rising 0.10→0.35 with θ (the memory effect Experiment 11 demanded). Parameters were fixed before running (seed = 300 real Herbal-A words; 12 × 2,000 words; seed 1404); the four criteria were pre-specified and no tuning followed.

| criterion | prediction | result |
|---|---|---|
| (i) unit h2 in low band [1.6, 2.3] | stays low (crude control failed high) | **regime met**: 1.95 → 1.10, brackets real Bio-B (1.74), overshoots below |
| (ii) map axis-1 ≥ 70%, min-sim ≪ 98% | reproduces a gradient | **met**: axis-1 88.7%, min-sim 18% |
| (iii) real-instrument coordinate → ≥ +0.6 | traverses the pole | **failed**: drifts −0.16 → +0.12 only |
| (iv) late repetition ≈ real Bio-B (0.68) | rises to the pole's | **overshoots**: 0.90 |

The decisive result is (i)+(ii): **structured self-copying reproduces the manuscript's defining signatures — anomalously low conditional entropy together with a strong one-axis gradient** — which the crude random-mutation control could not. This answers the question Experiment 13 left open in the affirmative: a meaningless self-copying process can generate the low-entropy gradient. But (iii)+(iv) show it reproduces the *phenomenology*, not this manuscript: on the real Herbal-A→Bio-B instrument the drift reaches only +0.12 (its mutations do not push token frequencies onto the real Bio-B axis), and it over-copies at high drift (repetition 0.90 vs 0.68). A generator calibrated to the real axis is a further step; the mechanism-level point — self-copying suffices for the key statistics — is made.

---

## 19. Experiment 17 — Beam-search robustness

To test whether the A/B machinery gap is an artifact of greedy hill-climbing, the search was rerun as a beam search (widths 5 and 10; duplicate merge-sets pruned), taking the best final inventory per dialect.

| search | A ← B | B ← A |
|---|---|---|
| greedy | 76.6% | 77.2% |
| beam width 5 | 80.7% | 81.0% |
| beam width 10 | 80.6% | 81.0% |

Beam search finds slightly better inventories that recover a few points *more* (~81% vs ~77%) — consistent with the stochastic restarts of Experiment 10 — but the gap is stable and far from 100%: even the optimum-seeking beam leaves ~19% dialect-specific machinery. The A/B difference is not a greedy artifact.

---

## 20. Experiment 18 — Cross-transcriber replication

Every prior number uses Takahashi's ("H") transliteration. The interlinear file also carries independent transliterations by other transcribers; the A/B recovery was rerun on the two largest.

| transcriber | n (matched) | A ← B | B ← A |
|---|---|---|---|
| Takahashi (H) | 11,077 | 76.6% | 77.2% |
| Friedman-group (F) | 10,476 | 70.1% | 82.1% |
| (C) | 7,267 | 68.2% | 68.6% |

Two independent transcriptions reproduce the A/B machinery gap in the 68–82% band, bracketing Takahashi's 77%. The gap is not an artifact of one transcriber's fine-grained glyph decisions — it survives independent reading of the manuscript. (The modest spread is expected, since each transcriber made different segmentation choices.)

---

## 21. Experiment 19 — Richer label morphology (revising Experiment 12)

Experiment 12's marquee null used only the initial and final glyph. This test uses 2–3-gram prefix and suffix *templates*, where referent names — if present — might hide.

Star-labels vs plant-labels, total-variation distance: **suffix-2gram 0.278, suffix-3gram 0.284, prefix-2gram 0.254, prefix-3gram 0.326** — all well above the initial-glyph 0.154 of Experiment 12. Within dialect B (Bio / Cosmo / Stars: same register, different referent), between-referent suffix separation is significant against a permutation null: **suffix-2gram obs 0.383 vs null 0.173, p = 0.0005; suffix-3gram obs 0.538 vs null 0.316, p = 0.0005.**

So richer morphology **revises the strong negative of Experiment 12**: labels are *not* featureless across referents — endings and templates separate star from plant, and referent-categories within a dialect, significantly. But the *pattern* is the register axis, not evident naming: the separating n-grams are the e-vs-o contrast that defines Currier A/B (star endings lean to -e- forms — che, oke, eey, edy — plant endings to -o- forms — cho, oko, ory, ody). The label separation is real but still plausibly register rather than referent-semantics. Net: the interpretation question is *reopened, not resolved* — there is more structure in label endings than the coarse test found, but it looks like the same machinery gradient, not a naming system.

---

## 22. Experiment 20 — Calibrating the self-copying generator to the pole

Experiment 16 reproduced the low-entropy gradient *regime* but drifted only to +0.12 on the real axis. This experiment fits the mutation *directions* to the measured Herbal-A→Bio-B glyph-feature shift (Bio-B has more q-initial words, 0.25 vs 0.09; more -edy endings, 0.26 vs 0.04; more `ee`, 0.14 vs 0.06; `che` over `cho`) and pushes the generator toward the pole, keeping mutations strictly local and copying strictly from the generator's own output (no injected real words — that would be circular). Pre-specified criteria, no tuning after seeing results: (i) h2 in [1.6, 2.3]; (ii) axis-1 ≥ 70%; (iii) real-instrument coordinate ≥ +0.8; (iv) repetition in [0.5, 0.8]; (v) top-token overlap with real Bio-B ≥ 3/20.

| criterion | result |
|---|---|
| (i) h2 in band | **failed** — 0.89–1.92 (over-copies below the floor) |
| (ii) axis-1 ≥ 70% | **met** — 80.7% |
| (iii) coordinate ≥ +0.8 | **failed** — reaches +0.76 and plateaus (real pole +1.03) |
| (iv) repetition in band | **failed** — 0.99 (over-copies) |
| (v) token overlap ≥ 3/20 | **failed** — 1/20 |

The calibration fails, and the failure is the finding. Directed local self-copying reaches the pole's *statistical neighborhood* — coordinate +0.76, anomalously low entropy — but no further, and the words it generates there are *malformed*: piling the measured features onto arbitrary stems yields monstrosities like `qcheeetedy` and `otcheeel`, not Bio-B's coherent vocabulary (`qokedy`, `qokeedy`, `chedy`, `shedy`), which overlaps the generated top-20 in only one word. Real Voynich words obey a rigid internal template (a q–gallows–e–d–y slot structure) that independent local mutations violate. So the Biological pole's extremity requires *coherent word-template structure that directed local self-copying does not manufacture*.

This partially rehabilitates the reading that the pole carries structure beyond simple drift: any self-copying account of the manuscript must incorporate a word-template grammar — closer to Zattera's slot grammar than to random self-citation. With Experiment 16 (which reached the regime but not the axis), the two bracket the claim: **self-copying reproduces the manuscript's *phenomenology* but not its *vocabulary*, and the pole is the locus of the residual structure.**

---

## 23. Prediction ledger

| Prediction (pre-specified before each run) | Outcome |
|---|---|
| Exp 2: A/B early merges nearly identical; divergence only in vocabulary tail | **Falsified** — divergence at move 1; ~20% structural residue constant across depth |
| Exp 2: tail exclusives sort by dialect vocabulary | Confirmed |
| Exp 3: within-B across-scribe ≈ ceiling; across-dialect replicates 75–80% | Confirmed (94.2 / 98.7 / 75.5) |
| Exp 3: hand 1 = A signature; hands 4–5 left open | Confirmed; hand 4 → lexically A (contradicting the printed 2020 assignment); hand 5 → B |
| Exp 4: Herbal-A↔Herbal-B ≈ 75–80% (dialect survives topic control) | **Confirmed** (79.7%) |
| Exp 4: same-dialect cross-topic ≥ 90% | **Falsified** — range 80.7–97.8; B is a family, not a machine; Biological-B extreme |
| Exp 5: Minimal parse reproduces the A/B gap within a few points | Confirmed (76.7 / 80.6) |
| Exp 6: one dominant MDS axis | **Confirmed** (84.1% vs 8.2%) |
| Exp 6: ordering HA/PA → HB → SB → BB | Mostly confirmed; HB embeds in SB; PA at the center (both replicated on alternate windows) |
| Exp 6: clumpy no-axis outcome would kill the drift reading | Not observed |
| Exp 7: per-folio projection validates against the map (r > 0.9) | **Confirmed** (r = 0.938); Pharma central and Herbal-B up-gradient folio-by-folio |
| Exp 8: section ≫ scribe in unique variance; regime not penmanship | **Confirmed** — unique R² 0.235 (section) vs 0.010 (scribe); Scribe 2 personally reaches the pole |
| Exp 9 (T1): repetitiveness vs coordinate ρ ≥ +0.6 globally, positive within B | **Global falsified** (+0.053); **within-B confirmed** (+0.475); within-A −0.212 — monotony growth is a Currier-B continuum |
| Exp 9 (T2): within-section binding-order drift weak (\|ρ\| < 0.4) | Confirmed (−0.32 to +0.22; distance-decay 0.82–1.47×) |
| Exp 9 (T3): transfer asymmetry consistent with forward copying | Confirmed (BB→HA 44–48% vs HA→BB 60–62%); pure-additive drift rejected |
| Exp 10 (v101): A/B recovery replicates in a third parse, 70–85% | **Confirmed** (77.2 / 77.7%); B rebuilds the q-gallows independently |
| Exp 10 (restarts): recovery within ±3 of greedy; no path collapses | Central tendency confirmed (78.4/78.9 vs 76.6/77.2, sd ~5); core inventory ~13/17 stable, tail wanders |
| Exp 11 (P1): h2(θ) humps above the endpoint line (mixture entropy) | **Confirmed** (peak 2.135 at θ=0.2 vs line 2.042) |
| Exp 11 (P2): real sections lie below the blend curve (coherent, not blend) | **Falsified** — residuals ±0.08, mean −0.016; sections lie *on* the curve; mid-gradient is blend-like *in the (coord, h2) projection only* |
| Exp 11 (P3): generated coordinate monotonic and spans [0,1] | Monotonic yes; range only [+0.02, +0.79] — memoryless model cannot reach the Bio pole |
| Exp 11 (follow-up): pole extremity is a repetition/memory effect | **Confirmed** (real type/token 0.719 vs generated 0.612) |
| Exp 12 (H1): labels share their section's running-text machinery | **Falsified** — labels are a distinct register, pulled toward the A-pole (initial-glyph TV 0.14–0.33) |
| Exp 12 (H2): within-dialect labels separate by referent beyond a null | Confirmed statistically (p = 0.0005, labels > paragraphs) but the axis is register, not referent |
| Exp 12 (marquee): star-labels vs plant-labels differ (naming) | **Null** — coord +0.01 vs −0.00, TV 0.154; under these morphology tests, labels do not separate like referent-names |
| Exp 13: gradient distinctive vs synthetic controls | Null passes (random-bigram 42% / 98.5%, no gradient); but section-mixture (74%) and verbose-Latin (88%) also yield gradients — not diagnostic; only the mixture matches low entropy |
| Exp 14: Pharma-midpoint / poles are baked in | **Refuted** — Pharma +0.27 out-of-sample (vs +0.25); Bio pole +0.95 held-out; non-pole \|Δ\| ≤ 0.02 |
| Exp 15: the gradient is word-order structure | **Refuted** — word-order shuffle identical; ~74 of 88 axis points are glyph-frequency + word-length, ~14 genuine within-word sequence |
| Exp 16: structured self-copying reproduces the low-entropy gradient | **Yes** on entropy+gradient (h2 1.1–1.9, axis-1 88.7%) — the answer Exp 13 lacked; overshoots repetition; real-axis drift only +0.12 (phenomenology, not this manuscript) |
| Exp 17: A/B gap is a greedy artifact | **Refuted** — beam-5/10 give 80.7/81.0%, stable, far from 100% |
| Exp 18: A/B gap is a transcription artifact | **Refuted** — holds on 2 independent transcribers (70/82%, 68/68% vs 77/77%) |
| Exp 19: labels do not separate by referent (Exp-12 revisited) | **Partly revised** — n-gram templates separate star/plant (TV 0.25–0.33) and within-dialect (p=0.0005), but the pattern is the e-vs-o register axis, not evident naming |
| Exp 20: calibrated self-copying reaches the pole | **Failed informatively** — reaches coord +0.76 / low entropy but generates malformed pole words (overlap 1/20), stalls short of +1.03; the pole needs coherent word-template structure beyond directed local self-copying |

---

## 24. Limitations

Greedy hill-climbing explores one path; discovered token *sets* are order-sensitive, so raw overlaps overstate divergence — the transfer/recovery numbers are the robust metric. The objective is h2-only; matching h2 demonstrably breaks h1 and word length. Merges never cross spaces (the analysis trusts the manuscript's word divisions). Three parse lineages tested (Maximal-Simplified, Minimal, v101 — Exp 10). Unit sizes of 3,400 and 2,000 words carry finite-sample bias; matched sizes keep comparisons fair, split-half ceilings (98.5–98.7%) bound the noise, and the two headline anomalies (Pharma-A central; Herbal-B in the SB cloud) were replicated on disjoint windows — but Pharma-A rests on ~2,300 words total. Within-section scrambling in the seriation may reflect true plateau structure or unit-level noise; folio-resolution methods are needed to distinguish. Section and language labels come from the interlinear metadata; Currier left some pages unclassified, and the Pharma-A anomaly may partly interrogate the label itself. The causal nature of the latent axis (time of writing, register, scribe mixture, drifting generation parameter) is undetermined by these data. The Experiment-1 control is order-1 Markov; a fully faithful Timm–Schinner generator remains unavailable because the exact modification table is not published or reconstructed here — Experiments 16 and 20 are mechanism-level analogues, not exact reproductions. Small cells (Cosmo-B, Text-A/B, Currier-unclassified) are unmapped. The folio estimator (Exp 7) is a linear projection onto a single axis, validated only against the 13-unit seriation (r = 0.938); it captures the dominant dimension by construction and discards the ~16% off-axis variance, and it omits folios below 60 words (several Pharma/Cosmo folios rest on ~100). The scribe decomposition (Exp 8) inherits the residual dialect/scribe confound: the A/B distinction itself remains inseparable from Scribe 1 vs the rest, so Exp 8 constrains only the finer within-dialect gradient. Finally, the located primary sources confirm that no per-folio chronology was ever published by Timm — his 2014 analysis yields a generative model, not a sequence — so Experiment 9 tests that model's predictions rather than an ordering, and inherits the rebinding caveat that the surviving page sequence is not the original. T1's repetitiveness measure is one operationalization (60-word type–token); alternatives may behave differently. The remaining genuinely external need is a codicological reconstruction of the original gathering order (quire marks, ink and pigment sequencing, bifolio analyses), against which the folio coordinate could finally be read as a chronology. Two robustness caveats from Experiment 10: stochastic restarts show ~5-point recovery sd, so any single reported recovery figure carries roughly that path uncertainty (the means are stable and no path collapses), and the ~4-token inventory tail is near-tied and should not be over-interpreted; the v101 replication rests on one digital edition of that alphabet. Experiment 11's generator is a first-order (character-level bigram) Markov model; it cannot represent the supra-bigram word-repetition that defines the Biological pole, so its manifold test is informative only for the two statistics used (coordinate and h2) and understates the pole. Experiment 12's label sets are small (Herbal 71, Pharma 265 tokens) and "referent-category" is operationalized as section, which differs for reasons beyond the depicted object; the permutation tests establish that labels are non-randomly structured by section, not that they semantically name their referents. Only the coordinate, word length, and initial/final-glyph distributions were used; a deeper label analysis (label-internal repetition, position on the object, cross-folio label reuse, full n-gram morphology) could sharpen or overturn the null marquee result. The star-vs-plant contrast is dialect-confounded and reported descriptively; its value is that a confound cannot fabricate the observed near-identity across a large referent gap. Experiment 13's self-copying control uses random-substitution mutation and therefore *raises* entropy rather than lowering it; it is too crude to test whether structured self-copying reproduces the low-entropy gradient; Experiments 16 and 20 are the mechanism-level analogues that partly address this (Exp 16 reaches the low-entropy regime; Exp 20 shows the pole needs template structure). Its verbose-cipher control uses a hand-built homophonic table, an analog rather than a claim about the manuscript's construction. Experiments 13 and 15 jointly show the dominant axis is largely (~74 of 88 points) a first-order per-section phenomenon (glyph frequency + word length) with a secondary genuine within-word sequential component, so the "machinery" framing should be read with that decomposition in mind; and Experiment 13 shows a one-axis gradient is reproducible by both meaningful and meaningless processes, so the gradient constrains interpretation without deciding it. Experiment 16's generator is faithful in mechanism but not in Timm–Schinner's exact (unpublished) modification table, and its drift is uncalibrated (it overshoots repetition and does not traverse the real axis); it establishes that structured self-copying *can* produce the low-entropy gradient, not that it produced this manuscript. Experiment 18's alternative transcribers cover fewer folios and made different segmentation choices, so their recovery band is wider. Experiment 19 shows label endings carry significant referent/section structure, but it remains entangled with the register axis and does not isolate semantic naming; a within-dialect, within-register label contrast (unavailable at adequate sample size) would be needed to separate the two. Experiment 20's negative result depends on the mutation operators being local and feature-independent; a template-aware self-copying generator (respecting the slot grammar) might reach the pole — but building one concedes the central point, that the pole requires template structure beyond simple drift, and it is the natural next model. This version closes the current computational pass; further progress likely requires external replication, codicological evidence, and independent model-building — the remaining routes toward meaning (multispectral imaging, botanical and art-historical iconography, codicological gathering-order reconstruction) being off-platform.

---

## 25. Reproducibility

Corpus: `https://github.com/chirila/Voynich-public` (prepared partitions plus `Voynich_texts/interlinear_full_words.txt`; filters: transcriber H, placement P\*, lowercase, a–z words). Estimator: h1 = unigram entropy; h2 = bigram joint entropy − h1; space as symbol. Search: greedy, top-90 within-word pairs per step, argmax-h2. Depths: k = 17 (structural), 40 (full). Seeds: Markov control 1404; Exp-2 B subsample 1438 (stability 2026, 408); Exp-3 split-halves 1401–1403 (n = 5,000); Exp-4 corpora 2601–2604 (n = 3,400; bootstrap seed 7, 200 reps, 100-word blocks); Exp-5 seed 1438 (n = 11,077); Exp-6: thirteen contiguous 2,000-word chunks in manuscript order, no sampling; robustness windows: last-2,000-word slices of Pharma-A and Herbal-B. Experiment 7 uses a global 40-merge inventory over the whole manuscript; each folio (≥ 60 words) is a token relative-frequency vector projected onto the Herbal-A→Biological-B centroid difference, calibrated so the pole means are 0 and 1; validated against the Exp-6 Fiedler coordinates (r = 0.938). Experiment 8 joins each folio's modal Davis scribe (interlinear `d.hand` column) to that coordinate and runs a commonality decomposition via one-hot least squares. Experiment 9's repetitiveness metric is 1 − (types/60) over each folio's first 60 paragraph words; correlations are Spearman with tie-averaged ranks. Experiment 10 additionally requires the v101 transliteration (`git clone https://github.com/musyoku/voynich-transcription`); its stochastic search samples uniformly among the top-3 entropy-improving merges (seeds 100–104 for A, 200–204 for B). Experiment 11 fits character-level bigram transition matrices (add-0.1 smoothing) to Herbal-A and Biological-B, mixes them as (1−θ)P_A + θP_B, and generates 60,000-symbol corpora per θ (seeds 1400+10θ). Experiment 12 partitions tokens into paragraph (placement P) vs label (all other placements) per section, scores each set with the global-inventory coordinate, and compares initial/final-glyph distributions via total variation with a 2000-draw referent-tag permutation null (seed 408). Experiment 13 builds four synthetic corpora (random whole-MS bigram, per-section-mixture bigram, self-copying-with-drift, and a homophonic verbose cipher of Secreta Secretorum Latin + Rettorica Italian) and pushes each through the same 12×2,000-word map pipeline; Experiment 14 rebuilds the inventory/axis leaving each section out (pole sections via split-half); Experiment 15 reruns the map under word-order and glyph shuffles (seed 408). Experiment 16 runs the faithful-in-mechanism self-copying generator; Experiments 17–19 run beam search, cross-transcriber recovery, and richer label n-gram templates. Experiment 20 runs the calibrated self-copying generator. Seventeen scripts (the sixteen above plus `exp20_calibrated_generator.py`; Python 3 + NumPy only, relative paths, seeded) reproduce every number across the twenty experiments in this note, and each writes a `*_results.json`. They ship with a README and the result JSONs as a companion code package.

---

## 26. Selected references

- W. R. Bennett, *Scientific and Engineering Problem-Solving with the Computer* (1976).
- P. Currier, papers on the two "languages" (1976; reprinted in D'Imperio, ed.).
- M. D'Imperio, *The Voynich Manuscript: An Elegant Enigma* (NSA, 1978).
- D. Stallings, "Understanding the Second-Order Entropies of Voynich Text" (1998).
- N. Pelling, *The Curse of the Voynich* (2006).
- S. Reddy & K. Knight, "What we know about the Voynich manuscript" (ACL workshop, 2011).
- T. Timm, "How the Voynich Manuscript was created" (arXiv:1407.6639, 2014) — the sequential self-copying model and page-order evidence.
- T. Timm & A. Schinner, "A possible generating algorithm of the Voynich manuscript," *Cryptologia* (2019).
- L. F. Davis, "How Many Glyphs and How Many Scribes? Digital Paleography and the Voynich Manuscript," *Manuscript Studies* 5.1 (2020).
- L. Lindemann & C. Bowern, "Character Entropy in Modern and Historical Texts" (arXiv:2010.14697); C. Bowern & L. Lindemann, *Annual Review of Linguistics* 7 (2021).
- K. Gheuens, "Entropy Hunting," *The Voynich Temple* (2020).
- M. Zattera, slot-alphabet paper, International Conference on the Voynich Manuscript (2022).
- "Naibbe cipher" study, *Cryptologia* (2025).
- "A Quantitative Confirmation of the Currier Language Distinction" (arXiv:2604.25979, 2026).
- R. Zandbergen, *The Voynich Manuscript* (voynich.nu) — transliterations, entropy analyses, and per-folio hand/dialect/section tables.
