import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_floor():
    glBegin(GL_QUADS)
    glColor3fv((0.5, 0.5, 0.5))  # Gray color
    glVertex3fv((-10, 0, 10))
    glVertex3fv((10, 0, 10))
    glVertex3fv((10, 0, -10))
    glVertex3fv((-10, 0, -10))
    glEnd()

def draw_wall_with_window():
    # Draw the whole wall first
    glBegin(GL_QUADS)
    glColor3fv((1, 0, 0))  # Red color
    glVertex3fv((-10, 0, -10))
    glVertex3fv((10, 0, -10))
    glVertex3fv((10, 10, -10))
    glVertex3fv((-10, 10, -10))
    glEnd()
    
    # Cut out the window by drawing a quad with the background color
    # Note: This is a basic way to achieve the effect and might not work in all cases
    glBegin(GL_QUADS)
    glColor3fv((0, 0, 0))  # Black color for the background
    glVertex3fv((-5, 5, -9.99))  # Slightly in front to avoid z-fighting
    glVertex3fv((5, 5, -9.99))
    glVertex3fv((5, 8, -9.99))
    glVertex3fv((-5, 8, -9.99))
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_floor()
        draw_wall_with_window()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    main()
