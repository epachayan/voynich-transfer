import csv, json
import numpy as np
from collections import Counter, OrderedDict

SPACE = 32
allowed = set("abcdefghiklmnopqrstxyz")
KGLOBAL = 40
MIN_WORDS = 60

def stats_h2(sb):
    arr = np.frombuffer(sb, dtype=np.uint8)
    u = np.bincount(arr, minlength=256).astype(np.float64)
    p = u[u > 0] / u.sum()
    h1 = -(p * np.log2(p)).sum()
    bg = arr[:-1].astype(np.int32) * 256 + arr[1:]
    b = np.bincount(bg, minlength=65536).astype(np.float64)
    q = b[b > 0] / b.sum()
    return -(q * np.log2(q)).sum() - h1

def ts(words):
    return (" ".join(words)).encode("latin-1")

def greedy_global(words, max_merges=KGLOBAL, topk=90):
    stream = ts(words)
    names = {ord(c): c for c in sorted(set("".join(words)))}
    nxt = 128
    h2 = stats_h2(stream)
    ops = []
    for _ in range(max_merges):
        arr = np.frombuffer(stream, dtype=np.uint8)
        m = (arr[:-1] != SPACE) & (arr[1:] != SPACE)
        cnt = Counter((arr[:-1][m].astype(np.int32) * 256 + arr[1:][m]).tolist())
        best = None
        for pair, c in cnt.most_common(topk):
            a, b = pair // 256, pair % 256
            cand = stream.replace(bytes([a, b]), bytes([nxt]))
            ch2 = stats_h2(cand)
            if best is None or ch2 > best[0]:
                best = (ch2, a, b, cand)
        if best is None or best[0] <= h2:
            break
        h2, a, b, stream = best
        names[nxt] = names[a] + names[b]
        ops.append((a, b, nxt))
        nxt += 1
    return ops, names

def token_vec(words, ops):
    s = ts(words)
    for a, b, nxt in ops:
        s = s.replace(bytes([a, b]), bytes([nxt]))
    arr = np.frombuffer(s, dtype=np.uint8)
    c = np.bincount(arr, minlength=256).astype(np.float64)
    c[SPACE] = 0
    tot = c.sum()
    return c / tot if tot else c

folio_words = OrderedDict()
folio_meta = {}
cells = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"):
            continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if not w or any(c not in allowed for c in w):
            continue
        fol = row["folio"]
        folio_words.setdefault(fol, []).append(w)
        folio_meta[fol] = (row["section"], row["language"])
        cells.setdefault((row["section"], row["language"]), []).append(w)

all_words = [w for ws in folio_words.values() for w in ws]
print(f"folios total: {len(folio_words)}, words: {len(all_words)}")
ops, names = greedy_global(all_words)
print("global inventory:", " ".join(names[o[2]] for o in ops))

vHA = token_vec(cells[("H", "A")], ops)
vBB = token_vec(cells[("B", "B")], ops)
u = vBB - vHA
denom = float(u @ (vBB - vHA))
def score(words):
    return float((token_vec(words, ops) - vHA) @ u) / denom

loading = [(names.get(i, chr(i)), u[i]) for i in range(256) if abs(u[i]) > 0]
loading.sort(key=lambda x: x[1])
print("\naxis loadings  (HA pole <- ... -> BB pole):")
print("  HA side:", " ".join(f"{t}({100*v:.1f})" for t, v in loading[:7]))
print("  BB side:", " ".join(f"{t}(+{100*v:.1f})" for t, v in loading[-7:][::-1]))

mp = json.load(open("results/map_results.json"))
plan = [("H", "A", "HA", 3), ("P", "A", "PA", 1), ("H", "B", "HB", 1),
        ("S", "B", "SB", 5), ("B", "B", "BB", 3)]
unit_scores = {}
for sec, lang, tag, nch in plan:
    w = cells[(sec, lang)]
    for i in range(nch):
        unit = f"{tag}{i+1}" if nch > 1 else tag
        unit_scores[unit] = score(w[i * 2000:(i + 1) * 2000])
fied = {un: fv for un, fv in zip(mp["units"], mp["fiedler"])}
xs = np.array([fied[k] for k in unit_scores])
ys = np.array([unit_scores[k] for k in unit_scores])
r = float(np.corrcoef(xs, ys)[0, 1])
print(f"\nVALIDATION: projection vs Fiedler over 13 units: r = {r:.3f}")

fol_score = {}
for fol, ws in folio_words.items():
    if len(ws) >= MIN_WORDS:
        fol_score[fol] = score(ws)
print(f"folios scored (>= {MIN_WORDS} words): {len(fol_score)}")

groups = {}
for fol, sc in fol_score.items():
    groups.setdefault(folio_meta[fol], []).append((fol, sc))

print("\nper-section folio score distributions (0 = HA pole, 1 = BB pole):")
for key in sorted(groups, key=lambda k: np.mean([s for _, s in groups[k]])):
    vals = [s for _, s in groups[key]]
    print(f"  {key[0]}/{key[1]:>2}: n={len(vals):3d}  mean={np.mean(vals):+.2f}  range [{min(vals):+.2f}, {max(vals):+.2f}]")

print("\nPharma-A folios individually:")
for fol, sc in sorted(groups.get(("P", "A"), []), key=lambda x: x[1]):
    print(f"  {fol:6s} {sc:+.2f}  ({len(folio_words[fol])} w)")
print("\nHerbal-B folios individually:")
for fol, sc in sorted(groups.get(("H", "B"), []), key=lambda x: x[1]):
    print(f"  {fol:6s} {sc:+.2f}  ({len(folio_words[fol])} w)")
print("\nCurrier-unclassified / text-only pages:")
for key in groups:
    if key[1] == "NA" or key[0] == "T":
        for fol, sc in sorted(groups[key], key=lambda x: x[1]):
            print(f"  {fol:6s} [{key[0]}/{key[1]}] {sc:+.2f}  ({len(folio_words[fol])} w)")

sd = float(np.std(list(fol_score.values())))
adj = []
for key, lst in groups.items():
    ordered = [(f, s) for f, s in lst]
    for (f1, s1), (f2, s2) in zip(ordered, ordered[1:]):
        adj.append(abs(s1 - s2))
print(f"\nnoise check: mean adjacent-folio |delta| within section = {np.mean(adj):.3f} vs overall folio sd = {sd:.3f}")

json.dump({"folio_scores": fol_score, "meta": {f: folio_meta[f] for f in fol_score},
           "validation_r": r}, open("results/folio_gradient.json", "w"), indent=1)
print("saved results/folio_gradient.json")
