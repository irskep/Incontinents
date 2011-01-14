import math, random, sets, util
# random.seed(2011)
import namegen
from primitives import *
from territory import *
from types import *
from country import Country
from fractalgen import FractalGenerator
import sea

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
        fgen = FractalGenerator(128*self.num_countries)
        self.sea_terrs = set()
        self.lines, self.outside_lines, self.land_terrs = fgen.generate()
        
        lm = Map(self.lines, self.outside_lines, self.land_terrs, self.sea_terrs)
        lm.name, lm.abbreviation = self.namer.create('land')
        lm.find_bounds()
        for territory in lm.land_terrs:
            territory.place_text()
        
        sea.add_seas_to(lm)
        return lm
    
