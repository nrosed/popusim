from controllers.base import Controller
from support.euclid import Vector2
from support.helpers import avg

class DummyFollowController(Controller):
    def think(self, me):
        if hasattr(me.team, 'centroid'):
            return (me.team.centroid - Vector2(me.x, me.y)).normalized() * 6000.0
        else:
            # try to find our team's centroid
            teammates = me.team.members
            centroid = Vector2(*(avg([ent.x for ent in teammates]), avg([ent.y for ent in teammates])))
            return (centroid - Vector2(me.x, me.y)).normalized() * 6000.0
