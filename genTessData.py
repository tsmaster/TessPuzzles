from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import json
import math
import random
import sys

import bdggeom
import drawcontext
import font
import grids
import halfplane
import shapes

CUT_COLOR = (0, 0, 1)
ENGRAVE_COLOR = (1, 0, 0)
LABEL_COLOR = (1, 0, 0)


"""
TODO
support definition with more than one piece
support engrave lines
support "logical" neighbor connection lines
support "optional cut" lines
support curvy, hi-res lines for circles, lizard legs
"""

class PuzzDesc:
    def __init__(self, pdDict):
        self.pdDict = pdDict

    def getRandomSeed(self):
        return self.pdDict["seed"]

    def getGridName(self):
        return self.pdDict["grid_type"]

    def getTileEdgeLength(self):
        return float(self.pdDict["tile_edge_length_inches"])

    def isFixedGridRotation(self):
        return self.pdDict["is_fixed_grid_rotation"]

    def getFixedGridRotation(self):
        return float(self.pdDict["fixed_grid_rotation"])

    def getPiecePointsAndTransformations(self):
        # TODO support multipiece

        points = []
        for p in self.pdDict["points"]:
            x, y = p
            points.append((x,y))
        transformations = []
        
        for t in self.pdDict["transformations"]:
            if t["type"] == "rotation":
                c = t["center"]
                cx, cy = c
                jc = int(t["join_count"])
                transformations.append(shapes.makeRotationDesc(jc,
                                                               (cx, cy)))
            elif t["type"] == "translation":
                o = t["offset"]
                ox, oy = o
                transformations.append(shapes.makeTranslationDesc((ox, oy)))
        yield (points, transformations)

        return

    def getBorderWidthInches(self):
        return float(self.pdDict["border_width_inches"])

    def getPageWidthInches(self):
        return float(self.pdDict["page_width_inches"])
                
    def getPageHeightInches(self):
        return float(self.pdDict["page_height_inches"])

    def getPieceCount(self):
        return int(self.pdDict["piece_count"])

    def isLimitedRun(self):
        return self.pdDict["limited_run"]

    def getLimitedRunCount(self):
        return self.pdDict["run_count"]

    def getName(self):
        return self.pdDict["name"]

    def getOutputFilename(self):
        return self.pdDict["out_filename"]

    def isPDFEnabled(self):
        return self.pdDict["output_to_pdf"]

    def isSVGEnabled(self):
        return self.pdDict["output_to_svg"]
        

def getPuzzDesc(puzzName, filename="pieces.json"):
    fileData = open(filename).read()
    pieceList = json.loads(fileData)

    for p in pieceList:
        print p["name"], "loaded"
    for p in pieceList:
        if p["name"] == puzzName:
            return PuzzDesc(p)
    return None

def completelyInsideAllHalfPlanes(vecList, halfPlanes):
    for hp in halfPlanes:
        if hp.areAnyPointsOutside(vecList):
            return False
    return True

def partiallyOutsideAnyHalfPlane(vecList, halfPlanes):
    return not completelyInsideAllHalfPlanes(vecList, halfPlanes)

def completelyOutsideAnyHalfPlane(vecList, halfPlanes):
    for hp in halfPlanes:
        if hp.areAllPointsOutside(vecList):
            return True
    return False

def cullPiecesByHalfPlanes(pieceList, halfPlanes):
    filteredPieces = []
    for p in pieceList:
        vecList = list(p.getVects())
        if not completelyOutsideAnyHalfPlane(vecList, halfPlanes):
            filteredPieces.append(p)
    return filteredPieces



def findVecInList(vecList, vec, tolerance):
    if not vecList:
        return -1
    belowIndex = 0
    aboveIndex = len(vecList) - 1
    while True:
        #print "checking", belowIndex, aboveIndex
        testIndex = (belowIndex + aboveIndex) / 2
        testVec = vecList[testIndex]

        if (aboveIndex == belowIndex):
            if (testVec - vec).magnitude() < tolerance:
                return aboveIndex
            else:
                return -1
        elif (aboveIndex == belowIndex + 1):
            belowVec = vecList[belowIndex]
            aboveVec = vecList[aboveIndex]
            if (belowVec - vec).magnitude() < tolerance:
                return belowIndex
            elif (aboveVec - vec).magnitude() < tolerance:
                return aboveIndex
            else:
                return -1
        
        if vec < testVec:
            aboveIndex = testIndex
        elif vec > testVec:
            belowIndex = testIndex
        else:
            return testIndex

def insertVecIntoList(vecList, vec):
    if not vecList:
        vecList.append(vec)
        return 0
    else:
        return insertVecIntoListWithIndices(vecList, vec, 0, len(vecList) - 1)

