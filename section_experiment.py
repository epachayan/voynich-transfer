import csv, random
import numpy as np
from collections import Counter

random.seed(408)
SPACE = 32
N = 3400
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

def recovery(words, own_ops, other_ops, k=K):
    b = stats(to_stream(words))[1]
    return (apply_ops(words, other_ops, k) - b) / (apply_ops(words, own_ops, k) - b)

def two_disjoint(words, n, seed, blk=200):
    rng = random.Random(seed)
    starts = list(range(0, len(words) - blk, blk))
    rng.shuffle(starts)
    a, b = [], []
    for s in starts:
        (a if len(a) < n else b).extend(words[s:s + blk])
        if len(a) >= n and len(b) >= n:
            break
    return a[:n], b[:n]

def block_sample(words, n, seed, blk=200):
    rng = random.Random(seed)
    starts = list(range(0, max(1, len(words) - blk), blk))
    rng.shuffle(starts)
    out = []
    for s in starts:
        out.extend(words[s:s + blk])
        if len(out) >= n:
            break
    return out[:n]

cells = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"):
            continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if not w or any(c not in allowed for c in w):
            continue
        cells.setdefault((row["section"], row["language"]), []).append(w)

full = [w for k in cells for w in cells[k]]
h1f, h2f = stats(to_stream(full))
print(f"calibration: rebuilt full corpus {len(full)} words, h2={h2f:.3f} (target ~2.112)")

corp = {
    "HAa": None, "HAb": None,
    "HB": block_sample(cells[("H", "B")], N, 2603),
    "BB": block_sample(cells[("B", "B")], N, 2604),
    "SBa": None, "SBb": None,
}
corp["HAa"], corp["HAb"] = two_disjoint(cells[("H", "A")], N, 2601)
corp["SBa"], corp["SBb"] = two_disjoint(cells[("S", "B")], N, 2602)
labels = ["HAa", "HAb", "HB", "BB", "SBa", "SBb"]
print("cell sizes:", {f"{s}/{l}": len(v) for (s, l), v in sorted(cells.items()) if len(v) > 300})

OPS, TOKS = {}, {}
for L in labels:
    b = stats(to_stream(corp[L]))[1]
    TOKS[L], OPS[L], own = greedy(corp[L])
    print(f"{L:4s} base h2={b:.3f} own@{K}={own:.3f}  first: {' '.join(TOKS[L][:8])}")

print("\n=== recovery matrix (rows=text, cols=inventory, %) ===")
rec = {}
print("      " + "  ".join(f"{c:>5}" for c in labels))
for r in labels:
    row = []
    for c in labels:
        v = 1.0 if r == c else recovery(corp[r], OPS[r], OPS[c])
        rec[(r, c)] = v
        row.append(f"{100*v:5.1f}")
    print(f"{r:>4}  " + "  ".join(row))

topic = {"HAa": "H", "HAb": "H", "HB": "H", "BB": "B", "SBa": "S", "SBb": "S"}
dial = {"HAa": "A", "HAb": "A", "HB": "B", "BB": "B", "SBa": "B", "SBb": "B"}
def tier(pred):
    v = [rec[(r, c)] for r in labels for c in labels if r != c and pred(r, c)]
    return 100 * sum(v) / len(v), len(v)

t1 = tier(lambda r, c: dial[r] == dial[c] and topic[r] == topic[c])
t2 = tier(lambda r, c: dial[r] == dial[c] and topic[r] != topic[c])
t3 = tier(lambda r, c: dial[r] != dial[c] and topic[r] == topic[c])
t4 = tier(lambda r, c: dial[r] != dial[c] and topic[r] != topic[c])
print(f"\nsame dialect, same topic (ceiling): {t1[0]:.1f}%  (n={t1[1]})")
print(f"same dialect, DIFF topic:           {t2[0]:.1f}%  (n={t2[1]})")
print(f"DIFF dialect, same topic (herbal):  {t3[0]:.1f}%  (n={t3[1]})")
print(f"DIFF dialect, diff topic:           {t4[0]:.1f}%  (n={t4[1]})")

def boot_ci(y_words, own_ops, other_ops, reps=200, blk=100):
    rng = random.Random(7)
    vals = []
    nb = len(y_words) // blk
    blocks = [y_words[i * blk:(i + 1) * blk] for i in range(nb)]
    for _ in range(reps):
        w = []
        for _ in range(nb):
            w.extend(blocks[rng.randrange(nb)])
        vals.append(recovery(w, own_ops, other_ops))
    vals.sort()
    return 100 * vals[int(0.025 * reps)], 100 * vals[int(0.975 * reps)]

lo, hi = boot_ci(corp["HB"], OPS["HB"], OPS["HAa"])
print(f"\nbootstrap 95% CI, HB text under HAa inventory (dialect effect): [{lo:.1f}, {hi:.1f}]%")
lo, hi = boot_ci(corp["HB"], OPS["HB"], OPS["BB"])
print(f"bootstrap 95% CI, HB text under BB inventory (topic effect):    [{lo:.1f}, {hi:.1f}]%")

print("\n================ Minimal-parse robustness rerun ================")
MB = "Voynich-public/Corpora/Voynich_texts/Minimal"
def load_keepcase(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for w in txt.split():
        w = "".join(c for c in w if c.isalpha())
        if w and all(ord(c) < 128 for c in w):
            out.append(w)
    return out
Am = load_keepcase(f"{MB}/Voynich A Minimal Text")
Bm = load_keepcase(f"{MB}/Voynich B Minimal Text")
n = min(len(Am), len(Bm))
Bm_s = block_sample(Bm, n, 1438)
Am_s = Am[:n] if len(Am) == n else block_sample(Am, n, 1438)
print(f"A minimal {len(Am)} w, B minimal {len(Bm)} w -> matched {n}")
for tag, w in (("A", Am_s), ("B", Bm_s)):
    print(f"{tag} minimal base h2={stats(to_stream(w))[1]:.3f}")
tA, oA, ownA = greedy(Am_s)
tB, oB, ownB = greedy(Bm_s)
print(f"A first merges: {' '.join(tA[:8])}")
print(f"B first merges: {' '.join(tB[:8])}")
print(f"A text: own {ownA:.3f} | B inv -> recovery {100*recovery(Am_s, oA, oB):.1f}%")
print(f"B text: own {ownB:.3f} | A inv -> recovery {100*recovery(Bm_s, oB, oA):.1f}%")
