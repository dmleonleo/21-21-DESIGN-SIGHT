import pickle,json,numpy as np,trimesh
R=pickle.load(open('R.pkl','rb')); X=json.load(open('xf.json'))
s=X['s']; Rm=np.array(X['R']); t=np.array(X['t'])
ZUP=4.8/5.55   # above GL: model roof max 5.55 -> official max height 4.8
PLAN={  # (top, component) -> (z shift, material, name)
 ('ID6003','ID4056'):(-15.63,'concrete','F1_walls_RC'),
 ('ID6003','ID4250'):(-15.63,'steel','F1_mullions_frames'),
 ('ID6003','ID4828'):(-15.63,'glass','F1_glass'),
 ('ID6003','ID4877'):(-42.82,'roof','Roofs_steel_plate'),
 ('ID6044','ID3897'):('split','concrete','B1_structure_slabs'),
 ('ID6044','ID3939'):(0.0,'concrete','B1_walls'),
 ('ID6044','ID3881'):(0.0,'concrete','B1_stair_main'),
 ('ID6044','ID6050'):(0.0,'concrete','B1_steps'),
}
parts={}
for r in R:
    p=r['path']
    if len(p)<7: continue
    key=(p[3],p[6])
    if key==('ID6003','ID6009') and p[5]=='ID6008': key2=(-15.63,'stone','F1_floor_slab')
    elif key in PLAN: key2=PLAN[key]
    else: continue
    dz,mat,name=key2
    V=r['V'].copy()
    if dz=='split': V[:,2]=np.where(V[:,2]>9,V[:,2]-15.63,V[:,2]); 
    else: V[:,2]+=dz
    xy=(s*(Rm@V[:,:2].T)).T+t
    z=np.where(V[:,2]>0,V[:,2]*ZUP,V[:,2])
    V2=np.c_[xy,z]
    parts.setdefault((name,mat),[]).append((V2,r['F']))
# split B1 slabs: floor (z<-3) vs roof slab under lawn (z>-3, top lowered 3 cm, lawn colour)
L=parts.pop(('B1_structure_slabs','concrete')); lo=[];hi=[]
for V,F in L:
    zc=V[F].mean(1)[:,2]
    if (zc<-3).any(): lo.append((V,F[zc<-3]))
    if (zc>=-3).any():
        V2=V.copy(); V2[:,2]=np.where(V2[:,2]>-0.01,-0.03,V2[:,2]); hi.append((V2,F[zc>=-3]))
parts[('B1_floor_slab','concrete')]=lo; parts[('B1_roof_slab_lawn','lawn')]=hi
out=[]
for (name,mat),L in parts.items():
    Vs=[];Fs=[];o=0
    for V,F in L: Vs.append(V); Fs.append(F+o); o+=len(V)
    V=np.vstack(Vs); F=np.vstack(Fs)
    out.append((name,V,F,mat)); print(name,mat,len(F),np.round(V.min(0),2),np.round(V.max(0),2))
pickle.dump(out,open('parts_dae.pkl','wb'))
MATS={'roof':[0.30,0.31,0.33,1],'concrete':[0.74,0.73,0.70,1],'glass':[0.62,0.75,0.82,0.35],'steel':[0.20,0.20,0.21,1],'stone':[0.55,0.55,0.53,1],'lawn':[0.42,0.55,0.32,1]}
scene=trimesh.Scene(); Yup=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float)
for name,V,F,mat in out:
    mm=trimesh.Trimesh(V,F,process=False); mm.apply_transform(Yup)
    mm.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(name='MAT_'+mat,baseColorFactor=MATS[mat],metallicFactor=0.6 if mat in('roof','steel') else 0,roughnessFactor=0.3 if mat=='glass' else 0.85,alphaMode='BLEND' if mat=='glass' else 'OPAQUE',doubleSided=True))
    scene.add_geometry(mm,node_name=name,geom_name=name)
scene.export('2121_v3_from_skp.glb')
json.dump({'source':'21_21+DS+CORREGIDO SketchUp model (DAE export, author unknown), exploded components re-assembled',
 'z_shifts_in_exploded_frame':{'1F walls/glass/mullions/1F slab':-15.63,'roofs':-42.82,'B1 ground slab part (z>9)':-15.63,'B1':0},
 'horizontal':{'scale':s,'rotation_deg':float(np.degrees(np.arctan2(Rm[1,0],Rm[0,0]))),'translation':t.tolist(),'fit':'9 roof corners to PLATEAU outline, rms 0.25 m'},
 'vertical':{'above_GL_scale':ZUP,'below_GL_scale':1.0,'why':'model roof max +5.55 vs official 4.8; B1 kept: floor -6.0, ceilings 5.0 (official G1 5.0)'},
 'frame':'X east, Y north, Z up, origin 35.6674N 139.7301E, GL=0 (T.P. 27.05); GLB Y-up'},open('xf_v3.json','w'),indent=1)
