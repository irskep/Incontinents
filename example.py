import argparse, sys
from incontinents import steve, render, demo, namegen, country

primitive_ratio = 0.7

parser = argparse.ArgumentParser(prog='Incontinents',
                                 description='Generate landmasses')

make_arg = parser.add_argument
make_arg('-o', '--output', action='store', type=str,
         help="Where to store the resulting PNG")
make_arg('-n', '--num', action='store', type=int, default=7,
      help="Number of countries in the continent")
make_arg('-v', '--view', action='store_true', default=False,
         help="Immediately show the continent (requires the pyglet library)")

args = parser.parse_args(sys.argv[1:])

namer = namegen.Namer()
gen = steve.ContinentGenerator(num_countries=args.num, namer=namer)
landmass = gen.generate()
landmass.enforce_territory_count_limit(len(landmass.outside_lines) * primitive_ratio)
for t in landmass.land_terrs:
    for t2 in t.adjacencies:
        if t2 not in landmass.land_terrs and t2 not in landmass.sea_terrs:
            print 'wtf?', t2
landmass.remove_surrounded_or_tiny_territories()
landmass.assign_names(namer)
print 'countries'
country.assign_countries_to(landmass, args.num)

if args.output:
    render.basic(landmass, args.output, draw_cities=True, 
                 supply_center_image_path="resources/star.png",
                 font_name="resources/courR08.pil")

if args.view:
    main_window = demo.MapGenWindow(gen, landmass)
