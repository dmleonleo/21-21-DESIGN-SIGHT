# G3 entrance: the SketchUp door leaves were solid opaque slabs (render black). Replace with a frameless-look glass leaf + 40 mm frame (inferred; photos show glass doors).
import pickle,numpy as np,trimesh
P=pickle.load(open('parts_dae_r3.pkl','rb')); D={p[0]:i for i,p in enumerate(P)}
nm,V,F,m=P[D['F1_mullions_frames']]
M=trimesh.Trimesh(V,F,process=False); comps=M.split(only_watertight=False)
keep=[];leaf=None
for c in comps:
    b=c.bounds
    if abs(b[0][0]-10.5)<0.08 and abs(b[1][0]-10.9)<0.08 and abs(b[0][1]-6.2)<0.08 and abs(b[1][2]-2.46)<0.05:
        leaf=b; continue
    keep.append(c)
print('leaf bounds',leaf)
# leaf plane: diagonal of its plan bbox following the frame line (10.4,7.2)->(11.1,5.8)
p0=np.array([leaf[0][0],leaf[1][1]]); p1=np.array([leaf[1][0],leaf[0][1]]); z0,z1=leaf[0][2],leaf[1][2]
d=p1-p0; L=np.linalg.norm(d); u=d/L; nrm=np.array([-u[1],u[0]])
def box(a,b,za,zb,t):  # box from plan point a to b, thickness t, z range
    c=(a+b)/2; l=np.linalg.norm(b-a); ang=np.arctan2(*(b-a)[::-1])
    B=trimesh.creation.box([l,t,zb-za]); B.apply_transform(trimesh.transformations.rotation_matrix(ang,[0,0,1])); B.apply_translation([c[0],c[1],(za+zb)/2]); return B
fw=0.04
frame=[box(p0,p0+u*fw,z0,z1,0.05),box(p1-u*fw,p1,z0,z1,0.05),box(p0,p1,z0,z0+fw,0.05),box(p0,p1,z1-fw,z1,0.05),
       box(p0+u*(L-0.12),p0+u*(L-0.10),0.95,1.15,0.09)]  # pull handle (inferred)
glass=box(p0+u*fw,p1-u*fw,z0+fw,z1-fw,0.012)
newM=trimesh.util.concatenate(keep+frame)
P[D['F1_mullions_frames']]=(nm,newM.vertices,newM.faces,m)
gn,gV,gF,gm=P[D['F1_glass']]; G=trimesh.util.concatenate([trimesh.Trimesh(gV,gF,process=False),glass])
P[D['F1_glass']]=(gn,G.vertices,G.faces,gm)
pickle.dump(P,open('parts_dae_r4.pkl','wb')); print('leaf width %.2f height %.2f'%(L,z1-z0))