def insertVecIntoListWithIndices(vecList, vec, belowIndex, aboveIndex):
    if belowIndex == aboveIndex:
        existingVec = vecList[belowIndex]
        if vec < existingVec:
            vecList.insert(belowIndex, vec)
            return belowIndex
        elif vec > existingVec:
            vecList.insert(belowIndex + 1, vec)
            return belowIndex + 1
        else:
            return belowIndex
    elif aboveIndex == belowIndex + 1:
        existingBelowVec = vecList[belowIndex]
        existingAboveVec = vecList[aboveIndex]
        if vec < existingBelowVec:
            vecList.insert(belowIndex, vec)
            return belowIndex
        elif vec > existingAboveVec:
            vecList.insert(aboveIndex + 1, vec)
            return aboveIndex + 1
        else:
            vecList.insert(aboveIndex, vec)
            return aboveIndex
    else:
        testIndex = (aboveIndex + belowIndex) / 2
        existingVec = vecList[testIndex]
        if vec < existingVec:
            return insertVecIntoListWithIndices(vecList, vec, belowIndex, testIndex)
        elif vec > existingVec:
            return insertVecIntoListWithIndices(vecList, vec, testIndex, aboveIndex)
        else:
            return testIndex

def collectVertices(triList, tolerance):
    verts = []
    for t in triList:
        for tv in t.verts:
            foundDup = False
            tVec = bdggeom.Vec2f(*tv)
            fInd = findVecInList(verts, tVec, tolerance)
            if (fInd == -1):
                #print "adding",tVec
                insertVecIntoList(verts, tVec)
            else:
                #print "found existing"
                pass
    return verts


def makeInnerHalfPlanes(puzzleDesc):
    bwi = puzzleDesc.getBorderWidthInches()
    pwi = puzzleDesc.getPageWidthInches()
    phi = puzzleDesc.getPageWidthInches()
    
    leftHP = halfplane.HalfPlane(bdggeom.Vec2f(bwi, 0),
                                 bdggeom.Vec2f(1, 0))
    
    rightHP = halfplane.HalfPlane(bdggeom.Vec2f(pwi - bwi, 0),
                                  bdggeom.Vec2f(-1, 0))
    
    bottomHP = halfplane.HalfPlane(bdggeom.Vec2f(0, bwi),
                                 bdggeom.Vec2f(0, 1))
    
    topHP = halfplane.HalfPlane(bdggeom.Vec2f(0, phi - bwi),
                                bdggeom.Vec2f(0, -1))
    
    innerHalfPlanes = [leftHP, rightHP, bottomHP, topHP]
    return innerHalfPlanes

def makeOuterHalfPlanes(puzzleDesc):
    bwi = puzzleDesc.getBorderWidthInches()
    pwi = puzzleDesc.getPageWidthInches()
    phi = puzzleDesc.getPageWidthInches()
    
    leftHP = halfplane.HalfPlane(bdggeom.Vec2f(0 - bwi, 0),
                                 bdggeom.Vec2f(1, 0))
    
    rightHP = halfplane.HalfPlane(bdggeom.Vec2f(pwi + bwi,
                                                0),
                                  bdggeom.Vec2f(-1, 0))
    
    bottomHP = halfplane.HalfPlane(bdggeom.Vec2f(0, 0 - bwi),
                                   bdggeom.Vec2f(0, 1))
    
    topHP = halfplane.HalfPlane(bdggeom.Vec2f(0, phi + bwi),
                                bdggeom.Vec2f(0, -1))

    outerHalfPlanes = [leftHP, rightHP, bottomHP, topHP]
    return outerHalfPlanes

def makeExactHalfPlanes(puzzleDesc):
    pwi = puzzleDesc.getPageWidthInches()
    phi = puzzleDesc.getPageWidthInches()
    
    leftHP = halfplane.HalfPlane(bdggeom.Vec2f(0, 0),
                                 bdggeom.Vec2f(1, 0))

    rightHP = halfplane.HalfPlane(bdggeom.Vec2f(pwi, 0),
                                  bdggeom.Vec2f(-1, 0))

    bottomHP = halfplane.HalfPlane(bdggeom.Vec2f(0, 0),
                                 bdggeom.Vec2f(0, 1))

    topHP = halfplane.HalfPlane(bdggeom.Vec2f(0, phi),
                                  bdggeom.Vec2f(0, -1))

    exactHalfPlanes = [leftHP, rightHP, bottomHP, topHP]
    return exactHalfPlanes

