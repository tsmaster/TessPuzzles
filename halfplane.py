import bdggeom


"""
A halfplane is half a plane, defined by a point on the edge of the
halfplane and a vector pointing toward the interior from that point.
"""

class HalfPlane:
    def __init__(self, point, interiorVec):
        self.point = point
        self.interiorVec = interiorVec

    def characterizePoint(self, otherPoint):
        """
        Determine if the other point is inside, on the boundary, or
        outside the halfplane. This is done by subtracting the new
        (other) point from the halfplane's reference point, then doing
        a dot product with the interiorVec.
        This results in:
          > 0 : inside
          = 0 : on border
          < 0 : outside
        """
        deltaVec = otherPoint - self.point
        return self.interiorVec.dot(deltaVec)

    def areAllPointsOnBorderOrInside(self, listOfVectors):
        for v in listOfVectors:
            c = self.characterizePoint(v)
            if c < 0:
                return False
        return True

    def areAnyPointsOutside(self, listOfVectors):
        return not self.areAllPointsOnBorderOrInside(listOfVectors)

    def areAnyPointsInside(self, listOfVectors):
        for v in listOfVectors:
            c = self.characterizePoint(v)
            if c >= 0:
                return True
        return False

    def areAllPointsOutside(self, listOfVectors):
        return not self.areAnyPointsInside(listOfVectors)

    def areAllPointsInside(self, listOfVectors):
        for v in listOfVectors:
            c = self.characterizePoint(v)
            if c < 0:
                return False
        return True
        
