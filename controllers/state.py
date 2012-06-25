from collections import defaultdict
import math
import random
from controllers.base import Controller
from framework.values import VISION_RADIUS, START_HEALTH
from support.euclid import Vector2

__author__ = 'Natalie'

AVOID_RADIUS = VISION_RADIUS/2.5 # distance under which avoidance takes effect
AVOID_STRENGTH = 200.0 # strength of the avoid impulse
ATTRACT_STRENGTH = 100.0 # strength of group cohesion among teammates
ALIGN_STRENGTH = 300.0 # strength of alignment among teammates
EVADE_STRENGTH = 400.0 # strength of evading away from closest foe
ATTACK_STRENGTH = 400.0 # strength of attacking foe

GOALSEEK_STRENGTH = 600.0 # strength of explicit goal-seeking

def sigmoid(x, shift=0.0):
    try:
        return 1.0/(1.0 + math.exp(-1.0 * x + shift))
    except OverflowError:
        raise Exception("Overflowed, %f and shift %f" % (x, shift))

class StateController(Controller):
    def __init__(self, type):
        # this is the original state variables
        if type == 0:
            self.stateDict = defaultdict(list)
            for i in range(0, 16):
                listChanceNum = []
                for j in range(0, 4):
                    listChanceNum.append(random.randint(1, 100))

                listChanceNum = sorted(listChanceNum)
                self.stateDict[i] = [listChanceNum[0], listChanceNum[1] - listChanceNum[0],\
                                   listChanceNum[2] - listChanceNum[1], listChanceNum[3] - listChanceNum[2],\
                                   100 - listChanceNum[3]]
        else:
            self.makeWinnerController()



    def init(self, me):
        me.action = 0


    def think(self, me):

        # this'll be where we store the answer
        total_vec = Vector2()

        friends = []
        foes = []

        # === subgoal 1. avoidance
        avoid_vec = Vector2()
        for other, dist in me.neighbors:
            # avoid all other creatures if they're too close
            avoid_vec += (other.pos - me.pos) * (1.0 - sigmoid(dist, 24.0))

            if other in me.team.members:
                friends.append(other)
            else:
                foes.append(other)

        # === subgoal 2. attraction
        # friends = [x[0] for x in me.neighbors if (x in me.team.members)]

        attract_vec = Vector2()
        if len(friends) > 0:
            centroid = Vector2(
                sum([ent.x for ent in friends])/len(friends),
                sum([ent.y for ent in friends])/len(friends)
            )
            # and compute our difference from it
            attract_vec = (centroid - me.pos)
            attract_vec *= sigmoid(attract_vec.magnitude(), AVOID_RADIUS+20.0)

        # === subgoal 3. alignment
        alignment_vec = Vector2()
        for friend in friends:
            alignment_vec += friend.v

        # === subgoal 4. attack
        attack_vec = Vector2()
        #now the first foe is the closest one since it is sorted by distance
        if foes:
            foe = foes[0]
            attack_vec = foe.pos - me.pos
        else:
            attack_vec = me.pos - me.pos

        # === subgoal 5. evade
        evade_vec = Vector2()
        #now the first foe is the closest one since it is sorted by distance
        if foes:
            foe = foes[0]
            evade_vec = me.pos - foe.pos
        else:
            evade_vec = me.pos - me.pos



        # so now we have 5 vectors that we will need to blend based on the states that each of the boids are in
        # avoid_vec, attract_vec, alignment_vec (normalized), attack_vec, evade_vec
        # now we are going to make the state machine, each boid has a vector for each state which says
        # how likely it is to go to the next state

        #get the state
        state = self.getState(me.health, len(foes), len(friends))

        #get the probabilities for the state and find what action to take
        prob = self.stateDict[state]
        choosenProb = random.randint(1, 100)
        if choosenProb < prob[0]:
            me.action = 0
        elif choosenProb < prob[0] + prob[1]:
            me.action = 1
        elif choosenProb < prob[0] + prob[1] + prob[2]:
            me.action = 2
        elif choosenProb < prob[0] + prob[1] + prob[2] + prob[3]:
            me.action = 3
        else:
            me.action = 4

        total_vec = Vector2()
        total_vec = self.calcTotalVec(me.action, avoid_vec, attract_vec, alignment_vec, attack_vec, evade_vec)
        if total_vec.x == 0 and total_vec.y == 0:
            total_vec.x = random.randint(250, 500)
            total_vec.y = random.randint(250, 500)
        return total_vec


    def getState(self, health, foes, friends):
        if friends > 0 and friends <= foes and health > START_HEALTH *0.75:
            return 0
        elif friends > 0 and friends <= foes and health > START_HEALTH *0.5:
            return 1
        elif friends > 0 and friends <= foes and health > START_HEALTH *0.25:
            return 2
        elif friends > 0 and friends <=foes and health <= START_HEALTH *0.25:
            return 3

        elif foes > 0 and friends > foes and health > START_HEALTH *0.75:
            return 4
        elif foes > 0 and friends > foes and health > START_HEALTH *0.5:
            return 5
        elif foes > 0 and friends > foes and health > START_HEALTH *0.25:
            return 6
        elif foes > 0 and friends > foes and health <= START_HEALTH *0.25:
            return 7

        elif foes == 0 and health > START_HEALTH *0.75:
            return 8
        elif foes == 0 and health > START_HEALTH *0.5:
            return 9
        elif foes == 0 and health > START_HEALTH *0.25:
            return 10
        elif foes == 0 and health <= START_HEALTH *0.25:
            return 11

        elif friends == 0 and health > START_HEALTH *0.75:
            return 12
        elif friends == 0 and health > START_HEALTH *0.5:
            return 13
        elif friends == 0 and health > START_HEALTH *0.25:
            return 14
        elif friends == 0 and health <= START_HEALTH *0.25:
            return 15
        else:
            return -1

    def __str__(self):
        output = []
        for key in self.stateDict:
            if key == 0:
                output.append("friend > foes, health > 75% ")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 1:
                output.append( "friend > foes, health > 50%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 2:
                output.append( "friend > foes, health > 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 3:
                output.append( "friend > foes, health <= 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])

            if key == 4:
                output.append( "friend < foes, health > 75%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 5:
                output.append( "friend < foes, health > 50%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 6:
                output.append("friend < foes, health > 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 7:
                output.append("friend < foes, health <= 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])

            elif key == 8:
                output.append("foes = 0, health > 75%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 9:
                output.append("foes = 0, health > 50%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 10:
                output.append("foes = 0, health > 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 11:
                output.append("foes = 0, health <= 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])

            elif key == 12:
                output.append("friend = 0, health > 75%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 13:
                output.append("friend = 0, health > 50%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 14:
                output.append("friend = 0, health > 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])
            elif key == 15:
                output.append("friend = 0, health <= 25%")
                output.append("\t evade: %s" % self.stateDict.get(key)[0])
                output.append("\t attack: %s" % self.stateDict.get(key)[1])
                output.append("\t disperse: %s" % self.stateDict.get(key)[2])
                output.append("\t collision avoidance: %s" % self.stateDict.get(key)[3])
                output.append("\t cohesion: %s" % self.stateDict.get(key)[4])

        return "\n".join(output)

    def calcTotalVec(self, action, avoid_vec, attract_vec, alignment_vec, attack_vec, evade_vec):

        alignment_vec = alignment_vec.normalized()
        total_vec = Vector2()

        #evade
        if action == 0:
            total_vec = (avoid_vec * -1.0 * AVOID_STRENGTH) +\
                        (attract_vec * ATTRACT_STRENGTH/2) +\
                        (alignment_vec.normalized() * ALIGN_STRENGTH) +\
                        (attack_vec * ATTACK_STRENGTH * 0) + \
                        (evade_vec * EVADE_STRENGTH * 2)
        #attack
        elif action == 1:
            total_vec = (avoid_vec * -1.0 * AVOID_STRENGTH / 2) +\
                        (attract_vec * ATTRACT_STRENGTH) +\
                        (alignment_vec.normalized() * ALIGN_STRENGTH) +\
                        (attack_vec * ATTACK_STRENGTH * 4) +\
                        (evade_vec * EVADE_STRENGTH / 2)
        #disperse
        elif action == 2:
            total_vec = (avoid_vec * -1.0 * AVOID_STRENGTH * 2) +\
                        (attract_vec * ATTRACT_STRENGTH / 2) +\
                        (alignment_vec.normalized() * ALIGN_STRENGTH) +\
                        (attack_vec * ATTACK_STRENGTH / 2) +\
                        (evade_vec * EVADE_STRENGTH * 2)
        #cohesion
        elif action == 3:
            total_vec = (avoid_vec * -1.0 * AVOID_STRENGTH) +\
                        (attract_vec * ATTRACT_STRENGTH) +\
                        (alignment_vec.normalized() * ALIGN_STRENGTH) +\
                        (attack_vec * ATTACK_STRENGTH * 0) +\
                        (evade_vec * EVADE_STRENGTH * 0)
        #collision avoidance
        elif action == 4:
            total_vec = (avoid_vec * -1.0 * AVOID_STRENGTH * 2) +\
                        (attract_vec * ATTRACT_STRENGTH) +\
                        (alignment_vec.normalized() * ALIGN_STRENGTH) +\
                        (attack_vec * ATTACK_STRENGTH) +\
                        (evade_vec * EVADE_STRENGTH * 2)

        return total_vec

    def makeWinnerController(self):
        self.stateDict = defaultdict(list)
        self.stateDict[0] = [24, 11, 10, 24, 31]
        self.stateDict[1] = [2, 35, 16, 22, 25]
        self.stateDict[2] = [23, 16, 40, 16, 5]
        self.stateDict[3] = [15, 1, 21, 42, 21]

        self.stateDict[4] = [47, 6, 22, 25, 0]
        self.stateDict[5] = [50, 13, 31, 4, 2]
        self.stateDict[6] = [13, 22, 15, 3, 47]
        self.stateDict[7] = [44, 4, 27, 7, 18]

        self.stateDict[8] = [29, 6, 3, 62, 0]
        self.stateDict[9] = [2, 31, 11, 40, 16]
        self.stateDict[10] = [7, 30, 24, 24, 15]
        self.stateDict[11] = [10, 11, 15, 25, 39]

        self.stateDict[12] = [2, 15, 34, 1, 48]
        self.stateDict[13] = [17, 14, 15, 43, 11]
        self.stateDict[14] = [10, 12, 30, 25, 23]
        self.stateDict[15] = [6, 6, 9, 24, 55]
