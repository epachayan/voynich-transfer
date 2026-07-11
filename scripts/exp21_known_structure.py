"""
EXPERIMENT 21 -- Known-structure positive control ("calibration ladder").
Question: does merge-transfer similarity recover KNOWN structure in real
texts whose internal divisions are independently established? This is the
construct-validation step: every prior experiment showed the metric behaves
consistently on the Voynich; this one tests it against ground truth.

Design: 12 units x 2000 words (identical pipeline to Exp 13: k=17 greedy
merges, pairwise recovery, symmetrised, classical MDS), drawn from works of
KNOWN language and identity in the same corpus package:
  LAT_SS   x2  Secreta Secretorum, Latin
  LAT_AIX  x2  Aix chronicle, Latin
  LAT_PIC  x2  Picatrix, Latin
  ITA_RET  x2  Rettorica (Brunetto Latini), Italian
  ENG_SS   x2  Secreta Secretorum, Middle English   <- same CONTENT as LAT_SS
  ENG_ALPH x2  Alphabet of Tales, Middle English

Tiers: T0 same work | T1 same language, different work | T2 different language.
LAT_SS <-> ENG_SS is the topic control: same content, different language.

PRE-SPECIFIED PREDICTIONS (declared before running):
  P1 coherence:  T0 (same-work) mean recovery >= 0.90.
  P2 ladder:     strict ordering of tier means T0 > T1 > T2.
  P3 placement:  T2 (different-language) mean recovery < 0.77, i.e. BELOW
                 the Voynich Currier A<->B transfer (0.77-0.80 at k=17,
                 Exp 2). If so, A<->B is SMALLER than a language gap --
                 consistent with registers/dialects of one system, not two
                 languages. Falsification (T2 >= 0.77) would be important:
                 it would say the A/B gap is language-sized.
  P4 geometry:   the known two-language corpus shows CLUSTER structure,
                 not a filled gradient: max-gap/range of MDS axis-1
                 coordinates > the Voynich real-unit value (the Voynich
                 axis is filled -- Pharma sits mid-axis, Exp 6/7).

Run from repo root: python scripts/exp21_known_structure.py
Writes results/exp21_results.json
"""
import csv, json, random
import numpy as np
from collections import Counter

allowed = set("abcdefghiklmnopqrstxyz")
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
        assert self.n0 + 60 < 256, f"alphabet too large: {self.n0}"
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

def blocks(words, n, offset=0):
    return [words[offset + i*UW : offset + (i+1)*UW] for i in range(n)]

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
labels, units = [], []
for name, ws in works.items():
    assert len(ws) >= 2*UW + 500, f"{name} too short: {len(ws)}"
    for b in blocks(ws, 2):
        labels.append(name); units.append(b)
assert len(units) == NU

print("EXPERIMENT 21 -- known-structure positive control (calibration ladder)")
print("Pre-specified: P1 same-work>=0.90 | P2 T0>T1>T2 | P3 T2<0.77 (A<->B above language gap) | P4 known corpus max-gap > Voynich max-gap\n")

env = Env(units)
ops = [env.greedy(u) for u in units]
n = len(units)
S = np.eye(n)
for i in range(n):
    for j in range(n):
        if i != j: S[i, j] = env.rec(units[i], ops[i], ops[j])
S = (S + S.T) / 2

def tier(i, j):
    if labels[i] == labels[j]: return "T0_same_work"
    if lang[labels[i]] == lang[labels[j]]: return "T1_same_lang"
    return "T2_diff_lang"

tiers = {"T0_same_work": [], "T1_same_lang": [], "T2_diff_lang": []}
topic_ctrl = []   # LAT_SS <-> ENG_SS: same content, different language
for i in range(n):
    for j in range(i+1, n):
        tiers[tier(i, j)].append(S[i, j])
        if {labels[i], labels[j]} == {"LAT_SS", "ENG_SS"}: topic_ctrl.append(S[i, j])

tm = {k: float(np.mean(v)) for k, v in tiers.items()}
print(f"{'tier':<16}{'n_pairs':>8}{'mean':>8}{'min':>8}{'max':>8}")
for k, v in tiers.items():
    print(f"{k:<16}{len(v):>8}{np.mean(v):>8.3f}{np.min(v):>8.3f}{np.max(v):>8.3f}")
print(f"{'topic control (LAT_SS<->ENG_SS, same content diff lang)':<52}{np.mean(topic_ctrl):>8.3f}")

# per-language-pair detail
pairsets = {}
for i in range(n):
    for j in range(i+1, n):
        if labels[i] != labels[j]:
            key = "<->".join(sorted({lang[labels[i]], lang[labels[j]]})) if lang[labels[i]] != lang[labels[j]] \
                  else lang[labels[i]] + " (cross-work)"
            pairsets.setdefault(key, []).append(S[i, j])
