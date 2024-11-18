import pygame as pg
from OpenGL.GL import *
import math
import numpy as np
from scipy.interpolate import BSpline

class Figure:
    def __init__(self,vertices, color, translate, draw_type):
        self.draw_type = draw_type
        self.original_vertices = vertices
        self.vertices_to_operate = vertices
        self.rotated_vertices = vertices     
        
        self.original_color = color
        self.color = self.original_color
        self.rotation_angel = 0.0
        
        self.original_translate = translate
        self.translate = translate
        self.picked = False       
        self.was_curved = False
        self.scale_factor = 1.0
    
    def draw(self):
            if self.picked:
                self.color = (0.0, 1.0, 0.0)
            else:
                self.color = self.original_color                    
           
            glPushMatrix()
            glTranslatef(*self.translate)
            glBegin(self.draw_type)
            glColor3f(*self.color)
            for x, y in self.rotated_vertices:
                glVertex2f(x,y)
            glEnd()
            glPopMatrix()
    
    def rotate(self, angle):
        self.rotation_angel += angle
        self.rotated_vertices = []
        
        for x, y in self.vertices_to_operate:            
            x_rot = x * math.cos(math.radians(self.rotation_angel)) - y * math.sin(math.radians(self.rotation_angel))
            y_rot = x * math.sin(math.radians(self.rotation_angel)) + y * math.cos(math.radians(self.rotation_angel))
            self.rotated_vertices.append((x_rot, y_rot))
        
    def b_spline(self, degree):
        if not self.was_curved:            
            wrapped_points = self.vertices_to_operate[-degree:] + self.vertices_to_operate + self.vertices_to_operate[:degree]
            num_points = len(wrapped_points)
            knot_vector = np.linspace(0, 1, num_points + degree + 1)

            wrapped_points = np.array(wrapped_points)
            x_points, y_points = wrapped_points[:,0], wrapped_points[:,1]

            bspline_x = BSpline(knot_vector, x_points, degree)
            bspline_y = BSpline(knot_vector, y_points, degree)

            t_vals = np.linspace(knot_vector[degree], knot_vector[-degree-1], 100)
            curve_points = [(bspline_x(t), bspline_y(t)) for t in t_vals]
            self.vertices_to_operate = curve_points           
            self.rotate(0)    
 
    def resize(self, scale_delta, x_is_axe_to_resize,mouse_resize):        
        scale_factor_local = scale_delta * self.scale_factor 
        if(mouse_resize):
            self.resized_vert = [
                (x * scale_factor_local, y * scale_factor_local) for x, y in self.vertices_to_operate                
            ]            
        else:
            if(x_is_axe_to_resize):
                self.resized_vert = [
                    (x * scale_factor_local, y) for x, y in self.vertices_to_operate
                ]
            else:
                self.resized_vert = [
                    (x, y * scale_factor_local) for x, y in self.vertices_to_operate
                ]
        self.vertices_to_operate = self.resized_vert 
        self.rotate(0) 

class Plane(Figure):
    def __init__(self):        
        vertices =[
            (0, 76), (-32, 16), (-76, 16), (-96, -12), (-32, -12), (0, -72), (36, -72),
            (4, -12), (40, -12), (96, 44), (64, 44), (36, 16), (0, 16), (32, 76),(0,76)
            ]
        color = (0.992, 0.965, 0.686)
        translate = (-250,0,0)
        draw_type = GL_LINE_STRIP          
        super().__init__(vertices, color,translate, draw_type)

class Christmas_tree(Figure):
    def __init__(self):
        vertices = [
            (0, 80), (-30, 40), (-10, 40), (-40, 0), (-20, 0), (-50, -50), (-10, -50), (-10, -90),
            (10, -90), (10, -50), (50, -50), (20, 0), (40, 0), (10, 40), (30,40),(0,80)
            ]
        color = (0.992, 0.965, 0.686)
        translate = (0,-250,0)
        draw_type = GL_LINE_STRIP  
        super().__init__(vertices, color, translate, draw_type)

