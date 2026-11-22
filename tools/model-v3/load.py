import collada, numpy as np, collada.scene as S
m=collada.Collada('model.dae')
U=m.assetInfo.unitmeter
def walk(node,T,path):
    out=[]
    if isinstance(node,S.Node):
        T=T@node.matrix; nm=node.id or ''
        for c in node.children: out+=walk(c,T,path+[nm])
    elif isinstance(node,S.NodeNode):
        out+=walk(node.node,T,path)
    elif isinstance(node,S.GeometryNode):
        mats={}
        for mn in node.materials: mats[mn.symbol]=mn.target.name if mn.target is not None else mn.symbol
        for p in node.geometry.primitives:
            if isinstance(p,collada.triangleset.TriangleSet) or isinstance(p,collada.polylist.Polylist) or isinstance(p,collada.polygons.Polygons):
                tri=p.triangleset() if not isinstance(p,collada.triangleset.TriangleSet) else p
                v=(T[:3,:3]@tri.vertex.T).T+T[:3,3]
                out.append(dict(path=path,geom=node.geometry.name,mat=mats.get(tri.material,tri.material),V=v*U,F=tri.vertex_index))
    return out
def load():
    res=[]
    for n in m.scene.nodes: res+=walk(n,np.eye(4),[])
    return res
