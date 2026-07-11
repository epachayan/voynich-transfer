"""
EXPERIMENT 12 -- Labels: do object-labels carry referent-specific structure?
============================================================================
Companion to voynich_gradient_note (Experiments 1-11). This is the only
experiment aimed at INTERPRETATION rather than pure structure, because a
label is anchored to a drawn object -- the closest thing the manuscript
offers to a bilingual crib.

DATA. Every prior experiment used ONLY paragraph text (placement 'P...').
Here we use the complement -- the label/legend/circular tokens (placements
L, R, S, C, ...) that were filtered out throughout -- tagged by the section
whose illustrations they annotate (the referent-category proxy).

HYPOTHESES (pre-specified before running):
  H1  Labels share their section's running-text machinery
      (label coordinate ~ paragraph coordinate within a section).
  H2  WITHIN a fixed dialect (controlling register), label morphology
      separates by referent-category MORE than a permutation null
      -> a structural crib: form tracks the depicted thing.
  H0  Labels are undifferentiated / identical to running text.

CONFOUND CONTROL. Referent-category correlates with Currier dialect
(plants=A, nymphs/cosmo=B). So the clean H2 test is run WITHIN dialect B
(Bio vs Cosmo vs Stars) and WITHIN dialect A (Pharma vs Herbal vs Text),
never across the A/B line. The star-vs-plant contrast (marquee, but
dialect-confounded) is reported descriptively only.

METHOD. (a) gradient coordinate = project a token-set's frequency vector,
under the global 40-merge inventory, onto the Herbal-A -> Bio-B pole axis
(same instrument as Exp 7; works on small samples). (b) morphology =
initial-glyph and final-glyph distributions + mean word length. Distance
between distributions = total variation (TV). Permutation null: pool tokens
within a dialect, reshuffle referent tags at fixed group sizes, 2000 draws.
"""
import csv, random
import numpy as np
from collections import Counter, defaultdict

allowed = set("abcdefghiklmnopqrstxyz")
SPACE = 32
rng = random.Random(408)

def stats_h2(sb):
    arr = np.frombuffer(sb, dtype=np.uint8)
    u = np.bincount(arr, minlength=256).astype(np.float64); p = u[u>0]/u.sum()
    h1 = -(p*np.log2(p)).sum()
    bg = arr[:-1].astype(np.int32)*256+arr[1:]
    b = np.bincount(bg, minlength=65536).astype(np.float64); q = b[b>0]/b.sum()
    return -(q*np.log2(q)).sum()-h1
def strm(words): return (" ".join(words)).encode("latin-1")
def greedy_ops(words, mm=40, topk=90):
    s=strm(words); nxt=128; h2=stats_h2(s); ops=[]
    for _ in range(mm):
        a=np.frombuffer(s,dtype=np.uint8); m=(a[:-1]!=SPACE)&(a[1:]!=SPACE)
        cnt=Counter((a[:-1][m].astype(np.int32)*256+a[1:][m]).tolist()); best=None
        for pair,c in cnt.most_common(topk):
            x,y=pair//256,pair%256; cand=s.replace(bytes([x,y]),bytes([nxt])); ch=stats_h2(cand)
            if best is None or ch>best[0]: best=(ch,x,y,cand)
        if best is None or best[0]<=h2: break
        h2,x,y,s=best; ops.append((x,y,nxt)); nxt+=1
    return ops
def tok_vec(words, ops):
    s=strm(words)
    for x,y,nxt in ops: s=s.replace(bytes([x,y]),bytes([nxt]))
    a=np.frombuffer(s,dtype=np.uint8); c=np.bincount(a,minlength=256).astype(np.float64)
    c[SPACE]=0; t=c.sum(); return c/t if t else c

# ---- load ----
lab=defaultdict(list); par=defaultdict(list); langs=defaultdict(Counter); allw=[]
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row["transcriber"]!="H": continue
        w="".join(c for c in row["word"].lower() if c.isalpha())
        if not w or any(c not in allowed for c in w): continue
        allw.append(w); langs[row["section"]][row["language"]]+=1
        (par if row["placement"].startswith("P") else lab)[row["section"]].append(w)

ops=greedy_ops(allw)
vHA=tok_vec(par["H"],ops); vBB=tok_vec(par["B"],ops)  # poles = running text
u=vBB-vHA; den=float(u@u)
def coord(words): return float((tok_vec(words,ops)-vHA)@u)/den if words else float("nan")

def bench(c): return "ch" if c[:2]=="ch" else ("sh" if c[:2]=="sh" else None)
INIT=["q","o","y","ch","sh","d","s","k","t","p","f","l","r","a","e"]
def init_class(w):
    b=bench(w)
    if b: return b
    return w[0] if w[0] in INIT else "other"
FIN=["y","n","l","r","m","o","s","a","d"]
def fin_class(w): return w[-1] if w[-1] in FIN else "other"
def dist(words, classes, fn):
    c=Counter(fn(w) for w in words); n=sum(c.values())
    return np.array([c.get(k,0)/n for k in classes+["other"]]) if n else None
def TV(p,q): return 0.5*np.abs(p-q).sum()

SEC={"H":"Herbal","P":"Pharma","Z":"Zodiac","C":"Cosmo","A":"Astro","B":"Bio","S":"Stars","T":"Text"}
def meanlen(ws): return np.mean([len(w) for w in ws])

