# Data setup and reproducibility

This repository contains **code and result artifacts only**. The Voynich
transliterations it analyses belong to their compilers and are fetched
separately.

## 1. Clone the corpora into the repo directory

From the repository root:

```bash
git clone --depth 1 https://github.com/chirila/Voynich-public
git clone --depth 1 https://github.com/musyoku/voynich-transcription   # only needed for Experiment 10 (v101 parse)
```

The scripts use **relative paths** (`Voynich-public/...`,
`voynich-transcription/...`), resolved against the **current working
directory**, not the script's own location — so clone the corpora into the
repo root and always run scripts from the repo root (e.g.
`python scripts/verbose_search.py`, not `cd scripts && python verbose_search.py`).
`.gitignore` keeps the cloned corpora out of version control.

## 2. Pinned commits

`--depth 1` fetches the current HEAD of each upstream repo. If those repos
change, the reported numbers may drift. To pin an exact snapshot:

```bash
cd Voynich-public && git checkout decc4caaa6515b86e42a219d1da8d81114736f2e && cd ..
cd voynich-transcription && git checkout 18117f968be1240cc6fec1d78fe303adcb33d8ad && cd ..
```

These are the upstream HEAD commits as of 2026-07-11 (`Voynich-public` last
updated 2024-06-04; `voynich-transcription` last updated 2016-12-28 — both
repos are dormant, so a shallow `--depth 1` clone today should already match
these SHAs). They were **not** independently re-verified against the exact
commits the original reported numbers in `RESEARCH_NOTE.md` were run
against; if you need byte-exact reproduction rather than a matching
snapshot, re-derive and confirm the SHAs yourself with `git rev-parse HEAD`
inside each clone before relying on this pin.

## 3. Run

Python 3.10+ and NumPy (`pip install -r requirements.txt`), run from the
**repository root**:

```bash
python scripts/verbose_search.py        # Experiment 1
python scripts/ab_search.py             # Experiment 2
python scripts/map_experiment.py        # Experiment 6 (writes results/map_results.json)
python scripts/folio_gradient.py        # Experiment 7 (reads map_results.json, writes results/folio_gradient.json)
python scripts/scribe_decomposition.py  # Experiment 8 (reads results/folio_gradient.json)
# ... see README.md for the full script -> experiment table and run order
```

Each script prints its results and writes a `*_results.json` into `results/`.
Compare against the committed reference JSON of the same name (restore it
with `git checkout -- results/<name>_results.json` if a local run overwrote
it). Some scripts read another script's output (e.g. `folio_gradient.py`
needs `results/map_results.json` from `map_experiment.py` first, and
`scribe_decomposition.py` / `timm_tests.py` need `results/folio_gradient.json`)
— see the run-order table in README.md.
