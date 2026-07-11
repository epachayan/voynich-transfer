"""EXP 14 leave-one-section-out (is Pharma-midpoint / the axis baked in?)
   EXP 15 shuffle nulls (word-order vs glyph-structure): what carries the gradient?"""
import csv, random
import numpy as np
from collections import Counter
allowed=set("abcdefghiklmnopqrstxyz"); SPACE=32; K=17; UW=2000; NU=12
rng=random.Random(408)

def h2(sb):
    a=np.frombuffer(sb,np.uint8);u=np.bincount(a,minlength=256).astype(float)
    p=u[u>0]/u.sum();h1=-(p*np.log2(p)).sum()
    bg=a[:-1].astype(np.int32)*256+a[1:];b=np.bincount(bg,minlength=65536).astype(float)
    q=b[b>0]/b.sum();return -(q*np.log2(q)).sum()-h1
def strm(ws): return (" ".join(ws)).encode("latin-1")
def greedy(ws,mm=40,topk=90):
    s=strm(ws);nxt=128;h=h2(s);ops=[]
    for _ in range(mm):
        a=np.frombuffer(s,np.uint8);m=(a[:-1]!=SPACE)&(a[1:]!=SPACE)
        cnt=Counter((a[:-1][m].astype(np.int32)*256+a[1:][m]).tolist());best=None
        for pr,c in cnt.most_common(topk):
            x,y=pr//256,pr%256;cd=s.replace(bytes([x,y]),bytes([nxt]));ch=h2(cd)
            if best is None or ch>best[0]:best=(ch,x,y,cd)
        if best is None or best[0]<=h:break
        h,x,y,s=best;ops.append((x,y,nxt));nxt+=1
    return ops
def tvec(ws,ops):
    s=strm(ws)
    for x,y,n in ops:s=s.replace(bytes([x,y]),bytes([n]))
    a=np.frombuffer(s,np.uint8);c=np.bincount(a,minlength=256).astype(float);c[SPACE]=0
    t=c.sum();return c/t if t else c

secw={}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f,delimiter="\t"):
        if row["transcriber"]!="H" or not row["placement"].startswith("P"):continue
        w="".join(c for c in row["word"].lower() if c.isalpha())
        if w and all(c in allowed for c in w):secw.setdefault(row["section"],[]).append(w)
allw=[w for v in secw.values() for w in v]

# ---------- EXP 14: leave-one-section-out ----------
print("="*60); print("EXP 14  leave-one-section-out coordinates")
# in-sample reference: inventory on all, axis HA->BB
ops_all=greedy(allw); vHA=tvec(secw["H"],ops_all); vBB=tvec(secw["B"],ops_all)
u=vBB-vHA; den=float(u@u)
def coord_ref(ws): return float((tvec(ws,ops_all)-vHA)@u)/den
insample={s:coord_ref(secw[s]) for s in ["H","P","C","B","S"]}
print(f"{'section':<9}{'in-sample':>11}{'LOO':>9}{'delta':>8}  note")
for s in ["P","C","S"]:  # non-pole: rebuild inventory without s, axis intact
    rest=[w for k,ws in secw.items() if k!=s for w in ws]
    o=greedy(rest); a=tvec(secw["H"],o); b=tvec(secw["B"],o); uu=b-a; dd=float(uu@uu)
    c=float((tvec(secw[s],o)-a)@uu)/dd
    print(f"{s:<9}{insample[s]:>+11.2f}{c:>+9.2f}{c-insample[s]:>+8.2f}  inventory rebuilt w/o {s}")
# pole sections: split-half, define pole from half, project other half
for s,lbl in [("H","A-pole"),("B","B-pole")]:
    half=len(secw[s])//2; h1w,h2w=secw[s][:half],secw[s][half:]
    if s=="H": a=tvec(h1w,ops_all); b=vBB
    else: a=vHA; b=tvec(h1w,ops_all)
    uu=b-a; dd=float(uu@uu); c=float((tvec(h2w,ops_all)-a)@uu)/dd
    print(f"{s+'(half)':<9}{insample[s]:>+11.2f}{c:>+9.2f}{c-insample[s]:>+8.2f}  {lbl} from half, project other half")

# ---------- EXP 15: shuffle nulls ----------
print("\n"+"="*60); print("EXP 15  shuffle nulls: 12x12 map axis-1% and min-similarity")
seq=["H","H","H","P","C","C","B","B","B","S","S","S"]
def build_units(transform=None):
    U=[]; ptr={s:0 for s in secw}
    for s in seq:
        pool=secw[s]; st=ptr[s]
        if st+UW>len(pool): st=rng.randrange(max(1,len(pool)-UW))
        blk=pool[st:st+UW]; ptr[s]=st+UW
        U.append(transform(blk) if transform else blk)
    return [x for x in U if len(x)>=UW-200][:NU]
def word_order_shuffle(ws):
    w=ws[:]; rng.shuffle(w); return w
def glyph_shuffle(ws):  # preserve each word's length + section unigram glyph freq; destroy within-word bigrams
    pool=list("".join(ws)); rng.shuffle(pool); out=[]; i=0
    for w in ws: out.append("".join(pool[i:i+len(w)])); i+=len(w)
    return out
