import json, random
import numpy as np
from collections import Counter

BASE = "Voynich-public/Corpora/Voynich_texts/Maximal Simplified"
allowed = set("abcdefghiklmnopqrstxyz")
SPACE = 32

def load_words(path):
    txt = open(path, encoding="utf-8", errors="replace").read().lower()
    out = []
    for w in txt.split():
        w = "".join(c for c in w if c.isalpha())
        if w and all(c in allowed for c in w):
            out.append(w)
    return out

def to_stream(words):
    return (" ".join(words)).encode("latin-1")

def stats(sb):
    arr = np.frombuffer(sb, dtype=np.uint8)
    u = np.bincount(arr, minlength=256).astype(np.float64)
    p = u[u > 0] / u.sum()
    h1 = -(p * np.log2(p)).sum()
    bg = arr[:-1].astype(np.int32) * 256 + arr[1:]
    b = np.bincount(bg, minlength=65536).astype(np.float64)
    q = b[b > 0] / b.sum()
    return h1, -(q * np.log2(q)).sum() - h1, int((u > 0).sum())

def greedy(words, max_merges=40, topk=90):
    stream = to_stream(words)
    names = {ord(c): c for c in sorted(set("".join(words)))}
    nxt = 128
    h1, h2, K = stats(stream)
    traj = [dict(step=0, token="", h1=round(h1, 4), h2=round(h2, 4), K=K)]
    ops = []
    for step in range(1, max_merges + 1):
        arr = np.frombuffer(stream, dtype=np.uint8)
        m = (arr[:-1] != SPACE) & (arr[1:] != SPACE)
        cnt = Counter((arr[:-1][m].astype(np.int32) * 256 + arr[1:][m]).tolist())
        best = None
        for pair, c in cnt.most_common(topk):
            a, b = pair // 256, pair % 256
            cand = stream.replace(bytes([a, b]), bytes([nxt]))
            ch1, ch2, cK = stats(cand)
            if best is None or ch2 > best[0]:
                best = (ch2, ch1, cK, a, b, cand)
        if best is None or best[0] <= h2:
            break
        h2, h1, K, a, b, stream = best
        names[nxt] = names[a] + names[b]
        ops.append((a, b, nxt, names[nxt]))
        traj.append(dict(step=step, token=names[nxt], h1=round(h1, 4), h2=round(h2, 4), K=K))
        nxt += 1
    return traj, ops

def apply_ops(words, ops, k):
    stream = to_stream(words)
    for a, b, nxt, _ in ops[:k]:
        stream = stream.replace(bytes([a, b]), bytes([nxt]))
    return stats(stream)

def block_sample(words, n, seed):
    rng = random.Random(seed)
    B = 200
    starts = list(range(0, len(words) - B, B))
    rng.shuffle(starts)
    out = []
    for s in starts:
        out.extend(words[s:s + B])
        if len(out) >= n:
            break
    return out[:n]

A = load_words(f"{BASE}/Voynich A Maximal Simplified Text")
Bfull = load_words(f"{BASE}/Voynich B Maximal Simplified Text")
print(f"A words: {len(A)}   B words: {len(Bfull)}  -> subsampling B to {len(A)}")
Bsub = block_sample(Bfull, len(A), seed=1438)

for tag, w in (("A", A), ("B full", Bfull), ("B sub", Bsub)):
    h1, h2, K = stats(to_stream(w))
    print(f"{tag:6s} baseline: h1={h1:.3f} h2={h2:.3f} K={K}  (CSV: A 3.842/2.146, Bfull 3.875/2.005)")

trajA, opsA = greedy(A)
trajB, opsB = greedy(Bsub)

print("\n=== merge sequences side by side ===")
print(f"{'step':>4}  {'A':10s}  {'B':10s}")
for i in range(1, max(len(trajA), len(trajB))):
    ta = trajA[i]["token"] if i < len(trajA) else ""
    tb = trajB[i]["token"] if i < len(trajB) else ""
    print(f"{i:>4}  {ta:10s}  {tb:10s}")
print(f"\nfinal h2:  A={trajA[-1]['h2']:.3f} ({len(trajA)-1} merges)   B={trajB[-1]['h2']:.3f} ({len(trajB)-1} merges)")

setA17 = {t["token"] for t in trajA[1:18]}
setB17 = {t["token"] for t in trajB[1:18]}
setA = {t["token"] for t in trajA[1:]}
setB = {t["token"] for t in trajB[1:]}
print("\n=== inventory overlap ===")
print(f"first 17:  shared {len(setA17 & setB17)}  jaccard {len(setA17 & setB17)/len(setA17 | setB17):.2f}")
print(f"  A-only@17: {sorted(setA17 - setB17)}")
print(f"  B-only@17: {sorted(setB17 - setA17)}")
print(f"all 40:    shared {len(setA & setB)}  jaccard {len(setA & setB)/len(setA | setB):.2f}")
print(f"  A-only: {sorted(setA - setB)}")
print(f"  B-only: {sorted(setB - setA)}")

print("\n=== transfer matrix: h2 after applying k ops of each inventory to each corpus ===")
for k in (17, 40):
    aa = apply_ops(A, opsA, k)[1]
    ab = apply_ops(A, opsB, k)[1]
    bb = apply_ops(Bsub, opsB, k)[1]
    ba = apply_ops(Bsub, opsA, k)[1]
    print(f"k={k}:  A text: own inv {aa:.3f} | B's inv {ab:.3f} (gap {aa-ab:+.3f})")
    print(f"       B text: own inv {bb:.3f} | A's inv {ba:.3f} (gap {bb-ba:+.3f})")

print("\n=== B subsample stability (first-17 inventory, other seeds) ===")
for seed in (2026, 408):
    Bs = block_sample(Bfull, len(A), seed=seed)
    tj, _ = greedy(Bs, max_merges=17)
    s = {t["token"] for t in tj[1:]}
    print(f"seed {seed}: shared with main B run: {len(s & setB17)}/17 | new: {sorted(s - setB17)}")

json.dump(dict(trajA=trajA, trajB=trajB), open("ab_results.json", "w"), indent=1)
print("\nsaved ab_results.json")
