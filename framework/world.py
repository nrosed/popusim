import colorsys
from math import sqrt
import operator
import random
import pyglet
from pyglet.gl import *
import entities
from framework import values
from support.euclid import Vector2
from support.helpers import rgb_scaled, circle, line

class World(object):
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.ents = []
        self.batch = pyglet.graphics.Batch()
        self.teams = {}

        self.hit_markers = []
        self.hit_marker_batch = pyglet.graphics.Batch()

        # and allocate some resources
        self.bird_img = pyglet.resource.image('res/bird.png')
        self.bird_img.anchor_x, self.bird_img.anchor_y = 8, 8
        self.goal_img = pyglet.resource.image('res/goal.png')
        self.goal_img.anchor_x, self.goal_img.anchor_y = 8, 8

    def addEntity(self, ent, team):
        """
        Adds an entity to the world.

        This creates a sprite for the entity and adds it to the world's render list, as well as calls the entity's
        update() method before each frame.
        """

        # and add the entity to its team + color it for its team
        ent.team = team
        ent.team.members.append(ent)
        ent.base_color = ent.team.color
        ent.sprite.color = ent.team.color

        # and stick it in the list of things to consider
        self.ents.append(ent)

        return ent

    def draw(self):
        # draw the goals, if present
        for team in self.teams:
            if hasattr(team, 'goal_sprite'):
                team.goal_sprite.draw()

        # prior to drawing each ent with a color mask, its color must be updated by each mask
        for me in [x for x in self.ents if x.color_masks]:
            finalcolor = list(me.base_color)
            for mask in me.color_masks.values():
                for i in xrange(0,2): finalcolor[i] = min(finalcolor[i] + mask[i], 255)
            me.sprite.color = tuple(finalcolor)

        # and draw the boids, of course!
        self.batch.draw()

        # and draw damage indicators on top
        self.hit_marker_batch.draw()

        # and move the damage indicators up + fade them out
        self.hit_markers = [x for x in self.hit_markers if x.ttl > 0]
        for lbl in self.hit_markers:
            frac = lbl.ttl/float(values.HIT_MAX_TTL)
            # move it up a little bit
            lbl.x += lbl.scatter[0]
            lbl.y += lbl.scatter[1]
            # fade it out a little bit
            lbl.color = (255, 255, 255, int(255.0 * frac))

            # decrease time-to-live and remove when it's 0
            lbl.ttl -= 1
            if lbl.ttl <= 0:
                lbl.delete()


    def update(self):
        # compute collision sets for all entities
        self._calc_collisions()

        # once we've computed all the neighbor/collision sets, it's time to update each ent
        for me in self.ents:
            # we don't update dead entities
            if me.dead: continue

            # --------------------------
            # --- entity thinking
            # --------------------------

            # computes the entity's acceleration, mostly, and usually using a controller
            me.update()

            # decrement counters, etc.
            if me.damage_debounce > 0:
                # decrease and set our color accordingly
                me.damage_debounce -= 1
                me.color_masks['debounce'] = (255.0 * (me.damage_debounce/float(values.DAMAGE_DEBOUNCE_MAX)), 0, 0)

                # if we just finished debouncing, remove the mask
                if me.damage_debounce <= 0:
                    del me.color_masks['debounce']

            # --------------------------
            # --- collision response
            # --------------------------

            for other, dist in me.colliders:
                # find collision midpoint, apply impulse in opposite direction
                midpoint = (me.pos - other.pos) * 0.5
                me.v += midpoint.normalized() * values.COLLISION_REPULSE_MULT
                # me.v = midpoint * values.COLLISION_REPULSE_MULT

                # only damage us if we're not already reeling from an earlier attack
                if me.damage_debounce <= 0:
                    # DAMAGE!!!
                    dmg_val = max(int(
                        (me.v.normalized().dot(other.v.normalized()) + 1.0) *
                        other.v.magnitude() * values.COLLISION_DAMAGE_MULT +
                        values.COLLISION_DAMAGE_STATIC), 0)

                    # make a hit indication to float upward
                    lbl = pyglet.text.Label(
                        text=str(dmg_val), bold=True,
                        batch=self.hit_marker_batch,
                        font_size=7.0, font_name="Small Fonts",
                        x=me.x, y=me.y, anchor_x="center", color=(255,255,255,255)
                    )
                    # lbl.scatter = (random.randint(-3,3), random.randint(-3,3))
                    lbl.scatter = (random.randint(-1,1),1)
                    lbl.ttl = values.HIT_MAX_TTL
                    self.hit_markers.append(lbl)

                    # apply damage based on the dot product of their velocities
                    me.health -= dmg_val
                    me.damage_debounce = values.DAMAGE_DEBOUNCE_MAX

            # --------------------------
            # --- death response
            # --------------------------

            # if we just died, make us sad and gray
            if me.dead:
                me.sprite.color = (200,200,200)
                me.sprite.opacity = 100
                # and tell our controller, too
                me.controller.dead(me)

    def integrate(self, dt):
        # perform motion calculations and move our entities
        for ent in self.ents:
            ent.integrate(dt)

    # ====================================================
    # === Internal Methods
    # ====================================================

    def _calc_collisions(self):
        # compute the neighbors for each entity
        for me in self.ents:
            # clear our neighbors, first off
            me.neighbors[:] = []
            me.colliders[:] = []

            # don't consider us if we're dead
            if me.dead: continue

            for other in self.ents:
                # and don't consider ourselves our own neighbor/collider, either
                if me == other: continue
                # don't consider other dead entities
                if other.dead: continue

                # finally, it's a real, live entity that might be a neighbor/collider!
                dist = Vector2(me.x - other.x, me.y - other.y).magnitude()

                if dist <= values.VISION_RADIUS:
                    # it's within range, add it to our near list
                    me.neighbors.append((other, dist))

                if dist <= values.COLLISION_DIST and other not in me.team.members:
                    # we're colliding!
                    me.colliders.append((other, dist))

            # sort neighbors and colliders by dist asc
            me.neighbors = sorted(me.neighbors, key=operator.itemgetter(1))
            me.colliders = sorted(me.colliders, key=operator.itemgetter(1))