import numpy as np, pickle, json, trimesh
from PIL import Image
PW,PH=1.8,0.9
import os
P=pickle.load(open(os.environ.get('PARTS','parts_dae_r9.pkl'),'rb'))
TEX={'concrete_v':'tex_concrete_tie.png','concrete_h':'tex_concrete_floor.png','roof':'tex_steel.png','lawn':'tex_lawn.png','stone':'tex_stone.png'}
def uv_tri(T,kind):
    n=np.cross(T[1]-T[0],T[2]-T[0]); nn=np.linalg.norm(n); n=n/nn if nn>0 else np.array([0,0,1])
    if kind=='roof': # plate joints along slope: project on plane, u along strike
        s=np.array([-n[1],n[0],0.]); s=s/np.linalg.norm(s) if np.linalg.norm(s)>1e-6 else np.array([1,0,0.]); d=np.cross(n,s)
        return np.c_[T@s/PW, T@d/1.5*0.5]   # 1.5 m plate strips -> half tile height (inferred)
    if abs(n[2])<0.7:  # vertical-ish face: u along wall, v = height (joints aligned to GL)
        t=np.array([-n[1],n[0],0.]); t/=np.linalg.norm(t)
        return np.c_[T@t/PW, -T[:,2]/PH], 'v'
    return np.c_[T[:,0]/PW, T[:,1]/PH], 'h'
# panel grid origin per wall plane: u starts at the wall's own end, v starts at that level's floor (1F 0.0, B1 -6.0)
import collections
def plane_key(T):
    n=np.cross(T[1]-T[0],T[2]-T[0]); nn=np.linalg.norm(n)
    if nn<1e-9: return None
    n=n/nn
    if n[2]<0 or (abs(n[2])<1e-6 and (n[1]<0 or (abs(n[1])<1e-6 and n[0]<0))): n=-n
    return (tuple(np.round(n,2)),round(float(n@T[0]),1))
umin={}
for name,V,F,mat in P:
    if mat!='concrete': continue
    for f in F:
        T=V[f]; k=plane_key(T)
        if k is None or abs(k[0][2])>=0.7: continue
        n=np.array(k[0]); t=np.array([-n[1],n[0],0.]); t/=np.linalg.norm(t)
        umin[k]=min(umin.get(k,1e9),float((T@t).min()))
groups={}
for name,V,F,mat in P:
    for f in F:
        T=V[f]
        if mat=='concrete':
            uv,k=uv_tri(T,'c'); key='concrete_'+k
            if k=='v':
                pk=plane_key(T); n=np.array(pk[0]); tt=np.array([-n[1],n[0],0.]); tt/=np.linalg.norm(tt)
                z0=-6.0 if T[:,2].min()<-1.0 else 0.0
                uv=np.c_[(T@tt-umin[pk])/(2*PW), -(T[:,2]-z0)/(2*PH)]  # 2x2-panel tile
        elif mat=='stone':
            uv,k=uv_tri(T,'c'); key='stone' if k=='h' else 'concrete_v'
            if k=='h': uv=np.c_[T[:,0]/1.8,T[:,1]/1.8]  # 600 mm granite grid (inferred), 3x3 per tile
        elif mat=='lawn': uv=np.c_[T[:,0]/4,T[:,1]/4]; key='lawn'
        elif mat=='roof':
            nz=np.cross(T[1]-T[0],T[2]-T[0]); nz=nz[2]/(np.linalg.norm(nz)+1e-12)
            if nz<-0.5: uv=np.zeros((3,2)); key='soffit'   # roof underside: light painted soffit as in photo DSC06710
            else: uv=uv_tri(T,'roof'); key='roof'
        else: uv=np.zeros((3,2)); key=mat
        groups.setdefault((name,key),[]).append((T,uv))
pickle.dump(groups,open('groups_tex.pkl','wb'))
MAT={}
def pbr(key):
    if key in TEX:
        return trimesh.visual.material.PBRMaterial(name='MAT_'+key,baseColorTexture=Image.open(TEX[key]),metallicFactor=0.7 if key=='roof' else 0.0,roughnessFactor=0.55 if key=='roof' else 0.9,doubleSided=True)
    c={'glass':[0.62,0.75,0.82,0.30],'steel':[0.62,0.64,0.66,1],'panel':[0.80,0.80,0.79,1],'soffit':[0.88,0.88,0.86,1],'frosted':[0.80,0.88,0.86,0.80],'ceiling':[0.93,0.93,0.91,1],'b1floor':[0.70,0.70,0.68,1],'light':[1,0.97,0.9,1]}[key]
    return trimesh.visual.material.PBRMaterial(name='MAT_'+key,baseColorFactor=c,emissiveFactor=[1,0.95,0.85] if key=='light' else None,metallicFactor=0.1 if key in ('glass','frosted') else (0.0 if key in ('ceiling','b1floor','light') else 0.8),roughnessFactor={'glass':0.05,'frosted':0.6}.get(key,0.4),alphaMode='BLEND' if key in ('glass','frosted') else 'OPAQUE',doubleSided=True)
Yup=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float)
sc=trimesh.Scene()
for (name,key),L in groups.items():
    V=np.vstack([t for t,_ in L]); UV=np.vstack([u for _,u in L]); F=np.arange(len(V)).reshape(-1,3)
    m=trimesh.Trimesh(V,F,process=False); m.apply_transform(Yup)
    if key not in MAT: MAT[key]=pbr(key)
    m.visual=trimesh.visual.TextureVisuals(uv=UV,material=MAT[key])
    sc.add_geometry(m,node_name=f'{name}__{key}',geom_name=f'{name}__{key}')
sc.export('2121_v3_textured.glb')
print({k:len(v) for k,v in groups.items()})