class Heart(Figure):
    def __init__(self):
        vertices =[(0, 70), (-30, 90), (-60, 90), (-90, 60), (-90, 20), (-60, -30), (0, -90),
                    (60, -30), (90, 20), (90, 60), (60, 90), (30, 90), (0,70)]
        color = (0.992, 0.965, 0.686)
        translate = (0,0,0)
        draw_type = GL_LINE_STRIP        
        super().__init__(vertices, color, translate, draw_type)

class App:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.clock = pg.time.Clock()

        pg.init()
        pg.display.set_mode((self.width, self.height),pg.OPENGL|pg.DOUBLEBUF)
        pg.display.set_caption(self.title)
        glOrtho(-width / 2, width / 2, -height / 2, height / 2, -1, 1)
        glClearColor(0.1, 0.2, 0.2, 1)
        
        self.plane = Plane()
        self.tree = Christmas_tree()
        self.heart = Heart()
        self.figure_to_perform = None
        #wself.figure_to_perform = self.plane     
        
        self.main_loop()

    def main_loop(self):
        running = True        
        while(running):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    running = False
                    break
                
                elif event.type == pg.KEYDOWN:                    
                    if event.key == pg.K_1:
                        self.select_figure(self.plane)                    
                    elif event.key == pg.K_2:                       
                        self.select_figure(self.tree)                    
                    elif event.key == pg.K_3:                        
                        self.select_figure(self.heart)
                    elif event.key == pg.K_4:                        
                        self.select_figure(None)
                    elif event.key == pg.K_r:
                        self.reset()
                    
                    if self.figure_to_perform is None:
                        break 

                    elif event.key == pg.K_k:                        
                        self.figure_to_perform.rotate(5)                         
                    elif event.key == pg.K_l:                        
                        self.figure_to_perform.rotate(-5)
                    
                    elif event.key == pg.K_UP:                        
                        self.move(1,5)
                    elif event.key == pg.K_DOWN:                        
                        self.move(1,-5)                   
                    elif event.key == pg.K_LEFT:                        
                        self.move(0,-5)                   
                    elif event.key == pg.K_RIGHT:                        
                        self.move(0,5)     

                    elif event.key == pg.K_c:                        
                        self.figure_to_perform.b_spline(2)
                        self.figure_to_perform.was_curved=True
                        print("Curved")

                    elif event.key == pg.K_w:
                        self.figure_to_perform.resize(1.1,False,False)
                    elif event.key == pg.K_s:
                        self.figure_to_perform.resize(0.9,False,False)
                    elif event.key == pg.K_a:
                        self.figure_to_perform.resize(1.1,True,False)
                    elif event.key == pg.K_d:
                        self.figure_to_perform.resize(0.9,True,False)                 
                
                
                
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.figure_to_perform is None:
                        break                     
                    if event.button == 4:  # Scroll up
                        self.figure_to_perform.resize(1.1,True,True)
                    elif event.button == 5:  # Scroll down
                        self.figure_to_perform.resize(0.9,True,True)

            
            self.plane.draw()
            self.tree.draw()
            self.heart.draw()                                  
            pg.display.flip()           
            self.clock.tick(60)
        self.exit()
    
    def select_figure(self, figure):       
        self.plane.picked = self.tree.picked = self.heart.picked = False
        if figure is None:
            self.figure_to_perform = None
        else:
            figure.picked = True
            self.figure_to_perform = figure
            print(f"Selected {figure.__class__.__name__}")
    
    def move(self, axis, value):
        coordinate_list = list(self.figure_to_perform.translate)
        coordinate_list[axis] += value
        self.figure_to_perform.translate = tuple(coordinate_list)
    
    def reset(self): 
        self.plane = Plane()
        self.tree = Christmas_tree()
        self.heart = Heart() 
    def exit(self):
        pg.quit()

if __name__ == "__main__":
    window = App(1000, 800, "Demo")