def makeClustersWithRelaxation(pieces, numClusters, width, height):
    seedVertices = {}
    for clusterIndex in range(1, numClusters + 1):
        seedVertices[clusterIndex] = bdggeom.Vec2f(random.uniform(0, width),
                                                   random.uniform(0, height))
    TOLERANCE = 0.01
    while True:
        setClustersByProximity(pieces, seedVertices)
        anyMoved = False
        for clusterIndex, clusterCenter in seedVertices.iteritems():
            newClusterCenter = findClusterCenter(pieces, clusterIndex)
            if newClusterCenter is None:
                anyMoved = True
                continue
            
            dist = (clusterCenter - newClusterCenter).magnitude()
            if dist > TOLERANCE:
                anyMoved = True
                #print "cluster {0} moved by {1}".format(clusterIndex, dist)
            seedVertices[clusterIndex] = newClusterCenter
        if not anyMoved:
            return

def findClusterCenter(pieces, clusterIndex):
    centerPoint = bdggeom.Vec2f(0, 0)
    pieceCount = 0
    for p in pieces:
        if p.clusterIndex == clusterIndex:
            pieceCount += 1
            centerPoint += p.getCenter()
    if pieceCount == 0:
        return None
    return centerPoint * (1.0 / pieceCount)

def setClustersByProximity(pieces, seedVertices):
    for p in pieces:
        if p.clusterIndex == 0:
            continue
        pc = p.getCenter()
        bestCluster = -1
        bestDistance = None
        for ci, seedVec in seedVertices.iteritems():
            dist = (seedVec - pc).magnitude()
            if ((bestCluster == -1) or
                (dist < bestDistance)):
                bestCluster = ci
                bestDistance = dist
        p.clusterIndex = bestCluster

def unsetStragglers(pieces):
    lowestConnectedPieceIndexByPieceIndex = {}
    for pi in range(len(pieces)):
        lowestConnectedPieceIndexByPieceIndex[pi] = pi
        
    while True:
        hasFoundNewConnection = False
        for pi, piece in enumerate(pieces):
            connectedPieceIndices = []
            for ni in piece.neighborPieces:
                neighborPiece = pieces[ni]
                if neighborPiece.clusterIndex == piece.clusterIndex:
                    connectedPieceIndices.append(ni)
            lowestRoot = pi
            for cpi in connectedPieceIndices:
                root = lowestConnectedPieceIndexByPieceIndex[cpi]
                if root < lowestRoot:
                    lowestRoot = root
            if lowestRoot < lowestConnectedPieceIndexByPieceIndex[pi]:
                hasFoundNewConnection = True
                lowestConnectedPieceIndexByPieceIndex[pi] = lowestRoot

        if not hasFoundNewConnection:
            break

    lowestConnectionsByClusterIndex = {}
    
    for pi, piece in enumerate(pieces):
        if lowestConnectedPieceIndexByPieceIndex[pi] == pi:
            ci = piece.clusterIndex
            if not (ci in lowestConnectionsByClusterIndex):
                lowestConnectionsByClusterIndex[ci] = []
            lowestConnectionsByClusterIndex[ci].append(pi)
    for ci in lowestConnectionsByClusterIndex:
        if len(lowestConnectionsByClusterIndex[ci]) > 1:
            print ci, lowestConnectionsByClusterIndex[ci], "DUP"

            biggestComponentRoot = findBiggestComponentRoot(pieces,
                                                            lowestConnectedPieceIndexByPieceIndex,
                                                            lowestConnectionsByClusterIndex,
                                                            ci)

            for pi, piece in enumerate(pieces):
                if ((piece.clusterIndex == ci) and
                    (lowestConnectedPieceIndexByPieceIndex[pi] != biggestComponentRoot)):
                    piece.clusterIndex = -1
                    print "removing straggler", pi

        else:
            print ci, lowestConnectionsByClusterIndex[ci]

def anyUnset(pieces):
    for piece in pieces:
        if piece.clusterIndex == -1:
            return True
    return False

def randomlyAssignUnset(pieces):
    while anyUnset(pieces):
        for pi, piece in enumerate(pieces):
            if piece.clusterIndex != -1:
                continue
            print "pi", pi, piece
            print "neighbors:", piece.neighborPieces
            if len(piece.neighborPieces) == 0:
                print "found a piece with no neighbors"
                piece.clusterIndex = 0
                piece.isBorder = True
                continue
            assert(len(piece.neighborPieces)> 0)
            randNeighborIndex = random.choice(piece.neighborPieces)
            randNeighbor = pieces[randNeighborIndex]
            piece.clusterIndex = randNeighbor.clusterIndex
        

def componentSizeByLowestConnectedRI(rhombList, lri, lowestConnectedRIByRI):
    c = 0
    for ri, r in enumerate(rhombList):
        if lowestConnectedRIByRI[ri] == lri:
            c += 1
    return c

def findBiggestComponentRoot(rhombList,
                             lcrbr,
                             lcbci,
                             ci):
    sizes = []
    for c in lcbci[ci]:
        s = componentSizeByLowestConnectedRI(rhombList, c, lcrbr)
        sizes.append((s, c))
    sizes.sort()
    print "sizes:", sizes
    return sizes[-1][1]

