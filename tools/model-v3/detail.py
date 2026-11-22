# detail pass 1: drop SketchUp back-face duplicates, add glass balustrades to B1 scissor stair
import pickle,numpy as np
P=pickle.load(open('parts_dae_r.pkl','rb'))
out=[]
for name,V,F,mat in P:
    V=np.asarray(V); F=np.asarray(F); seen=set(); keep=[]
    for f in F:
        k=tuple(sorted(map(tuple,np.round(V[f],3))))
        if k in seen: continue
        seen.add(k); keep.append(f)
    out.append((name,V,np.array(keep),mat))
def strip(pts,h=1.1,below=0.25,t=0.012):
    """vertical glass band following polyline pts (x,y,z_base) -> box mesh"""
    V=[];F=[]
    for (a,b) in zip(pts[:-1],pts[1:]):
        a=np.array(a,float);b=np.array(b,float); d=b[:2]-a[:2]; n=np.array([-d[1],d[0]])/np.linalg.norm(d)*t/2
        q=[]
        for s in (1,-1):
            for p in (a,b):
                q+=[[p[0]+s*n[0],p[1]+s*n[1],p[2]-below],[p[0]+s*n[0],p[1]+s*n[1],p[2]+h]]
        i=len(V); V+=q
        # q: 0 a_lo+,1 a_hi+,2 b_lo+,3 b_hi+,4 a_lo-,5 a_hi-,6 b_lo-,7 b_hi-
        for tri in [(0,2,3),(0,3,1),(4,7,6),(4,5,7),(1,3,7),(1,7,5),(0,6,2),(0,4,6),(0,1,5),(0,5,4),(2,6,7),(2,7,3)]:
            F.append([i+k for k in tri])
    return np.array(V),np.array(F)
ylo=lambda x:14.13-0.047*(x-45.5); yhi=lambda x:17.41-0.047*(x-45.5)
zlo=lambda x:-4.59+0.453*(x-45.5); zhi=lambda x:-1.13-0.467*(x-45.5)
o=0.03  # set 30 mm inside the stair edge
lower=[(44.95,ylo(44.95)+o,-5.1),(49.25,ylo(49.25)+o,-3.06),(53.1,ylo(53.1)+o,-3.06),(53.1-o,yhi(53.1)-o,-3.06)]
upper=[(53.1-o,yhi(53.1)-o,-3.06),(49.6,yhi(49.6)-o,-3.06),(43.1,yhi(43.1)-o,0.0)]
Vs=[];Fs=[];n0=0
for pl in (lower,upper):
    v,f=strip(pl); Vs.append(v); Fs.append(f+n0); n0+=len(v)
out.append(('B1_stair_balustrade',np.vstack(Vs),np.vstack(Fs),'glass'))
pickle.dump(out,open('parts_dae_r2.pkl','wb'))
for name,V,F,mat in out: print(name,len(F))
