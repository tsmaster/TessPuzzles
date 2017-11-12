
# See, for example https://en.wikipedia.org/wiki/Doubly_connected_edge_list
#
# - a record for each edge, vertex and face
# - each half edge contains
#   - a reference to the face it bounds
#   - a reference to the next and previous half edge of that face
#   - a reference to the "twin" or other half.
#   - a reference to its origin vertex (the destination is the origin of the "twin")
#
# - each vertex contains
#   - the coordinates of the vertex
#   - a reference to an arbitrary half-edge leaving the vertex
#
# - each face contains
#   - a reference to some half-edge on its boundary
#   - if there are holes, a list of half edges, one per hole
#
# To reach the other face, we can go to the twin of the half-edge and
# then traverse the other face. Each half-edge also has a pointer
#
#             i
#      A-------------B
#             j
#
# Vertex A is the origin vertex of edge i, Vertex B is the origin
# vertex of edge j. The face bounded by i is above the edge, the face
# bounded by j is below.

import copy
import math
from bdggeom import Vec2f

def angleWrapRadians(a):
    while a < 0:
        a += math.pi * 2.0
    while a >= math.pi * 2.0:
        a -= math.pi * 2.0
    return a

class HalfEdgeDef:
    def __init__(self,
                 originVertIndex, #left
                 edgeLabel,
                 twinIndex,
                 nextEdgeIndex,
                 prevEdgeIndex,
                 faceIndex):
        self.originVertIndex = originVertIndex
        self.label = edgeLabel
        self.twinIndex = twinIndex
        self.nextEdgeIndex = nextEdgeIndex
        self.prevEdgeIndex = prevEdgeIndex
        self.faceIndex = faceIndex

class VertDef:
    def __init__(self,
                 pos): # vec2f
        self.pos = pos
        self.edgeIndex = -1

    def addEdge(self, edgeIndex):
        # TODO
        pass


    def removeEdge(self, edgeIndex):
        # TODO
        pass

class FaceDef:
    def __init__(self,
                 boundingEdgeIndex):
        self.boundingEdgeIndex = boundingEdgeIndex
        self.color = -1
        

