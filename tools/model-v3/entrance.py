# Museum main entrance (rev 3, per Leon 2026-11-22 12:57 + photo DSC06710 Daderot CC0):
# no wall on the facade line: the triangle between the facade line, the sign wall and the banner wall is a covered outdoor forecourt.
# The free-standing banner wall runs into the building: it continues past its end by 2x its thickness at full height, then a glass door
# fills the rest of that line up to the sign wall. Concrete lintel over the door to the wall top, glass strip from there to the roof. Door height inferred.
import pickle,numpy as np,trimesh
P=pickle.load(open('parts_dae_r4.pkl','rb')); D={p[0]:i for i,p in enumerate(P)}
R=P[D['Roofs_steel_plate']]; T=R[1][R[2]]; n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]; bot=T[n[:,2]<-0.3]
def zb(p):
    best=None
    for t in bot:
        A,B,C=t[:,:2]; d=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
        if abs(d)<1e-12: continue
        l1=((B[1]-C[1])*(p[0]-C[0])+(C[0]-B[0])*(p[1]-C[1]))/d; l2=((C[1]-A[1])*(p[0]-C[0])+(A[0]-C[0])*(p[1]-C[1]))/d; l3=1-l1-l2
        if min(l1,l2,l3)>=-1e-3:
            z=l1*t[0,2]+l2*t[1,2]+l3*t[2,2]; best=z if best is None else min(best,z)
    return best
W0,W1=np.array([19.30,9.74]),np.array([20.82,5.59])        # banner wall west face (wall section at z=1)
E0,E1=np.array([19.59,9.85]),np.array([22.07,3.10])        # east face
d=(W0-W1)/np.linalg.norm(W0-W1)                            # direction along the wall, pointing into the building
nE=np.array([d[1],-d[0]])                                  # normal toward the east face
TH=float(np.dot(E0-W0,nE)); print('banner wall thickness %.2f'%TH)
ZTOP=3.60                                                   # banner wall top near the door: 4 panel rows of 900 in photo DSC06710 (model had 2.59 at its north end)
from shapely.geometry import Polygon as _Pg, Point as _Pt
# rev 7 (Leon 2026-11-22 14:21): keep the SketchUp structure. The concrete band over the door (z 4.11-4.59) is real (photo of the 単位展 entrance),
# so it stays. Only the banner wall's north top is raised from 2.59 to 3.6, and the stray caps that bridged it into the building are removed.
_fin=_Pg([(19.3,9.74),(20.82,5.59),(21.77,2.99),(22.07,3.1),(20.22,8.14),(19.59,9.85)]).buffer(0.05)
_nm,_V,_F,_m=P[D['F1_walls_RC']]; _V=_V.copy()
for _i,_p in enumerate(_V):
    if abs(_p[2]-2.59)<0.02 and _fin.contains(_Pt(_p[:2])): _V[_i,2]=ZTOP
_raised=np.array([abs(p[2]-ZTOP)<1e-6 and _fin.contains(_Pt(p[:2])) for p in _V])
_bad=_raised[_F].any(1)&(np.abs(_V[_F][:,:,2]-2.59)<0.02).any(1)
print('removed stray cap faces',int(_bad.sum())); _F=_F[~_bad]
P[D['F1_walls_RC']]=(_nm,_V,_F,_m)
S0,S1=np.array([15.81,9.35]),np.array([18.54,11.81])        # sign wall SE face
def inter(a,da,b,db):
    A=np.array([da,-db]).T; t=np.linalg.solve(A,b-a); return a+da*t[0]