def sortByDistanceFromPoint(pieces, pieceIndices, center):
    distIndices = []
    for pi in pieceIndices:
        p = pieces[pi]
        pc = p.getCenter()
        d = (center - pc).magnitude()
        distIndices.append((d, pi))
    distIndices.sort()
    return distIndices

def findCenterOfUnusedPieces(pieces):
    centroid = bdggeom.Vec2f(0, 0)
    unusedCount = 0
    unusedIndices = getUnusedPieceIndices(pieces)
    if not unusedIndices:
        return None
    for ui in unusedIndices:
        ur = pieces[ui]
        urc = ur.getCenter()
        centroid += urc
        unusedCount += 1
    return centroid * (1.0 / unusedCount)

def findSeedPiece(pieces):
    if not pieces:
        return None
    # find center of unused pieces from pieces
    centerPoint = findCenterOfUnusedPieces(pieces)
    # sort pieces by distance from center
    pil = getUnusedPieceIndices(pieces)
    if not pil:
        print "didn't find any unused pieces"
        return None
    spil = sortByDistanceFromPoint(pieces, pil, centerPoint)
    # return farthest index
    try:
        r = spil[-1][1]
    except IndexError:
        #print "pieces:", pieces
        print "pil:", pil
        print "spil:", spil
        print "spil[-1]:", spil[-1]
        exit(-1)
    return spil[-1][1]

def getUnusedPieceIndices(pieces):
    indices = []
    for ri, r in enumerate(pieces):
        if r.clusterIndex == -1:
            indices.append(ri)
    return indices

def makeClusterFromFarthestFromCenter(pieces, newClusterCount, clusterIndex):
    seedPieceIndex = findSeedPiece(pieces)
    seedPiece = pieces[seedPieceIndex]
    seedCenter = seedPiece.getCenter()
    upiList = getUnusedPieceIndices(pieces)
    supiList = sortByDistanceFromPoint(pieces, upiList, seedCenter)

    if newClusterCount >= len(supiList):
        pass
    else:
        supiList = supiList[:newClusterCount]
    for d,i in supiList:
        pieces[i].clusterIndex = clusterIndex

def growClusterFromSeeds(rhombList, seedIndices, newClusterCount, clusterIndex):
    seedRhombIndex = findSeedRhomb(rhombList)
    # start the cluster with that seed

    while getClusterCount(clusterIndex) < newClusterCount:
        # find all unused rhombs on border of cluster
        adjRhombs = getRhombsAdjacentToCluster(clusterIndex)
        if not adjRhombs:
            return False
        getCenterOfCluster(clusterIndex)
        # pick rhomb closest to the center
        # add it to the cluster
    return True


def drawPieces(c, pieces):
    for p in pieces:
        p.drawToCanvas(c)

def drawPiecesWithColor(c, pieces, rgb):
    c.setStrokeColorRGB(*rgb)
    for p in pieces:
        p.drawToCanvas(c)

def drawRhombsWithStrokeColor(c, pieces, rgb):
    c.setStrokeColorRGB(*rgb)
    for p in pieces:
        p.drawToCanvas(c)

def drawRhombsWithFillColor(c, rhombList, vertList, rgb):
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(*rgb)
    for r in rhombList:
        r.drawToCanvas(c, vertList, stroke = 0, fill = 1)

        
def clipEdgeToHalfPlane(e, hp):
    if e is None:
        return None
    
    if hp.areAllPointsOutside(e):
        return None
    if hp.areAllPointsInside(e):
        return e
    v0, v1 = e
    c0 = hp.characterizePoint(v0)
    c1 = hp.characterizePoint(v1)

    if c0 == c1:
        return e

    t = (0 - c0) / (c1 - c0)
    midpoint = v0 + (v1 - v0) * t

    if c0 < 0:
        #print "LT", midpoint, v1
        return (midpoint, v1)
    else:
        #print "GT", v0, midpoint
        return (v0, midpoint)

def clipEdgeToHalfPlaneList(e, hpl):
    if e is None:
        return None
    for hp in hpl:
        e = clipEdgeToHalfPlane(e, hp)
        if e is None:
            return None
    return e

