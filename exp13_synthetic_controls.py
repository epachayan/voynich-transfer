"""
EXPERIMENT 13 -- Synthetic controls for the transfer map.
Question: is the manuscript's one-axis (84%) gradient a distinctive property,
or does any structured text yield it? Build controls, push each through the
IDENTICAL map pipeline (12 units x 2000 words, pairwise k=17 recovery,
symmetrise, classical-MDS axis-1 %, and min pairwise similarity = spread),
and compare to the real manuscript.
Controls: (1) random bigram (whole-MS, one model -> no section identity);
(2) section-mixture bigram (per-section bigram -> section differences baked
in, no memory); (3) self-copying with drift (Timm-lite); (4) verbose-cipher
of real Latin+Italian (two known registers). Pre-specified predictions in
the accompanying note.
"""
import csv, random
import numpy as np
from collections import Counter

allowed = set("abcdefghiklmnopqrstxyz")
SPACE = 32
NU, UW, K = 12, 2000, 17
rng = random.Random(408)
npr = np.random.default_rng(408)

def h2_of(sb, space):
    a = np.frombuffer(sb, np.uint8); u = np.bincount(a, minlength=256).astype(float)
    p = u[u > 0] / u.sum(); h1 = -(p * np.log2(p)).sum()
    bg = a[:-1].astype(np.int32) * 256 + a[1:]; b = np.bincount(bg, minlength=65536).astype(float)
    q = b[b > 0] / b.sum(); return -(q * np.log2(q)).sum() - h1

class Env:
    def __init__(self, unitlists):
        syms = sorted(set(c for u in unitlists for w in u for c in w))
        self.sp = 0; self.code = {c: i + 1 for i, c in enumerate(syms)}; self.n0 = len(syms) + 1
        assert self.n0 + 60 < 256
    def stream(self, words):
        b = bytearray()
        for i, w in enumerate(words):
            if i: b.append(self.sp)
            for c in w: b.append(self.code[c])
        return bytes(b)
    def greedy(self, words, mm=K, topk=90):
        s = self.stream(words); nxt = self.n0; h = h2_of(s, self.sp); ops = []
        for _ in range(mm):
            a = np.frombuffer(s, np.uint8); m = (a[:-1] != self.sp) & (a[1:] != self.sp)
            cnt = Counter((a[:-1][m].astype(np.int32) * 256 + a[1:][m]).tolist()); best = None
            for pr, c in cnt.most_common(topk):
                x, y = pr // 256, pr % 256; cd = s.replace(bytes([x, y]), bytes([nxt])); ch = h2_of(cd, self.sp)
                if best is None or ch > best[0]: best = (ch, x, y, cd)
            if best is None or best[0] <= h: break
            h, x, y, s = best; ops.append((x, y, nxt)); nxt += 1
        return ops
    def apply(self, words, ops):
        s = self.stream(words)
        for x, y, n in ops: s = s.replace(bytes([x, y]), bytes([n]))
        return h2_of(s, self.sp)
    def rec(self, wi, own, oth):
        b = h2_of(self.stream(wi), self.sp); base = self.apply(wi, own) - b
        return (self.apply(wi, oth) - b) / base if base > 1e-9 else 1.0

def mapstats(units):
    env = Env(units); ops = [env.greedy(u) for u in units]
    n = len(units); S = np.eye(n)
    for i in range(n):
        for j in range(n):
            if i != j: S[i, j] = env.rec(units[i], ops[i], ops[j])
    S = (S + S.T) / 2
    D = 1 - S; J = np.eye(n) - np.ones((n, n)) / n; B = -0.5 * J @ (D**2) @ J
    ev = np.sort(np.linalg.eigvalsh(B))[::-1]; pos = ev[ev > 1e-9]
    ax1 = 100 * pos[0] / pos.sum() if len(pos) else float('nan')
    off = S[~np.eye(n, dtype=bool)]
    h2s = [h2_of(env.stream(u), env.sp) for u in units]
    return ax1, off.min() * 100, off.mean() * 100, min(h2s), max(h2s)

# ---------- real corpus: 12 units of 2000 words in section order ----------
cells = {}
order = ["H","H","H","H","P","C","C","B","B","S","S","S"]  # manuscript-ish flow, filled below
secw = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"): continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if w and all(c in allowed for c in w): secw.setdefault(row["section"], []).append(w)
allw = [w for v in secw.values() for w in v]
# real units: draw 2000-word blocks walking sections H,P,C,B,S to span the gradient
seq = []
for s in ["H","H","H","P","C","C","B","B","B","S","S","S"]:
    seq.append(s)
real_units = []
ptr = {s: 0 for s in secw}
for s in seq:
    pool = secw[s]; st = ptr[s]
    if st + UW > len(pool): st = rng.randrange(max(1, len(pool) - UW))
    real_units.append(pool[st:st + UW]); ptr[s] = st + UW
