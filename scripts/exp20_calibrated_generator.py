"""EXP 20 -- calibrated self-copying generator.
Same mechanism as Exp 16 (whole-word copying from own recent output; LOCAL
glyph mutations only; no external word injection) but mutation forward-rates
are FIT to the measured Herbal-A -> Bio-B glyph-feature shift, then the
generator is asked to traverse the real pole axis. Pre-set criteria:
(i) h2 in [1.6,2.3]; (ii) axis1>=70%; (iii) real-instrument coord >= +0.8;
(iv) repetition in [0.5,0.8]; (v) top-token overlap with real Bio-B >= 3/20.
No tuning after seeing the coordinate."""
import csv, random, re, json
import numpy as np
from collections import Counter
allowed=set("abcdefghiklmnopqrstxyz"); NU,UW,K=12,2000,17
rng=random.Random(1404)

def h2b(sb):
    a=np.frombuffer(sb,np.uint8);u=np.bincount(a,minlength=256).astype(float)
    p=u[u>0]/u.sum();h1=-(p*np.log2(p)).sum()
    bg=a[:-1].astype(np.int32)*256+a[1:];b=np.bincount(bg,minlength=65536).astype(float)
    q=b[b>0]/b.sum();return -(q*np.log2(q)).sum()-h1
class Env:
    def __init__(self,U):
        sy=sorted(set(c for u in U for w in u for c in w));self.code={c:i+1 for i,c in enumerate(sy)};self.n0=len(sy)+1
    def st(self,ws):
        b=bytearray()
        for i,w in enumerate(ws):
            if i:b.append(0)
            for c in w:b.append(self.code[c])
        return bytes(b)
    def greedy(self,ws,mm=K):
        s=self.st(ws);nxt=self.n0;h=h2b(s);ops=[]
        for _ in range(mm):
            a=np.frombuffer(s,np.uint8);m=(a[:-1]!=0)&(a[1:]!=0)
            cnt=Counter((a[:-1][m].astype(np.int32)*256+a[1:][m]).tolist());best=None
            for pr,c in cnt.most_common(90):
                x,y=pr//256,pr%256;cd=s.replace(bytes([x,y]),bytes([nxt]));ch=h2b(cd)
                if best is None or ch>best[0]:best=(ch,x,y,cd)
            if best is None or best[0]<=h:break
            h,x,y,s=best;ops.append((x,y,nxt));nxt+=1
        return ops
    def ap(self,ws,ops):
        s=self.st(ws)
        for x,y,n in ops:s=s.replace(bytes([x,y]),bytes([n]))
        return h2b(s)
    def rec(self,wi,o1,o2):
        b=h2b(self.st(wi));base=self.ap(wi,o1)-b
        return (self.ap(wi,o2)-b)/base if base>1e-9 else 1.0
def mapstats(U):
    e=Env(U);ops=[e.greedy(u) for u in U];n=len(U);S=np.eye(n)
    for i in range(n):
        for j in range(n):
            if i!=j:S[i,j]=e.rec(U[i],ops[i],ops[j])
    S=(S+S.T)/2;D=1-S;J=np.eye(n)-np.ones((n,n))/n;B=-0.5*J@(D**2)@J
    ev=np.sort(np.linalg.eigvalsh(B))[::-1];pos=ev[ev>1e-9];off=S[~np.eye(n,dtype=bool)]
    return 100*pos[0]/pos.sum(),off.min()*100

secw={}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f,delimiter="\t"):
        if row["transcriber"]!="H" or not row["placement"].startswith("P"):continue
        w="".join(c for c in row["word"].lower() if c.isalpha())
        if w and all(c in allowed for c in w):secw.setdefault(row["section"],[]).append(w)
allw=[w for v in secw.values() for w in v]
HA=secw["H"]; BB=secw["B"]

# ---- measure A->B feature target rates ----
def rate(ws,fn): return np.mean([fn(w) for w in ws])
feats={"q_init":lambda w:w.startswith("q"),"has_ee":lambda w:"ee" in w,
       "end_edy":lambda w:w.endswith("edy"),"end_dy":lambda w:w.endswith("dy"),
       "che":lambda w:"che" in w,"cho":lambda w:"cho" in w,
       "a_rate":lambda w:"a" in w,"end_y":lambda w:w.endswith("y")}
print("feature        Herbal-A   Bio-B   (target=B)")
tgt={}
for k,fn in feats.items():
    ra,rb=rate(HA,fn),rate(BB,fn);tgt[k]=rb
    print(f"  {k:<12}{ra:>8.3f}{rb:>8.3f}")

