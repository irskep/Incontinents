import render
import behemoth
import trigen
import types

"""
territory
    Territory
        country
            default None
        adjacencies, lines
            lists
        is_coastal, has_supply_center, is_sea
            booleans
        x, y
            text position
        pc_x, pc_y
            icon position
        ter_id
        name
        abbreviation
    
    SeaTerr(line)
        Pass it a single line. Reason: bay-generating code in behemoth uses it to check
        intersections and then bows it outward later.
    
    LandTerr(lines, color=(0.5, 0.5, 0.5, 1.0))
        color
        add_line(line)
        remove_line(line)
        add_triangle(x1...y3)
        find_adjacencies()
            Call when map is generated; finds adjacent territories via its lines
        place_piece()
            place icon based on text position
        place_text()
            Places the text label and icon. This will probably work well enough for
            sane shapes.
        color_self()
            set color to a variation of country's color
        point_inside()
            determine if a point is inside the territory

primitives
    Point(x, y)
        x, y
        get_tuple()
            returns (x, y)
        You can refer to point like p[0], p[1] as well.
    
    Line(a, b, left=None, right=None, color=(0,0,0,1))
        a, b
            end points
        left, right
            Neighboring lines. Only meaningful for border lines.
        normal
            angle perpendicular to angle formed by line against horizontal
        midpoint
        outside
            boolean, determines if line borders sea
        territories
            list containing one or two territories
        length
            starts at zero, set when get_length() called
        favored
            used in behemoth.py
        get_length()
            sets length if unset, returns it regardless

util
    point_inside_polygon(x, y, (x1, y1, x2, y2, x3, y3...))
    area_of_triangle(x1...y3)
    intersect(p1, p2, p3, p4)
        line 1 is p1 to p2, line 2 is p3 to p4
        There are more efficient ways to do this, but I could never make them work.
        
"""

