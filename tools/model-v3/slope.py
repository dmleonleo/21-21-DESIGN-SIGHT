# Ground slope (2026-11-22): parts_dae_r6.pkl -> parts_dae_r7.pkl
# Archweb south elevation: ground falls ~0.6 m west -> east over the building length (REPORT.md). Modelled as a plane in x.
# Building floor stays at 0. Outdoor paving fades to 0 within 3 m of the roof footprint (doors at floor level). Lawn takes the full slope.
# Free wall and slab edges are extended down so nothing floats. All inferred.
import pickle,numpy as np,trimesh
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from shapely import vectorized
P=pickle.load(open('parts_dae_r6.pkl','rb')); D={p[0]:i for i,p in enumerate(P)}
X0,X1,DROP=-8.7,65.8,0.6
g=lambda x: -DROP*np.clip((x-X0)/(X1-X0),0,1)
n,V,F,m=P[D['Roofs_steel_plate']]; T=V[F]
roof=unary_union([Polygon(t[:,:2]).buffer(0.01) for t in T if Polygon(t[:,:2]).area>1e-6]).buffer(0.05)
def fade(xy):
    d=np.array([roof.distance(Point(p)) for p in xy]); return np.clip(d/3.0,0,1)
def sub(V,F,me): 
    v,f=trimesh.remesh.subdivide_to_size(V,F,max_edge=me); return v,f
# lawn surfaces: whole slab shifted
for nm,me in (('Ground_lawn',2.0),('Site_lawn_south',1.0),('B1_roof_slab_lawn',2.0)):
    n,V,F,m=P[D[nm]]; V=V.copy()  # g is linear in x: no subdivision needed
    s=V[:,2]>-0.5 if nm=='B1_roof_slab_lawn' else np.ones(len(V),bool)
    V[s,2]+=g(V[s,0]); P[D[nm]]=(n,V,F,m); print(nm,len(F))
# paving (floor slab top and its edge tops), faded near the building
n,V,F,m=P[D['F1_floor_slab']]; V,F=sub(V,F,1.5); V=V.copy()
s=V[:,2]>-0.01; V[s,2]+=g(V[s,0])*fade(V[s,:2]); P[D['F1_floor_slab']]=(n,V,F,m)
# free wall bottom down to -0.8 so it reaches the lowered ground
STRIP=Polygon([(4.85,-5.19),(4.70,-4.80),(15.93,-0.66),(16.11,-1.17)]).buffer(0.03)
n,V,F,m=P[D['F1_walls_RC']]; V=V.copy()
for i,v in enumerate(V):
    if abs(v[2])<0.01 and v[0]>4.8 and STRIP.contains(Point(v[0],v[1])): V[i,2]=-0.8
P[D['F1_walls_RC']]=(n,V,F,m)
# skirt: the floor slab sides already run to -1.0; Ground_lawn bottom also shifted. Done.
pickle.dump(P,open('parts_dae_r7.pkl','wb')); print('ok')
