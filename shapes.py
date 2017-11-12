import math

import bdggeom

##
## Triangular spiral S
##
## X goes right
## Y goes 60 degrees from right, northeast

class RotTransformationDesc:
    def __init__(self, rotCount, rotCenterIndices):
        self.rotCount = rotCount
        self.rotCenterIndices = rotCenterIndices

    def makeMatrix(self, grid):
        # first apply a negative translation by the rotCenter
        # then apply the rotation
        # then reverse the rotCenter
        centerVec = bdggeom.Vec2f(*grid.indexToWorld(*self.rotCenterIndices))
        rotRad = 2 * math.pi / self.rotCount
        negTrans = bdggeom.makeTranslationMatrix(-centerVec.x, -centerVec.y)
        posTrans = bdggeom.makeTranslationMatrix(centerVec.x, centerVec.y)
        rotTrans = bdggeom.makeRotationMatrix(rotRad)
        return posTrans.mulMat(rotTrans.mulMat(negTrans))

    def makeInverseMatrix(self, grid):
        # first apply a negative translation by the rotCenter
        # then apply the rotation
        # then reverse the rotCenter
        centerVec = bdggeom.Vec2f(*grid.indexToWorld(*self.rotCenterIndices))
        rotRad = 2 * math.pi / self.rotCount
        negTrans = bdggeom.makeTranslationMatrix(-centerVec.x, -centerVec.y)
        posTrans = bdggeom.makeTranslationMatrix(centerVec.x, centerVec.y)
        rotTrans = bdggeom.makeRotationMatrix(-rotRad)
        return posTrans.mulMat(rotTrans.mulMat(negTrans))
    

class TransTransformationDesc:
    def __init__(self, offset):
        self.offset = offset

    def makeMatrix(self, grid):
        offsetVec = bdggeom.Vec2f(*grid.indexToWorld(*self.offset))
        return bdggeom.makeTranslationMatrix(offsetVec.x, offsetVec.y)

    def makeInverseMatrix(self, grid):
        offsetVec = bdggeom.Vec2f(*grid.indexToWorld(*self.offset))
        return bdggeom.makeTranslationMatrix(-offsetVec.x, -offsetVec.y)
    

# takes rotCount, an integer period
# takes rotCenter, grid indices of the center
def makeRotationDesc(rotCount, rotCenterIndices):
    return RotTransformationDesc(rotCount, rotCenterIndices)

# takes offset, grid indices of the translation
def makeTranslationDesc(offset):
    return TransTransformationDesc(offset)

triSpiralS_points = [(0, 0),
                     (-1, 1),
                     (-1, 2),
                     (1, 2),
                     (4, -1),
                     (7, -1),
                     (7, 2),
                     (4, 5),
                     (2, 5),
                     (2, 3),
                     (4, 1),
                     (5, 1),
                     (5, 2),
                     (4, 3), # top of 2-spiral, ready to come back
                     (4, 2),
                     (3, 3),
                     (3, 4),
                     (4, 4),
                     (6, 2),
                     (6, 0),
                     (4, 0),
                     (1, 3),
                     (-2, 3),
                     (-2, 1),
                     (-1, 0)]
triSpiralS_transformations = [makeRotationDesc(6, (0, 0)),
                              makeRotationDesc(3, (7, -1)),
                              makeRotationDesc(2, (4, 2.5))]

pentoT_points = [(0, 0),
                 (7, 0),
                 (7, 3),
                 (5, 3),
                 (5, 2),
                 (6, 2),
                 (6, 1),
                 (4, 1),
                 (4, 4),
                 (4, 7),
                 (6, 7),
                 (6, 6),
                 (5, 6),
                 (5, 5),
                 (7, 5),
                 (7, 8), # far corner, let's come back
                 (0, 8),
                 (0, 5),
                 (2, 5),
                 (2, 6),
                 (1, 6),
                 (1, 7),
                 (3, 7),
                 (3, 4),
                 (3, 1),
                 (1, 1),
                 (1, 2),
                 (2, 2),
                 (2, 3),
                 (0, 3)]
pentoT_transformations = [makeTranslationDesc((0, 8)),
                          makeTranslationDesc((4, 4))]
                 



