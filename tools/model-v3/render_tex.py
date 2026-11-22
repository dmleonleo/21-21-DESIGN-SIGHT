import numpy as np,pickle
from PIL import Image
from render import look
G=pickle.load(open('groups_tex.pkl','rb'))
TEXF={'concrete_v':'tex_concrete_tie.png','concrete_h':'tex_concrete_floor.png','roof':'tex_steel.png','lawn':'tex_lawn.png','stone':'tex_stone.png'}
TX={k:np.asarray(Image.open(f)).astype(float)/255 for k,f in TEXF.items()}
COL={'ceiling':np.array([0.93,0.93,0.91]),'b1floor':np.array([0.70,0.70,0.68]),'light':np.array([1,0.97,0.9]),'frosted':np.array([0.74,0.82,0.80]),'soffit':np.array([0.88,0.88,0.86]),'panel':np.array([0.80,0.80,0.79]),'glass':np.array([0.62,0.75,0.82]),'steel':np.array([0.62,0.64,0.66])}
def render(eye,target,fov=50,W=1400,H=800,fn='t.png',title='',skip=()):
    eye,M=look(eye,target); fpx=(W/2)/np.tan(np.radians(fov/2))
    zb=np.full((H,W),np.inf); img=np.zeros((H,W,3)); img[:]=[0.86,0.89,0.93]
    L=np.array([0.4,-0.6,0.7]); L/=np.linalg.norm(L)
    for passno in (0,1):
      for (name,key),tris in G.items():
        if any(name.startswith(s) for s in skip): continue
        if (key=='glass')!=(passno==1): continue
        for T,uv in tris:
            p=(T-eye)@M.T
            if (p[:,2]<0.3).any(): continue
            n=np.cross(T[1]-T[0],T[2]-T[0]); nn=np.linalg.norm(n)
            if nn<1e-9: continue
            sh=0.5+0.5*abs(n/nn@L)
            x=W/2+fpx*p[:,0]/p[:,2]; y=H/2-fpx*p[:,1]/p[:,2]; z=p[:,2]
            x0,x1=int(max(0,np.floor(x.min()))),int(min(W-1,np.ceil(x.max()))); y0,y1=int(max(0,np.floor(y.min()))),int(min(H-1,np.ceil(y.max())))
            if x0>x1 or y0>y1: continue
            X,Y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            d=(x[1]-x[0])*(y[2]-y[0])-(x[2]-x[0])*(y[1]-y[0])
            if abs(d)<1e-9: continue
            l1=((x[1]-X)*(y[2]-Y)-(x[2]-X)*(y[1]-Y))/d; l2=((x[2]-X)*(y[0]-Y)-(x[0]-X)*(y[2]-Y))/d; l3=1-l1-l2
            m=(l1>=-1e-4)&(l2>=-1e-4)&(l3>=-1e-4)
            if not m.any(): continue
            iz=l1/z[0]+l2/z[1]+l3/z[2]; zz=1/iz
            sub=zb[y0:y1+1,x0:x1+1]; m&=zz<sub-0.01
            if not m.any(): continue
            if key in TX:
                tx=TX[key]; th,tw=tx.shape[:2]
                u=(l1*uv[0,0]/z[0]+l2*uv[1,0]/z[1]+l3*uv[2,0]/z[2])*zz
                v=(l1*uv[0,1]/z[0]+l2*uv[1,1]/z[1]+l3*uv[2,1]/z[2])*zz
                c=tx[((v%1)*th).astype(int)%th,((u%1)*tw).astype(int)%tw][...,:3]*sh
            else: c=np.broadcast_to(COL[key]*sh,X.shape+(3,))
            blk=img[y0:y1+1,x0:x1+1]
            if key=='glass': blk[m]=blk[m]*0.65+c[m]*0.35
            else: blk[m]=c[m]; sub[m]=zz[m]
    im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))
    from PIL import ImageDraw; ImageDraw.Draw(im).text((10,8),title,fill=(20,20,20)); im.save(fn); print(fn)
if __name__=='__main__':
    render((25,-12,1.6),(25,10,2.2),62,fn='t_south.png',title='v3 textured: eye level, south lawn')
    render((72,-8,10),(56,10,-5),60,fn='t_court.png',title='sunken court from SE')
    render((95,-75,55),(30,5,0),40,fn='t_aerial.png',title='aerial SE')
    render((48,4,-4.3),(44,14,-3),70,fn='t_b1court.png',title='B1, looking at court wall',skip=('F1_floor','B1_roof','Ground'))
