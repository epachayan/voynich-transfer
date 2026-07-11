import csv
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
    return -(q * np.log2(q)).sum() - h1

def ts(w):
    return (" ".join(w)).encode("latin-1")

def greedy(words):
    stream = ts(words)
    nxt = 128
    h2 = stats(stream)
    ops = []
    for _ in range(K):
        arr = np.frombuffer(stream, dtype=np.uint8)
        m = (arr[:-1] != SPACE) & (arr[1:] != SPACE)
        cnt = Counter((arr[:-1][m].astype(np.int32) * 256 + arr[1:][m]).tolist())
        best = None
        for pair, c in cnt.most_common(90):
            a, b = pair // 256, pair % 256
            cand = stream.replace(bytes([a, b]), bytes([nxt]))
            ch2 = stats(cand)
            if best is None or ch2 > best[0]:
                best = (ch2, a, b, cand)
        if best is None or best[0] <= h2:
            break
        h2, a, b, stream = best
        ops.append((a, b, nxt))
        nxt += 1
    return ops

def rec(words, own_ops, other_ops):
    b = stats(ts(words))
    def ap(ops):
        s = ts(words)
        for a, bb, nx in ops:
            s = s.replace(bytes([a, bb]), bytes([nx]))
        return stats(s)
    return (ap(other_ops) - b) / (ap(own_ops) - b)

cells = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"):
            continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if not w or any(c not in allowed for c in w):
            continue
        cells.setdefault((row["section"], row["language"]), []).append(w)

U = {"HA1": cells[("H", "A")][:N],
     "SB2": cells[("S", "B")][N:2 * N],
     "BB1": cells[("B", "B")][:N],
     "PAalt": cells[("P", "A")][-N:],
     "HBalt": cells[("H", "B")][-N:]}
OPS = {}
for k, w in U.items():
    OPS[k] = greedy(w)
for probe in ("PAalt", "HBalt"):
    line = []
    for anchor in ("HA1", "SB2", "BB1"):
        s = 100 * (rec(U[probe], OPS[probe], OPS[anchor]) + rec(U[anchor], OPS[anchor], OPS[probe])) / 2
        line.append(f"{anchor} {s:.1f}")
    print(probe, "sym-similarity ->", " | ".join(line))
