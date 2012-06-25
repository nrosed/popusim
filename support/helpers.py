from math import sin, pi, cos
import pyglet
from pyglet.gl.gl import glBegin, glVertex2f, glEnd, GL_TRIANGLE_FAN, glColor3f, glColor4f

__author__ = 'Faisal'

def avg(l):
    """
    Computes averages for each dimension of the given tuple.
    """
    lenr = len(l)
    if lenr <= 0: return 0
    return sum(l)/float(lenr)

def rgb_scaled(input):
    return tuple([x*255 for x in input])

def line(x1, y1, x2, y2, color):
    glColor3f(*color)
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x1, y1, x2, y2)))

def circle(x, y, radius, color):
    iterations = 20
    s = sin(2*pi / iterations)
    c = cos(2*pi / iterations)

    dx, dy = radius, 0

    glColor4f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations+1):
        glVertex2f(x+dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()