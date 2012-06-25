from controllers.boidy_sigmoid import BoidySigmoidController
from controllers.dummyfollow import DummyFollowController
from controllers.boidy import BoidyController
from controllers.state import StateController

from framework import harness
from framework.team import Team

#number of first to 3 rounds
numberOfRounds = 20

#first to this number wins
bestOf = 3

winner = []
teams = [
    Team(name="boids!",  controller=StateController(0)),
    Team(name="robots?", controller=StateController(0))
]

#run this numberOfRounds times
currNumRounds = 0
while currNumRounds < numberOfRounds:
    print "round ", currNumRounds
    currNumRounds += 1

    #first to bestOf wins
    team0StartScore = teams[0].score
    team1StartScore = teams[1].score

    while team0StartScore +bestOf > teams[0].score and team1StartScore +bestOf > teams[1].score:
        #battle
        winner = harness.run(width=800, height=600,
            teams=teams,
            per_team=8, timelimit=60, end_on_victory=True)
        if winner:
            print "Winner: %s, health %d, score %d" % (winner[0].name, winner[1], winner[0].score)

    #now we have the winner, replace the other team
    if teams[0].score - team0StartScore < teams[1].score - team1StartScore:
        teams[0] = Team(name="boids!",  controller=StateController(0))
        print "robots wins!"
    else:
        teams[1] = Team(name="robots?",  controller=StateController(0))
        print "boids wins"

outputFile = open('C:\Users\Natalie\Documents\cs275\\tournamentOutput.txt', 'w')
outputStr = "Overall Winner:" + winner[0].controller.__str__()
outputFile.write(outputStr)



