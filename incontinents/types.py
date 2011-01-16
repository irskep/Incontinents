import random
import itertools
import collections

country_colors = [
    (1.0, 0.0, 0.0, 1.0), (1.0, 0.5, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), 
    (0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 1.0), (0.7, 0.0, 1.0, 1.0), 
    (1.0, 0.5, 1.0, 1.0), (0.7, 0.3, 0.0, 1.0)
]
random.shuffle(country_colors)

grey_colors = []
c = 0.6
while c < 0.8:
    grey_colors.append((c,c,c,1))
    c += 0.15

grey_colorer = itertools.cycle(grey_colors)

class Map(object):
    """Container for territories, countries, and display objects"""
    
    def __init__(self, lines, outside_lines, land_terrs, sea_terrs):
        super(Map, self).__init__()
        self.lines = lines
        self.outside_lines = outside_lines
        self.land_terrs = land_terrs
        self.sea_terrs = sea_terrs
        self.name = "Untitled"
        self.base_distance = 35.0
        self.width, self.height = 0, 0
        self.offset = (0,0)
        self.hash_cell_size = int(self.base_distance*4.5)
        self.outer_line_hash = collections.defaultdict(set)
        self.triangle_hash = collections.defaultdict(set)
    
    def find_bounds(self):
        xs = lambda: itertools.chain(*((line.a.x, line.b.x) for line in self.outside_lines))
        ys = lambda: itertools.chain(*((line.a.y, line.b.y) for line in self.outside_lines))
        min_x = reduce(min, xs(), 0)
        max_x = reduce(max, xs(), min_x)
        min_y = reduce(min, ys(), 0)
        max_y = reduce(max, ys(), min_y)
        self.offset = (-min_x, -min_y)
        self.width = int(max_x - min_x)
        self.height = int(max_y - min_y)
    
    def combine(self, absorber, to_remove):
        absorber.color = [(absorber.color[i]+to_remove.color[i])/2 for i in range(4)]
        if absorber == to_remove: 
            print 'bad combine attempt: territories are the same'
            return
        if to_remove not in self.land_terrs:
            print 'bad combine attempt: territory not in list'
            return
        self.land_terrs.remove(to_remove)
        absorber.triangles.extend(to_remove.triangles)
        for l in to_remove.lines:
            if l in absorber.lines:
                absorber.remove_line(l)
                self.lines.remove(l)
            else:
                absorber.add_line(l)
        for l in to_remove.lines[:]:
            to_remove.remove_line(l)
        for t in to_remove.adjacencies:
            t.find_adjacencies()
        absorber.combinations += 1
        absorber.find_adjacencies()
    
    def enforce_territory_count_limit(self, n):
        if n < 2 or len(self.land_terrs) < 2 \
        or len(self.outside_lines) == len(self.lines):
            return 'No thanks'
        while len(self.land_terrs) > n:
            self._combine_random()
        for t in self.land_terrs:
            t.color = grey_colorer.next()
    
    def _combine_random(self):
        def line_maker():
            for line in self.lines:
                if len(line.territories) == 2:
                    yield line
        score = lambda a: len(a.triangles) + len(a.adjacencies)
        metascore = lambda a: score(a.territories[0]) + score(a.territories[1])
        min_func = lambda a, b: a if metascore(a) < metascore(b) or random.randint(0, 2) == 0 else b
        
        _first = None
        for line in self.lines:
            if len(line.territories) == 2:
                _first = line
                break
        
        line = reduce(min_func, line_maker(), _first)
        absorber = line.territories[0]
        to_remove = line.territories[1]
        self.combine(absorber, to_remove)
    
    def hashes_for_pair(self, a, b):
        return (int(a.x/self.hash_cell_size), int(a.y/self.hash_cell_size)), \
               (int(b.x/self.hash_cell_size), int(b.y/self.hash_cell_size))
    
    def outside_lines_colliding_with(self, a, b):
        for k in self.hashes_for_pair(a, b):
            for line in self.outer_line_hash[k]:
                yield line
    
    def hash_for_point(self, x, y):
        return (int(x/self.hash_cell_size), int(y/self.hash_cell_size))
    
    def triangles_colliding_with(self, x, y):
        for tri in self.triangle_hash[self.hash_for_point(x, y)]:
            yield tri
    
    def fill_triangle_hash(self):
        for territory in self.land_terrs:
            for tri in territory.triangles:
                self.triangle_hash[self.hash_for_point(tri[0], tri[1])].add(tri)
                self.triangle_hash[self.hash_for_point(tri[2], tri[3])].add(tri)
                self.triangle_hash[self.hash_for_point(tri[4], tri[5])].add(tri)
    
    def territory_adjacent_to(self, terr):
        for line in terr.lines:
            for terr2 in line.territories:
                if terr2 != terr:
                    return terr2
    
    def remove_surrounded_or_tiny_territories(self):
        #Removes territories that are entirely surrounded by a single territory
        #or are made of only one triangle
        absorbed = set()
        for terr in self.land_terrs:
            check = True
            for line in terr.lines:
                if len(line.territories) != 2:
                    check = False
            if check:
                absorb = True
                surr_terr = terr.lines[0].territories[1]
                for line in terr.lines:
                    if line.territories[1] != surr_terr:
                        absorb = False
                if absorb:
                    absorbed.add((surr_terr, terr))
        for surr_terr, terr in absorbed:
            self.combine(surr_terr, terr)
        to_kill = [
            terr for terr in self.land_terrs if len(terr.triangles) == 1
        ]
        li = len(self.land_terrs)
        for terr in to_kill:
            self.combine(self.territory_adjacent_to(terr), terr)
    
    def outer_territories(self):
        start_line = self.outside_lines.pop()
        self.outside_lines.add(start_line)
        
        this_terr = start_line.territories[0]
        outside_terrs = [this_terr]
        this_line = start_line.right

        while this_line != start_line:
            if this_line.territories[0] != this_terr:
                this_terr = this_line.territories[0]
                outside_terrs.append(this_terr)
            this_line = this_line.right
    
    def assign_names(self, namer):
        for terr in self.land_terrs:
            terr.name, terr.abbreviation = namer.create('land')
        for terr in self.sea_terrs:
            terr.name, terr.abbreviation = namer.create('sea')
        for terr in itertools.chain(self.land_terrs, self.sea_terrs):
            terr.place_text()
    

class Generator(object):
    """Abstract landmass generator"""
    
    def __init__(self, num_countries):
        super(Generator, self).__init__()
        self.num_countries = num_countries
        self.lines = set()
        self.outside_lines = set()
        self.land_terrs = set()
        self.sea_terrs = set()
        self.width, self.height = 0, 0
        self.offset = (0, 0)
    
    def generate(self):
        raise NotImplementedError
    
    def verify_data(self):
        for terr in self.land_terrs|self.sea_terrs:
            for ln in terr.lines:
                self.lines.add(ln)
            terr.adjacencies = [t for t in terr.adjacencies if t in self.land_terrs|self.sea_terrs]
    
