# Validation addendum — Experiments 21 & 21b: known-structure positive control

*Addendum to "Inventory-transfer analysis reveals a robust one-dimensional
structural gradient in Voynichese" (v11). Run 2026-07-11 on the pinned corpus
commit (`decc4caa…`), same estimator and protocol as Experiments 6/13
(2,000-word units, k=17 greedy merges, normalized recovery, classical MDS).*

## Why this experiment

Experiments 1–20 established that the metric behaves *consistently* on the
Voynich (robust to parses, transcribers, search strategy, holdout). What they
did not establish is **construct validity**: does merge-transfer similarity
recover *known* structure in texts whose internal divisions are independently
established? Without that, a critic can argue the dominant one-axis gradient
is something the metric produces on *any* real corpus. Experiments 21/21b
close that gap using the historical reference texts already packaged in the
pinned corpus.

## Design: a calibration ladder

Twelve 2,000-word units from six works of known identity and language:
Latin ×3 (*Secreta Secretorum* LAT, the Aix chronicle, *Picatrix*),
Italian ×1 (*Rettorica*), Middle English ×2 (*Secreta Secretorum* ENG,
*Alphabet of Tales*). Two units per work. Every unit pair falls in one tier:

- **T0** same work · **T1** same language, different work · **T2** different language.

*Secreta Secretorum* appears in both Latin and English — same **content**,
different **language** — isolating language from topic (the same confound the
Voynich sections present).

Pre-specified predictions: **P1** T0 ≥ 0.90 · **P2** T0 > T1 > T2 ·
**P3** T2 < 0.77 (the Voynich A↔B transfer, Exp 2) · **P4** the known
multi-language corpus shows cluster geometry (larger max-gap/range on MDS
axis-1) rather than the Voynich's filled gradient. 21b adds **P5/P6**: the
ladder ordering and P3 hold on a second, non-overlapping draw of units.

## Results — all six predictions pass

| tier | pairs | mean | min | max |
|---|---|---|---|---|
| T0 same work | 6 | **0.940** | 0.915 | 0.969 |
| T1 same language, different work | 16 | **0.578** | 0.379 | 0.890 |
| T2 different language | 44 | **0.333** | 0.155 | 0.484 |

Re-draw (21b): T0 = 0.898, T1 = 0.543, T2 = 0.338 — same ordering, same
placement. Topic control: *Secreta* Latin ↔ *Secreta* English = **0.277** —
same content, different language transfers *worse* than the different-language
average. Language/orthography dominates content in this metric.

Work-level matrix highlights (draw 0): LAT_SS↔LAT_AIX **0.842** (closest
same-language pair); LAT_PIC sits low within Latin (0.43–0.45), showing T1
spans a wide range depending on period/orthographic convention.

Geometry: the known corpus gives MDS axis-1 = **47.0%** with
max-gap/range = 0.362 (clusters); the Voynich real units give **88.1%** with
max-gap/range = 0.182 (one filled axis).

## What this establishes

1. **The metric measures what it claims.** It reproduces ground truth: same
   work ≈ 0.94, same language ≈ 0.58, different language ≈ 0.33, monotone,
   stable under re-draw. The ruler is calibrated.
2. **The one-axis gradient is not generic.** A genuinely multi-language corpus
   pushed through the identical pipeline yields 47% axis-1 and visible cluster
   gaps — not the Voynich's 88% filled axis. The Voynich geometry is a property
   of the manuscript, not of the method.
3. **The Currier A↔B gap is register-sized, not language-sized.** A↔B transfers
   at 0.77–0.80 — far above the different-language tier (0.33), above the
   same-language-different-work mean (0.58), and comparable to the *closest*
   pair of works within one language (0.842). On a calibrated ladder, A and B
   sit where two closely related registers of one writing system sit — not
   where two languages sit. This sharpens the note's central claim with an
   external yardstick.
4. **Topic does not drive the metric.** Same content in two languages scores
   0.277; different topics inside the Voynich score 0.77–0.95+. Whatever
   separates Voynich sections, it is not subject matter per se — consistent
   with Exp 4's within-manuscript topic control, now confirmed on known text.

## Honest caveats

- **Cross-writing-system comparison is indicative, not exact.** The ladder is
  calibrated on Latin-alphabet natural language; Voynichese is a different
  symbol system with different alphabet size. Normalized recovery mitigates
  but does not eliminate this; P3's placement should be read as
  "A↔B ≫ language-gap" rather than a precise rung.
- **T1 variance is large** (0.38–0.89). "Same language" is not one number —
  orthographic convention and period matter. Placement claims use the range.
- **Middle English orthography is itself unstandardized**, which likely
  depresses ENG↔ENG (0.589) relative to modern expectations; this makes the
  T1 tier conservative, which works against P3 rather than for it.
- Six works, three languages, one draw protocol. A fuller validation would add
  more languages (the corpus's Hebrew texts were excluded to keep a single
  script family) and register-controlled pairs within one language.

## Prediction ledger entries

| # | Prediction (pre-specified) | Outcome |
|---|---|---|
| P1 | Same-work recovery ≥ 0.90 | **PASS** (0.940) |
| P2 | Ladder monotone T0 > T1 > T2 | **PASS** (0.940 > 0.578 > 0.333) |
| P3 | Different-language < 0.77 (A↔B) | **PASS** (0.333) |
| P4 | Known corpus gappier than Voynich | **PASS** (0.362 > 0.182) |
| P5 | Ladder holds on re-draw | **PASS** (0.898 > 0.543 > 0.338) |
| P6 | Re-draw different-language < 0.77 | **PASS** (0.338) |

## Files

- `scripts/exp21_known_structure.py` → `results/exp21_results.json`
- `scripts/exp21b_ladder_robustness.py` → `results/exp21b_results.json`

Run from the repo root with the pinned corpora cloned (see `docs/DATA.md`).
