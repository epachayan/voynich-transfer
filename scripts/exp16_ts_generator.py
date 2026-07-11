"""EXP 16 -- faithful-in-mechanism Timm-Schinner generator.
Whole-word copying from recent text; mutations only within attested
similarity classes; drift theta biases direction (o-attachment early ->
e-cascade/q-prefix late); verbatim-copy prob rises with theta.
Pre-set params, no tuning: seed=300 real HA words, window=600,
p_copy=0.10+0.25*theta, 12x2000 words, rng 1404.
Criteria: (i) h2 in [1.6,2.3]; (ii) map axis1>=70%, min-sim << 98%;
(iii) real-instrument coordinate rises to >=+0.6; (iv) late repetition
approaches real Bio-B."""
import csv, random, re, json
import numpy as np
from collections import Counter

allowed=set("abcdefghiklmnopqrstxyz"); SPACE=32; NU,UW,K=12,2000,17
rng=random.Random(1404)

def h2b(sb,sp=0):
    a=np.frombuffer(sb,np.uint8);u=np.bincount(a,minlength=256).astype(float)
    p=u[u>0]/u.sum();h1=-(p*np.log2(p)).sum()
    bg=a[:-1].astype(np.int32)*256+a[1:];b=np.bincount(bg,minlength=65536).astype(float)
    q=b[b>0]/b.sum();return -(q*np.log2(q)).sum()-h1

class Env:
    def __init__(self,unitlists):
        syms=sorted(set(c for u in unitlists for w in u for c in w))
        self.code={c:i+1 for i,c in enumerate(syms)};self.n0=len(syms)+1
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
    def rec(self,wi,own,oth):
        b=h2b(self.st(wi));base=self.ap(wi,own)-b
        return (self.ap(wi,oth)-b)/base if base>1e-9 else 1.0

def mapstats(U):
    env=Env(U);ops=[env.greedy(u) for u in U];n=len(U);S=np.eye(n)
    for i in range(n):
        for j in range(n):
            if i!=j:S[i,j]=env.rec(U[i],ops[i],ops[j])
    S=(S+S.T)/2;D=1-S;J=np.eye(n)-np.ones((n,n))/n;B=-0.5*J@(D**2)@J
    ev=np.sort(np.linalg.eigvalsh(B))[::-1];pos=ev[ev>1e-9]
    off=S[~np.eye(n,dtype=bool)]
    return 100*pos[0]/pos.sum(),off.min()*100,off.mean()*100

secw={}
with open("Voynich-public/Corpora/Voynich_texts/interlinear_full_words.txt") as f:
    for row in csv.DictReader(f,delimiter="\t"):
        if row["transcriber"]!="H" or not row["placement"].startswith("P"):continue
        w="".join(c for c in row["word"].lower() if c.isalpha())
        if w and all(c in allowed for c in w):secw.setdefault(row["section"],[]).append(w)
allw=[w for v in secw.values() for w in v]

def mutate(w,th):
    ops=[]
    if "k" in w:ops.append(("k","t"))
    if "t" in w:ops.append(("t","k"))
    if "p" in w:ops.append(("p","f"))
    if "f" in w:ops.append(("f","p"))
    if "ch" in w and rng.random()<0.5:ops.append(("ch","sh"))
    if "sh" in w:ops.append(("sh","ch"))
    if "cho" in w and rng.random()<th:ops.append(("cho","che"))
    if "che" in w and rng.random()<(1-th):ops.append(("che","cho"))
    if "o" in w and rng.random()<0.3:ops.append(("o","a"))
    if "a" in w and rng.random()<0.3:ops.append(("a","o"))
    if "ee" in w and rng.random()<(1-th):ops.append(("ee","e"))
    elif "e" in w and rng.random()<th:ops.append(("e","ee"))
    m=re.search(r"i+n",w)
    if m:
        run=m.group(0)
        ops.append((run,"i"*max(1,len(run)-2)+"n") if rng.random()<0.5 and len(run)>2 else (run,"i"*(len(run))+ "n" if False else "i"*(len(run)-1)+"in"))
    if w.endswith("dy") and rng.random()<th*0.5:ops.append(("dy","edy"))
    elif w.endswith("edy") and rng.random()<(1-th)*0.5:ops.append(("edy","dy"))
    elif w.endswith("y") and rng.random()<th:ops.append(("y","dy"))
    elif w.endswith("dy") and rng.random()<(1-th):ops.append(("dy","y"))
    if w.startswith("o") and rng.random()<th:ops.append(("^o","qo"))
    if w.startswith("qo") and rng.random()<(1-th):ops.append(("^qo","o"))
    if w.endswith("r"):ops.append(("r$","s"))
    if w.endswith("s"):ops.append(("s$","r"))
    if not ops:return w
    a,b=rng.choice(ops)
    if a.startswith("^"):return b+w[len(a)-1:]
    if a.endswith("$"):return w[:-(len(a)-1)]+b
    i=w.find(a);return w[:i]+b+w[i+len(a):]

seed=secw["H"][:300];text=seed[:];W=600;target=NU*UW+300
while len(text)<target:
    th=(len(text)-300)/(target-300)
    src=text[max(0,len(text)-W)+rng.randrange(min(W,len(text)))]
    p_copy=0.10+0.25*th
    text.append(src if rng.random()<p_copy else mutate(src,th))
gen=text[300:]
U=[gen[i*UW:(i+1)*UW] for i in range(NU)]

envh=Env([allw]) if False else None
# real instrument: global ops on real MS + real poles
class E2(Env):pass
env_real=Env([allw]+U)  # shared symbol table covering both
ops_real=env_real.greedy(allw,mm=40)
def tvec(ws):
    s=env_real.st(ws)
    for x,y,n in ops_real:s=s.replace(bytes([x,y]),bytes([n]))
    a=np.frombuffer(s,np.uint8);c=np.bincount(a,minlength=256).astype(float);c[0]=0
    t=c.sum();return c/t
vHA=tvec(secw["H"]);vBB=tvec(secw["B"]);u=vBB-vHA;den=float(u@u)
def coord(ws):return float((tvec(ws)-vHA)@u)/den

print("unit  h2     coord(real instr)  1-type/token")
h2s=[];coords=[]
for i,x in enumerate(U):
    h=h2b(env_real.st(x));c=coord(x);r=1-len(set(x))/len(x)
    h2s.append(h);coords.append(c)
    if i in (0,3,6,9,11):print(f"{i+1:>4}  {h:.3f}  {c:>+8.2f}          {r:.3f}")
realBio=secw["B"][:2000];print(f"real Bio-B (2000w): h2={h2b(env_real.st(realBio)):.3f} coord={coord(realBio):+.2f} rep={1-len(set(realBio))/len(realBio):.3f}")
ax,mn,me=mapstats(U)
print(f"\nmap: axis1={ax:.1f}%  min-sim={mn:.1f}%  mean-sim={me:.1f}%")
res={"criteria":{"h2_band":[1.6,2.3],"axis1_min":70,"coord_target":0.6},
     "unit_h2_range":[round(min(h2s),3),round(max(h2s),3)],
     "coord_first_last":[round(coords[0],2),round(coords[-1],2)],
     "coords":[round(c,2) for c in coords],
     "late_repetition":round(1-len(set(U[-1]))/len(U[-1]),3),
     "real_bio_repetition_2000w":round(1-len(set(realBio))/len(realBio),3),
     "map":{"axis1_pct":round(ax,1),"min_sim_pct":round(mn,1),"mean_sim_pct":round(me,1)}}
json.dump(res,open("results/exp16_results.json","w"),indent=2)
print("wrote results/exp16_results.json")
