import argparse, sys
from incontinents import behemoth, render, demo, namegen, country

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
gen = behemoth.ContinentGenerator(num_countries=args.num, namer=namer)
landmass = gen.generate()
# landmass.enforce_territory_count_limit(len(landmass.outside_lines) * primitive_ratio)
landmass.assign_names(namer)
# landmass.remove_surrounded_or_tiny_territories()
# country.assign_countries_to(landmass, args.num)

if args.output:
    render.basic(landmass, args.output, draw_cities=True, 
                 supply_center_image_path="resources/star.png",
                 font_name="resources/courR08.pil")

if args.view:
    main_window = demo.MapGenWindow(gen, landmass)
