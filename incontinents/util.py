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

def tuple_sub(a, b):
    return (a[0]-b[0], a[1]-b[1])

def dot(v1,v2):
    return v1[0]*v2[0]+v1[1]*v2[1]

def point_inside_triangle(x, y, coord_list):
    # http://www.blackpawn.com/texts/pointinpoly/default.html
    P = (x, y)
    A = coord_list[0:2]
    B = coord_list[2:4]
    C = coord_list[4:6]
    v0 = tuple_sub(C, A)
    v1 = tuple_sub(B, A)
    v2 = tuple_sub(P, A)
    
    dot00 = dot(v0, v0)
    dot01 = dot(v0, v1)
    dot02 = dot(v0, v2)
    dot11 = dot(v1, v1)
    dot12 = dot(v1, v2)
    
    invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    v = (dot00 * dot12 - dot01 * dot02) * invDenom
    
    return (u > 0) and (v > 0) and (u + v < 1)

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
    a = (xk - xi) * (yj - yi)
    b = (xj - xi) * (yk - yi)
    if a < b:
        return -1
    else:
        if a > b:
            return 1
        else:
            return 0

def intersect(a, b, c, d):
    if a.x == c.x and a.y == c.y or \
        b.x == d.x and b.y == d.y or \
        a.x == d.x and a.y == d.y or \
        b.x == c.x and b.y == c.y:
        return False
    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]
    x3, y3 = c[0], c[1]
    x4, y4 = d[0], d[1]
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
