import json, random, re, unicodedata
import numpy as np
from collections import Counter

BASE = "Voynich-public/Corpora"
random.seed(408)

def load_words(path, keep=None):
    txt = open(path, encoding="utf-8", errors="replace").read().lower()
    words = []
    for w in txt.split():
        w = "".join(c for c in w if c.isalpha())
        if not w:
            continue
        if keep and any(c not in keep for c in w):
            continue
        words.append(w)
    return words

def stats(stream_bytes):
    arr = np.frombuffer(stream_bytes, dtype=np.uint8)
    u = np.bincount(arr, minlength=256).astype(np.float64)
    n = u.sum()
    p = u[u > 0] / n
    h1 = -(p * np.log2(p)).sum()
    bg = arr[:-1].astype(np.int32) * 256 + arr[1:]
    b = np.bincount(bg, minlength=65536).astype(np.float64)
    q = b[b > 0] / b.sum()
    H2 = -(q * np.log2(q)).sum()
    return h1, H2 - h1, int((u > 0).sum())

def word_stats(words):
    chars = sum(len(w) for w in words)
    return chars / len(words)

def to_stream(words):
    return (" ".join(words)).encode("latin-1")

def ref_stream(words):
    txt = " ".join(words)
    mapping, nxt, out = {" ": 32}, 33, bytearray()
    for c in txt:
        if c not in mapping:
            mapping[c] = nxt
            nxt += 1
        out.append(mapping[c])
    return bytes(out)

voy_words_raw = load_words(f"{BASE}/Voynich_texts/Maximal Simplified/Full Voynich Maximal Simplified Text")
allowed = set("abcdefghiklmnopqrstxyzjuvw")
voy_words = [w for w in voy_words_raw if all(c in allowed for c in w)]
charset = sorted(set("".join(voy_words)))
print("Voynich words kept:", len(voy_words), "of", len(voy_words_raw), "| charset:", "".join(charset))

refs = {
    "Latin (Secreta Secretorum)": f"{BASE}/Historical_texts/Secreta_Secretorum_LAT",
    "Italian (Rettorica, 13th c.)": f"{BASE}/Historical_texts/Rettorica",
    "Middle English (Cirurgie)": f"{BASE}/Historical_texts/Cirurgie",
    "Hebrew (Genesis, unpointed)": f"{BASE}/Historical_texts/Hebrew_Bereshit",
}

print("\n=== calibration: my estimator vs Yale CSV (h1 / h2) ===")
ref_stats = {}
vs = to_stream(voy_words)
h1, h2, k = stats(vs)
print(f"Voynich MaxSimpText  mine: h1={h1:.3f} h2={h2:.3f} K={k} | CSV: 3.877/2.115")
voy_base = dict(h1=h1, h2=h2, K=k, cpw=word_stats(voy_words))
csv_vals = {"Latin (Secreta Secretorum)": (4.017, 3.277),
            "Italian (Rettorica, 13th c.)": (4.032, 3.141),
            "Middle English (Cirurgie)": (4.132, 3.240),
            "Hebrew (Genesis, unpointed)": (4.202, 3.526)}
for name, path in refs.items():
    w = load_words(path)
    rh1, rh2, rk = stats(ref_stream(w))
    ref_stats[name] = dict(h1=rh1, h2=rh2, K=rk, cpw=word_stats(w), nwords=len(w))
    c1, c2 = csv_vals[name]
    print(f"{name[:28]:28s} mine: h1={rh1:.3f} h2={rh2:.3f} K={rk} cpw={ref_stats[name]['cpw']:.2f} | CSV: {c1}/{c2}")

SPACE = 32
def expand_map():
    return {bytes([ord(c)]): c for c in charset}

