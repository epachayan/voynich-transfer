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
`voynich-transcription/...`), so they must sit alongside the `.py` files.
`.gitignore` keeps them out of version control.

## 2. Pinned commits (fill in before archiving)

`--depth 1` fetches the current HEAD of each upstream repo. If those repos
change, the reported numbers may drift. For an exact reproduction, pin the
commits the reported runs used:

```bash
# TODO: record the actual commit SHAs you ran against, e.g.
# cd Voynich-public && git checkout <SHA_A>
# cd voynich-transcription && git checkout <SHA_B>
```

> Record these once and paste them here. They are the only thing standing
> between "reproducible in principle" and "reproducible in fact."

## 3. Run

Python 3.10+ and NumPy (`pip install -r requirements.txt`). Then e.g.:

```bash
python verbose_search.py        # Experiment 1
python ab_search.py             # Experiment 2
python folio_gradient.py        # Experiment 7 (writes folio_gradient.json)
python scribe_decomposition.py  # Experiment 8 (consumes folio_gradient.json)
# ... see README.md for the full script -> experiment table and run order
```

Each script prints its results and writes a `*_results.json`. Compare against
the committed reference JSON of the same name.
