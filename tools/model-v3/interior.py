# Interior finishes (2026-11-22): parts_dae_r8.pkl -> parts_dae_r9.pkl
# Per official interior photos (2121designsight.jp): ceilings white, B1 gallery floor light grey; downlights in B1 ceilings.
# Walls stay exposed concrete (Ando). Downlight grid 2.7 m, 160 mm discs: inferred.
import pickle,numpy as np,trimesh
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
P=pickle.load(open('parts_dae_r8.pkl','rb')); P=[p for p in P if not p[0].startswith('INT_')]
D={p[0]:i for i,p in enumerate(P)}
def nzs(V,F):
    T=V[F]; n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); return n[:,2]/(np.linalg.norm(n,axis=1)+1e-12), T[:,:,2].mean(1)
add=[]
def split(name,sel,newname,mat):
    n,V,F,m=P[D[name]]; P[D[name]]=(n,V,F[~sel],m); add.append((newname,V,F[sel],mat))
for nm in ('B1_roof_slab_lawn','F1_floor_slab'):
    n,V,F,m=P[D[nm]]; nz,z=nzs(V,F); split(nm,(nz<-0.9)&(np.abs(z+1.0)<0.02),'INT_ceiling_'+nm,'ceiling')
n,V,F,m=P[D['B1_floor_slab']]; nz,z=nzs(V,F); sel=(nz>0.9)&(np.abs(z+6.0)<0.02)
split('B1_floor_slab',sel,'INT_B1_floor','b1floor')
# downlights under the B1 ceiling (B1_roof_slab_lawn underside only; F1 slab underside is mostly over B1 too)
cs=[a for a in add if a[0].startswith('INT_ceiling')]
poly=unary_union([Polygon(t[:,:2]) for nm,V,F,m in cs for t in V[F] if Polygon(t[:,:2]).area>1e-6]).buffer(-0.6)
fl=[a for a in add if a[0]=='INT_B1_floor'][0]; b1=unary_union([Polygon(t[:,:2]) for t in fl[1][fl[2]] if Polygon(t[:,:2]).area>1e-6]).buffer(-0.6); poly=poly.intersection(b1)  # only over the B1 rooms
xs=np.arange(poly.bounds[0],poly.bounds[2],2.7); ys=np.arange(poly.bounds[1],poly.bounds[3],2.7)
ms=[]
for x in xs:
    for y in ys:
        if poly.contains(Point(x,y)):
            c=trimesh.creation.cylinder(radius=0.08,height=0.01,sections=12); c.apply_translation([x,y,-1.006]); ms.append(c)
L=trimesh.util.concatenate(ms); add.append(('INT_downlights',L.vertices,L.faces,'light'))
P+=add; pickle.dump(P,open('parts_dae_r9.pkl','wb'))
print('downlights',len(ms),'ceiling m2',round(poly.buffer(0.6).area))
