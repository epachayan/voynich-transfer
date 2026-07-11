import csv, re, random
import numpy as np
from collections import Counter

def stats(sb, space_byte):
    arr = np.frombuffer(sb, dtype=np.uint8)
    u = np.bincount(arr, minlength=256).astype(np.float64)
    p = u[u > 0] / u.sum()
    h1 = -(p * np.log2(p)).sum()
    bg = arr[:-1].astype(np.int32) * 256 + arr[1:]
    b = np.bincount(bg, minlength=65536).astype(np.float64)
    q = b[b > 0] / b.sum()
    return -(q * np.log2(q)).sum() - h1

class Env:
    def __init__(self, wordlists):
        syms = sorted(set(c for wl in wordlists for w in wl for c in w))
        assert len(syms) < 170, len(syms)
        self.space = 0
        self.code = {c: i + 1 for i, c in enumerate(syms)}  # 1..K
        self.next0 = len(syms) + 1
    def stream(self, words):
        b = bytearray()
        for i, w in enumerate(words):
            if i: b.append(self.space)
            for c in w: b.append(self.code[c])
        return bytes(b)
    def greedy(self, words, rng=None, topk=90, max_merges=40, k_report=17):
        stream = self.stream(words)
        names = {b: c for c, b in self.code.items()}
        nxt = self.next0
        h2 = stats(stream, self.space)
        toks, ops = [], []
        for _ in range(max_merges):
            arr = np.frombuffer(stream, dtype=np.uint8)
            m = (arr[:-1] != self.space) & (arr[1:] != self.space)
            cnt = Counter((arr[:-1][m].astype(np.int32) * 256 + arr[1:][m]).tolist())
            cands = []
            for pair, c in cnt.most_common(topk):
                a, b = pair // 256, pair % 256
                cand = stream.replace(bytes([a, b]), bytes([nxt]))
                ch2 = stats(cand, self.space)
                if ch2 > h2:
                    cands.append((ch2, a, b, cand))
            if not cands:
                break
            cands.sort(key=lambda x: -x[0])
            pick = cands[0] if rng is None else cands[rng.randrange(min(3, len(cands)))]
            h2, a, b, stream = pick
            names[nxt] = (names[a]) + (names[b])
            ops.append((a, b, nxt))
            toks.append(names[nxt])
            nxt += 1
        return toks, ops, h2
    def apply(self, words, ops, k):
        s = self.stream(words)
        for a, b, nxt in ops[:k]:
            s = s.replace(bytes([a, b]), bytes([nxt]))
        return stats(s, self.space)
    def recovery(self, words, own_ops, other_ops, k=17):
        base = stats(self.stream(words), self.space)
        return (self.apply(words, other_ops, k) - base) / (self.apply(words, own_ops, k) - base)

def block_sample(words, n, seed, blk=200):
    rng = random.Random(seed)
    starts = list(range(0, max(1, len(words) - blk), blk))
    rng.shuffle(starts)
    out = []
    for s in starts:
        out.extend(words[s:s + blk])
        if len(out) >= n: break
    return out[:n]

# ---------- Currier language per folio ----------
tmp = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H": continue
        tmp.setdefault(row["folio"], Counter())[row["language"]] += 1
lang = {}
for fol, c in tmp.items():
    cc = {k: v for k, v in c.items() if k in ("A", "B")}
    if cc: lang[fol] = max(cc, key=cc.get)

# ================= PART 1: v101 A/B transfer =================
print("=" * 60)
print("PART 1  v101 (independent third parse): Currier A vs B")
def parse_v101(path):
    fw = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            mo = re.match(r'<(f?[^.]+)\.[^>]*>(.*)', line.strip())
            if not mo: continue
            fol = "f" + mo.group(1).lstrip("f")
            fw.setdefault(fol, []).append(mo.group(2).replace("=", ".").replace("-", ""))
    return {fol: [w for w in "".join(ch).split(".") if w] for fol, ch in fw.items()}
