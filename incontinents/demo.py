import pyglet, itertools
from pyglet import gl
from pyglet.window import key

class MapGenWindow(pyglet.window.Window):
    def __init__(self, my_gen, landmass=None):
        self.my_gen = my_gen
        super(MapGenWindow,self).__init__(width=800, height=800)
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT,gl.GL_NICEST);
        gl.glHint(gl.GL_POINT_SMOOTH_HINT,gl.GL_NICEST);
        gl.glHint(gl.GL_LINE_SMOOTH_HINT,gl.GL_NICEST);
        gl.glDisable(gl.GL_DEPTH_TEST)
        
        self.landmass = landmass or self.my_gen.generate()
        self.draw_capitals = False
        
        self.labels = []
        self.batch = pyglet.graphics.Batch()
        
        self.update()
        
        pyglet.app.run()
    
    def update(self):    
        self.update_labels()
        
        self.camera = [
            self.landmass.offset[0]+5, self.landmass.offset[1]+5
        ]
    
    def on_key_press(self, symbol, modifiers):
        self.on_draw()
        if symbol == key.SPACE:
            self.landmass = self.my_gen.generate()
            self.update()
        elif symbol == key.UP:
            self.camera[1] -= 40
        elif symbol == key.DOWN:
            self.camera[1] += 40
        elif symbol == key.RIGHT:
            self.camera[0] -= 40
        elif symbol == key.LEFT:
            self.camera[0] += 40
    
    def on_mouse_press(self, x, y, button, modifiers):
        for terr in self.landmass.land_terrs:
            if terr.point_inside(x-self.camera[0], y-self.camera[1]):
                line_strings = []
                for line in terr.lines:
                    line_strings.append(', '.join([t.name for t in line.territories]))
                print terr.country, terr.adjacent_countries, terr.adjacencies
    
    def draw_line(self, x1, y1, x2, y2):    
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x1, y1, x2, y2)))
    
    def draw_rect(self, x1, y1, x2, y2):
        pyglet.graphics.draw(
            4, pyglet.gl.GL_QUADS, 
            ('v2f', (x1, y1, x1, y2, x2, y2, x2, y1))
        )
    
    def on_draw(self):
        pyglet.gl.glClearColor(0.2,0.2,0.8,1)
        self.clear()
        gl.glPushMatrix()
        gl.glTranslatef(self.camera[0], self.camera[1], 0)
        for territory in self.landmass.land_terrs:
            for tri in territory.triangles:
                pyglet.gl.glColor4f(*territory.color)
                pyglet.graphics.draw(
                    3, pyglet.gl.GL_TRIANGLES, ('v2f', tri)
                )
            for line in territory.lines:
                pyglet.gl.glColor4f(*line.color)
                self.draw_line(line.a.x, line.a.y, line.b.x, line.b.y)
        for terr in self.landmass.sea_terrs:
            for line in terr.lines:
                pyglet.gl.glColor4f(*line.color)
                self.draw_line(line.a.x, line.a.y, line.b.x, line.b.y)
        if self.draw_capitals:
            for terr in itertools.chain(self.landmass.land_terrs, self.landmass.sea_terrs):
                pyglet.gl.glColor4f(1,1,1,1)
                w = terr.label.content_width/2+2
                h = terr.label.content_height/2
                self.draw_rect(terr.x-w, terr.y-h, terr.x+w, terr.y+h)
                pyglet.gl.glColor4f(1,1,1,1)
                self.batch.draw()
        gl.glPopMatrix()
        self.draw_line(
            0, self.height-20, self.my_gen.base_distance, self.height-20
        )
    
    def update_labels(self):
        for label in self.labels:
            label.delete()
        self.labels = []
        for terr in itertools.chain(self.landmass.land_terrs, self.landmass.sea_terrs):
            l = pyglet.text.Label(
                terr.name, x=terr.x, y=terr.y, color=(0,0,0,255),
                font_size=8, font_name="Inconsolata",
                anchor_x='center', anchor_y='center', batch=self.batch
            )
            self.labels.append(l)
            terr.label = l
    
