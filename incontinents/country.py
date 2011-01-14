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
    

def assign_countries_to(landmass):
    pass
