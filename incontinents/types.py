import random
import itertools

country_colors = [
    (1.0, 0.0, 0.0, 1.0), (1.0, 0.5, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), 
    (0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 1.0), (0.7, 0.0, 1.0, 1.0), 
    (1.0, 0.5, 1.0, 1.0), (0.7, 0.3, 0.0, 1.0)
]
random.shuffle(country_colors)

class Map(object):
    """Container for territories, countries, and display objects"""
    
    def __init__(self, lines, outside_lines, land_terrs, sea_terrs, countries=[]):
        super(Map, self).__init__()
        self.lines = lines
        self.outside_lines = outside_lines
        self.land_terrs = land_terrs
        self.sea_terrs = sea_terrs
        self.countries = countries
        self.name = "Untitled"
        self.map_id = 0
        self.width, self.height = 0, 0
        self.offset = (0,0)
    
    def find_bounds(self):
        xs = itertools.chain(*((line.a.x, line.b.x) for line in self.outside_lines))
        ys = itertools.chain(*((line.a.y, line.b.y) for line in self.outside_lines))
        min_x = reduce(min, xs, 0)
        max_x = reduce(max, xs, 0)
        min_y = reduce(min, ys, 0)
        max_y = reduce(max, ys, 0)
        self.offset = (-min_x, -min_y)
        self.width = int(max_x - min_x)
        self.height = int(max_y - min_y)
    

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
    
