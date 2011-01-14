import itertools
import random
import namegen
import util

land_terrs_per_player = 10

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
    

sort_countries = lambda countries: countries.sort(lambda x, y: len(x)-len(y))

def assign_countries_to(landmass, num=7, namer=None):
    namer = namer or namegen.Namer()
    remaining_terrs = landmass.land_terrs.copy()
    
    countries = [Country(country_colors[i]) for i in range(num)]
    
    start_line = landmass.outside_lines.pop()
    landmass.outside_lines.add(start_line)
    
    this_terr = start_line.territories[0]
    outside_terrs = [this_terr]
    this_line = start_line.right
    
    while this_line != start_line:
        if this_line.territories[0] != this_terr:
            this_terr = this_line.territories[0]
            outside_terrs.append(this_terr)
        this_line = this_line.right
    
    terrs_per_country = len(outside_terrs)/num
    i = 0
    for country in countries:
        this_terr = outside_terrs[i]
        j = 0
        while this_terr not in remaining_terrs:
            this_terr = outside_terrs[i + j]
            j += 1
        country.add(this_terr)
        remaining_terrs.remove(this_terr)
        i += terrs_per_country
    
    terrs_left = len(remaining_terrs)
    
    worked = True
    while terrs_left > 0 and worked:
        worked = False
        sort_countries(countries)
        for country in countries:
            adjacencies = []
            for terr in country.territories:
                adjacencies.extend(terr.adjacencies)
            adjacencies = list(set(adjacencies))
            random.shuffle(adjacencies)
            country.expand_options = []
            for terr in adjacencies:
                if terr in remaining_terrs and terr.country == None:
                    if terr not in country.territories:
                        remaining_terrs.remove(terr)
                        country.add(terr)
                        terrs_left -= 1
                        worked = True
                        break
    
    small, large = _unbalanced_countries(countries)
    i = 0
    while len(small) > 0 and i < 1000:
        i += 1
        for country in small:
            try:
                country.find_adjacent_countries()
                if len(large) > 0:
                    if random.randint(0,1) == 0:
                        target = large[-1]
                        to_take = target.land_terrs[0]
                    else:
                        target = country.adjacencies[-1]
                        target.find_adjacent_countries()
                        to_take = target.territory_bordering(country)
                else:
                    target = country.adjacencies[-1]
                    target.find_adjacent_countries()
                    to_take = target.territory_bordering(country)
                if to_take != None:
                    target.remove(to_take)
                    country.add(to_take)
            except:
                pass #fail silently, mrawrg
        small, large = _unbalanced_countries(countries)
    
    worked = True
    while worked:
        worked = _remove_lone_territories(landmass)
    
    _merge_in_countries(countries, landmass)
    _place_supply_centers(countries)
    sort_countries(countries)
    for terr in itertools.chain(*(country.territories for country in countries)):
        terr.color_self()
    for country in countries:
        country.name, country.abbreviation = namer.create('land')

def _unbalanced_countries(countries):
    sort_countries(countries)
    q1 = len(countries)/4.0
    q2 = int(q1*2)
    q3 = int(q1*3)
    q1 = int(q1)
    quant1 = countries[:q1]
    quant2 = countries[q1:q2]
    quant3 = countries[q2:q3]
    median = util.median(countries)
    mid50 = len(quant2[-1].territories) - len(quant2[0].territories)
    min_terrs = median - mid50*1.5
    max_terrs = median + mid50*1.5
    small = [c for c in countries if len(c.territories) < min_terrs]
    large = [c for c in countries if len(c.territories) > max_terrs]
    
    if len(countries[0].territories)*1.5 \
            < len(countries[-1].territories):
        if countries[0] not in small:
            small.append(countries[0])
        if countries[-1] not in large:
            large.append(countries[-1])
    return sorted(small), sorted(large)

def _remove_lone_territories(landmass):
    worked = False
    for terr in landmass.land_terrs:
        if terr.country:
            terr.find_adjacencies()
            if not terr.country in terr.adjacent_countries:
                for country in terr.adjacent_countries:
                    if country != terr.country:
                        country.absorb(terr)
                        worked = True
                        break
    return worked

def _merge_in_countries(countries, landmass):
    sort_countries(countries)
    country = countries[-1]
    bad_countries = [c for c in countries if len(c) > land_terrs_per_player]
    for country in bad_countries:
        while len(country) > land_terrs_per_player:
            for terr in landmass.land_terrs:
                terr.find_adjacencies()
            country.territories.sort(
                lambda x, y: len(x.adjacencies) - len(y.adjacencies)
            )
            to_remove = country.territories[0]
            to_remove.adjacencies.sort(
                lambda x, y: len(x.adjacencies) - len(y.adjacencies)
            )
            absorb_candidates = [t for t in to_remove.adjacencies if t.country == country]
            if len(absorb_candidates) > 0:
                to_absorb = absorb_candidates[0]
                landmass.combine(to_absorb, to_remove)
                country.territories.remove(to_remove)
            else:
                _remove_lone_territories(landmass)

def _place_supply_centers(countries):
    for country in countries:
        terr_list = [t for t in country.territories if len(t.triangles) > 2]
        random.shuffle(terr_list)
        for t in terr_list[:5]:
            t.has_supply_center = True
        for t in terr_list[3:]:
            t.country = None
        for t in terr_list[:3]:
            t.occupied = True
