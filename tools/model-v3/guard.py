# Frosted glass guard at the east roof tip (2026-11-22): parts_dae_r7.pkl -> parts_dae_r8.pkl
# Photos: Guilhem Vellut, Commons 14086741589 / 14250258306 (CC BY 2.0). A free-standing frosted glass panel
# with a thin stainless top frame stands in front of the knife-edge tip, along the south glass line.
# Leon 2026-11-22 16:11: it stands perpendicular to the building. Inferred: 1.1 m high, 12 mm, 3.08 m long, at the point where the roof edge drops to 1.1 m.
import pickle,numpy as np,trimesh
P=pickle.load(open('parts_dae_r7.pkl','rb')); P=[p for p in P if p[0] not in ('Site_glass_guard','Site_glass_guard_frame')]
A=np.array([19.88,9.05]); B=np.array([41.10,8.03]); zA,zB=3.98,0.72; H=1.10
d=(B-A)/np.linalg.norm(B-A); nrm=np.array([d[1],-d[0]])  # points south
t0=(zA-H)/(zA-zB); L=np.linalg.norm(B-A)
p0=A+d*L*t0+nrm*0.05; p1=p0+nrm*3.08  # rev 2 per Leon: perpendicular to the building, from the glass line where the roof edge is 1.1 m, running south
def box(a,b,w,z0,z1):
    v=b-a; ln=np.linalg.norm(v); ang=np.arctan2(v[1],v[0])
    m=trimesh.creation.box(extents=[ln,w,z1-z0]); 
    T=trimesh.transformations.rotation_matrix(ang,[0,0,1]); T[:3,3]=[*(a+b)/2,(z0+z1)/2]; m.apply_transform(T); return m
g=box(p0,p1,0.012,0.0,H-0.03)
fr=trimesh.util.concatenate([box(p0,p1,0.03,H-0.03,H), box(p1-d*0.02,p1,0.03,0,H)])
P.append(('Site_glass_guard',g.vertices,g.faces,'frosted')); P.append(('Site_glass_guard_frame',fr.vertices,fr.faces,'steel'))
pickle.dump(P,open('parts_dae_r8.pkl','wb')); print('guard',np.round(p0,2),np.round(p1,2),'len %.2f'%np.linalg.norm(p1-p0))
