import csv, json
import numpy as np
from collections import Counter

SPACE = 32
N = 2000
K = 17
allowed = set("abcdefghiklmnopqrstxyz")

def stats(sb):
    arr = np.frombuffer(sb, dtype=np.uint8)
    u = np.bincount(arr, minlength=256).astype(np.float64)
    p = u[u > 0] / u.sum()
    h1 = -(p * np.log2(p)).sum()
    bg = arr[:-1].astype(np.int32) * 256 + arr[1:]
    b = np.bincount(bg, minlength=65536).astype(np.float64)
    q = b[b > 0] / b.sum()
    return h1, -(q * np.log2(q)).sum() - h1

def to_stream(words):
    return (" ".join(words)).encode("latin-1")

def greedy(words, max_merges=K, topk=90):
    stream = to_stream(words)
    names = {ord(c): c for c in sorted(set("".join(words)))}
    nxt = 128
    h2 = stats(stream)[1]
    toks, ops = [], []
    for _ in range(max_merges):
        arr = np.frombuffer(stream, dtype=np.uint8)
        m = (arr[:-1] != SPACE) & (arr[1:] != SPACE)
        cnt = Counter((arr[:-1][m].astype(np.int32) * 256 + arr[1:][m]).tolist())
        best = None
        for pair, c in cnt.most_common(topk):
            a, b = pair // 256, pair % 256
            cand = stream.replace(bytes([a, b]), bytes([nxt]))
            ch2 = stats(cand)[1]
            if best is None or ch2 > best[0]:
                best = (ch2, a, b, cand)
        if best is None or best[0] <= h2:
            break
        h2, a, b, stream = best
        names[nxt] = names[a] + names[b]
        ops.append((a, b, nxt))
        toks.append(names[nxt])
        nxt += 1
    return toks, ops, h2

def apply_ops(words, ops, k=K):
    stream = to_stream(words)
    for a, b, nxt in ops[:k]:
        stream = stream.replace(bytes([a, b]), bytes([nxt]))
    return stats(stream)[1]

cells = {}
folio_first = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"):
            continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if not w or any(c not in allowed for c in w):
            continue
        key = (row["section"], row["language"])
        cells.setdefault(key, []).append(w)
        folio_first.setdefault(key, row["folio"])

plan = [("H", "A", "HA"), ("P", "A", "PA"), ("H", "B", "HB"),
        ("S", "B", "SB"), ("B", "B", "BB")]
units, unit_words = [], {}
for sec, lang, tag in plan:
    w = cells[(sec, lang)]
    nch = len(w) // N
    for i in range(nch):
        u = f"{tag}{i+1}" if nch > 1 else tag
        units.append(u)
        unit_words[u] = w[i * N:(i + 1) * N]
print("units:", " ".join(units))

OPS, base, own = {}, {}, {}
for u in units:
    base[u] = stats(to_stream(unit_words[u]))[1]
    _, OPS[u], own[u] = greedy(unit_words[u])
print("baselines h2:", {u: round(base[u], 3) for u in units})

M = len(units)
R = np.eye(M)
for i, r in enumerate(units):
    for j, c in enumerate(units):
        if i != j:
            R[i, j] = (apply_ops(unit_words[r], OPS[c]) - base[r]) / (own[r] - base[r])
S = (R + R.T) / 2

W = S.copy(); np.fill_diagonal(W, 0)
L = np.diag(W.sum(1)) - W
evals, evecs = np.linalg.eigh(L)
fiedler = evecs[:, 1]
if fiedler[units.index("BB1")] < fiedler[units.index("HA1")]:
    fiedler = -fiedler
order = np.argsort(fiedler)

Dm = 1 - S
J = np.eye(M) - np.ones((M, M)) / M
Bm = -0.5 * J @ (Dm ** 2) @ J
mev = np.sort(np.linalg.eigvalsh(Bm))[::-1]
pos = mev[mev > 0]
print(f"\nMDS variance: axis1 {100*pos[0]/pos.sum():.1f}%  axis2 {100*pos[1]/pos.sum():.1f}%  axis3 {100*pos[2]/pos.sum():.1f}%")

print("\nspectral seriation (Fiedler coordinate):")
for idx in order:
    print(f"  {units[idx]:4s} {fiedler[idx]:+.3f}   base h2={base[units[idx]]:.3f}")

print("\nsymmetrised similarity, seriated order (x100):")
ou = [units[i] for i in order]
print("      " + " ".join(f"{u:>4}" for u in ou))
for i in order:
    print(f"{units[i]:>4}  " + " ".join(f"{100*S[i, j]:4.0f}" for j in order))

adj = [S[order[i], order[i+1]] for i in range(M - 1)]
far = S[order[0], order[-1]]
print(f"\nmean adjacent similarity along the order: {100*np.mean(adj):.1f}")
print(f"endpoint similarity ({ou[0]} vs {ou[-1]}): {100*far:.1f}")

json.dump({"units": units, "R": R.tolist(), "fiedler": fiedler.tolist(),
           "order": [units[i] for i in order], "base": base},
          open("results/map_results.json", "w"), indent=1)
print("saved results/map_results.json")