def drawEdges(c, vertList, rhombList, clipLeft, clipBottom, clipRight, clipTop):
    edges = {}

    halfPlanes = [
        halfplane.HalfPlane(bdggeom.Vec2f(clipLeft, clipBottom),
                            bdggeom.Vec2f(1, 0)),
        halfplane.HalfPlane(bdggeom.Vec2f(clipLeft, clipBottom),
                            bdggeom.Vec2f(0, 1)),
        halfplane.HalfPlane(bdggeom.Vec2f(clipRight, clipTop),
                            bdggeom.Vec2f(-1, 0)),
        halfplane.HalfPlane(bdggeom.Vec2f(clipRight, clipTop),
                            bdggeom.Vec2f(0, -1)),
        ]

    for ri, r in enumerate(rhombList):
        for vii in range(len(r.vertIndices)):
            vi0 = r.vertIndices[vii-1]
            vi1 = r.vertIndices[vii]

            key = min((vi0, vi1), (vi1, vi0))
            edgeList = edges.get(key, [])
            edgeList.append(ri)
            edges[key] = edgeList

    for key in edges:
        isCut = False

        rhombs = edges[key]
        #if len(rhombs) == 1:
        #    isCut = True
        if len(rhombs) == 2:
            ri0, ri1 = rhombs
            r0 = rhombList[ri0]
            r1 = rhombList[ri1]
            if (r0.clusterIndex != r1.clusterIndex):
                isCut = True

        if isCut:
            c.setStrokeColorRGB(*CUT_COLOR)
        else:
            c.setStrokeColorRGB(*ENGRAVE_COLOR)
        vi0, vi1 = key
        v0 = vertList[vi0]
        v1 = vertList[vi1]
        newEdge = clipEdgeToHalfPlaneList((v0, v1), halfPlanes)

        if newEdge is None:
            continue
        
        v0, v1 = newEdge
        
        p = c.beginPath()
        p.moveTo(v0.x, v0.y)
        p.lineTo(v1.x, v1.y)
        c.drawPath(p, stroke=1, fill=0)

def drawBoundingBox(drawContext, left, bottom, right, top):
    drawContext.setStrokeColorRGB(*CUT_COLOR)
    p = drawContext.beginPath()
    p.moveTo(left, bottom)
    p.lineTo(left, top)
    p.lineTo(right, top)
    p.lineTo(right, bottom)
    p.lineTo(left,bottom)
    drawContext.drawPath(p)
    
    
    


