import random
import operator
import pyglet
from pyglet.window import mouse, key
from framework import values
from framework.entities import Bird
from framework.world import World
from support.euclid import Vector2

def run(width, height, teams=[], per_team=values.BIRDS_PER_TEAM, randseed=-1, timelimit=0, end_on_victory=False):
    window = pyglet.window.Window(width=width, height=height)

    if randseed != -1:
        random.seed(randseed)

    myworld = World(window.width, window.height)
    myworld.chosen_ent = None
    myworld.winner = None

    # create a HUD to show us info about the selected entity
    HUDlabel = pyglet.text.Label(
        x=5, y=window.height-5, anchor_y="top",
        font_name="Courier New", font_size=10.0,
        multiline=True, width=window.width,
        color=(255,255,255,200)
    )

    HUDTeamScores = pyglet.text.Label(
        x=5, y=5, anchor_y="bottom",
        font_name="Courier New", font_size=10.0,
        multiline=True, width=window.width,
        color=(255,255,255,100)
    )

    # assign the teams wholesale to world
    for team in teams:
        team.purge()

    myworld.teams = teams

    # generate teams around some random points
    for team in teams:
        # set its centroid
        center = Vector2(random.randint(0,window.width/2) + window.width/2, random.randint(0,window.height/2) + window.height/2)

        # create the birds in this team
        for i in xrange(per_team):
            # compute a random pos within the radius of our centroid
            # discretized to give our little fearsome monsters some space
            x = center.x + random.randrange(-values.FLOCK_SPREAD, values.FLOCK_SPREAD, values.FLOCK_INTERNAL_DIST)
            y = center.y + random.randrange(-values.FLOCK_SPREAD, values.FLOCK_SPREAD, values.FLOCK_INTERNAL_DIST)
            ent = myworld.addEntity(Bird(myworld, x, y), team=team)
            ent.controller = team.controller
            ent.controller.init(ent)
            # and give a default velocity to make things interesting
            ent.v = Vector2(random.uniform(-15.0, 15.0), random.uniform(-15.0, 15.0))

    @window.event
    def on_draw():
        window.clear()
        myworld.draw()

        # display info about the chosen ent, if they exist
        if myworld.chosen_ent:
            HUDlabel.text = """Health: %(health)4d, Team: %(team)s\nController: %(controller)s""" % {
                'health': myworld.chosen_ent.health,
                'team': myworld.chosen_ent.team.name,
                'controller': myworld.chosen_ent.controller.__class__.__name__
            }
            HUDlabel.draw()

        # draw team info, calculated in update()
        HUDTeamScores.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        # left button chooses a boid
        # right button assigns a destination for all the boids in the chosen boid's team
        if button == mouse.LEFT:
            # clear the previous selection's attributes, if selected
            try:
                myworld.chosen_ent.sprite.scale = 1.0
                del myworld.chosen_ent.color_masks['selected']
                myworld.chosen_ent.sprite.color = myworld.chosen_ent.base_color
                myworld.chosen_ent = None
            except AttributeError:
                # and just throw it away
                pass

            # and find our new selection
            for ent in myworld.ents:
                if not ent.dead and Vector2(ent.x - x, ent.y - y).magnitude() <= 24.0:
                    myworld.chosen_ent = ent
                    myworld.chosen_ent.color_masks['selected'] = (255,255,255)
                    myworld.chosen_ent.sprite.scale = 1.8
                    break
        elif button == mouse.RIGHT:
            try:
                myworld.chosen_ent.team.goal = Vector2(x,y)
                myworld.chosen_ent.team.goal_sprite = pyglet.sprite.Sprite(x=x, y=y, img=myworld.goal_img)
                myworld.chosen_ent.team.goal_sprite.color = myworld.chosen_ent.team.color
            except AttributeError:
                pass

    @window.event
    def on_key_release(symbol, modifiers):
        # releases the goal of the currently selected team
        if symbol == key.SPACE:
            try:
                del myworld.chosen_ent.team.goal
                del myworld.chosen_ent.team.goal_sprite
            except AttributeError:
                pass
            except KeyError:
                pass

    def update(dt):
        myworld.update()
        myworld.integrate(dt)

        # also populate team info textbox
        teamScores = []
        survivors = 0
        for team in myworld.teams:
            teamHealth = sum([x.health for x in team.members if not x.dead])
            teamScores.append( "%(name)8s: %(health)4d %(bar)s" % {
                'name': team.name,
                'health': teamHealth,
                'bar': ("*" * int(10 * teamHealth/(len(team.members) * values.START_HEALTH)))
            })

            if teamHealth > 0:
                survivors += 1

        HUDTeamScores.text = "\n".join(teamScores)

        # if we end on victory, check for victory conditions
        if end_on_victory and survivors <= 1:
            endgame(0)

    pyglet.clock.schedule_interval(update, 1.0/60.0)

    def endgame(dt):
        # figure out who the winner is
        teamScores = [(team, sum([x.health for x in team.members if not x.dead])) for team in myworld.teams]
        myworld.winner = max(teamScores, key=operator.itemgetter(1))
        if myworld.winner:
            myworld.winner[0].score += 1

        pyglet.app.exit()

    # also schedule and ending timer to call the victory checker/ender
    if timelimit > 0:
        pyglet.clock.schedule_once(endgame, timelimit)

    pyglet.app.run()
    window.close()

    return myworld.winner
