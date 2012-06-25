from collections import defaultdict
import math
import random
import pyglet
from framework import values
from framework.values import START_HEALTH
from support.euclid import Vector2

class Entity(object):
    def __init__(self, world, x, y):
        self.sprite = pyglet.sprite.Sprite(world.bird_img, x=x, y=y, batch=world.batch)
        self.color_masks = {}
        self.world = world
        self.neighbors = []
        self.colliders = []
        self.v = Vector2()
        self.a = Vector2()
        self.mass = 1.0/values.DEFAULT_MASS

        self.health = START_HEALTH
        self.damage_debounce = 0 # time after taking damage to visibly represent it

    # position getters/setters
    def getX(self): return self.sprite.x
    def getY(self): return self.sprite.y
    def setX(self, v): self.sprite.x = v
    def setY(self, v): self.sprite.y = v
    x, y = property(getX, setX), property(getY, setY)

    def getPos(self): return Vector2(self.x, self.y)
    def setPos(self, v): self.x, self.y = v.x, v.y
    pos = property(getPos, setPos)


    # life status getter
    def getDead(self): return self.health <= 0
    dead = property(getDead)

    def update(self):
        if self.controller:
            self.a = self.controller.think(self) * self.mass

    def integrate(self, dt):
        # no updates for velocity under a certain threshold
        # if self.v.magnitude_squared() < 0.01: return

        # perform euler integration to find our position
        self.sprite.x += self.v.x*dt + 0.5*self.a.x*(dt**2.0)
        self.sprite.y += self.v.y*dt + 0.5*self.a.y*(dt**2.0)

        self.v += self.a*dt

        # zero out the accel each round
        self.a[:] = (0,0)

        # and damp the velociy
        self.v *= values.VELOCITY_DAMPING if not self.dead else values.VELOCITY_DAMPING_DEAD

        # toroidally map x and y to the world limits
        self.x, self.y = self.x % self.world.width, self.y % self.world.height
        # hard limit the edges
        # self.x = min(max(self.x, 0), self.world.width)
        # self.y = min(max(self.y, 0), self.world.height)

        # and update our sprite's yaw
        self.sprite.rotation = ((math.atan2(self.v.x, self.v.y) + math.pi)/(math.pi * 2.0) * 360.0) + 180.0

class Bird(Entity):
    def __init__(self, world, x, y):
        super(Bird, self).__init__(world, x, y)
