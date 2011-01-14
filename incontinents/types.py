import random
import itertools

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
        self.map_id = 0
        self.width, self.height = 0, 0
        self.offset = (0,0)
    
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
            return
        if to_remove not in self.land_terrs:
            print 'bad combine attempt: territory not in list'
            return
        self.land_terrs.remove(to_remove)
        absorber.triangles.extend(to_remove.triangles)
        for l in to_remove.lines:
            if l not in absorber.lines:
                absorber.add_line(l)
            else:
                absorber.remove_line(l)
                self.lines.remove(l)
        for l in to_remove.lines[:]:
            to_remove.remove_line(l)
        absorber.place_text()
        absorber.combinations += 1
    
    def enforce_territory_count_limit(self, n):
        if n < 2:
            return 'No thanks'
        while len(self.land_terrs) > n:
            self._combine_random()
        for t in self.land_terrs:
            t.color = grey_colorer.next()
    
    def _combine_random(self):
        if len(self.land_terrs) < 2: return
        if len(self.outside_lines) == len(self.lines): return
        inside_lines = list(self.lines.difference(self.outside_lines))
        
        avg_combos = 0
        for terr in self.land_terrs:
            avg_combos += terr.combinations
        avg_combos /= float(len(self.land_terrs))
        
        _first = self.land_terrs.pop()
        self.land_terrs.add(_first)
        largest_terr = reduce(lambda a, b: a if len(a.triangles) > len(b.triangles) else b, 
                              self.land_terrs, _first)
        
        candidates_1 = [
            line for line in inside_lines \
            if len(line.territories) > 1 \
            and not largest_terr in line.territories
        ]
        candidates_2 = [
            line for line in candidates_1 \
            if (len(line.territories[0].triangles) == 1 \
            or len(line.territories[1].triangles) == 1) \
            and not largest_terr in line.territories
        ]
        if len(candidates_2) > 0:
            candidates = candidates_2
        else:
            candidates = candidates_1
        found = False
        i = 0
        while not found and i < 200:
            i += 1
            line = random.choice(inside_lines)
            found = True
            if len(line.territories) <= 1:
                found = False
            else:
                for terr in line.territories:
                    if terr.combinations > avg_combos:
                        found = False
        try:
            absorber = line.territories[0]
            to_remove = line.territories[1]
        except:
            return
        self.combine(absorber, to_remove)
    
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
    
    def assign_names(self, namer):
        for terr in self.land_terrs:
            terr.name, terr.abbreviation = namer.create('land')
        for terr in self.sea_terrs:
            terr.name, terr.abbreviation = namer.create('sea')
    

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
    
