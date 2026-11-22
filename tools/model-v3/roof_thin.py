# roof: 0.30 m slab -> thin plate (official 16 mm steel; modelled 40 mm incl. edge, inferred). Walls/mullions/glass that met the old underside are raised to the new one.
import pickle,numpy as np
P=pickle.load(open('parts_dae_r2.pkl','rb'))
T_NEW=0.04
R=[p for p in P if p[0]=='Roofs_steel_plate'][0]; V=R[1].copy(); F=R[2]
Tri=V[F]; n=np.cross(Tri[:,1]-Tri[:,0],Tri[:,2]-Tri[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]
top=Tri[n[:,2]>0.3]; bot=Tri[n[:,2]<-0.3]
def zon(tris,p):
    for t in tris:
        A,B,C=t[:,:2]; d=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
        if abs(d)<1e-12: continue
        l1=((B[1]-C[1])*(p[0]-C[0])+(C[0]-B[0])*(p[1]-C[1]))/d; l2=((C[1]-A[1])*(p[0]-C[0])+(A[0]-C[0])*(p[1]-C[1]))/d; l3=1-l1-l2
        if min(l1,l2,l3)>=-1e-3: return l1*t[0,2]+l2*t[1,2]+l3*t[2,2]
    return None
# bottom vertices = vertices used by bottom faces; lift each to (top z at same xy) - T_NEW
botv=set(F[n[:,2]<-0.3].ravel())
delta={}
for i in botv:
    zt=zon(top,V[i])
    if zt is None: continue
    delta[i]=(zt-T_NEW)-V[i,2]; V[i,2]=zt-T_NEW
print('lift range',min(delta.values()),max(delta.values()))
newbot=V[F][n[:,2]<-0.3]
out=[]; moved=0
for name,Vp,Fp,mat in P:
    Vp=Vp.copy()
    if name=='Roofs_steel_plate': Vp=V
    elif name.startswith('F1_') and name!='F1_floor_slab':
        for i,p in enumerate(Vp):
            if p[2]<2.0: continue
            zb=zon(bot,p)
            if zb is not None and -0.08<=p[2]-zb<=0.03:
                zn=zon(newbot,p); Vp[i,2]=zn; moved+=1
    out.append((name,Vp,Fp,mat))
print('raised vertices',moved)
pickle.dump(out,open('parts_dae_r3.pkl','wb'))
