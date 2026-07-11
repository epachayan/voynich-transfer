"""
EXPERIMENT 21b -- robustness of the calibration ladder (re-draw) + labeled matrix.
Two additions to Exp 21:
  (a) fully labeled pair matrix (which works are similar to which);
  (b) a SECOND, non-overlapping draw of units from each work (offset blocks),
      to check the ladder is not an artifact of the particular 2000-word
      blocks sampled in Exp 21.

PRE-SPECIFIED PREDICTIONS:
  P5 re-draw ladder: tier ordering T0 > T1 > T2 holds on the second draw.
  P6 re-draw placement: T2 (different-language) mean < 0.77 on the second draw.

Run from repo root: python scripts/exp21b_ladder_robustness.py
Writes results/exp21b_results.json
"""
import json, random
import numpy as np
from collections import Counter

NU, UW, K = 12, 2000, 17
rng = random.Random(408)

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

def load_ref(path):
    t = open(path, encoding="utf-8", errors="replace").read().lower()
    ws = ["".join(c for c in w if c.isalpha() and c.isascii()) for w in t.split()]
    return [w for w in ws if w]

BASE = "Voynich-public/Corpora/Historical_texts"
works = {
    "LAT_SS":   load_ref(f"{BASE}/Secreta_Secretorum_LAT"),
    "LAT_AIX":  load_ref(f"{BASE}/Latin_Aix"),
    "LAT_PIC":  load_ref(f"{BASE}/Picatrix"),
    "ITA_RET":  load_ref(f"{BASE}/Rettorica"),
    "ENG_SS":   load_ref(f"{BASE}/Secreta_Secretorum_ENG"),
    "ENG_ALPH": load_ref(f"{BASE}/AlphabetOfTales"),
}
lang = {k: k.split("_")[0] for k in works}

def build(draw):
    """draw 0 = blocks at start (Exp 21); draw 1 = offset, non-overlapping blocks."""
    labels, units = [], []
    for name, ws in works.items():
        need = 2 * UW
        off = 0 if draw == 0 else min(need + 1000, max(0, len(ws) - need - 1))
        for i in range(2):
            labels.append(name); units.append(ws[off + i*UW: off + (i+1)*UW])
    return labels, units

def ladder(labels, units):
    env = Env(units); ops = [env.greedy(u) for u in units]
    n = len(units); S = np.eye(n)
    for i in range(n):
        for j in range(n):
            if i != j: S[i, j] = env.rec(units[i], ops[i], ops[j])
    S = (S + S.T)/2
    tiers = {"T0": [], "T1": [], "T2": []}
    for i in range(n):
        for j in range(i+1, n):
            t = "T0" if labels[i] == labels[j] else ("T1" if lang[labels[i]] == lang[labels[j]] else "T2")
            tiers[t].append(S[i, j])
    return S, {k: float(np.mean(v)) for k, v in tiers.items()}

print("EXPERIMENT 21b -- ladder robustness (re-draw) + labeled matrix")
print("Pre-specified: P5 re-draw T0>T1>T2 | P6 re-draw T2 < 0.77\n")

labels0, units0 = build(0)
S0, t0 = ladder(labels0, units0)

# labeled work-level matrix from draw 0 (mean of the 2x2 unit block per work pair)
worklist = list(works)
print("work-level mean recovery (draw 0):")
print(f"{'':<10}" + "".join(f"{w:>10}" for w in worklist))
M = {}
for a in worklist:
    row = f"{a:<10}"
    for b in worklist:
        ia = [i for i, l in enumerate(labels0) if l == a]
        ib = [i for i, l in enumerate(labels0) if l == b]
        vals = [S0[i, j] for i in ia for j in ib if i != j]
        m = float(np.mean(vals)); M[f"{a}|{b}"] = round(m, 3)
        row += f"{m:>10.3f}"
    print(row)

labels1, units1 = build(1)
S1, t1 = ladder(labels1, units1)

print(f"\nladder draw 0 (Exp 21 blocks):  T0={t0['T0']:.3f}  T1={t0['T1']:.3f}  T2={t0['T2']:.3f}")
print(f"ladder draw 1 (offset blocks):  T0={t1['T0']:.3f}  T1={t1['T1']:.3f}  T2={t1['T2']:.3f}")

P5 = t1["T0"] > t1["T1"] > t1["T2"]
P6 = t1["T2"] < 0.77
print("\nverdicts:")
print(f"  P5 re-draw ladder monotone : {'PASS' if P5 else 'FAIL'}")
print(f"  P6 re-draw diff-language {t1['T2']:.3f} < 0.77 : {'PASS' if P6 else 'FAIL'}")

json.dump({
    "draw0_tiers": {k: round(v, 3) for k, v in t0.items()},
    "draw1_tiers": {k: round(v, 3) for k, v in t1.items()},
    "work_matrix_draw0": M,
    "verdicts": {"P5_redraw_ladder": bool(P5), "P6_redraw_T2_below_077": bool(P6)},
}, open("results/exp21b_results.json", "w"), indent=1)
print("\nsaved results/exp21b_results.json")
