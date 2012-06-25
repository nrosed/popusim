import colorsys
from support.helpers import rgb_scaled

__author__ = 'Faisal'

class Team(object):
    def __init__(self, name, controller):
        self.name = name
        self.controller = controller
        self.score = 0
        self.match_score = 0
        self.members = []

        # create a (hopefully) unique color for the team by their name
        teamColor = (name.__hash__() % 500)/500.0
        self.color = rgb_scaled(colorsys.hsv_to_rgb(teamColor, 1.0, 1.0))

    def purge(self):
        self.match_score = 0
        self.members = []
        self.controller.purge()
