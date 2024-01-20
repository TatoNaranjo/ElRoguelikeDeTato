class Action:
    pass

#Used to describe when the user hit the Esc key to Exit the Game
class EscapeAction(Action):
    pass

#Used to describe when our player moves around.
class MovementAction(Action):
    #This passes the direction where the player is trying to move.
    def __init__(self,dx:int,dy:int):
        super().__init__()

        self.dx = dx
        self.dy = dy