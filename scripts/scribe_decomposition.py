import csv, json
import numpy as np
from collections import Counter, defaultdict

fdh = defaultdict(Counter)
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H":
            continue
        fdh[row["folio"]][row["d.hand"]] += 1

G = json.load(open("results/folio_gradient.json"))
score = G["folio_scores"]
meta = G["meta"]
SEC = {"H": "Herbal", "P": "Pharma", "S": "Stars", "B": "Bio",
       "C": "Cosmo", "T": "Text", "A": "Astro", "Z": "Zodiac"}

def modal(counter):
    c = {k: v for k, v in counter.items() if k not in ("NA", "", "2, 3")}
    return max(c, key=c.get) if c else None

rows = []
for f in score:
    h = modal(fdh[f])
    if h is None:
        continue
    sec, lang = meta[f]
    rows.append((f, h, SEC.get(sec, sec), lang, score[f]))
print(f"folios with a Davis scribe + coordinate: {len(rows)}")

grid = defaultdict(list)
for f, h, sec, lang, s in rows:
    grid[(h, sec, lang)].append(s)
scribes = sorted(set(r[1] for r in rows))
combos = sorted(set((r[2], r[3]) for r in rows),
                key=lambda k: np.mean([r[4] for r in rows if (r[2], r[3]) == k]))

print("\nSCRIBE x (SECTION/dialect) mean coordinate (n):  [0=Herbal-A pole ... 1=Bio-B pole]")
print("          " + "".join(f"{s+'/'+l:>12}" for s, l in combos))
for h in scribes:
    line = f"scribe {h}: "
    for s, l in combos:
        v = grid.get((h, s, l))
        line += f"{(f'{np.mean(v):+.2f}({len(v)})' if v else '.'):>12}"
    print(line)

print("\nWITHIN-SCRIBE across sections (>=3 folios/cell):")
for h in scribes:
    cells = {(s, l): grid[(h, s, l)] for s, l in combos if len(grid.get((h, s, l), [])) >= 3}
    if len(cells) >= 2:
        parts = "  ".join(f"{s}/{l} {np.mean(v):+.2f}" for (s, l), v in cells.items())
        span = max(np.mean(v) for v in cells.values()) - min(np.mean(v) for v in cells.values())
        print(f"  scribe {h}: {parts}  -> span {span:.2f}")

print("\nWITHIN-(section/dialect) across scribes (>=3 folios/cell):")
for s, l in combos:
    cells = {h: grid[(h, s, l)] for h in scribes if len(grid.get((h, s, l), [])) >= 3}
    if len(cells) >= 2:
        parts = "  ".join(f"sc{h} {np.mean(v):+.2f}" for h, v in cells.items())
        span = max(np.mean(v) for v in cells.values()) - min(np.mean(v) for v in cells.values())
        print(f"  {s}/{l}: {parts}  -> span {span:.2f}")

y = np.array([r[4] for r in rows]); y = y - y.mean()
def oh(v):
    u = sorted(set(v)); idx = {k: i for i, k in enumerate(u)}
    M = np.zeros((len(v), len(u)))
    for i, x in enumerate(v):
        M[i, idx[x]] = 1
    return M
def r2(X):
    X = np.hstack([X, np.ones((X.shape[0], 1))])
    b, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    return 1 - (((y - X @ b) ** 2).sum() / (y ** 2).sum())
Xsec = oh([r[2] + r[3] for r in rows]); Xsc = oh([r[1] for r in rows])
rs, rh, rb = r2(Xsec), r2(Xsc), r2(np.hstack([Xsec, Xsc]))
print(f"\nR^2  section+dialect only: {rs:.3f} | scribe only: {rh:.3f} | both: {rb:.3f}")
print(f"unique to section: {rb-rh:+.3f} | unique to scribe: {rb-rs:+.3f} | shared: {rs+rh-rb:.3f}")