print("\nper language pair:")
for k in sorted(pairsets): print(f"  {k:<22}{np.mean(pairsets[k]):>7.3f}")

# ---- geometry: MDS axis-1 and gap statistic, known corpus vs Voynich ----
def mds_axis1(Smat):
    D = 1 - Smat; nn = len(Smat); J = np.eye(nn) - np.ones((nn, nn))/nn
    B = -0.5 * J @ (D**2) @ J
    ev, V = np.linalg.eigh(B); order = np.argsort(ev)[::-1]
    ev, V = ev[order], V[:, order]
    ax1pct = 100*ev[0]/ev[ev > 1e-9].sum()
    coord = V[:, 0]*np.sqrt(max(ev[0], 0))
    c = np.sort(coord); gaps = np.diff(c)
    return ax1pct, float(gaps.max()/(c[-1]-c[0])) if c[-1] > c[0] else 0.0, coord

ax1_known, gap_known, coord_known = mds_axis1(S)

# Voynich real units, constructed exactly as Exp 13 (same seed/protocol)
secw = {}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"] != "H" or not row["placement"].startswith("P"): continue
        w = "".join(c for c in row["word"].lower() if c.isalpha())
        if w and all(c in allowed for c in w): secw.setdefault(row["section"], []).append(w)
seq = ["H","H","H","P","C","C","B","B","B","S","S","S"]
real_units, ptr = [], {s: 0 for s in secw}
for s in seq:
    pool = secw[s]; st = ptr[s]
    if st + UW > len(pool): st = rng.randrange(max(1, len(pool) - UW))
    real_units.append(pool[st:st+UW]); ptr[s] = st + UW
real_units = [u for u in real_units if len(u) >= UW - 200][:NU]
envV = Env(real_units)
opsV = [envV.greedy(u) for u in real_units]
nV = len(real_units); SV = np.eye(nV)
for i in range(nV):
    for j in range(nV):
        if i != j: SV[i, j] = envV.rec(real_units[i], opsV[i], opsV[j])
SV = (SV + SV.T)/2
ax1_v, gap_v, coord_v = mds_axis1(SV)

print(f"\ngeometry:  known 2-language corpus  axis1={ax1_known:.1f}%  max-gap/range={gap_known:.3f}")
print(f"           Voynich real units       axis1={ax1_v:.1f}%  max-gap/range={gap_v:.3f}")

# ---- verdicts ----
P1 = tm["T0_same_work"] >= 0.90
P2 = tm["T0_same_work"] > tm["T1_same_lang"] > tm["T2_diff_lang"]
P3 = tm["T2_diff_lang"] < 0.77
P4 = gap_known > gap_v
print("\nverdicts:")
print(f"  P1 same-work mean {tm['T0_same_work']:.3f} >= 0.90 : {'PASS' if P1 else 'FAIL'}")
print(f"  P2 ladder {tm['T0_same_work']:.3f} > {tm['T1_same_lang']:.3f} > {tm['T2_diff_lang']:.3f} : {'PASS' if P2 else 'FAIL'}")
print(f"  P3 diff-language {tm['T2_diff_lang']:.3f} < 0.77 (Voynich A<->B) : {'PASS' if P3 else 'FAIL'}")
print(f"  P4 known max-gap {gap_known:.3f} > Voynich {gap_v:.3f} : {'PASS' if P4 else 'FAIL'}")

json.dump({
    "design": {"units": labels, "unit_words": UW, "k": K},
    "tier_means": tm,
    "tier_detail": {k: [round(float(x), 3) for x in v] for k, v in tiers.items()},
    "topic_control_LATSS_ENGSS": round(float(np.mean(topic_ctrl)), 3),
    "language_pairs": {k: round(float(np.mean(v)), 3) for k, v in pairsets.items()},
    "geometry": {"known_axis1_pct": round(float(ax1_known), 1), "known_maxgap_over_range": round(gap_known, 3),
                  "voynich_axis1_pct": round(float(ax1_v), 1), "voynich_maxgap_over_range": round(gap_v, 3),
                  "known_axis1_coords": {f"{labels[i]}_{i%2}": round(float(coord_known[i]), 3) for i in range(n)}},
    "verdicts": {"P1_same_work_ge_090": bool(P1), "P2_ladder_monotone": bool(P2),
                  "P3_difflang_below_voynich_AB": bool(P3), "P4_known_gappier_than_voynich": bool(P4)},
    "reference": {"voynich_AB_recovery_k17": 0.77, "source": "Exp 2"},
}, open("results/exp21_results.json", "w"), indent=1)
print("\nsaved results/exp21_results.json")