def mapstats(U):
    sm=sorted(set(c for x in U for w in x for c in w)); code={c:i+1 for i,c in enumerate(sm)}; n0=len(sm)+1
    def st(ws):
        b=bytearray()
        for i,w in enumerate(ws):
            if i:b.append(0)
            for c in w:b.append(code[c])
        return bytes(b)
    def h2b(sb):
        a=np.frombuffer(sb,np.uint8);uu=np.bincount(a,minlength=256).astype(float)
        p=uu[uu>0]/uu.sum();h1=-(p*np.log2(p)).sum()
        bg=a[:-1].astype(np.int32)*256+a[1:];b=np.bincount(bg,minlength=65536).astype(float)
        q=b[b>0]/b.sum();return -(q*np.log2(q)).sum()-h1
    def gr(ws,mm=K):
        s=st(ws);nxt=n0;h=h2b(s);ops=[]
        for _ in range(mm):
            a=np.frombuffer(s,np.uint8);m=(a[:-1]!=0)&(a[1:]!=0)
            cnt=Counter((a[:-1][m].astype(np.int32)*256+a[1:][m]).tolist());best=None
            for pr,c in cnt.most_common(90):
                x,y=pr//256,pr%256;cd=s.replace(bytes([x,y]),bytes([nxt]));ch=h2b(cd)
                if best is None or ch>best[0]:best=(ch,x,y,cd)
            if best is None or best[0]<=h:break
            h,x,y,s=best;ops.append((x,y,nxt));nxt+=1
        return ops
    def ap(ws,ops):
        s=st(ws)
        for x,y,n in ops:s=s.replace(bytes([x,y]),bytes([n]))
        return h2b(s)
    ops=[gr(x) for x in U]; n=len(U); S=np.eye(n)
    for i in range(n):
        bi=h2b(st(U[i])); base=ap(U[i],ops[i])-bi
        for j in range(n):
            if i!=j: S[i,j]=(ap(U[i],ops[j])-bi)/base if base>1e-9 else 1.0
    S=(S+S.T)/2; D=1-S; J=np.eye(n)-np.ones((n,n))/n; B=-0.5*J@(D**2)@J
    ev=np.sort(np.linalg.eigvalsh(B))[::-1]; pos=ev[ev>1e-9]
    off=S[~np.eye(n,dtype=bool)]
    return 100*pos[0]/pos.sum(), off.min()*100
base_ax,base_mn=mapstats(build_units())
wo_ax,wo_mn=mapstats(build_units(word_order_shuffle))
gs_ax,gs_mn=mapstats(build_units(glyph_shuffle))
print(f"{'condition':<34}{'axis1%':>8}{'minSim%':>9}")
print(f"{'real (unshuffled)':<34}{base_ax:>8.1f}{base_mn:>9.1f}")
print(f"{'word-order shuffled within units':<34}{wo_ax:>8.1f}{wo_mn:>9.1f}")
print(f"{'glyph shuffled (lengths+freq kept)':<34}{gs_ax:>8.1f}{gs_mn:>9.1f}")

import json
json.dump({"exp14_leave_one_out":{s:{"in_sample":round(insample[s],3)} for s in insample},
           "exp15_shuffle":{"real":[round(base_ax,1),round(base_mn,1)],
                            "word_order_shuffle":[round(wo_ax,1),round(wo_mn,1)],
                            "glyph_shuffle":[round(gs_ax,1),round(gs_mn,1)]}},
          open("exp14_15_results.json","w"),indent=2)
print("\nwrote exp14_15_results.json")

# --- corrected JSON: include leave-one-out values (review fix #3) ---
import json as _j
_loo={}
for _s in ["P","C","S"]:
    _rest=[w for k,ws in secw.items() if k!=_s for w in ws]
    _o=greedy(_rest); _a=tvec(secw["H"],_o); _b=tvec(secw["B"],_o); _uu=_b-_a; _dd=float(_uu@_uu)
    _loo[_s]=round(float((tvec(secw[_s],_o)-_a)@_uu)/_dd,3)
for _s in ["H","B"]:
    _half=len(secw[_s])//2; _h1=secw[_s][:_half]; _h2=secw[_s][_half:]
    if _s=="H": _a=tvec(_h1,ops_all); _b=vBB
    else: _a=vHA; _b=tvec(_h1,ops_all)
    _uu=_b-_a; _dd=float(_uu@_uu); _loo[_s+"_half"]=round(float((tvec(_h2,ops_all)-_a)@_uu)/_dd,3)
_out={"exp14_leave_one_section_out":{_s:{"in_sample":round(insample[_s],3),
        "leave_one_out":_loo.get(_s,_loo.get(_s+"_half"))} for _s in insample},
      "exp15_shuffle":{"real":[round(base_ax,1),round(base_mn,1)],
                       "word_order_shuffle":[round(wo_ax,1),round(wo_mn,1)],
                       "glyph_shuffle":[round(gs_ax,1),round(gs_mn,1)]}}
_j.dump(_out,open("exp14_15_results.json","w"),indent=2)
print("rewrote exp14_15_results.json with leave-one-out values")