class TessPiece:
    def __init__(self, points, transformations, grid):
        self.points = points  # untransformed, grid indexed pairs
        self.transformations = transformations
        self.grid = grid
        self.transformMatrix = bdggeom.makeIdentityMatrix()
        self.neighborPieces = []

    def appendTranslation(self, dx, dy):
        self.transformMatrix = bdggeom.makeTranslationMatrix(dx, dy).mulMat(self.transformMatrix)

    def appendRotation(self, theta):
        """ theta is in radians """
        self.transformMatrix = bdggeom.makeRotationMatrix(theta).mulMat(self.transformMatrix)

    def collectVertices(self):
        """ transforms self.points by self.transformMatrix, returning a list of vec2fs"""
        verts = []
        for p in self.points:
            wx, wy = self.grid.indexToWorld(*p)
            wVec = bdggeom.Vec2f(wx, wy)
            tVec = self.transformMatrix.mulVec(wVec)
            verts.append(tVec)
        return verts

    def copy(self):
        newPiece = TessPiece(self.points, self.transformations, self.grid)
        newPiece.transformMatrix = self.transformMatrix
        return newPiece

    def makeTransformedNeighbors(self):
        neighbors = []
        for transform in self.transformations:
            n = self.copy()
            tm = transform.makeMatrix(self.grid)
            n.transformMatrix = n.transformMatrix.mulMat(tm)
            neighbors.append(n)
            n = self.copy()
            itm = transform.makeInverseMatrix(self.grid)
            n.transformMatrix = n.transformMatrix.mulMat(itm)
            neighbors.append(n)
        return neighbors

    def collectTransformedVertices(self):
        vecs = []
        for ip in self.points:
            ptCvt = self.grid.indexToWorld(*ip)
            cvtVec = bdggeom.Vec2f(*ptCvt)
            transformed = self.transformMatrix.mulVec(cvtVec)
            vecs.append(transformed)
        return vecs

    def getCenter(self):
        cv = bdggeom.Vec2f(0, 0)
        for v in self.collectTransformedVertices():
            cv += v
        cv *= (1.0 / len(self.points))
        return cv

    def makeIndexedVertexList(self):
        self.indexedVertexList = []
        for v in self.collectTransformedVertices():
            ix, iy = self.grid.snapWorldToIndices(v.x, v.y)
            self.indexedVertexList.append((ix, iy))

    def drawDebugToCanvas(self, c):
        p = c.beginPath()
        ptCvt0 = self.grid.indexToWorld(*self.points[0])
        p.moveTo(*ptCvt0)
        for pt in self.points[1:]:
            ptCvt = self.grid.indexToWorld(*pt)
            p.lineTo(*ptCvt)
        p.lineTo(*ptCvt0)
        c.drawPath(p, stroke = 1)

    def drawDebugTransformedToCanvas(self, c):
        p = c.beginPath()
        ptCvt0 = self.grid.indexToWorld(*self.points[0])
        cvtVec0 = bdggeom.Vec2f(*ptCvt0)
        transformed0 = self.transformMatrix.mulVec(cvtVec0)
        p.moveTo(transformed0.x, transformed0.y)
        for pt in self.points[1:]:
            ptCvt = self.grid.indexToWorld(*pt)
            cvtVec = bdggeom.Vec2f(*ptCvt)
            transformed = self.transformMatrix.mulVec(cvtVec)
            p.lineTo(transformed.x, transformed.y)
        p.lineTo(transformed0.x, transformed0.y)
        c.drawPath(p)

    def drawColoredPieceToCanvas(self, drawContext, color):
        drawContext.setFillColorRGB(*color)
        p = drawContext.beginPath()
        ptCvt0 = self.grid.indexToWorld(*self.points[0])
        cvtVec0 = bdggeom.Vec2f(*ptCvt0)
        transformed0 = self.transformMatrix.mulVec(cvtVec0)
        p.moveTo(transformed0.x, transformed0.y)
        for pt in self.points[1:]:
            ptCvt = self.grid.indexToWorld(*pt)
            cvtVec = bdggeom.Vec2f(*ptCvt)
            transformed = self.transformMatrix.mulVec(cvtVec)
            p.lineTo(transformed.x, transformed.y)
        p.lineTo(transformed0.x, transformed0.y)
        drawContext.drawFilledPath(p)

    def matchesIndexedVertices(self, other):
        for vi, indexPair in enumerate(self.indexedVertexList):
            otherPair = other.indexedVertexList[vi]
            if (not (self.grid.snappedPairsMatch(indexPair,otherPair))):
                return False
        return True

    def totallyOutside(self, halfPlaneList):
        verts = self.collectTransformedVertices()
        return completelyOutsideAnyHalfPlane(verts, halfPlaneList)

    def partiallyOutside(self, halfPlaneList):
        verts = self.collectTransformedVertices()
        return partiallyOutsideAnyHalfPlane(verts, halfPlaneList)
    
    def getIndexedEdges(self):
        for vi, indexPair in enumerate(self.indexedVertexList):
            prevIndexPair = self.indexedVertexList[vi - 1]
            if indexPair < prevIndexPair:
                yield (indexPair, prevIndexPair)
            else:
                yield (prevIndexPair, indexPair)

    def findNeighborsFromEdgeDictionary(self, edgeToPieceDictionary):
        self.neighborPieces = []
        if self.grid.getSnapToInts():
            for e in self.getIndexedEdges():
                for ni in edgeToPieceDictionary[e]:
                    if ((ni == self.pieceIndex) or ni in self.neighborPieces):
                        continue
                    self.neighborPieces.append(ni)
        else:
            for e in self.getIndexedEdges():
                e1, e2 = e
                for ne in edgeToPieceDictionary.keys():
                    ne1, ne2 = ne
                    if (self.grid.snappedPairsMatch(e1, ne1) and
                        self.grid.snappedPairsMatch(e2, ne2)):
                        for ni in edgeToPieceDictionary[ne]:
                            if ((ni == self.pieceIndex) or ni in self.neighborPieces):
                                continue
                            self.neighborPieces.append(ni)
                        break
                
    def addEdgesToEdgeDictionary(self, edgeToPieceDictionary):
        if self.grid.getSnapToInts():
            for e in self.getIndexedEdges():
                oldList = edgeToPieceDictionary.get(e,[])
                oldList.append(self.pieceIndex)
                edgeToPieceDictionary[e] = oldList
        else:
            for e in self.getIndexedEdges():
                e1, e2 = e
                foundMatch = False
                for ne in edgeToPieceDictionary.keys():
                    ne1, ne2 = ne

                    # TODO this is a HACK - shouldn't have to compare both ways, right?
                    if ((self.grid.snappedPairsMatch(e1, ne1) and
                         self.grid.snappedPairsMatch(e2, ne2)) or
                        (self.grid.snappedPairsMatch(e2, ne1) and
                         self.grid.snappedPairsMatch(e1, ne2))):
                        foundMatch = True
                        oldList = edgeToPieceDictionary[ne]
                        if self.pieceIndex in oldList:
                            print "piece already in oldlist. Weird"
                            print e1, e2
                            print ne1, ne2
                            print self.pieceIndex
                            print oldList
                            print len(edgeToPieceDictionary)
                        else:
                            oldList.append(self.pieceIndex)
                            edgeToPieceDictionary[ne] = oldList
                        break
                if not foundMatch:
                    edgeToPieceDictionary[e] = [self.pieceIndex]

                
                
                        

