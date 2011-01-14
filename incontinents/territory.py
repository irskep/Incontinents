import util, random, itertools

PICK_TRIANGLE = 0
AVERAGE_POINTS = 1
LARGEST_TRIANGLE = 2

class Territory(object):
    def __init__(self):
        super(Territory, self).__init__()
        self.country = None
        self.adjacencies = []
        self.lines = []
        self.is_coastal = False
        self.has_supply_center = False
        self.occupied = False
        self.x, self.y = 0.0, 0.0
        self.name = ""
        self.abbreviation = ""
        self.ter_id = 0
        self.is_sea = False
        self.pc_x, self.pc_y = 0, 0
        self.triangles = []
    

class SeaTerr(Territory):
    def __init__(self, line=None):
        super(SeaTerr, self).__init__()
        self.line = line
        self.size = 0
        self.is_sea = True
        if line != None:
            self.lines.append(line)
            self.x = (line.a.x + line.b.x) / 2
            self.y = (line.a.y + line.b.y) / 2
            self.pc_x = self.x
            self.pc_y = self.y - 10
        else:    
            self.x, self.y = 0, 0
            self.pc_x, self.pc_y = 0, 0
    

class LandTerr(Territory):
    def __init__(self, lines=[], color=(0.5,0.5,0.5,1)):
        super(LandTerr, self).__init__()
        for line in lines:
            self.add_line(line)
        self.color = color
        self.adjacent_countries = []
        self.combinations = 0
        self.offset = (0,0)
        self._min_x, self._min_y, self._max_x, self._max_y = None, None, None, None
    
    def add_line(self, line):
        if line not in self.lines:
            self.lines.append(line)
            line.territories.append(self)
    
    def remove_line(self, line):
        self.lines.remove(line)
        line.territories.remove(self)
    
    def add_triangle(self, x1, y1, x2, y2, x3, y3):
        self.triangles.append((x1, y1, x2, y2, x3, y3))
    
    def find_adjacencies(self): 
        self.adjacent_countries = []
        self.adjacencies = []
        for line in self.lines:
            for terr in line.territories:
                if terr != self and terr not in self.adjacencies:
                    self.adjacencies.append(terr)
        for terr in self.adjacencies:
            if terr.country not in self.adjacent_countries:
                if terr.country != None:
                    self.adjacent_countries.append(terr.country)
    
    def _find_bounding_box(self):
        xs = lambda: itertools.chain(*((line.a.x, line.b.x) for line in self.lines))
        ys = lambda: itertools.chain(*((line.a.y, line.b.y) for line in self.lines))
        process = lambda f, l: int(reduce(f, l, 0))
        self._min_x, self._max_x = process(min, xs()), process(max, xs())
        self._min_y, self._max_y = process(min, ys()), process(max, ys())
    
    def _get_min_x(self):
        if self._min_x is None: self._find_bounding_box()
        return self._min_x
    
    def _get_min_y(self):
        if self._min_y is None: self._find_bounding_box()
        return self._min_y
    
    def _get_max_x(self):
        if self._max_x is None: self._find_bounding_box()
        return self._max_x
    
    def _get_max_y(self):
        if self._max_y is None: self._find_bounding_box()
        return self._max_y
    
    min_x = property(_get_min_x)
    min_y = property(_get_min_y)
    max_x = property(_get_max_x)
    max_y = property(_get_max_y)
    
    def check_point(self, x, y, x_dist=12, y_dist=5):
        for p in  ((x, y),):#, (x+x_dist, y+y_dist), (x-x_dist, y+y_dist),
                          #(x+x_dist, y-y_dist), (x-x_dist, y+y_dist)):
            if not self.point_inside(*p): return False
        return True
    
    def place_piece(self):
        self.pc_x = self.x
        self.pc_y = self.y-10
        if not self.point_inside(self.pc_x, self.pc_y-10):
            self.pc_x, self.pc_y = self.x+20, self.y
        if not self.point_inside(self.pc_x+10, self.pc_y):
            self.pc_x, self.pc_y = self.x, self.y+10
        if not self.point_inside(self.pc_x, self.pc_y+10):
            self.pc_x, self.pc_y = self.x-20, self.y
        if not self.point_inside(self.pc_x-10, self.pc_y):
            self.pc_x, self.pc_y = self.find_empty_space()
            if self.pc_x == 0 and self.pc_y == 0:
                self.pc_x, self.pc_y = self.x, self.y-10
    
    def check_avoid(self, x, y, avoid_x, avoid_y):
        if avoid_x == 0 and avoid_y == 0: return True
        return (x-avoid_x)*(x-avoid_x)+(y-avoid_y)*(y-avoid_y) >= 20*20
    
    def find_empty_space(self, avoid_x=0, avoid_y=0):
        x = random.randint(self.min_x, self.max_x)
        y = random.randint(self.min_y, self.max_y)
        i = 0
        while not self.check_point(x, y) and i < 200 and self.check_avoid(x, y, avoid_x, avoid_y):
            x = random.randint(self.min_x, self.max_x)
            y = random.randint(self.min_y, self.max_y)
            i += 1
        if i == 200:
            return 0, 0
        else:
            return x, y
    
    def place_text(self):
        self.x, self.y = self.find_empty_space()
        if self.x == 0 and self.y == 0:
            if not self.place_text_using_point_average():
                self.place_text_in_largest_triangle()
        self.place_piece()
    
    def place_text_using_point_average(self):
        points = {line.a.tuple for line in self.lines} | {line.b.tuple for line in self.lines}
        self.x = reduce(lambda a, b: a+b[0], points, 0.0)/len(points)
        self.y = reduce(lambda a, b: a+b[1], points, 0.0)/len(points)
        
        check_pairs = ((self.x, self.y), (self.x+15, self.y), (self.x+15, self.y),
                       (self.x, self.y+15), (self.x, self.y-15))
        
        return reduce(lambda a, b: a and self.point_inside(*b), check_pairs, True)
    
    def place_text_in_largest_triangle(self):
        chosen_tri = 0
        max_area = 0
        for i in range(1, len(self.triangles)):
            a = util.area_of_triangle(self.triangles[i])
            if a > max_area:
                max_area = a
                chosen_tri = i
        tri = self.triangles[chosen_tri]
        self.x = tri[0] + tri[2] + tri[4]
        self.y = tri[1] + tri[3] + tri[5]
        self.x /= 3.0
        self.y /= 3.0
    
    def color_self(self):
        darken_amt = (1.0-random.random()*0.15)
        col = self.country.color if self.country != None \
                                    and (self.has_supply_center or self.occupied) \
              else (1.0, 1.0, 1.0, 1.0)
        self.color = (col[0]*darken_amt, col[1]*darken_amt, col[2]*darken_amt, 1.0)
        self.color = self.country.color if self.color == (0.0, 0.0, 0.0, 1.0) else self.color
    
    def point_inside(self, x, y):
        """Returns True if (x,y) is inside the territory."""
        for tri in self.triangles:
            if util.point_inside_triangle(x, y, tri):
                return True
        return False
    
    def __repr__(self):
        return str(self.ter_id)
    