class PlanarGraph:
    def __init__(self):
        self.HalfEdges = [] # HalfEdgeDef
        self.Vertices = [] # VertDef
        self.Faces = [] # FaceDef

    def clone(self):
        newPG = copy.deepcopy(self)
        return newPG
    
    def addVertex(self,
                  pos): # vec2f
        "returns the index of the new vertex"
        vertDef = VertDef(pos)
        self.Vertices.append(vertDef)
        return len(self.Vertices) - 1

    def findOrAddVertex(self,
                        pos, #vec2f
                        proximity = 1): 
        "returns the index of the vertex at that point. Could be new."
        for vi, v in enumerate(self.Vertices):
            d = pos - v.pos
            if d.magnitude() < proximity:
                return vi
        return self.addVertex(pos)

    def matchingTag(self, tagNum):
        matchDict={
            1: 4,
            2: 3,
            3: 2,
            4: 1}
        return matchDict[tagNum]

    def addEdge(self,
                vertIndex1,
                vertIndex2,
                label):
        edgeDef1 = HalfEdgeDef(vertIndex1,
                               label,
                               -1,
                               -1,
                               -1,
                               -1)
        
        edgeDef2 = HalfEdgeDef(vertIndex2,
                               self.matchingTag(label),
                               -1,
                               -1,
                               -1,
                               -1)
        
        self.HalfEdges.append(edgeDef1)
        self.HalfEdges.append(edgeDef2)
        ei1 = len(self.HalfEdges) - 2
        ei2 = len(self.HalfEdges) - 1
        edgeDef1.twinIndex = ei2
        edgeDef2.twinIndex = ei1

        edgeDef1.nextEdgeIndex = ei2
        edgeDef2.nextEdgeIndex = ei1
        edgeDef1.prevEdgeIndex = ei2
        edgeDef2.prevEdgeIndex = ei1
        if self.Vertices[vertIndex1].edgeIndex == -1:
            self.Vertices[vertIndex1].edgeIndex = ei1
        if self.Vertices[vertIndex2].edgeIndex == -1:
            self.Vertices[vertIndex2].edgeIndex = ei2
            
        return ei2

    def addFaceOld(self,
                edgeIndexList, #list(indices)
                faceTag):
        "returns a face index"
        fd = FaceDef(edgeIndexList[0])
        self.Faces.append(fd)

        #print "adding face",edgeIndexList

        # stitch together all pointers
        
        e0i, e1i, e2i, e3i = edgeIndexList
        e0, e1, e2, e3 = [self.HalfEdges[x] for x in edgeIndexList]
        e0ti, e1ti, e2ti, e3ti = [self.HalfEdges[x].twinIndex for x in edgeIndexList]
        e0t, e1t, e2t, e3t = [self.HalfEdges[x] for x in [e0ti, e1ti, e2ti, e3ti]]

        e0dc = (e0.nextEdgeIndex == e0.twinIndex)
        e1dc = (e1.nextEdgeIndex == e1.twinIndex)
        e2dc = (e2.nextEdgeIndex == e2.twinIndex)
        e3dc = (e3.nextEdgeIndex == e3.twinIndex)

        oldNextIndex0 = e0.nextEdgeIndex
        oldPrevIndex0 = e0.prevEdgeIndex
        oldNextIndex1 = e1.nextEdgeIndex
        oldPrevIndex1 = e1.prevEdgeIndex
        oldNextIndex2 = e2.nextEdgeIndex
        oldPrevIndex2 = e2.prevEdgeIndex
        oldNextIndex3 = e3.nextEdgeIndex
        oldPrevIndex3 = e3.prevEdgeIndex
        #print "oldPrev:", oldPrevIndex
        #print "oldNext:", oldNextIndex
        oldNext = self.HalfEdges[oldNextIndex]
        oldPrev = self.HalfEdges[oldPrevIndex]
        
        e0.nextEdgeIndex = e1i
        e1.nextEdgeIndex = e2i
        e2.nextEdgeIndex = e3i
        e3.nextEdgeIndex = e0i

        e0.prevEdgeIndex = e3i
        e1.prevEdgeIndex = e0i
        e2.prevEdgeIndex = e1i
        e3.prevEdgeIndex = e2i

        if e1dc:
            e1t.nextEdgeIndex = oldNextIndex0
            this.HalfEdges[oldNextIndex0].prevEdgeIndex=e1ti
        if e2dc:
            e2t.nextEdgeIndex = oldNextIndex1
        e3t.nextEdgeIndex = oldNextIndex2
        e0t.nextEdgeIndex

        e1t.prevEdgeIndex = e2ti
        e2t.prevEdgeIndex = e3ti
        e3t.prevEdgeIndex = oldPrevIndex
        oldNext.prevEdgeIndex = e1ti
        
        fi = len(self.Faces)-1

        e0.faceIndex = fi
        e1.faceIndex = fi
        e2.faceIndex = fi
        e3.faceIndex = fi
        
        return fi

    def addFace(self,
                edgeIndexList, #list(indices)
                faceTag):
        "returns a face index"
        fd = FaceDef(edgeIndexList[0])
        self.Faces.append(fd)

        #print "adding face",edgeIndexList
        
        fi = len(self.Faces)-1

        e0, e1, e2, e3 = [self.HalfEdges[x] for x in edgeIndexList]
        
        e0.faceIndex = fi
        e1.faceIndex = fi
        e2.faceIndex = fi
        e3.faceIndex = fi
        
        return fi

    def spliceEdges(self, e0i, e1i):
        e0 = self.HalfEdges[e0i]
        e1 = self.HalfEdges[e1i]
        if e0.nextEdgeIndex == e1i:
            return

        e0oldNextIndex = e0.nextEdgeIndex
        e1oldPrevIndex = e1.prevEdgeIndex
        e0oldNext = self.HalfEdges[e0oldNextIndex]
        e1oldPrev = self.HalfEdges[e1oldPrevIndex]
        e0.nextEdgeIndex = e1i
        e1.prevEdgeIndex = e0i
        e1oldPrev.nextEdgeIndex = e0oldNextIndex
        e0oldNext.prevEdgeIndex = e1oldPrevIndex
    
    def removeFace(self,
                   faceIndex):
        # TODO
        pass

    def getVertIndicesForEdge(self,
                              edgeIndex):
        halfEdge = self.HalfEdges[edgeIndex]
        vi1 = halfEdge.originVertIndex
        vi2 = self.HalfEdges[halfEdge.twinIndex].originVertIndex
        return (vi1, vi2)
    
    def getVertPosnsForEdge(self,
                            edgeIndex):
        halfEdge = self.HalfEdges[edgeIndex]
        vi1 = halfEdge.originVertIndex
        vi2 = self.HalfEdges[halfEdge.twinIndex].originVertIndex
        vec1 = self.Vertices[vi1].pos
        vec2 = self.Vertices[vi2].pos
        return (vec1, vec2)

    def getVertIndicesForFace(self,
                              faceIndex):
        vertIndices = []
        edgeIndex = self.Faces[faceIndex].boundingEdgeIndex
        while True:
            e = self.HalfEdges[edgeIndex]
            if e.originVertIndex in vertIndices:
                assert (e.originVertIndex == vertIndices[0])
                return vertIndices
            vertIndices.append(e.originVertIndex)
            edgeIndex = e.nextEdgeIndex
            
    def getVertPosnsForFace(self,
                            faceIndex):
        return [self.Vertices[vi].pos for vi in self.getVertIndicesForFace(faceIndex)]

    def isHalfEdgeLowerThanTwin(self,
                                edgeIndex):
        halfEdge = self.HalfEdges[edgeIndex]
        return edgeIndex < halfEdge.twinIndex

    def allEdgeIndicesLeavingVertIndex(self,
                                       vertIndex):
        #print "getting all edges leaving",vertIndex
        e0i = self.Vertices[vertIndex].edgeIndex
        if e0i == -1:
            return []
        edgeIndices = [e0i]

        #print "starting at",e0i
        
        thisIndex = e0i
        while True:
            thisEdge = self.HalfEdges[thisIndex]
            prevEdge = self.HalfEdges[thisEdge.prevEdgeIndex]
            ptwi = prevEdge.twinIndex
            #print "found",ptwi
            if ptwi == e0i:
                #print "stopping"
                break
            assert(not(ptwi in edgeIndices))
            edgeIndices.append(ptwi)
            thisIndex = ptwi

        return edgeIndices

    def getEdgeIndexByVertIndices(self, v0i, v1i):
        if ((v0i >= len(self.Vertices)) or
            (v1i >= len(self.Vertices))):
            #print "vert out of bounds!"
            return -1
        v0 = self.Vertices[v0i]
        v1 = self.Vertices[v1i]

        if ((v0.edgeIndex == -1) or
            (v1.edgeIndex == -1)):
            return -1

        for ei in self.allEdgeIndicesLeavingVertIndex(v0i):
            ev0i, ev1i = self.getVertIndicesForEdge(ei)
            if ev1i == v1i:
                return ei

        return -1

    def checkVertexAngles(self, vi):
        #print "checking angles at vertex", vi
        thisPos = self.Vertices[vi].pos
        tx = thisPos.x
        ty = thisPos.y
        edgeIndices = self.allEdgeIndicesLeavingVertIndex(vi)
        if len(edgeIndices) == 1:
            return True
        
        #print "cva edgeIndices:", edgeIndices

        edges = [self.HalfEdges[i] for i in edgeIndices]
        otherVertIndices = [self.getVertIndicesForEdge(ei)[1] for ei in edgeIndices]
        #print "cva otherVertIndices:", otherVertIndices
        otherPosns = [self.Vertices[vi].pos for vi in otherVertIndices]
        absAngles = [math.atan2(p.y - ty, p.x-tx) for p in otherPosns]
        clampedAngles = [angleWrapRadians(absAngles[ai] - absAngles[ai-1]) for ai in range(len(absAngles))]
        #print "cva clampedAngles:", clampedAngles
        s = sum(clampedAngles)
        #print "sum:", s
        if (s/(math.pi * 2.0)) > 1.01:
            #print "does not fit"
            return False
        return True

    def dump(self):
        print "debug dump"
        print "edges"
        for ei, e in enumerate(self.HalfEdges):
            print "{0} - prev: {1} next: {2} twin: {3} face: {4} vert: {5} tag: {6}".format(ei, e.prevEdgeIndex, e.nextEdgeIndex, e.twinIndex, e.faceIndex, e.originVertIndex, e.label)
        print "vertices"
        for vi, v in enumerate(self.Vertices):
            print "{0} - edge: {1} x: {2} y: {3}".format(vi, v.edgeIndex, v.pos.x, v.pos.y)

        print "faces"
        for fi, f in enumerate(self.Faces):
            print "{0} - edge: {1}".format(fi, f.boundingEdgeIndex)
                   

    
            
        
                               
                
    
                     
    