def makeGrid(puzzDesc):
    gn = puzzDesc.getGridName()
    el = puzzDesc.getTileEdgeLength()
    if gn == "square":
        grid = grids.makeSquareGrid(el)
    elif gn == "triangular":
        grid = grids.makeTriangularGrid(el)
    elif gn == "cartesian":
        # what does this mean?
        grid = grids.makeCartesianGrid(el)

    if puzzDesc.isFixedGridRotation():
        rot = puzzDesc.getFixedGridRotation()
    else:
        rot = random.uniform(0, 2*math.pi)
        
    grid.appendRotation(rot)
    return grid


def floodFillPieces(seedPieces, halfPlanes):
    openPieces = seedPieces[:]
    pieces = []

    while openPieces:
        #print "piece count:", len(openPieces)
        p = openPieces.pop()
        #print "top piece", p
        pieces.append(p)
        for n in p.makeTransformedNeighbors():
            n.makeIndexedVertexList()
            
            if (n.totallyOutside(halfPlanes)):
                continue

            foundDup = False
            for op in pieces:
                if n.matchesIndexedVertices(op):
                    foundDup = True
                    break
            if not foundDup:
                for op in openPieces:
                    if n.matchesIndexedVertices(op):
                        foundDup = True
                        break
            if not foundDup:
                openPieces.append(n)

    return pieces


class Puzzle:
    def __init__(self):
        self.desc = None
        self.vertexList = []
        self.pieces = []
        self.edgeToPieceIndexDictionary = {}

    def addPieceToVertexList(self, piece):
        """
        take all transformed verts, 
        snap to grid verts (as appropriate),
        then look for dups in our vertex list

        leverage:TessPiece.makeIndexedVertList()
        """
        piece.indexedVertexList = []
        for v in piece.collectTransformedVertices():
            sx, sy = self.grid.snapWorldToIndices(v.x, v.y)
            piece.indexedVertexList.append((sx, sy))

            #TODO maybe get the grid to help here?
            foundDup = False
            for oldVert in self.vertexList:
                if oldVert == (sx, sy):
                    foundDup = True
                    break
            if not foundDup:
                self.vertexList.append((sx, sy))

    def render(self):
        runCount = 1
        if self.desc.isLimitedRun():
            runCount = self.desc.getLimitedRunCount()

        for serialNumber in range(1, runCount + 1):
            if self.desc.isLimitedRun():
                runCountStr = str(self.desc.getLimitedRunCount())
                runCountDigitCount = len(runCountStr)
                serialNumberStr = str(serialNumber)
                while len(serialNumberStr) < runCountDigitCount:
                    serialNumberStr = "0" + serialNumberStr
                label = "{0} {1}/{2}".format(self.desc.getName(),
                                             serialNumberStr,
                                             runCountStr)
                filename = "{0}_{1}_{2}".format(self.desc.getOutputFilename(),
                                                serialNumberStr,
                                                runCountStr)
            else:
                label = self.desc.getName()
                filename = self.desc.getOutputFilename()

            drawContext = drawcontext.DrawContext(filename,
                                                  self.desc.getPageWidthInches(),
                                                  self.desc.getPageHeightInches(),
                                                  self.desc.isPDFEnabled(),
                                                  self.desc.isSVGEnabled())
            
            # TODO - support drawing strategies
            DRAW_SINGLE_PIECE = False
            if DRAW_SINGLE_PIECE:
                drawSinglePiece(drawContext, self.pieces[0])

            DRAW_SURROUND = False
            if DRAW_SURROUND:
                centerIndex = len(self.pieces)/2
                drawSinglePiece(drawContext, self.pieces[centerIndex])
                
                for ni in self.pieces[centerIndex].neighborPieces:
                    drawSinglePiece(drawContext, self.pieces[ni])
    
            debugColors = {
                0: (0.5, 0.5, 0.5),
                1: (1, 0, 0),
                2: (0, 1, 0),
                3: (0, 0, 1),
                4: (0.5, 1, 0),
                5: (0, 0.5, 1),
                6: (1, 0, 0.5),
                7: (1, 0.5, 0),
                8: (0, 1, 0.5),
                9: (0.5, 0, 1),
                }
        
            # draw colored clusters
            DRAW_COLORED_CLUSTERS = False
        
            if DRAW_COLORED_CLUSTERS:
                for p in self.pieces:
                    ci = p.clusterIndex
                    if ci not in debugColors:
                        debugColors[ci] = (random.uniform(0.2, 0.8),
                                           random.uniform(0.2, 0.8),
                                           random.uniform(0.2, 0.8))
                    p.drawColoredPieceToCanvas(drawContext, debugColors[ci])
        
            
            #for p in pieces:
            #    p.drawDebugTransformedToCanvas(c)
            
            # draw edges
            DRAW_EDGES = True
            if DRAW_EDGES:
                for e,pieceIndices in self.edgeToPieceIndexDictionary.iteritems():
                    isCut = False
                    isError = False
                    if len(pieceIndices) == 1:
                        isCut = False
                        isError = True
                    else:
                        if len(pieceIndices) != 2:
                            print "ERROR: found non-2 piece list in drawing edges:", pieceIndices
                        else:
                            p0, p1 = pieceIndices
                            if self.pieces[p0].clusterIndex != self.pieces[p1].clusterIndex:
                                isCut = True
            
                    v0, v1 = e
                    edge = (bdggeom.Vec2f(*self.grid.indexToWorld(*v0)),
                            bdggeom.Vec2f(*self.grid.indexToWorld(*v1)))
                    newEdge = clipEdgeToHalfPlaneList(edge, self.exactHalfPlanes)
                    if newEdge is None:
                        continue
                                
                    p = drawContext.beginPath()
                    if isError:
                        drawContext.setStrokeColorRGB(0, 0, 255)
                    elif isCut:
                        drawContext.setStrokeColorRGB(*CUT_COLOR)
                    else:
                        drawContext.setStrokeColorRGB(*ENGRAVE_COLOR)
            
                    v0, v1 = newEdge

                    if isError:
                        print "WARNING: found edge with one piece", e, pieceIndices
                    p.moveTo(v0.x, v0.y)
                    p.lineTo(v1.x, v1.y)
                    drawContext.drawPath(p)
        
            drawBoundingBox(drawContext, 0, 0,
                            self.desc.getPageWidthInches(),
                            self.desc.getPageHeightInches())
        
            drawContext.setStrokeColorRGB(*LABEL_COLOR)
        
            DRAW_LABEL = True
            if DRAW_LABEL:
                print "drawing label", label
                font.drawStringToDrawContext(drawContext,
                                             label,
                                             font.fontS2,
                                             bdggeom.Vec2f(0.3, 0.15),
                                             0.04)
        
            drawContext.save()


