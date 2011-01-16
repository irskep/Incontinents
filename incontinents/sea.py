import math
import util
from primitives import Line, Point
from territory import SeaTerr

def check_intersections(lm, a, b):
    for line in lm.outside_lines:
        if util.intersect(a, b, line.a, line.b):
            return False
    return True

def check_point(lm, point):
    for tri in lm.triangles_colliding_with(point.x, point.y):
        if util.point_inside_triangle(point.x, point.y, tri):
            return False
    return True

def _possible_starting_lines(lm):
    start_line = lm.outside_lines.pop()
    lm.outside_lines.add(start_line)
    line = start_line.right
    bay_starts = []
    #Find seed lines
    while line != start_line:
        if util.angle_between_line_and_next(line) < math.pi*0.4:
            bay_starts.append(line)
        line = line.right
    return bay_starts

def _seed_bay(lm, line_left, line_right=None, best_line_left=None, best_line_right=None, i=0, max_seeks=None):
    max_seeks = max_seeks or len(lm.outside_lines)/3
    if i >= max_seeks:
        return best_line_left, best_line_right
    line_right = line_right or line_left
    
    line_right = line_right.right
    test_line = Line(line_left.a, line_right.a)
    if check_intersections(lm, test_line.a, test_line.b) and \
            check_point(lm, test_line.midpoint):
        best_line_left, best_line_right = line_left, line_right
    line_left = line_left.left
    test_line = Line(line_left.a, line_right.a)
    if check_intersections(lm, test_line.a, test_line.b) and \
            check_point(lm, test_line.midpoint):
        best_line_left, best_line_right = line_left, line_right
    return _seed_bay(lm, line_left, line_right,
                     best_line_left, best_line_right,
                     i+1, max_seeks)

def _seed_bays(lm):
    bay_starts = _possible_starting_lines(lm)
    for line in bay_starts:
        # Find a concave area
        best_line_left, best_line_right = _seed_bay(lm, line)
        
        # Expand it as much as possible
        if best_line_left != None:
            left = best_line_left
            right = best_line_right
            worked = True
            while worked:
                worked = False
                for i in xrange(5):
                    left = left.left
                    test_line = Line(left.a, best_line_right.a)
                    if check_intersections(lm, test_line.a, test_line.b) \
                            and check_point(lm, test_line.midpoint):
                        best_line_left = left
                        worked = True
                for i in xrange(5):
                    right = right.right
                    test_line = Line(best_line_left.a, right.a)
                    if check_intersections(lm, test_line.a, test_line.b) \
                                and check_point(lm, test_line.midpoint):
                        best_line_right = right
                        worked = True
            new_line = Line(
                best_line_left.a, best_line_right.a, 
                best_line_left.left, best_line_right
            )
            new_bay = SeaTerr(new_line)
            lm.sea_terrs.add(new_bay)

def _remove_overlapping_bays(lm):
    removal_queue = set()
    for terr in lm.sea_terrs:
        if terr not in removal_queue:
            for terr2 in lm.sea_terrs:
                intersect = False
                if terr != terr2 and terr2 not in removal_queue:
                    s1 = set(terr.adjacencies)
                    s2 = set(terr2.adjacencies)
                    if terr.line.a == terr2.line.a \
                            or terr.line.b == terr2.line.b \
                            or (s1 & s2):
                        if terr.size > terr2.size:
                            removal_queue.add(terr2)
                        else:
                            removal_queue.add(terr1)
            if terr.size < 5: removal_queue.add(terr)
    lm.sea_terrs = lm.sea_terrs.difference(removal_queue)

def _bump_out_borders(lm):
    for terr in lm.sea_terrs:
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

def _fill_sea_terr_adjacency_lists(lm):
    for terr in lm.sea_terrs:
        moving_line = terr.line.left.right
        while moving_line != terr.line.right.left:
            for terr2 in moving_line.territories:
                if not terr2 in terr.adjacencies:
                    terr.adjacencies.append(terr2)
                if not terr in terr2.adjacencies:
                    terr2.adjacencies.append(terr)
            moving_line = moving_line.right
        terr.size = len(terr.adjacencies)

def add_seas_to(lm):
    print 'oceans of pain'
    lm.fill_triangle_hash()
    _seed_bays(lm)
    removal_queue = set()
    persistent_lines = set()
    new_bays = set()
    for terr in lm.sea_terrs:
        if terr not in removal_queue:
            moving_line = terr.line.left.right
            while moving_line != terr.line.right.left:
                moving_line = moving_line.right
                for terr2 in lm.sea_terrs:
                    if terr2 != terr:
                        if moving_line == terr2.line.left or \
                                moving_line == terr2.line.right:
                            if terr2.size < terr.size:
                                removal_queue.add(terr2)
            for terr2 in lm.sea_terrs:
                if terr2 not in removal_queue and terr2 != terr:
                    if terr.size == terr2.size:
                        terr2.size += 1
                    if util.intersect(
                                terr.line.a, terr.line.b, 
                                terr2.line.a, terr2.line.b
                            ):
                        if check_intersections(lm, 
                                    terr.line.a, terr2.line.b
                                ):
                            new_line = Line(
                                terr.line.a, terr2.line.b, 
                                terr.line.left, terr2.line.right
                            )
                            new_bay = SeaTerr(new_line)
                            new_bay.adjacencies = terr.adjacencies + \
                                                    terr2.adjacencies
                            new_bay.adjacencies = list(set(
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
    lm.sea_terrs.update(new_bays)
    lm.sea_terrs = lm.sea_terrs.difference(removal_queue)
    
    _remove_overlapping_bays(lm)
    _bump_out_borders(lm)
    _fill_sea_terr_adjacency_lists(lm)
