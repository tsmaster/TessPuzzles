import math

import bdggeom


class Grid:
    def __init__(self, unit):
        self.unit = unit
        self.bases = [bdggeom.Vec2f(unit, 0),
                      bdggeom.Vec2f(0, unit)]
        self.gridToWorldTransform = bdggeom.makeIdentityMatrix()
        self.worldToGridTransform = bdggeom.makeIdentityMatrix()

    def indexToWorld(self, ix, iy):
        p = (self.bases[0] * ix +
             self.bases[1] * iy)
        p = self.gridToWorldTransform.mulVec(p)
        return p.x, p.y

    def appendRotation(self, radians):
        rotMat = bdggeom.makeRotationMatrix(radians)
        self.gridToWorldTransform = rotMat.mulMat(self.gridToWorldTransform)
        invRotMat = bdggeom.makeRotationMatrix(-radians)
        self.worldToGridTransform = self.worldToGridTransform.mulMat(invRotMat)

    def appendTranslation(self, dx, dy):
        trans = bdggeom.makeTranslationMatrix(dx, dy)
        self.gridToWorldTransform = trans.mulMat(self.gridToWorldTransform)
        invTrans = bdggeom.makeTranslationMatrix(-dx, -dy)
        self.worldToGridTransform = self.worldToGridTransform.mulMat(invTrans)

    def invertMatrix(self, wx, wy):
        worldVec = bdggeom.Vec2f(wx, wy)
        localVec = self.worldToGridTransform.mulVec(worldVec)

        wx = localVec.x
        wy = localVec.y
        
        #wx = ix * self.bases[0].x + iy * self.bases[1].x 
        #wy = ix * self.bases[0].y + iy * self.bases[1].y

        #wx = ix * A + iy * B
        #wy = ix * C + iy * D

        # if A != 0
        # ix = (wx - iy * B) / A
        # wy = (wx - iy * B) * C / A + iy * D
        # wy = wx * C - iy * BC/A + iy * D
        # wy - wx * C = iy * ( D - BC/A)
        # iy = (wy - wx * C) / (D - BC/A)

        A = self.bases[0].x
        B = self.bases[1].x
        C = self.bases[0].y
        D = self.bases[1].y

        if (abs(C) < 0.001):
            return self.c0snapper(wx, wy)

        if ((abs(A) > 0.001) and (abs(D-B*C/A) > 0.001)):
            iy = (wy - wx * C) / (D - B*C/A)
            ix = (wx - iy * B) / A
        else:
            assert(False)
        return ix, iy
        
    def snapWorldToIndices(self, wx, wy):
        ix, iy = self.invertMatrix(wx, wy)

        iy = int(round(iy))
        ix = int(round(ix))

        return ix, iy
            
    def c0snapper(self, wx, wy):
        A = self.bases[0].x
        B = self.bases[1].x
        D = self.bases[1].y
        
        iy = wy / D
        ix = (wx - iy * B) / A
        
        return ix, iy

    def snappedPairsMatch(self, pair1, pair2):
        return pair1 == pair2

    def getSnapToInts(self):
        return True

class CartesianGrid(Grid):
    def snapWorldToIndices(self, wx, wy):
        ix, iy = self.invertMatrix(wx, wy)
        return ix, iy

    def snappedPairsMatch(self, pair1, pair2):
        v1 = bdggeom.Vec2f(*pair1)
        v2 = bdggeom.Vec2f(*pair2)
        d = (v2 - v1).magnitude()
        return d < self.unit * 0.1

    def getSnapToInts(self):
        return False

def makeTriangularGrid(width):
    g = Grid(width)
    g.bases[1] = bdggeom.Vec2f(0.5 * g.unit,
                               math.sin(math.pi / 3) * g.unit)
    return g

def makeSquareGrid(width):
    g = Grid(width)
    return g

def makeHexGrid(width):
    pass

def makeCartesianGrid(width):
    g = CartesianGrid(width)
    return g