real_units = [u for u in real_units if len(u) >= UW - 200][:NU]

def bigram_counts(words, syms):
    idx = {c: i for i, c in enumerate([" "] + syms)}; K = len(idx)
    N = np.zeros((K, K))
    for w in words:
        p = 0
        for c in w:
            j = idx[c]; N[p, j] += 1; p = j
        N[p, 0] += 1
    return N, idx
def gen_from(N, idx, n_words):
    inv = {v: k for k, v in idx.items()}; P = (N + 0.05); P /= P.sum(1, keepdims=True)
    K = len(idx); out = []; cur = 0; w = ""
    while len(out) < n_words:
        cur = npr.choice(K, p=P[cur])
        if cur == 0:
            if w: out.append(w); w = ""
        else:
            w += inv[cur]
    return out

syms_all = sorted(set("".join(allw)))

# (1) random bigram: one model, 12 units
Nall, idxall = bigram_counts(allw, syms_all)
rb = gen_from(Nall, idxall, NU * UW); rand_units = [rb[i*UW:(i+1)*UW] for i in range(NU)]

# (2) section-mixture bigram: each real unit's section model
mix_units = []
for s in seq[:len(real_units)]:
    Ns, ix = bigram_counts(secw[s], syms_all); mix_units.append(gen_from(Ns, ix, UW))

# (3) self-copying with drift (Timm-lite)
seed = allw[:400][:]; text = seed[:]
p0, p1 = 0.03, 0.18; target = NU * UW
while len(text) < target:
    frac = len(text) / target; p = p0 + (p1 - p0) * frac
    w0 = rng.randrange(len(text) - 30); win = text[w0:w0 + rng.randint(8, 20)]
    for w in win:
        w = list(w)
        for k in range(len(w)):
            if rng.random() < p: w[k] = rng.choice(syms_all)
        if w and rng.random() < p * 0.5: w.append(rng.choice(syms_all))
        text.append("".join(w))
self_units = [text[i*UW:(i+1)*UW] for i in range(NU)]

# (4) verbose cipher of real Latin + Italian
def load_ref(path):
    t = open(path, encoding="utf-8", errors="replace").read().lower()
    return ["".join(c for c in w if c.isalpha()) for w in t.split() if any(ch.isalpha() for ch in w)]
lat = load_ref("Voynich-public/Corpora/Historical_texts/Secreta_Secretorum_LAT")
ita = load_ref("Voynich-public/Corpora/Historical_texts/Rettorica")
cipher = {}
vsyms = syms_all[:]
for ch in "abcdefghijklmnopqrstuvwxyz":
    k = rng.randint(1, 2); cipher[ch] = [rng.choice(vsyms) + (rng.choice(vsyms) if rng.random()<0.5 else "") for _ in range(k)]
def encipher(words):
    out = []
    for w in words:
        s = "".join(rng.choice(cipher.get(c, ["o"])) for c in w)
        if s: out.append(s)
    return out
lat_c = encipher(lat); ita_c = encipher(ita)
vc_units = ([lat_c[i*UW:(i+1)*UW] for i in range(6)] + [ita_c[i*UW:(i+1)*UW] for i in range(6)])
vc_units = [u for u in vc_units if len(u) >= UW - 300]

print(f"{'corpus':<26}{'axis1%':>8}{'minSim%':>9}{'meanSim%':>10}{'h2_lo':>7}{'h2_hi':>7}")
for name, U in [("REAL manuscript", real_units),
                ("random bigram (null)", rand_units),
                ("section-mixture bigram", mix_units),
                ("self-copying + drift", self_units),
                ("verbose Latin+Italian", vc_units)]:
    U = [u for u in U if len(u) >= UW - 300][:NU]
    a, mn, me, lo, hi = mapstats(U)
    print(f"{name:<26}{a:>8.1f}{mn:>9.1f}{me:>10.1f}{lo:>7.3f}{hi:>7.3f}")

import json
# rerun to capture for json
res = {}
for name, U in [("real", real_units), ("random_bigram", rand_units), ("section_mixture", mix_units),
                ("self_copying_drift", self_units), ("verbose_latin_italian", vc_units)]:
    U = [u for u in U if len(u) >= UW - 300][:NU]
    a, mn, me, lo, hi = mapstats(U)
    res[name] = {"axis1_pct": round(a,1), "min_sim_pct": round(mn,1), "mean_sim_pct": round(me,1),
                 "h2_lo": round(lo,3), "h2_hi": round(hi,3), "n_units": len(U)}
json.dump(res, open("exp13_results.json","w"), indent=2)
print("\nwrote exp13_results.json")
