import math, primitives
from itertools import starmap, izip
from operator import mul

def angle_between_line_and_next(line):
    a1 = math.atan2(line.right.b.y-line.b.y, line.right.b.x-line.b.x)
    a2 = math.atan2(line.a.y-line.b.y, line.a.x-line.b.x)
    return (a1 - a2) % (math.pi*2)

def median(countries):
    values = sorted([len(country.territories) for country in countries])
    if len(values) % 2 == 1:
        return values[(len(values)+1)/2-1]
    else:
        lower = values[len(values)/2-1]
        upper = values[len(values)/2]
        return float(lower+upper)/2

def point_inside_triangle(x, y, coord_list):
    # http://www.blackpawn.com/texts/pointinpoly/default.html
    
    x1, x2, x3 = coord_list[0], coord_list[2], coord_list[4]
    y1, y2, y3 = coord_list[1], coord_list[3], coord_list[5]
    if x < x1 and x < x2 and x < x3: return False
    if x > x1 and x > x2 and x > x3: return False
    if y < y1 and y < y2 and y < y3: return False
    if y > y1 and y > y2 and y > y3: return False
    
    P = (x, y)
    A = coord_list[0:2]
    B = coord_list[2:4]
    C = coord_list[4:6]
    
    v0 = (C[0]-A[0], C[1]-A[1])
    v1 = (B[0]-A[0], B[1]-A[1])
    v2 = (P[0]-A[0], P[1]-A[1])
    
    dot00 = v0[0]*v0[0]+v0[1]*v0[1]
    dot01 = v0[0]*v1[0]+v0[1]*v1[1]
    dot02 = v0[0]*v2[0]+v0[1]*v2[1]
    dot11 = v1[0]*v1[0]+v1[1]*v1[1]
    dot12 = v1[0]*v2[0]+v1[1]*v2[1]
    
    invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    if u <= 0: return False
    v = (dot00 * dot12 - dot01 * dot02) * invDenom
    
    return (v > 0) and (u + v < 1)

def area_of_triangle(tri):
    x1 = min(tri[0], tri[2], tri[4])
    y1 = min(tri[1], tri[3], tri[5])
    x2 = max(tri[0], tri[2], tri[4])
    y2 = max(tri[1], tri[3], tri[5])
    w = x2 - x1
    h = y2 - y1
    return w*h/2.0

def _on_segment(xi, yi, xj, yj, xk, yk):
  return (xi <= xk or xj <= xk) and (xk <= xi or xk <= xj) and \
         (yi <= yk or yj <= yk) and (yk <= yi or yk <= yj)

def _direction(xi, yi, xj, yj, xk, yk):
    return (xk - xi) * (yj - yi) - (xj - xi) * (yk - yi)

def intersect(a, b, c, d):
    x1, y1 = a.x, a.y
    x2, y2 = b.x, b.y
    x3, y3 = c.x, c.y
    x4, y4 = d.x, d.y
    if x1 == x3 and y1 == y3 or \
        x2 == x4 and y2 == y4 or \
        x1 == x4 and y1 == y4 or \
        x2 == x3 and y2 == y3:
        return False
    d1 = _direction(x3, y3, x4, y4, x1, y1)
    d2 = _direction(x3, y3, x4, y4, x2, y2)
    d3 = _direction(x1, y1, x2, y2, x3, y3)
    d4 = _direction(x1, y1, x2, y2, x4, y4)
    return (((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
          ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0))) or \
         (d1 == 0 and _on_segment(x3, y3, x4, y4, x1, y1)) or \
         (d2 == 0 and _on_segment(x3, y3, x4, y4, x2, y2)) or \
         (d3 == 0 and _on_segment(x1, y1, x2, y2, x3, y3)) or \
         (d4 == 0 and _on_segment(x1, y1, x2, y2, x4, y4))