# ---- calibrated local mutation: forward prob scaled by (B_rate) at drift th ----
def mutate(w,th):
    # e-cascade: e->ee toward B (target has_ee ~ tgt)
    if "ee" not in w and "e" in w and rng.random()<th*tgt["has_ee"]*3: w=w.replace("e","ee",1)
    elif "ee" in w and rng.random()<(1-th)*0.3: w=w.replace("ee","e",1)
    # cho<->che toward che at high th
    if "cho" in w and rng.random()<th*0.9: w=w.replace("cho","che",1)
    elif "che" in w and rng.random()<(1-th)*0.5: w=w.replace("che","cho",1)
    # endings y->dy->edy toward -edy
    if w.endswith("edy"): pass
    elif w.endswith("dy") and rng.random()<th*0.8: w=w[:-2]+"edy"
    elif w.endswith("y") and not w.endswith("dy") and rng.random()<th*0.8: w=w[:-1]+"dy"
    elif w.endswith("dy") and rng.random()<(1-th)*0.4: w=w[:-2]+"y"
    # q-prefix add toward B (Bio-B q_init target)
    if not w.startswith("q") and rng.random()<th*tgt["q_init"]*2.2:
        w=("qo"+w[1:]) if w.startswith("o") else ("q"+w)
    elif w.startswith("q") and rng.random()<(1-th)*0.5: w=w[1:] if not w.startswith("qo") else "o"+w[2:]
    # k<->t, ch<->sh neutral wander (entropy realism)
    if "k" in w and rng.random()<0.2: w=w.replace("k","t",1)
    if "ch" in w and "che" not in w and "cho" not in w and rng.random()<0.15: w=w.replace("ch","sh",1)
    return w

seed=HA[:300]; text=seed[:]; W=600; target=NU*UW+300
while len(text)<target:
    th=(len(text)-300)/(target-300)
    src=text[max(0,len(text)-W)+rng.randrange(min(W,len(text)))]
    p_copy=0.10+0.28*th
    text.append(src if rng.random()<p_copy else mutate(src,th))
gen=text[300:]; U=[gen[i*UW:(i+1)*UW] for i in range(NU)]

# real instrument
env=Env([allw]+U); ops_real=env.greedy(allw,mm=40)
def tvec(ws):
    s=env.st(ws)
    for x,y,n in ops_real:s=s.replace(bytes([x,y]),bytes([n]))
    a=np.frombuffer(s,np.uint8);c=np.bincount(a,minlength=256).astype(float);c[0]=0;t=c.sum();return c/t
vHA=tvec(HA);vBB=tvec(BB);u=vBB-vHA;den=float(u@u)
coord=lambda ws:float((tvec(ws)-vHA)@u)/den

print("\nunit  h2     coord   rep")
h2s=[];cs=[]
for i,x in enumerate(U):
    h=h2b(env.st(x));c=coord(x);r=1-len(set(x))/len(x);h2s.append(h);cs.append(c)
    if i in (0,3,6,9,11):print(f"{i+1:>4}  {h:.3f}  {c:>+6.2f}  {r:.3f}")
realBio=BB[:2000]
topB=set([w for w,_ in Counter(realBio).most_common(20)])
topG=set([w for w,_ in Counter(U[-1]).most_common(20)])
ov=len(topB&topG)
ax,mn=mapstats(U)
print(f"\nreal Bio-B: coord={coord(realBio):+.2f} rep={1-len(set(realBio))/len(realBio):.3f}")
print(f"map axis1={ax:.1f}% min-sim={mn:.1f}%")
print(f"top-token overlap with real Bio-B: {ov}/20  (gen top: {sorted(topG)[:8]})")
crit={"i_h2_in_band":bool(1.6<=min(h2s) and max(h2s)<=2.3) or f"range {min(h2s):.2f}-{max(h2s):.2f}",
      "ii_axis1_ge70":bool(ax>=70),"iii_coord_ge_0.8":round(max(cs),2),
      "iv_rep_in_band":round(1-len(set(U[-1]))/len(U[-1]),3),"v_token_overlap":ov}
print("\nCRITERIA:",crit)
json.dump({"targets":{k:round(v,3) for k,v in tgt.items()},"unit_h2":[round(x,3) for x in h2s],
           "coords":[round(c,2) for c in cs],"coord_max":round(max(cs),2),
           "map_axis1":round(ax,1),"map_min_sim":round(mn,1),"token_overlap_20":ov,
           "criteria":crit},open("results/exp20_results.json","w"),indent=2,default=str)
print("wrote results/exp20_results.json")
