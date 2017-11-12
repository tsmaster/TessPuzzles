#
# Big Dice Games' geometry code
#

import math

class Vec2f:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "[{0} {1}]".format(self.x, self.y)

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return Vec2f(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2f(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2f(self.x * scalar, self.y * scalar)

    def __cmp__(self, other):
        if isinstance(other, Vec2f):
            if self.x < other.x:
                return -1
            if self.x > other.x:
                return 1
            if self.y < other.y:
                return -1
            if self.y > other.y:
                return 1
            return 0
        return NotImplemented

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

class Mat2f:
    """ Really a 3 element wide by 2 element high matrix. Good for translating 
        and rotating vectors. """
    def __init__(self, a, b, c, d, e, f):
        self.elements = [[a, b, c],
                         [d, e, f]]

    def __mul__(self, s):
        a, b, c = self.elements[0]
        d, e, f = self.elements[1]
        
        return Mat2f(a*s, b*s, c*s,
                     d*s, e*s, f*s)

    def __str__(self):
        a, b, c = self.elements[0]
        d, e, f = self.elements[1]
        
        s = "[{0} {1} {2}]\n".format(a,b,c)
        s += "[{0} {1} {2}]".format(d, e, f)
        return s

    def mulMat(self, otherMat):
        """
        S*O
        """
        sa, sb, sc = self.elements[0]
        sd, se, sf = self.elements[1]

        oa, ob, oc = otherMat.elements[0]
        od, oe, of = otherMat.elements[1]

        ra = sa * oa + sb * od
        rb = sa * ob + sb * oe
        rc = sa * oc + sb * of + sc
        rd = sd * oa + se * od
        re = sd * ob + se * oe
        rf = sd * oc + se * of + sf

        return Mat2f(ra, rb, rc,
                     rd, re, rf)

    def mulVec(self, vec):
        """
        S*V
        """
        
        sa, sb, sc = self.elements[0]
        sd, se, sf = self.elements[1]

        rx = sa * vec.x + sb * vec.y + sc
        ry = sd * vec.x + se * vec.y + sf

        return Vec2f(rx, ry)

def makeIdentityMatrix():
    return Mat2f(1.0, 0.0, 0.0,
                 0.0, 1.0, 0.0)

def makeScaleMatrix(s):
    return Mat2f(s, 0, 0,
                 0, s, 0)

def makeTranslationMatrix(tx, ty):
    return Mat2f(1.0, 0.0, tx,
                 0.0, 1.0, ty)

def makeRotationMatrix(theta):
    c = math.cos(theta)
    s = math.sin(theta)

    return Mat2f(c, s, 0.0,
                 -s, c, 0.0)


def testMat():
    zeroVec = Vec2f(0, 0)
    print zeroVec

    translateXMat = makeTranslationMatrix(1,0)

    translatedXVec = translateXMat.mulVec(zeroVec)

    print translatedXVec

    translateYMat = makeTranslationMatrix(0, 1)
    
    translatedYVec = translateYMat.mulVec(zeroVec)

    print translatedYVec

if __name__ == '__main__':
    testMat()
