import argparse, sys
from incontinents import behemoth, render, demo

parser = argparse.ArgumentParser(prog='Incontinents',
                                 description='Generate landmasses')

make_arg = parser.add_argument
make_arg('-o', '--output', action='store', type=str,
         help="Where to store the resulting PNG")
make_arg('-v', '--view', action='store_true', default=False,
         help="Immediately show the continent (requires the pyglet library)")

args = parser.parse_args(sys.argv[1:])

gen = behemoth.ContinentGenerator(num_countries=2)
landmass = gen.generate()

if args.output:
    render.basic(landmass, args.output, draw_cities=True, 
                 supply_center_image_path="resources/star.png",
                 font_name="resources/courR08.pil")

if args.view:
    main_window = demo.MapGenWindow(gen)
