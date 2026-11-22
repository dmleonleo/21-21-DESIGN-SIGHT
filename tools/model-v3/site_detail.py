# Site details from the photo audit (2026-11-22): parts_dae_r5.pkl -> parts_dae_r6.pkl
# Evidence: Kakidai 2018-3 (from the plaza), Wei-Te Wong 16202555152 (from the lawn).
# 1) The free-standing low wall from the west-wing roof tip (4.85,-5.19) to (16.11,-1.17) stands ~1.0 m
#    above the ground on both sides (lawn south, plaza north): top raised 0.52 -> 0.65, level with the roof tip as both photos show.
#    The curb under the SW glass (x<4.85) keeps 0.52.
# 2) South of the wall line the SketchUp has stone paving; photos show lawn there. Paving west of x~16.3 is replaced by lawn (top -0.03).
# 3) Stainless round handrail on the raised wall: 76 mm dia, 0.15 m above the top, posts ~2 m (inferred).
import pickle,numpy as np,trimesh
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
P=pickle.load(open('parts_dae_r5.pkl','rb')); D={p[0]:i for i,p in enumerate(P)}
TIP=np.array([4.85,-5.19]); STRIP_E=Polygon([(4.85,-5.19),(4.70,-4.80),(15.93,-0.66),(16.11,-1.17)]).buffer(0.03)
ZT=0.65  # = roof tip (top 0.69); photos show the tip level with the wall top
# 1) raise the free wall
n,V,F,m=P[D['F1_walls_RC']]; V=V.copy(); k=0
for i,v in enumerate(V):
    if abs(v[2]-0.52)<0.01 and STRIP_E.contains(Point(v[0],v[1])) and v[0]>4.80: V[i,2]=ZT; k+=1
P[D['F1_walls_RC']]=(n,V,F,m); print('wall verts raised',k)
# 2) paving -> lawn south of the wall
LAWN=Polygon([(-8.10,-9.79),(4.85,-5.19),(16.11,-1.17),(16.30,-10.30),(-8.30,-10.30),(-8.30,-9.90)])
n,V,F,m=P[D['F1_floor_slab']]; T=V[F]
top=(np.abs(T[:,:,2])<0.005).all(1)
cent=T[:,:,:2].mean(1)
topU=unary_union([Polygon(t[:,:2]).buffer(1e-4) for t in T[top] if Polygon(t[:,:2]).area>1e-8])
lawn=topU.intersection(LAWN); keep=topU.difference(LAWN)
def tri(poly,z):
    vs,fs=[],[]
    for g in getattr(poly,'geoms',[poly]):
        if g.area<1e-4: continue
        v,f=trimesh.creation.triangulate_polygon(g,engine='earcut'); fs.append(f+sum(len(x) for x in vs)); vs.append(np.c_[v,np.full(len(v),z)])
    return np.vstack(vs),np.vstack(fs)
vk,fk=tri(keep,0.0)
inL=np.array([LAWN.buffer(0.05).contains(Point(*c)) for c in cent])
Fn=F[~top & ~inL]; Vn=V  # also drop slab side faces left inside the new lawn
Vn2=np.vstack([Vn,vk]); Fn2=np.vstack([Fn,fk+len(Vn)])
P[D['F1_floor_slab']]=(n,Vn2,Fn2,m)
vl,fl=tri(lawn,-0.03)
# skirt along the lawn/paving boundary (paving edge 0.0 down to lawn -0.03 is tiny; add the paving slab edge face)
P.append(('Site_lawn_south',vl,fl,'lawn'))
print('lawn area %.1f m2, paving kept %.1f m2'%(lawn.area,keep.area))
# 3) handrail
A=TIP+np.array([0.35,0.13]); B=np.array([16.02,-0.915])
L=np.linalg.norm(B-A); d=(B-A)/L
cyl=lambda p0,p1,r: trimesh.creation.cylinder(radius=r,segment=[p0,p1],sections=12)
parts=[cyl([*A,ZT+0.15],[*B,ZT+0.15],0.038)]
nn=int(np.ceil(L/2.0))
for i in range(nn+1):
    p=A+d*min(L-0.15,max(0.15,i*L/nn)); parts.append(cyl([*p,ZT],[*p,ZT+0.15],0.012))
M=trimesh.util.concatenate(parts)
P=[p for p in P if p[0]!='Site_handrail']+[('Site_handrail',M.vertices,M.faces,'steel')]
pickle.dump(P,open('parts_dae_r6.pkl','wb')); print('rail %.1f m, %d posts'%(L,nn+1))