def greedy_search(words, tag, max_merges=40, topk=90):
    stream = to_stream(words)
    names = {ord(c): c for c in charset}
    next_sym = 128
    h1, h2, K = stats(stream)
    tpw = (len(stream) - stream.count(b" ") * 0 + 0) 
    ntok = len(stream) - stream.count(b" ")
    nw = stream.count(b" ") + 1
    traj = [dict(step=0, token="", h1=round(h1, 4), h2=round(h2, 4), K=K, tpw=round(ntok / nw, 3))]
    for step in range(1, max_merges + 1):
        arr = np.frombuffer(stream, dtype=np.uint8)
        mask = (arr[:-1] != SPACE) & (arr[1:] != SPACE)
        bg = arr[:-1][mask].astype(np.int32) * 256 + arr[1:][mask]
        cnt = Counter(bg.tolist())
        best = None
        for pair, c in cnt.most_common(topk):
            a, b = pair // 256, pair % 256
            cand = stream.replace(bytes([a, b]), bytes([next_sym]))
            ch1, ch2, cK = stats(cand)
            if best is None or ch2 > best[0]:
                best = (ch2, ch1, cK, a, b, cand)
        if best is None or best[0] <= h2:
            break
        h2, h1, K, a, b, stream = best
        names[next_sym] = names[a] + names[b]
        tokname = names[next_sym]
        next_sym += 1
        ntok = len(stream) - stream.count(b" ")
        nw = stream.count(b" ") + 1
        traj.append(dict(step=step, token=tokname, h1=round(h1, 4), h2=round(h2, 4), K=K, tpw=round(ntok / nw, 3)))
    return traj

print("\n=== run A: greedy h2-maximising merge search on the real manuscript ===")
trajA = greedy_search(voy_words, "voynich")
for t in trajA:
    print(f"step {t['step']:2d}  +{t['token']:6s}  h1={t['h1']:.3f}  h2={t['h2']:.3f}  K={t['K']:2d}  tok/word={t['tpw']:.2f}")

print("\n=== run B (control): same search on meaningless bigram-Markov gibberish ===")
big = b" " + to_stream(voy_words) + b" "
arr = np.frombuffer(big, dtype=np.uint8)
trans = {}
for x, y in zip(arr[:-1], arr[1:]):
    trans.setdefault(int(x), []).append(int(y))
rng = random.Random(1404)
out, cur, target_len = [], SPACE, len(big)
while len(out) < target_len:
    cur = rng.choice(trans[cur])
    out.append(cur)
ctrl_stream = bytes(out).strip()
ctrl_words = ctrl_stream.decode("latin-1").split()
ctrl_words = [w for w in ctrl_words if w]
ch1, ch2, cK = stats(to_stream(ctrl_words))
print(f"control baseline: h1={ch1:.3f} h2={ch2:.3f} (voynich baseline h2={voy_base['h2']:.3f})")
trajB = greedy_search(ctrl_words, "markov")
for t in trajB[::5] + [trajB[-1]]:
    print(f"step {t['step']:2d}  +{t['token']:6s}  h1={t['h1']:.3f}  h2={t['h2']:.3f}  K={t['K']:2d}  tok/word={t['tpw']:.2f}")

print("\n=== per-language alignment along the Voynich trajectory ===")
align = {}
for name, r in ref_stats.items():
    hit = None
    for t in trajA:
        if t["h2"] >= r["h2"]:
            hit = t
            break
    align[name] = dict(ref=r, hit=hit)
    if hit:
        print(f"{name[:28]:28s} target h2={r['h2']:.3f} reached at merge {hit['step']} | inv K={hit['K']} vs alphabet {r['K']} | tok/word={hit['tpw']:.2f} vs letters/word={r['cpw']:.2f}")
    else:
        print(f"{name[:28]:28s} target h2={r['h2']:.3f} NOT reached (max {trajA[-1]['h2']:.3f})")

json.dump(dict(voy_base=voy_base, refs=ref_stats, trajA=trajA, trajB=trajB), open("results.json", "w"), indent=1)
print("\nsaved results.json")
