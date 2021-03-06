import math, random, sets, util, collections, itertools
# random.seed(2011)
import namegen
from primitives import *
from territory import *
from types import *
from country import Country

hash_colors = [
    (1.0, 0.0, 0.0, 1.0), (1.0, 0.5, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), 
    (0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 1.0), (0.7, 0.0, 1.0, 1.0), 
    (1.0, 0.5, 1.0, 1.0), (0.7, 0.3, 0.0, 1.0)
]
random.shuffle(hash_colors)
colorer = itertools.cycle(hash_colors)

class FractalGenerator(object):
    def __init__(self, num_lines):
        super(FractalGenerator, self).__init__()
        self.wiggle = math.pi/6
        self.num_lines = num_lines
        self.check_collisions = True
        self.offset = (0,0)
        self.width, self.height = 0, 0
    
    def generate(self):
        self.lm = Map(set(), set(), set(), set())
        
        self.generate_initial_polygon()
        self.generate_iteratively()
        self.connect()
        
        return self.lm
    
    def generate_iteratively(self):
        while self.num_lines > 0:
            outside_list = list(self.lm.outside_lines)
            base_line = random.choice(outside_list)
            if not base_line.favored:
                base_line = random.choice(outside_list)
            if self.check_concave(base_line):
                if self.check_concave(base_line.left):
                    self.expand_line(base_line)
    
    def generate_initial_polygon(self):
        a = 0
        r = self.random_length()
        first_point = Point(r, 0)
        last_point = first_point
        line_num = 0
        triangles = []
        last_line = None
        first_line = None
        while a < math.pi*2-math.pi/5:
            a += random.random()*math.pi*(0.666-0.2)+math.pi/5
            if a < math.pi*2-math.pi/5:
                r = self.random_length()
                new_point = Point(r*math.cos(a), r*math.sin(a))
                self.num_lines -= 1
            else:
                new_point = first_point
            new_line = self.make_line(last_point, new_point)
            if line_num > 0:
                last_line.right = new_line
                new_line.left = last_line
                last_line = new_line
            else:
                first_line = new_line
                last_line = new_line
            self.lm.lines.add(new_line)
            self.lm.outside_lines.add(new_line)
            triangles.append(
                (0, 0, last_point.x, last_point.y, new_point.x, new_point.y)
            )
            last_point = new_point
            line_num += 1
        last_line.right = first_line
        first_line.left = last_line
        self.lm.land_terrs = set()
        self.add_terr(triangles, self.lm.lines, (1,0,0,1))
    
    def make_line(self, *args, **kwargs):
        l = Line(*args, **kwargs)
        for k in self.lm.hashes_for_pair(l.a, l.b):
            self.lm.outer_line_hash[k].add(l)
        return l
    
    def remove_line_from_outside(self, line):
        self.lm.outside_lines.remove(line)
        for k in self.lm.hashes_for_pair(line.a, line.b):
            try:
                self.lm.outer_line_hash[k].remove(line)
            except KeyError:
                pass
    
    def add_terr(self, triangles, lines, color=(0.5, 0.5, 0.5, 1)):
        new_terr = LandTerr(lines, color=color)
        new_terr.triangles = triangles
        self.lm.land_terrs.add(new_terr)
        return new_terr
    
    def random_length(self):
        return random.random()*self.lm.base_distance*0.3 + self.lm.base_distance*0.7
    
    def check_intersections(self, a, b):
        if not self.check_collisions: return True
        for line in self.lm.outside_lines_colliding_with(a, b):
            if util.intersect(a, b, line.a, line.b):
                return False
        return True
    
    def check_point(self, point):
        if not self.check_collisions: return True
        for territory in self.lm.land_terrs:
            for tri in territory.triangles:
                if util.point_inside_triangle(point.x, point.y, tri):
                    return False
        return True
    
    def check_concave(self, line):
        if line.a == line.right.b:
            self.remove_floating_lines()
            if self.verbose: print 'weird line error'
            return False
        if not self.check_intersections(line.a, line.right.b): return False
        if util.angle_between_line_and_next(line) > math.pi*0.75 \
            or line.length + line.right.length > self.lm.base_distance*3.5:
            return True
        new_line = self.make_line(line.a, line.right.b, line.left, line.right.right)
        line.left.right = new_line
        line.right.right.left = new_line
        self.lm.lines.add(new_line)
        self.lm.outside_lines.add(new_line)
        self.remove_line_from_outside(line)
        self.remove_line_from_outside(line.right)
        self.num_lines -= 1
        self.add_terr([(line.a.x, line.a.y, 
                        line.b.x, line.b.y, 
                        line.right.b.x, line.right.b.y)], 
                      [line, line.right, new_line],
                      (0,1,0,1))
        return False
    
    def make_new_tri(self, base_line, new_point):
        nl1 = self.make_line(base_line.a, new_point, base_line.left)
        nl2 = self.make_line(new_point, base_line.b, nl1, base_line.right)
        nl1.right = nl2
        base_line.left.right = nl1
        base_line.right.left = nl2
        self.remove_line_from_outside(base_line)
        self.lm.outside_lines.add(nl1)
        self.lm.outside_lines.add(nl2)
        self.lm.lines.add(nl1)
        self.lm.lines.add(nl2)
        self.num_lines -= 2
        self.add_terr([(base_line.a.x, base_line.a.y, 
                        base_line.b.x, base_line.b.y, 
                        new_point.x, new_point.y)],
                      [nl1, nl2, base_line],
                      (0, 0, 1, 1))
        return nl1, nl2
    
    def expand_to_triangle(self, base_line):
        r = self.random_length()
        a = base_line.normal + random.random()*self.wiggle-self.wiggle/2
        nx = r*math.cos(a)
        ny = r*math.sin(a)
        new_point = Point(
            base_line.midpoint.x+nx,
            base_line.midpoint.y+ny
        )
        test_point = Point(
            base_line.midpoint.x+nx*2, 
            base_line.midpoint.y+ny*2
        )
        if not self.check_intersections(base_line.a, test_point): return
        if not self.check_intersections(test_point, base_line.b): return
        
        self.make_new_tri(base_line, new_point)
    
    def expand_to_trapezoid(self, line):
        r = self.random_length()
        l = line.length * 0.8 + random.random()*0.4
        l = max(l, 10)
        nx = r*math.cos(line.normal)
        ny = r*math.sin(line.normal)
        mx = line.midpoint.x + nx
        my = line.midpoint.y + ny
        mxb = line.midpoint.x + nx*2
        myb = line.midpoint.y + ny*2
        ax = l*0.5*math.cos(line.normal+math.pi/2)
        ay = l*0.5*math.sin(line.normal+math.pi/2)
        p1 = Point(mx - ax, my - ay)
        p2 = Point(mx + ax, my + ay)
        p1b = Point(mxb - ax*1.25, myb - ay*1.25)
        p2b = Point(mxb + ax*1.25, myb + ay*1.25)
        
        if not self.check_intersections(line.a, p1): return
        if not self.check_intersections(line.b, p2): return
        if not self.check_intersections(p1, p2): return
        
        nl1, nl2 = self.make_new_tri(line, p1)
        nl3, nl4 = self.make_new_tri(nl2, p2)
        nl3.favored = True
    
    def expand_line(self, base_line):
        expand_dict = {
            0: self.expand_to_triangle,
            1: self.expand_to_trapezoid,
            2: self.expand_to_trapezoid
        }
        expand_dict[random.randint(0,len(expand_dict)-1)](base_line)
    
    def connect(self):
        for line in self.lm.outside_lines:
            for adj in line.territories:
                adj.is_coastal = True
        
        for terr in self.lm.land_terrs:
            terr.find_adjacencies()
    
