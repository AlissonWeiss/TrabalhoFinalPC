import math


class Point():

    def __init__(self, _x=None, _y=None):
        self.x = _x
        self.y = _y
        self.selected = False
        self.vertex = None
        self.attributes = []

        self.x_fixed = False
        self.y_fixed = False
        self.x_force = float(0)
        self.y_force = float(0)
        self.temperature = None

    def setX(self, _x):
        self.x = _x

    def setY(self, _y):
        self.y = _y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setCoords(self, _x, _y):
        self.x = _x
        self.y = _y

    def setSelected(self, _select):
        self.selected = _select

    def isSelected(self):
        return self.selected

    def setFixedX(self, _fixed):
        self.x_fixed = _fixed

    def setFixedY(self, _fixed):
        self.y_fixed = _fixed

    def isFixedX(self):
        return self.x_fixed

    def isFixedY(self):
        return self.y_fixed

    def setXForce(self, _force: float):
        self.x_force = _force

    def getXForce(self):
        return self.x_force

    def setYForce(self, _force: float):
        self.y_force = _force

    def getYForce(self):
        return self.y_force

    def setTemperature(self, _temperature):
        self.temperature = _temperature

    def getTemperature(self):
        return self.temperature

    # Equality test with tolerance (Manhattan distance)
    @staticmethod
    def equal(p1, p2, tol):
        return abs(p1.x - p2.x) < tol.x and abs(p1.y-p2.y) < tol.y

    # Equality test without tolerance
    def __eq__(p1, p2):
        return (p1.x == p2.x) and (p1.y == p2.y)

    # operator <
    def __lt__(p1, p2):
        if p1.x == p2.x:
            return p1.y < p2.y
        else:
            return p1.x < p2.x

    # # operator >
    def __gt__(p1, p2):
        if p1.x == p2.x:
            return p1.y > p2.y
        else:
            return p1.x > p2.x

    # Inequality test without tolerance
    def __ne__(p1, p2):
        return not (p1 == p2)

    # Addition +
    def __add__(p1, p2):
        return Point(p1.x+p2.x, p1.y+p2.y)

    # Addition +=
    def __iadd__(p1, p2):
        p1 = p1+p2
        return p1

    # Subtraction -
    def __sub__(p1, p2):
        return Point(p1.x-p2.x, p1.y-p2.y)

    # Subtraction -=
    def __isub__(p1, p2):
        p1 = p1-p2
        return p1

    # Scalar multiplication
    def __mul__(p, s):
        return Point(p.x*s, p.y*s)

    # Division by scalar
    def __truediv__(p, s):
        if s == 0:
            return Point(0.0, 0.0)
        return Point(p.x/s, p.y/s)

    # Euclidian distance
    @staticmethod
    def euclidiandistance(p1, p2):
        return math.sqrt((p1.x-p2.x)*(p1.x-p2.x) +
                         (p1.y-p2.y)*(p1.y-p2.y))

    # Manhattan distance
    @staticmethod
    def manhattandistance(p1, p2):
        return abs(p1.x-p2.x) + abs(p1.y-p2.y)

    # Square of size (vector)
    @staticmethod
    def sizesquare(p):
        return (p.x*p.x + p.y*p.y)

    # Size (vector)
    @staticmethod
    def size(p):
        return math.sqrt(Point.sizesquare(p))

    # Dot product (vector)
    @staticmethod
    def dotprod(p1, p2):
        return p1.x*p2.x + p1.y*p2.y

    # Cross product (vector)
    @staticmethod
    def crossprod(p1, p2):
        return p1.x*p2.y - p2.x*p1.y

    # Normalize (vector)
    @staticmethod
    def normalize(p):
        norm = Point.size(p)
        if norm == 0:
            return Point(0.0, 0.0)
        return Point(p.x/norm, p.y/norm)

    # Twice the signed area of triangle p1-p2-p3
    @staticmethod
    def area2d(p1, p2, p3):
        ptA = p2 - p1
        ptB = p3 - p1
        return Point.crossprod(ptA, ptB)
