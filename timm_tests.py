import csv, json
import numpy as np
from collections import OrderedDict

allowed = set("abcdefghiklmnopqrstxyz")
G = json.load(open("folio_gradient.json"))
score, meta = G["folio_scores"], G["meta"]

folio_words = OrderedDict()
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"):
            continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if w and all(c in allowed for c in w):
            folio_words.setdefault(row["folio"], []).append(w)

def rank(a):
    a = np.asarray(a, float)
    order = np.argsort(a)
    r = np.empty(len(a)); r[order] = np.arange(len(a), dtype=float)
    for v in np.unique(a):
        m = a == v
        if m.sum() > 1: r[m] = r[m].mean()
    return r

def spearman(x, y):
    rx, ry = rank(x), rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])

fols = [f for f in folio_words if f in score]
coord = np.array([score[f] for f in fols])
rep = np.array([1 - len(set(folio_words[f][:60])) / 60 for f in fols])

print("T1  repetitiveness (1 - types/60 on first 60 words) vs gradient coordinate")
print(f"    all {len(fols)} folios: Spearman rho = {spearman(coord, rep):+.3f}")
Bmask = [i for i, f in enumerate(fols) if meta[f][1] == "B"]
print(f"    within Currier B only (n={len(Bmask)}): rho = {spearman(coord[Bmask], rep[Bmask]):+.3f}")
Amask = [i for i, f in enumerate(fols) if meta[f][1] == "A"]
print(f"    within Currier A only (n={len(Amask)}): rho = {spearman(coord[Amask], rep[Amask]):+.3f}")

print("\nT2  within-section binding order vs coordinate")
secs = {}
for i, f in enumerate(fols):
    secs.setdefault(tuple(meta[f]), []).append(i)
for key, idx in sorted(secs.items(), key=lambda kv: -len(kv[1])):
    if len(idx) < 15: continue
    pos = np.arange(len(idx), dtype=float)
    c = coord[idx]
    rho = spearman(pos, c)
    adj = np.mean(np.abs(np.diff(c)))
    allp = np.mean([abs(c[a] - c[b]) for a in range(len(c)) for b in range(a + 1, len(c))])
    print(f"    {key[0]}/{key[1]}  n={len(idx):3d}  rho(position,coord)={rho:+.3f}  adj|d|={adj:.3f} vs all-pairs|d|={allp:.3f}  decay={allp/adj:.2f}x")
