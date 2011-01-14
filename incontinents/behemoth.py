import math, random, sets, util
# random.seed(2011)
import namegen
from primitives import *
from territory import *
from types import *
from country import Country

grey_colors = []
c = 0.6
while c < 0.8:
    grey_colors.append((c,c,c,1))
    c += 0.15

class ContinentGenerator(Generator):
    def __init__(self, num_countries=7, namer=None, verbose=False):
        super(ContinentGenerator, self).__init__(num_countries)
        self.namer = namer or namegen.Namer()
        self.balance_countries = True
        self.verbose = verbose
        self.wiggle = math.pi/6
        self.base_distance = 35.0
        self.num_lines = 128*num_countries
        self.check_collisions = True
        self.offset = (0,0)
        self.width, self.height = 0, 0
    
    def generate(self):
        if self.num_lines <= 0:
            self.num_lines = 900
        self.lines = set()
        self.outside_lines = set()
        self.land_terrs = set()
        self.sea_terrs = set()
        self.which_color = 0
        
        if self.verbose: print "generating..."
        self.generate_initial_polygon()
        self.generate_iteratively()
        self.connect()
        self.make_seas()
        
        if self.verbose: print "done"
        return self.get_landmass()
    
    def get_landmass(self):
        lm = Map(self.lines, self.outside_lines, self.land_terrs, self.sea_terrs)
        lm.name, lm.abbreviation = self.namer.create('land')
        lm.find_bounds()
        for territory in lm.land_terrs:
            territory.place_text()
        return lm
    
    def generate_iteratively(self):
        while self.num_lines > 0:
            outside_list = list(self.outside_lines)
            base_line = random.choice(outside_list)
            if not base_line.favored:
                base_line = random.choice(outside_list)
            if self.check_concave(base_line):
                if self.check_concave(base_line.left):
                    self.expand_line(base_line)
    
    def generate_initial_polygon(self):
        a = 0
        r = self.get_radius()
        first_point = Point(r, 0)
        last_point = first_point
        line_num = 0
        triangles = []
        last_line = None
        first_line = None
        while a < math.pi*2-math.pi/5:
            a += random.random()*math.pi*(0.666-0.2)+math.pi/5
            if a < math.pi*2-math.pi/5:
                r = self.get_radius()
                new_point = Point(r*math.cos(a), r*math.sin(a))
                self.num_lines -= 1
            else:
                new_point = first_point
            new_line = Line(last_point, new_point)
            if line_num > 0:
                last_line.right = new_line
                new_line.left = last_line
                last_line = new_line
            else:
                first_line = new_line
                last_line = new_line
            self.lines.add(new_line)
            self.outside_lines.add(new_line)
            triangles.append(
                (0, 0, last_point.x, last_point.y, new_point.x, new_point.y)
            )
            last_point = new_point
            line_num += 1
        last_line.right = first_line
        first_line.left = last_line
        self.land_terrs = set()
        new_terr = LandTerr(self.lines, self.get_color(0))
        new_terr.triangles = triangles
        self.land_terrs.add(new_terr)
    
    def get_radius(self):
        return random.random()*self.base_distance*0.3 + self.base_distance*0.7
    
    def get_color(self, n=-1):
        if n == -1: n = self.which_color
        n = n % len(grey_colors)
        c = grey_colors[n]
        self.which_color += 1
        return c
    
    def angle_between_line_and_next(self, line):    
        a1 = math.atan2(line.right.b.y-line.b.y, line.right.b.x-line.b.x)
        a2 = math.atan2(line.a.y-line.b.y, line.a.x-line.b.x)
        return (a1 - a2) % (math.pi*2)
    
    def check_intersections(self, a, b):
        if not self.check_collisions: return True
        for line in self.outside_lines:
            if util.intersect(a, b, line.a, line.b):
                return False
        return True
    
    def check_point(self, point):
        if not self.check_collisions: return True
        for territory in self.land_terrs:
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
        if self.angle_between_line_and_next(line) > math.pi*0.75: return True
        new_line = Line(line.a, line.right.b, line.left, line.right.right)
        #if not self.check_point(new_line.midpoint): return False
        line.left.right = new_line
        line.right.right.left = new_line
        self.lines.add(new_line)
        self.outside_lines.add(new_line)
        self.outside_lines.remove(line)
        self.outside_lines.remove(line.right)
        self.num_lines -= 1
        
        rn = random.randint(0, 100)
        can_expand = True
        can_expand = False
        for s in line.territories:
            if len(s.lines) > 8: can_expand = False
        if rn >= 50 and can_expand:
            self.lines.remove(line)
            for s in line.territories:
                s.remove_line(line)
                s.add_line(new_line)
                s.add_line(line.right)
                s.add_triangle(
                    line.a.x, line.a.y, line.b.x, line.b.y, 
                    line.right.b.x, line.right.b.y
                )
        else:
            rn = random.randint(0, 100)
            can_expand = True
            for s in line.right.territories:
                if len(s.lines) > 8: can_expand = False
            if rn >= 50 and can_expand:
                self.lines.remove(line.right)
                for s in line.right.territories:
                    s.remove_line(line.right)
                    s.add_line(new_line)
                    s.add_line(line)
                    s.add_triangle(
                        line.a.x, line.a.y, line.b.x, line.b.y, 
                        line.right.b.x, line.right.b.y
                    )
            else:
                new_territory = LandTerr(
                    [line, line.right, new_line], self.get_color()
                )
                new_territory.dist = line.territories[0].dist
                new_territory.dist += line.right.territories[0].dist
                new_territory.dist = int(new_territory.dist/2) + 1
                new_territory.color = self.get_color(new_territory.dist)
                self.land_terrs.add(new_territory)
                new_territory.add_triangle(
                    line.a.x, line.a.y, line.b.x, line.b.y, 
                    line.right.b.x, line.right.b.y
                )
        return False
    
    def make_new_tri(self, base_line, new_point, erase_old=False):
        nl1 = Line(base_line.a, new_point, base_line.left)
        nl2 = Line(new_point, base_line.b, nl1, base_line.right)
        nl1.right = nl2
        base_line.left.right = nl1
        base_line.right.left = nl2
        self.outside_lines.remove(base_line)
        self.outside_lines.add(nl1)
        self.outside_lines.add(nl2)
        self.lines.add(nl1)
        self.lines.add(nl2)
        self.num_lines -= 2
        
        if erase_old:
            self.lines.remove(base_line)
            for s in base_line.territories:
                s.remove_line(base_line)
                s.add_line(nl1)
                s.add_line(nl2)
                s.add_triangle(
                    base_line.a.x, base_line.a.y, base_line.b.x, base_line.b.y, 
                    new_point.x, new_point.y
                )
        else:
            new_territory = LandTerr([nl1, nl2, base_line], self.get_color())
            self.land_terrs.add(new_territory)
            new_territory.add_triangle(
                base_line.a.x, base_line.a.y, base_line.b.x, base_line.b.y, 
                new_point.x, new_point.y
            )
            new_territory.dist = base_line.territories[0].dist+1
            new_territory.color = self.get_color(new_territory.dist)
        return nl1, nl2
    
    def expand_to_triangle(self, base_line):
        r = self.get_radius()
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
        
        rn = random.randint(0, 100)
        can_expand = True
        can_expand = False
        for s in base_line.territories:
            if len(s.lines) > 8: can_expand = False
        
        self.make_new_tri(base_line, new_point, (rn >= 50 and can_expand))
    
    def expand_to_trapezoid(self, line):
        r = self.get_radius()
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
        
        nl1, nl2 = self.make_new_tri(line, p1, False)
        nl3, nl4 = self.make_new_tri(nl2, p2, True)
        nl3.favored = True
    
    def expand_line(self, base_line):
        expand_dict = {
            0: self.expand_to_triangle,
            1: self.expand_to_trapezoid,
            2: self.expand_to_trapezoid
        }
        expand_dict[random.randint(0,len(expand_dict)-1)](base_line)
    
    def connect(self):
        for line in self.outside_lines:
            for adj in line.territories:
                adj.is_coastal = True
        
        if self.verbose: print "generating adjacencies..."
        for terr in self.land_terrs:
            terr.find_adjacencies()
    
    def territory_is_outside(self, terr):
        for line in terr.lines:
            if line in self.outside_lines:
                return True
        return False
    
    def make_seas(self):
        if self.verbose: print 'finding bays...'
        max_seeks = len(self.outside_lines)/3
        start_line = self.outside_lines.pop()
        self.outside_lines.add(start_line)
        line = start_line.right
        bay_starts = []
        #Find seed lines
        while line != start_line:
            if self.angle_between_line_and_next(line) < math.pi*0.4:
                bay_starts.append(line)
            line = line.right
        
        #Find bays for all seed lines
        for line in bay_starts:
            line_left = line
            line_right = line
            best_line_left = None
            best_line_right = None
            i = 0
            last_i = 0
            while i < max_seeks:
                i += 1
                line_right = line_right.right
                test_line = Line(line_left.a, line_right.a)
                if self.check_intersections(test_line.a, test_line.b) and \
                        self.check_point(test_line.midpoint):
                    best_line_left, best_line_right = line_left, line_right
                    last_i = i
                line_left = line_left.left
                test_line = Line(line_left.a, line_right.a)
                if self.check_intersections(test_line.a, test_line.b) and \
                        self.check_point(test_line.midpoint):
                    best_line_left, best_line_right = line_left, line_right
                    last_i = i
            if best_line_left != None:
                left = best_line_left
                right = best_line_right
                last_i_2 = 0
                worked = True
                while worked:
                    worked = False
                    i = 0
                    while i < 5:
                        left = left.left
                        test_line = Line(left.a, best_line_right.a)
                        if self.check_intersections(test_line.a, test_line.b) \
                                and self.check_point(test_line.midpoint):
                            best_line_left = left
                            last_i_2 = last_i + i
                            worked = True
                        i += 1
                    last_i = last_i_2
                    i = 0
                    while i < 5:
                        right = right.right
                        test_line = Line(best_line_left.a, right.a)
                        if self.check_intersections(test_line.a, test_line.b) \
                                    and self.check_point(test_line.midpoint):
                            best_line_right = right
                            last_i_2 = last_i + i
                            worked = True
                        i += 1
                new_line = Line(
                    best_line_left.a, best_line_right.a, 
                    best_line_left.left, best_line_right
                )
                new_bay = SeaTerr(new_line)
                self.sea_terrs.add(new_bay)
        removal_queue = set()
        persistent_lines = set()
        for terr in self.sea_terrs:
            moving_line = terr.line.left.right
            while moving_line != terr.line.right.left:
                for terr2 in moving_line.territories:
                    if not terr2 in terr.adjacencies:
                        terr.adjacencies.append(terr2)
                    if not terr in terr2.adjacencies:
                        terr2.adjacencies.append(terr)
                moving_line = moving_line.right
            terr.size = len(terr.adjacencies)
        new_bays = set()
        for terr in self.sea_terrs:
            if terr not in removal_queue:
                moving_line = terr.line.left.right
                while moving_line != terr.line.right.left:
                    moving_line = moving_line.right
                    for terr2 in self.sea_terrs:
                        if terr2 != terr:
                            if moving_line == terr2.line.left or \
                                    moving_line == terr2.line.right:
                                if terr2.size < terr.size:
                                    removal_queue.add(terr2)
                for terr2 in self.sea_terrs:
                    if terr2 not in removal_queue and terr2 != terr:
                        if terr.size == terr2.size:
                            terr2.size += 1
                        if util.intersect(
                                    terr.line.a, terr.line.b, 
                                    terr2.line.a, terr2.line.b
                                ):
                            if self.check_intersections(
                                        terr.line.a, terr2.line.b
                                    ):
                                new_line = Line(
                                    terr.line.a, terr2.line.b, 
                                    terr.line.left, terr2.line.right
                                )
                                new_bay = SeaTerr(new_line)
                                new_bay.adjacencies = terr.adjacencies + \
                                                        terr2.adjacencies
                                new_bay.adjacencies = list(sets.Set(
                                    new_bay.adjacencies
                                ))
                                new_bay.size = len(new_bay.adjacencies)
                                new_bays.add(new_bay)
                                removal_queue.add(terr)
                                removal_queue.add(terr2)
                            elif terr.size < terr2.size:
                                removal_queue.add(terr)
                            elif terr.size > terr2.size:
                                removal_queue.add(terr2)
                            else:
                                removal_queue.add(terr)
                        else:
                            if terr.line.left == terr2.line.left or \
                                    terr.line.right == terr2.line.right:
                                if terr.size < terr2.size:
                                    removal_queue.add(terr)
                                else:
                                    removal_queue.add(terr2)
        self.sea_terrs.update(new_bays)
        self.sea_terrs = self.sea_terrs.difference(removal_queue)
        removal_queue = set()
        for terr in self.sea_terrs:
            for terr2 in self.sea_terrs:
                intersect = False
                if terr != terr2:
                    s1 = set(terr.adjacencies)
                    s2 = set(terr2.adjacencies)
                    if terr.line.a == terr2.line.a \
                            or terr.line.b == terr2.line.b \
                            or (s1 & s2):
                        if terr.size == terr2.size:
                            terr2.size += 1
                        if terr.size > terr2.size:
                            removal_queue.add(terr2)
            if terr.size < 3: removal_queue.add(terr)
        self.sea_terrs = self.sea_terrs.difference(removal_queue)
        for terr in self.sea_terrs:
            new_x, new_y = terr.x, terr.y
            new_x += math.cos(terr.line.normal)*20.0
            new_y += math.sin(terr.line.normal)*20.0
            new_point = Point(new_x, new_y)
            nl1 = Line(terr.line.a, new_point, terr.line.left)
            nl2 = Line(new_point, terr.line.b, nl1, terr.line.right)
            nl1.right = nl2
            terr.lines = [nl1, nl2]
            line2 = terr.line.left.right
            while line2 != terr.line.right:
                line2.color = (1,1,1,1)
                line2 = line2.right
    
