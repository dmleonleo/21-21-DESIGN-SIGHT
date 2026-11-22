import render_tex,numpy as np
from render_tex import render
def subdiv(T,uv,me=2.0):
    out=[(T,uv)];res=[]
    while out:
        T,uv=out.pop(); e=[np.linalg.norm(T[(i+1)%3]-T[i]) for i in range(3)]; i=int(np.argmax(e))
        if e[i]<=me: res.append((T,uv)); continue
        j=(i+1)%3;k=(i+2)%3; mT=(T[i]+T[j])/2; mu=(uv[i]+uv[j])/2
        out.append((np.array([T[i],mT,T[k]]),np.array([uv[i],mu,uv[k]]))); out.append((np.array([mT,T[j],T[k]]),np.array([mu,uv[j],uv[k]])))
    return res
for key,tris in render_tex.G.items():
    nt=[]
    for T,uv in tris: nt+=subdiv(np.asarray(T,float),np.asarray(uv,float)) if max(np.linalg.norm(T[1]-T[0]),np.linalg.norm(T[2]-T[1]),np.linalg.norm(T[0]-T[2]))>2 else [(T,uv)]
    render_tex.G[key]=nt
import sys
V={'sw':((-25,-35,1.6),(20,5,2),55),'s':((25,-40,1.6),(25,5,2),60),'se':((80,-30,1.6),(40,5,2),55),
   'e':((95,5,1.6),(40,5,2),50),'w':((-45,5,1.6),(10,5,2),50),'n':((25,55,1.6),(25,5,2),60),
   'g3a':((-22,-22,1.6),(2,0,1.5),60),'g3b':((-5,-28,1.6),(-2,0,1.5),60),'g3c':((20,-15,1.6),(0,-3,1.5),60),'p3':((20,3.5,1.6),(6,-2.5,1.0),72),'p8':((10,-17,1.6),(8,0,1.4),70),'gd1':((39.5,-20,1.6),(40,8,1.2),40),'gd2':((47,-4,1.6),(38,8.5,1.2),62),'b1a':((22,2,-4.4),(45,4,-4.6),75),'b1b':((45,4,-4.4),(25,0,-4.6),75),'p0':((-30,-28,1.6),(15,2,2.0),55),'top':((25,5,120),(25,5.01,0),40),'aer_sw':((-40,-60,40),(25,5,0),45),'aer_ne':((90,70,40),(25,5,0),45)}
for k in sys.argv[1:]:
    e,t,f=V[k]; render(e,t,f,W=900,H=520,fn=f'ov_{k}.png',title=k)
