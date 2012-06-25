import math
from controllers.base import Controller
from framework.values import VISION_RADIUS
from support.euclid import Vector2
from support.helpers import avg

AVOID_RADIUS = VISION_RADIUS/2.5 # distance under which avoidance takes effect
AVOID_STRENGTH = 200.0 # strength of the avoid impulse
ATTRACT_STRENGTH = 100.0 # strength of group cohesion among teammates
ALIGN_STRENGTH = 300.0 # strength of alignment among teammates
GOALSEEK_STRENGTH = 600.0 # strength of explicit goal-seeking

class BoidyController(Controller):
    def think(self, me):
        # this'll be where we store the answer
        total_vec = Vector2()

        friends = []

        # === subgoal 1. avoidance
        avoid_vec = Vector2()
        for other, dist in me.neighbors:
            # avoid all other creatures if they're too close
            if dist <= AVOID_RADIUS:
                avoid_vec += (other.pos - me.pos)

            if other in me.team.members:
                friends.append(other)

        # === subgoal 2. attraction
        # friends = [x[0] for x in me.neighbors if (x in me.team.1)]

        attract_vec = Vector2()
        if len(friends) > 0:
            centroid = Vector2(
                sum([ent.x for ent in friends])/len(friends),
                sum([ent.y for ent in friends])/len(friends)
            )
            # and compute our difference from it
            attract_vec = centroid - me.pos

        # === subgoal 3. alignment
        alignment_vec = Vector2()
        for friend in friends:
            alignment_vec += friend.v

        # === subgoal 4. goal-seeking (optional)
        if hasattr(me.team, 'goal'):
            total_vec += (me.team.goal - me.pos).normalized() * GOALSEEK_STRENGTH

        # compute and return the weighted sum of our subgoals
        total_vec += (avoid_vec * -1.0 * AVOID_STRENGTH) + \
                     (attract_vec * ATTRACT_STRENGTH) + \
                     (alignment_vec.normalized() * ALIGN_STRENGTH)

        return total_vec