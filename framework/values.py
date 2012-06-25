FLOCK_SPREAD = 100 # max distance of boid from flock center at generation time
FLOCK_INTERNAL_DIST = 20 # distance between boids at generation time
BIRDS_PER_TEAM = 10 # number of boids per team, unless explicitly specified via argument to run()

DEFAULT_MASS = 20.0 # mass of a boid -- the bigger, the slower
VISION_RADIUS = 100.0 # distance a boid can see
COLLISION_DIST = 16.0 # distance under which two enemy boids are considered colliding

VELOCITY_DAMPING = 0.99 # velocity's multiplied by this to gradually bring boids to a stop
VELOCITY_DAMPING_DEAD = 0.8 # damper for slowing down dead entities

START_HEALTH = 100 #the health each boid has in the beginning
COLLISION_DAMAGE_MULT = 0.1 # the multiplier of the dot product of two colliding birds' velocities
COLLISION_DAMAGE_STATIC = 1.0 # the base amount of damage to inflict no matter what
COLLISION_REPULSE_MULT = 32.0 # the multiplier for the impulse that separates two colliding birds
DAMAGE_DEBOUNCE_MAX = 10 # number of frames of damage 'debouncing'

HIT_MAX_TTL = 20 # number of frames to display a damage count