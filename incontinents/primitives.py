import math

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
    
    tuple = property(lambda self: (self.x, self.y))
    
    def __hash__(self): return self.tuple.__hash__()
    
    def __eq__(self, b):
        t = (self.x, self.y)
        try:
            return t == b.tuple
        except:
            return t == b
    
    def __ne__(self, b):
        return not self.__eq__(b)
    
    def __sub__(self, b):
        return Point(self.x - b.x, self.y - b.y)
    
    def __repr__(self):
        return str(self.tuple)
    
    def __str__(self):
        return str(self.tuple)
    

class Line(object):
    def __init__(self, a, b, left=None, right=None, color=(0,0,0,1)):
        self.a = a
        self.b = b
        self.left = left    #line connecting to self.a
        self.right = right  #line connecting to self.b
        self.normal = math.atan2(b.y-a.y, b.x-a.x) - math.pi/2
        self.midpoint = Point((a.x+b.x)/2, (a.y+b.y)/2)
        self.outside = True #line is on outside of shape
        self.color = color
        self.territories = []
        self.id = 0
        self._length = 0     #calculated when requested
        self.favored = False
    
    def _get_length(self):
        if self._length == 0:
            self._length = math.sqrt(
                (self.a.x-self.b.x)*(self.a.x-self.b.x) + (self.a.y-self.b.y)*(self.a.y-self.b.y)
            )
        return self._length
    
    length = property(_get_length)

    def __hash__(self): 
        t = (self.a.tuple, self.b.tuple)
        return t.__hash__()

    def __eq__(self, x):
        if not x: return False
        return self.a == x.a and self.b == x.b
    
    def __ne__(self, b):
        return not self.__eq__(b)
    
    def __repr__(self):
        return "Line((%r, %r), (%r, %r))" % (
            self.a.x, self.a.y, self.b.x, self.b.y
        )

class Triangle(object):
    
    def __init__(self, p1, p2, p3, mid=None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.mid = mid
        self.adj = list()
        self.__hash = None
        self.lines = (Line(p1, p2), Line(p2, p3), Line(p3, p1))
    
    def area(self):
        def length(a, b):
            return ((a.x - b.x)**2 + (a.y - b.y)**2)**.5
        m = Point((self.p2.x + self.p3.x)/2.0, (self.p2.y + self.p3.y)/2.0)
        b = length(self.p2, self.p3)
        h = length(m, self.p1)
        return .5*(b)*(h)
    
    def dist_2(self, b):
        return ((self.mid.x - b.mid.x)**2 + (self.mid.y - b.mid.y)**2)
    
    def _get_tuple(self):
        return (self.p1.tuple, self.p2.tuple, self.p3.tuple)
    
    tuple = property(_get_tuple)

    def __hash__(self): 
        if self.__hash: return self.__hash
        return self.tuple.__hash__()

    def __eq__(self, b):
        if type(b) == type(tuple()): return self.tuple == b
        return self.p1 == b.p1 and self.p2 == b.p2 and self.p3 == b.p3
    
    def __ne__(self, b):
        return not self.__eq__(b)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return '(' + str(self.p1) + ', ' + str(self.p2) + ', ' + str(self.p3) + ')'
    
