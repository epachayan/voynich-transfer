import json, random
import numpy as np
from collections import Counter

BASE = "Voynich-public/Corpora/Voynich_texts/Maximal Simplified"
allowed = set("abcdefghiklmnopqrstxyz")
SPACE = 32
N = 5000
K_DEPTH = 17

def load_words(path):
    txt = open(path, encoding="utf-8", errors="replace").read().lower()
    return [w2 for w in txt.split() if (w2 := "".join(c for c in w if c.isalpha())) and all(c in allowed for c in w2)]

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

def greedy(words, max_merges=K_DEPTH, topk=90):
    stream = to_stream(words)
    names = {ord(c): c for c in sorted(set("".join(words)))}
    nxt = 128
    h1, h2, K = stats(stream)
    toks, ops = [], []
    for step in range(max_merges):
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
        ops.append((a, b, nxt))
        toks.append(names[nxt])
        nxt += 1
    return toks, ops, h2

def apply_ops(words, ops):
    stream = to_stream(words)
    for a, b, nxt in ops:
        stream = stream.replace(bytes([a, b]), bytes([nxt]))
    return stats(stream)[1]

def two_disjoint(words, n, seed):
    rng = random.Random(seed)
    B = 200
    starts = list(range(0, len(words) - B, B))
    rng.shuffle(starts)
    a, b = [], []
    for s in starts:
        blk = words[s:s + B]
        if len(a) < n:
            a.extend(blk)
        elif len(b) < n:
            b.extend(blk)
    return a[:n], b[:n]

hands = {}
for h in (1, 2, 3):
    w = load_words(f"{BASE}/Voynich {h} Maximal Simplified Text")
    a, b = two_disjoint(w, N, seed=1400 + h)
    hands[f"{h}a"], hands[f"{h}b"] = a, b
labels = ["1a", "1b", "2a", "2b", "3a", "3b"]

base, own, OPS, TOKS = {}, {}, {}, {}
for L in labels:
    base[L] = stats(to_stream(hands[L]))[1]
    TOKS[L], OPS[L], own[L] = greedy(hands[L])
    print(f"{L}: base h2={base[L]:.3f}  own@{K_DEPTH}={own[L]:.3f}  first tokens: {' '.join(TOKS[L][:10])}")

print("\nsplit-half inventory agreement (first 17 sets):")
for h in (1, 2, 3):
    sa, sb = set(TOKS[f"{h}a"]), set(TOKS[f"{h}b"])
    print(f"  hand {h}: {len(sa & sb)}/17 shared")

print("\n=== recovery matrix (rows = text, cols = inventory, % of own gain) ===")
rec = {}
print("      " + "  ".join(f"{c:>5}" for c in labels))
for r in labels:
    row = []
    for c in labels:
        g = (apply_ops(hands[r], OPS[c]) - base[r]) / (own[r] - base[r])
        rec[(r, c)] = g
        row.append(f"{100*g:5.1f}")
    print(f"{r:>4}  " + "  ".join(row))

def mean(pairs):
    v = [rec[p] for p in pairs]
    return 100 * sum(v) / len(v)

within_scribe = [("1a","1b"),("1b","1a"),("2a","2b"),("2b","2a"),("3a","3b"),("3b","3a")]
within_B = [(r, c) for r in ("2a","2b","3a","3b") for c in ("2a","2b","3a","3b") if r[0] != c[0]]
across = [(r, c) for r in labels for c in labels if (r[0] == "1") != (c[0] == "1")]
print(f"\nwithin-scribe (ceiling): {mean(within_scribe):.1f}%")
print(f"within-B, across-scribe (2 vs 3): {mean(within_B):.1f}%")
print(f"across-dialect (1 vs 2,3): {mean(across):.1f}%")

print("\n=== tiny hands 4 and 5: inventory-based classification ===")
Aset = ["chol", "chor", "cthy", "ckhy", "cthor"]
Bset = ["chedy", "shedy", "qokeedy", "qokedy", "qokain", "qokaiin"]
for h in (1, 2, 3, 4, 5):
    w = load_words(f"{BASE}/Voynich {h} Maximal Simplified Text")
    n = len(w)
    ra = 1000 * sum(w.count(x) for x in Aset) / n
    rb = 1000 * sum(w.count(x) for x in Bset) / n
    line = f"hand {h} ({n:5d} w): A-words {ra:5.1f}/1000  B-words {rb:5.1f}/1000"
    if h in (4, 5):
        b0 = stats(to_stream(w))[1]
        dA = apply_ops(w, OPS["1a"]) - b0
        dB = apply_ops(w, OPS["3a"]) - b0
        line += f"  | repair by A-inv {dA:+.3f} vs B-inv {dB:+.3f} -> {'A' if dA > dB else 'B'}-affine"
    print(line)

json.dump({"base": base, "own": own, "toks": TOKS,
           "rec": {f"{r}|{c}": v for (r, c), v in rec.items()}},
          open("scribes_results.json", "w"), indent=1)
print("\nsaved scribes_results.json")