def makeBasePieces(puzzDesc,
                   grid):
    pieces = []

    # TODO support multiPiece

    for points, transformations in puzzDesc.getPiecePointsAndTransformations():
        p0 = TessPiece(points,
                       transformations,
                       grid)

        pieces.append(p0)

    return pieces

    

def makePuzzle(puzzleName):
    puzz = Puzzle()
    puzz.desc = getPuzzDesc(puzzleName) 

    if not puzz.desc:
        print "no puzzle description found"
        exit(-1)

    seed = puzz.desc.getRandomSeed()
    random.seed(seed)

    puzz.grid = makeGrid(puzz.desc)

    puzz.basePieces = makeBasePieces(puzz.desc, puzz.grid)

    puzz.vertexList = []

    puzz.pieces = []

    puzz.outerHalfPlanes = makeOuterHalfPlanes(puzz.desc)
    puzz.innerHalfPlanes = makeInnerHalfPlanes(puzz.desc)
    puzz.exactHalfPlanes = makeExactHalfPlanes(puzz.desc)

    for p in puzz.basePieces:
        puzz.addPieceToVertexList(p)
        #p0.makeIndexedVertexList()

    for p in floodFillPieces(puzz.basePieces, puzz.outerHalfPlanes):
        puzz.addPieceToVertexList(p)
        puzz.pieces.append(p)
    
    for pi, piece in enumerate(puzz.pieces):
        piece.pieceIndex = pi

    puzz.edgeToPieceIndexDictionary = {}

    for piece in puzz.pieces:
        piece.addEdgesToEdgeDictionary(puzz.edgeToPieceIndexDictionary)

    for pi,piece in enumerate(puzz.pieces):
        #print "finding neighbors for", pi
        piece.findNeighborsFromEdgeDictionary(puzz.edgeToPieceIndexDictionary)

    #for pi, piece in enumerate(puzz.pieces):
    #    print pi, len(piece.neighborPieces)

    for piece in puzz.pieces:
        piece.clusterIndex = -1

    for piece in puzz.pieces:
        if piece.partiallyOutside(puzz.innerHalfPlanes):
            piece.clusterIndex = 0

    makeClustersWithRelaxation(puzz.pieces, puzz.desc.getPieceCount(),
                               puzz.desc.getPageWidthInches(),
                               puzz.desc.getPageHeightInches())

    unsetStragglers(puzz.pieces)
    randomlyAssignUnset(puzz.pieces)
    
    return puzz


            
    

    
        



def drawSinglePiece(c, piece):
    piece.drawDebugTransformedToCanvas(c)

if __name__ == "__main__":
    # TODO fancier argument parsing
    if len(sys.argv) == 1:
        print "usage: genTessData.py <puzzname>*"
        exit(-1)
    
    for puzzName in sys.argv[1:]:
        print "trying to make puzzle name:", puzzName
        puzzle = makePuzzle(puzzName)
        print "rendering puzzle"
        puzzle.render()
        