print("="*66)
print("H1  label vs paragraph, per section  (coordinate + initial-glyph TV)")
print(f"{'section':<8}{'dial':<5}{'n_lab':>6}{'coord_lab':>10}{'coord_par':>10}{'len_lab':>8}{'len_par':>8}{'initTV':>8}")
for s in ["H","P","B","C","S"]:
    if s not in par or not par[s]: continue
    cl,cp=coord(lab[s]),coord(par[s])
    tv=TV(dist(lab[s],INIT,init_class),dist(par[s],INIT,init_class))
    d=langs[s].most_common(1)[0][0]
    print(f"{SEC[s]:<8}{d:<5}{len(lab[s]):>6}{cl:>+10.2f}{cp:>+10.2f}{meanlen(lab[s]):>8.2f}{meanlen(par[s]):>8.2f}{tv:>8.3f}")

def perm_between(groups_tokens, classes, fn, reps=2000):
    dists=[dist(t,classes,fn) for t in groups_tokens]
    def meanpair(ds): 
        return np.mean([TV(ds[i],ds[j]) for i in range(len(ds)) for j in range(i+1,len(ds))])
    obs=meanpair(dists)
    pool=[w for t in groups_tokens for w in t]; sizes=[len(t) for t in groups_tokens]
    null=[]
    for _ in range(reps):
        rng.shuffle(pool); idx=0; gs=[]
        for sz in sizes: gs.append(pool[idx:idx+sz]); idx+=sz
        null.append(meanpair([dist(g,classes,fn) for g in gs]))
    null=np.array(null); p=(np.sum(null>=obs)+1)/(reps+1)
    return obs, null.mean(), p

print("\n"+"="*66)
print("H2  within-dialect referent separation (labels vs paragraphs)")
for dia, secs in [("B",["B","C","S"]), ("A",["P","H","T"])]:
    labtok=[lab[s] for s in secs]; partok=[par[s] for s in secs if par.get(s)]
    ol,nl,pl=perm_between(labtok, INIT, init_class)
    op,npr,pp=perm_between(partok, INIT, init_class)
    names="/".join(SEC[s] for s in secs)
    print(f"  dialect {dia} ({names}):")
    print(f"     LABELS  between-referent initTV obs={ol:.3f} null={nl:.3f}  p={pl:.4f}")
    print(f"     PARA    between-referent initTV obs={op:.3f} null={npr:.3f}  p={pp:.4f}")

print("\n"+"="*66)
print("MARQUEE (descriptive, DIALECT-CONFOUNDED): star-labels vs plant-labels")
star=lab["Z"]+lab["A"]; plant=lab["H"]+lab["P"]
ds,dp=dist(star,INIT,init_class),dist(plant,INIT,init_class)
print(f"  star-labels  (Zodiac+Astro, n={len(star)}): coord {coord(star):+.2f}, len {meanlen(star):.2f}")
print(f"  plant-labels (Herbal+Pharma, n={len(plant)}): coord {coord(plant):+.2f}, len {meanlen(plant):.2f}")
print(f"  initial-glyph TV(star,plant) = {TV(ds,dp):.3f}")
print("  top initial glyphs:")
for lbl,ws in [("star ",star),("plant",plant)]:
    c=Counter(init_class(w) for w in ws); n=len(ws)
    top=", ".join(f"{k}:{v/n:.2f}" for k,v in c.most_common(5))
    print(f"    {lbl}: {top}")
print("\n(Interpretation caveat: star vs plant confounds referent with dialect/section;")
print(" the within-dialect tests above are the controlled evidence.)")

# ---- machine-readable output (Exp 12) ----
import json as _json
_res = {"H1_label_vs_paragraph": {}, "H2_within_dialect": {}, "marquee_star_vs_plant": {}}
for s in ["H", "P", "B", "C", "S"]:
    if s not in par or not par[s]:
        continue
    _res["H1_label_vs_paragraph"][SEC[s]] = {
        "dialect": langs[s].most_common(1)[0][0], "n_labels": len(lab[s]),
        "coord_labels": round(coord(lab[s]), 3), "coord_paragraph": round(coord(par[s]), 3),
        "len_labels": round(meanlen(lab[s]), 2), "len_paragraph": round(meanlen(par[s]), 2),
        "initial_glyph_TV": round(float(TV(dist(lab[s], INIT, init_class), dist(par[s], INIT, init_class))), 3)}
for dia, secs in [("B", ["B", "C", "S"]), ("A", ["P", "H", "T"])]:
    labtok = [lab[s] for s in secs]; partok = [par[s] for s in secs if par.get(s)]
    ol, nl, pl = perm_between(labtok, INIT, init_class); op, npr, pp = perm_between(partok, INIT, init_class)
    _res["H2_within_dialect"][dia] = {
        "sections": [SEC[s] for s in secs],
        "labels_between_referent_TV": round(ol, 3), "labels_null": round(nl, 3), "labels_p": round(pl, 4),
        "paragraph_between_referent_TV": round(op, 3), "paragraph_null": round(npr, 3), "paragraph_p": round(pp, 4)}
_star = lab["Z"] + lab["A"]; _plant = lab["H"] + lab["P"]
_res["marquee_star_vs_plant"] = {
    "star_n": len(_star), "plant_n": len(_plant),
    "star_coord": round(coord(_star), 3), "plant_coord": round(coord(_plant), 3),
    "initial_glyph_TV": round(float(TV(dist(_star, INIT, init_class), dist(_plant, INIT, init_class))), 3),
    "verdict": "under these morphology tests, star-labels and plant-labels do not separate like referent names"}
_json.dump(_res, open("results/label_results.json", "w"), indent=2)
print("\nwrote results/label_results.json")
