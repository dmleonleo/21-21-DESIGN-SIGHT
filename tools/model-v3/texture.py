import numpy as np, pickle, json, trimesh
from PIL import Image, ImageDraw, ImageFilter
rng=np.random.default_rng(7)
PW,PH=1.8,0.9            # Ando form panel 1800x900 (horizontal), 6 ties per panel (3x2) - hole layout inferred
TX,TY=1024,512
def noise(h,w,scales=((8,.5),(32,.3),(128,.2))):
    out=np.zeros((h,w))
    for s,a in scales:
        n=rng.random((max(2,h//s),max(2,w//s)))
        out+=a*np.array(Image.fromarray((n*255).astype(np.uint8)).resize((w,h),Image.BICUBIC))/255
    return out
def concrete(holes=True,base=0.72,fn='tex_concrete_tie.png',tile=1):
    W,H=TX*tile,TY*tile
    n=noise(H,W); fine=rng.random((H,W))*0.04
    g=base+0.08*(n-n.mean())+fine-0.02
    img=np.stack([g*0.99,g*0.985,g*0.96],-1)
    im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im)
    jl=(152,150,145)   # ordinary panel joint
    jd=(118,116,112)   # darker joint every 2 panels (official G3 elevation; likely pour/primary joint)
    for i in range(tile):
        c=jd if i==0 else jl; w=4 if i==0 else 3
        d.line([(0,i*TY),(W,i*TY)],fill=c,width=w); d.line([(i*TX,0),(i*TX,H)],fill=c,width=w)
    if holes:
        for px in range(tile):
            for py in range(tile):
                for hx in (0.3,0.9,1.5):          # official G3 elevation: 3 holes @600, half-pitch margins
                    for hy in (0.225,0.675):       # 2 rows @450
                        cx,cy=px*TX+hx/PW*TX,py*TY+hy/PH*TY; r=0.016/PW*TX
                        d.ellipse([cx-r-3,cy-r-3,cx+r+3,cy+r+3],fill=(150,148,144))
                        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(95,94,92))
    im=im.filter(ImageFilter.GaussianBlur(0.6)); im.save(fn); return im
concrete(True,tile=2); concrete(False,base=0.62,fn='tex_concrete_floor.png')
# steel roof plate: dark grey, joints every 1.5 m (inferred)
n=noise(TY,TX); g=0.30+0.03*(n-n.mean()); s=np.stack([g,g*1.01,g*1.05],-1)
im=Image.fromarray((np.clip(s,0,1)*255).astype(np.uint8)); ImageDraw.Draw(im).line([(0,0),(TX,0)],fill=(40,40,42),width=2); im.save('tex_steel.png')
n=noise(TY,TX,((4,.5),(16,.5))); g=np.stack([0.36+0.1*n,0.50+0.12*n,0.27+0.06*n],-1)
Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)).save('tex_lawn.png')
