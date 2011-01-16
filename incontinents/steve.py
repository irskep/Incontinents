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
        self.verbose = verbose
        self.num_countries=num_countries
    
    def generate(self):
        lm = FractalGenerator(128*self.num_countries).generate()
        lm.name, lm.abbreviation = self.namer.create('land')
        lm.find_bounds()
        
        sea.add_seas_to(lm)
        return lm
    
