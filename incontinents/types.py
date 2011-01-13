import random
import itertools

country_colors = [
    (1.0, 0.0, 0.0, 1.0), (1.0, 0.5, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), 
    (0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 1.0), (0.7, 0.0, 1.0, 1.0), 
    (1.0, 0.5, 1.0, 1.0), (0.7, 0.3, 0.0, 1.0)
]
random.shuffle(country_colors)

class Country(object):
    """Collection of territories belonging to the same governing body"""
    
    def __init__(self, color, name="America", cty_id=0):
        self.name = name
        self.color = color  #4-tuple of floats in the range 0.0-1.0
        self.territories = []
        self.adjacencies = []
        self.cty_id = cty_id
    
    def __len__(self):
        return len(self.territories)
    
    def add(self, new_terr):
        """Include new_terr in this country"""
        if new_terr in self.territories: return
        self.territories.append(new_terr)
        new_terr.country = self
    
    def remove(self, old_terr):
        """Exclude old_terr from this country"""
        if old_terr in self.territories:
            self.territories.remove(old_terr)
    
    def absorb(self, new_terr):
        """Remove a territory from another country and put it in this one"""
        new_terr.country.remove(new_terr)
        self.add(new_terr)
    
    def find_adjacent_countries(self):
        """Find countries with territories adjacent to any of this country's territories"""
        adjacencies = set()
        for terr in self.territories:
            for terr2 in terr.adjacencies:
                adjacencies.add(terr2.country)
        adjacencies.remove(self)
        self.adjacencies = sorted(list(adjacencies))
    
    def territory_bordering(self, other):
        """Find a territory in this country bordering a territory not in this country"""
        if other not in self.adjacencies:
            return None
        possibilities = []
        for terr in self.territories:
            for terr2 in terr.adjacencies:
                if other == terr2.country:
                    return terr
                    if terr in possibilities:
                        terr.awesomeness += 1
                    else:
                        possibilities.append(terr)
                        terr.awesomeness = 1
        random.shuffle(possibilities)
        r = None
        for p in possibilities:
            r = p
            if p.awesomeness > 1: return p
        return r
    
    def __repr__(self):
        return "Country(%s, %s, %d)" % (str(self.color), self.name, self.cty_id)
    

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
    
