class Controller(object):
    """
    The brains of our birds. Provides the logic for each entity's update cycle and holds some common state between
    members of the same team, if necessary.

    Override the think() method to implement your own logic.
    """

    def init(self, me):
        """
        Initializes each bird ("me") before the simulation begins. This is largely so your strategy can
        store custom data with each bird, if you like.
        """
        pass

    def think(self, me):
        """
        Takes a bird ("me") and produces an acceleration that is applied to the bird next timestep. This method
        must be overridden by classes which implement Controller to implement custom logic.
        """
        pass

    def dead(self, me):
        """
        Called at the moment that a bird is killed (i.e its health becomes <= 0). You may use this as a last
        chance to adjust your strategy.
        """
        pass

    def purge(self):
        pass