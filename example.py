import sys
from incontinents import behemoth, render

if len(sys.argv) != 2:
    print 'python example.py <path.png>'
    sys.exit(1)

gen = behemoth.ContinentGenerator(num_countries=2)
landmass = gen.generate()
render.basic(landmass, sys.argv[1], draw_cities=True, 
             supply_center_image_path="star.png",
             font_name="courR08.pil")
