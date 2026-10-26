#! /usr/bin/env python3
"""Flag contours whose start node differs between the Light and Bold masters of a .glyphs file.
usage: python toolchain/check_start_points.py masters/Hind.glyphs

For each compatible contour pair, try every cyclic rotation of the Bold nodes that keeps node types aligned;
flag when some rotation fits the Light shape much better than the stored order (0)."""
import sys, glyphsLib
font = glyphsLib.GSFont(sys.argv[1])
ids = [m.id for m in font.masters]
def norm(nodes):
    xs=[n.position.x for n in nodes]; ys=[n.position.y for n in nodes]
    cx,cy=sum(xs)/len(xs),sum(ys)/len(ys); s=max(max(xs)-min(xs),max(ys)-min(ys),1)
    return [((x-cx)/s,(y-cy)/s) for x,y in zip(xs,ys)]
hits=[]
for g in font.glyphs:
    if not g.export: continue
    la=[l for l in g.layers if l.layerId==ids[0]][0]; lb=[l for l in g.layers if l.layerId==ids[-1]][0]
    if len(la.paths)!=len(lb.paths): continue
    for i,(pa,pb) in enumerate(zip(la.paths,lb.paths)):
        na,nb=list(pa.nodes),list(pb.nodes)
        if len(na)!=len(nb) or len(na)<3: continue
        A,B=norm(na),norm(nb); n=len(na); ta=[x.type for x in na]; tb=[x.type for x in nb]
        costs={}
        for r in range(n):
            if [tb[(k+r)%n] for k in range(n)]!=ta: continue
            costs[r]=sum((A[k][0]-B[(k+r)%n][0])**2+(A[k][1]-B[(k+r)%n][1])**2 for k in range(n))
        if 0 not in costs: hits.append((g.name,i,"node types misaligned at 0",None)); continue
        best=min(costs,key=costs.get)
        if best!=0 and costs[0]>3*costs[best]+0.01:
            hits.append((g.name,i,f"rotate Bold by {best}",round(costs[0]/max(costs[best],1e-9),1)))
for h in hits: print(*h)
print(len(hits),"flagged")