endW=W0; L_to_sign=np.dot(inter(W0,d,S0,(S1-S0)/np.linalg.norm(S1-S0))-W0,d)
EXT=2*TH; L_door=L_to_sign-EXT; print('to sign wall %.2f m, extension %.2f m, door bay %.2f m'%(L_to_sign,EXT,L_door))
def Q(s,o): return W0+d*s+nE*o
def prism(s0,s1,o0,o1,z0,z1=None,ztop=None):
    q=[Q(s0,o0),Q(s1,o0),Q(s1,o1),Q(s0,o1)]
    zt=[ztop(*_q) for _q in [(s0,o0),(s1,o0),(s1,o1),(s0,o1)]] if ztop else [z1]*4
    Vv=np.array([[*q[i],z0] for i in range(4)]+[[*q[i],zt[i]] for i in range(4)])
    return trimesh.Trimesh(Vv,[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],process=False)
def box(s0,s1,o,z0,z1,t):
    a,b=Q(s0,o),Q(s1,o); c=(a+b)/2; l=max(np.linalg.norm(b-a),1e-3); ang=np.arctan2(*(b-a)[::-1])
    B=trimesh.creation.box([l,t,z1-z0]); B.apply_transform(trimesh.transformations.rotation_matrix(ang,[0,0,1])); B.apply_translation([c[0],c[1],(z0+z1)/2]); return B
DH=2.55; LT=3.40;  # door head 2.5 m and lintel top 3.4 m measured on the photo against the 900 mm panel rows
fw=0.05; mid=TH/2
walls=[prism(-0.02,EXT,0,TH,0,ZTOP)]                         # wall continues into the building by 2x thickness
# the band over the door in DSC06710 is smooth light grey with no tie holes: a solid panel in the door plane, not concrete
def quad(s0,s1,o,z0,z1):
    a,b=Q(s0,o),Q(s1,o); Vq=np.array([[*a,z0],[*b,z0],[*b,z1],[*a,z1]])
    return trimesh.Trimesh(Vq,[[0,1,2],[0,2,3],[0,2,1],[0,3,2]],process=False)
_ss=np.linspace(EXT,L_to_sign,9); _zz=np.linspace(DH,LT,5)   # split into small quads so the depth-sorted preview renderer draws it cleanly
panel=[quad(a,b,mid+o,z0,z1) for a,b in zip(_ss[:-1],_ss[1:]) for z0,z1 in zip(_zz[:-1],_zz[1:]) for o in (-0.02,0.02)]
glass=[box(EXT+fw,L_to_sign-fw,mid,fw,DH-fw,0.012)]
frame=[box(EXT,EXT+fw,mid,0,DH,0.05),box(L_to_sign-fw,L_to_sign,mid,0,DH,0.05),box(EXT,L_to_sign,mid,0,fw,0.05),
       box(EXT+0.10,EXT+0.12,mid,0.9,1.3,0.10)]
# glass strip between the wall top and the roof, from where the wall passes under the roof edge to the sign wall
ss=np.concatenate([np.linspace(-0.8,EXT,5),np.linspace(EXT,L_to_sign,5)[1:]])
for a,b in zip(ss[:-1],ss[1:]):
    za,zb_=zb(Q(a,mid)),zb(Q(b,mid))
    z0=LT if a>=EXT-1e-6 else ZTOP
    if za is None or zb_ is None or min(za,zb_)<z0+0.05: continue
    q0,q1=Q(a,mid),Q(b,mid); Vq=np.array([[*q0,z0],[*q1,z0],[*q1,zb_-0.01],[*q0,za-0.01]])
    glass.append(trimesh.Trimesh(Vq,[[0,1,2],[0,2,3],[0,2,1],[0,3,2]],process=False))
for key,add in (('F1_walls_RC',walls),('F1_glass',glass),('F1_mullions_frames',frame)):
    nm,V,F,m=P[D[key]]; M=trimesh.util.concatenate([trimesh.Trimesh(V,F,process=False)]+add); P[D[key]]=(nm,M.vertices,M.faces,m)
Mp=trimesh.util.concatenate(panel); P.append(('Entrance_transom_panel',Mp.vertices,Mp.faces,'panel'))
pickle.dump(P,open('parts_dae_r5.pkl','wb'))