v = parse_v101("voynich-transcription/voynich.txt")
vA = [w for fol, ws in v.items() if lang.get(fol) == "A" for w in ws]
vB = [w for fol, ws in v.items() if lang.get(fol) == "B" for w in ws]
n = min(len(vA), len(vB))
vBs = block_sample(vB, n, 1438)
vAs = vA[:n] if len(vA) == n else block_sample(vA, n, 1438)
env = Env([vAs, vBs])
print(f"matched size: {n} words each")
print(f"A baseline h2={stats(env.stream(vAs), env.space):.3f} | B baseline h2={stats(env.stream(vBs), env.space):.3f}")
tA, oA, _ = env.greedy(vAs)
tB, oB, _ = env.greedy(vBs)
print("A first merges (v101 codes):", " ".join(tA[:8]))
print("B first merges (v101 codes):", " ".join(tB[:8]))
print(f"A text: own vs B-inv -> recovery {100*env.recovery(vAs, oA, oB):.1f}%")
print(f"B text: own vs A-inv -> recovery {100*env.recovery(vBs, oB, oA):.1f}%")

# ================= PART 2: restart stability (EVA) =================
print("=" * 60)
print("PART 2  stochastic-restart stability (EVA Maximal Simplified)")
def load(path):
    allowed = set("abcdefghiklmnopqrstxyz")
    txt = open(path, encoding="utf-8", errors="replace").read().lower()
    return [w2 for w in txt.split() if (w2 := "".join(c for c in w if c.isalpha())) and all(c in allowed for c in w2)]
base = "Voynich-public/Corpora/Voynich_texts/Maximal Simplified"
A = load(f"{base}/Voynich A Maximal Simplified Text")
Bf = load(f"{base}/Voynich B Maximal Simplified Text")
n = len(A)
Bs = block_sample(Bf, n, 1438)
env2 = Env([A, Bs])
# deterministic reference
_, oA0, _ = env2.greedy(A); _, oB0, _ = env2.greedy(Bs)
recA0 = 100 * env2.recovery(A, oA0, oB0); recB0 = 100 * env2.recovery(Bs, oB0, oA0)
print(f"deterministic greedy: A<-B {recA0:.1f}% | B<-A {recB0:.1f}%")
setsA, setsB, recsA, recsB = [], [], [], []
opsA_list, opsB_list = [], []
for seed in range(5):
    tA, oA, _ = env2.greedy(A, rng=random.Random(100 + seed))
    tB, oB, _ = env2.greedy(Bs, rng=random.Random(200 + seed))
    setsA.append(set(tA[:17])); setsB.append(set(tB[:17]))
    opsA_list.append(oA); opsB_list.append(oB)
    recsA.append(100 * env2.recovery(A, oA, oB))
    recsB.append(100 * env2.recovery(Bs, oB, oA))
print(f"stochastic restarts (5 seeds, uniform over top-3):")
print(f"  A<-B recovery: mean {np.mean(recsA):.1f}% sd {np.std(recsA):.2f}  range [{min(recsA):.1f},{max(recsA):.1f}]")
print(f"  B<-A recovery: mean {np.mean(recsB):.1f}% sd {np.std(recsB):.2f}  range [{min(recsB):.1f},{max(recsB):.1f}]")
def mean_overlap(sets):
    vals = [len(sets[i] & sets[j]) for i in range(len(sets)) for j in range(i+1, len(sets))]
    return np.mean(vals)
print(f"  first-17 inventory overlap across restarts: A {mean_overlap(setsA):.1f}/17 | B {mean_overlap(setsB):.1f}/17")
# overlap of stochastic inventories with the deterministic one
detA, detB = set(t for t in [env2.greedy(A)[0][:17]][0]), set(env2.greedy(Bs)[0][:17])
oaA = np.mean([len(s & detA) for s in setsA]); oaB = np.mean([len(s & detB) for s in setsB])
print(f"  overlap with deterministic first-17: A {oaA:.1f}/17 | B {oaB:.1f}/17")
